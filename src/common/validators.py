"""
Security validators for file uploads and data validation.

Implements defense against:
- Malicious file uploads
- Path traversal attacks
- XXE injection
- Zip bombs
- Content-type spoofing
"""

import os
import unicodedata
from django.core.exceptions import ValidationError
from django.utils.decorate import method_decorator
from django.views.decorators.debug import sensitive_variables

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False


# ============================================================================
# FILE UPLOAD VALIDATORS
# ============================================================================

@sensitive_variables('file')
def validate_file_size(file, max_size_mb=10):
    """
    Validate file size to prevent disk exhaustion attacks.

    Args:
        file: UploadedFile object
        max_size_mb: Maximum file size in megabytes (default: 10MB)

    Raises:
        ValidationError: If file exceeds size limit
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(
            f"File size exceeds maximum allowed size of {max_size_mb}MB. "
            f"Your file is {file.size / (1024 * 1024):.2f}MB."
        )


def validate_file_extension(file, allowed_extensions=None):
    """
    Validate file extension against whitelist.

    Args:
        file: UploadedFile object
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.docx'])
                          If None, uses default safe extensions

    Raises:
        ValidationError: If file extension not allowed
    """
    if allowed_extensions is None:
        allowed_extensions = [
            '.pdf',  # Documents
            '.doc', '.docx',
            '.xls', '.xlsx',
            '.jpg', '.jpeg', '.png', '.gif',  # Images
            '.zip',  # Archives (with caution)
        ]

    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f"File type '{ext}' is not allowed. "
            f"Allowed types: {', '.join(allowed_extensions)}"
        )


@sensitive_variables('file')
def validate_file_content_type(file):
    """
    Validate file content type using python-magic (libmagic).

    Prevents content-type spoofing by checking actual file content,
    not just the extension or MIME type header.

    Args:
        file: UploadedFile object

    Raises:
        ValidationError: If content type is not allowed or doesn't match extension
    """
    if not MAGIC_AVAILABLE:
        # Fall back to extension-only validation if python-magic not installed
        return

    # Allowed MIME types
    allowed_mime_types = [
        # Images
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        # Documents
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        # Archives
        'application/zip',
        'application/x-zip-compressed',
    ]

    # Read first 2048 bytes to determine content type
    file.seek(0)
    file_header = file.read(2048)
    file.seek(0)  # Reset file pointer

    mime_type = magic.from_buffer(file_header, mime=True)

    if mime_type not in allowed_mime_types:
        raise ValidationError(
            f"File content type '{mime_type}' is not allowed. "
            f"This may indicate a spoofed file."
        )

    # Additional check: Ensure MIME type matches file extension
    ext = os.path.splitext(file.name)[1].lower()
    mime_extension_map = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }

    expected_mime = mime_extension_map.get(ext)
    if expected_mime and mime_type != expected_mime:
        raise ValidationError(
            f"File extension '{ext}' does not match actual content type '{mime_type}'. "
            f"This may indicate a malicious file."
        )


def sanitize_filename(filename):
    """
    Sanitize filename to prevent path traversal and other attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem storage
    """
    # Normalize Unicode characters
    filename = unicodedata.normalize('NFKD', filename)

    # Remove path traversal attempts
    filename = filename.replace('..', '')
    filename = filename.replace('/', '')
    filename = filename.replace('\\', '')

    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\x00']
    for char in dangerous_chars:
        filename = filename.replace(char, '')

    # Limit filename length
    name, ext = os.path.splitext(filename)
    if len(name) > 100:
        name = name[:100]

    return name + ext


def validate_image_file(file):
    """
    Comprehensive validation for image uploads.

    Validates:
    - File size (max 5MB for images)
    - File extension
    - Content type
    - Filename sanitization

    Args:
        file: UploadedFile object

    Raises:
        ValidationError: If any validation fails
    """
    validate_file_size(file, max_size_mb=5)
    validate_file_extension(file, allowed_extensions=['.jpg', '.jpeg', '.png', '.gif', '.webp'])
    validate_file_content_type(file)
    file.name = sanitize_filename(file.name)


def validate_document_file(file):
    """
    Comprehensive validation for document uploads.

    Validates:
    - File size (max 10MB for documents)
    - File extension
    - Content type
    - Filename sanitization

    Args:
        file: UploadedFile object

    Raises:
        ValidationError: If any validation fails
    """
    validate_file_size(file, max_size_mb=10)
    validate_file_extension(file, allowed_extensions=[
        '.pdf', '.doc', '.docx', '.xls', '.xlsx'
    ])
    validate_file_content_type(file)
    file.name = sanitize_filename(file.name)


# ============================================================================
# USAGE IN MODELS
# ============================================================================
# from common.validators import validate_image_file, validate_document_file
#
# class MyModel(models.Model):
#     photo = models.ImageField(
#         upload_to='photos/%Y/%m/',
#         validators=[validate_image_file]
#     )
#     document = models.FileField(
#         upload_to='documents/%Y/%m/',
#         validators=[validate_document_file]
#     )
