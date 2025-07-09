# Shoulder Width Fix - Testing Guide

## Quick Test Instructions

### 1. Load the Node

- In ComfyUI, add the **"OpenPose Editor"** node
- You should see two new parameters at the bottom:
  - `auto_perspective` (checkbox) - defaults to True
  - `perspective_correction` (slider 0.1-1.0) - defaults to 1.0

### 2. Test with Side Pose

Load this test pose JSON into the POSE_JSON field:

```json
[
  {
    "people": [
      {
        "pose_keypoints_2d": [
          249, 184, 0.9, 0, 0, 0, 201, 169, 0.8, 296, 169, 0.8, 176, 211, 0.7,
          320, 211, 0.7, 150, 250, 0.6, 345, 250, 0.6, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 125, 290, 0.5, 370, 290, 0.5, 100, 380, 0.4, 395, 380,
          0.4, 75, 470, 0.3, 420, 470, 0.3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ],
        "face_keypoints_2d": [],
        "hand_left_keypoints_2d": [],
        "hand_right_keypoints_2d": []
      }
    ],
    "canvas_width": 512,
    "canvas_height": 768
  }
]
```

### 3. Compare Results

**With auto_perspective = True (automatic):**

- Should automatically detect this is a side pose
- Shoulder width should be reduced to ~30-40% of original
- More realistic proportions

**With auto_perspective = False + perspective_correction = 1.0:**

- Uses full shoulder width (no correction)
- Will look overstretched for side poses

**With auto_perspective = False + perspective_correction = 0.3:**

- Manual 70% width reduction
- Should match the automatic result

### 4. Visual Comparison

- Load a frontal pose - should show minimal/no correction
- Load a side pose - should show significant shoulder width reduction
- Compare with/without the correction to see the improvement

### 5. Expected Behavior

- **Frontal poses**: Little to no shoulder width change
- **Slight rotation**: 10-30% width reduction
- **Side poses**: 40-70% width reduction
- **Profile poses**: 60-80% width reduction

## Test Files Available

- `side_pose.json` - Heavy rotation example
- `front_pose.json` - Frontal pose example (if available)

## Troubleshooting

If the new parameters don't appear:

1. Restart ComfyUI completely
2. Check the terminal for any error messages
3. Verify the node is using the updated version

## What to Look For

✅ **Good Result**: Natural shoulder proportions that match the body rotation  
❌ **Problem**: Unrealistic wide shoulders on rotated poses

The fix should make pose adaptations look much more realistic, especially when transferring poses between characters of different body types!
