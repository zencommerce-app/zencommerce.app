"""
Zen-Commerce Excel loader
"""

# from openpyxl import load_workbook
import pandas as pd
import json

from django.conf import settings

from .models import EtsyListing, EtsyUploadJob
from .utils import _to_int, _to_str, _to_str_bool, _normalize_bool, _jobs_log


def create_load_job(user, shop, file_excel, file_archive):
    "Creates a job to upload Listings to Etsy and our DB"

    data = pd.read_excel(file_excel.temporary_file_path())
    # check result
    print (data.head(3))
    # print (data.to_json(orient='records'))
    json_data = data.to_json(orient='records')
    items_total = len(data.index)

    item = EtsyUploadJob(
        title = "Job - {}, items {}".format(shop, items_total),
        user = user,
        shop = shop,
        status = "new",
        items_total = items_total,
        items_processed = 0,
        job_data = json.loads(json_data),
        file_archive = file_archive
    )

    item.save()

    return items_total


def load_excel_file(shop, filename):
    "Loads Excel file into Etsy and our DB"

    # wb = load_workbook(filename=filename)
    # ws = wb['Listings'] # Sheet name in Excel file
    # data = pd.DataFrame(ws.values)

    API_ENDPOINT = 'listings/'
    API_ENDPOINT_UPDATE = 'listings/{}'

    data = pd.read_excel(filename) #, header=1)
    # check result
    print (data.head(3))
    # print (data.to_json(orient='records'))
    # json_data = data.to_json(orient='records')

    items_processed = 0
    session = shop.get_oauth()

    for index, row in data.iterrows():
        print ("Processing", row['Title'])
        item = None
        recreating_on_etsy = False
        listing_id = _to_int(row['Listing id'])

        sku = _to_str(row['Sku'])

        if listing_id:
            try:
                item = EtsyListing.objects.get(pk=listing_id)
            except:
                pass
        else:
            # Search for Listing in DB by SKU
            items = EtsyListing.objects.filter(shop=shop).filter(sku__contains=[sku])
            if items.count():
                item = items[0]
                listing_id = item.listing_id

        item_data = {
            'sku': sku,
            'is_digital': _to_str_bool(row['Is digital']),
            'title': row['Title'],
            'description': row['Description'],
            'price': row['Price'],
            'currency_code': row['Currency code'],
            'quantity': row['Quantity'],
            'taxonomy_id': row['Taxonomy id'],
            'state': row['State'],
            'who_made': row['Who made'],
            'is_supply': _to_str_bool(row['Is supply']),
            'when_made': row['When made'],
            'shipping_template_id': row['Shipping template id'],
            'tags': row['Tags']
        }

        if listing_id:
            item_data['listing_id'] = listing_id
            url = settings.ETSY_API_URI + API_ENDPOINT_UPDATE.format(listing_id)
            print ("[UPDATE] Putting to URL", url)
            _jobs_log(shop, "[UPDATE] Putting to URL {}".format(url))
            response = session.put(url, data=item_data)

            if not response.ok:
                _jobs_log(shop, "[API ERROR] {}".format(response.text))
                item.state = "removed"
                item.save()
                item = None
                # Listing may exists in our DB but not on ETSY
                # Will try to recreate it
                recreating_on_etsy = True
                del item_data['listing_id']

                url = settings.ETSY_API_URI + API_ENDPOINT
                print ("[NEW for UPDATE] Posting to URL", url)
                _jobs_log(shop, "[NEW] Posting to URL {}".format(url))
                response = session.post(url, json=item_data)

        else:
            url = settings.ETSY_API_URI + API_ENDPOINT
            print ("[NEW] Posting to URL", url)
            _jobs_log(shop, "[NEW] Posting to URL {}".format(url))
            response = session.post(url, json=item_data)

        print (response)
        print (response.text)

        if response.ok:
            print ("OK")
            # _jobs_log(shop, "[API OK] {}".format(response.text))

            if (not 'results' in response.json()) or (response.json()['count'] == 0):
                # no Listing data in response
                continue

            item_json = response.json()['results'][0]

            item_json['etsy_user_id'] = item_json['user_id']
            del item_json['user_id']
            item_json['is_supply'] = _normalize_bool(item_json['is_supply'])
            del item_json['ShippingInfo']

            if not item_json['sku'] and sku:
                item_json['sku'] = [sku]

            if not item:
                item = EtsyListing()
                item.shop = shop
                item.user = shop.user

            for attr, value in item_json.items():
                if hasattr(item, attr):
                    setattr(item, attr, value)

            item.save()
            _jobs_log(shop, "Updated {}".format(item))
        else:
            _jobs_log(shop, "[API ERROR] {}".format(response.text))

        items_processed += 1
        _jobs_log(shop, "Processed {}".format(items_processed))

    return items_processed

    # images upload
    # https://stackoverflow.com/questions/44855616/how-to-add-a-new-item-using-python-etsy-http-api-methods
