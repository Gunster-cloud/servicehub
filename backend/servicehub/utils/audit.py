"""
Audit and logging utilities for ServiceHub.
"""

from functools import wraps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from servicehub.utils.models import AuditLog
import json
from django.core.serializers.json import DjangoJSONEncoder


def audit_action(action_type):
    """Decorator to log actions."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            result = func(self, request, *args, **kwargs)
            
            try:
                user = request.user.username if request.user.is_authenticated else 'anonymous'
                ip_address = get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                
                AuditLog.objects.create(
                    user=user,
                    action=action_type,
                    model_name=self.queryset.model.__name__,
                    object_id=getattr(self, 'kwargs', {}).get('pk', 'N/A'),
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            except Exception as e:
                print(f"Error logging action: {e}")
            
            return result
        return wrapper
    return decorator


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_model_changes(sender, instance, created, **kwargs):
    """Signal handler to log model changes."""
    try:
        if created:
            action = 'create'
            old_values = {}
            new_values = serialize_model(instance)
        else:
            action = 'update'
            # Get previous values from database
            try:
                old_instance = sender.objects.get(pk=instance.pk)
                old_values = serialize_model(old_instance)
                new_values = serialize_model(instance)
            except sender.DoesNotExist:
                old_values = {}
                new_values = serialize_model(instance)
        
        AuditLog.objects.create(
            user='system',
            action=action,
            model_name=sender.__name__,
            object_id=str(instance.pk),
            old_values=old_values,
            new_values=new_values,
        )
    except Exception as e:
        print(f"Error logging model changes: {e}")


def serialize_model(instance):
    """Serialize model instance to JSON-compatible dict."""
    data = {}
    for field in instance._meta.get_fields():
        if field.many_to_one or field.one_to_one:
            continue
        if field.many_to_many:
            continue
        
        try:
            value = getattr(instance, field.name)
            if hasattr(value, 'isoformat'):
                data[field.name] = value.isoformat()
            else:
                data[field.name] = str(value)
        except Exception:
            pass
    
    return data


class AuditMixin:
    """Mixin to add audit logging to viewsets."""
    
    def perform_create(self, serializer):
        """Log creation."""
        serializer.save()
        AuditLog.objects.create(
            user=self.request.user.username,
            action='create',
            model_name=self.queryset.model.__name__,
            object_id=str(serializer.instance.pk),
            new_values=serialize_model(serializer.instance),
            ip_address=get_client_ip(self.request),
        )
    
    def perform_update(self, serializer):
        """Log update."""
        old_instance = self.get_object()
        old_values = serialize_model(old_instance)
        
        serializer.save()
        
        AuditLog.objects.create(
            user=self.request.user.username,
            action='update',
            model_name=self.queryset.model.__name__,
            object_id=str(serializer.instance.pk),
            old_values=old_values,
            new_values=serialize_model(serializer.instance),
            ip_address=get_client_ip(self.request),
        )
    
    def perform_destroy(self, instance):
        """Log deletion."""
        AuditLog.objects.create(
            user=self.request.user.username,
            action='delete',
            model_name=self.queryset.model.__name__,
            object_id=str(instance.pk),
            old_values=serialize_model(instance),
            ip_address=get_client_ip(self.request),
        )
        instance.delete()

