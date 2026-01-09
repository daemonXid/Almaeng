"""
📁 Media Module

Media file management with optimization.

Features:
- File upload handling
- Image optimization and resizing
- Multiple storage backends (local, S3)
- CDN-ready URL generation

Usage:
    from domains.base.media.interface import upload_file, get_media_url

    media = upload_file(request.FILES['image'], user=request.user)
    url = get_media_url(media)
"""
