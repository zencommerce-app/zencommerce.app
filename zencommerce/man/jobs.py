"""
Functions for background jobs
"""

import json

from django.conf import settings
from django.db import transaction

from .utils import _normalize_bool, _jobs_log


def sync_countries(shop):
    """
    Downloads countries. ETSY Shop needed to establish OAUTH v1 session.
    Any shop can be used here.
    """
    from .models import EtsyCountry

    API_ENDPOINT = 'countries'
    items_processed = 0

    _jobs_log(shop, '[Countries] sync started')

    session = shop.get_oauth()
    response = session.get(settings.ETSY_API_URI + API_ENDPOINT)

    # TODO: check response.headers['X-RateLimit-Remaining']

    if (not 'results' in response.json()) or (response.json()['count'] == 0):
        return 0

    with transaction.atomic():
        for country_json in response.json()['results']:
            item = EtsyCountry(**country_json)
            item.save()

            items_processed += 1

    _jobs_log(shop, '[Countries] downloaded: {}'.format(items_processed))

    return items_processed


def sync_listings(shop, l_type='active'):
    """
    Downloads listings for given ETSY Shop.
    Maximum items per page is 100, need to check requests limit as well.
    TODO: check response.headers['X-RateLimit-Remaining']
    TODO: per user Plan - limit MAX of items downloaded (ex. - Free - 10; Hobby - 50, and so on)

    API documentation:
    https://www.etsy.com/developers/documentation/getting_started/api_basics#section_pagination
    """
    from .models import EtsyListing

    # shops/__SELF__/listings/active
    # shops/__SELF__/listings/inactive
    API_ENDPOINT = 'shops/__SELF__/listings/{}?limit={}&offset={}'
    limit = 100 # per page
    offset = 0
    items_processed = 0

    _jobs_log(shop, '[Listings/{}] sync started'.format(l_type))

    session = shop.get_oauth()

    while True:
        # TODO: Expose Job progress on URL/or Admin panel

        response = session.get(
            settings.ETSY_API_URI + API_ENDPOINT.format(l_type, limit, offset)
        )

        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            # TODO: process error
            break

        # no more listings, or no listings at all in ETSY Shop
        if (not 'results' in data) or (not data['results']):
            # TODO: log or message into Admin panel that job is completed
            break

        if items_processed == 0:
            _jobs_log(shop, '[Listings/{}] API limit remaining: {}'.format(
                l_type, response.headers['X-RateLimit-Remaining'])
            )
            _jobs_log(shop, '[Listings/{}] found: {}'.format(
                l_type, data['count'])
            )

        if data['count'] == 0:
            break

        #TODO: Check response.headers['X-RateLimit-Remaining']

        with transaction.atomic():
            for item_json in data['results']:
                item_json['etsy_user_id'] = item_json['user_id']
                item_json.pop('user_id', None)
                item_json['is_supply'] = _normalize_bool(item_json['is_supply'])

                item = EtsyListing()
                item.shop = shop
                item.user = shop.user
                item.listing_data = item_json
                for attr, value in item_json.items():
                    if hasattr(item, attr):
                        setattr(item, attr, value)
                    # TODO: consider:
                    # try:
                    #     setattr(item, attr, value)
                    # except AttributeError:
                    #     pass
                item.save()

                items_processed += 1

        offset += limit
        _jobs_log(shop, '[Listings/{}] offset: {}'.format(l_type, offset))
        # Debug, GET 1 page and EXIT:
        # break

    _jobs_log(shop, '[Listings/{}] downloaded: {}'.format(l_type, items_processed))
    return items_processed


