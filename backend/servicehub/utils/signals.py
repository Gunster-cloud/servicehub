"""
Django signals for ServiceHub.
"""

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from servicehub.apps.quotes.models import Quote, Proposal
from servicehub.apps.services.models import ServiceOrder
import uuid


@receiver(pre_save, sender=Quote)
def generate_quote_number(sender, instance, **kwargs):
    """Generate quote number automatically."""
    if not instance.quote_number:
        # Format: QT-YYYYMMDD-XXXX
        today = timezone.now().strftime('%Y%m%d')
        random_suffix = str(uuid.uuid4().int)[:4]
        instance.quote_number = f"QT-{today}-{random_suffix}"


@receiver(pre_save, sender=Proposal)
def generate_proposal_number(sender, instance, **kwargs):
    """Generate proposal number automatically."""
    if not instance.proposal_number:
        # Format: PR-YYYYMMDD-XXXX
        today = timezone.now().strftime('%Y%m%d')
        random_suffix = str(uuid.uuid4().int)[:4]
        instance.proposal_number = f"PR-{today}-{random_suffix}"


@receiver(pre_save, sender=ServiceOrder)
def generate_order_number(sender, instance, **kwargs):
    """Generate service order number automatically."""
    if not instance.order_number:
        # Format: SO-YYYYMMDD-XXXX
        today = timezone.now().strftime('%Y%m%d')
        random_suffix = str(uuid.uuid4().int)[:4]
        instance.order_number = f"SO-{today}-{random_suffix}"


@receiver(pre_save, sender=Quote)
def calculate_quote_total(sender, instance, **kwargs):
    """Calculate quote total automatically."""
    instance.total = instance.subtotal - instance.discount + instance.tax

