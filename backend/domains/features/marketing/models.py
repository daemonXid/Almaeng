"""
📈 Marketing Models
"""

from django.db import models
from django_lifecycle import LifecycleModel


class Campaign(LifecycleModel):
    """
    Marketing Campaign tracker (UTM Source).
    """

    name = models.CharField(max_length=100)
    utm_source = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "daemon_marketing_campaigns"
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"

    def __str__(self):
        return self.name


class Lead(LifecycleModel):
    """
    Potential user/customer (Waitlist).
    """

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("converted", "Converted"),
        ("closed", "Closed"),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    source = models.CharField(max_length=100, blank=True, help_text="Referrer or Campaign")
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "daemon_marketing_leads"
        verbose_name = "Lead"
        verbose_name_plural = "Leads"

    def __str__(self):
        return self.email
