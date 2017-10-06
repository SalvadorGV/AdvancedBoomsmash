# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Blender Playblast",
    "author": "Luciano Muñoz & Cristian Hasbun & Salvador Garcia",
    "version": (0, 13),
    "blender": (2, 79, 0),
    "location": "View3D > Toolshelf > Playblast",
    "description": "Preview animation by screen-capturing frames",
    "warning": "The addon still in progress! Be careful!",
    "category": "Render"}

import os.path

import bpy
from bpy.props import *

#DEBUGGER
#import pudb
#_MODULE_SOURCE_CODE = bpy.data.texts[__file__.split('/')[-1]].as_string()
#_MODULE_SOURCE_CODE = bpy.data.texts[os.path.basename(__file__)].as_string()


class BoomProps(bpy.types.PropertyGroup):

    global_toggle = BoolProperty(
        name = 'Global',
        description = 'Same Playblast settings for all scenes in file.',
        default = False)

    #twm.image_settings = bpy.types.ImageFormatSettings(
    #                        bpy.context.scene.render.image_settings)

    scene_cam = BoolProperty(
        name = 'Active Camera',
        description = 'Always renders from the active camera that\'s set in the Scene properties')

    incremental = BoolProperty(
        name = 'Incremental',
        description = 'Save incremental Playblast.',
        default = False)

    use_stamp = BoolProperty(
        name = 'Stamp',
        description = 'Turn on stamp (uses settings from render properties).',
        default = False)

    transparent = BoolProperty(
        name = 'Transparent',
        description = 'Make background transparent (only for formats that support alpha, i.e.: .png).',
        default = False)

    autoplay = BoolProperty(
        name = 'Autoplay',
        description = 'Autoplay after making it.',
        default = True)

    unsimplify = BoolProperty(
        name = 'Simplify Off',
        description = "Playblast with the Subsurf level at it's render settings.",
        default = False)

    onlyrender = BoolProperty(
        name = 'Only Render',
        description = 'Only have renderable objects visible during Playblast.',
        default = False)

    frame_skip = IntProperty(
        name = 'Skip Frames',
        description = 'Number of frames to skip',
        default = 0,
        min = 0)

    resolution_percentage = IntProperty(
        subtype = "PERCENTAGE",
        name = '',
        description = 'Porcentage scale for render resolution playblast',
        default = 50,
        min = 0,
        max = 100)

    #DEBUG
    #pu.db

    dirname = StringProperty(
        name = '',
        description = 'Folder where your Playblast will be stored',
        #default = bpy.app.tempdir,
        default = '/tmp/',
        subtype = 'DIR_PATH')

    filename = StringProperty(
        subtype = 'FILE_NAME',
        name = '',
        description = 'Filename where your Playblast will be stored',
        default = 'playblast_')


class setDirname(bpy.types.Operator):
    bl_idname = 'bs.setdirname'
    bl_label = 'PlayblastDirname'
    bl_description = 'Use blend file directory'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        cs = context.scene
        #cs.boom_props.dirname = os.path.dirname(bpy.data.filepath)
        file_path = os.path.dirname(bpy.data.filepath)
        cs.boom_props.dirname = file_path + '/'
        return {'FINISHED'}


class setFilename(bpy.types.Operator):
    bl_idname = 'bs.setfilename'
    bl_label = 'PlayblastFilename'
    bl_description = 'Rename to: file name _ scene name _'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        cs = context.scene
        blend_name = os.path.basename(
                      os.path.splitext(bpy.data.filepath)[0])
        cs.boom_props.filename = blend_name + '_' + bpy.context.scene.name + '_'
        return {'FINISHED'}


class DoBoom(bpy.types.Operator):
    bl_idname = 'bs.doboom'
    bl_label = 'Playblast'
    bl_description = 'Preview animation by screen-capturing frames'
    bl_options = {'REGISTER'}

    def execute(self, context):
        cs = context.scene
        wm = context.window_manager
        rd = context.scene.render
        sd = context.space_data

        if wm.boom_props.global_toggle:
            boom_props = wm.boom_props
        else:
            boom_props = cs.boom_props

        #pu.db

        #guardo settings
        old_use_stamp = rd.use_stamp
        old_onlyrender = sd.show_only_render
        old_simplify = rd.use_simplify
        old_filepath = rd.filepath
        old_alpha_mode = rd.alpha_mode
        #old_image_settings = rd.image_settings
        old_resolution_percentage = rd.resolution_percentage
        old_frame_step = cs.frame_step

        #afecto settings originales
        rd.use_stamp = boom_props.use_stamp
        sd.show_only_render = boom_props.onlyrender
        if boom_props.unsimplify:
            rd.use_simplify = False
        rd.filepath = cs.boom_props.dirname + cs.boom_props.filename
        rd.alpha_mode = 'TRANSPARENT' if boom_props.transparent else 'SKY'

        #rd.image_settings = boom_props.image_settings
        rd.resolution_percentage = boom_props.resolution_percentage
        cs.frame_step = boom_props.frame_skip + 1
        view_pers = context.area.spaces[0].region_3d.view_perspective
        if boom_props.scene_cam and view_pers is not 'CAMERA':
            context.area.spaces[0].region_3d.view_perspective = 'CAMERA'


        #ejecuto
        bpy.ops.render.opengl(animation = True)
        if boom_props.autoplay:
            bpy.ops.render.play_rendered_anim()

        #devuelvo settings
        rd.use_stamp = old_use_stamp
        sd.show_only_render = old_onlyrender
        rd.use_simplify = old_simplify
        rd.filepath = old_filepath
        rd.alpha_mode = old_alpha_mode
        #rd.image_settings = old_image_settings
        rd.resolution_percentage = old_resolution_percentage
        context.scene.frame_step = old_frame_step
        if boom_props.scene_cam and view_pers is not 'CAMERA':
            context.area.spaces[0].region_3d.view_perspective = view_pers

        return {'FINISHED'}

    #def cancel(self, context):
    #    print('cancelado...')
    #    return {'CANCELLED'}

