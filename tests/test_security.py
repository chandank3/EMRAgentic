"""Basic tests for Healthcare Care Coordinator Agent"""
import pytest
from datetime import datetime
from src.security.rbac import RBACManager, Permission
from src.security.pii_masking import PIIMasker, MaskingStrategy
from src.models.models import UserRole
from src.policy.policy_engine import PolicyEngine


class TestRBAC:
    """Test RBAC functionality"""
    
    def test_admin_has_all_permissions(self):
        """Admin should have all permissions"""
        permissions = RBACManager.get_role_permissions(UserRole.ADMIN)
        assert len(permissions) > 0
        assert Permission.MANAGE_USERS in permissions
        assert Permission.APPROVE_CARE_PLAN in permissions
    
    def test_patient_limited_permissions(self):
        """Patient should have limited permissions"""
        permissions = RBACManager.get_role_permissions(UserRole.PATIENT)
        assert Permission.MANAGE_USERS not in permissions
        assert Permission.APPROVE_CARE_PLAN not in permissions
        assert Permission.VIEW_APPOINTMENT in permissions
    
    def test_permission_check(self):
        """Test permission checking"""
        assert RBACManager.has_permission(UserRole.ADMIN, Permission.MANAGE_USERS)
        assert not RBACManager.has_permission(UserRole.PATIENT, Permission.MANAGE_USERS)


class TestPIIMasking:
    """Test PII masking functionality"""
    
    def test_partial_masking(self):
        """Test partial masking strategy"""
        text = "SSN: 123-45-6789"
        masked = PIIMasker.mask_pii(text, MaskingStrategy.PARTIAL)
        assert "XXX-XX" in masked
        assert "6789" in masked
    
    def test_full_masking(self):
        """Test full masking strategy"""
        text = "Email: john@example.com"
        masked = PIIMasker.mask_pii(text, MaskingStrategy.FULL)
        assert "*" in masked
        assert "john" not in masked.lower() or "@example.com" not in masked.lower()
    
    def test_dict_masking(self):
        """Test masking dictionary data"""
        data = {
            "name": "John Doe",
            "ssn": "123-45-6789",
            "email": "john@example.com"
        }
        masked = PIIMasker.mask_dict(data, MaskingStrategy.FULL)
        assert masked["ssn"] == "*" * len(data["ssn"])
        assert masked["email"] == "*" * len(data["email"])


class TestPolicyEngine:
    """Test policy engine"""
    
    def test_care_plan_validation_valid(self):
        """Test validation of valid care plan"""
        engine = PolicyEngine()
        plan = {
            "title": "Test Plan",
            "goals": ["Goal 1"],
            "coordinator_id": "coord-123"
        }
        result = engine.validate_care_plan(plan)
        assert result["valid"]
    
    def test_care_plan_validation_invalid(self):
        """Test validation of invalid care plan"""
        engine = PolicyEngine()
        plan = {
            "title": "Test Plan",
            "goals": [],  # No goals - violation
            "coordinator_id": None
        }
        result = engine.validate_care_plan(plan)
        assert not result["valid"]
        assert len(result["violations"]) > 0
    
    def test_appointment_validation(self):
        """Test appointment validation"""
        engine = PolicyEngine()
        apt = {
            "duration_minutes": 30,
            "title": "Checkup"
        }
        result = engine.validate_appointment(apt)
        assert result["valid"]
    
    def test_appointment_validation_duration_too_short(self):
        """Test appointment with invalid duration"""
        engine = PolicyEngine()
        apt = {
            "duration_minutes": 5,  # Too short
            "title": "Checkup"
        }
        result = engine.validate_appointment(apt)
        assert not result["valid"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
