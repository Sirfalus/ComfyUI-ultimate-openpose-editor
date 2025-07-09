# 3D OpenPose Editor Workflow Guide

## Overview

This guide explains how to use the 3D OpenPose Editor as an alternative solution for handling shoulder width problems in rotated poses. The 3D approach provides natural perspective handling and intuitive pose adjustments.

## Problem Summary

The original issue was that when characters rotate their body (particularly in side poses), the shoulder width remained unrealistically long as if viewed from the front, causing "overstretched shoulder" appearances. While we implemented a 2D solution with automatic rotation detection, the 3D editor provides a more intuitive and visually accurate approach.

## 3D Editor Workflow

### Step 1: Convert 2D Pose to 3D Format

Use the `pose_2d_to_3d_converter.py` script to convert your 2D OpenPose data to 3D editor format:

```python
from pose_2d_to_3d_converter import convert_pose_to_3d_editor_format

# Convert with automatic rotation detection
convert_pose_to_3d_editor_format(
    "side_pose.json",           # Input 2D pose
    "side_pose_3d.json",        # Output 3D scene
    auto_rotation_factor=0.3    # 0.3 = heavy rotation, 1.0 = frontal
)
```

The rotation factor is determined by our automatic detection:

- **1.0**: Frontal pose (no rotation)
- **0.8-0.95**: Slight rotation
- **0.6-0.8**: Moderate rotation
- **0.3-0.6**: Heavy rotation (side poses)

### Step 2: Open 3D Editor

1. Start the 3D OpenPose Editor:

   ```bash
   cd f:\3dopen-pose-editor
   npm run dev
   ```

2. Open in browser: `http://localhost:5173/open-pose-editor/`

### Step 3: Load and Adjust Pose

1. **Load Scene**: In the 3D editor, load your converted 3D scene file (`side_pose_3d.json`)

2. **Adjust Pose**:

   - Rotate the body naturally in 3D space
   - Adjust shoulder positions with proper perspective
   - Fine-tune hand and limb positions
   - Use the visual 3D representation to ensure realistic proportions

3. **Save Scene**: Export the adjusted scene from the 3D editor

### Step 4: Convert Back to 2D

Use the `pose_3d_to_2d_converter.py` script to convert the adjusted 3D pose back to 2D:

```python
from pose_3d_to_2d_converter import convert_3d_scene_to_2d_pose

# Convert back to 2D with proper perspective
convert_3d_scene_to_2d_pose(
    "adjusted_scene_3d.json",   # 3D scene from editor
    "corrected_pose_2d.json",   # Output 2D pose
    canvas_width=512,
    canvas_height=768
)
```

### Step 5: Use in ComfyUI

The resulting 2D pose file can be used directly in ComfyUI with the OpenPose Editor node, and will have naturally corrected shoulder width and perspective.

## Scripts Reference

### 1. `pose_2d_to_3d_converter.py`

**Purpose**: Converts 2D OpenPose data to 3D editor format with estimated depth based on rotation.

**Key Features**:

- Automatic depth estimation from rotation factor
- Perspective geometry calculations
- 3D bone structure creation
- Maintains keypoint relationships

**Usage**:

```python
from pose_2d_to_3d_converter import Pose2DTo3DConverter

converter = Pose2DTo3DConverter()
scene_3d = converter.convert_2d_pose_to_3d_format(pose_2d_data, rotation_factor)
```

### 2. `pose_3d_to_2d_converter.py`

**Purpose**: Converts adjusted 3D scenes back to 2D OpenPose format.

**Key Features**:

- Perspective projection from 3D to 2D
- Camera parameter handling
- Coordinate system conversion
- Maintains pose accuracy

**Usage**:

```python
from pose_3d_to_2d_converter import Pose3DTo2DConverter

converter = Pose3DTo2DConverter()
pose_2d = converter.convert_3d_scene_to_2d_pose(scene_3d_data, width, height)
```

## Integration with Existing System

### Combined Approach

You can use both the 2D automatic correction and 3D editor approach:

1. **Quick Fixes**: Use the automatic 2D rotation detection for batch processing
2. **Precision Work**: Use the 3D editor workflow for specific poses that need manual adjustment

### Automation Scripts

Create batch scripts to process multiple poses:

