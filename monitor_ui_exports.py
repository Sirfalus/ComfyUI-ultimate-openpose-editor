#!/usr/bin/env python3
"""
UI Export Button Test - Verify what the UI export buttons actually do
This script helps debug if the UI buttons use our fixed backend code.

This test will help us understand:
1. Are the UI export buttons calling our PoseSaverNode?
2. Or are they doing direct file operations that bypass our fixes?
3. What files are actually created by the UI exports?
"""

import json
import os
import time
import glob
from datetime import datetime

def monitor_directory_changes(watch_dir=".", watch_time=30):
    """Monitor a directory for new files being created"""
    print(f"Monitoring directory: {os.path.abspath(watch_dir)}")
    print(f"Watching for {watch_time} seconds...")
    print("Please use the UI export buttons NOW!")
    print("-" * 50)
    
    # Get initial state
    initial_files = set()
    for root, dirs, files in os.walk(watch_dir):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                initial_files.add(file_path)
    
    print(f"Initial JSON files found: {len(initial_files)}")
    
    # Monitor for changes
    start_time = time.time()
    new_files = []
    
    while time.time() - start_time < watch_time:
        current_files = set()
        for root, dirs, files in os.walk(watch_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    current_files.add(file_path)
        
        # Check for new files
        newly_created = current_files - initial_files
        for new_file in newly_created:
            if new_file not in [f[0] for f in new_files]:
                new_files.append((new_file, datetime.now()))
                print(f"NEW FILE DETECTED: {new_file}")
        
        time.sleep(1)
    
    return new_files

def check_canvas_dimensions_in_files(file_list):
    """Check if the newly created files have canvas dimensions"""
    print("\\n" + "="*60)
    print("CHECKING CANVAS DIMENSIONS IN NEW FILES")
    print("="*60)
    
    for file_path, created_time in file_list:
        print(f"\\nChecking: {file_path}")
        print(f"Created at: {created_time}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            has_canvas_width = False
            has_canvas_height = False
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        if 'canvas_width' in item:
                            has_canvas_width = True
                            print(f"  ✓ canvas_width: {item['canvas_width']}")
                        else:
                            print(f"  ✗ canvas_width: MISSING")
                        
                        if 'canvas_height' in item:
                            has_canvas_height = True
                            print(f"  ✓ canvas_height: {item['canvas_height']}")
                        else:
                            print(f"  ✗ canvas_height: MISSING")
                        
                        break  # Just check first item
            elif isinstance(data, dict):
                if 'canvas_width' in data:
                    has_canvas_width = True
                    print(f"  ✓ canvas_width: {data['canvas_width']}")
                else:
                    print(f"  ✗ canvas_width: MISSING")
                
                if 'canvas_height' in data:
                    has_canvas_height = True
                    print(f"  ✓ canvas_height: {data['canvas_height']}")
                else:
                    print(f"  ✗ canvas_height: MISSING")
            
            if has_canvas_width and has_canvas_height:
                print(f"  🎉 RESULT: Canvas dimensions PRESENT - Our fix WORKED!")
            else:
                print(f"  ❌ RESULT: Canvas dimensions MISSING - UI bypasses our fix!")
                
        except Exception as e:
            print(f"  ERROR reading file: {e}")

def main():
    print("UI EXPORT BUTTON MONITOR")
    print("="*60)
    print("This script will monitor for new JSON files created by UI export buttons.")
    print("\\nINSTRUCTIONS:")
    print("1. Start this script")
    print("2. Open ComfyUI and load the OpenPose Editor")
    print("3. Click 'Save JSON to Pose Save Folder' button")
    print("4. Click 'Export All JSON Files to Target' button")
    print("5. Wait for the monitoring to complete")
    print()
    
    input("Press ENTER to start monitoring...")
    
    # Monitor the current directory and common output locations
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Base directory: {base_dir}")
    
    # Check common output folders
    possible_dirs = [
        base_dir,
        os.path.join(base_dir, "output_poses"),
        os.path.join(base_dir, "output"),
        os.path.join(base_dir, "exports"),
        os.path.join(base_dir, ".."),  # Parent directory
        os.path.join(base_dir, "..", "..", "output"),  # ComfyUI/output
    ]
    
    all_new_files = []
    
    for watch_dir in possible_dirs:
        if os.path.exists(watch_dir):
            print(f"\\nMonitoring: {watch_dir}")
            new_files = monitor_directory_changes(watch_dir, watch_time=10)
            all_new_files.extend(new_files)
    
    if all_new_files:
        print(f"\\nFound {len(all_new_files)} new JSON files!")
        check_canvas_dimensions_in_files(all_new_files)
    else:
        print("\\n❌ No new JSON files detected.")
        print("Either:")
        print("1. The UI export buttons weren't clicked")
        print("2. Files were saved to a location we're not monitoring")
        print("3. The UI export functionality doesn't create JSON files directly")
        
        print("\\nTip: Try manually searching for recently created .json files:")
        print("find . -name '*.json' -mtime -1  # On Linux/Mac")
        print("Get-ChildItem -Path . -Recurse -Name '*.json' | Where-Object {$_.LastWriteTime -gt (Get-Date).AddMinutes(-10)}  # On PowerShell")

if __name__ == "__main__":
    main()
