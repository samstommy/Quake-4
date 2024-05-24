import zipfile
import os
import bpy

# Base path and .pk4 files
base_path = "/Q4/q4base/"
pk4_files = [
    "pak010.pk4", "pak011.pk4", "pak012.pk4",
    "pak013.pk4", "pak014.pk4", "pak016.pk4", "pak019.pk4"
]

# Preferred file type
preferred_extension = ".tga"

def search_in_base_path(base_path, search_path):
    full_path = os.path.join(base_path, search_path)
    if os.path.exists(full_path):
        print(f"Found in base path: {full_path}")
        return [full_path]
    return None

def search_in_pk4_files(pk4_files, search_path):
    matches = []
    for pk4_file in pk4_files:
        with zipfile.ZipFile(pk4_file, 'r') as pk4:
            file_list = pk4.namelist()
            matches.extend([file for file in file_list if file.startswith(search_path)])
            if matches:
                print(f"Found matches in {pk4_file}:")
                for match in matches:
                    print(match)
                # Check preferred file type
                preferred_file = next((file for file in matches if file.endswith(preferred_extension)), None)
                if preferred_file:
                    print(f"Preferred file found: {preferred_file}")
                    extract_and_import_texture(pk4, preferred_file, search_path)
                return matches
    return matches

def extract_and_import_texture(pk4, file_path, material_name):
    temp_dir = bpy.app.tempdir
    temp_file_path = os.path.join(temp_dir, os.path.basename(file_path))
    with pk4.open(file_path) as source, open(temp_file_path, 'wb') as target:
        target.write(source.read())
    
    # Import
    if temp_file_path.endswith(".tga") or temp_file_path.endswith(".dds"):
        img = bpy.data.images.load(temp_file_path)
        print(f"Imported texture: {img.name}")
        
        # Apply
        material = bpy.data.materials.get(material_name)
        if material:
            apply_texture_to_material(material, img)
    else:
        print(f"File type of {temp_file_path} is not supported for import into Blender.")

def apply_texture_to_material(material, texture):
    # Enable 'Use Nodes' for the material
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get('Principled BSDF')
    
    if not bsdf:
        bsdf = material.node_tree.nodes.new('ShaderNodeBsdfPrincipled')

    # Create a new texture node
    tex_image = material.node_tree.nodes.new('ShaderNodeTexImage')
    tex_image.image = texture

    # Link the texture node to the BSDF node
    material.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])

def main():
    # Seach all materials
    for material in bpy.data.materials:
        if material.name.startswith("textures"):
            search_path = material.name
            print(f"Searching for material: {search_path}")
            
            # Check first the base path
            result = search_in_base_path(base_path, search_path)
            
            # If not found using .pk4 files instead
            if not result:
                pk4_paths = [os.path.join(base_path, pk4) for pk4 in pk4_files]
                result = search_in_pk4_files(pk4_paths, search_path)
    
    print("Search and application process completed.")

# Run the main function
main()
