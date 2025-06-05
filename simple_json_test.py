#!/usr/bin/env python3
"""
Simple test to verify JSON files can be loaded and processed
"""

import json
import os
import glob

def test_json_loading():
    """Test loading JSON files directly"""
    
    print("Testing JSON file loading in current directory")
    print("=" * 50)
    
    # Get all JSON files in current directory
    json_files = glob.glob("*.json")
    json_files.sort()
    
    print(f"Found {len(json_files)} JSON files:")
    
    for i, file_path in enumerate(json_files):
        print(f"\n{i+1}. Testing file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"   ✓ Successfully loaded JSON")
            print(f"   ✓ File size: {os.path.getsize(file_path)} bytes")
            
            # Check if it's a list or single object
            if isinstance(data, list):
                print(f"   ✓ Format: Array with {len(data)} items")
                if len(data) > 0 and 'people' in data[0]:
                    people_count = len(data[0]['people'])
                    print(f"   ✓ People in first frame: {people_count}")
                    
                    if people_count > 0:
                        person = data[0]['people'][0]
                        pose_kp = person.get('pose_keypoints_2d', [])
                        face_kp = person.get('face_keypoints_2d', [])
                        hand_l_kp = person.get('hand_left_keypoints_2d', [])
                        hand_r_kp = person.get('hand_right_keypoints_2d', [])
                        
                        print(f"   ✓ Pose keypoints: {len(pose_kp)}")
                        print(f"   ✓ Face keypoints: {len(face_kp)}")
                        print(f"   ✓ Left hand keypoints: {len(hand_l_kp)}")
                        print(f"   ✓ Right hand keypoints: {len(hand_r_kp)}")
                        
                        # Check canvas dimensions
                        canvas_w = data[0].get('canvas_width', 'N/A')
                        canvas_h = data[0].get('canvas_height', 'N/A')
                        print(f"   ✓ Canvas size: {canvas_w}x{canvas_h}")
                        
                        # Check format (flat array vs nested array)
                        if len(pose_kp) > 0:
                            if isinstance(pose_kp[0], list):
                                print(f"   ✓ Format: OpenPose Editor format (nested arrays)")
                            else:
                                print(f"   ✓ Format: Standard OpenPose format (flat arrays)")
                        
            else:
                print(f"   ✓ Format: Single object")
                
        except json.JSONDecodeError as e:
            print(f"   ✗ JSON parsing error: {e}")
        except Exception as e:
            print(f"   ✗ Error: {e}")

def show_usage_instructions():
    """Show how to use the batch loader in ComfyUI"""
    
    print("\n" + "=" * 60)
    print("HOW TO USE POSE BATCH LOADER IN COMFYUI")
    print("=" * 60)
    
    print("\n1. RESTART COMFYUI")
    print("   After adding the new nodes, restart ComfyUI to load them.")
    
    print("\n2. ADD THE NODES")
    print("   Right-click in ComfyUI workflow → Add Node → ultimate-openpose")
    print("   You should now see:")
    print("   - OpenPose Editor")
    print("   - Pose Batch Loader  ← NEW!")
    print("   - Pose Batch Iterator ← NEW!")
    
    print("\n3. SETUP POSE BATCH LOADER")
    print("   - folder_path: f:/0VideoForAi/Undead/stable_pose_normal/json")
    print("   - file_pattern: *.json")
    print("   - current_index: 0 (start with first file)")
    print("   - sort_files: true (alphabetical order)")
    print("   - loop_batch: false (or true for automatic cycling)")
    
    print("\n4. CONNECT THE NODES")
    print("   Pose Batch Loader → OpenPose Editor")
    print("   POSE_KEYPOINT     → POSE_KEYPOINT")
    
    print("\n5. WORKFLOW EXAMPLE")
    print("   [Pose Batch Loader] → [OpenPose Editor] → [Your AI Model]")
    print("            ↓")
    print("   Current file info displayed in outputs")
    
    print("\n6. CYCLING THROUGH POSES")
    print("   - Change current_index to load different poses")
    print("   - Use TOTAL_COUNT output to see how many files available")
    print("   - Use FILENAME output to see which file is loaded")
    print("   - Enable loop_batch for automatic cycling in batch processing")
    
    print("\n7. OUTPUTS AVAILABLE")
    print("   - POSE_KEYPOINT: Direct pose data for OpenPose Editor")
    print("   - POSE_JSON: JSON string representation")  
    print("   - FILENAME: Current file being processed")
    print("   - TOTAL_COUNT: Total JSON files found")
    print("   - CURRENT_INDEX: Current file index")

if __name__ == "__main__":
    test_json_loading()
    show_usage_instructions()
