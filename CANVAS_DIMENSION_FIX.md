# Canvas Dimension Preservation Fix

## Problem
When exporting JSON from the OpenPose Editor Node, the canvas dimensions were being reset to default values (512×768) instead of preserving the original canvas dimensions from the input JSON. This caused:

- Loss of original canvas size information (e.g., 720×1280 became 512×768)
- Unwanted cropping or scaling of the pose visualization
- Inconsistent output compared to input

## Root Cause
The output JSON generation was using the processed canvas dimensions (`W`, `H`) which could have been overridden by default values when handling missing canvas data, rather than preserving the original input canvas dimensions.

## Solution
Modified the canvas dimension handling in `util.py` to:

### 1. Separate Processing vs Output Dimensions
```python
# Handle missing canvas dimensions with default values
original_H = image_data.get('canvas_height')
original_W = image_data.get('canvas_width')

# Use original values for output if they exist, otherwise use defaults
if original_H is not None and original_W is not None:
    output_H = original_H
    output_W = original_W
else:
    output_H = 768
    output_W = 512

# Ensure dimensions are valid numbers for processing
try:
    H = int(original_H) if original_H is not None else 768
    W = int(original_W) if original_W is not None else 512
    if H <= 0: H = 768
    if W <= 0: W = 512
except (ValueError, TypeError):
    H, W = 768, 512
```

### 2. Preserve Original Dimensions in Output
```python
current_frame_keypoint_object = { 
    "people": current_image_people_data_for_output, 
    "canvas_width": output_W,    # Uses original input value
    "canvas_height": output_H    # Uses original input value
}
```

## Key Features

### ✅ **Preserves Original Canvas Dimensions**
- Input: `{"canvas_width": 720, "canvas_height": 1280, ...}`
- Output: `{"canvas_width": 720, "canvas_height": 1280, ...}`

### ✅ **Handles Missing Canvas Data**
- Input: `{"people": [...]}` (no canvas info)
- Output: `{"canvas_width": 512, "canvas_height": 768, "people": [...]}`

### ✅ **Robust Processing**
- Uses safe defaults for internal calculations when input data is invalid
- Preserves exact original values (including data types) in output
- Handles edge cases like negative or non-numeric values

## Usage Examples

### Example 1: Preserving Custom Canvas Size
```json
// Input JSON
{
  "canvas_width": 1920,
  "canvas_height": 1080,
  "people": [...]
}

// Output JSON (dimensions preserved)
{
  "canvas_width": 1920,
  "canvas_height": 1080,
  "people": [...]
}
```

### Example 2: Adding Missing Canvas Dimensions
```json
// Input JSON (no canvas info)
{
  "people": [...]
}

// Output JSON (defaults added)
{
  "canvas_width": 512,
  "canvas_height": 768,
  "people": [...]
}
```

## Testing
Created and verified with `test_canvas_preservation.py`:
- ✅ Original canvas dimensions are preserved exactly
- ✅ Default dimensions are used when missing
- ✅ Invalid/malformed dimensions are handled gracefully

## Benefits
1. **No More Unwanted Cropping**: Your 720×1280 poses stay 720×1280
2. **Consistent Input/Output**: What goes in comes out with same canvas size
3. **Backward Compatible**: Still works with JSON that lacks canvas dimensions
4. **Robust**: Handles edge cases and malformed data gracefully

## Before vs After

### Before (Buggy Behavior)
```
Input:  720×1280 canvas → Output: 512×768 canvas (WRONG!)
Result: Pose gets cropped/scaled unexpectedly
```

### After (Fixed Behavior)
```
Input:  720×1280 canvas → Output: 720×1280 canvas (CORRECT!)
Result: Pose maintains exact original canvas dimensions
```

Your OpenPose Editor Node will now correctly preserve the original canvas dimensions when exporting JSON!