```python
import os
import glob
from pose_2d_to_3d_converter import convert_pose_to_3d_editor_format
from util import detect_body_rotation_factor

def batch_convert_to_3d(input_folder, output_folder):
    """Convert all poses in a folder to 3D editor format"""
    for json_file in glob.glob(os.path.join(input_folder, "*.json")):
        # Load pose and detect rotation
        with open(json_file, 'r') as f:
            pose_data = json.load(f)

        # Auto-detect rotation factor
        if 'people' in pose_data and pose_data['people']:
            keypoints = pose_data['people'][0].get('pose_keypoints_2d', [])
            rotation_factor = detect_body_rotation_factor(keypoints)
        else:
            rotation_factor = 1.0

        # Convert to 3D
        output_file = os.path.join(output_folder,
                                 os.path.basename(json_file).replace('.json', '_3d.json'))
        convert_pose_to_3d_editor_format(json_file, output_file, rotation_factor)
```

## Advantages of 3D Approach

### 1. **Visual Accuracy**

- True 3D representation of body rotation
- Natural perspective handling
- Intuitive visual feedback

### 2. **Precise Control**

- Manual fine-tuning capability
- Real-time visual feedback
- Better understanding of pose geometry

### 3. **No Algorithm Limitations**

- Not constrained by 2D rotation detection accuracy
- Can handle complex poses and edge cases
- User has full control over adjustments

### 4. **Educational Value**

- Helps understand pose geometry
- Visual learning of perspective effects
- Better intuition for pose correction

## Workflow Examples

### Example 1: Side Portrait Correction

```bash
# 1. Convert side pose to 3D (heavy rotation detected)
python -c "from pose_2d_to_3d_converter import convert_pose_to_3d_editor_format; convert_pose_to_3d_editor_format('side_portrait.json', 'side_portrait_3d.json', 0.3)"

# 2. Open 3D editor and adjust
# Load side_portrait_3d.json, adjust pose, save as side_portrait_adjusted_3d.json

# 3. Convert back to 2D
python -c "from pose_3d_to_2d_converter import convert_3d_scene_to_2d_pose; convert_3d_scene_to_2d_pose('side_portrait_adjusted_3d.json', 'side_portrait_corrected.json')"
```

### Example 2: Three-Quarter View Correction

```bash
# 1. Convert with moderate rotation
python -c "from pose_2d_to_3d_converter import convert_pose_to_3d_editor_format; convert_pose_to_3d_editor_format('three_quarter.json', 'three_quarter_3d.json', 0.7)"

# 2. Adjust in 3D editor
# 3. Convert back to 2D
python -c "from pose_3d_to_2d_converter import convert_3d_scene_to_2d_pose; convert_3d_scene_to_2d_pose('three_quarter_adjusted_3d.json', 'three_quarter_corrected.json')"
```

## Troubleshooting

### Common Issues

1. **3D Editor Not Loading**:

   - Ensure npm dependencies are installed
   - Check that the dev server is running on correct port

2. **Conversion Errors**:

   - Verify input JSON format
   - Check for missing keypoint data
   - Ensure rotation factor is in valid range (0.3-1.0)

3. **Pose Appears Distorted**:
   - Adjust camera position in 3D editor
   - Check coordinate system conversions
   - Verify canvas dimensions match target

### Best Practices

1. **Always backup original poses** before conversion
2. **Use appropriate rotation factors** based on pose type
3. **Test with simple poses first** to understand the workflow
4. **Save intermediate 3D scenes** for future adjustments

## Future Enhancements

### Planned Features

1. **Direct ComfyUI Integration**: Node to automatically launch 3D editor
2. **Batch Processing UI**: Interface for processing multiple poses
3. **Preset Rotations**: Common rotation presets for different pose types
4. **Real-time Preview**: Live preview of 2D result while editing in 3D

### Extension Possibilities

1. **Hand Pose Support**: Extend to include hand keypoints
2. **Face Keypoints**: Support for facial feature adjustments
3. **Animation Support**: Timeline-based pose adjustments
4. **AI Assistance**: Automatic pose improvement suggestions

---

This 3D editor approach provides a powerful alternative to the automatic 2D correction, offering both precision and visual clarity for pose adjustments. Use it when you need the highest quality results or when working with particularly challenging rotated poses.
