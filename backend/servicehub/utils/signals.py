"""
Django signals for ServiceHub.
"""

import uuid

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from servicehub.apps.quotes.models import Quote, Proposal
from servicehub.apps.services.models import ServiceOrder


def _generate_unique_identifier(model, field_name, prefix):
    """Return a unique identifier with a prefix and date component."""
    today = timezone.now().strftime('%Y%m%d')
    while True:
        random_suffix = uuid.uuid4().hex[:6].upper()
        identifier = f"{prefix}-{today}-{random_suffix}"
        if not model.objects.filter(**{field_name: identifier}).exists():
            return identifier


@receiver(pre_save, sender=Quote)
def generate_quote_number(sender, instance, **kwargs):
    """Generate quote number automatically."""
    if not instance.quote_number:
        instance.quote_number = _generate_unique_identifier(Quote, 'quote_number', 'QT')


@receiver(pre_save, sender=Proposal)
def generate_proposal_number(sender, instance, **kwargs):
    """Generate proposal number automatically."""
    if not instance.proposal_number:
        instance.proposal_number = _generate_unique_identifier(Proposal, 'proposal_number', 'PR')


@receiver(pre_save, sender=ServiceOrder)
def generate_order_number(sender, instance, **kwargs):
    """Generate service order number automatically."""
    if not instance.order_number:
        instance.order_number = _generate_unique_identifier(ServiceOrder, 'order_number', 'SO')


@receiver(pre_save, sender=Quote)
def calculate_quote_total(sender, instance, **kwargs):
    """Calculate quote total automatically."""
    instance.total = instance.subtotal - instance.discount + instance.tax

