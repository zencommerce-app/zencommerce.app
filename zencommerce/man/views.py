"""
Zen-Commerce views
"""

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.conf import settings

from .models import EtsyShop, EtsyReceipt
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

    steps = BusinessProcessStep.objects.all().order_by('step')

    paginator = Paginator(
        EtsyReceipt.objects.filter(user=request.user),
        settings.PER_PAGE
    )

    items = paginator.page(request.GET.get("page", 1))

    context = {
        "steps": steps,
        "items": items,
    }
    return render(request, 'dashboard.html', context)


def oauth_callback(request, shop_id):
    """
    Connects shop in our DB with ETSY shop,
    by OAUTHv1 and storing received tokens
    """

    item = EtsyShop.objects.get(pk=shop_id)

    if request.method == "GET":
        context = item.request_etsy_token()
        return HttpResponse(context['login_url'])

    if request.method == "POST":
        verifier = request.POST["verifier"]
        item.store_access_request(verifier=verifier)
        return HttpResponse("ok")

    return HttpResponse("GET or POST accepted")


@staff_member_required
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
