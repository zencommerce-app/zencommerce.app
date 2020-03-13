"""
Zen-Commerce views
"""

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.conf import settings

from .models import EtsyShop, EtsyReceipt, EtsyListing, EtsyUploadJob
from .excel_loader import create_load_job, load_excel_file
from flow.models import BusinessProcessStep


def home(request):
    """
    Index/home page for a web service Zen-Commerce
    """
    return render(request, 'index.html', {})


@login_required
def dashboard(request):
    """
    Dashboard with orders, shops and work tools
    """

    step = request.GET.get("step", "")
    steps = BusinessProcessStep.objects.all().order_by('step')

    shops = EtsyShop.objects.filter(user=request.user)
    orders = EtsyReceipt.objects.filter(user=request.user).order_by('creation_tsz')

    if step == "New":
        orders = orders.filter(was_paid=False)

    paginator = Paginator(
        orders,
        settings.PER_PAGE
    )

    page = request.GET.get("page", 1)
    items = paginator.page(page)

    delta_page_range = 20
    index = items.number - 1
    max_index = len(paginator.page_range)
    start_index = index - delta_page_range if index >= delta_page_range else 0
    end_index = index + delta_page_range if index <= max_index - delta_page_range else max_index
    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        "step": step,
        "steps": steps,
        "shops": shops,
        "items": items,
        'page_range': page_range,
    }
    return render(request, 'dashboard.html', context)


@login_required
def listings(request):
    """
    Dashboard with listings
    """

    shops = EtsyShop.objects.filter(user=request.user)

    items_all = EtsyListing.objects.filter(user=request.user).order_by('creation_tsz')

    paginator = Paginator(
        items_all,
        settings.PER_PAGE
    )

    page = request.GET.get("page", 1)
    items = paginator.page(page)

    delta_page_range = 20
    index = items.number - 1
    max_index = len(paginator.page_range)
    start_index = index - delta_page_range if index >= delta_page_range else 0
    end_index = index + delta_page_range if index <= max_index - delta_page_range else max_index
    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        "shops": shops,
        "items": items,
        'page_range': page_range,
    }
    return render(request, 'dashboard_listings.html', context)


@login_required
def shops(request):
    """
    Dashboard with shops
    """

    items_all = EtsyShop.objects.filter(user=request.user)

    paginator = Paginator(
        items_all,
        settings.PER_PAGE
    )

    page = request.GET.get("page", 1)
    items = paginator.page(page)

    delta_page_range = 20
    index = items.number - 1
    max_index = len(paginator.page_range)
    start_index = index - delta_page_range if index >= delta_page_range else 0
    end_index = index + delta_page_range if index <= max_index - delta_page_range else max_index
    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        "shops": items_all,
        "items": items,
        'page_range': page_range,
    }
    return render(request, 'dashboard_shops.html', context)


@login_required
@csrf_exempt
def excel(request):
    """
    Load listings from Excel/etc
    """
    user = request.user
    shops = EtsyShop.objects.filter(user=user)
    shop = None
    items_processed = 0

    if request.method == "POST" and request.FILES['excelfile']:
        shop_id = request.POST['shop']
        fd = request.FILES['excelfile']
        file_archive = request.FILES.get('file_archive', None)

        # TODO: check this shop is owned by request.user
        shop = EtsyShop.objects.get(pk=shop_id)

        items_processed = create_load_job(user, shop, fd, file_archive)
        shop = None
        # items_processed = load_excel_file(shop, fd.temporary_file_path())

    context = {
        "shop": shop,
        "shops": shops,
        "items_processed": items_processed
    }
    return render(request, 'excel.html', context)


@csrf_exempt
def oauth_callback(request, shop_id):
    """
    Connects shop in our DB with ETSY shop,
    by OAUTHv1 and storing received tokens
    """

    item = EtsyShop.objects.get(pk=shop_id)

    if request.method == "GET":
        try:
            context = item.request_etsy_token()
            return JsonResponse({'login_url': context['login_url']})
        except Exception as e:
            return JsonResponse({"error": str(e)})

    if request.method == "POST":
        verifier = request.POST["verifier"]
        item.store_access_request(verifier=verifier)
        return HttpResponse("Shop tokens ok")

    return HttpResponse("GET or POST accepted")


@staff_member_required
@csrf_exempt
def etsy_response(request, shop_id):
    """
    Returns raw response from ETSY
    """

    context = {}

    try:
        item = EtsyShop.objects.get(pk=shop_id)
        response = item.get_etsy_response(request.GET["method"])

        context.update({
            'response': response,
            'headers_dict': dict(response.headers),
            'remaining_limit': response.headers.get('X-RateLimit-Remaining', 'N/A')
        })
    except EtsyShop.DoesNotExist:
        context["error"] = "Shop with ID #{} does not exists or not added into our database".format(shop_id)

    return render(request, 'etsy_response.html', context)


# TODO: check if user is owner of this shop
@staff_member_required
def run_job(request, shop_id):
    """
    Starts a background job in worker.py
    """

    shop = EtsyShop.objects.get(pk=shop_id)
    method = request.GET["method"]
    res = 'Invalid job type. Specify valid one in "?method=[country|listing|inactive]" '

    if method == 'country':
        res = "Countries sync job started"
        shop.sync_countries()
    elif method == 'receipt':
        res = "Receipts sync job started"
        shop.sync_receipts()
    elif method == 'transaction':
        res = "Transactions sync job started"
        shop.sync_transactions()
    elif method == 'listing':
        res = "Listings/active sync job started"
        shop.sync_listings()
    elif method == 'inactive':
        res = "Listings/inactive sync job started"
        shop.sync_listings('inactive')
    elif method == 'draft':
        res = "Listings/draft sync job started"
        shop.sync_listings('draft')
    elif method == 'expired':
        res = "Listings/expired sync job started"
        shop.sync_listings('expired')

    return HttpResponse(res)
