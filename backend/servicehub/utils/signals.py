"""Django signals for ServiceHub."""

from __future__ import annotations

import secrets

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from servicehub.apps.quotes.models import Proposal, Quote
from servicehub.apps.services.models import ServiceOrder


IDENTIFIER_SUFFIX_LENGTH = 4
MAX_IDENTIFIER_ATTEMPTS = 100


def _generate_unique_identifier(model, field_name, prefix):
    """Return a unique identifier using the legacy ``PREFIX-YYYYMMDD-XXXX`` format."""

    today = timezone.now().strftime("%Y%m%d")
    lookup_manager = getattr(model, "_default_manager", model.objects)

    for _ in range(MAX_IDENTIFIER_ATTEMPTS):
        random_suffix = secrets.randbelow(10**IDENTIFIER_SUFFIX_LENGTH)
        identifier = f"{prefix}-{today}-{random_suffix:0{IDENTIFIER_SUFFIX_LENGTH}d}"
        if not lookup_manager.filter(**{field_name: identifier}).exists():
            return identifier

    raise RuntimeError(
        "Unable to generate a unique identifier after "
        f"{MAX_IDENTIFIER_ATTEMPTS} attempts"
    )


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

