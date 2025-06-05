#!/usr/bin/env python3
"""
Simple test script for JSON batch loading logic (without ComfyUI dependencies)
"""

import json
import glob
import os

def simple_batch_load_test(folder_path, file_pattern="*.json", current_index=0, sort_files=True, loop_batch=False):
    """
    Simplified version of the batch loading logic
    """
    try:
        # Validate folder path
        if not folder_path or not os.path.exists(folder_path):
            print(f"Error: Folder path '{folder_path}' does not exist")
            return None, "{}", "No files found", 0, 0
        
        # Get all JSON files matching the pattern
        search_pattern = os.path.join(folder_path, file_pattern)
        json_files = glob.glob(search_pattern)
        
        if not json_files:
            print(f"No files found matching pattern: {search_pattern}")
            return None, "{}", "No files found", 0, 0
        
        # Sort files if requested
        if sort_files:
            json_files.sort()
        
        total_files = len(json_files)
        
        # Handle looping
        if loop_batch and total_files > 0:
            current_index = current_index % total_files
        elif current_index >= total_files:
            current_index = max(0, total_files - 1)
        
        # Load the current file
        current_file = json_files[current_index]
        filename = os.path.basename(current_file)
        
        try:
            with open(current_file, 'r', encoding='utf-8') as f:
                pose_data = json.load(f)
            
            # Convert to string for JSON output
            pose_json_str = json.dumps(pose_data, indent=2)
            
            print(f"✓ Loaded pose file: {filename} ({current_index + 1}/{total_files})")
            
            return pose_data, pose_json_str, filename, total_files, current_index
            
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing JSON file {filename}: {e}")
            return None, "{}", f"Error parsing {filename}", total_files, current_index
        except Exception as e:
            print(f"✗ Error reading file {filename}: {e}")
            return None, "{}", f"Error reading {filename}", total_files, current_index
            
    except Exception as e:
        print(f"✗ Error in batch load: {e}")
        return None, "{}", "Error", 0, 0

def test_batch_loading():
    """Test the batch loading with current directory"""
    
    print("Testing Batch JSON Loading")
    print("=" * 50)
    
    # Test current directory
    test_folder = "."
    
    print(f"Testing folder: {test_folder}")
    
    # Get list of JSON files first
    json_files = glob.glob("*.json")
    print(f"Found JSON files: {json_files}")
    
    if not json_files:
        print("No JSON files found in current directory")
        return
    
    # Test loading different files by index
    for i in range(min(len(json_files), 3)):  # Test first 3 files or all if less than 3
        print(f"\n--- Testing index {i} ---")
        
        result = simple_batch_load_test(
            folder_path=test_folder,
            file_pattern="*.json", 
            current_index=i,
            sort_files=True,
            loop_batch=False
        )
        
        pose_data, pose_json, filename, total_count, current_index = result
        
        print(f"Filename: {filename}")
        print(f"Total files: {total_count}")
        print(f"Current index: {current_index}")
        
        if pose_data:
            print(f"✓ Pose data loaded successfully")
            
            # Analyze the structure
            if isinstance(pose_data, list) and len(pose_data) > 0:
                first_frame = pose_data[0]
                if 'people' in first_frame and len(first_frame['people']) > 0:
                    person = first_frame['people'][0]
                    pose_kp = person.get('pose_keypoints_2d', [])
                    print(f"  - Pose keypoints count: {len(pose_kp)}")
                    print(f"  - First few keypoints: {pose_kp[:9]}")
                    
                    # Check for other keypoint types
                    face_kp = person.get('face_keypoints_2d', [])
                    hand_l_kp = person.get('hand_left_keypoints_2d', [])
                    hand_r_kp = person.get('hand_right_keypoints_2d', [])
                    
                    print(f"  - Face keypoints: {len(face_kp)}")
                    print(f"  - Left hand keypoints: {len(hand_l_kp)}")
                    print(f"  - Right hand keypoints: {len(hand_r_kp)}")
                    
                    # Check canvas dimensions
                    canvas_w = first_frame.get('canvas_width', 'N/A')
                    canvas_h = first_frame.get('canvas_height', 'N/A')
                    print(f"  - Canvas dimensions: {canvas_w}x{canvas_h}")
                    
                    # Determine format
                    if len(pose_kp) > 0:
                        first_element = pose_kp[0]
                        if isinstance(first_element, list):
                            print(f"  - Format: OpenPose Editor format (nested arrays)")
                        else:
                            print(f"  - Format: Standard OpenPose format (flat arrays)")
                    
                else:
                    print(f"  ✗ No people data found")
            else:
                print(f"  ✗ Unexpected data structure")
        else:
            print(f"  ✗ Failed to load pose data")

def show_usage_instructions():
    """Show how to use this in ComfyUI"""
    
    print("\n" + "=" * 60)
    print("HOW TO USE POSE BATCH LOADER IN COMFYUI")
    print("=" * 60)
    
    print("1. Restart ComfyUI to load the new nodes")
    print("2. In ComfyUI, add the 'Pose Batch Loader' node")
    print("3. Configure the node:")
    print("   - folder_path: Path to your JSON folder")
    print("     Example: f:/0VideoForAi/Undead/stable_pose_normal/json")
    print("   - file_pattern: *.json")
    print("   - current_index: 0 (start with first file)")
    print("   - sort_files: True (alphabetical order)")
    print("   - loop_batch: False (or True for automatic cycling)")
    
    print("\n4. Connect the outputs:")
    print("   - POSE_KEYPOINT → OpenposeEditorNode POSE_KEYPOINT input")
    print("   - POSE_JSON → (optional) for debugging")
    print("   - FILENAME → (optional) to see current file")
    
    print("\n5. Workflow tips:")
    print("   - Use current_index to manually select different poses")
    print("   - Enable loop_batch for automatic cycling")
    print("   - The TOTAL_COUNT output shows how many files were found")
    print("   - Your exported JSON files are already in the correct format!")
    
    print("\n6. Node outputs:")
    print("   - POSE_KEYPOINT: Ready to use with OpenposeEditorNode")
    print("   - POSE_JSON: JSON string representation")
    print("   - FILENAME: Current file being loaded")
    print("   - TOTAL_COUNT: Total number of JSON files found")
    print("   - CURRENT_INDEX: Current file index")

if __name__ == "__main__":
    test_batch_loading()
    show_usage_instructions()
