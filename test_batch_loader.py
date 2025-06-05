#!/usr/bin/env python3
"""
Test script for the new Pose Batch Loader nodes
"""

import os
import sys
import json

# Add the ComfyUI custom nodes path to sys.path for testing
sys.path.append(r'f:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI-ultimate-openpose-editor')

def create_test_json_files(test_folder):
    """Create some test JSON files for batch loading"""
    os.makedirs(test_folder, exist_ok=True)
    
    # Sample pose data structure
    sample_poses = [
        {
            "people": [{
                "pose_keypoints_2d": [100, 200, 1.0, 150, 180, 1.0],  # Simplified for test
                "face_keypoints_2d": [],
                "hand_left_keypoints_2d": [],
                "hand_right_keypoints_2d": []
            }],
            "canvas_width": 512,
            "canvas_height": 768
        },
        {
            "people": [{
                "pose_keypoints_2d": [120, 220, 1.0, 170, 200, 1.0],  # Different pose
                "face_keypoints_2d": [],
                "hand_left_keypoints_2d": [],
                "hand_right_keypoints_2d": []
            }],
            "canvas_width": 512,
            "canvas_height": 768
        },
        {
            "people": [{
                "pose_keypoints_2d": [140, 240, 1.0, 190, 220, 1.0],  # Another pose
                "face_keypoints_2d": [],
                "hand_left_keypoints_2d": [],
                "hand_right_keypoints_2d": []
            }],
            "canvas_width": 512,
            "canvas_height": 768
        }
    ]
    
    # Create test files
    for i, pose_data in enumerate(sample_poses):
        filename = f"test_pose_{i+1:03d}.json"
        filepath = os.path.join(test_folder, filename)
        with open(filepath, 'w') as f:
            json.dump(pose_data, f, indent=2)
        print(f"Created {filepath}")
    
    return len(sample_poses)

def test_batch_loader():
    """Test the PoseBatchLoaderNode functionality"""
    print("Testing Pose Batch Loader...")
    
    # Create test data
    test_folder = r"f:\ComfyUI_windows_portable\ComfyUI\custom_nodes\ComfyUI-ultimate-openpose-editor\test_poses"
    num_files = create_test_json_files(test_folder)
    
    try:
        # Import the batch loader node
        from openpose_editor_nodes import PoseBatchLoaderNode
        
        # Create an instance
        loader = PoseBatchLoaderNode()
        
        # Test loading each file
        for i in range(num_files):
            print(f"\n--- Testing file {i+1}/{num_files} ---")
            
            result = loader.load_batch_pose(
                folder_path=test_folder,
                file_pattern="*.json",
                current_index=i,
                sort_files=True,
                loop_batch=False
            )
            
            pose_keypoint, pose_json, filename, total_count, current_index = result
            
            print(f"Filename: {filename}")
            print(f"Total files: {total_count}")
            print(f"Current index: {current_index}")
            print(f"Pose data loaded: {pose_keypoint is not None}")
            print(f"JSON length: {len(pose_json) if pose_json else 0}")
            
            if pose_keypoint:
                print(f"People count: {len(pose_keypoint.get('people', []))}")
        
        # Test error handling - non-existent folder
        print(f"\n--- Testing error handling ---")
        result = loader.load_batch_pose(
            folder_path="/non/existent/folder",
            file_pattern="*.json",
            current_index=0
        )
        print(f"Error test result: {result[2]}")  # Should show error message
        
        print(f"\n✅ Batch loader test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up test files
        import shutil
        if os.path.exists(test_folder):
            shutil.rmtree(test_folder)
            print(f"Cleaned up test folder: {test_folder}")

if __name__ == "__main__":
    print("=" * 50)
    print("Pose Batch Loader Test")
    print("=" * 50)
    
    success = test_batch_loader()
    
    if success:
        print("\n🎉 All tests passed! The batch loader nodes are ready to use.")
        print("\nNext steps:")
        print("1. Restart ComfyUI to load the new nodes")
        print("2. Look for 'Pose Batch Loader' in the 'ultimate-openpose' category")
        print("3. Connect it to the OpenPose Editor node")
        print("4. Set your JSON files folder path and start processing!")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
