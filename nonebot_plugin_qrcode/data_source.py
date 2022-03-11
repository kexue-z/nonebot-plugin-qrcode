import qrcode
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import ImageColorMask
from typing import Optional


def generate_qrcode(
    data: str,
    embeded_image: Optional[bytes] = None,
    mask_image: Optional[bytes] = None,
) -> Image:

    qr = qrcode.QRCode(
        error_correction=qrcode.ERROR_CORRECT_H,
        box_size=10,
        border=1,
    )
    qr.add_data(data)

    img: Image = qr.make_image(
        image_factory=StyledPilImage if (embeded_image or mask_image) else None,
        embeded_image=embeded_image if embeded_image else None,
        color_mask=ImageColorMask(mask_image) if mask_image else None,
    )

    return img
