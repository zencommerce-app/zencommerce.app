"""
Zen-Commerce model mixins
"""

from django.db import models
from django.contrib.auth.models import User


class BaseMixin(models.Model):
    """
    Base model for ETSY objects
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class JobsLogMixin(models.Model):
    """
    Provides field and method to use RQ jobs log
    """
    jobs_log = models.TextField(blank=True)

    def jobs_log_tail(self):
        if not self.jobs_log:
            return ""
        return self.jobs_log.split('\n', 1)[0]

    class Meta:
        abstract = True
