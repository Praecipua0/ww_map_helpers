# This script tries to match the visuals of material preview on blender to what you could expect to see ingame
# The script will modify all materials so that you can see texture transparency and vertex colour for each mesh
# The calibration is done by eye, so there might be minor differences between what you see in blender, compared to ingame

#For any help and questions, I can be contacted by discord: Praecipua#1831 or on twitter: @PraecipuaWW


import bpy

# Set display device to "sRGB"
bpy.context.scene.display_settings.display_device = 'sRGB'
# Set view transform to "Raw"
bpy.context.scene.view_settings.view_transform = 'Raw'
# Set look to "None"
bpy.context.scene.view_settings.look = 'None'
# Set exposure to 0.0
bpy.context.scene.view_settings.exposure = 0.0
# Set gamma to 2.2
bpy.context.scene.view_settings.gamma = 2.2
# Set sequencer to "Linear"
bpy.context.scene.sequencer_colorspace_settings.name = 'Linear'
# Disable curves
bpy.context.scene.view_settings.use_curve_mapping = False

# Get the 3D view
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        # Set viewport shading to "Material Preview"
        area.spaces[0].shading.type = 'MATERIAL'
        # Enable scene lights and scene world in lighting
        area.spaces[0].shading.use_scene_lights = True
        area.spaces[0].shading.use_scene_world = True
        # Set clip start distance to 100m
        area.spaces[0].clip_start = 100.0
        # Set clip end distance to 1000000m
        area.spaces[0].clip_end = 1000000.0
        
# Get the world node tree
world_node_tree = bpy.context.scene.world.node_tree

# Get the background node
background_node = world_node_tree.nodes.get("Background")

# Set the color of the background node to black
background_node.inputs[0].default_value = (0, 0, 0, 1)

# Iterate over all meshes in the scene
for mesh in bpy.context.scene.objects:
    if mesh.type == 'MESH':
        # Get the material of the mesh
        mat = mesh.active_material
        
        # Set blend mode to "Alpha Clip"
        mat.blend_method = 'CLIP'
        # Set "Clip Treshold" to 0.1
        mat.alpha_threshold = 0.1

        # Check if the "Image Texture" node exists in the node tree
        image_tex_node_exists = False
        for node in mat.node_tree.nodes:
            if node.name == "Image Texture":
                image_tex_node_exists = True
                break

        if not image_tex_node_exists:
            # Skip the mesh if the "Image Texture" node does not exist
            continue

        # Create a vertex color node
        vert_col_node = mat.node_tree.nodes.new(type='ShaderNodeVertexColor')
        vert_col_node.layer_name = mesh.data.vertex_colors.keys()[0]  # Use first vertex color layer in the list
        vert_col_node.mute = False

        # Create a mix RGB node
        mix_rgb_node = mat.node_tree.nodes.new(type='ShaderNodeMixRGB')
        mix_rgb_node.blend_type = 'MULTIPLY'  # Set blend type to "Multiply"
        mix_rgb_node.use_clamp = True  # Enable clamp
        mix_rgb_node.inputs[0].default_value = 1.0  # Set "Factor" to 1.0

        # Connect nodes
        mat.node_tree.links.new(mat.node_tree.nodes['Image Texture'].outputs[0], mix_rgb_node.inputs[1])
        mat.node_tree.links.new(mat.node_tree.nodes['Image Texture'].outputs[1], mat.node_tree.nodes['Principled BSDF'].inputs['Alpha'])
        mat.node_tree.links.new(vert_col_node.outputs[0], mix_rgb_node.inputs[2])
        mat.node_tree.links.new(mix_rgb_node.outputs[0], mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
        mat.node_tree.links.new(mix_rgb_node.outputs[0], mat.node_tree.nodes['Principled BSDF'].inputs['Emission'])

        # Set specular, roughness, and sheen tint to 0.0
        mat.node_tree.nodes['Principled BSDF'].inputs['Specular'].default_value = 0.0
        mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.0
        mat.node_tree.nodes['Principled BSDF'].inputs['Sheen Tint'].default_value = 0.0