#!/usr/bin/env python3
"""
Batch convert .docx files to PDF
Preserves directory structure
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple
import subprocess
import platform
from docx2pdf import convert as docx2pdf_convert
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocxToPdfConverter:
    def __init__(self, input_dir: str = "data/raw", skip_existing: bool = True):
        self.input_dir = Path(input_dir)
        self.skip_existing = skip_existing
        self.converted_count = 0
        self.skipped_count = 0
        self.failed_count = 0
        self.failed_files = []
        
    def find_docx_files(self) -> List[Path]:
        """Find all .docx files in the directory tree."""
        docx_files = list(self.input_dir.rglob("*.docx"))
        # Exclude temporary files
        docx_files = [f for f in docx_files if not f.name.startswith("~")]
        logger.info(f"Found {len(docx_files)} .docx files")
        return docx_files
    
    def convert_file(self, docx_path: Path) -> bool:
        """Convert a single .docx file to PDF."""
        # Generate PDF path (same directory, different extension)
        pdf_path = docx_path.with_suffix('.pdf')
        
        # Skip if PDF already exists and skip_existing is True
        if self.skip_existing and pdf_path.exists():
            logger.debug(f"Skipping (PDF exists): {docx_path.name}")
            self.skipped_count += 1
            return True
        
        try:
            logger.info(f"Converting: {docx_path.relative_to(self.input_dir)}")
            
            # Use docx2pdf for conversion
            docx2pdf_convert(str(docx_path), str(pdf_path))
            
            self.converted_count += 1
            logger.info(f"✓ Converted: {pdf_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to convert {docx_path.name}: {str(e)}")
            self.failed_count += 1
            self.failed_files.append((docx_path, str(e)))
            return False
    
    def convert_with_libreoffice(self, docx_path: Path, pdf_path: Path) -> bool:
        """Alternative conversion using LibreOffice (cross-platform)."""
        try:
            # Find LibreOffice executable
            if platform.system() == "Darwin":  # macOS
                libreoffice_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
            elif platform.system() == "Windows":
                libreoffice_path = "C:\\Program Files\\LibreOffice\\program\\soffice.exe"
            else:  # Linux
                libreoffice_path = "libreoffice"
            
            # Check if LibreOffice exists
            if not os.path.exists(libreoffice_path) and platform.system() != "Linux":
                raise FileNotFoundError(f"LibreOffice not found at {libreoffice_path}")
            
            # Convert using LibreOffice
            cmd = [
                libreoffice_path,
                "--headless",
                "--convert-to", "pdf",
                "--outdir", str(docx_path.parent),
                str(docx_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            else:
                raise Exception(f"LibreOffice error: {result.stderr}")
                
        except Exception as e:
            logger.debug(f"LibreOffice conversion failed: {str(e)}")
            return False
    
    def batch_convert(self) -> Tuple[int, int, int]:
        """Convert all .docx files to PDF."""
        docx_files = self.find_docx_files()
        
        if not docx_files:
            logger.info("No .docx files found to convert")
            return 0, 0, 0
        
        logger.info(f"Starting batch conversion of {len(docx_files)} files...")
        logger.info(f"Skip existing PDFs: {self.skip_existing}")
        
        for i, docx_file in enumerate(docx_files, 1):
            logger.info(f"\n[{i}/{len(docx_files)}] Processing...")
            self.convert_file(docx_file)
        
        # Print summary
        logger.info("\n" + "="*50)
        logger.info("CONVERSION SUMMARY")
        logger.info("="*50)
        logger.info(f"Total files found: {len(docx_files)}")
        logger.info(f"✓ Converted: {self.converted_count}")
        logger.info(f"⏭ Skipped (existing): {self.skipped_count}")
        logger.info(f"✗ Failed: {self.failed_count}")
        
        if self.failed_files:
            logger.error("\nFailed conversions:")
            for file_path, error in self.failed_files:
                logger.error(f"  - {file_path.name}: {error}")
        
        return self.converted_count, self.skipped_count, self.failed_count
    
    def generate_report(self) -> None:
        """Generate a detailed conversion report."""
        report_path = self.input_dir / "pdf_conversion_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("PDF CONVERSION REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Statistics
            f.write(f"Total .docx files found: {self.converted_count + self.skipped_count + self.failed_count}\n")
            f.write(f"Successfully converted: {self.converted_count}\n")
            f.write(f"Skipped (PDF exists): {self.skipped_count}\n")
            f.write(f"Failed conversions: {self.failed_count}\n\n")
            
            # List all conversions by directory
            docx_files = self.find_docx_files()
            current_dir = None
            
            f.write("CONVERSIONS BY DIRECTORY:\n")
            f.write("-" * 50 + "\n\n")
            
            for docx_file in sorted(docx_files):
                if docx_file.parent != current_dir:
                    current_dir = docx_file.parent
                    rel_dir = current_dir.relative_to(self.input_dir)
                    f.write(f"\n{rel_dir}/\n")
                
                pdf_file = docx_file.with_suffix('.pdf')
                status = "✓" if pdf_file.exists() else "✗"
                f.write(f"  {status} {docx_file.name}\n")
            
            # Failed files detail
            if self.failed_files:
                f.write("\n\nFAILED CONVERSIONS DETAIL:\n")
                f.write("-" * 50 + "\n")
                for file_path, error in self.failed_files:
                    f.write(f"\nFile: {file_path.relative_to(self.input_dir)}\n")
                    f.write(f"Error: {error}\n")
        
        logger.info(f"\nDetailed report saved to: {report_path}")


def main():
    """Main function to run the converter."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch convert .docx files to PDF")
    parser.add_argument(
        "--input-dir",
        default="data/raw",
        help="Input directory containing .docx files (default: data/raw)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force conversion even if PDF already exists"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed conversion report"
    )
    
    args = parser.parse_args()
    
    # Create converter
    converter = DocxToPdfConverter(
        input_dir=args.input_dir,
        skip_existing=not args.force
    )
    
    # Run conversion
    converted, skipped, failed = converter.batch_convert()
    
    # Generate report if requested
    if args.report:
        converter.generate_report()
    
    # Exit with error code if any conversions failed
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()