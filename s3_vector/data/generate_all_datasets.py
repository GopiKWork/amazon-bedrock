#!/usr/bin/env python3
"""
Master Automotive Dataset Generator
==================================

Generates all automotive datasets with configurable counts.

Usage:
    python generate_all_datasets.py [options]

Options:
    --dealers N         Number of dealers to generate (default: 50)
    --parts N           Number of parts inventory items to generate (default: 50)  
    --recalls N         Number of recalls to generate (default: 50)
    --catalog N         Number of catalog parts to generate (default: 50)
    --oem N             Number of OEM interactions to generate (default: 50)
    --expert N          Number of expert knowledge entries to generate (default: 50)
    --all N             Set count for all datasets (overrides individual counts)
    --clean             Remove existing files before generating new ones
"""

import argparse
import os
import sys
import subprocess
import shutil
from datetime import datetime


def run_generator(script_name: str, count: int, description: str):
    """Run a generator script with the specified count."""
    print(f"\n{'='*60}")
    print(f"🔧 Generating {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([
            sys.executable, script_name, '--count', str(count)
        ], check=True, capture_output=True, text=True)
        
        # Print the output from the generator
        if result.stdout:
            print(result.stdout)
        
        print(f"✅ {description} generation completed successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating {description}:")
        print(f"   Exit code: {e.returncode}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False
    
    return True


def clean_existing_files():
    """Remove existing dataset files."""
    files_to_clean = [
        "normalized_dealer_database.json",
        "normalized_parts_inventory.json", 
        "normalized_recall_database.json",
        "parts_catalog.json",
        "dealer_oem_interaction.json",
        "automotive_expert_knowledge.json"
    ]
    
    print("🧹 Cleaning existing dataset files...")
    
    for filename in files_to_clean:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"   Removed {filename}")
        else:
            print(f"   {filename} not found (skipping)")


def check_dependencies():
    """Check if all generator scripts exist."""
    required_scripts = [
        "generate_dealer_database.py",
        "generate_parts_inventory.py",
        "generate_recall_database.py", 
        "generate_parts_catalog.py",
        "dealer_oem_data_generator.py",
        "generate_expert_knowledge.py"
    ]
    
    missing_scripts = []
    for script in required_scripts:
        if not os.path.exists(script):
            missing_scripts.append(script)
    
    if missing_scripts:
        print("❌ Missing required generator scripts:")
        for script in missing_scripts:
            print(f"   {script}")
        return False
    
    return True


def copy_data_files():
    """Copy relevant data files to strands-bedrock-agent-core/data folder."""
    source_files = [
        "normalized_dealer_database.json",
        "normalized_parts_inventory.json",
        "normalized_recall_database.json", 
        "parts_catalog.json",
        "dealer_oem_interaction.json",
        "automotive_expert_knowledge.json",
        "multimodal_damage_data.json",
        "dealer_issue_escalation.txt"
    ]
    
    target_dir = "../strands-bedrock-agent-core/data"
    
    if not os.path.exists(target_dir):
        print(f"⚠️  Target directory {target_dir} does not exist. Skipping file copy.")
        return False
    
    print(f"\n📁 Copying data files to {target_dir}...")
    copied_count = 0
    
    for filename in source_files:
        if os.path.exists(filename):
            try:
                shutil.copy2(filename, target_dir)
                print(f"   ✅ Copied {filename}")
                copied_count += 1
            except Exception as e:
                print(f"   ❌ Failed to copy {filename}: {e}")
        else:
            print(f"   ⚠️  {filename} not found (skipping)")
    
    print(f"📊 Copied {copied_count}/{len(source_files)} files to strands-bedrock-agent-core/data")
    return copied_count > 0


