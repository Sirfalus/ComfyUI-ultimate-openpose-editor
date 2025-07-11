#!/usr/bin/env python3
"""
UI Export Investigation - Final Diagnosis

This script helps determine exactly what the UI export buttons are doing.
It creates multiple monitoring points to catch any file creation.
"""

import os
import json
import time
import threading
import glob
from datetime import datetime
from pathlib import Path

class FileMonitor:
    def __init__(self, watch_paths):
        self.watch_paths = watch_paths
        self.initial_files = {}
        self.new_files = []
        self.monitoring = False
        
    def scan_initial_files(self):
        """Scan initial state of all watch paths"""
        self.initial_files = {}
        for path in self.watch_paths:
            if os.path.exists(path):
                files = set()
                for root, dirs, filenames in os.walk(path):
                    for filename in filenames:
                        if filename.endswith('.json'):
                            full_path = os.path.join(root, filename)
                            files.add((full_path, os.path.getmtime(full_path)))
                self.initial_files[path] = files
            else:
                self.initial_files[path] = set()
    
    def check_for_new_files(self):
        """Check for new or modified files"""
        current_time = time.time()
        for path in self.watch_paths:
            if not os.path.exists(path):
                continue
                
            current_files = set()
            for root, dirs, filenames in os.walk(path):
                for filename in filenames:
                    if filename.endswith('.json'):
                        full_path = os.path.join(root, filename)
                        mtime = os.path.getmtime(full_path)
                        current_files.add((full_path, mtime))
            
            # Find new or modified files
            initial = self.initial_files.get(path, set())
            new_or_modified = current_files - initial
            
            for file_path, mtime in new_or_modified:
                # Only consider files modified in the last 60 seconds
                if current_time - mtime < 60:
                    if file_path not in [f[0] for f in self.new_files]:
                        self.new_files.append((file_path, datetime.fromtimestamp(mtime)))
                        print(f"🔍 NEW FILE DETECTED: {file_path}")
                        print(f"   Created/Modified: {datetime.fromtimestamp(mtime)}")
                        self.analyze_file(file_path)
    
    def analyze_file(self, file_path):
        """Analyze a newly created/modified JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"   📄 Analyzing file content...")
            
            # Check structure
            if isinstance(data, list):
                print(f"   📊 Structure: List with {len(data)} item(s)")
                if data:
                    first_item = data[0]
                    self.check_canvas_dimensions(first_item, "   ")
            elif isinstance(data, dict):
                print(f"   📊 Structure: Single dictionary object")
                self.check_canvas_dimensions(data, "   ")
            else:
                print(f"   📊 Structure: Unknown ({type(data)})")
                
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
    
    def check_canvas_dimensions(self, obj, indent=""):
        """Check if an object has canvas dimensions"""
        if not isinstance(obj, dict):
            print(f"{indent}⚠️  Not a dictionary object")
            return
            
        has_width = 'canvas_width' in obj
        has_height = 'canvas_height' in obj
        
        if has_width and has_height:
            print(f"{indent}✅ Canvas dimensions: {obj['canvas_width']}x{obj['canvas_height']}")
            print(f"{indent}🎉 SUCCESS - Our fix worked!")
        else:
            print(f"{indent}❌ Canvas dimensions MISSING:")
            if not has_width:
                print(f"{indent}   - canvas_width: NOT FOUND")
            if not has_height:
                print(f"{indent}   - canvas_height: NOT FOUND")
            print(f"{indent}🚨 UI is bypassing our backend fix!")
        
        # Show other keys for context
        other_keys = [k for k in obj.keys() if k not in ['canvas_width', 'canvas_height']]
        if other_keys:
            print(f"{indent}📋 Other keys: {', '.join(other_keys[:5])}{'...' if len(other_keys) > 5 else ''}")
    
    def start_monitoring(self, duration=60):
        """Start monitoring for new files"""
        print(f"🔄 Starting file monitoring for {duration} seconds...")
        self.scan_initial_files()
        self.monitoring = True
        
        start_time = time.time()
        while self.monitoring and (time.time() - start_time) < duration:
            self.check_for_new_files()
            time.sleep(1)
        
        self.monitoring = False
        return self.new_files

def main():
    print("UI EXPORT INVESTIGATION - FINAL DIAGNOSIS")
    print("="*60)
    print()
    print("This script will monitor multiple locations for JSON file creation.")
    print("Please follow these steps:")
    print()
    print("1. Start this script")
    print("2. Open ComfyUI and the OpenPose Editor") 
    print("3. Create or load a pose")
    print("4. Click 'Save JSON to Pose Save Folder'")
    print("5. Click 'Export All JSON Files to Target'")
    print("6. Wait for monitoring to complete")
    print()
    
    # Define paths to monitor
    base_dir = Path(__file__).parent.absolute()
    
    # Possible output locations
    watch_paths = [
        str(base_dir),  # Current directory
        str(base_dir / "output_poses"),  # Default PoseSaver target
        str(base_dir / "output"),
        str(base_dir / "exports"),
        str(base_dir / "saved"),
        str(base_dir.parent.parent / "output"),  # ComfyUI/output
        str(base_dir.parent.parent / "temp"),    # ComfyUI/temp
        str(base_dir.parent.parent / "web"),     # ComfyUI/web
    ]
    
    # Add user's Downloads folder (common browser download location)
    import os
    if os.name == 'nt':  # Windows
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        if os.path.exists(downloads):
            watch_paths.append(downloads)
    
    print(f"📂 Monitoring {len(watch_paths)} locations:")
    for i, path in enumerate(watch_paths, 1):
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"   {i:2d}. {exists} {path}")
    
    print()
    input("Press ENTER to start monitoring...")
    
    # Start monitoring
    monitor = FileMonitor(watch_paths)
    new_files = monitor.start_monitoring(duration=60)
    
    print()
    print("="*60)
    print("MONITORING COMPLETE")
    print("="*60)
    
    if new_files:
        print(f"\\n📄 Found {len(new_files)} new/modified JSON file(s):")
        
        canvas_fixed_count = 0
        canvas_missing_count = 0
        
        for file_path, created_time in new_files:
            print(f"\\n📁 File: {file_path}")
            print(f"🕒 Time: {created_time}")
            
            # Re-analyze for summary
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if any object has canvas dimensions
                has_canvas = False
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and 'canvas_width' in item and 'canvas_height' in item:
                            has_canvas = True
                            break
                elif isinstance(data, dict):
                    if 'canvas_width' in data and 'canvas_height' in data:
                        has_canvas = True
                
                if has_canvas:
                    canvas_fixed_count += 1
                    print("   ✅ Has canvas dimensions - Fix WORKED!")
                else:
                    canvas_missing_count += 1
                    print("   ❌ Missing canvas dimensions - UI bypasses backend!")
                    
            except Exception as e:
                print(f"   ⚠️  Could not analyze: {e}")
        
        print(f"\\n📊 SUMMARY:")
        print(f"   ✅ Files with canvas dimensions: {canvas_fixed_count}")
        print(f"   ❌ Files missing canvas dimensions: {canvas_missing_count}")
        
        if canvas_missing_count > 0:
            print(f"\\n🔍 DIAGNOSIS:")
            print(f"   The UI export buttons are NOT using our PoseSaverNode backend.")
            print(f"   They are likely using one of these mechanisms:")
            print(f"   1. Direct browser file download (client-side export)")
            print(f"   2. ComfyUI web API endpoints that bypass our nodes") 
            print(f"   3. A different custom node or extension")
            print(f"   4. Frontend JavaScript that creates files directly")
            
            print(f"\\n💡 NEXT STEPS:")
            print(f"   1. Check if the OpenPose Editor UI has client-side export code")
            print(f"   2. Look for ComfyUI web API routes handling export")
            print(f"   3. Check if other extensions override our nodes")
            print(f"   4. Add canvas dimension logic directly to the UI export code")
        else:
            print(f"\\n🎉 SUCCESS: All exported files have canvas dimensions!")
            print(f"   Our backend fix is working correctly.")
    
    else:
        print("\\n❌ No new JSON files detected!")
        print("\\nPossible reasons:")
        print("   1. Export buttons weren't clicked")
        print("   2. Files are saved to a location we're not monitoring")
        print("   3. Export creates non-JSON files")
        print("   4. Export functionality is broken")
        
        print("\\n🔍 Manual check suggestions:")
        print("   1. Check browser Downloads folder")
        print("   2. Look for any new files with different extensions")
        print("   3. Check ComfyUI console for error messages")
        print("   4. Verify the export buttons actually do something")

if __name__ == "__main__":
    main()
