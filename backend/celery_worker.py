from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

def make_celery():
    """
    Create a Celery instance with configuration from environment variables
    """
    # Define celery without Flask app to avoid circular imports
    celery_app = Celery(
        'backend',
        broker=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
        backend=os.getenv('REDIS_URL', 'redis://redis:6379/0')
    )
    
    # Configure Celery
    celery_app.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    
    return celery_app

# Create the celery instance
celery = make_celery()

# This will only run when celery_worker is imported directly
# It will set up the Flask context for task execution
def init_flask():
    """Initialize Flask app for Celery tasks when needed"""
    try:
        from app import create_app
        flask_app = create_app()
        
        # Update Celery with Flask config
        celery.conf.update(flask_app.config)
        
        class FlaskTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with flask_app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = FlaskTask
        return flask_app
    except ImportError:
        # If we can't import the Flask app, just continue without it
        # This allows for celery to be used in standalone mode
        print("Warning: Flask app import failed. Running Celery in standalone mode.")
        return None
