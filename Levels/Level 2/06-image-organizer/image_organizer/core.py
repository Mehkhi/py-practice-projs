"""
Core image organization functionality.
"""

import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image, ExifTags
import imagehash


logger = logging.getLogger(__name__)

# Supported image extensions
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif'}


class ImageOrganizer:
    """Main class for organizing images by date."""

    def __init__(self, source_dir: str, target_dir: str, dry_run: bool = False,
                 create_thumbnails: bool = False, thumbnail_size: tuple = (150, 150),
                 custom_naming: str = None):
        """
        Initialize the image organizer.

        Args:
            source_dir: Directory containing images to organize
            target_dir: Directory where organized images will be placed
            dry_run: If True, don't actually move files, just report what would be done
            create_thumbnails: If True, create thumbnails for organized images
            thumbnail_size: Size for thumbnails as (width, height) tuple
            custom_naming: Custom naming template (e.g., "{date}_{original_name}")
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.dry_run = dry_run
        self.create_thumbnails = create_thumbnails
        self.thumbnail_size = thumbnail_size
        self.custom_naming = custom_naming
        self.stats = {
            'processed': 0,
            'moved': 0,
            'skipped': 0,
            'errors': 0,
            'duplicates_found': 0,
            'thumbnails_created': 0
        }
        self.duplicate_hashes = {}

        # Create target directory if it doesn't exist
        if not self.dry_run:
            self.target_dir.mkdir(parents=True, exist_ok=True)

    def scan_images(self) -> List[Path]:
        """
        Scan the source directory for supported image files.

        Returns:
            List of image file paths
        """
        logger.info(f"Scanning directory: {self.source_dir}")
        images = []

        if not self.source_dir.exists():
            logger.error(f"Source directory does not exist: {self.source_dir}")
            return images

        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                images.append(file_path)

        logger.info(f"Found {len(images)} image files")
        return images

    def get_image_date(self, image_path: Path) -> Optional[datetime]:
        """
        Extract date from image EXIF data or use file modification time as fallback.

        Args:
            image_path: Path to the image file

        Returns:
            datetime object or None if no date can be determined
        """
        try:
            with Image.open(image_path) as img:
                exif = img._getexif()

                if exif is not None:
                    # Look for DateTime or DateTimeOriginal in EXIF
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        if tag in ['DateTime', 'DateTimeOriginal']:
                            try:
                                # Parse EXIF date format: "YYYY:MM:DD HH:MM:SS"
                                date_str = str(value)
                                return datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                            except ValueError:
                                continue

                # Fallback to file modification time
                logger.debug(f"No EXIF date found for {image_path}, using modification time")
                mtime = image_path.stat().st_mtime
                return datetime.fromtimestamp(mtime)

        except Exception as e:
            logger.error(f"Error reading date from {image_path}: {e}")
            # Final fallback to file modification time
            try:
                mtime = image_path.stat().st_mtime
                return datetime.fromtimestamp(mtime)
            except Exception as fallback_error:
                logger.error(f"Error reading modification time for {image_path}: {fallback_error}")
                return None

    def get_image_hash(self, image_path: Path) -> Optional[str]:
        """
        Generate perceptual hash for duplicate detection.

        Args:
            image_path: Path to the image file

        Returns:
            Hash string or None if error
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                hash_value = imagehash.average_hash(img)
                return str(hash_value)
        except Exception as e:
            logger.error(f"Error generating hash for {image_path}: {e}")
            return None

    def get_organization_path(self, image_date: datetime, image_path: Path) -> Path:
        """
        Generate the target path for organizing the image by date.

        Args:
            image_date: Date extracted from the image
            image_path: Original image path

        Returns:
            Target path for the organized image
        """
        year = image_date.year
        month = f"{image_date.month:02d}"

        # Apply custom naming if specified
        if self.custom_naming:
            filename = self._apply_custom_naming(image_date, image_path)
        else:
            filename = image_path.name

        return self.target_dir / str(year) / month / filename

    def _apply_custom_naming(self, image_date: datetime, image_path: Path) -> str:
        """
        Apply custom naming template to filename.

        Args:
            image_date: Date extracted from the image
            image_path: Original image path

        Returns:
            New filename based on template
        """
        if not self.custom_naming:
            return image_path.name

        # Available template variables
        template_vars = {
            'date': image_date.strftime('%Y%m%d'),
            'time': image_date.strftime('%H%M%S'),
            'datetime': image_date.strftime('%Y%m%d_%H%M%S'),
            'year': str(image_date.year),
            'month': f"{image_date.month:02d}",
            'day': f"{image_date.day:02d}",
            'original_name': image_path.stem,
            'extension': image_path.suffix
        }

        try:
            filename = self.custom_naming.format(**template_vars)
            # Preserve provided extension (case-insensitive) or append original suffix.
            if not Path(filename).suffix:
                filename = f"{filename}{image_path.suffix}"
            return filename
        except KeyError as e:
            logger.warning(f"Invalid template variable {e} in custom naming, using original name")
            return image_path.name

    def handle_duplicate(self, image_path: Path, target_path: Path) -> bool:
        """
        Handle duplicate images by checking perceptual hash.

        Args:
            image_path: Source image path
            target_path: Target image path

        Returns:
            True if this is a duplicate, False otherwise
        """
        image_hash = self.get_image_hash(image_path)
        if not image_hash:
            return False

        if image_hash in self.duplicate_hashes:
            logger.info(f"Duplicate found: {image_path} (same as {self.duplicate_hashes[image_hash]})")
            self.stats['duplicates_found'] += 1
            return True

        self.duplicate_hashes[image_hash] = image_path
        return False

    def organize_image(self, image_path: Path) -> bool:
        """
        Organize a single image file.

        Args:
            image_path: Path to the image file

        Returns:
            True if successful, False otherwise
        """
        try:
            self.stats['processed'] += 1

            # Get image date
            image_date = self.get_image_date(image_path)
            if not image_date:
                logger.warning(f"Could not determine date for {image_path}, skipping")
                self.stats['skipped'] += 1
                return False

            # Generate target path
            target_path = self.get_organization_path(image_date, image_path)

            # Check for duplicates
            if self.handle_duplicate(image_path, target_path):
                self.stats['skipped'] += 1
                return False

            # Create target directory
            if not self.dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)

            # Handle file conflicts
            if target_path.exists():
                # Generate unique filename
                counter = 1
                stem = target_path.stem
                suffix = target_path.suffix
                while target_path.exists():
                    target_path = target_path.parent / f"{stem}_{counter}{suffix}"
                    counter += 1

            # Move or copy the file
            if self.dry_run:
                logger.info(f"Would move: {image_path} -> {target_path}")
            else:
                shutil.move(str(image_path), str(target_path))
                logger.info(f"Moved: {image_path} -> {target_path}")

                # Create thumbnail if requested
                if self.create_thumbnails:
                    self._create_thumbnail(target_path)

            self.stats['moved'] += 1
            return True

        except Exception as e:
            logger.error(f"Error organizing {image_path}: {e}")
            self.stats['errors'] += 1
            return False

    def organize_images(self) -> Dict[str, int]:
        """
        Organize all images in the source directory.

        Returns:
            Dictionary with statistics about the operation
        """
        logger.info("Starting image organization")

        images = self.scan_images()
        if not images:
            logger.warning("No images found to organize")
            return self.stats

        for image_path in images:
            self.organize_image(image_path)

        logger.info("Image organization completed")
        return self.stats

    def _create_thumbnail(self, image_path: Path) -> bool:
        """
        Create a thumbnail for the given image.

        Args:
            image_path: Path to the image file

        Returns:
            True if successful, False otherwise
        """
        try:
            from .utils import create_thumbnail

            # Create thumbnail path in same directory with _thumb suffix
            thumbnail_path = image_path.parent / f"{image_path.stem}_thumb{image_path.suffix}"

            success = create_thumbnail(image_path, thumbnail_path, self.thumbnail_size)
            if success:
                self.stats['thumbnails_created'] += 1
                logger.debug(f"Created thumbnail: {thumbnail_path}")

            return success

        except Exception as e:
            logger.error(f"Error creating thumbnail for {image_path}: {e}")
            return False

    def generate_report(self) -> str:
        """
        Generate a summary report of the organization process.

        Returns:
            Formatted report string
        """
        report = [
            "=" * 50,
            "IMAGE ORGANIZATION REPORT",
            "=" * 50,
            f"Source Directory: {self.source_dir}",
            f"Target Directory: {self.target_dir}",
            f"Dry Run: {self.dry_run}",
            f"Thumbnails: {'Yes' if self.create_thumbnails else 'No'}",
            f"Custom Naming: {self.custom_naming or 'None'}",
            "",
            "STATISTICS:",
            f"  Images Processed: {self.stats['processed']}",
            f"  Images Moved: {self.stats['moved']}",
            f"  Images Skipped: {self.stats['skipped']}",
            f"  Errors: {self.stats['errors']}",
            f"  Duplicates Found: {self.stats['duplicates_found']}",
            f"  Thumbnails Created: {self.stats['thumbnails_created']}",
            "=" * 50
        ]

        return "\n".join(report)
