#!/usr/bin/env python3
"""
Add specific canvas dimensions to bad_json.json
"""

import json

def add_custom_canvas_dimensions():
    """Add 720x1280 canvas dimensions to bad_json.json"""
    
    # Load the original file
    with open('bad_json.json', 'r') as f:
        data = json.load(f)
    
    # Add canvas dimensions to each frame
    for frame in data:
        # Add canvas dimensions at the beginning of each frame
        frame_with_canvas = {
            'canvas_width': 720,
            'canvas_height': 1280
        }
        # Add the rest of the frame data
        frame_with_canvas.update(frame)
        # Replace the frame in the list
        data[data.index(frame)] = frame_with_canvas
    
    # Save as a new file
    with open('bad_json_720x1280.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print("✅ Created bad_json_720x1280.json with canvas dimensions 720x1280")
    
    # Show the first few lines
    print("\nFirst few lines of the fixed JSON:")
    with open('bad_json_720x1280.json', 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:10]):
            print(f"{i+1:2d}: {line.rstrip()}")

if __name__ == "__main__":
    add_custom_canvas_dimensions()
