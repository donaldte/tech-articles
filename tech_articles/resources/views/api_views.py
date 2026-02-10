"""
API views for S3 multipart upload management
"""
import json
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext as _

from tech_articles.resources.utils.s3_manager import s3_resource_manager

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def create_multipart_upload(request):
    """
    Initialize a multipart upload for a resource document

    Request body:
        {
            "file_name": "document.pdf",
            "content_type": "application/pdf"
        }

    Response:
        {
            "uploadId": "...",
            "key": "media/resource_documents/..."
        }
    """
    try:
        data = json.loads(request.body)
        file_name = data.get('file_name')
        content_type = data.get('content_type', 'application/pdf')

        if not file_name:
            return JsonResponse({
                'error': _('File name is required')
            }, status=400)

        # Check S3 configuration
        if not s3_resource_manager.is_configured():
            return JsonResponse({
                'error': _('S3 storage is not configured')
            }, status=503)

        # Create multipart upload
        result = s3_resource_manager.create_multipart_upload(
            file_name=file_name,
            content_type=content_type,
            user_email=request.user.email
        )

        if not result:
            return JsonResponse({
                'error': _('Failed to initialize upload')
            }, status=500)

        return JsonResponse(result)

    except json.JSONDecodeError:
        return JsonResponse({
            'error': _('Invalid JSON data')
        }, status=400)
    except Exception as e:
        logger.error(f"Error creating multipart upload: {e}")
        return JsonResponse({
            'error': _('An unexpected error occurred')
        }, status=500)


@login_required
@require_http_methods(["POST"])
def generate_presigned_urls(request):
    """
    Generate presigned URLs for uploading parts

    Request body:
        {
            "key": "media/resource_documents/...",
            "uploadId": "...",
            "parts": 5
        }

    Response:
        {
            "urls": [
                {"partNumber": 1, "url": "https://..."},
                {"partNumber": 2, "url": "https://..."},
                ...
            ]
        }
    """
    try:
        data = json.loads(request.body)
        key = data.get('key')
        upload_id = data.get('uploadId')
        parts = data.get('parts')

        if not all([key, upload_id, parts]):
            return JsonResponse({
                'error': _('Missing required parameters')
            }, status=400)

        try:
            parts_count = int(parts)
            if parts_count < 1 or parts_count > 10000:
                return JsonResponse({
                    'error': _('Invalid number of parts')
                }, status=400)
        except ValueError:
            return JsonResponse({
                'error': _('Parts must be a number')
            }, status=400)

        # Generate presigned URLs
        urls = s3_resource_manager.generate_presigned_urls(
            key=key,
            upload_id=upload_id,
            parts=parts_count
        )

        if not urls:
            return JsonResponse({
                'error': _('Failed to generate presigned URLs')
            }, status=500)

        return JsonResponse({'urls': urls})

    except json.JSONDecodeError:
        return JsonResponse({
            'error': _('Invalid JSON data')
        }, status=400)
    except Exception as e:
        logger.error(f"Error generating presigned URLs: {e}")
        return JsonResponse({
            'error': _('An unexpected error occurred')
        }, status=500)


@login_required
@require_http_methods(["POST"])
def complete_multipart_upload(request):
    """
    Complete multipart upload

    Request body:
        {
            "key": "media/resource_documents/...",
            "uploadId": "...",
            "parts": [
                {"ETag": "...", "PartNumber": 1},
                {"ETag": "...", "PartNumber": 2},
                ...
            ]
        }

    Response:
        {
            "location": "https://s3.amazonaws.com/...",
            "key": "media/resource_documents/..."
        }
    """
    try:
        data = json.loads(request.body)
        key = data.get('key')
        upload_id = data.get('uploadId')
        parts = data.get('parts')

        if not all([key, upload_id, parts]):
            return JsonResponse({
                'error': _('Missing required parameters')
            }, status=400)

        if not isinstance(parts, list):
            return JsonResponse({
                'error': _('Parts must be a list')
            }, status=400)

        # Complete multipart upload
        location = s3_resource_manager.complete_multipart_upload(
            key=key,
            upload_id=upload_id,
            parts=parts
        )

        if not location:
            return JsonResponse({
                'error': _('Failed to complete upload')
            }, status=500)

        return JsonResponse({
            'location': location,
            'key': key
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': _('Invalid JSON data')
        }, status=400)
    except Exception as e:
        logger.error(f"Error completing multipart upload: {e}")
        return JsonResponse({
            'error': _('An unexpected error occurred')
        }, status=500)


@login_required
@require_http_methods(["POST"])
def abort_multipart_upload(request):
    """
    Abort multipart upload

    Request body:
        {
            "key": "media/resource_documents/...",
            "uploadId": "..."
        }

    Response:
        {
            "message": "Upload aborted successfully"
        }
    """
    try:
        data = json.loads(request.body)
        key = data.get('key')
        upload_id = data.get('uploadId')

        if not all([key, upload_id]):
            return JsonResponse({
                'error': _('Missing required parameters')
            }, status=400)

        # Abort multipart upload
        success = s3_resource_manager.abort_multipart_upload(
            key=key,
            upload_id=upload_id
        )

        if not success:
            return JsonResponse({
                'error': _('Failed to abort upload')
            }, status=500)

        return JsonResponse({
            'message': _('Upload aborted successfully')
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'error': _('Invalid JSON data')
        }, status=400)
    except Exception as e:
        logger.error(f"Error aborting multipart upload: {e}")
        return JsonResponse({
            'error': _('An unexpected error occurred')
        }, status=500)


@login_required
@require_http_methods(["POST"])
def generate_download_url(request):
    """
    Generate temporary signed URL for downloading a resource

    Request body:
        {
            "key": "media/resource_documents/...",
            "expires_in": 300
        }

    Response:
        {
            "url": "https://..."
        }
    """
    try:
        data = json.loads(request.body)
        key = data.get('key')
        expires_in = data.get('expires_in', 300)  # Default 5 minutes

        if not key:
            return JsonResponse({
                'error': _('File key is required')
            }, status=400)

        # Validate expires_in
        try:
            expires_in = int(expires_in)
            if expires_in < 60 or expires_in > 3600:  # Between 1 min and 1 hour
                expires_in = 300
        except ValueError:
            expires_in = 300

        # Generate signed URL
        url = s3_resource_manager.generate_signed_download_url(
            key=key,
            expires_in=expires_in
        )

        if not url:
            return JsonResponse({
                'error': _('Failed to generate download URL')
            }, status=500)

        return JsonResponse({'url': url})

    except json.JSONDecodeError:
        return JsonResponse({
            'error': _('Invalid JSON data')
        }, status=400)
    except Exception as e:
        logger.error(f"Error generating download URL: {e}")
        return JsonResponse({
            'error': _('An unexpected error occurred')
        }, status=500)

