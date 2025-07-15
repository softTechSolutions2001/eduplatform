#!/usr/bin/env python3
"""
BOM (Byte Order Mark) Removal Script
====================================

This script recursively scans a project directory and removes UTF-8 BOM
from all relevant files. It's specifically designed to fix the critical
BOM issues that prevent Python imports from working.

Usage:
    python remove_bom.py [directory_path]

If no directory is specified, it scans the current directory.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

# File extensions to process
SUPPORTED_EXTENSIONS = {
    ".py",  # Python files
    ".pyx",  # Cython files
    ".pyi",  # Python interface files
    ".js",  # JavaScript files
    ".jsx",  # React JSX files
    ".ts",  # TypeScript files
    ".tsx",  # TypeScript JSX files
    ".css",  # CSS files
    ".scss",  # SCSS files
    ".sass",  # SASS files
    ".less",  # LESS files
    ".html",  # HTML files
    ".htm",  # HTML files
    ".xml",  # XML files
    ".json",  # JSON files
    ".yaml",  # YAML files
    ".yml",  # YAML files
    ".md",  # Markdown files
    ".txt",  # Text files
    ".sql",  # SQL files
    ".sh",  # Shell scripts
    ".bat",  # Batch files
    ".ps1",  # PowerShell scripts
}

# Directories to skip (common build/cache directories)
SKIP_DIRECTORIES = {
    "__pycache__",
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    ".venv",
    "venv",
    ".env",
    "env",
    ".tox",
    "build",
    "dist",
    ".pytest_cache",
    ".coverage",
    ".mypy_cache",
    ".idea",
    ".vscode",
    "htmlcov",
    "static",
    "media",
    "logs",
    "tmp",
    "temp",
}

# UTF-8 BOM signature
UTF8_BOM = b"\xef\xbb\xbf"


class BOMRemover:
    """Handles BOM detection and removal from files."""

    def __init__(
        self,
        root_path: str,
        verbose: bool = True,
        dry_run: bool = False,
        backup: bool = False,
    ):
        self.root_path = Path(root_path).resolve()
        self.verbose = verbose
        self.dry_run = dry_run
        self.backup = backup
        self.stats = {
            "files_scanned": 0,
            "files_with_bom": 0,
            "files_processed": 0,
            "files_failed": 0,
            "directories_skipped": 0,
            "files_skipped_size": 0,
        }
        self.processed_files: List[str] = []
        self.failed_files: List[Tuple[str, str]] = []

    def should_skip_directory(self, dir_path: Path) -> bool:
        """Check if directory should be skipped."""
        return dir_path.name in SKIP_DIRECTORIES

    def should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed based on extension."""
        return file_path.suffix.lower() in SUPPORTED_EXTENSIONS

    def create_backup(self, file_path: Path) -> bool:
        """Create a backup of the file before modification."""
        if not self.backup:
            return True

        try:
            backup_path = file_path.with_suffix(file_path.suffix + ".bom-backup")
            backup_path.write_bytes(file_path.read_bytes())
            return True
        except (IOError, OSError) as e:
            if self.verbose:
                print(f"⚠️  Cannot create backup for {file_path}: {e}")
            return False

    def has_bom(self, file_path: Path) -> bool:
        """Return True if file starts with UTF-8 BOM."""
        try:
            with open(file_path, "rb") as f:
                return f.read(3) == UTF8_BOM
        except (IOError, OSError) as e:
            if self.verbose:
                print(f"⚠️  Cannot read {file_path}: {e}")
            return False

    def remove_bom(self, file_path: Path) -> bool:
        """Remove BOM from file and return success status."""
        try:
            # Check file size first (skip files > 10MB to avoid memory issues)
            file_size = file_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                self.stats["files_skipped_size"] += 1
                if self.verbose:
                    print(
                        f"⏭️  Skipping large file: {file_path.relative_to(self.root_path)} ({file_size // 1024 // 1024}MB)"
                    )
                return False

            # Memory-efficient BOM removal
            with open(file_path, "rb+") as f:
                prefix = f.read(3)
                if prefix != UTF8_BOM:
                    return False

                # Only read rest of file if BOM was found
                rest = f.read()

                if not self.dry_run:
                    # Write back without BOM
                    f.seek(0)
                    f.truncate()
                    f.write(rest)

            return True

        except (IOError, OSError) as e:
            self.failed_files.append((str(file_path), str(e)))
            if self.verbose:
                print(f"❌ Failed to process {file_path}: {e}")
            return False

    def scan_directory(self, directory: Path) -> None:
        """Recursively scan directory for files with BOM."""
        try:
            for item in directory.iterdir():
                if item.is_dir():
                    if self.should_skip_directory(item):
                        self.stats["directories_skipped"] += 1
                        if self.verbose:
                            print(
                                f"⏭️  Skipping directory: {item.relative_to(self.root_path)}"
                            )
                        continue

                    # Recursively scan subdirectory
                    self.scan_directory(item)

                elif item.is_file():
                    if self.should_process_file(item):
                        self.process_file(item)

        except (IOError, OSError, PermissionError) as e:
            if self.verbose:
                print(f"⚠️  Cannot access directory {directory}: {e}")

    def process_file(self, file_path: Path) -> None:
        """Process a single file."""
        self.stats["files_scanned"] += 1

        if self.has_bom(file_path):
            self.stats["files_with_bom"] += 1

            if self.verbose:
                relative_path = file_path.relative_to(self.root_path)
                action = "Would remove" if self.dry_run else "Removing"
                print(f"🔧 {action} BOM from: {relative_path}")

            # Create backup if requested
            if self.backup and not self.dry_run:
                if not self.create_backup(file_path):
                    self.stats["files_failed"] += 1
                    return

            if self.remove_bom(file_path):
                self.stats["files_processed"] += 1
                self.processed_files.append(str(file_path.relative_to(self.root_path)))
            else:
                self.stats["files_failed"] += 1

    def run(self) -> None:
        """Main execution method."""
        if not self.root_path.exists():
            print(f"❌ Error: Directory '{self.root_path}' does not exist!")
            sys.exit(1)

        if not self.root_path.is_dir():
            print(f"❌ Error: '{self.root_path}' is not a directory!")
            sys.exit(1)

        print(f"🔍 Scanning for BOM in: {self.root_path}")
        print(f"📁 File types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")

        if self.dry_run:
            print("🔬 DRY RUN MODE - No files will be modified")

        if self.backup:
            print("💾 BACKUP MODE - Original files will be saved as .bom-backup")

        print("─" * 60)

        # Start scanning
        self.scan_directory(self.root_path)

        # Print results
        self.print_summary()

    def print_summary(self) -> None:
        """Print execution summary."""
        print("─" * 60)
        print("📊 SUMMARY")
        print("─" * 60)

        print(f"Files scanned:       {self.stats['files_scanned']:,}")
        print(f"Files with BOM:      {self.stats['files_with_bom']:,}")
        print(f"Files processed:     {self.stats['files_processed']:,}")
        print(f"Files failed:        {self.stats['files_failed']:,}")
        print(f"Directories skipped: {self.stats['directories_skipped']:,}")
        print(f"Large files skipped: {self.stats['files_skipped_size']:,}")

        if self.processed_files:
            print(f"\n✅ Successfully processed files:")
            for file_path in sorted(self.processed_files):
                print(f"   • {file_path}")

        if self.failed_files:
            print(f"\n❌ Failed to process:")
            for file_path, error in self.failed_files:
                print(f"   • {file_path}: {error}")

        if self.stats["files_with_bom"] == 0:
            print("🎉 No BOM found in any files!")
        elif self.stats["files_processed"] == self.stats["files_with_bom"]:
            if not self.dry_run:
                print("🎉 All BOM issues have been fixed!")
            else:
                print("ℹ️  Run without --dry-run to fix these issues")
        else:
            print("⚠️  Some files could not be processed. Check the errors above.")

        # VS Code on Windows specific advice
        if self.stats["files_processed"] > 0 and not self.dry_run:
            print("\n💡 VS Code on Windows Users:")
            print("   Consider adding to .gitattributes:")
            print("   *.py text eol=lf")
            print("   *.js text eol=lf")
            print("   *.css text eol=lf")
            print("   And set VS Code: 'files.encoding': 'utf8' (without BOM)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Remove UTF-8 BOM from source code files recursively",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python remove_bom.py                    # Scan current directory
  python remove_bom.py /path/to/project   # Scan specific directory
  python remove_bom.py --dry-run          # Preview changes without modifying files
  python remove_bom.py --quiet            # Run silently (errors only)""",
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory)",
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Run silently (only show summary and errors)",
    )

    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create .bom-backup files before modification",
    )

    parser.add_argument(
        "--extensions",
        nargs="*",
        help="Additional file extensions to process (e.g., --extensions .cfg .ini)",
    )

    args = parser.parse_args()

    # Add custom extensions if provided
    if hasattr(args, "extensions") and args.extensions:
        for ext in args.extensions:
            if not ext.startswith("."):
                ext = "." + ext
            SUPPORTED_EXTENSIONS.add(ext.lower())

    # Create and run BOM remover
    remover = BOMRemover(
        root_path=args.directory,
        verbose=not args.quiet,
        dry_run=args.dry_run,
        backup=args.backup,
    )

    try:
        remover.run()
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
