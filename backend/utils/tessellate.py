from ocp_tessellate.convert import to_ocpgroup, tessellate_group

def tessellate_cad_objects(
    *cad_objs, names=None, colors=None, alphas=None, progress=None, **kwargs
):
    """
    Tessellates CAD objects using ocp-tessellate v3.0.16.
    This version uses the to_ocpgroup function (not to_ocp_group).
    """
    # Create an OcpGroup from the CAD objects using the correct function name.
    group, instances = to_ocpgroup(
        *cad_objs,
        names=names,
        colors=colors,
        alphas=alphas,
        progress=progress,
        **kwargs,
    )

    # Perform the tessellation using tessellate_group with correct parameter order
    # The function returns 3 values: meshed_instances, shapes, mapping
    meshed_instances, shapes, mapping = tessellate_group(group, instances, progress=progress)
    
    # Process shapes to include actual mesh data instead of references
    def resolve_shape_references(shapes_data, meshed_instances):
        """递归地解析shapes中的引用，将ref替换为实际的几何数据"""
        if isinstance(shapes_data, dict):
            result = shapes_data.copy()
            
            # 处理parts列表
            if 'parts' in result and isinstance(result['parts'], list):
                resolved_parts = []
                for part in result['parts']:
                    resolved_part = resolve_shape_references(part, meshed_instances)
                    resolved_parts.append(resolved_part)
                result['parts'] = resolved_parts
            
            # 如果这是一个shape对象且有ref，替换为实际数据
            if 'shape' in result and isinstance(result['shape'], dict) and 'ref' in result['shape']:
                ref_index = result['shape']['ref']
                if 0 <= ref_index < len(meshed_instances):
                    # 将引用替换为实际的几何数据
                    mesh_data = meshed_instances[ref_index]
                    result['shape'] = {
                        'vertices': mesh_data.get('vertices', []),
                        'triangles': mesh_data.get('triangles', []),
                        'normals': mesh_data.get('normals', []),
                        'edges': mesh_data.get('edges', []),
                        'face_types': mesh_data.get('face_types', []),
                        'edge_types': mesh_data.get('edge_types', []),
                    }
            
            return result
        elif isinstance(shapes_data, list):
            return [resolve_shape_references(item, meshed_instances) for item in shapes_data]
        else:
            return shapes_data
    
    # 解析shapes中的引用
    resolved_shapes = resolve_shape_references(shapes, meshed_instances)
    
    # Return the correct data structure that the frontend expects
    # The frontend expects shapes and the actual mesh data
    return (resolved_shapes, meshed_instances), mapping 