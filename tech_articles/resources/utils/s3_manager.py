"""
S3 utilities for managing resource document uploads with presigned URLs
"""
import logging
import boto3
from datetime import datetime
from typing import Optional, Dict, List
from urllib.parse import urlparse, unquote
from botocore.exceptions import ClientError
from django.conf import settings

logger = logging.getLogger(__name__)


class S3ResourceManager:
    """Manager for S3 multipart uploads with presigned URLs for resource documents"""

    def __init__(self):
        self.s3_client = self._initialize_s3_client()
        self.bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
        self.region = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')

    def _initialize_s3_client(self):
        """Initialize S3 client with AWS credentials"""
        try:
            aws_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
            aws_secret = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
            aws_region = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')

            if not all([aws_key, aws_secret, aws_region]):
                logger.warning("AWS credentials not fully configured")
                return None

            return boto3.client(
                's3',
                aws_access_key_id=aws_key,
                aws_secret_access_key=aws_secret,
                region_name=aws_region
            )
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            return None

    def is_configured(self) -> bool:
        """Check if S3 is properly configured"""
        return self.s3_client is not None and self.bucket_name is not None

    def generate_resource_key(self, user_email: str, file_name: str) -> str:
        """Generate unique S3 key for a resource document"""
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # milliseconds

        # Clean file name
        safe_filename = file_name.replace(' ', '_')

        return f"media/resource_documents/{user_email}/{timestamp}/{safe_filename}"

    def create_multipart_upload(
        self,
        file_name: str,
        content_type: str,
        user_email: str
    ) -> Optional[Dict]:
        """
        Initialize multipart upload

        Returns:
            Dict with uploadId and key, or None on error
        """
        if not self.is_configured():
            logger.error("S3 not configured")
            return None

        try:
            key = self.generate_resource_key(user_email, file_name)

            response = self.s3_client.create_multipart_upload(
                Bucket=self.bucket_name,
                Key=key,
                ContentType=content_type
            )

            logger.info(f"Created multipart upload for resource: {key}")

            return {
                'uploadId': response['UploadId'],
                'key': key
            }

        except ClientError as e:
            logger.error(f"Error creating multipart upload: {e}")
            return None

    def generate_presigned_urls(
        self,
        key: str,
        upload_id: str,
        parts: int
    ) -> Optional[List[Dict]]:
        """
        Generate presigned URLs for uploading parts

        Returns:
            List of dicts with partNumber and url, or None on error
        """
        if not self.is_configured():
            return None

        try:
            urls = []

            for part_number in range(1, parts + 1):
                url = self.s3_client.generate_presigned_url(
                    'upload_part',
                    Params={
                        'Bucket': self.bucket_name,
                        'Key': key,
                        'UploadId': upload_id,
                        'PartNumber': part_number
                    },
                    ExpiresIn=3600  # 1 hour
                )

                urls.append({
                    'partNumber': part_number,
                    'url': url
                })

            logger.info(f"Generated {parts} presigned URLs for resource: {key}")
            return urls

        except ClientError as e:
            logger.error(f"Error generating presigned URLs: {e}")
            return None

    def complete_multipart_upload(
        self,
        key: str,
        upload_id: str,
        parts: List[Dict]
    ) -> Optional[str]:
        """
        Complete multipart upload

        Args:
            parts: List of dicts with ETag and PartNumber

        Returns:
            S3 location URL or None on error
        """
        if not self.is_configured():
            return None

        try:
            response = self.s3_client.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )

            logger.info(f"Completed multipart upload for resource: {key}")
            return response['Location']

        except ClientError as e:
            logger.error(f"Error completing multipart upload: {e}")
            return None

    def abort_multipart_upload(self, key: str, upload_id: str) -> bool:
        """Abort multipart upload"""
        if not self.is_configured():
            return False

        try:
            self.s3_client.abort_multipart_upload(
                Bucket=self.bucket_name,
                Key=key,
                UploadId=upload_id
            )

            logger.info(f"Aborted multipart upload for resource: {key}")
            return True

        except ClientError as e:
            logger.error(f"Error aborting multipart upload: {e}")
            return False

    def delete_object(self, key: str) -> bool:
        """Delete object from S3"""
        if not self.is_configured():
            return False

        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )

            logger.info(f"Deleted resource object: {key}")
            return True

        except ClientError as e:
            logger.error(f"Error deleting object: {e}")
            return False

    def generate_signed_download_url(
        self,
        key: str,
        expires_in: int = 300
    ) -> Optional[str]:
        """
        Generate presigned URL for downloading

        Args:
            key: S3 object key
            expires_in: URL validity in seconds (default 5 minutes)

        Returns:
            Presigned URL or None
        """
        if not self.is_configured():
            return None

        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expires_in
            )

            return url

        except ClientError as e:
            logger.error(f"Error generating download URL: {e}")
            return None

    def get_object_metadata(self, key: str) -> Optional[Dict]:
        """Get object metadata including size and content type"""
        if not self.is_configured():
            return None

        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=key
            )

            return {
                'size': response['ContentLength'],
                'content_type': response.get('ContentType', ''),
                'last_modified': response.get('LastModified')
            }

        except ClientError as e:
            logger.error(f"Error getting object metadata: {e}")
            return None


# Global instance
s3_resource_manager = S3ResourceManager()