def print_summary(dealers: int, parts: int, recalls: int, catalog: int, oem: int, expert: int, success_count: int):
    """Print generation summary."""
    print(f"\n{'='*60}")
    print(f"📊 GENERATION SUMMARY")
    print(f"{'='*60}")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"")
    print(f"Dataset counts requested:")
    print(f"   Dealers: {dealers}")
    print(f"   Parts Inventory: {parts}")
    print(f"   Recalls: {recalls}")
    print(f"   Parts Catalog: {catalog}")
    print(f"   OEM Interactions: {oem}")
    print(f"   Expert Knowledge: {expert}")
    print(f"")
    print(f"Generation results: {success_count}/6 successful")
    
    if success_count == 6:
        print("✅ All datasets generated successfully!")
        print("")
        print("📁 Generated files:")
        files = [
            ("normalized_dealer_database.json", "Dealer database with contact info and specialties"),
            ("normalized_parts_inventory.json", "Parts inventory across dealers with pricing"),
            ("normalized_recall_database.json", "Vehicle recalls with affected models and remedies"),
            ("parts_catalog.json", "Parts catalog with OEM and aftermarket options"),
            ("dealer_oem_interaction.json", "Dealer-OEM interaction scenarios and communications"),
            ("automotive_expert_knowledge.json", "Technical knowledge base with TSBs and procedures")
        ]
        
        for filename, description in files:
            if os.path.exists(filename):
                size = os.path.getsize(filename)
                size_kb = size / 1024
                print(f"   {filename} ({size_kb:.1f} KB) - {description}")
        
        print("")
        print("🚀 Next steps:")
        print("   • Use these datasets in your automotive applications")
        print("   • Import into vector stores for semantic search")
        print("   • Build dealer recommendation systems")
        print("   • Create parts availability checkers")
        print("   • Implement recall notification systems")
    else:
        print("⚠️  Some datasets failed to generate. Check the error messages above.")


def main():
    parser = argparse.ArgumentParser(
        description='Generate all automotive datasets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_all_datasets.py                    # Generate 50 of each
  python generate_all_datasets.py --all 100         # Generate 100 of each  
  python generate_all_datasets.py --dealers 25 --parts 75 --oem 40  # Custom counts
  python generate_all_datasets.py --clean --all 30  # Clean and generate 30 each
        """
    )
    
    parser.add_argument('--dealers', type=int, default=50,
                       help='Number of dealers to generate (default: 50)')
    parser.add_argument('--parts', type=int, default=50,
                       help='Number of parts inventory items to generate (default: 50)')
    parser.add_argument('--recalls', type=int, default=50,
                       help='Number of recalls to generate (default: 50)')
    parser.add_argument('--catalog', type=int, default=50,
                       help='Number of catalog parts to generate (default: 50)')
    parser.add_argument('--oem', type=int, default=50,
                       help='Number of OEM interactions to generate (default: 50)')
    parser.add_argument('--expert', type=int, default=50,
                       help='Number of expert knowledge entries to generate (default: 50)')
    parser.add_argument('--all', type=int,
                       help='Set count for all datasets (overrides individual counts)')
    parser.add_argument('--clean', action='store_true',
                       help='Remove existing files before generating new ones')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.all is not None:
        if args.all < 1:
            print("Error: --all count must be at least 1")
            return
        dealers_count = parts_count = recalls_count = catalog_count = oem_count = expert_count = args.all
    else:
        if any(count < 1 for count in [args.dealers, args.parts, args.recalls, args.catalog, args.oem, args.expert]):
            print("Error: All counts must be at least 1")
            return
        dealers_count = args.dealers
        parts_count = args.parts
        recalls_count = args.recalls
        catalog_count = args.catalog
        oem_count = args.oem
        expert_count = args.expert
    
    print("🚀 Automotive Dataset Generator")
    print("=" * 60)
    print(f"Generating datasets with the following counts:")
    print(f"   Dealers: {dealers_count}")
    print(f"   Parts Inventory: {parts_count}")
    print(f"   Recalls: {recalls_count}")
    print(f"   Parts Catalog: {catalog_count}")
    print(f"   OEM Interactions: {oem_count}")
    print(f"   Expert Knowledge: {expert_count}")
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease ensure all generator scripts are present in the current directory.")
        return
    
    # Clean existing files if requested
    if args.clean:
        clean_existing_files()
    
    # Generate datasets in order (dealers first, as others may reference it)
    generators = [
        ("generate_dealer_database.py", dealers_count, "Dealer Database"),
        ("generate_parts_inventory.py", parts_count, "Parts Inventory"),
        ("generate_recall_database.py", recalls_count, "Recall Database"),
        ("generate_parts_catalog.py", catalog_count, "Parts Catalog"),
        ("dealer_oem_data_generator.py", oem_count, "OEM Interactions"),
        ("generate_expert_knowledge.py", expert_count, "Expert Knowledge")
    ]
    
    success_count = 0
    start_time = datetime.now()
    
    for script, count, description in generators:
        if run_generator(script, count, description):
            success_count += 1
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    print(f"\n⏱️  Total generation time: {duration.total_seconds():.1f} seconds")
    
    # Copy files to strands-bedrock-agent-core/data
    copy_success = copy_data_files()
    
    # Print summary
    print_summary(dealers_count, parts_count, recalls_count, catalog_count, oem_count, expert_count, success_count)


if __name__ == "__main__":
    main()