def draw_boomsmash_panel(context, layout):
    col = layout.column(align = True)
    cs = context.scene
    wm = context.window_manager
    rd = context.scene.render

    if wm.boom_props.global_toggle:
        boom_props = wm.boom_props
    else:
        boom_props = cs.boom_props

    row = col.row()
    col.operator('bs.doboom', text = 'Playblast', icon = 'RENDER_ANIMATION')
    col.prop(context.window_manager.boom_props, 'global_toggle')
    col.separator()

    split = col.split()
    subcol = split.column()
    #subcol.prop(boom_props, 'incremental')
    subcol.prop(boom_props, 'use_stamp')
    subcol.prop(boom_props, 'onlyrender')
    subcol.prop(boom_props, 'scene_cam')

    subcol = split.column()
    subcol.prop(boom_props, 'transparent')
    subcol.prop(boom_props, 'autoplay')
    subcol.prop(boom_props, 'unsimplify')

    col.separator()
    col.label(text = 'Time range:')
    sub = col.split()
    subrow = sub.row(align = True)
    subrow.prop(context.scene, 'use_preview_range', text = '')
    subrow.prop(context.scene, 'frame_preview_start', text = 'Start')
    subrow.prop(context.scene, 'frame_preview_end', text = 'End')
    subrow.prop(boom_props, 'frame_skip', text = 'Skip')
    col.separator()

    final_res_x = (rd.resolution_x * boom_props.resolution_percentage) / 100
    final_res_y = (rd.resolution_y * boom_props.resolution_percentage) / 100
    col.label(text = 'Display size: {} x {}'.format(str(final_res_x)[:-2], str(final_res_y)[:-2]))
    col.prop(boom_props, 'resolution_percentage', slider = True )

    col.separator()

    #col.label(text = 'Output Format:')
    #col.template_image_settings(wm.image_settings, color_management = False)

    '''
    col.label(text = 'Output folder:')
    row = col.row()
    row.prop(cs.boom_props, 'dirname')
    row.operator('bs.setdirname', text = '', icon = 'PACKAGE')
    col.separator()
    col.label(text = 'Movie file:')
    row = col.row()
    row.prop(cs.boom_props, 'filename')
    row.operator('bs.setfilename', text = '', icon = 'SCENE_DATA')
    '''

    image_settings = rd.image_settings
    file_format = image_settings.file_format
 
    col.label(text = 'Output folder:')
    row = col.row()
    row.prop(cs.boom_props, 'dirname')
    row.operator('bs.setdirname', text = '', icon = 'PACKAGE')
    
    col.separator()
    
    col.label(text = 'Movie file:')
    row = col.row()
    row.prop(cs.boom_props, 'filename')
    row.operator('bs.setfilename', text = '', icon = 'SCENE_DATA')
 
    #split = layout.split()
 
    #col = split.column()
    
    col.separator()
    
    #col.active = not rd.is_movie_format
    #col.prop(rd, "use_overwrite")
    #col.prop(rd, "use_placeholder")
 
    #split.prop(rd, "use_file_extension")
 
    col.label(text = 'Format:')
    row = col.row()
    row.template_image_settings(image_settings, color_management=False)



class VIEW3D_PT_tools_animation_boomsmash(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Playblast'
    bl_context = 'objectmode'
    bl_label = 'Playblast'

    def draw_header(self, context):
        DoBTN = self.layout
        #DoBTN.operator('bs.doboom', text = 'Playblast', icon = 'RENDER_ANIMATION')
        #DoBTN.prop(context.window_manager.boom_props, 'global_toggle')

        #DoBTN.animation = True

    def draw(self, context):
        layout = self.layout
        draw_boomsmash_panel(context, layout)


class VIEW3D_PT_tools_pose_animation_boomsmash(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Playblast'
    bl_context = 'posemode'
    bl_label = 'Playblast'

    def draw_header(self, context):
        DoBTN = self.layout
        #DoBTN.operator('bs.doboom', text = 'Playblast', icon = 'RENDER_ANIMATION')
        #DoBTN.prop(context.window_manager.boom_props, 'global_toggle')

    def draw(self, context):
        layout = self.layout
        draw_boomsmash_panel(context, layout)


def register():
    bpy.utils.register_module(__name__)

    bpy.types.Scene.boom_props = PointerProperty(
            type = BoomProps, name = 'Playblast Properties', description = '')

    bpy.types.WindowManager.boom_props = PointerProperty(
            type = BoomProps, name = 'Playblast Global Properties', description = '')


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.boom_props
    del bpy.types.WindowManager.boom_props


if __name__ == '__main__':
    register()
    #unregister()
    print('Playblast finish!...')
