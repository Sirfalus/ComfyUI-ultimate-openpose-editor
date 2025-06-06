from .openpose_editor_nodes import OpenposeEditorNode, PoseBatchLoaderNode, PoseBatchIteratorNode, PoseReferenceLoaderNode, PoseSaverNode


WEB_DIRECTORY = "js"

NODE_CLASS_MAPPINGS = {
    "OpenposeEditorNode": OpenposeEditorNode,
    "PoseBatchLoaderNode": PoseBatchLoaderNode,
    "PoseBatchIteratorNode": PoseBatchIteratorNode,
    "PoseReferenceLoaderNode": PoseReferenceLoaderNode,
    "PoseSaverNode": PoseSaverNode,  # Added PoseSaverNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OpenposeEditorNode": "Openpose Editor Node",
    "PoseBatchLoaderNode": "Pose Batch Loader",
    "PoseBatchIteratorNode": "Pose Batch Iterator",
    "PoseReferenceLoaderNode": "Pose Reference Loader",
    "PoseSaverNode": "Pose Saver",  # Added PoseSaverNode
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
