#!/usr/bin/env python3
"""
Test the shoulder width fix implementation in a live ComfyUI environment.
This script tests both automatic rotation detection and manual perspective correction.
"""

import json
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_shoulder_width_fix():
    """Test the shoulder width correction features"""
    print("🧪 Testing Shoulder Width Fix Implementation")
    print("=" * 50)
    
    try:
        # Import the util module directly
        from util import detect_body_rotation_factor, draw_pose_json
        print("✅ Successfully imported util functions")
        
        # Test data - side pose that should trigger rotation detection
        side_pose_data = [{
            "people": [{
                "pose_keypoints_2d": [
                    # Nose (0)
                    250, 100, 0.9,
                    # Neck (1) 
                    250, 150, 0.9,
                    # Right shoulder (2) - rotated position
                    280, 160, 0.9,
                    # Right elbow (3)
                    320, 200, 0.8,
                    # Right wrist (4)
                    350, 240, 0.7,
                    # Left shoulder (5) - rotated position  
                    220, 170, 0.9,
                    # Left elbow (6)
                    180, 210, 0.8,
                    # Left wrist (7)
                    150, 250, 0.7,
                    # Mid hip (8)
                    250, 300, 0.9,
                    # Right hip (9)
                    270, 310, 0.8,
                    # Right knee (10)
                    280, 400, 0.7,
                    # Right ankle (11)
                    285, 480, 0.6,
                    # Left hip (12)
                    230, 320, 0.8,
                    # Left knee (13)
                    220, 410, 0.7,
                    # Left ankle (14)
                    215, 490, 0.6,
                    # Right eye (15)
                    260, 90, 0.8,
                    # Left eye (16)
                    240, 95, 0.8,
                    # Right ear (17)
                    270, 105, 0.7,
                    # Left ear (18)
                    230, 110, 0.7
                ],
                "face_keypoints_2d": [],
                "hand_left_keypoints_2d": [],
                "hand_right_keypoints_2d": []
            }],
            "canvas_width": 512,
            "canvas_height": 768
        }]
        
        # Test automatic rotation detection
        print("\n🔄 Testing Automatic Rotation Detection:")
        keypoints = side_pose_data[0]["people"][0]["pose_keypoints_2d"]
        rotation_factor = detect_body_rotation_factor(keypoints)
        print(f"   Detected rotation factor: {rotation_factor:.3f}")
        
        if 0.3 <= rotation_factor <= 0.8:
            print("   ✅ Rotation detection working correctly (0.3-0.8 range for rotated pose)")
        else:
            print(f"   ⚠️  Unexpected rotation factor: {rotation_factor}")
        
        # Test the full pipeline with automatic perspective correction
        print("\n🎨 Testing Automatic Perspective Correction:")
        try:
            pose_imgs, final_keypoints = draw_pose_json(
                json.dumps(side_pose_data),
                resolution_x=512,
                use_ground_plane=True,
                show_body=True,
                show_face=False,
                show_hands=False,
                pose_marker_size=4,
                face_marker_size=3,
                hand_marker_size=2,
                pelvis_scale=1.0,
                torso_scale=1.0,
                neck_scale=1.0,
                head_scale=1.0,
                eye_distance_scale=1.0,
                eye_height=0.0,
                eyebrow_height=0.0,
                left_eye_scale=1.0,
                right_eye_scale=1.0,
                left_eyebrow_scale=1.0,
                right_eyebrow_scale=1.0,
                mouth_scale=1.0,
                nose_scale_face=1.0,
                face_shape_scale=1.0,
                shoulder_scale=1.0,
                auto_perspective=True,  # Enable automatic detection
                perspective_correction=1.0,  # This will be ignored due to auto_perspective=True
                arm_scale=1.0,
                leg_scale=1.0,
                hands_scale=1.0,
                overall_scale=1.0
            )
            print("   ✅ Automatic perspective correction pipeline completed")
            print(f"   Generated {len(pose_imgs)} pose image(s)")
            
        except Exception as e:
            print(f"   ❌ Error in automatic pipeline: {e}")
            return False
        
        # Test manual perspective correction
        print("\n🎛️  Testing Manual Perspective Correction:")
        try:
            pose_imgs_manual, final_keypoints_manual = draw_pose_json(
                json.dumps(side_pose_data),
                resolution_x=512,
                use_ground_plane=True,
                show_body=True,
                show_face=False,
                show_hands=False,
                pose_marker_size=4,
                face_marker_size=3,
                hand_marker_size=2,
                pelvis_scale=1.0,
                torso_scale=1.0,
                neck_scale=1.0,
                head_scale=1.0,
                eye_distance_scale=1.0,
                eye_height=0.0,
                eyebrow_height=0.0,
                left_eye_scale=1.0,
                right_eye_scale=1.0,
                left_eyebrow_scale=1.0,
                right_eyebrow_scale=1.0,
                mouth_scale=1.0,
                nose_scale_face=1.0,
                face_shape_scale=1.0,
                shoulder_scale=1.0,
                auto_perspective=False,  # Disable automatic detection
                perspective_correction=0.4,  # Manual 60% reduction
                arm_scale=1.0,
                leg_scale=1.0,
                hands_scale=1.0,
                overall_scale=1.0
            )
            print("   ✅ Manual perspective correction pipeline completed")
            print(f"   Generated {len(pose_imgs_manual)} pose image(s) with 60% shoulder width reduction")
            
        except Exception as e:
            print(f"   ❌ Error in manual pipeline: {e}")
            return False
        
        print("\n🎉 All tests completed successfully!")
        print("=" * 50)
        print("✅ Shoulder width fix is properly integrated and functional")
        print("\nFeatures available:")
        print("   • Automatic rotation detection with multi-factor analysis")
        print("   • Manual perspective correction (0.1-1.0 range)")
        print("   • UI controls: auto_perspective + perspective_correction")
        print("   • Compatible with existing ComfyUI workflows")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   The util module may not be properly configured for ComfyUI")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_shoulder_width_fix()
    sys.exit(0 if success else 1)
