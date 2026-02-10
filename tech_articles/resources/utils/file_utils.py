"""
Utility functions for file handling in resources app.
"""
import os


def truncate_filename(filename, max_length=30):
    """
    Truncate a filename intelligently.

    If the file has an extension (.pdf, .docx, etc.), truncates the middle
    while preserving the start and extension (e.g., "document...xyz.pdf").

    If no extension, truncates at the end (e.g., "longfilename...").

    Args:
        filename (str): The filename to truncate
        max_length (int): Maximum length of the truncated filename (default: 30)

    Returns:
        str: The truncated filename

    Examples:
        >>> truncate_filename("very_long_document_name.pdf", 20)
        'very_lo...me.pdf'

        >>> truncate_filename("document_without_extension", 20)
        'document_withou...'

        >>> truncate_filename("short.pdf", 20)
        'short.pdf'
    """
    if not filename:
        return ""

    # If filename is already short enough, return as is
    if len(filename) <= max_length:
        return filename

    # Split filename and extension
    name, ext = os.path.splitext(filename)

    # If there's an extension
    if ext:
        # Calculate space for name part (accounting for "..." and extension)
        available_space = max_length - len(ext) - 3  # 3 for "..."

        if available_space <= 0:
            # Extension is too long, just truncate the whole thing
            return filename[:max_length - 3] + "..."

        # Split available space between start and end of name
        start_length = available_space // 2
        end_length = available_space - start_length

        # Truncate in the middle
        truncated_name = name[:start_length] + "..." + name[-end_length:] if end_length > 0 else name[:start_length] + "..."

        return truncated_name + ext

    else:
        # No extension, truncate at the end
        return filename[:max_length - 3] + "..."


def format_file_size(size_in_bytes):
    """
    Format file size in bytes to human-readable format.

    Args:
        size_in_bytes (int): Size in bytes

    Returns:
        str: Formatted file size (e.g., "1.5 MB", "500 KB")

    Examples:
        >>> format_file_size(1024)
        '1.0 KB'

        >>> format_file_size(1048576)
        '1.0 MB'

        >>> format_file_size(500)
        '500 Bytes'
    """
    if not size_in_bytes or size_in_bytes == 0:
        return "0 Bytes"

    try:
        size_in_bytes = int(size_in_bytes)
    except (ValueError, TypeError):
        return "0 Bytes"

    units = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_in_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    # Format with appropriate decimal places
    if unit_index == 0:  # Bytes
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def get_file_icon_class(filename):
    """
    Get icon class based on file extension.

    Args:
        filename (str): The filename

    Returns:
        str: Icon class name for styling

    Examples:
        >>> get_file_icon_class("document.pdf")
        'file-pdf'

        >>> get_file_icon_class("spreadsheet.xlsx")
        'file-excel'
    """
    if not filename:
        return "file-default"

    _, ext = os.path.splitext(filename.lower())

    icon_map = {
        '.pdf': 'file-pdf',
        '.doc': 'file-word',
        '.docx': 'file-word',
        '.xls': 'file-excel',
        '.xlsx': 'file-excel',
        '.ppt': 'file-powerpoint',
        '.pptx': 'file-powerpoint',
        '.txt': 'file-text',
        '.zip': 'file-archive',
        '.rar': 'file-archive',
        '.7z': 'file-archive',
        '.tar': 'file-archive',
        '.gz': 'file-archive',
        '.jpg': 'file-image',
        '.jpeg': 'file-image',
        '.png': 'file-image',
        '.gif': 'file-image',
        '.svg': 'file-image',
        '.mp4': 'file-video',
        '.avi': 'file-video',
        '.mov': 'file-video',
        '.mp3': 'file-audio',
        '.wav': 'file-audio',
        '.csv': 'file-csv',
    }

    return icon_map.get(ext, 'file-default')

