import bpy

# --- Set Blender units to millimeters ---
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001
scene.unit_settings.use_separate = False

# Remove all existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_true_tslot_profile(name, length, orientation='X', location=(0,0,0)):
    width = 30
    height = 30
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.name = name

    if orientation == 'X':
        obj.scale = (length, width, height)
    elif orientation == 'Y':
        obj.scale = (width, length, height)
    else:
        raise ValueError("Orientation must be 'X' or 'Y'")

    obj.location = location
    return obj

class Part:
    def __init__(self, part_type, name):
        self.part_type = part_type
        self.name = name

    def build_geometry(self, location=(0, 0, 0)):
        raise NotImplementedError

    def create(self, location=(0, 0, 0)):
        return self.build_geometry(location)

class TSlotProfile(Part):
    def __init__(self, part_type, name, length, orientation='X'):
        super().__init__(part_type, name)
        self.length = length
        self.orientation = orientation

    def build_geometry(self, location=(0, 0, 0)):
        return create_true_tslot_profile(self.name, self.length, orientation=self.orientation, location=location)

class AluProfile3030(TSlotProfile):
    def __init__(self, name, length, orientation='X'):
        super().__init__("AluProfile3030", name, length, orientation)

class Assembly:
    def __init__(self, name):
        self.name = name
        self.parts = []

    def add_part(self, part, location=(0, 0, 0)):
        self.parts.append((part, location))

    def build(self):
        for part, loc in self.parts:
            part.create(location=loc)

class FrameAssembly(Assembly):
    def __init__(self, name, width, length):
        super().__init__(name)
        self.width = width
        self.length = length
        self.build_frame_parts()

    def build_frame_parts(self):
        x_beam_length = self.width
        y_beam_length = self.length
        profile_width = 30
        x_corner_extend = 60

        rear_rail = AluProfile3030("Frame_Rear_Rail", x_beam_length, orientation='X')
        front_rail = AluProfile3030("Frame_Front_Rail", x_beam_length, orientation='X')
        left_rail = AluProfile3030("Frame_Left_Side", y_beam_length, orientation='Y')
        right_rail = AluProfile3030("Frame_Right_Side", y_beam_length, orientation='Y')
        mid_rail = AluProfile3030("Frame_Mid_Cross_Top", y_beam_length, orientation='Y')

        self.add_part(front_rail, location=(0, ((y_beam_length + profile_width) / 2), 0))
        self.add_part(rear_rail, location=(0, -((y_beam_length + profile_width)/ 2), 0))
        self.add_part(left_rail, location=(-(self.width - x_corner_extend)/ 2, 0, 0))
        self.add_part(right_rail, location=((self.width - x_corner_extend)/ 2, 0, 0))
        self.add_part(mid_rail, location=(0, 0, 0))

# Create and build frame assembly
frame = FrameAssembly("Base_Frame", width=700, length=1000)
frame.build()

print("CNC frame created using FrameAssembly class with correct joined corners and matching your drawing structure.")



# https://blender.stackexchange.com/questions/38611/setting-camera-clip-end-via-python

for a in bpy.context.screen.areas:
    if a.type == 'VIEW_3D':
        for s in a.spaces:
            if s.type == 'VIEW_3D':
                s.clip_end = 1300
                
                