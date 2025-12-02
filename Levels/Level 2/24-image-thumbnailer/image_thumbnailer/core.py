"""Core image thumbnail generation functionality."""

import logging
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}


def resize_image(
    image: Image.Image, size: Tuple[int, int], maintain_aspect: bool = True
) -> Image.Image:
    """Resize an image to the specified size.

    Args:
        image: PIL Image object
        size: Target size as (width, height)
        maintain_aspect: Whether to maintain aspect ratio

    Returns:
        Resized PIL Image object
    """
    if maintain_aspect:
        image.thumbnail(size, Image.Resampling.LANCZOS)
    else:
        image = image.resize(size, Image.Resampling.LANCZOS)
    return image


def add_watermark(
    image: Image.Image, text: str, position: str = "bottom-right", opacity: float = 0.5
) -> Image.Image:
    """Add a text watermark to an image.

    Args:
        image: PIL Image object
        text: Watermark text
        position: Position ('bottom-right', 'bottom-left', 'top-right', 'top-left')
        opacity: Opacity of watermark (0.0 to 1.0)

    Returns:
        Image with watermark
    """
    # Create a copy to avoid modifying original
    img = image.copy()

    # Create watermark layer
    watermark = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)

    # Try to use default font, fallback to basic
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()

    # Calculate text position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    positions = {
        "bottom-right": (img.width - text_width - 10, img.height - text_height - 10),
        "bottom-left": (10, img.height - text_height - 10),
        "top-right": (img.width - text_width - 10, 10),
        "top-left": (10, 10),
    }

    x, y = positions.get(position, positions["bottom-right"])

    # Draw text with opacity
    alpha = int(255 * opacity)
    draw.text((x, y), text, fill=(255, 255, 255, alpha), font=font)

    # Composite watermark onto image
    img = Image.alpha_composite(img.convert("RGBA"), watermark)
    return img.convert("RGB")


def add_border(
    image: Image.Image, border_width: int = 5, color: str = "black"
) -> Image.Image:
    """Add a border to an image.

    Args:
        image: PIL Image object
        border_width: Width of border in pixels
        color: Border color

    Returns:
        Image with border
    """
    # Create new image with border space
    new_size = (image.width + 2 * border_width, image.height + 2 * border_width)
    bordered = Image.new("RGB", new_size, color)

    # Paste original image in center
    bordered.paste(image, (border_width, border_width))

    return bordered


def preserve_exif_orientation(image: Image.Image) -> Image.Image:
    """Apply EXIF orientation to correct image rotation.

    Args:
        image: PIL Image object

    Returns:
        Correctly oriented PIL Image object
    """
    try:
        exif = image.getexif()
        if exif is not None:
            orientation = exif.get(274)  # 274 is the orientation tag
            if orientation == 3:
                image = image.rotate(180, expand=True)
            elif orientation == 6:
                image = image.rotate(270, expand=True)
            elif orientation == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # EXIF not available or malformed
        pass

    return image


def create_thumbnail(
    input_path: Path,
    output_path: Path,
    size: Tuple[int, int],
    maintain_aspect: bool = True,
    watermark_text: Optional[str] = None,
    border_width: int = 0,
    quality: int = 85,
) -> bool:
    """Create a thumbnail from an image file.

    Args:
        input_path: Path to input image
        output_path: Path to save thumbnail
        size: Target size as (width, height)
        maintain_aspect: Whether to maintain aspect ratio
        watermark_text: Optional watermark text
        border_width: Border width in pixels
        quality: JPEG quality (1-100)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate input
        if not input_path.exists():
            logger.error(f"Input file does not exist: {input_path}")
            return False

        if input_path.suffix.lower() not in SUPPORTED_FORMATS:
            logger.error(f"Unsupported format: {input_path.suffix}")
            return False

        # Open and process image
        with Image.open(input_path) as img:
            # Preserve EXIF orientation
            img = preserve_exif_orientation(img)

            # Convert to RGB if necessary
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            # Resize
            img = resize_image(img, size, maintain_aspect)

            # Add watermark if specified
            if watermark_text:
                img = add_watermark(img, watermark_text)

            # Add border if specified
            if border_width > 0:
                img = add_border(img, border_width)

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save with appropriate format
            suffix = output_path.suffix.lower()
            if suffix in (".jpg", ".jpeg"):
                img.save(output_path, "JPEG", quality=quality, optimize=True)
            elif suffix == ".png":
                img.save(output_path, "PNG", optimize=True)
            elif suffix == ".webp":
                img.save(output_path, "WEBP", quality=quality)
            else:
                logger.error(f"Unsupported output format: {output_path.suffix}")
                return False

            logger.info(f"Created thumbnail: {output_path}")
            return True

    except Exception as e:
        logger.error(f"Error creating thumbnail for {input_path}: {e}")
        return False


def batch_create_thumbnails(
    input_dir: Path, output_dir: Path, size: Tuple[int, int], **kwargs
) -> int:
    """Create thumbnails for all supported images in a directory.

    Args:
        input_dir: Directory containing images
        output_dir: Directory to save thumbnails
        size: Target size as (width, height)
        **kwargs: Additional arguments for create_thumbnail

    Returns:
        Number of thumbnails created successfully
    """
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    for img_path in input_dir.glob("*"):
        if img_path.suffix.lower() in SUPPORTED_FORMATS:
            output_path = output_dir / f"thumb_{img_path.name}"
            if create_thumbnail(img_path, output_path, size, **kwargs):
                success_count += 1

    logger.info(f"Created {success_count} thumbnails")
    return success_count
