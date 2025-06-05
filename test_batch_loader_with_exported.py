#!/usr/bin/env python3
"""
Test script for PoseBatchLoaderNode with exported JSON files
"""

import sys
import os
import json

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from openpose_editor_nodes import PoseBatchLoaderNode

def test_batch_loader():
    """Test the PoseBatchLoaderNode with your exported JSON files"""
      # Test folder path - using the current directory where we copied the JSON files
    test_folder = "."  # Current directory
    
    print(f"Testing PoseBatchLoaderNode with folder: {test_folder}")
    print("=" * 60)
    
    # Create an instance of the batch loader
    loader = PoseBatchLoaderNode()
    
    # Test loading different files by index
    for i in range(5):  # Test first 5 files
        print(f"\nTesting index {i}:")
        
        try:
            # Call the load_batch_pose method
            result = loader.load_batch_pose(
                folder_path=test_folder,
                file_pattern="*.json", 
                current_index=i,
                sort_files=True,
                loop_batch=False
            )
            
            pose_keypoint, pose_json, filename, total_count, current_index = result
            
            print(f"  Filename: {filename}")
            print(f"  Total files: {total_count}")
            print(f"  Current index: {current_index}")
            
            if pose_keypoint:
                print(f"  Pose data loaded successfully")
                # Check if it's a list and has people
                if isinstance(pose_keypoint, list) and len(pose_keypoint) > 0:
                    first_frame = pose_keypoint[0]
                    if 'people' in first_frame and len(first_frame['people']) > 0:
                        person = first_frame['people'][0]
                        pose_kp = person.get('pose_keypoints_2d', [])
                        print(f"  Pose keypoints count: {len(pose_kp)}")
                        print(f"  First few keypoints: {pose_kp[:9]}")
                        
                        # Check canvas dimensions if available
                        canvas_w = first_frame.get('canvas_width', 'N/A')
                        canvas_h = first_frame.get('canvas_height', 'N/A')
                        print(f"  Canvas dimensions: {canvas_w}x{canvas_h}")
                    else:
                        print(f"  No people data found in pose")
                else:
                    print(f"  Unexpected pose data format")
            else:
                print(f"  Failed to load pose data")
                
        except Exception as e:
            print(f"  Error: {e}")
            
        # Stop if we've reached the end
        if filename == "No files found":
            break
    
    print("\n" + "=" * 60)
    print("Test completed!")

def test_with_comfyui_workflow():
    """Show how to use the batch loader in a ComfyUI workflow"""
    
    print("\nHow to use Pose Batch Loader in ComfyUI:")
    print("=" * 50)
    print("1. Add 'Pose Batch Loader' node to your workflow")
    print("2. Set the folder_path to your JSON folder:")
    print("   f:/0VideoForAi/Undead/stable_pose_normal/json")
    print("3. Set file_pattern to: *.json")
    print("4. Connect POSE_KEYPOINT output to OpenposeEditorNode POSE_KEYPOINT input")
    print("5. Use current_index to cycle through different poses")
    print("6. Enable loop_batch if you want automatic cycling")
    print("\nNode outputs:")
    print("- POSE_KEYPOINT: Direct pose data for OpenposeEditorNode")
    print("- POSE_JSON: JSON string representation")
    print("- FILENAME: Current file being loaded")
    print("- TOTAL_COUNT: Total number of JSON files found")
    print("- CURRENT_INDEX: Current file index")

if __name__ == "__main__":
    test_batch_loader()
    test_with_comfyui_workflow()
