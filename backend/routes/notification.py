from flask import Blueprint, jsonify, request
from flask_socketio import SocketIO, emit
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json
from typing import Dict, List, Optional
import threading
import queue
import time

notification_bp = Blueprint('notification', __name__)
socketio = SocketIO()
notification_queue = queue.Queue()

class NotificationManager:
    def __init__(self):
        self.notifications: List[Dict] = []
        self._start_notification_worker()

    def _start_notification_worker(self):
        def worker():
            while True:
                try:
                    # Process automated notifications
                    self._check_invoice_processing()
                    self._check_risk_alerts()
                    self._check_spend_thresholds()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    print(f"Error in notification worker: {e}")

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def _check_invoice_processing(self):
        # In a real app, this would check database for new processed invoices
        pass

    def _check_risk_alerts(self):
        # In a real app, this would check for new risk alerts
        pass

    def _check_spend_thresholds(self):
        # In a real app, this would monitor spending thresholds
        pass

    def add_notification(self, notification_type: str, message: str, metadata: Optional[Dict] = None):
        notification = {
            'id': str(len(self.notifications) + 1),
            'type': notification_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'read': False,
            'metadata': metadata or {}
        }
        self.notifications.insert(0, notification)
        socketio.emit('notification', notification)
        return notification

    def get_notifications(self, limit: int = 50) -> List[Dict]:
        return self.notifications[:limit]

    def mark_as_read(self, notification_id: str) -> bool:
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                return True
        return False

    def mark_all_as_read(self) -> bool:
        for notification in self.notifications:
            notification['read'] = True
        return True

    def delete_notification(self, notification_id: str) -> bool:
        self.notifications = [n for n in self.notifications if n['id'] != notification_id]
        return True

    def clear_notifications(self) -> bool:
        self.notifications.clear()
        return True

notification_manager = NotificationManager()

@notification_bp.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    current_user = get_jwt_identity()
    limit = int(request.args.get('limit', 50))
    return jsonify(notification_manager.get_notifications(limit))

@notification_bp.route('/api/notifications/<notification_id>/read', methods=['POST'])
@jwt_required()
def mark_as_read(notification_id):
    current_user = get_jwt_identity()
    success = notification_manager.mark_as_read(notification_id)
    return jsonify({'success': success})

@notification_bp.route('/api/notifications/read-all', methods=['POST'])
@jwt_required()
def mark_all_as_read():
    current_user = get_jwt_identity()
    success = notification_manager.mark_all_as_read()
    return jsonify({'success': success})

@notification_bp.route('/api/notifications/<notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    current_user = get_jwt_identity()
    success = notification_manager.delete_notification(notification_id)
    return jsonify({'success': success})

@notification_bp.route('/api/notifications', methods=['DELETE'])
@jwt_required()
def clear_notifications():
    current_user = get_jwt_identity()
    success = notification_manager.clear_notifications()
    return jsonify({'success': success})

@socketio.on('connect')
def handle_connect():
    print('Client connected to notifications')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from notifications')

# Example notifications for testing
@notification_bp.route('/api/notifications/test', methods=['POST'])
@jwt_required()
def add_test_notification():
    current_user = get_jwt_identity()
    notification_types = ['success', 'warning', 'info', 'error']
    test_messages = [
        'New invoice processed successfully',
        'High-risk invoice detected',
        'Monthly spend report ready',
        'Failed to process invoice'
    ]
    
    for type_, message in zip(notification_types, test_messages):
        notification_manager.add_notification(type_, message)
    
    return jsonify({'success': True})
