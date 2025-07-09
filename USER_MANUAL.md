# Shoulder Width Fix - User Manual

## Overview

The shoulder width fix addresses the problem where poses rotated at angles (especially side poses) maintain unrealistic shoulder widths, making characters appear "overstretched." This update provides automatic detection and manual correction options.

## New Controls

### Auto Perspective (Boolean)

- **Default**: True (Enabled)
- **Purpose**: Automatically detects body rotation and adjusts shoulder width
- **When to disable**: When you want manual control or the automatic detection isn't working well for your specific pose

### Perspective Correction (Float: 0.1-1.0)

- **Default**: 1.0 (No correction)
- **Purpose**: Manual control over shoulder width reduction
- **Only active when**: Auto Perspective is disabled
- **Values**:
  - `1.0` = Frontal view (no width reduction)
  - `0.7` = Slight rotation (30% width reduction)
  - `0.5` = Moderate rotation (50% width reduction)
  - `0.3` = Side view (70% width reduction)
  - `0.1` = Extreme profile (90% width reduction)

## How It Works

### Automatic Mode (Recommended)

1. Enable `auto_perspective = True`
2. The algorithm analyzes the pose using:
   - Shoulder angle (horizontal vs vertical alignment)
   - Y-coordinate differences between shoulders
   - Body symmetry patterns
3. Calculates appropriate width reduction (0.3-1.0 factor)
4. Applies correction automatically

### Manual Mode (Advanced Users)

1. Disable `auto_perspective = False`
2. Adjust `perspective_correction` slider based on pose rotation:
   - Study your pose visually
   - Estimate rotation level (frontal, slight, moderate, side, profile)
   - Set appropriate correction value
   - Fine-tune until shoulders look natural

## Best Practices

### When to Use Automatic Mode

- ✅ Most general use cases
- ✅ Batch processing multiple poses
- ✅ When you're not sure about rotation angles
- ✅ For consistent results across workflows

### When to Use Manual Mode

- ✅ Fine-tuning specific problematic poses
- ✅ When automatic detection seems off
- ✅ For artistic control over proportions
- ✅ When working with unusual or extreme poses

### Tips for Best Results

1. **Test both modes** on your specific poses to see which works better
2. **Start with automatic** - it handles most cases well
3. **Use manual for edge cases** where automatic doesn't look right
4. **Remember the reference values**:
   - Frontal: 1.0
   - Slight angle: 0.8-0.9
   - Side view: 0.3-0.5
   - Profile: 0.1-0.3

## Common Scenarios

### Problem: Character looks too wide in side pose

- **Solution**: Enable auto_perspective or set perspective_correction to 0.3-0.5

### Problem: Frontal pose shoulders look too narrow

- **Solution**: Disable auto_perspective and set perspective_correction to 1.0

### Problem: Automatic detection not working well

- **Solution**: Switch to manual mode and adjust perspective_correction based on visual assessment

### Problem: Inconsistent results across similar poses

- **Solution**: Use manual mode with consistent perspective_correction values

## Compatibility

- Works with all existing pose JSON formats
- Backwards compatible - existing workflows will use automatic mode by default
- No changes needed to existing pose data
- Integrates seamlessly with all other scaling parameters

## Technical Details

The fix works by:

1. Analyzing 2D shoulder positions to infer 3D body rotation
2. Calculating perspective foreshortening effects
3. Applying mathematically-derived width corrections
4. Preserving all other pose proportions and relationships

This provides more realistic pose adaptations that account for viewing angles and body rotation, particularly important when transferring poses between different character body types.
