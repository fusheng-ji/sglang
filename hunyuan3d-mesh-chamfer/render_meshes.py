"""CPU-only Blender rendering; preserve imported mesh positions and scales."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

root = Path(sys.argv[sys.argv.index('--') + 1]).resolve()
out = root / 'render'
out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.render.resolution_x = 680
scene.render.resolution_y = 680
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.78, 0.84, 0.91, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3
scene.view_settings.view_transform = 'AgX'

clay = bpy.data.materials.new('Shared neutral clay')
clay.use_nodes = True
bsdf = clay.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (0.065, 0.16, 0.23, 1)
bsdf.inputs['Roughness'].default_value = 0.68

groups = {}
original_materials = {}
for label, filename in [('reference', 'reference.glb'), ('generated', 'generated.glb')]:
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(root / filename))
    objects = list(set(bpy.data.objects) - before)
    groups[label] = objects
    for obj in objects:
        obj.hide_render = True
        if obj.type == 'MESH':
            original_materials[obj.name] = list(obj.data.materials)
            obj.data.materials.clear()
            obj.data.materials.append(clay)
            for polygon in obj.data.polygons:
                polygon.material_index = 0
                polygon.use_smooth = True

bounds = [obj.matrix_world @ Vector(corner) for obj in groups['reference'] if obj.type == 'MESH' for corner in obj.bound_box]
lo = Vector([min(p[i] for p in bounds) for i in range(3)])
hi = Vector([max(p[i] for p in bounds) for i in range(3)])
center = (lo + hi) * 0.5
extent = max(hi - lo)

# Camera uses only the reference frame for every image.
bpy.ops.object.camera_add()
camera = bpy.context.object
camera.data.type = 'ORTHO'
camera.data.ortho_scale = extent * 1.27
camera.data.lens = 50
scene.camera = camera

def aim(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat('-Z', 'Y').to_euler()

for name, relative, power, size in [
    ('Key', (3,-4,5), 450, 4),
    ('Fill', (-4,-1,2), 150, 4),
    ('Rim', (1,4,4), 450, 3),
]:
    bpy.ops.object.light_add(type='AREA', location=center + Vector(relative))
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = 'DISK'
    light.data.size = size
    aim(light, center)

bpy.ops.mesh.primitive_plane_add(size=200, location=(center.x,center.y,lo.z - 0.03))
floor = bpy.context.object
mat = bpy.data.materials.new('Backdrop')
mat.diffuse_color = (0.78,0.83,0.87,1)
floor.data.materials.append(mat)

views = [('front',(0,-1,0.16)),('three_quarter',(1,-1,0.32)),('rear',(0,1,0.16))]
for label, objects in groups.items():
    for obj in objects: obj.hide_render = False
    for view, direction in views:
        camera.location = center + Vector(direction).normalized() * extent * 4
        aim(camera, center)
        scene.render.filepath = str(out / f'{label}_{view}.png')
        bpy.ops.render.render(write_still=True)
    for obj in objects: obj.hide_render = True

for obj in groups['generated']:
    obj.hide_render = False
    if obj.type == 'MESH':
        obj.data.materials.clear()
        for material in original_materials[obj.name]: obj.data.materials.append(material)
camera.location = center + Vector((1,-1,0.32)).normalized() * extent * 4
aim(camera, center)
scene.render.filepath = str(out/'generated_textured.png')
bpy.ops.render.render(write_still=True)
(out/'render-settings.json').write_text(json.dumps({
    'engine':'Blender 4.2.3 Cycles CPU', 'samples':32,
    'reference_bounds_blender_axes':[list(lo),list(hi)],
    'shared_camera_center':list(center), 'orthographic_scale':camera.data.ortho_scale,
    'views':views, 'mesh_transform':'Only GLTF importer coordinate-system conversion; no per-mesh scaling/alignment',
    'material':'Shared neutral clay for comparison; original GLB materials for textured image',
}, indent=2)+'\n')
