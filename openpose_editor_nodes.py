import json
import torch
import numpy as np
import os
import glob
from .util import draw_pose_json, draw_pose

OpenposeJSON = dict

class OpenposeEditorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "show_body": ("BOOLEAN", {"default": True}),
                "show_face": ("BOOLEAN", {"default": True}),
                "show_hands": ("BOOLEAN", {"default": True}),
                "resolution_x": ("INT", {"default": -1, "min": -1, "max": 12800}),
                "use_ground_plane": ("BOOLEAN", {"default": True}),
                "pose_marker_size": ("INT", { "default": 4, "min": 0, "max": 100 }),
                "face_marker_size": ("INT", { "default": 3, "min": 0, "max": 100 }),
                "hand_marker_size": ("INT", { "default": 2, "min": 0, "max": 100 }),
                "pelvis_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01 }),
                "torso_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01 }),
                "neck_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01 }),
                # --- 머리 및 눈 관련 스케일 ---
                "head_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 5.0, "step": 0.01 }),
                "eye_distance_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 5.0, "step": 0.01 }),
                "eye_height": ("FLOAT", { "default": 0.0, "min": -100.0, "max": 100.0, "step": 0.1 }),
                "eyebrow_height": ("FLOAT", { "default": 0.0, "min": -100.0, "max": 100.0, "step": 0.1 }), # 눈썹 높이 조절
                "left_eye_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 5.0, "step": 0.01 }),
                "right_eye_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 5.0, "step": 0.01 }),
                "left_eyebrow_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 5.0, "step": 0.01 }),
                "right_eyebrow_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 5.0, "step": 0.01 }),
                "mouth_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 5.0, "step": 0.01 }),
                "nose_scale_face": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 5.0, "step": 0.01 }),
                "face_shape_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 5.0, "step": 0.01 }),
                # ---
                "shoulder_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01 }),
                "arm_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01 }),
                "leg_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01 }),
                "hands_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01 }),
                "overall_scale": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 10.0, "step": 0.01 }),
                "POSE_JSON": ("STRING", {"multiline": True}),
                "POSE_KEYPOINT": ("POSE_KEYPOINT",{"default": None}),
                "Target_pose_keypoint": ("POSE_KEYPOINT", {"default": None}),
            },
        }

    RETURN_NAMES = ("POSE_IMAGE", "POSE_KEYPOINT", "POSE_JSON")
    RETURN_TYPES = ("IMAGE", "POSE_KEYPOINT", "STRING")
    OUTPUT_NODE = True
    FUNCTION = "load_pose"
    CATEGORY = "ultimate-openpose"

    def load_pose(self, show_body, show_face, show_hands, resolution_x, use_ground_plane,
                  pose_marker_size, face_marker_size, hand_marker_size,
                  pelvis_scale, torso_scale, neck_scale, head_scale, eye_distance_scale, eye_height, eyebrow_height,
                  left_eye_scale, right_eye_scale, left_eyebrow_scale, right_eyebrow_scale,
                  mouth_scale, nose_scale_face, face_shape_scale,
                  shoulder_scale, arm_scale, leg_scale, hands_scale, overall_scale,
                  POSE_JSON: str, POSE_KEYPOINT=None, Target_pose_keypoint=None) -> tuple[OpenposeJSON]:
        
        # 내부 함수인 process_pose에 Target_pose_keypoint를 전달하도록 수정
        def process_pose(pose_input_str_list, target_pose_obj=None):
            pose_imgs, final_keypoints_batch = draw_pose_json(
                pose_input_str_list, resolution_x, use_ground_plane, show_body, show_face, show_hands,
                pose_marker_size, face_marker_size, hand_marker_size,
                pelvis_scale, torso_scale, neck_scale, head_scale, eye_distance_scale, eye_height, eyebrow_height,
                left_eye_scale, right_eye_scale, left_eyebrow_scale, right_eyebrow_scale,
                mouth_scale, nose_scale_face, face_shape_scale,
                shoulder_scale, arm_scale, leg_scale, hands_scale, overall_scale,
                target_pose_keypoint_obj=target_pose_obj # util.py 함수로 Target_pose_keypoint 전달
            )
            
            if not pose_imgs: return None, None, None
            
            pose_imgs_np = np.array(pose_imgs).astype(np.float32) / 255
            final_json_str = json.dumps(final_keypoints_batch, indent=4)
            return torch.from_numpy(pose_imgs_np), final_keypoints_batch, final_json_str

        input_json_str = ""
        # 팔 길이 비교를 위해 POSE_KEYPOINT가 우선순위를 갖도록 순서 조정
        if POSE_KEYPOINT is not None:
            normalized_json_data = json.dumps(POSE_KEYPOINT, indent=4).replace("'",'"').replace('None','[]')
            if not isinstance(POSE_KEYPOINT, list):
                input_json_str = f'[{normalized_json_data}]'
            else:
                input_json_str = normalized_json_data
        elif POSE_JSON: 
            temp_json = POSE_JSON.replace("'",'"').replace('None','[]')
            try:
                parsed_json = json.loads(temp_json)
                input_json_str = f"[{temp_json}]" if not isinstance(parsed_json, list) else temp_json
            except json.JSONDecodeError: input_json_str = f"[{temp_json}]"
        
        if input_json_str:
            # Ensure canvas dimensions are present in the JSON data
            try:
                parsed_data = json.loads(input_json_str)
                if isinstance(parsed_data, list):
                    for item in parsed_data:
                        if isinstance(item, dict):
                            if 'canvas_width' not in item:
                                item['canvas_width'] = 512
                            if 'canvas_height' not in item:
                                item['canvas_height'] = 768
                else:
                    if isinstance(parsed_data, dict):
                        if 'canvas_width' not in parsed_data:
                            parsed_data['canvas_width'] = 512
                        if 'canvas_height' not in parsed_data:
                            parsed_data['canvas_height'] = 768
                        parsed_data = [parsed_data]
                input_json_str = json.dumps(parsed_data)
            except json.JSONDecodeError:
                # If parsing fails, just continue with original string
                pass
            
            # process_pose 호출 시 Target_pose_keypoint 객체를 인자로 전달
            image_tensor, keypoint_obj_batch, json_str_batch = process_pose(input_json_str, Target_pose_keypoint)
            if image_tensor is not None:
                return { "ui": {"POSE_JSON": [json_str_batch]}, "result": (image_tensor, keypoint_obj_batch, json_str_batch) }

        W, H = 512, 768
        blank_person = dict(pose_keypoints_2d=[], face_keypoints_2d=[], hand_left_keypoints_2d=[], hand_right_keypoints_2d=[])
        blank_output_keypoints = [{"people": [blank_person], "canvas_width": W, "canvas_height": H}]
        W_scaled = resolution_x if resolution_x >= 64 else W
        H_scaled = int(H*(W_scaled*1.0/W))
        blank_pose_for_draw = {"people": [blank_person]}
        pose_img = [draw_pose(blank_pose_for_draw, H_scaled, W_scaled, pose_marker_size, face_marker_size, hand_marker_size)]
        pose_img_np = np.array(pose_img).astype(np.float32) / 255
        return { "ui": {"POSE_JSON": [json.dumps(blank_output_keypoints)]}, "result": (torch.from_numpy(pose_img_np), blank_output_keypoints, json.dumps(blank_output_keypoints)) }


class PoseBatchLoaderNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "", "multiline": False}),
                "file_pattern": ("STRING", {"default": "*.json", "multiline": False}),
                "current_index": ("INT", {"default": 0, "min": 0, "max": 10000}),
            },
            "optional": {
                "sort_files": ("BOOLEAN", {"default": True}),
                "loop_batch": ("BOOLEAN", {"default": False}),
            }
        }
    
    RETURN_NAMES = ("POSE_KEYPOINT", "POSE_JSON", "FILENAME", "TOTAL_COUNT", "CURRENT_INDEX")
    RETURN_TYPES = ("POSE_KEYPOINT", "STRING", "STRING", "INT", "INT")
    FUNCTION = "load_batch_pose"
    CATEGORY = "ultimate-openpose"

    def load_batch_pose(self, folder_path, file_pattern, current_index, sort_files=True, loop_batch=False):
        """
        Load pose JSON files from a folder and return them one by one based on current_index.
        """
        try:
            # Validate folder path
            if not folder_path or not os.path.exists(folder_path):
                print(f"Error: Folder path '{folder_path}' does not exist")
                return (None, "{}", "No files found", 0, 0)
            
            # Get all JSON files matching the pattern
            search_pattern = os.path.join(folder_path, file_pattern)
            json_files = glob.glob(search_pattern)
            
            if not json_files:
                print(f"No files found matching pattern: {search_pattern}")
                return (None, "{}", "No files found", 0, 0)
            
            # Sort files if requested
            if sort_files:
                json_files.sort()
            
            total_files = len(json_files)
            
            # Handle looping
            if loop_batch and total_files > 0:
                current_index = current_index % total_files
            elif current_index >= total_files:
                current_index = max(0, total_files - 1)
            
            # Load the current file
            current_file = json_files[current_index]
            filename = os.path.basename(current_file)
            
            try:
                with open(current_file, 'r', encoding='utf-8') as f:
                    pose_data = json.load(f)
                
                # Convert to string for POSE_JSON output
                pose_json_str = json.dumps(pose_data, indent=2)
                
                print(f"Loaded pose file: {filename} ({current_index + 1}/{total_files})")
                
                return (pose_data, pose_json_str, filename, total_files, current_index)
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON file {filename}: {e}")
                return (None, "{}", f"Error parsing {filename}", total_files, current_index)
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
                return (None, "{}", f"Error reading {filename}", total_files, current_index)
                
        except Exception as e:
            print(f"Error in load_batch_pose: {e}")
            return (None, "{}", "Error", 0, 0)


class PoseBatchIteratorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "batch_loader_output": ("POSE_KEYPOINT", {}),
                "auto_increment": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "manual_index": ("INT", {"default": -1, "min": -1, "max": 10000}),
            }
        }
    
    RETURN_NAMES = ("POSE_KEYPOINT", "NEXT_INDEX")
    RETURN_TYPES = ("POSE_KEYPOINT", "INT")
    FUNCTION = "iterate_batch"
    CATEGORY = "ultimate-openpose"

    def __init__(self):
        self.current_index = 0

    def iterate_batch(self, batch_loader_output, auto_increment, manual_index=-1):
        """
        Helper node to iterate through batch poses with automatic or manual indexing.
        """
        if manual_index >= 0:
            self.current_index = manual_index
        elif auto_increment:
            self.current_index += 1
        
        next_index = self.current_index + 1 if auto_increment else self.current_index
        return (batch_loader_output, next_index)


class PoseReferenceLoaderNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_file_path": ("STRING", {"default": "", "multiline": False}),
            },
        }
    
    RETURN_NAMES = ("POSE_KEYPOINT",)
    RETURN_TYPES = ("POSE_KEYPOINT",)
    FUNCTION = "load_reference_pose"
    CATEGORY = "ultimate-openpose"

    def load_reference_pose(self, json_file_path):
        """
        Load a single JSON pose file for use as Target_pose_keypoint reference.
        """
        try:
            # Validate file path
            if not json_file_path or not os.path.exists(json_file_path):
                print(f"Error: File path '{json_file_path}' does not exist")
                return (None,)
            
            # Check if it's a JSON file
            if not json_file_path.lower().endswith('.json'):
                print(f"Error: File '{json_file_path}' is not a JSON file")
                return (None,)
            
            filename = os.path.basename(json_file_path)
            
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    pose_data = json.load(f)
                
                print(f"Loaded reference pose: {filename}")
                return (pose_data,)
                
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON file {filename}: {e}")
                return (None,)
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
                return (None,)
                
        except Exception as e:
            print(f"Error in load_reference_pose: {e}")
            return (None,)


class PoseSaverNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "pose_keypoint": ("POSE_KEYPOINT", {}),
                "target_folder": ("STRING", {"default": "./output_poses", "multiline": False}),
                "filename": ("STRING", {"default": "saved_pose.json", "multiline": False}), 
            },
            "optional": {
                "filename_prefix": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("SAVED_FILE_PATH",)
    FUNCTION = "save_pose_keypoint"
    CATEGORY = "ultimate-openpose"
    OUTPUT_NODE = True

    def save_pose_keypoint(self, pose_keypoint, target_folder, filename, filename_prefix=""):
        if pose_keypoint is None:
            print("PoseSaverNode: No pose_keypoint data to save.")
            return ("",) 

        if not target_folder:
            print("PoseSaverNode: Target folder not specified. Please provide a valid folder path.")
            # Fallback to a default if somehow empty, though ComfyUI usually provides the default from INPUT_TYPES
            target_folder = "./output_poses_fallback"
        
        if not filename:
            print("PoseSaverNode: Filename not specified. Please provide a valid filename.")
            # Fallback, though ComfyUI provides default
            filename = "default_saved_pose.json"

        try:
            os.makedirs(target_folder, exist_ok=True)

            base_name_from_input, _ = os.path.splitext(filename)
            
            prefix = filename_prefix if filename_prefix is not None else ""

            final_filename = f"{prefix}{base_name_from_input}.json"
            
            file_path = os.path.join(target_folder, final_filename)

            # Ensure canvas dimensions are present before saving
            processed_pose_keypoint = self._ensure_canvas_dimensions(pose_keypoint)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(processed_pose_keypoint, f, indent=4) 

            print(f"PoseSaverNode: Saved pose to {file_path}")
            return (file_path,)

        except Exception as e:
            print(f"PoseSaverNode: Error saving pose - {e}")
            return ("",)
    
    def _ensure_canvas_dimensions(self, pose_keypoint):
        """Ensure canvas dimensions are present in the pose data"""
        if pose_keypoint is None:
            return None
        
        # Make a deep copy to avoid modifying the original
        import copy
        processed_data = copy.deepcopy(pose_keypoint)
        
        # Handle different data structures
        if isinstance(processed_data, list):
            # List of pose objects
            for item in processed_data:
                if isinstance(item, dict):
                    if 'canvas_width' not in item:
                        item['canvas_width'] = 512
                    if 'canvas_height' not in item:
                        item['canvas_height'] = 768
        elif isinstance(processed_data, dict):
            # Single pose object
            if 'canvas_width' not in processed_data:
                processed_data['canvas_width'] = 512
            if 'canvas_height' not in processed_data:
                processed_data['canvas_height'] = 768
        
        return processed_data


# Add the new nodes to the node class mappings
NODE_CLASS_MAPPINGS = {
    "OpenposeEditorNode": OpenposeEditorNode,
    "PoseBatchLoaderNode": PoseBatchLoaderNode,
    "PoseBatchIteratorNode": PoseBatchIteratorNode,
    "PoseReferenceLoaderNode": PoseReferenceLoaderNode,
    "PoseSaverNode": PoseSaverNode, # Added new node
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenposeEditorNode": "OpenPose Editor",
    "PoseBatchLoaderNode": "Pose Batch Loader",
    "PoseBatchIteratorNode": "Pose Batch Iterator",
    "PoseReferenceLoaderNode": "Pose Reference Loader",
    "PoseSaverNode": "Pose Saver", # Added new node display name
}
