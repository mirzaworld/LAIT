"""
Enhanced audit logging service for tracking all system events
"""
import logging
from datetime import datetime
from flask import request, g
from models import db, AuditLog
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

class AuditLogger:
    @staticmethod
    def log_event(
        event_type: str,
        event_details: Dict[Any, Any],
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        status: str = "success"
    ) -> None:
        """
        Log an auditable event to both database and log file
        
        Args:
            event_type: Type of event (e.g., 'invoice_upload', 'user_login')
            event_details: Dictionary containing event details
            resource_id: ID of the affected resource
            resource_type: Type of resource (e.g., 'invoice', 'user')
            status: Outcome status of the event
        """
        try:
            # Get user from flask g object
            user_id = getattr(g, 'user_id', None)
            
            # Create audit log entry
            audit_log = AuditLog(
                user_id=user_id,
                event_type=event_type,
                resource_type=resource_type,
                resource_id=resource_id,
                event_details=json.dumps(event_details),
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                status=status,
                timestamp=datetime.utcnow()
            )
            
            # Save to database
            db.session.add(audit_log)
            db.session.commit()
            
            # Also log to file
            log_message = (
                f"AUDIT: {event_type} | "
                f"User: {user_id} | "
                f"Resource: {resource_type}:{resource_id} | "
                f"Status: {status} | "
                f"IP: {request.remote_addr} | "
                f"Details: {json.dumps(event_details)}"
            )
            logger.info(log_message)
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            # Ensure database session is clean
            db.session.rollback()
            raise

    @staticmethod
    def log_security_event(
        event_type: str,
        event_details: Dict[Any, Any],
        severity: str = "info"
    ) -> None:
        """
        Log security-specific events with enhanced detail
        """
        try:
            user_id = getattr(g, 'user_id', None)
            
            security_details = {
                **event_details,
                "headers": dict(request.headers),
                "endpoint": request.endpoint,
                "method": request.method
            }
            
            audit_log = AuditLog(
                user_id=user_id,
                event_type=f"SECURITY_{event_type}",
                event_details=json.dumps(security_details),
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
                severity=severity,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
            logger.warning(f"SECURITY: {event_type} | User: {user_id} | Severity: {severity} | IP: {request.remote_addr}")
            
        except Exception as e:
            logger.error(f"Failed to create security audit log: {str(e)}")
            db.session.rollback()
            raise

    @staticmethod
    def get_audit_logs(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 50
    ):
        """
        Retrieve audit logs with filtering and pagination
        """
        query = AuditLog.query
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
            
        return query.order_by(AuditLog.timestamp.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
