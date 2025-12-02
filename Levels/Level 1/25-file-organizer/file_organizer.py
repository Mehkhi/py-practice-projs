#!/usr/bin/env python3
"""
File Organizer - A command-line tool to organize files by extension

This program scans a directory, categorizes files by their extensions,
and moves them into organized folders.
"""

import os
import shutil
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set


class FileOrganizer:
    """Main class for organizing files by extension."""

    def __init__(self, target_dir: str, dry_run: bool = False):
        """
        Initialize the FileOrganizer.

        Args:
            target_dir: Directory to organize
            dry_run: If True, only preview actions without moving files
        """
        self.target_dir = Path(target_dir)
        self.dry_run = dry_run
        self.file_categories = defaultdict(list)
        self.actions_taken = []

        # Common file extensions and their categories
        self.extension_categories = {
            # Images
            'jpg': 'Images', 'jpeg': 'Images', 'png': 'Images', 'gif': 'Images',
            'bmp': 'Images', 'svg': 'Images', 'tiff': 'Images', 'webp': 'Images',
            'ico': 'Images', 'raw': 'Images',

            # Documents
            'pdf': 'Documents', 'doc': 'Documents', 'docx': 'Documents',
            'txt': 'Documents', 'rtf': 'Documents', 'odt': 'Documents',
            'pages': 'Documents', 'md': 'Documents', 'tex': 'Documents',

            # Spreadsheets
            'xls': 'Spreadsheets', 'xlsx': 'Spreadsheets', 'csv': 'Spreadsheets',
            'ods': 'Spreadsheets', 'numbers': 'Spreadsheets',

            # Presentations
            'ppt': 'Presentations', 'pptx': 'Presentations', 'odp': 'Presentations',
            'key': 'Presentations',

            # Videos
            'mp4': 'Videos', 'avi': 'Videos', 'mov': 'Videos', 'wmv': 'Videos',
            'flv': 'Videos', 'webm': 'Videos', 'mkv': 'Videos', 'm4v': 'Videos',

            # Audio
            'mp3': 'Audio', 'wav': 'Audio', 'flac': 'Audio', 'aac': 'Audio',
            'ogg': 'Audio', 'wma': 'Audio', 'm4a': 'Audio',

            # Archives
            'zip': 'Archives', 'rar': 'Archives', '7z': 'Archives', 'tar': 'Archives',
            'gz': 'Archives', 'bz2': 'Archives', 'xz': 'Archives',

            # Code
            'py': 'Code', 'js': 'Code', 'html': 'Code', 'css': 'Code',
            'java': 'Code', 'cpp': 'Code', 'c': 'Code', 'php': 'Code',
            'rb': 'Code', 'go': 'Code', 'rs': 'Code', 'ts': 'Code',
            'json': 'Code', 'xml': 'Code', 'yaml': 'Code', 'yml': 'Code',
            'sql': 'Code', 'sh': 'Code', 'bat': 'Code', 'ps1': 'Code',

            # Executables
            'exe': 'Executables', 'msi': 'Executables', 'dmg': 'Executables',
            'pkg': 'Executables', 'deb': 'Executables', 'rpm': 'Executables',
            'app': 'Executables', 'bin': 'Executables',
        }

    def scan_directory(self) -> Dict[str, List[Path]]:
        """
        Scan the target directory for files and categorize them.

        Returns:
            Dictionary mapping categories to lists of file paths
        """
        if not self.target_dir.exists():
            raise FileNotFoundError(f"Directory '{self.target_dir}' does not exist")

        if not self.target_dir.is_dir():
            raise NotADirectoryError(f"'{self.target_dir}' is not a directory")

        print(f"Scanning directory: {self.target_dir}")

        # Reset categories
        self.file_categories = defaultdict(list)

        # Scan for files
        for item in self.target_dir.iterdir():
            if item.is_file():
                extension = item.suffix.lower().lstrip('.')
                category = self.extension_categories.get(extension, 'Other')
                self.file_categories[category].append(item)

        return dict(self.file_categories)

    def create_category_folders(self, categories: Set[str]) -> None:
        """
        Create folders for each category.

        Args:
            categories: Set of category names to create folders for
        """
        for category in categories:
            folder_path = self.target_dir / category
            if not folder_path.exists():
                if self.dry_run:
                    print(f"[DRY RUN] Would create folder: {folder_path}")
                    self.actions_taken.append(f"Would create folder: {folder_path}")
                else:
                    folder_path.mkdir(exist_ok=True)
                    print(f"Created folder: {folder_path}")
                    self.actions_taken.append(f"Created folder: {folder_path}")

    def move_files(self) -> None:
        """Move files to their respective category folders."""
        if not self.file_categories:
            print("No files to organize. Run scan_directory() first.")
            return

        # Create folders for all categories
        categories = set(self.file_categories.keys())
        self.create_category_folders(categories)

        # Move files
        for category, files in self.file_categories.items():
            category_folder = self.target_dir / category

            for file_path in files:
                destination = category_folder / file_path.name

                # Handle duplicate filenames
                counter = 1
                original_destination = destination
                while destination.exists():
                    stem = original_destination.stem
                    suffix = original_destination.suffix
                    destination = category_folder / f"{stem}_{counter}{suffix}"
                    counter += 1

                if self.dry_run:
                    print(f"[DRY RUN] Would move: {file_path.name} -> {category}/{destination.name}")
                    self.actions_taken.append(f"Would move: {file_path.name} -> {category}/{destination.name}")
                else:
                    try:
                        shutil.move(str(file_path), str(destination))
                        print(f"Moved: {file_path.name} -> {category}/{destination.name}")
                        self.actions_taken.append(f"Moved: {file_path.name} -> {category}/{destination.name}")
                    except Exception as e:
                        error_msg = f"Failed to move {file_path.name}: {e}"
                        print(f"Error: {error_msg}")
                        self.actions_taken.append(f"Error: {error_msg}")

    def generate_report(self) -> None:
        """Generate and display a report of actions taken."""
        print("\n" + "="*50)
        print("FILE ORGANIZATION REPORT")
        print("="*50)

        if not self.file_categories:
            print("No files were processed.")
            return

        # Summary by category
        print("\nFiles organized by category:")
        total_files = 0
        for category, files in self.file_categories.items():
            count = len(files)
            total_files += count
            print(f"  {category}: {count} files")

        print(f"\nTotal files processed: {total_files}")

        # Actions taken
        if self.actions_taken:
            print(f"\nActions {'planned' if self.dry_run else 'taken'}:")
            for action in self.actions_taken:
                print(f"  - {action}")

        print("\n" + "="*50)

    def organize(self) -> None:
        """Main method to organize files in the target directory."""
        try:
            # Scan directory
            categories = self.scan_directory()

            if not categories:
                print("No files found to organize.")
                return

            # Display what will be organized
            print("\nFound files to organize:")
            total_files = 0
            for category, files in categories.items():
                count = len(files)
                total_files += count
                print(f"  {category}: {count} files")
            print(f"Total: {total_files} files")

            if self.dry_run:
                print("\n[DRY RUN MODE] - No files will be moved")

            # Ask for confirmation unless in dry run mode
            if not self.dry_run and total_files > 0:
                response = input(f"\nOrganize {total_files} files? (y/N): ").strip().lower()
                if response not in ['y', 'yes']:
                    print("Operation cancelled.")
                    return

            # Move files
            self.move_files()

            # Generate report
            self.generate_report()

        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main function to run the file organizer."""
    parser = argparse.ArgumentParser(
        description="Organize files by extension into category folders"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to organize (default: current directory)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without moving files"
    )

    args = parser.parse_args()

    # Convert to absolute path
    target_dir = os.path.abspath(args.directory)

    print("File Organizer")
    print("="*50)
    print(f"Target directory: {target_dir}")
    if args.dry_run:
        print("Mode: DRY RUN (preview only)")
    print()

    organizer = FileOrganizer(target_dir, dry_run=args.dry_run)
    organizer.organize()


if __name__ == "__main__":
    main()
