from celery import Celery
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

def make_celery(app=None):
    """
    Create a Celery instance with the Flask app's configuration
    """
    app = app or create_app()
    
    celery = Celery(
        app.import_name,
        broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def create_app():
    """
    Create Flask app for Celery to use app's config
    """
    from app import app
    return app

# Create the celery instance
celery = make_celery()
