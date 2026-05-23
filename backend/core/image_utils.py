from io import BytesIO
import os
from django.core.files.base import ContentFile
from PIL import Image


MAX_WIDTH = 1600
MAX_HEIGHT = 1600
JPEG_QUALITY = 82


def optimize_image_field(instance, field_name):
    field = getattr(instance, field_name, None)
    if not field or not field.name:
        return
    try:
        field.open('rb')
        raw = field.read()
        field.close()
        img = Image.open(BytesIO(raw))
        fmt = img.format or 'JPEG'
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
            fmt = 'JPEG'
        changed = False
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            img.thumbnail((MAX_WIDTH, MAX_HEIGHT), Image.LANCZOS)
            changed = True
        if fmt == 'JPEG' or changed:
            out = BytesIO()
            img.save(out, format='JPEG', quality=JPEG_QUALITY, optimize=True)
            out.seek(0)
            base = os.path.splitext(os.path.basename(field.name))[0]
            new_name = f"{base}.jpg"
            field.save(new_name, ContentFile(out.read()), save=False)
    except Exception:
        pass
