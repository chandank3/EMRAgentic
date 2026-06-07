"""RBAC (Role-Based Access Control) implementation"""
from enum import Enum
from typing import Set, Dict, List, Optional
from functools import wraps
from fastapi import Depends, HTTPException, status
from src.models.models import UserRole
import logging

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """System permissions"""
    # Appointment permissions
    SCHEDULE_APPOINTMENT = "schedule_appointment"
    VIEW_APPOINTMENT = "view_appointment"
    EDIT_APPOINTMENT = "edit_appointment"
    CANCEL_APPOINTMENT = "cancel_appointment"

    # Care plan permissions
    CREATE_CARE_PLAN = "create_care_plan"
    VIEW_CARE_PLAN = "view_care_plan"
    EDIT_CARE_PLAN = "edit_care_plan"
    APPROVE_CARE_PLAN = "approve_care_plan"

    # Medication permissions
    MANAGE_MEDICATIONS = "manage_medications"
    VIEW_MEDICATIONS = "view_medications"

    # Document permissions
    UPLOAD_DOCUMENT = "upload_document"
    VIEW_DOCUMENT = "view_document"
    DELETE_DOCUMENT = "delete_document"

    # User management
    MANAGE_USERS = "manage_users"
    VIEW_USERS = "view_users"

    # Audit and compliance
    VIEW_AUDIT_LOG = "view_audit_log"
    MANAGE_POLICIES = "manage_policies"


class RBACManager:
    """Role-based access control manager"""

    # Define role-permission mapping
    ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
        UserRole.ADMIN: {
            Permission.SCHEDULE_APPOINTMENT,
            Permission.VIEW_APPOINTMENT,
            Permission.EDIT_APPOINTMENT,
            Permission.CANCEL_APPOINTMENT,
            Permission.CREATE_CARE_PLAN,
            Permission.VIEW_CARE_PLAN,
            Permission.EDIT_CARE_PLAN,
            Permission.APPROVE_CARE_PLAN,
            Permission.MANAGE_MEDICATIONS,
            Permission.VIEW_MEDICATIONS,
            Permission.UPLOAD_DOCUMENT,
            Permission.VIEW_DOCUMENT,
            Permission.DELETE_DOCUMENT,
            Permission.MANAGE_USERS,
            Permission.VIEW_USERS,
            Permission.VIEW_AUDIT_LOG,
            Permission.MANAGE_POLICIES,
        },
        UserRole.CARE_COORDINATOR: {
            Permission.SCHEDULE_APPOINTMENT,
            Permission.VIEW_APPOINTMENT,
            Permission.EDIT_APPOINTMENT,
            Permission.CANCEL_APPOINTMENT,
            Permission.CREATE_CARE_PLAN,
            Permission.VIEW_CARE_PLAN,
            Permission.EDIT_CARE_PLAN,
            Permission.MANAGE_MEDICATIONS,
            Permission.VIEW_MEDICATIONS,
            Permission.UPLOAD_DOCUMENT,
            Permission.VIEW_DOCUMENT,
            Permission.VIEW_AUDIT_LOG,
        },
        UserRole.PHYSICIAN: {
            Permission.VIEW_APPOINTMENT,
            Permission.VIEW_CARE_PLAN,
            Permission.APPROVE_CARE_PLAN,
            Permission.MANAGE_MEDICATIONS,
            Permission.VIEW_MEDICATIONS,
            Permission.VIEW_DOCUMENT,
            Permission.UPLOAD_DOCUMENT,
        },
        UserRole.NURSE: {
            Permission.VIEW_APPOINTMENT,
            Permission.VIEW_CARE_PLAN,
            Permission.MANAGE_MEDICATIONS,
            Permission.VIEW_MEDICATIONS,
            Permission.VIEW_DOCUMENT,
            Permission.UPLOAD_DOCUMENT,
        },
        UserRole.APPROVER: {
            Permission.APPROVE_CARE_PLAN,
            Permission.VIEW_CARE_PLAN,
            Permission.VIEW_APPOINTMENT,
        },
        UserRole.PATIENT: {
            Permission.VIEW_APPOINTMENT,
            Permission.VIEW_CARE_PLAN,
            Permission.VIEW_MEDICATIONS,
            Permission.VIEW_DOCUMENT,
        },
    }

    @classmethod
    def has_permission(cls, user_role: UserRole, permission: Permission) -> bool:
        """Check if user role has specific permission"""
        return permission in cls.ROLE_PERMISSIONS.get(user_role, set())

    @classmethod
    def check_permission(cls, user_role: UserRole, permission: Permission) -> None:
        """Raise exception if user doesn't have permission"""
        if not cls.has_permission(user_role, permission):
            logger.warning(f"Permission denied: {user_role} lacks {permission}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User lacks required permission: {permission}"
            )

    @classmethod
    def get_role_permissions(cls, user_role: UserRole) -> Set[Permission]:
        """Get all permissions for a role"""
        return cls.ROLE_PERMISSIONS.get(user_role, set())


def require_permission(permission: Permission):
    """Decorator to enforce permission checks"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user=None, **kwargs):
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            RBACManager.check_permission(current_user.role, permission)
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator


class ResourceLevelAccess:
    """Implement resource-level access control"""

    @staticmethod
    def can_access_patient_data(user_role: UserRole, user_id: str, patient_id: str) -> bool:
        """Check if user can access specific patient's data"""
        # Patient can only access their own data
        if user_role == UserRole.PATIENT:
            return user_id == patient_id
        
        # Care coordinators, physicians, nurses can access all patients
        if user_role in [UserRole.CARE_COORDINATOR, UserRole.PHYSICIAN, UserRole.NURSE]:
            return True
        
        # Admin can access all
        if user_role == UserRole.ADMIN:
            return True
        
        return False

    @staticmethod
    def can_approve_care_plan(user_role: UserRole) -> bool:
        """Check if user can approve care plans"""
        return user_role in [UserRole.ADMIN, UserRole.APPROVER, UserRole.PHYSICIAN]

    @staticmethod
    def can_edit_care_plan(user_role: UserRole) -> bool:
        """Check if user can edit care plans"""
        return user_role in [UserRole.ADMIN, UserRole.CARE_COORDINATOR, UserRole.PHYSICIAN]
