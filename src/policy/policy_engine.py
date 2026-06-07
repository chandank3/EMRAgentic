"""Policy engine for validating actions against organizational policies"""
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class PolicyStatus(str, Enum):
    """Policy validation status"""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class PolicyRule:
    """Single policy rule"""
    rule_id: str
    name: str
    description: str
    rule_type: str  # appointment, care_plan, medication, document, etc.
    condition: str  # Human-readable condition
    severity: str  # low, medium, high, critical
    enabled: bool = True


class PolicyEngine:
    """Validate actions against organizational policies"""

    def __init__(self):
        self.rules: Dict[str, PolicyRule] = {}
        self._initialize_default_policies()

    def _initialize_default_policies(self):
        """Initialize default policies"""
        
        # Appointment policies
        self.add_rule(PolicyRule(
            rule_id="APT001",
            name="Appointment Duration Limit",
            description="Appointments must be between 15 and 480 minutes",
            rule_type="appointment",
            condition="duration >= 15 AND duration <= 480",
            severity="medium"
        ))

        self.add_rule(PolicyRule(
            rule_id="APT002",
            name="Appointment Scheduling Window",
            description="Appointments must be scheduled within 180 days",
            rule_type="appointment",
            condition="days_in_future <= 180",
            severity="high"
        ))

        # Care plan policies
        self.add_rule(PolicyRule(
            rule_id="CP001",
            name="Care Plan Requires Approval",
            description="All care plans must be approved before activation",
            rule_type="care_plan",
            condition="status == PENDING_APPROVAL OR APPROVED",
            severity="critical"
        ))

        self.add_rule(PolicyRule(
            rule_id="CP002",
            name="Care Plan Goals Required",
            description="Care plans must have at least one goal",
            rule_type="care_plan",
            condition="goals.length > 0",
            severity="high"
        ))

        self.add_rule(PolicyRule(
            rule_id="CP003",
            name="Care Plan Coordinator Assignment",
            description="Care plans must be assigned to a care coordinator",
            rule_type="care_plan",
            condition="coordinator_id != NULL",
            severity="high"
        ))

        # Medication policies
        self.add_rule(PolicyRule(
            rule_id="MED001",
            name="Medication Must Have Start Date",
            description="All medications must have a start date",
            rule_type="medication",
            condition="start_date != NULL",
            severity="high"
        ))

        self.add_rule(PolicyRule(
            rule_id="MED002",
            name="High Risk Drug Review",
            description="High-risk medications require additional review",
            rule_type="medication",
            condition="requires_review IF high_risk_drug",
            severity="critical"
        ))

        # Document policies
        self.add_rule(PolicyRule(
            rule_id="DOC001",
            name="Document PHI Protection",
            description="All documents containing PHI must be encrypted",
            rule_type="document",
            condition="contains_phi => encryption_enabled",
            severity="critical"
        ))

        self.add_rule(PolicyRule(
            rule_id="DOC002",
            name="Document Upload Authentication",
            description="Documents can only be uploaded by authenticated users",
            rule_type="document",
            condition="uploader_authenticated == true",
            severity="high"
        ))

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a new policy rule"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added policy rule: {rule.rule_id} - {rule.name}")

    def validate_appointment(self, appointment_data: Dict) -> Dict:
        """Validate appointment against policies"""
        violations = []
        warnings = []
        
        apt_rules = [r for r in self.rules.values() if r.rule_type == "appointment" and r.enabled]
        
        for rule in apt_rules:
            if rule.rule_id == "APT001":
                duration = appointment_data.get("duration_minutes", 30)
                if not (15 <= duration <= 480):
                    violations.append({
                        "rule_id": rule.rule_id,
                        "message": f"Duration {duration} violates {rule.name}",
                        "severity": rule.severity
                    })
            
            elif rule.rule_id == "APT002":
                # Check scheduling window
                pass  # Implementation depends on appointment date
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "passed_rules": len(apt_rules) - len(violations)
        }

    def validate_care_plan(self, care_plan_data: Dict) -> Dict:
        """Validate care plan against policies"""
        violations = []
        warnings = []
        
        cp_rules = [r for r in self.rules.values() if r.rule_type == "care_plan" and r.enabled]
        
        for rule in cp_rules:
            if rule.rule_id == "CP002":
                if not care_plan_data.get("goals") or len(care_plan_data.get("goals", [])) == 0:
                    violations.append({
                        "rule_id": rule.rule_id,
                        "message": f"Care plan violates {rule.name}",
                        "severity": rule.severity
                    })
            
            elif rule.rule_id == "CP003":
                if not care_plan_data.get("coordinator_id"):
                    violations.append({
                        "rule_id": rule.rule_id,
                        "message": f"Care plan requires coordinator assignment",
                        "severity": rule.severity
                    })
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "passed_rules": len(cp_rules) - len(violations)
        }

    def validate_medication(self, medication_data: Dict) -> Dict:
        """Validate medication against policies"""
        violations = []
        warnings = []
        
        med_rules = [r for r in self.rules.values() if r.rule_type == "medication" and r.enabled]
        
        for rule in med_rules:
            if rule.rule_id == "MED001":
                if not medication_data.get("start_date"):
                    violations.append({
                        "rule_id": rule.rule_id,
                        "message": f"Medication violates {rule.name}",
                        "severity": rule.severity
                    })
            
            elif rule.rule_id == "MED002":
                if medication_data.get("is_high_risk", False):
                    warnings.append({
                        "rule_id": rule.rule_id,
                        "message": f"High-risk drug requiring additional review",
                        "severity": rule.severity
                    })
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "passed_rules": len(med_rules) - len(violations)
        }

    def validate_document(self, document_data: Dict) -> Dict:
        """Validate document against policies"""
        violations = []
        warnings = []
        
        doc_rules = [r for r in self.rules.values() if r.rule_type == "document" and r.enabled]
        
        for rule in doc_rules:
            if rule.rule_id == "DOC002":
                if not document_data.get("uploader_authenticated"):
                    violations.append({
                        "rule_id": rule.rule_id,
                        "message": f"Document upload requires authentication",
                        "severity": rule.severity
                    })
            
            elif rule.rule_id == "DOC001":
                if document_data.get("contains_phi") and not document_data.get("encrypted"):
                    violations.append({
                        "rule_id": rule.rule_id,
                        "message": f"PHI-containing document must be encrypted",
                        "severity": rule.severity
                    })
        
        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "passed_rules": len(doc_rules) - len(violations)
        }

    def get_violations_report(self) -> Dict:
        """Get summary of all policy rules"""
        return {
            "total_rules": len(self.rules),
            "enabled_rules": sum(1 for r in self.rules.values() if r.enabled),
            "rules_by_type": self._group_rules_by_type(),
            "critical_rules": [
                {
                    "rule_id": r.rule_id,
                    "name": r.name,
                    "description": r.description
                }
                for r in self.rules.values()
                if r.severity == "critical" and r.enabled
            ]
        }

    def _group_rules_by_type(self) -> Dict[str, int]:
        """Group rules by type"""
        groups = {}
        for rule in self.rules.values():
            if rule.rule_type not in groups:
                groups[rule.rule_type] = 0
            groups[rule.rule_type] += 1
        return groups
