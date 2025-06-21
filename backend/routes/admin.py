from flask import Blueprint, request, jsonify
from backend.db.database import get_db_session
from flask_jwt_extended import jwt_required, get_jwt_identity
from auth import role_required
from tasks import retrain_models
import json
import os

admin_bp = Blueprint('admin', __name__)

# Settings storage (in real app, would be in DB)
SETTINGS_FILE = 'config/settings.json'

def get_settings():
    """Load settings from file"""
    try:
        if not os.path.exists(SETTINGS_FILE):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
            # Create default settings
            default_settings = {
                'anomaly_threshold': 0.8,
                'high_risk_threshold': 7,
                'hourly_rate_threshold': 1.2,  # Multiplier for hourly rate comparison
                'notifications_enabled': True,
                'auto_retrain_enabled': True,
                'auto_retrain_frequency': 'monthly'  # daily, weekly, monthly
            }
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(default_settings, f, indent=2)
            return default_settings
        
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
        return {
            'anomaly_threshold': 0.8,
            'high_risk_threshold': 7,
            'hourly_rate_threshold': 1.2,
            'notifications_enabled': True,
            'auto_retrain_enabled': True,
            'auto_retrain_frequency': 'monthly'
        }

def save_settings(settings):
    """Save settings to file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {str(e)}")
        return False

@admin_bp.route('/settings', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def get_app_settings():
    """Get application settings"""
    settings = get_settings()
    return jsonify(settings)

@admin_bp.route('/settings', methods=['PUT'])
@jwt_required()
@role_required(['admin'])
def update_app_settings():
    """Update application settings"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    current_settings = get_settings()
    
    # Update only provided settings
    for key, value in data.items():
        if key in current_settings:
            current_settings[key] = value
            
    # Save updated settings
    if save_settings(current_settings):
        return jsonify({
            'message': 'Settings updated successfully',
            'settings': current_settings
        })
    else:
        return jsonify({'error': 'Failed to save settings'}), 500

@admin_bp.route('/retrain', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def trigger_model_retrain():
    """Trigger ML model retraining"""
    try:
        # Get model name if provided
        model_name = request.json.get('model') if request.json else None
        
        # Start retraining task
        task = retrain_models.delay()
        
        return jsonify({
            'message': 'Model retraining started',
            'task_id': task.id,
            'model': model_name or 'all'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to start retraining: {str(e)}'}), 500

@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def get_audit_logs():
    """Get system audit logs"""
    # In a real implementation, we would query an AuditLog table
    # For now, we'll return dummy data
    
    # Get pagination parameters
    offset = int(request.args.get('offset', 0))
    limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 per page
    
    # Get filter parameters
    action_type = request.args.get('action')
    user_id = request.args.get('user_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Dummy data
    logs = [
        {
            'id': 1,
            'user_id': 1,
            'username': 'admin@example.com',
            'action': 'LOGIN',
            'details': 'User login successful',
            'timestamp': '2023-06-15T10:30:00Z'
        },
        {
            'id': 2,
            'user_id': 1,
            'username': 'admin@example.com',
            'action': 'SETTINGS_CHANGE',
            'details': 'Updated anomaly threshold to 0.85',
            'timestamp': '2023-06-15T10:35:00Z'
        },
        {
            'id': 3,
            'user_id': 2,
            'username': 'user@example.com',
            'action': 'UPLOAD_INVOICE',
            'details': 'Uploaded invoice INV-2023-001',
            'timestamp': '2023-06-15T11:15:00Z'
        },
        {
            'id': 4,
            'user_id': 1,
            'username': 'admin@example.com',
            'action': 'MODEL_RETRAIN',
            'details': 'Initiated model retraining',
            'timestamp': '2023-06-15T14:20:00Z'
        }
    ]
    
    # Apply filters (in a real app, this would be done in the database query)
    if action_type:
        logs = [log for log in logs if log['action'] == action_type]
    if user_id:
        logs = [log for log in logs if log['user_id'] == int(user_id)]
    
    # Apply pagination
    paginated_logs = logs[offset:offset + limit]
    
    return jsonify({
        'logs': paginated_logs,
        'pagination': {
            'total': len(logs),
            'offset': offset,
            'limit': limit
        }
    })

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def get_admin_dashboard():
    """Get admin dashboard statistics"""
    session = get_db_session()
    try:
        # In a real implementation, we would query various tables
        # For now, we'll return dummy data
        
        return jsonify({
            'system_stats': {
                'users_count': 15,
                'invoices_count': 1250,
                'total_spend': 2750000,
                'avg_processing_time': 3.2  # days
            },
            'model_stats': {
                'last_retrained': '2023-06-10T08:15:00Z',
                'invoice_analyzer': {
                    'accuracy': 0.92,
                    'precision': 0.89,
                    'recall': 0.94
                },
                'risk_predictor': {
                    'accuracy': 0.85,
                    'precision': 0.82,
                    'recall': 0.88
                }
            },
            'recent_activities': [
                {
                    'action': 'Model Retraining',
                    'timestamp': '2023-06-10T08:15:00Z',
                    'status': 'completed'
                },
                {
                    'action': 'System Backup',
                    'timestamp': '2023-06-15T02:00:00Z',
                    'status': 'completed'
                },
                {
                    'action': 'User Import',
                    'timestamp': '2023-06-12T14:30:00Z',
                    'status': 'completed'
                }
            ]
        })
    except Exception as e:
        return jsonify({'error': f'Error retrieving admin dashboard: {str(e)}'}), 500
    finally:
        session.close()

@admin_bp.route('/settings', methods=['GET', 'POST'])
@jwt_required()
@role_required(['admin'])
def manage_settings():
    """Get or update application settings"""
    if request.method == 'GET':
        settings = get_settings()
        return jsonify(settings)

    if request.method == 'POST':
        new_settings = request.json
        save_settings(new_settings)
        return jsonify({'message': 'Settings updated successfully'})

@admin_bp.route('/audit-logs/report', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def audit_logs():
    """Fetch audit logs"""
    try:
        # Mocked audit logs (replace with actual implementation)
        logs = [
            {'timestamp': '2025-06-18T12:00:00Z', 'action': 'User login', 'user_id': 1},
            {'timestamp': '2025-06-18T12:05:00Z', 'action': 'Invoice upload', 'user_id': 2},
        ]
        return jsonify(logs)
    except Exception as e:
        return jsonify({'message': str(e)}), 500
