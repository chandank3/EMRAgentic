"""PII (Personally Identifiable Information) masking utilities"""
import re
from typing import Dict, Any, List, Optional
from enum import Enum
import hashlib
import logging

logger = logging.getLogger(__name__)


class MaskingStrategy(str, Enum):
    """PII masking strategies"""
    PARTIAL = "partial"  # Show first and last characters
    FULL = "full"        # Complete masking
    HASH = "hash"         # Hash value


class PIIType(str, Enum):
    """Types of PII that need masking"""
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    PHONE = "phone"
    EMAIL = "email"
    ADDRESS = "address"
    DATE_OF_BIRTH = "dob"
    MRN = "mrn"  # Medical Record Number


class PIIMasker:
    """Utilities for masking PII in data"""

    # PII detection patterns
    PATTERNS = {
        PIIType.SSN: r"\b\d{3}-\d{2}-\d{4}\b",
        PIIType.CREDIT_CARD: r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",
        PIIType.PHONE: r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        PIIType.EMAIL: r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        PIIType.ADDRESS: r"\b\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|boulevard|blvd)",
        PIIType.DATE_OF_BIRTH: r"\b(?:0?[1-9]|1[0-2])/(?:0?[1-9]|[12]\d|3[01])/\d{4}\b",
        PIIType.MRN: r"\bMRN[:\s]+(\d+)\b",
    }

    @staticmethod
    def mask_pii(data: str, strategy: MaskingStrategy = MaskingStrategy.PARTIAL) -> str:
        """Mask PII in text data"""
        masked_data = data
        
        for pii_type, pattern in PIIMasker.PATTERNS.items():
            matches = re.finditer(pattern, masked_data, re.IGNORECASE)
            
            for match in matches:
                original = match.group(0)
                
                if strategy == MaskingStrategy.PARTIAL:
                    masked = PIIMasker._partial_mask(original, pii_type)
                elif strategy == MaskingStrategy.FULL:
                    masked = PIIMasker._full_mask(original)
                elif strategy == MaskingStrategy.HASH:
                    masked = PIIMasker._hash_mask(original)
                else:
                    masked = original
                
                masked_data = masked_data.replace(original, masked)
                logger.debug(f"Masked {pii_type}: {original} -> {masked}")
        
        return masked_data

    @staticmethod
    def _partial_mask(value: str, pii_type: PIIType) -> str:
        """Partial masking - show first and last characters"""
        if len(value) <= 4:
            return "*" * len(value)
        
        if pii_type == PIIType.SSN:
            return f"XXX-XX-{value[-4:]}"
        elif pii_type == PIIType.CREDIT_CARD:
            return f"****-****-****-{value[-4:]}"
        elif pii_type == PIIType.PHONE:
            return f"(XXX) XXX-{value[-4:]}"
        elif pii_type == PIIType.EMAIL:
            parts = value.split("@")
            if len(parts) == 2:
                user, domain = parts
                masked_user = f"{user[0]}{'*' * (len(user) - 2)}{user[-1]}"
                return f"{masked_user}@{domain}"
        
        return f"{value[0]}{'*' * (len(value) - 2)}{value[-1]}"

    @staticmethod
    def _full_mask(value: str) -> str:
        """Complete masking"""
        return "*" * len(value)

    @staticmethod
    def _hash_mask(value: str) -> str:
        """Hash masking"""
        hash_obj = hashlib.sha256(value.encode())
        hash_str = hash_obj.hexdigest()[:8]
        return f"[HASH:{hash_str}]"

    @staticmethod
    def mask_dict(data: Dict[str, Any], strategy: MaskingStrategy = MaskingStrategy.PARTIAL) -> Dict[str, Any]:
        """Mask PII in dictionary"""
        masked_data = {}
        
        pii_fields = [
            "ssn", "social_security", "credit_card", "phone", "email",
            "address", "dob", "date_of_birth", "mrn", "medical_record_number"
        ]
        
        for key, value in data.items():
            if isinstance(value, str):
                # Check if field name suggests PII
                if any(pii in key.lower() for pii in pii_fields):
                    masked_data[key] = PIIMasker._full_mask(value)
                else:
                    # Check content for PII patterns
                    masked_data[key] = PIIMasker.mask_pii(value, strategy)
            elif isinstance(value, dict):
                masked_data[key] = PIIMasker.mask_dict(value, strategy)
            elif isinstance(value, list):
                masked_data[key] = [
                    PIIMasker.mask_dict(item, strategy) if isinstance(item, dict)
                    else PIIMasker.mask_pii(str(item), strategy) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                masked_data[key] = value
        
        return masked_data

    @staticmethod
    def redact_sensitive_fields(data: Dict[str, Any], fields_to_redact: List[str]) -> Dict[str, Any]:
        """Redact specific fields from data"""
        redacted_data = data.copy()
        
        for field in fields_to_redact:
            if field in redacted_data:
                redacted_data[field] = "[REDACTED]"
        
        return redacted_data


class DataClassificationLevel(str, Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class AccessControlList:
    """Fine-grained access control for sensitive data"""

    def __init__(self):
        self.classifications: Dict[str, DataClassificationLevel] = {}
        self.role_access: Dict[str, set] = {}

    def classify_data(self, data_id: str, level: DataClassificationLevel) -> None:
        """Classify data by sensitivity level"""
        self.classifications[data_id] = level
        logger.info(f"Classified {data_id} as {level}")

    def grant_access(self, role: str, data_id: str) -> None:
        """Grant role access to classified data"""
        if role not in self.role_access:
            self.role_access[role] = set()
        self.role_access[role].add(data_id)

    def can_access(self, role: str, data_id: str) -> bool:
        """Check if role can access data"""
        if role not in self.role_access:
            return False
        return data_id in self.role_access[role]
