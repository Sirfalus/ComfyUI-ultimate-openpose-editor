#!/usr/bin/env python3
"""
2D to 3D Pose Converter for OpenPose Editor
Converts 2D OpenPose data to 3D format for use with the 3D OpenPose Editor
for better perspective handling and pose adjustments.
"""

import json
import numpy as np
import math
from typing import Dict, List, Optional, Tuple

class Pose2DTo3DConverter:
    """Converts 2D OpenPose data to 3D format for the 3D OpenPose Editor"""
    
    def __init__(self):
        # OpenPose 25-point body model keypoint indices
        self.BODY_25_KEYPOINTS = {
            0: "Nose",
            1: "Neck", 
            2: "RShoulder",
            3: "RElbow",
            4: "RWrist",
            5: "LShoulder",
            6: "LElbow", 
            7: "LWrist",
            8: "MidHip",
            9: "RHip",
            10: "RKnee",
            11: "RAnkle",
            12: "LHip",
            13: "LKnee",
            14: "LAnkle",
            15: "REye",
            16: "LEye",
            17: "REar",
            18: "LEar",
            19: "LBigToe",
            20: "LSmallToe",
            21: "LHeel",
            22: "RBigToe",
            23: "RSmallToe",
            24: "RHeel"
        }
        
    def estimate_3d_depth_from_rotation(self, pose_2d: np.ndarray, auto_rotation_factor: float) -> np.ndarray:
        """
        Estimate 3D depth coordinates based on 2D pose and rotation factor.
        Uses perspective geometry to estimate realistic depth values.
        """
        if pose_2d.shape[0] < 25 or pose_2d.shape[1] < 3:
            return np.zeros((25, 3))
            
        pose_3d = pose_2d.copy()
        
        # Calculate rotation angle from the auto_rotation_factor
        # auto_rotation_factor ranges from 0.3 (heavy rotation) to 1.0 (frontal)
        # Convert to rotation angle: 0.3 -> ~60 degrees, 1.0 -> 0 degrees
        rotation_angle = (1.0 - auto_rotation_factor) * 60.0  # degrees
        rotation_rad = math.radians(rotation_angle)
        
        # Get key reference points
        neck = pose_2d[1] if len(pose_2d) > 1 else np.array([0, 0, 0])
        rshoulder = pose_2d[2] if len(pose_2d) > 2 else np.array([0, 0, 0])
        lshoulder = pose_2d[5] if len(pose_2d) > 5 else np.array([0, 0, 0])
        
        # Check if we have valid shoulder data
        if rshoulder[2] < 0.1 or lshoulder[2] < 0.1:  # confidence too low
            return pose_3d
            
        # Calculate shoulder width and center
        shoulder_center_x = (rshoulder[0] + lshoulder[0]) / 2
        shoulder_center_y = (rshoulder[1] + lshoulder[1]) / 2
        
        # Estimate depth based on body rotation
        # More rotated poses have more depth variation
        base_depth = 100  # Base depth in arbitrary units
        depth_variation = 50 * (1.0 - auto_rotation_factor)  # More variation when rotated
        
        # Assign depth values based on body part positions and rotation
        for i, (x, y, conf) in enumerate(pose_2d):
            if conf < 0.1:  # Skip invalid points
                continue
                
            # Calculate relative position from body center
            rel_x = x - shoulder_center_x
            rel_y = y - shoulder_center_y
            
            # Estimate depth based on body part and rotation
            if i in [2, 3, 4]:  # Right arm (closer to camera when rotated right)
                depth_offset = depth_variation * math.cos(rotation_rad)
            elif i in [5, 6, 7]:  # Left arm (farther when rotated right)  
                depth_offset = -depth_variation * math.cos(rotation_rad)
            elif i in [9, 10, 11]:  # Right leg
                depth_offset = depth_variation * 0.5 * math.cos(rotation_rad)
            elif i in [12, 13, 14]:  # Left leg
                depth_offset = -depth_variation * 0.5 * math.cos(rotation_rad)
            else:  # Central body parts
                depth_offset = 0
                
            # Add some natural body depth variation
            if i == 0:  # Nose - typically forward
                depth_offset += 20
            elif i in [15, 16]:  # Eyes
                depth_offset += 15
            elif i == 8:  # Mid hip - body center
                depth_offset = 0
                
            pose_3d[i, 2] = base_depth + depth_offset  # Z coordinate
            
        return pose_3d
        
    def convert_2d_pose_to_3d_format(self, pose_2d_data: Dict, auto_rotation_factor: float = 1.0) -> Dict:
        """
        Convert 2D OpenPose data to 3D editor format.
        
        Args:
            pose_2d_data: 2D OpenPose JSON data
            auto_rotation_factor: Rotation factor from the automatic detection (0.3-1.0)
            
        Returns:
            3D editor compatible format
        """
        if 'people' not in pose_2d_data or not pose_2d_data['people']:
            return self._create_empty_3d_scene()
            
        person = pose_2d_data['people'][0]
        
        # Extract 2D keypoints
        pose_keypoints = np.array(person.get('pose_keypoints_2d', []))
        if pose_keypoints.size == 0:
            return self._create_empty_3d_scene()
            
        # Reshape to proper format if needed
        if pose_keypoints.ndim == 1:
            pose_keypoints = pose_keypoints.reshape(-1, 3)
            
        # Ensure we have at least 25 points (pad with zeros if needed)
        if len(pose_keypoints) < 25:
            padded = np.zeros((25, 3))
            padded[:len(pose_keypoints)] = pose_keypoints
            pose_keypoints = padded
            
        # Convert to 3D with estimated depth
        pose_3d = self.estimate_3d_depth_from_rotation(pose_keypoints, auto_rotation_factor)
        
        # Convert to 3D editor format
        canvas_width = pose_2d_data.get('canvas_width', 512)
        canvas_height = pose_2d_data.get('canvas_height', 768)
        
        # Normalize coordinates to 3D editor space
        normalized_pose = self._normalize_pose_for_3d_editor(pose_3d, canvas_width, canvas_height)
        
        # Create 3D scene data
        scene_data = {
            "header": "Openpose Editor by Yu Zhu",
            "version": "1.0.0",
            "object": {
                "bodies": [self._create_3d_body_data(normalized_pose)],
                "camera": self._create_default_camera_data()
            },
            "setting": {},
            "metadata": {
                "source": "2D_to_3D_converted",
                "original_rotation_factor": auto_rotation_factor,
                "original_canvas_size": [canvas_width, canvas_height],
                "conversion_timestamp": self._get_timestamp()
            }
        }
        
        return scene_data
        
    def _normalize_pose_for_3d_editor(self, pose_3d: np.ndarray, canvas_width: int, canvas_height: int) -> np.ndarray:
        """Normalize 2D coordinates to 3D editor coordinate system"""
        normalized = pose_3d.copy()
        
        # Convert from pixel coordinates to normalized coordinates
        # Assuming 3D editor uses a coordinate system centered at origin
        for i, (x, y, z) in enumerate(pose_3d):
            if pose_3d[i, 2] < 0.1:  # Skip invalid points (confidence check from original data)
                continue
                
            # Normalize X and Y to range approximately [-1, 1]
            normalized[i, 0] = (x / canvas_width - 0.5) * 2.0
            normalized[i, 1] = -(y / canvas_height - 0.5) * 2.0  # Flip Y axis for 3D space
            
            # Z is already in arbitrary 3D units
            normalized[i, 2] = z / 100.0  # Scale to reasonable 3D editor range
            
        return normalized
        
    def _create_3d_body_data(self, pose_3d: np.ndarray) -> Dict:
        """Create 3D body data structure for the 3D editor"""
        
        # Create bone structure - this is a simplified version
        # The actual 3D editor may need more complex bone relationships
        bones = []
        
        # Define basic bone connections for OpenPose 25-point model
        bone_connections = [
            (1, 0),   # Neck to Nose
            (1, 2),   # Neck to Right Shoulder  
            (2, 3),   # Right Shoulder to Right Elbow
            (3, 4),   # Right Elbow to Right Wrist
            (1, 5),   # Neck to Left Shoulder
            (5, 6),   # Left Shoulder to Left Elbow
            (6, 7),   # Left Elbow to Left Wrist
            (1, 8),   # Neck to Mid Hip
            (8, 9),   # Mid Hip to Right Hip
            (9, 10),  # Right Hip to Right Knee
            (10, 11), # Right Knee to Right Ankle
            (8, 12),  # Mid Hip to Left Hip
            (12, 13), # Left Hip to Left Knee
            (13, 14), # Left Knee to Left Ankle
            (0, 15),  # Nose to Right Eye
            (0, 16),  # Nose to Left Eye
            (15, 17), # Right Eye to Right Ear
            (16, 18), # Left Eye to Left Ear
        ]
        
        # Create bone data
        for i, (start_idx, end_idx) in enumerate(bone_connections):
            if start_idx < len(pose_3d) and end_idx < len(pose_3d):
                start_pos = pose_3d[start_idx]
                end_pos = pose_3d[end_idx]
                
                # Skip if either point is invalid
                if start_pos[2] < 0.1 or end_pos[2] < 0.1:
                    continue
                    
                bone = {
                    "name": f"bone_{i}",
                    "parent": start_idx,
                    "position": [float(end_pos[0]), float(end_pos[1]), float(end_pos[2])],
                    "rotation": [0.0, 0.0, 0.0],
                    "scale": [1.0, 1.0, 1.0]
                }
                bones.append(bone)
                
        return {
            "name": "body_0",
            "type": "SkinnedMesh",
            "bones": bones,
            "position": [0.0, 0.0, 0.0],
            "rotation": [0.0, 0.0, 0.0],
            "scale": [1.0, 1.0, 1.0],
            "visible": True
        }
        
    def _create_default_camera_data(self) -> Dict:
        """Create default camera data for 3D editor"""
        return {
            "position": [0, 0, 5],
            "rotation": [0, 0, 0],
            "target": [0, 0, 0],
            "near": 0.1,
            "far": 1000,
            "zoom": 1.0
        }
        
    def _create_empty_3d_scene(self) -> Dict:
        """Create an empty 3D scene"""
        return {
            "header": "Openpose Editor by Yu Zhu",
            "version": "1.0.0", 
            "object": {
                "bodies": [],
                "camera": self._create_default_camera_data()
            },
            "setting": {},
            "metadata": {
                "source": "2D_to_3D_converted_empty",
                "conversion_timestamp": self._get_timestamp()
            }
        }
        
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()
        
    def convert_3d_scene_back_to_2d(self, scene_3d_data: Dict, target_canvas_width: int = 512, target_canvas_height: int = 768) -> Dict:
        """
        Convert 3D scene data back to 2D OpenPose format.
        This allows us to use the adjusted 3D pose as a 2D reference.
        """
        if 'object' not in scene_3d_data or 'bodies' not in scene_3d_data['object']:
            return self._create_empty_2d_pose(target_canvas_width, target_canvas_height)
            
        bodies = scene_3d_data['object']['bodies']
        if not bodies:
            return self._create_empty_2d_pose(target_canvas_width, target_canvas_height)
            
        body = bodies[0]  # Use first body
        bones = body.get('bones', [])
        
        # Extract 3D positions from bones and convert to 2D
        pose_2d = np.zeros((25, 3))
        
        # Project 3D coordinates back to 2D
        for bone in bones:
            position = bone.get('position', [0, 0, 0])
            parent_idx = bone.get('parent', 0)
            
            if parent_idx < 25:
                # Simple orthographic projection (ignore Z for now)
                x_2d = (position[0] / 2.0 + 0.5) * target_canvas_width
                y_2d = (-position[1] / 2.0 + 0.5) * target_canvas_height
                
                pose_2d[parent_idx] = [x_2d, y_2d, 1.0]  # Set confidence to 1.0
                
        # Create 2D OpenPose format
        pose_2d_data = {
            "canvas_width": target_canvas_width,
            "canvas_height": target_canvas_height,
            "people": [{
                "person_id": [-1],
                "pose_keypoints_2d": pose_2d.tolist(),
                "face_keypoints_2d": [],
                "hand_left_keypoints_2d": [],
                "hand_right_keypoints_2d": [],
                "pose_keypoints_3d": [],
                "face_keypoints_3d": [],
                "hand_left_keypoints_3d": [],
                "hand_right_keypoints_3d": []
            }],
            "metadata": {
                "source": "3D_to_2D_converted",
                "conversion_timestamp": self._get_timestamp()
            }
        }
        
        return pose_2d_data
        
    def _create_empty_2d_pose(self, canvas_width: int, canvas_height: int) -> Dict:
        """Create empty 2D pose data"""
        return {
            "canvas_width": canvas_width,
            "canvas_height": canvas_height,
            "people": [{
                "person_id": [-1],
                "pose_keypoints_2d": [],
                "face_keypoints_2d": [],
                "hand_left_keypoints_2d": [],
                "hand_right_keypoints_2d": [],
                "pose_keypoints_3d": [],
                "face_keypoints_3d": [],
                "hand_left_keypoints_3d": [],
                "hand_right_keypoints_3d": []
            }]
        }


