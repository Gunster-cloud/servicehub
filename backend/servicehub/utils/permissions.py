"""
Custom permissions for ServiceHub.
"""

from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsManager(permissions.BasePermission):
    """Allow access only to managers."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'manager']


class IsSalesperson(permissions.BasePermission):
    """Allow access only to salespersons."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'manager', 'salesperson']


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allow access only to object owner or admin."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        
        # Check if user is the owner
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsClientOwnerOrAdmin(permissions.BasePermission):
    """Allow access only to client owner or admin."""
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        
        # Check if user is assigned to the client
        if hasattr(obj, 'assigned_to'):
            return obj.assigned_to == request.user
        
        # Check if user created the client
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        return False


class CanViewAnalytics(permissions.BasePermission):
    """Allow access to analytics only to managers and admins."""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'manager']


class CanManageUsers(permissions.BasePermission):
    """Allow user management only to admins."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class ReadOnly(permissions.BasePermission):
    """Allow read-only access."""
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

