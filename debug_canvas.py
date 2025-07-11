#!/usr/bin/env python3
"""
Test script to debug canvas dimension setting in the actual util.py implementation
"""

import json
import sys
import os
import numpy as np

# Mock the ComfyUI ProgressBar
class MockProgressBar:
    def __init__(self, total):
        self.total = total
        self.current = 0
    
    def update(self, n):
        self.current += n
        print(f"Progress: {self.current}/{self.total}")

# Mock the comfy.utils module
sys.modules['comfy'] = type('MockModule', (), {})()
sys.modules['comfy.utils'] = type('MockModule', (), {'ProgressBar': MockProgressBar})()

# Now import our util functions
try:
    from util import draw_pose_json
    print("✅ Successfully imported draw_pose_json from util.py")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)

def test_canvas_dimensions():
    """Test that canvas dimensions are properly set in the output"""
    
    # Load the bad_json.json file
    try:
        with open('bad_json.json', 'r') as f:
            input_data = json.load(f)
    except FileNotFoundError:
        print("❌ bad_json.json file not found!")
        return False
    
    print(f"📁 Loaded JSON with {len(input_data)} frame(s)")
    
    # Convert to JSON string as expected by the function
    input_json_str = json.dumps(input_data)
    
    # Test parameters (using defaults)
    resolution_x = -1  # Use original/default dimensions
    use_ground_plane = True
    show_body = True
    show_face = True
    show_hands = True
    pose_marker_size = 4
    face_marker_size = 3
    hand_marker_size = 2
    
    # Scale parameters (all set to 1.0 for no scaling)
    pelvis_scale = 1.0
    torso_scale = 1.0
    neck_scale = 1.0
    head_scale = 1.0
    eye_distance_scale = 1.0
    eye_height = 0.0
    eyebrow_height = 0.0
    left_eye_scale = 1.0
    right_eye_scale = 1.0
    left_eyebrow_scale = 1.0
    right_eyebrow_scale = 1.0
    mouth_scale = 1.0
    nose_scale_face = 1.0
    face_shape_scale = 1.0
    shoulder_scale = 1.0
    arm_scale = 1.0
    leg_scale = 1.0
    hands_scale = 1.0
    overall_scale = 1.0
    
    print("\n🔍 Testing canvas dimension handling...")
    print("Input JSON structure:")
    for i, frame in enumerate(input_data):
        print(f"  Frame {i+1}:")
        print(f"    Has canvas_width: {'canvas_width' in frame}")
        print(f"    Has canvas_height: {'canvas_height' in frame}")
        if 'canvas_width' in frame:
            print(f"    canvas_width: {frame['canvas_width']}")
        if 'canvas_height' in frame:
            print(f"    canvas_height: {frame['canvas_height']}")
    
    print("\n🚀 Calling draw_pose_json...")
    
    try:
        # Call the function
        pose_imgs, output_keypoints = draw_pose_json(
            input_json_str, resolution_x, use_ground_plane, show_body, show_face, show_hands,
            pose_marker_size, face_marker_size, hand_marker_size,
            pelvis_scale, torso_scale, neck_scale, head_scale, eye_distance_scale, eye_height, eyebrow_height,
            left_eye_scale, right_eye_scale, left_eyebrow_scale, right_eyebrow_scale,
            mouth_scale, nose_scale_face, face_shape_scale,
            shoulder_scale, arm_scale, leg_scale, hands_scale, overall_scale
        )
        
        print(f"✅ Function completed successfully!")
        print(f"📊 Returned {len(pose_imgs)} pose images")
        print(f"📊 Returned {len(output_keypoints)} keypoint objects")
        
        # Check the output keypoints
        print("\n📋 Output JSON structure:")
        for i, keypoint_obj in enumerate(output_keypoints):
            print(f"  Frame {i+1}:")
            print(f"    Has canvas_width: {'canvas_width' in keypoint_obj}")
            print(f"    Has canvas_height: {'canvas_height' in keypoint_obj}")
            if 'canvas_width' in keypoint_obj:
                print(f"    canvas_width: {keypoint_obj['canvas_width']}")
            if 'canvas_height' in keypoint_obj:
                print(f"    canvas_height: {keypoint_obj['canvas_height']}")
            print(f"    People count: {len(keypoint_obj.get('people', []))}")
        
        # Save the output for inspection
        with open('debug_output.json', 'w') as f:
            json.dump(output_keypoints, f, indent=2)
        
        print(f"\n💾 Saved output to 'debug_output.json'")
        
        # Verify canvas dimensions are present
        for i, keypoint_obj in enumerate(output_keypoints):
            if 'canvas_width' not in keypoint_obj or 'canvas_height' not in keypoint_obj:
                print(f"❌ Frame {i+1} is missing canvas dimensions!")
                return False
        
        print("✅ All frames have canvas dimensions!")
        return True
        
    except Exception as e:
        print(f"❌ Error calling draw_pose_json: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing canvas dimension handling in util.py...\n")
    
    if test_canvas_dimensions():
        print("\n🎉 Test completed successfully!")
        print("Check the debug output and console messages above.")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)
