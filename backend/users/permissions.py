"""
File: backend/users/permissions.py
Purpose: Defines custom permission classes for role-based access control in EduPlatform.
Date: 2025-07-24 17:05:10

This file contains:
- IsOwnerOrAdmin: Allow access only to the owner of an object or administrators
- IsUserOrAdmin: Allow access only to the user associated with the object or administrators
- IsInstructor: Allow access only to instructors
- IsStudent: Allow access only to students
- IsStaffMember: Allow access only to staff members
- IsActivatedUser: Allow access only to users with verified emails
"""

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object or admins to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow administrators to make any changes
        if request.user.is_admin or request.user.is_superuser:
            return True

        # Owners can view/edit their own data
        # The obj.owner should be replaced with the appropriate attribute for your model
        # e.g., obj.user, obj.owner, etc.
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        # If the object is the user itself
        return obj == request.user


class IsUserOrAdmin(permissions.BasePermission):
    """
    Object-level permission to allow access only to the user associated with the object or admins.
    """

    def has_object_permission(self, request, view, obj):
        # Allow administrators
        if request.user.is_admin or request.user.is_superuser:
            return True

        # Users can view/edit their own profile
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # If the object is the user itself
        return obj == request.user


class IsInstructor(permissions.BasePermission):
    """
    Allow access only to users with instructor role.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_instructor


class IsStudent(permissions.BasePermission):
    """
    Allow access only to users with student role.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student


class IsPlatformAdmin(permissions.BasePermission):
    """
    Allow access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_admin or request.user.is_superuser)


class IsStaffMember(permissions.BasePermission):
    """
    Allow access only to staff members.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff_member


class IsActivatedUser(permissions.BasePermission):
    """
    Allow access only to users with verified emails.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_email_verified


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the user is the owner of the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user

        # If the object is the user itself
        return obj == request.user
