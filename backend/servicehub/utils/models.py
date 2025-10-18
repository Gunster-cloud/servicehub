"""
Base models and mixins for ServiceHub.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class SoftDeleteManager(models.Manager):
    """Manager for soft-deleted models."""
    
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)
    
    def all_with_deleted(self):
        return super().get_queryset()
    
    def deleted_only(self):
        return super().get_queryset().filter(deleted_at__isnull=False)


class SoftDeleteModel(models.Model):
    """Abstract model for soft delete functionality."""
    
    deleted_at = models.DateTimeField(_('deletado em'), null=True, blank=True)
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()
    
    class Meta:
        abstract = True
    
    def delete(self, *args, **kwargs):
        """Soft delete: mark as deleted instead of removing."""
        self.deleted_at = timezone.now()
        self.save()
    
    def hard_delete(self, *args, **kwargs):
        """Hard delete: permanently remove from database."""
        super().delete(*args, **kwargs)
    
    def restore(self):
        """Restore a soft-deleted object."""
        self.deleted_at = None
        self.save()
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None


class AuditModel(models.Model):
    """Abstract model for audit trail."""
    
    created_by = models.CharField(_('criado por'), max_length=255, null=True, blank=True)
    updated_by = models.CharField(_('atualizado por'), max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Abstract model with timestamp fields."""
    
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        abstract = True


class AuditLog(models.Model):
    """Model to store audit logs."""
    
    ACTION_CHOICES = (
        ('create', _('Criação')),
        ('update', _('Atualização')),
        ('delete', _('Exclusão')),
        ('restore', _('Restauração')),
    )
    
    user = models.CharField(_('usuário'), max_length=255)
    action = models.CharField(_('ação'), max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(_('modelo'), max_length=255)
    object_id = models.CharField(_('ID do objeto'), max_length=255)
    old_values = models.JSONField(_('valores antigos'), default=dict, blank=True)
    new_values = models.JSONField(_('valores novos'), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_('endereço IP'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Log de Auditoria')
        verbose_name_plural = _('Logs de Auditoria')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.model_name} ({self.object_id})"

