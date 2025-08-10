from flask import Blueprint, jsonify, request
from flask_socketio import SocketIO, emit
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json
from typing import Dict, List, Optional
import threading
import queue
import time
from db.database import get_db_session
from models.db_models import Notification, User

notification_bp = Blueprint('notification', __name__)
socketio = SocketIO()
notification_queue = queue.Queue()

class NotificationManager:
    def __init__(self):
        self._start_notification_worker()

    # ---------------- Background Worker (placeholder logic) -----------------
    def _start_notification_worker(self):
        def worker():
            while True:
                try:
                    # Future: poll for system events to generate notifications
                    time.sleep(60)
                except Exception as e:
                    print(f"Error in notification worker: {e}")
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    # ---------------- Persistence Helpers -----------------
    def add_notification(self, user_id: Optional[int], notification_type: str, message: str, metadata: Optional[Dict] = None):
        session = get_db_session()
        try:
            notif = Notification(
                user_id=user_id,
                type=notification_type,
                content={
                    'message': message,
                    'metadata': metadata or {}
                },
                read=False
            )
            session.add(notif)
            session.commit()
            payload = self._serialize(notif)
            socketio.emit('notification', payload)
            return payload
        finally:
            session.close()

    def get_notifications(self, user_id: int, limit: int = 50) -> List[Dict]:
        session = get_db_session()
        try:
            q = session.query(Notification).filter((Notification.user_id == user_id) | (Notification.user_id.is_(None)))\
                .order_by(Notification.created_at.desc()).limit(limit)
            return [self._serialize(n) for n in q]
        finally:
            session.close()

    def mark_as_read(self, user_id: int, notification_id: int) -> bool:
        session = get_db_session()
        try:
            notif = session.query(Notification).filter(Notification.id == notification_id, ((Notification.user_id == user_id) | (Notification.user_id.is_(None)))).first()
            if not notif:
                return False
            notif.read = True
            notif.read_at = datetime.utcnow()
            session.commit()
            return True
        finally:
            session.close()

    def mark_all_as_read(self, user_id: int) -> int:
        session = get_db_session()
        try:
            q = session.query(Notification).filter(((Notification.user_id == user_id) | (Notification.user_id.is_(None))), Notification.read.is_(False))
            count = 0
            for notif in q:
                notif.read = True
                notif.read_at = datetime.utcnow()
                count += 1
            session.commit()
            return count
        finally:
            session.close()

    def unread_count(self, user_id: int) -> int:
        session = get_db_session()
        try:
            return session.query(Notification).filter(((Notification.user_id == user_id) | (Notification.user_id.is_(None))), Notification.read.is_(False)).count()
        finally:
            session.close()

    def delete_notification(self, user_id: int, notification_id: int) -> bool:
        session = get_db_session()
        try:
            notif = session.query(Notification).filter(Notification.id == notification_id, ((Notification.user_id == user_id) | (Notification.user_id.is_(None)))).first()
            if not notif:
                return False
            session.delete(notif)
            session.commit()
            return True
        finally:
            session.close()

    def clear_notifications(self, user_id: int) -> int:
        session = get_db_session()
        try:
            q = session.query(Notification).filter(((Notification.user_id == user_id) | (Notification.user_id.is_(None))))
            count = q.count()
            q.delete(synchronize_session=False)
            session.commit()
            return count
        finally:
            session.close()

    def _serialize(self, notif: Notification) -> Dict:
        return {
            'id': notif.id,
            'type': notif.type,
            'message': (notif.content or {}).get('message'),
            'metadata': (notif.content or {}).get('metadata', {}),
            'timestamp': (notif.created_at or datetime.utcnow()).isoformat() + 'Z',
            'read': bool(notif.read),
            'readAt': notif.read_at.isoformat() + 'Z' if notif.read_at else None
        }

notification_manager = NotificationManager()

# ---------------- Routes -----------------
@notification_bp.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    user_id = get_jwt_identity()
    limit = int(request.args.get('limit', 50))
    return jsonify(notification_manager.get_notifications(int(user_id), limit))

@notification_bp.route('/api/notifications/unread-count', methods=['GET'])
@jwt_required()
def unread_count():
    user_id = get_jwt_identity()
    return jsonify({'unread': notification_manager.unread_count(int(user_id))})

@notification_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_as_read(notification_id):
    user_id = get_jwt_identity()
    success = notification_manager.mark_as_read(int(user_id), notification_id)
    return jsonify({'success': success})

@notification_bp.route('/api/notifications/read-all', methods=['POST'])
@jwt_required()
def mark_all_as_read():
    user_id = get_jwt_identity()
    count = notification_manager.mark_all_as_read(int(user_id))
    return jsonify({'updated': count})

@notification_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification_route(notification_id):
    user_id = get_jwt_identity()
    success = notification_manager.delete_notification(int(user_id), notification_id)
    return jsonify({'success': success})

@notification_bp.route('/api/notifications', methods=['DELETE'])
@jwt_required()
def clear_all_notifications():
    user_id = get_jwt_identity()
    count = notification_manager.clear_notifications(int(user_id))
    return jsonify({'deleted': count})

# Example bulk test notifications
@notification_bp.route('/api/notifications/test', methods=['POST'])
@jwt_required()
def add_test_notification():
    user_id = get_jwt_identity()
    notification_types = ['success', 'warning', 'info', 'error']
    test_messages = [
        'New invoice processed successfully',
        'High-risk invoice detected',
        'Monthly spend report ready',
        'Failed to process invoice'
    ]
    created = []
    for type_, message in zip(notification_types, test_messages):
        created.append(notification_manager.add_notification(int(user_id), type_, message))
    return jsonify({'created': created})

@socketio.on('connect')
def handle_connect():
    print('Client connected to notifications')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from notifications')
