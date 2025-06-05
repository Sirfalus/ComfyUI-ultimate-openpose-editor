from .openpose_editor_nodes import OpenposeEditorNode, PoseBatchLoaderNode, PoseBatchIteratorNode


WEB_DIRECTORY = "js"

NODE_CLASS_MAPPINGS = {
    "OpenposeEditorNode": OpenposeEditorNode,
    "PoseBatchLoaderNode": PoseBatchLoaderNode,
    "PoseBatchIteratorNode": PoseBatchIteratorNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenposeEditorNode": "Openpose Editor Node",
    "PoseBatchLoaderNode": "Pose Batch Loader",
    "PoseBatchIteratorNode": "Pose Batch Iterator",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
