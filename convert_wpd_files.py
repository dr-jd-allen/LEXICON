"""
Convert WordPerfect (.wpd) files to PDF using LibreOffice
"""
import os
import subprocess
from pathlib import Path
import logging
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_wpd_files(corpus_dir):
    """Find all WPD files in the corpus"""
    wpd_files = []
    for root, dirs, files in os.walk(corpus_dir):
        for file in files:
            if file.lower().endswith('.wpd'):
                wpd_files.append(os.path.join(root, file))
    return wpd_files

def check_libreoffice():
    """Check if LibreOffice is installed"""
    # Common LibreOffice installation paths on Windows
    possible_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        r"C:\Program Files\LibreOffice 7\program\soffice.exe",
        r"C:\Program Files\LibreOffice 24.8\program\soffice.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Try to find in PATH
    soffice_path = shutil.which("soffice")
    if soffice_path:
        return soffice_path
    
    return None

def convert_wpd_to_pdf(wpd_file, output_dir, soffice_path):
    """Convert a single WPD file to PDF"""
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Run LibreOffice in headless mode to convert
        cmd = [
            soffice_path,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            wpd_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Get the output filename
            base_name = Path(wpd_file).stem
            pdf_file = os.path.join(output_dir, f"{base_name}.pdf")
            if os.path.exists(pdf_file):
                return True, pdf_file
            else:
                return False, "PDF file not created"
        else:
            return False, result.stderr
            
    except Exception as e:
        return False, str(e)

def main():
    corpus_dir = r"C:\Users\jdall\lexicon-mvp-alpha\tbi-corpus"
    
    # Find all WPD files
    wpd_files = find_wpd_files(corpus_dir)
    logger.info(f"Found {len(wpd_files)} WordPerfect files")
    
    if not wpd_files:
        logger.info("No WPD files to convert")
        return
    
    # List the files
    logger.info("\nWordPerfect files found:")
    for i, file in enumerate(wpd_files, 1):
        rel_path = os.path.relpath(file, corpus_dir)
        size_kb = os.path.getsize(file) / 1024
        logger.info(f"{i}. {rel_path} ({size_kb:.1f} KB)")
    
    # Check for LibreOffice
    soffice_path = check_libreoffice()
    
    if not soffice_path:
        logger.error("\nLibreOffice not found!")
        logger.info("\nTo convert WordPerfect files, please:")
        logger.info("1. Download LibreOffice from: https://www.libreoffice.org/download/")
        logger.info("2. Install it with default settings")
        logger.info("3. Run this script again")
        
        # Create a batch file for manual conversion
        batch_content = "@echo off\necho WordPerfect files that need conversion:\n"
        for file in wpd_files:
            batch_content += f'echo "{file}"\n'
        
        with open("wpd_files_list.bat", "w") as f:
            f.write(batch_content)
        
        logger.info("\nCreated 'wpd_files_list.bat' with list of files to convert")
        return
    
    logger.info(f"\nLibreOffice found at: {soffice_path}")
    
    # Convert files
    logger.info("\nStarting conversion...")
    converted_dir = os.path.join(corpus_dir, "converted_from_wpd")
    
    success_count = 0
    for i, wpd_file in enumerate(wpd_files, 1):
        logger.info(f"\n[{i}/{len(wpd_files)}] Converting: {Path(wpd_file).name}")
        
        # Determine output subdirectory to maintain structure
        rel_path = os.path.relpath(wpd_file, corpus_dir)
        rel_dir = os.path.dirname(rel_path)
        output_dir = os.path.join(converted_dir, rel_dir)
        
        success, result = convert_wpd_to_pdf(wpd_file, output_dir, soffice_path)
        
        if success:
            logger.info(f"✓ Converted successfully: {result}")
            success_count += 1
        else:
            logger.error(f"✗ Failed: {result}")
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Conversion complete: {success_count}/{len(wpd_files)} files converted")
    logger.info(f"Converted PDFs saved in: {converted_dir}")

if __name__ == "__main__":
    main()