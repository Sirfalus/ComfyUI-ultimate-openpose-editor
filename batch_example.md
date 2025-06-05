# OpenPose Batch Loading Example

## Overview

I've added two new nodes to handle batch loading of JSON pose files:

1. **Pose Batch Loader** - Loads JSON files from a folder one by one
2. **Pose Batch Iterator** - Helper node for automatic iteration

## How to Use

### 1. Pose Batch Loader Node

**Inputs:**

- `folder_path` (STRING): Path to folder containing JSON files (e.g., "C:/poses/")
- `file_pattern` (STRING): File pattern to match (default: "\*.json")
- `current_index` (INT): Which file to load (0-based index)
- `sort_files` (BOOLEAN): Whether to sort files alphabetically (default: True)
- `loop_batch` (BOOLEAN): Whether to loop back to start when reaching end (default: False)

**Outputs:**

- `POSE_KEYPOINT`: The loaded pose data (compatible with OpenPose Editor)
- `POSE_JSON`: The pose data as JSON string
- `FILENAME`: Name of the currently loaded file
- `TOTAL_COUNT`: Total number of files found
- `CURRENT_INDEX`: Current file index

### 2. Workflow Example

```
[Pose Batch Loader] → [OpenPose Editor Node] → [Output]
        ↓
[Filename Display]
[Progress Display]
```

### 3. Basic Setup

1. **Add Pose Batch Loader node**

   - Set `folder_path` to your JSON files folder
   - Set `current_index` to 0 to start with first file
   - Enable `sort_files` to process files in alphabetical order

2. **Connect to OpenPose Editor**

   - Connect `POSE_KEYPOINT` output to `POSE_KEYPOINT` input of OpenPose Editor
   - Or connect `POSE_JSON` output to `POSE_JSON` input of OpenPose Editor

3. **Process Files One by One**
   - Increment `current_index` to load next file
   - Use `FILENAME` and `TOTAL_COUNT` outputs to track progress

### 4. Advanced Usage with Iteration

For automatic processing, you can use the **Pose Batch Iterator** node:

```
[Pose Batch Loader] → [Pose Batch Iterator] → [OpenPose Editor] → [Output]
```

The iterator can automatically increment the index for sequential processing.

### 5. Example Folder Structure

```
poses/
├── pose_001.json
├── pose_002.json
├── pose_003.json
└── pose_004.json
```

Set `folder_path` to `poses/` and `file_pattern` to `*.json`

## Features

- **Error Handling**: Gracefully handles missing files, invalid JSON, and folder errors
- **Progress Tracking**: Shows current file and total count
- **Flexible Patterns**: Support for custom file patterns (e.g., "pose\_\*.json")
- **Sorting**: Optional alphabetical sorting of files
- **Looping**: Optional automatic loop back to start
- **Compatibility**: Full compatibility with existing OpenPose Editor node

## Benefits

- Process hundreds of pose files efficiently
- Maintain consistent workflow for batch operations
- Easy integration with existing ComfyUI workflows
- Real-time progress feedback
- Error recovery and debugging support
