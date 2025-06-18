import boto3
import os
from botocore.exceptions import ClientError
import logging
from werkzeug.utils import secure_filename
import mimetypes

class S3Service:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket = os.getenv('AWS_S3_BUCKET')
        
    def upload_file(self, file, prefix='invoices'):
        """Upload a file to S3 bucket."""
        try:
            # Generate secure filename
            filename = secure_filename(file.filename)
            key = f"{prefix}/{filename}"
            
            # Check file type
            content_type = mimetypes.guess_type(filename)[0]
            if content_type != 'application/pdf':
                raise ValueError("Only PDF files are allowed")
            
            # Upload file
            self.s3.upload_fileobj(
                file,
                self.bucket,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ServerSideEncryption': 'AES256'
                }
            )
            
            return key
            
        except ClientError as e:
            logging.error(f"Error uploading file to S3: {str(e)}")
            raise
            
    def get_file(self, key):
        """Get a file from S3 bucket."""
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            return response['Body']
            
        except ClientError as e:
            logging.error(f"Error getting file from S3: {str(e)}")
            raise
            
    def generate_presigned_url(self, key, expiration=3600):
        """Generate a presigned URL for file download."""
        try:
            url = self.s3.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            return url
            
        except ClientError as e:
            logging.error(f"Error generating presigned URL: {str(e)}")
            raise
            
    def delete_file(self, key):
        """Delete a file from S3 bucket."""
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=key)
        except ClientError as e:
            logging.error(f"Error deleting file from S3: {str(e)}")
            raise
