#!/usr/bin/env python3
"""
3D to 2D Pose Converter - Reverse converter for the 3D OpenPose Editor
Converts adjusted 3D poses back to 2D OpenPose format for use in ComfyUI
"""

import json
import numpy as np
import math
from typing import Dict, List, Optional, Tuple

class Pose3DTo2DConverter:
    """Converts 3D OpenPose Editor data back to 2D format"""
    
    def __init__(self):
        # Camera projection parameters
        self.default_fov = 50  # Field of view in degrees
        self.camera_distance = 5.0
        self.aspect_ratio = 512 / 768  # Width / Height
        
    def project_3d_to_2d(self, pos_3d: List[float], camera_data: Optional[Dict] = None) -> Tuple[float, float]:
        """
        Project 3D position to 2D screen coordinates using perspective projection
        
        Args:
            pos_3d: [x, y, z] position in 3D space
            camera_data: Camera parameters (optional)
            
        Returns:
            (x, y) in normalized coordinates [0, 1]
        """
        if not pos_3d or len(pos_3d) < 3:
            return (0.5, 0.5)
            
        x, y, z = pos_3d[0], pos_3d[1], pos_3d[2]
        
        # Use camera data if available
        if camera_data:
            cam_pos = camera_data.get('position', [0, 0, 5])
            cam_target = camera_data.get('target', [0, 0, 0])
            
            # Translate to camera space
            x -= cam_pos[0]
            y -= cam_pos[1] 
            z -= cam_pos[2]
            
        # Simple perspective projection
        if z <= 0:
            z = 0.1  # Prevent division by zero
            
        # Calculate field of view factor
        fov_rad = math.radians(self.default_fov)
        fov_factor = math.tan(fov_rad / 2)
        
        # Project to normalized device coordinates
        projected_x = x / (z * fov_factor * self.aspect_ratio)
        projected_y = y / (z * fov_factor)
        
        # Convert to screen coordinates [0, 1]
        screen_x = (projected_x + 1) / 2
        screen_y = (1 - projected_y) / 2  # Flip Y axis
        
        # Clamp to valid range
        screen_x = max(0, min(1, screen_x))
        screen_y = max(0, min(1, screen_y))
        
        return screen_x, screen_y
        
    def extract_keypoints_from_3d_scene(self, scene_data: Dict) -> np.ndarray:
        """
        Extract 2D keypoints from 3D scene data
        
        Returns:
            numpy array of shape (25, 3) with [x, y, confidence]
        """
        pose_2d = np.zeros((25, 3))
        
        if 'object' not in scene_data or 'bodies' not in scene_data['object']:
            return pose_2d
            
        bodies = scene_data['object']['bodies']
        if not bodies:
            return pose_2d
            
        body = bodies[0]  # Use first body
        camera_data = scene_data['object'].get('camera', {})
        
        # Extract bone positions
        bones = body.get('bones', [])
        
        # Create a mapping from parent index to 3D position
        bone_positions = {}
        
        for bone in bones:
            parent_idx = bone.get('parent', 0)
            position_3d = bone.get('position', [0, 0, 0])
            
            if 0 <= parent_idx < 25:
                bone_positions[parent_idx] = position_3d
                
        # Also include the body root position
        body_position = body.get('position', [0, 0, 0])
        
        # Convert 3D positions to 2D
        for i in range(25):
            if i in bone_positions:
                pos_3d = bone_positions[i]
                x_norm, y_norm = self.project_3d_to_2d(pos_3d, camera_data)
                
                # Set confidence to 1.0 for valid points
                pose_2d[i] = [x_norm, y_norm, 1.0]
            else:
                # No data for this keypoint
                pose_2d[i] = [0, 0, 0]
                
        return pose_2d
        
    def convert_3d_scene_to_2d_pose(self, scene_data: Dict, canvas_width: int = 512, canvas_height: int = 768) -> Dict:
        """
        Convert 3D scene data to 2D OpenPose format
        
        Args:
            scene_data: 3D editor scene data
            canvas_width: Target canvas width
            canvas_height: Target canvas height
            
        Returns:
            2D OpenPose format dictionary
        """
        # Extract normalized keypoints
        pose_2d_norm = self.extract_keypoints_from_3d_scene(scene_data)
        
        # Convert normalized coordinates to pixel coordinates
        pose_2d_pixels = pose_2d_norm.copy()
        for i in range(len(pose_2d_pixels)):
            if pose_2d_pixels[i, 2] > 0:  # Valid point
                pose_2d_pixels[i, 0] = pose_2d_pixels[i, 0] * canvas_width
                pose_2d_pixels[i, 1] = pose_2d_pixels[i, 1] * canvas_height
                
        # Create OpenPose format
        pose_data = {
            "canvas_width": canvas_width,
            "canvas_height": canvas_height,
            "people": [{
                "person_id": [-1],
                "pose_keypoints_2d": pose_2d_pixels.tolist(),
                "face_keypoints_2d": [],
                "hand_left_keypoints_2d": [],
                "hand_right_keypoints_2d": [],
                "pose_keypoints_3d": [],
                "face_keypoints_3d": [],
                "hand_left_keypoints_3d": [],
                "hand_right_keypoints_3d": []
            }],
            "metadata": {
                "source": "3D_editor_converted",
                "original_3d_scene": True,
                "conversion_timestamp": self._get_timestamp()
            }
        }
        
        return pose_data
        
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().isoformat()


def convert_3d_scene_to_2d_pose(scene_3d_json_path: str, output_2d_json_path: str, 
                               canvas_width: int = 512, canvas_height: int = 768) -> bool:
    """
    Convenience function to convert 3D scene to 2D pose
    
    Args:
        scene_3d_json_path: Path to 3D editor scene file
        output_2d_json_path: Path to output 2D pose file
        canvas_width: Target canvas width
        canvas_height: Target canvas height
        
    Returns:
        True if successful, False otherwise
    """
    try:
        converter = Pose3DTo2DConverter()
        
        # Load 3D scene data
        with open(scene_3d_json_path, 'r') as f:
            scene_data = json.load(f)
            
        # Convert to 2D
        pose_2d_data = converter.convert_3d_scene_to_2d_pose(scene_data, canvas_width, canvas_height)
        
        # Save 2D pose data
        with open(output_2d_json_path, 'w') as f:
            json.dump(pose_2d_data, f, indent=2)
            
        print(f"Successfully converted {scene_3d_json_path} to 2D pose: {output_2d_json_path}")
        print(f"Canvas size: {canvas_width}x{canvas_height}")
        return True
        
    except Exception as e:
        print(f"Error converting 3D scene to 2D pose: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test the reverse converter
    import os
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scene_3d_path = os.path.join(current_dir, "side_pose_3d_editor.json")
    output_2d_path = os.path.join(current_dir, "side_pose_converted_back_2d.json")
    
    if os.path.exists(scene_3d_path):
        success = convert_3d_scene_to_2d_pose(scene_3d_path, output_2d_path)
        if success:
            print(f"\n✅ Converted back to 2D: {output_2d_path}")
            print("\nThis 2D pose can now be used in ComfyUI with corrected perspective!")
        else:
            print("❌ Reverse conversion failed")
    else:
        print(f"❌ 3D scene file not found: {scene_3d_path}")
