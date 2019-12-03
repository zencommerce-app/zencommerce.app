"""
Zen-Commerce models
"""

from requests_oauthlib import OAuth1Session

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User
from django.conf import settings

from rq import Queue
from worker import conn

from . import mixins
from . import jobs


class EtsyCountry(models.Model):
    """
    Model to represent ETSY country
    """
    country_id = models.IntegerField(primary_key=True)
    iso_country_code = models.CharField(max_length=5)
    world_bank_country_code = models.CharField(max_length=5)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return self.name


class EtsyShop(mixins.BaseMixin, mixins.JobsLogMixin):
    """
    Model to represent ETSY shop
    """
    uri = models.CharField(max_length=200, default="")
    etsy_id = models.IntegerField(blank=True, default=0)

    oauth_token = models.CharField(max_length=200, blank=True, default="")
    oauth_token_secret = models.CharField(max_length=200, blank=True, default="")
    verifier = models.CharField(max_length=200, blank=True, default="")

    def get_queue(self):
        """
        Returns RQ queue
        """
        return Queue(connection=conn)

    def get_oauth(self):
        """
        Returns OAUTH v1 session for this shop
        """
        return OAuth1Session(settings.ETSY_KEYSTRING,
            client_secret=settings.ETSY_SHARED_SECRET,
            resource_owner_key=self.oauth_token,
            resource_owner_secret=self.oauth_token_secret)

    def request_etsy_token(self):
        """
        OAUTH v1 Step 1 - get request tokens (temporary)
        https://requests-oauthlib.readthedocs.io/en/latest/oauth1_workflow.html
        """

        oauth = OAuth1Session(settings.ETSY_KEYSTRING,
            client_secret=settings.ETSY_SHARED_SECRET)
        response = oauth.fetch_request_token(
            settings.ETSY_API_URI + 'oauth/request_token')

        if not 'login_url' in response:
            raise Exception(str(response))

        self.oauth_token = response['oauth_token']
        self.oauth_token_secret = response['oauth_token_secret']
        self.verifier = ""
        self.save()

        return response

    def store_access_request(self, verifier):
        """
        OAUTH v1 Step 3
        Store permanent tokens from ETSY in DB to use later.
        """

        oauth = OAuth1Session(settings.ETSY_KEYSTRING,
            client_secret=settings.ETSY_SHARED_SECRET,
            resource_owner_key=self.oauth_token,
            resource_owner_secret=self.oauth_token_secret,
            verifier=verifier)

        # Fetch non-expiring tokens for this shop
        response = oauth.fetch_access_token(
            settings.ETSY_API_URI + 'oauth/access_token')

        if 'oauth_token' in response:
            self.oauth_token = response['oauth_token']
            self.oauth_token_secret = response['oauth_token_secret']
            self.verifier = verifier
            self.save()

            response2 = self.get_etsy_response('shops/__SELF__')
            if 'results' in response2.json():
                self.etsy_id = response2.json()['results'][0]['shop_id']
                self.save()

        return True

    def get_etsy_response(self, method):
        """
        Get API response, reference:
        https://www.etsy.com/developers/documentation/getting_started/oauth
        Examples:
         - oauth/scopes
         - users/__SELF__
         - shops/__SELF__

         Please note response.headers['X-RateLimit-Remaining']
        """
        return self.get_oauth().get(settings.ETSY_API_URI + method)

    def sync_listings(self, listing_type='active'):
        return self.get_queue().enqueue(jobs.sync_listings, self, listing_type)

    def sync_countries(self):
        return self.get_queue().enqueue(jobs.sync_countries, self)

    def sync_receipts(self):
        return self.get_queue().enqueue(jobs.sync_receipts, self)

    def sync_transactions(self):
        return self.get_queue().enqueue(jobs.sync_transactions, self)


