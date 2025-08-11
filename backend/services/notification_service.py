from datetime import datetime
import json
from flask_socketio import SocketIO
from db.database import get_db_session
from models.db_models import Invoice, RiskFactor, Vendor

class NotificationService:
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        
    def send_invoice_analysis_notification(self, invoice_id: int):
        """Send real-time notification for invoice analysis results"""
        session = get_db_session()
        try:
            invoice = session.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not invoice:
                return
                
            risk_factors = session.query(RiskFactor).filter(RiskFactor.invoice_id == invoice_id).all()
            
            notification = {
                'type': 'invoice_analysis',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'invoice_id': invoice.id,
                    'invoice_number': invoice.invoice_number,
                    'risk_score': invoice.risk_score,
                    'status': invoice.status,
                    'amount': float(invoice.amount),
                    'risk_factors': [
                        {
                            'type': rf.factor_type,
                            'severity': rf.severity,
                            'description': rf.description
                        } for rf in risk_factors
                    ],
                    'recommendations': invoice.analysis_result.get('recommendations', [])
                }
            }
            
            # Emit to all connected clients
            self.socketio.emit('notification', notification)
            
        finally:
            session.close()
    
    def send_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """Send a general alert notification"""
        notification = {
            'type': 'alert',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': {
                'alert_type': alert_type,
                'message': message,
                'severity': severity
            }
        }
        
        self.socketio.emit('notification', notification)
    
    def send_vendor_update(self, vendor_id: int):
        """Send notification for vendor performance updates"""
        session = get_db_session()
        try:
            # Query vendor performance data
            vendor = session.query(Vendor).filter(Vendor.id == vendor_id).first()
            if not vendor:
                return
                
            notification = {
                'type': 'vendor_update',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'data': {
                    'vendor_id': vendor.id,
                    'name': vendor.name,
                    'performance_score': vendor.performance_score,
                    'risk_profile': vendor.risk_profile,
                    'historical_performance': vendor.historical_performance
                }
            }
            
            self.socketio.emit('notification', notification)
            
        finally:
            session.close()
    
    def broadcast_system_status(self, status: dict):
        """Broadcast system status updates"""
        notification = {
            'type': 'system_status',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': status
        }
        
        self.socketio.emit('system_status', notification)
