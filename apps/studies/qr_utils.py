"""QR code generation for study sign-up URLs."""

import io

import qrcode


def build_signup_qr_png(url: str, size_px: int = 400) -> bytes:
    """Return PNG bytes for a QR code encoding url."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    if size_px:
        img = img.resize((size_px, size_px))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()