class EtsyListing(mixins.BaseMixin, mixins.JobsLogMixin):
    """
    Model to represent Listing (sellable item) in ETSY shop
    """
    shop = models.ForeignKey(EtsyShop, on_delete=models.CASCADE)

    is_modified_locally = models.BooleanField(default=False)

    # ---- ETSY FIELDS -------------------------------------------------------

    listing_id = models.IntegerField(primary_key=True)

    # title is in BaseMixin
    description = models.TextField(blank=True)

    state = models.CharField(max_length=200, blank=True)
    # user_id in JSON
    etsy_user_id = models.IntegerField(blank=True, default=0)
    category_id = models.IntegerField(blank=True, default=0)

    creation_tsz = models.FloatField(blank=True, default=0.0)
    ending_tsz = models.FloatField(blank=True, default=0.0)
    original_creation_tsz = models.FloatField(blank=True, default=0.0)
    last_modified_tsz = models.FloatField(blank=True, default=0.0)

    price = models.CharField(max_length=200, blank=True)
    currency_code = models.CharField(max_length=200, blank=True)
    quantity = models.IntegerField(blank=True, null=True)

    sku = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    category_path = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    category_path_ids = ArrayField(models.IntegerField(default=0), blank=True, null=True)
    materials = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    shop_section_id = models.IntegerField(blank=True, null=True)
    featured_rank = models.IntegerField(blank=True, null=True)
    state_tsz = models.FloatField(blank=True, default=0.0)
    url = models.CharField(max_length=200, blank=True)
    shipping_template_id = models.CharField(max_length=200, blank=True, null=True)
    processing_min = models.IntegerField(blank=True, null=True)
    processing_max = models.IntegerField(blank=True, null=True)
    who_made = models.CharField(max_length=200, blank=True)
    is_supply = models.BooleanField(default=False)
    when_made = models.CharField(max_length=200, blank=True)

    item_weight = models.IntegerField(blank=True, null=True)
    item_weight_unit = models.CharField(max_length=200, blank=True, null=True)
    item_length = models.IntegerField(blank=True, null=True)
    item_width = models.IntegerField(blank=True, null=True)
    item_height = models.IntegerField(blank=True, null=True)
    item_dimensions_unit = models.CharField(max_length=200, blank=True, null=True)
    is_private = models.BooleanField(default=False)
    recipient = models.CharField(max_length=200, blank=True, null=True)

    occasion = models.CharField(max_length=200, blank=True, null=True)
    style = ArrayField(models.CharField(max_length=200), blank=True, null=True)

    non_taxable = models.BooleanField(default=False)
    is_customizable = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    file_data = models.TextField(blank=True)
    can_write_inventory = models.BooleanField(default=False)
    should_auto_renew = models.BooleanField(default=False)
    language = models.CharField(max_length=200, blank=True)

    has_variations = models.BooleanField(default=False)
    taxonomy_id = models.IntegerField(blank=True, null=True)
    suggested_taxonomy_id = models.IntegerField(blank=True, null=True)
    taxonomy_path = ArrayField(models.CharField(max_length=200), blank=True, null=True)
    used_manufacturer = models.BooleanField(default=False)
    is_vintage = models.BooleanField(default=False)

    views = models.IntegerField(blank=True, null=True)
    num_favorers = models.IntegerField(blank=True, null=True)


class EtsyReceipt(mixins.BaseMixin, mixins.JobsLogMixin):
    """
    Model to represent Receipt (order) in ETSY shop.
    Each Order has multiple Transactions (sold listings in this order)
    """
    shop = models.ForeignKey(EtsyShop, on_delete=models.CASCADE)

    # ---- ETSY FIELDS -------------------------------------------------------

    receipt_id = models.IntegerField(primary_key=True)
    order_id = models.IntegerField()

    buyer_email = models.CharField(max_length=200, blank=True)
    creation_tsz = models.FloatField(blank=True, default=0.0)
    last_modified_tsz = models.FloatField(blank=True, default=0.0)

    is_gift = models.BooleanField(default=False)
    is_overdue = models.BooleanField(default=False)
    was_paid = models.BooleanField(default=False)
    was_shipped = models.BooleanField(default=False)

    currency_code = models.CharField(max_length=20, blank=True)

    discount_amt = models.CharField(max_length=20, blank=True)
    grandtotal = models.CharField(max_length=20, blank=True)
    adjusted_grandtotal = models.CharField(max_length=20, blank=True)
    buyer_adjusted_grandtotal = models.CharField(max_length=20, blank=True)

    receipt_data = JSONField()


class EtsyTransaction(mixins.BaseMixin, mixins.JobsLogMixin):
    """
    Model to represent sold item/listing(s) in order/receipt in ETSY shop.
    Each Order(receipt) has multiple Transactions (sold listings in this order)
    """
    shop = models.ForeignKey(EtsyShop, on_delete=models.CASCADE)

    # ---- ETSY FIELDS -------------------------------------------------------

    transaction_id = models.IntegerField(primary_key=True)
    receipt_id = models.IntegerField()
    listing_id = models.IntegerField()
    seller_user_id = models.IntegerField()
    buyer_user_id = models.IntegerField()
    creation_tsz = models.FloatField(blank=True, default=0.0)
    paid_tsz = models.FloatField(blank=True, null=True, default=0.0)
    shipped_tsz = models.FloatField(blank=True, null=True, default=0.0)
    price = models.CharField(max_length=200, blank=True)
    currency_code = models.CharField(max_length=200, blank=True)
    quantity = models.IntegerField(blank=True, null=True)
    shipping_cost = models.CharField(max_length=200, blank=True)

    transaction_data = JSONField()
