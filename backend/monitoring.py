"""Monitoring configuration for CloudWatch and logging."""
import os
import json
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
from time import time
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from typing import Any, Callable, Dict

class CloudWatchHandler:
    """Handler for sending logs to AWS CloudWatch."""
    
    def __init__(self, log_group: str, region: str):
        """Initialize CloudWatch client."""
        self.log_group = log_group
        self.client = boto3.client('logs', region_name=region)
        self._ensure_log_group_exists()
        
    def _ensure_log_group_exists(self) -> None:
        """Create log group if it doesn't exist."""
        try:
            self.client.create_log_group(logGroupName=self.log_group)
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                raise
                
    def send_log(self, log_stream: str, message: str, level: str = 'INFO') -> None:
        """Send a log message to CloudWatch."""
        try:
            # Create log stream if it doesn't exist
            try:
                self.client.create_log_stream(
                    logGroupName=self.log_group,
                    logStreamName=log_stream
                )
            except ClientError as e:
                if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                    raise
            
            # Send log event
            self.client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=log_stream,
                logEvents=[{
                    'timestamp': int(time() * 1000),
                    'message': json.dumps({
                        'level': level,
                        'message': message,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    })
                }]
            )
        except Exception as e:
            logging.error(f"Failed to send log to CloudWatch: {str(e)}")

class MetricsClient:
    """Client for sending custom metrics to CloudWatch."""
    
    def __init__(self, namespace: str, region: str):
        """Initialize CloudWatch client."""
        self.namespace = namespace
        self.client = boto3.client('cloudwatch', region_name=region)
        
    def put_metric(self, name: str, value: float, unit: str, dimensions: Dict[str, str]) -> None:
        """Send a metric to CloudWatch."""
        try:
            self.client.put_metric_data(
                Namespace=self.namespace,
                MetricData=[{
                    'MetricName': name,
                    'Value': value,
                    'Unit': unit,
                    'Dimensions': [
                        {'Name': k, 'Value': v} for k, v in dimensions.items()
                    ]
                }]
            )
        except Exception as e:
            logging.error(f"Failed to send metric to CloudWatch: {str(e)}")

def setup_logging(app_name: str, log_dir: str = 'logs') -> None:
    """Set up application logging."""
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Set up file handler
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, f'{app_name}.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    
    # Create formatters and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Set log level
    root_logger.setLevel(logging.INFO)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create CloudWatch handler if AWS credentials are available
    if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
        cloudwatch_handler = CloudWatchHandler(
            log_group=f"/lait/{app_name}",
            region=os.getenv('AWS_REGION', 'us-east-1')
        )
        root_logger.addHandler(cloudwatch_handler)

def track_performance(metrics_client: MetricsClient) -> Callable:
    """Decorator to track function performance metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time()
            result = func(*args, **kwargs)
            duration = time() - start_time
            
            # Send execution time metric
            metrics_client.put_metric(
                name=f"{func.__name__}_duration",
                value=duration,
                unit='Seconds',
                dimensions={
                    'Function': func.__name__,
                    'Environment': os.getenv('FLASK_ENV', 'development')
                }
            )
            
            return result
        return wrapper
    return decorator

def monitor_ml_predictions(metrics_client: MetricsClient) -> Callable:
    """Decorator to monitor ML model predictions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time()
            result = func(*args, **kwargs)
            duration = time() - start_time
            
            # Track prediction latency
            metrics_client.put_metric(
                name='ml_prediction_latency',
                value=duration,
                unit='Seconds',
                dimensions={
                    'Model': func.__name__,
                    'Environment': os.getenv('FLASK_ENV', 'development')
                }
            )
            
            # Track prediction counts
            metrics_client.put_metric(
                name='ml_prediction_count',
                value=1,
                unit='Count',
                dimensions={
                    'Model': func.__name__,
                    'Environment': os.getenv('FLASK_ENV', 'development')
                }
            )
            
            return result
        return wrapper
    return decorator
