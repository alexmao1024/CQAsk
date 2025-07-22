"""
JSON序列化工具
处理CAD对象和NumPy数组的JSON序列化
"""

import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        
        # Handle CAD objects that can't be serialized
        if hasattr(obj, '__class__'):
            class_name = str(type(obj))
            if any(x in class_name for x in ['TopLoc_Location', 'TopoDS_', 'gp_', 'Geom_', 'BRep_']):
                # Convert CAD objects to a serializable format or skip them
                print(f"Warning: Skipping non-serializable CAD object: {class_name}")
                return None
        
        # Try to convert to dict if object has __dict__
        if hasattr(obj, '__dict__'):
            try:
                return obj.__dict__
            except:
                print(f"Warning: Could not serialize object with __dict__: {type(obj)}")
                return None
        
        # For other objects, try to convert to string representation
        try:
            return str(obj)
        except:
            print(f"Warning: Could not serialize object: {type(obj)}")
            return None 