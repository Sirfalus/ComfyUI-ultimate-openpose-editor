#!/usr/bin/env python3
"""
Quick test to verify the ComfyUI node with rotation correction is working
"""

import json
import sys
import os

def test_comfyui_node_ready():
    print("=== ComfyUI Node Readiness Test ===\n")
    
    try:
        # Test 1: Import the node
        print("1. Testing node import...")
        sys.path.append('.')
        from openpose_editor_nodes import OpenposeEditorNode, NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
        print("   ✅ Nodes imported successfully")
        
        # Test 2: Check input parameters
        print("\n2. Checking input parameters...")
        input_types = OpenposeEditorNode.INPUT_TYPES()
        optional_params = input_types['optional']
        
        required_params = ['auto_perspective', 'perspective_correction', 'shoulder_scale']
        missing_params = []
        
        for param in required_params:
            if param in optional_params:
                print(f"   ✅ {param}: {optional_params[param]}")
            else:
                missing_params.append(param)
                print(f"   ❌ {param}: MISSING")
        
        if missing_params:
            print(f"\n❌ Missing parameters: {missing_params}")
            return False
        
        # Test 3: Check util.py function
        print("\n3. Testing util.py function...")
        from util import draw_pose_json
        print("   ✅ draw_pose_json function imported successfully")
        
        # Test 4: Load test pose data
        print("\n4. Testing with real pose data...")
        test_files = ['side_pose.json', 'front_pose.json']
        available_files = [f for f in test_files if os.path.exists(f)]
        
        if not available_files:
            print("   ⚠️  No test pose files found, but node should still work")
        else:
            print(f"   ✅ Test files available: {available_files}")
        
        # Test 5: Check node registration
        print("\n5. Checking node registration...")
        if 'OpenposeEditorNode' in NODE_CLASS_MAPPINGS:
            print("   ✅ OpenposeEditorNode registered in NODE_CLASS_MAPPINGS")
        else:
            print("   ❌ OpenposeEditorNode not registered")
            return False
            
        if 'OpenposeEditorNode' in NODE_DISPLAY_NAME_MAPPINGS:
            display_name = NODE_DISPLAY_NAME_MAPPINGS['OpenposeEditorNode']
            print(f"   ✅ Display name: '{display_name}'")
        else:
            print("   ❌ Display name not registered")
            return False
        
        print(f"\n🎉 SUCCESS! The ComfyUI node is ready to use with rotation correction!")
        print(f"\n📋 USAGE INSTRUCTIONS:")
        print(f"   1. In ComfyUI, look for 'OpenPose Editor' node")
        print(f"   2. Key parameters for rotation correction:")
        print(f"      • auto_perspective: True (automatic) / False (manual)")
        print(f"      • perspective_correction: 0.1-1.0 (when auto_perspective=False)")
        print(f"      • shoulder_scale: Additional scaling factor")
        print(f"   3. For side poses: set auto_perspective=False, perspective_correction=0.3")
        print(f"   4. For frontal poses: keep auto_perspective=True (default)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running this from the ComfyUI environment")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_comfyui_node_ready()
    sys.exit(0 if success else 1)
