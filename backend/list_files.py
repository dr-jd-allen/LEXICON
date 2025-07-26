import os
from pathlib import Path

def list_files_with_sizes(directory):
    """List all files in directory with their sizes"""
    files = []
    
    for root, dirs, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            try:
                size = os.path.getsize(filepath)
                size_kb = size / 1024
                size_mb = size_kb / 1024
                
                # Get relative path for cleaner display
                rel_path = os.path.relpath(filepath, directory)
                
                files.append({
                    'name': filename,
                    'path': rel_path,
                    'size_bytes': size,
                    'size_kb': size_kb,
                    'size_mb': size_mb
                })
            except Exception as e:
                print(f"Error accessing {filepath}: {e}")
    
    # Sort by size (largest first)
    files.sort(key=lambda x: x['size_bytes'], reverse=True)
    
    # Print summary
    total_size_mb = sum(f['size_mb'] for f in files)
    print(f"\nTotal files: {len(files)}")
    print(f"Total size: {total_size_mb:.2f} MB\n")
    
    # Print files
    print(f"{'Filename':<60} {'Size':>12} {'Path'}")
    print("-" * 120)
    
    for f in files:
        if f['size_mb'] > 1:
            size_str = f"{f['size_mb']:.2f} MB"
        else:
            size_str = f"{f['size_kb']:.2f} KB"
        
        # Truncate long filenames for display
        display_name = f['name'][:57] + "..." if len(f['name']) > 60 else f['name']
        
        print(f"{display_name:<60} {size_str:>12} {f['path']}")

if __name__ == "__main__":
    corpus_dir = r"C:\Users\jdall\lexicon-mvp-alpha\tbi-corpus"
    list_files_with_sizes(corpus_dir)