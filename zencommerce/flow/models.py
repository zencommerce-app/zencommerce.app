"""
Flow models
"""

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class BusinessProcessStep(models.Model):
    """
    Model to represent Step in business process.
    E.x.: Step 1 "Production" -> Step 2 "Packaging" -> Step 3 "Delivery"
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    step = models.IntegerField("Business process step #")
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    query = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['step',]