def sync_receipts(shop):
    """
    Downloads receipts for given ETSY Shop.
    Maximum items per page is 100, need to check requests limit as well.
    TODO: check response.headers['X-RateLimit-Remaining']
    TODO: per user Plan - limit MAX of items downloaded (ex. - Free - 10; Hobby - 50, and so on)
    """
    from .models import EtsyReceipt

    API_ENDPOINT = 'shops/__SELF__/receipts?limit={}&offset={}'
    limit = 100 # per page
    offset = 0
    items_processed = 0
    _fields = (
        'order_id',
        'buyer_email',
        'creation_tsz',
        'last_modified_tsz',
        'is_gift',
        'is_overdue',
        'was_paid',
        'was_shipped',
        'currency_code',
        'discount_amt',
        'grandtotal',
        'adjusted_grandtotal',
        'buyer_adjusted_grandtotal'
    )

    _jobs_log(shop, '[Receipts] sync started')

    session = shop.get_oauth()

    while True:
        # TODO: Expose Job progress on URL/or Admin panel

        response = session.get(
            settings.ETSY_API_URI + API_ENDPOINT.format(limit, offset)
        )

        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            # TODO: process error
            break

        if (not 'results' in data) or (not data['results']):
            break

        if items_processed == 0:
            _jobs_log(shop, '[Receipts] API rate limit remaining: {}'.format(
                response.headers['X-RateLimit-Remaining'])
            )
            _jobs_log(shop, '[Receipts] found: {}'.format(data['count']))

        if data['count'] == 0:
            break

        #TODO: Check response.headers['X-RateLimit-Remaining']

        with transaction.atomic():
            for item_json in data['results']:
                item = EtsyReceipt(
                    receipt_id=item_json['receipt_id'],
                    title = item_json['buyer_email']
                )
                for field in _fields:
                    setattr(item, field, item_json[field])
                item.shop = shop
                item.user = shop.user
                item.receipt_data = item_json
                item.save()

                items_processed += 1

        offset += limit
        _jobs_log(shop, '[Receipts] offset: {}'.format(offset))
        # Debug, GET 1 page and EXIT:
        # break

    _jobs_log(shop, '[Receipts] downloaded: {}'.format(items_processed))
    return items_processed


def sync_transactions(shop):
    """
    Downloads transactions (sold items inside Receipts) from ETSY shop
    """

    from .models import EtsyTransaction

    API_ENDPOINT = 'shops/__SELF__/transactions?limit={}&offset={}'
    limit = 100 # per page
    offset = 0
    items_processed = 0
    _fields = (
        'title',
        'receipt_id',
        'listing_id',
        'seller_user_id',
        'buyer_user_id',
        'creation_tsz',
        'paid_tsz',
        'shipped_tsz',
        'price',
        'currency_code',
        'quantity',
        'shipping_cost'
    )

    _jobs_log(shop, '[Transactions] sync started')
    session = shop.get_oauth()

    while True:
        # TODO: Expose Job progress on URL/or Admin panel
        response = session.get(
            settings.ETSY_API_URI + API_ENDPOINT.format(limit, offset)
        )

        # TODO: DRY common code from all sync jobs
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            # TODO: process error
            break

        if (not 'results' in data) or (not data['results']):
            break

        if items_processed == 0:
            _jobs_log(shop, '[Transactions] API rate limit remaining: {}'.format(
                response.headers['X-RateLimit-Remaining'])
            )
            _jobs_log(shop, '[Transactions] found: {}'.format(data['count']))

        if data['count'] == 0:
            break

        #TODO: Check response.headers['X-RateLimit-Remaining']

        with transaction.atomic():
            for item_json in data['results']:
                item = EtsyTransaction(
                    transaction_id=item_json['transaction_id']
                )
                for field in _fields:
                    setattr(item, field, item_json[field])
                item.shop = shop
                item.user = shop.user
                item.transaction_data = item_json
                item.save()

                items_processed += 1

        offset += limit
        _jobs_log(shop, '[Transactions] offset: {}'.format(offset))
        # Debug, GET 1 page and EXIT:
        # break

    _jobs_log(shop, '[Transactions] downloaded: {}'.format(items_processed))
    return items_processed
