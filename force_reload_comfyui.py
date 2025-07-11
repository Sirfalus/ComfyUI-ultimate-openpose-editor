#!/usr/bin/env python3
"""
Force ComfyUI Cache Clear and Node Reload Test

This script will help determine if the issue is caused by:
1. ComfyUI caching old node implementations
2. The nodes not being properly reloaded with our fixes
3. The UI using a different export mechanism

This script will force ComfyUI to reload all custom nodes and clear any caches.
"""

import os
import sys
import json
import time
import psutil
import subprocess
from pathlib import Path

def main():
    print("COMFYUI CACHE CLEAR AND NODE RELOAD TEST")
    print("="*60)
    
    # Get current directory
    script_dir = Path(__file__).parent
    print(f"Script directory: {script_dir}")
    
    # Check if we're in a ComfyUI custom_nodes directory
    comfyui_root = None
    current_dir = script_dir
    while current_dir.parent != current_dir:
        if (current_dir / "main.py").exists() and (current_dir / "custom_nodes").exists():
            comfyui_root = current_dir
            break
        current_dir = current_dir.parent
    
    if comfyui_root:
        print(f"ComfyUI root detected: {comfyui_root}")
    else:
        print("ComfyUI root not found - please run this from within ComfyUI custom_nodes directory")
        return
    
    print("\\nSTEP 1: Check if ComfyUI is running")
    comfyui_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                if proc.info['cmdline'] and any('main.py' in str(arg) for arg in proc.info['cmdline']):
                    comfyui_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if comfyui_processes:
        print(f"Found {len(comfyui_processes)} ComfyUI process(es) running:")
        for proc in comfyui_processes:
            print(f"  PID: {proc.info['pid']} - {' '.join(proc.info['cmdline'])}")
        print("\\n⚠️  WARNING: ComfyUI is currently running!")
        print("   For best results, please stop ComfyUI, run this script, then restart ComfyUI.")
        response = input("\\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    else:
        print("✅ No ComfyUI processes detected")
    
    print("\\nSTEP 2: Clear ComfyUI caches")
    
    # Clear Python cache files
    pycache_dirs = list(script_dir.rglob("__pycache__"))
    if pycache_dirs:
        print(f"Found {len(pycache_dirs)} __pycache__ directories to clean:")
        for cache_dir in pycache_dirs:
            print(f"  Removing: {cache_dir}")
            try:
                for file in cache_dir.iterdir():
                    if file.is_file():
                        file.unlink()
                cache_dir.rmdir()
            except Exception as e:
                print(f"    Error: {e}")
    else:
        print("No __pycache__ directories found")
    
    # Clear ComfyUI's model cache if it exists
    cache_dirs = [
        comfyui_root / "temp",
        comfyui_root / "output" / "temp", 
        comfyui_root / "web" / "cache",
    ]
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            print(f"Clearing cache directory: {cache_dir}")
            try:
                for file in cache_dir.rglob("*"):
                    if file.is_file():
                        file.unlink()
            except Exception as e:
                print(f"  Error clearing {cache_dir}: {e}")
    
    print("\\nSTEP 3: Verify our fixes are in place")
    
    # Check util.py
    util_file = script_dir / "util.py"
    if util_file.exists():
        with open(util_file, 'r', encoding='utf-8') as f:
            util_content = f.read()
        
        if 'canvas_width' in util_content and 'canvas_height' in util_content:
            print("✅ util.py contains canvas dimension fixes")
        else:
            print("❌ util.py missing canvas dimension fixes!")
    else:
        print("❌ util.py not found!")
    
    # Check openpose_editor_nodes.py
    nodes_file = script_dir / "openpose_editor_nodes.py"
    if nodes_file.exists():
        with open(nodes_file, 'r', encoding='utf-8') as f:
            nodes_content = f.read()
        
        if '_ensure_canvas_dimensions' in nodes_content:
            print("✅ openpose_editor_nodes.py contains PoseSaverNode canvas fixes")
        else:
            print("❌ openpose_editor_nodes.py missing PoseSaverNode canvas fixes!")
            
        if "if 'canvas_width' not in item:" in nodes_content:
            print("✅ openpose_editor_nodes.py contains OpenposeEditorNode preprocessing fixes")
        else:
            print("❌ openpose_editor_nodes.py missing OpenposeEditorNode preprocessing fixes!")
    else:
        print("❌ openpose_editor_nodes.py not found!")
    
    print("\\nSTEP 4: Test our backend fixes")
    
    # Test PoseSaver fix
    print("Testing PoseSaverNode fix...")
    try:
        sys.path.insert(0, str(script_dir))
        from openpose_editor_nodes import PoseSaverNode
        
        # Create a test pose without canvas dimensions
        test_pose = [{"people": [{"pose_keypoints_2d": []}]}]
        
        # Create PoseSaverNode instance
        saver = PoseSaverNode()
        
        # Test the _ensure_canvas_dimensions method
        processed = saver._ensure_canvas_dimensions(test_pose)
        
        if processed and processed[0].get('canvas_width') == 512 and processed[0].get('canvas_height') == 768:
            print("✅ PoseSaverNode._ensure_canvas_dimensions() working correctly")
        else:
            print("❌ PoseSaverNode._ensure_canvas_dimensions() not working!")
            print(f"   Result: {processed}")
            
    except Exception as e:
        print(f"❌ Error testing PoseSaverNode: {e}")
    
    print("\\nSTEP 5: Create a force-reload marker")
    
    # Create a timestamp file that can indicate when the node was last reloaded
    reload_marker = script_dir / "last_reload.txt"
    with open(reload_marker, 'w') as f:
        f.write(f"Last reload: {time.time()}\\n")
        f.write(f"Cache cleared at: {time.ctime()}\\n")
    
    print(f"✅ Created reload marker: {reload_marker}")
    
    print("\\nSTEP 6: Recommendations")
    print("-" * 40)
    
    if comfyui_processes:
        print("🔄 RESTART ComfyUI now to ensure all changes take effect")
        print("   1. Stop ComfyUI")
        print("   2. Wait 5 seconds")
        print("   3. Start ComfyUI")
        print("   4. Load your workflow")
        print("   5. Test the export buttons again")
    else:
        print("▶️  START ComfyUI now and test the export buttons")
    
    print("\\n📋 Test checklist:")
    print("   □ Open OpenPose Editor in ComfyUI")
    print("   □ Create or load a pose")
    print("   □ Click 'Save JSON to Pose Save Folder'")
    print("   □ Click 'Export All JSON Files to Target'") 
    print("   □ Check if exported JSON files have canvas_width and canvas_height")
    
    print("\\n💡 If the problem persists after restart:")
    print("   1. The UI might be using a different export mechanism")
    print("   2. There might be ComfyUI extensions overriding our nodes")
    print("   3. The UI might be calling ComfyUI APIs directly")
    
    print("\\n🔍 Next debugging steps if issue persists:")
    print("   1. Run monitor_ui_exports.py to see what files are created")
    print("   2. Check ComfyUI console output for any errors")
    print("   3. Look for any other custom nodes that might handle pose saving")

if __name__ == "__main__":
    main()