def convert_pose_to_3d_editor_format(pose_2d_json_path: str, output_3d_json_path: str, auto_rotation_factor: float = 1.0) -> bool:
    """
    Convenience function to convert a 2D pose file to 3D editor format.
    
    Args:
        pose_2d_json_path: Path to input 2D OpenPose JSON file
        output_3d_json_path: Path to output 3D editor JSON file
        auto_rotation_factor: Rotation factor (0.3-1.0)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        converter = Pose2DTo3DConverter()
        
        # Load 2D pose data
        with open(pose_2d_json_path, 'r') as f:
            pose_2d_data = json.load(f)
            
        # Handle list format
        if isinstance(pose_2d_data, list) and pose_2d_data:
            pose_2d_data = pose_2d_data[0]
            
        # Convert to 3D format
        scene_3d_data = converter.convert_2d_pose_to_3d_format(pose_2d_data, auto_rotation_factor)
        
        # Save 3D scene data
        with open(output_3d_json_path, 'w') as f:
            json.dump(scene_3d_data, f, indent=2)
            
        print(f"Successfully converted {pose_2d_json_path} to 3D format: {output_3d_json_path}")
        print(f"Rotation factor applied: {auto_rotation_factor}")
        return True
        
    except Exception as e:
        print(f"Error converting pose to 3D format: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test the converter with the side pose
    import sys
    import os
    
    # Get the side_pose.json path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    side_pose_path = os.path.join(current_dir, "side_pose.json")
    output_3d_path = os.path.join(current_dir, "side_pose_3d_editor.json")
    
    if os.path.exists(side_pose_path):
        # Use a rotation factor that represents the side pose (0.3 = heavy rotation)
        success = convert_pose_to_3d_editor_format(side_pose_path, output_3d_path, 0.3)
        if success:
            print(f"\n✅ 3D editor file created: {output_3d_path}")
            print("\nNext steps:")
            print("1. Open the 3D OpenPose Editor at http://localhost:5173/open-pose-editor/")
            print("2. Load the created 3D scene file")
            print("3. Adjust the pose with proper 3D rotation")
            print("4. Export back to 2D format for use in ComfyUI")
        else:
            print("❌ Conversion failed")
    else:
        print(f"❌ Side pose file not found: {side_pose_path}")
