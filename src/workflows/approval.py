"""Human-in-the-loop approval workflow"""
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.orm import Session
from src.models.models import ApprovalRequest, CarePlan, CarePlanStatus, User
from src.database import SessionLocal
import uuid
import logging

logger = logging.getLogger(__name__)


class ApprovalStatus(str, Enum):
    """Approval request statuses"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ApprovalWorkflow:
    """Manage approval workflows for critical actions"""

    def __init__(self, timeout_minutes: int = 60):
        self.timeout_minutes = timeout_minutes

    def create_approval_request(
        self,
        care_plan_id: str,
        request_data: Dict[str, Any],
        db: Session
    ) -> Dict:
        """Create an approval request for a care plan"""
        try:
            approval_request = ApprovalRequest(
                care_plan_id=care_plan_id,
                request_data=request_data,
                status="pending",
                requested_at=datetime.utcnow(),
            )
            db.add(approval_request)
            db.commit()
            db.refresh(approval_request)
            
            logger.info(f"Approval request {approval_request.id} created for care plan {care_plan_id}")
            
            return {
                "success": True,
                "request_id": str(approval_request.id),
                "status": "pending",
                "expires_at": (datetime.utcnow() + timedelta(minutes=self.timeout_minutes)).isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating approval request: {str(e)}")
            return {"success": False, "error": str(e)}

    def approve_request(
        self,
        request_id: str,
        approver_id: str,
        db: Session,
        reason: Optional[str] = None
    ) -> Dict:
        """Approve a pending request"""
        try:
            approval_request = db.query(ApprovalRequest).filter_by(id=request_id).first()
            if not approval_request:
                return {"success": False, "error": "Request not found"}

            if approval_request.status != "pending":
                return {"success": False, "error": f"Request already {approval_request.status}"}

            # Check if request has expired
            if self._is_expired(approval_request):
                approval_request.status = "expired"
                db.commit()
                return {"success": False, "error": "Request has expired"}

            # Update approval request
            approval_request.status = "approved"
            approval_request.approver_id = approver_id
            approval_request.decision_at = datetime.utcnow()
            approval_request.decision_reason = reason or "Approved"

            # Update care plan status
            care_plan = db.query(CarePlan).filter_by(id=approval_request.care_plan_id).first()
            if care_plan:
                care_plan.status = CarePlanStatus.APPROVED
                care_plan.approved_at = datetime.utcnow()

            db.commit()
            logger.info(f"Approval request {request_id} approved by {approver_id}")

            return {
                "success": True,
                "request_id": request_id,
                "status": "approved",
                "care_plan_id": str(approval_request.care_plan_id)
            }
        except Exception as e:
            logger.error(f"Error approving request: {str(e)}")
            db.rollback()
            return {"success": False, "error": str(e)}

    def reject_request(
        self,
        request_id: str,
        approver_id: str,
        db: Session,
        reason: str
    ) -> Dict:
        """Reject a pending request"""
        try:
            approval_request = db.query(ApprovalRequest).filter_by(id=request_id).first()
            if not approval_request:
                return {"success": False, "error": "Request not found"}

            approval_request.status = "rejected"
            approval_request.approver_id = approver_id
            approval_request.decision_at = datetime.utcnow()
            approval_request.decision_reason = reason

            # Keep care plan in draft status
            care_plan = db.query(CarePlan).filter_by(id=approval_request.care_plan_id).first()
            if care_plan:
                care_plan.status = CarePlanStatus.DRAFT

            db.commit()
            logger.info(f"Approval request {request_id} rejected by {approver_id}")

            return {
                "success": True,
                "request_id": request_id,
                "status": "rejected",
                "reason": reason
            }
        except Exception as e:
            logger.error(f"Error rejecting request: {str(e)}")
            db.rollback()
            return {"success": False, "error": str(e)}

    def get_pending_requests(self, db: Session) -> list:
        """Get all pending approval requests"""
        try:
            requests = db.query(ApprovalRequest).filter_by(status="pending").all()
            
            result = []
            for req in requests:
                if not self._is_expired(req):
                    result.append({
                        "request_id": str(req.id),
                        "care_plan_id": str(req.care_plan_id),
                        "requested_at": req.requested_at.isoformat(),
                        "expires_at": (req.requested_at + timedelta(minutes=self.timeout_minutes)).isoformat(),
                        "request_data": req.request_data,
                    })
                else:
                    # Mark as expired
                    req.status = "expired"
                    db.commit()
            
            return result
        except Exception as e:
            logger.error(f"Error retrieving pending requests: {str(e)}")
            return []

    def _is_expired(self, request: ApprovalRequest) -> bool:
        """Check if approval request has expired"""
        expiry_time = request.requested_at + timedelta(minutes=self.timeout_minutes)
        return datetime.utcnow() > expiry_time
