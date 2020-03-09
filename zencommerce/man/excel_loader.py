"""
Zen-Commerce Excel loader
"""

# from openpyxl import load_workbook
import pandas as pd
import json

from django.conf import settings

from .models import EtsyListing
from .utils import _to_int, _to_str, _to_str_bool, _normalize_bool, _jobs_log


class ListingProxy:
    "Proxy object to store loaded data"

    def __init__(self, data):
        self.data = data

    def __getattr__(self, attr):
        # self.data[]
        return attr.upper()


def load_excel_file(shop, filename):
    "Loads file into list of ListingProxy objects"

    # wb = load_workbook(filename=filename)
    # ws = wb['Listings'] # Sheet name in Excel file
    # data = pd.DataFrame(ws.values)

    API_ENDPOINT = 'listings/'
    API_ENDPOINT_UPDATE = 'listings/{}'

    data = pd.read_excel(filename) #, header=1)

    # check result
    print (data.head(3))


    items_processed = 0
    session = shop.get_oauth()

    for index, row in data.iterrows():
        print ("Processing", row['Title'])
        item = None
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
        else:
            url = settings.ETSY_API_URI + API_ENDPOINT
            print ("[NEW] Posting to URL", url)
            _jobs_log(shop, "[NEW] Posting to URL {}".format(url))
            response = session.post(url, json=item_data)

        print (response)
        print (response.text)

        if response.ok:
            print ("OK")
            _jobs_log(shop, "[API OK] {}".format(response.text))

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

            # TODO: check if hasattr, then assign attribute
            if item:
                for attr, value in item_json.items():
                    setattr(item, attr, value)
            else:
                item = EtsyListing(**item_json)
                item.shop = shop
                item.user = shop.user

            item.save()
            _jobs_log(shop, "Updated {}".format(item))
        else:
            _jobs_log(shop, "[API ERROR] {}".format(response.text))

        items_processed += 1
        _jobs_log(shop, "Processed {}".format(items_processed))

    return items_processed

    # images upload
    # https://stackoverflow.com/questions/44855616/how-to-add-a-new-item-using-python-etsy-http-api-methods
