#!/usr/bin/env python3
"""
Dataset Cleanup Script
======================

Removes generated automotive dataset files.

Usage:
    python cleanup_datasets.py [options]

Options:
    --local             Remove local data files (default)
    --confirm           Skip confirmation prompt
"""

import argparse
import os
import shutil


def cleanup_local_files(confirm: bool = True):
    """Remove local dataset files."""
    files_to_remove = [
        "normalized_dealer_database.json",
        "normalized_parts_inventory.json",
        "normalized_recall_database.json",
        "parts_catalog.json",
        "dealer_oem_interaction.json",
        "automotive_expert_knowledge.json"
    ]
    
    existing_files = [f for f in files_to_remove if os.path.exists(f)]
    
    if not existing_files:
        print("No local dataset files found to remove.")
        return
    
    print(f"Found {len(existing_files)} local dataset files to remove:")
    for filename in existing_files:
        size = os.path.getsize(filename) / 1024
        print(f"   {filename} ({size:.1f} KB)")
    
    if confirm:
        response = input("\nProceed with removal? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            print("Cleanup cancelled.")
            return
    
    removed_count = 0
    for filename in existing_files:
        try:
            os.remove(filename)
            print(f"   Removed {filename}")
            removed_count += 1
        except Exception as e:
            print(f"   Failed to remove {filename}: {e}")
    
    print(f"Removed {removed_count}/{len(existing_files)} local files")





def main():
    parser = argparse.ArgumentParser(
        description='Clean up generated automotive dataset files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup_datasets.py                    # Remove local files (with confirmation)
  python cleanup_datasets.py --all --confirm   # Remove all files (no confirmation)
  python cleanup_datasets.py --strands         # Remove only strands files
        """
    )
    
    parser.add_argument('--local', action='store_true',
                       help='Remove local data files (default)')
    parser.add_argument('--confirm', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Default to local if no specific option is given
    if not args.local:
        args.local = True
    
    print("Dataset Cleanup Script")
    print("=" * 50)
    
    if args.local:
        print("Cleaning up local dataset files...")
        cleanup_local_files(confirm=not args.confirm)
    
    print("\nCleanup completed!")


if __name__ == "__main__":
    main()