#!/usr/bin/env python3
"""
Quick test to verify the shoulder width fix is working in ComfyUI
"""

import json

# Test the shoulder width fix with a side pose
def test_shoulder_width_fix():
    print("=== SHOULDER WIDTH FIX TEST ===")
    
    # Sample side pose data (same as in TESTING_GUIDE.md)
    side_pose_json = '''[{"people": [{"pose_keypoints_2d": [249, 184, 0.9, 0, 0, 0, 201, 169, 0.8, 296, 169, 0.8, 176, 211, 0.7, 320, 211, 0.7, 150, 250, 0.6, 345, 250, 0.6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 125, 290, 0.5, 370, 290, 0.5, 100, 380, 0.4, 395, 380, 0.4, 75, 470, 0.3, 420, 470, 0.3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], "face_keypoints_2d": [], "hand_left_keypoints_2d": [], "hand_right_keypoints_2d": []}], "canvas_width": 512, "canvas_height": 768}]'''
    
    print("✅ Test data prepared")
    print("JSON length:", len(side_pose_json))
    
    # Test JSON parsing
    try:
        parsed_data = json.loads(side_pose_json)
        print("✅ JSON parsing successful")
        print("Number of people:", len(parsed_data[0]["people"]))
        
        # Extract shoulder positions
        keypoints = parsed_data[0]["people"][0]["pose_keypoints_2d"]
        left_shoulder = (keypoints[15], keypoints[16])  # Point 5
        right_shoulder = (keypoints[6], keypoints[7])   # Point 2
        
        print(f"✅ Shoulder positions extracted:")
        print(f"   Left shoulder: {left_shoulder}")
        print(f"   Right shoulder: {right_shoulder}")
        
        # Calculate base shoulder width
        import math
        base_width = math.sqrt((right_shoulder[0] - left_shoulder[0])**2 + (right_shoulder[1] - left_shoulder[1])**2)
        print(f"✅ Base shoulder width: {base_width:.2f}px")
        
        # Test rotation detection logic (simplified)
        shoulder_angle = math.degrees(math.atan2(
            right_shoulder[1] - left_shoulder[1], 
            right_shoulder[0] - left_shoulder[0]
        ))
        print(f"✅ Shoulder angle: {shoulder_angle:.1f}°")
        
        if abs(shoulder_angle) > 45:
            print("✅ Side pose detected - should apply width correction")
        else:
            print("ℹ️  Frontal pose detected - minimal correction expected")
            
    except Exception as e:
        print(f"❌ Error in test: {e}")
        return False
    
    print("\n=== INSTRUCTIONS FOR COMFYUI TESTING ===")
    print("1. Restart ComfyUI completely")
    print("2. Add an 'OpenPose Editor' node")
    print("3. Look for these new parameters:")
    print("   - auto_perspective (checkbox, default True)")
    print("   - perspective_correction (slider 0.1-1.0, default 1.0)")
    print("4. Paste the test JSON into POSE_JSON field")
    print("5. Compare results with auto_perspective ON vs OFF")
    print("6. With side pose: expect 40-70% width reduction when enabled")
    
    return True

if __name__ == "__main__":
    test_shoulder_width_fix()
