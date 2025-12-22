import qrcode, os
from django.conf import settings

def generate_qr(link, filename):
    img = qrcode.make(link)
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr', f'{filename}.png')
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    img.save(qr_path)
    return f'qr/{filename}.png'
