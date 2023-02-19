bl_info = {
	"name": "RE Chain Editor",
	"author": "NSA Cloud, alphaZomega",
	"version": (2, 0),
	"blender": (2, 93, 0),
	"location": "File > Import-Export",
	"description": "Import and export RE Engine chain files.",
	"warning": "",
	"wiki_url": "https://github.com/NSACloud/RE-Chain-Editor",
	"tracker_url": "",
	"category": "Import-Export"}

#Modified by alphaZomega to support RE2R, RE3R, RE8, RE2-3-7 RT, DMC5 and SF6 

#TODO Fix Header only export

import bpy
import os

from bpy_extras.io_utils import ExportHelper,ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty,PointerProperty
from bpy.types import Operator, OperatorFileListElement

from .modules.blender_re_chain import importChainFile,exportChainFile
from .modules.re_chain_propertyGroups import chainToolPanelPropertyGroup,chainHeaderPropertyGroup,chainWindSettingsPropertyGroup,chainSettingsPropertyGroup,chainGroupPropertyGroup,chainNodePropertyGroup,chainJigglePropertyGroup,chainCollisionPropertyGroup,chainClipboardPropertyGroup,chainLinkPropertyGroup,collisionSubDataPropertyGroup
from .modules.ui_re_chain_panels import OBJECT_PT_ChainObjectModePanel,OBJECT_PT_ChainPoseModePanel,OBJECT_PT_ChainPresetPanel,OBJECT_PT_ChainHeaderPanel,OBJECT_PT_WindSettingsPanel,OBJECT_PT_ChainSettingsPanel,OBJECT_PT_ChainGroupPanel,OBJECT_PT_ChainNodePanel,OBJECT_PT_ChainJigglePanel,OBJECT_PT_ChainCollisionPanel,OBJECT_PT_ChainClipboardPanel,OBJECT_PT_ChainLinkPanel,OBJECT_PT_ChainVisibilityPanel,OBJECT_PT_ChainCollisionSubDataPanel
from .modules.re_chain_operators import WM_OT_ChainFromBone,WM_OT_CollisionFromBones,WM_OT_AlignChainsToBones,WM_OT_AlignFrames,WM_OT_PointFrame,WM_OT_CopyChainProperties,WM_OT_PasteChainProperties,WM_OT_NewChainHeader,WM_OT_ApplyChainSettingsPreset,WM_OT_NewChainSettings,WM_OT_NewWindSettings,WM_OT_NewChainJiggle,WM_OT_ApplyChainGroupPreset,WM_OT_ApplyChainNodePreset,WM_OT_ApplyWindSettingsPreset,WM_OT_SavePreset,WM_OT_OpenPresetFolder,WM_OT_NewChainLink,WM_OT_CreateChainBoneGroup,WM_OT_SwitchToPoseMode,WM_OT_SwitchToObjectMode,WM_OT_HideNonNodes,WM_OT_HideNonAngleLimits,WM_OT_UnhideAll,WM_OT_RenameBoneChain,WM_OT_ApplyAngleLimitRamp,WM_OT_AlignBoneTailsToAxis,WM_OT_SetAttrFlags
class ImportREChain(bpy.types.Operator, ImportHelper):
	'''Import RE Engine Chain File'''
	bl_idname = "re_chain.importfile"
	bl_label = "Import RE Chain (.chain.*)"
	bl_options = {'PRESET', "REGISTER", "UNDO"}
	files : CollectionProperty(
			name="File Path",
			type=OperatorFileListElement,
			)
	directory : StringProperty(
			subtype='DIR_PATH',
			)
	filename_ext = ".chain.*"
	filter_glob: StringProperty(default="*.chain.*", options={'HIDDEN'})

	def execute(self, context):
		directory = self.directory
		#from . import pack_import
		for file_elem in self.files:
			filepath = os.path.join(directory, file_elem.name)
			if os.path.isfile(filepath):
				success = importChainFile(filepath)
				if success:
					return {"FINISHED"}
				else:
					self.report({"INFO"},"Failed to import RE Chain. Make sure the mesh file is imported.")
					return {"CANCELLED"}
		
class ExportREChain(bpy.types.Operator, ExportHelper):
	'''Export RE Engine Chain File (MHRise Sunbreak)'''
	bl_idname = "re_chain.exportfile"
	bl_label = "Export RE Chain (.chain.48)"
	bl_options = {'PRESET'}
	filename_ext = ".48"
	filter_glob: StringProperty(default="*.chain*", options={'HIDDEN'})

	def execute(self, context):
		success = exportChainFile(self.filepath, 48)
		if success:
			self.report({"INFO"},"Exported RE Chain successfully.")
		return {"FINISHED"}

class ExportREChain21(bpy.types.Operator, ExportHelper):
	'''Export RE Engine Chain File (DMC5, RE2R)'''
	bl_idname = "re_chain.exportfile21"
	bl_label = "Export RE Chain (.chain.21)"
	bl_options = {'PRESET'}
	filename_ext = ".21"
	filter_glob: StringProperty(default="*.chain*", options={'HIDDEN'})

	def execute(self, context):
		success = exportChainFile(self.filepath, 21)
		if success:
			self.report({"INFO"},"Exported RE Chain successfully.")
		return {"FINISHED"}

class ExportREChain24(bpy.types.Operator, ExportHelper):
	'''Export RE Engine Chain File (RE3R, Resistance)'''
	bl_idname = "re_chain.exportfile24"
	bl_label = "Export RE Chain (.chain.24)"
	bl_options = {'PRESET'}
	filename_ext = ".24"
	filter_glob: StringProperty(default="*.chain*", options={'HIDDEN'})

	def execute(self, context):
		success = exportChainFile(self.filepath, 24)
		if success:
			self.report({"INFO"},"Exported RE Chain successfully.")
		return {"FINISHED"}

class ExportREChain39(bpy.types.Operator, ExportHelper):
	'''Export RE Engine Chain File (RE8)'''
	bl_idname = "re_chain.exportfile39"
	bl_label = "Export RE Chain (.chain.39)"
	bl_options = {'PRESET'}
	filename_ext = ".39"
	filter_glob: StringProperty(default="*.chain*", options={'HIDDEN'})

	def execute(self, context):
		success = exportChainFile(self.filepath, 39)
		if success:
			self.report({"INFO"},"Exported RE Chain successfully.")
		return {"FINISHED"}

class ExportREChain46(bpy.types.Operator, ExportHelper):
	'''Export RE Engine Chain File (Ray Tracing RE2,3,7)'''
	bl_idname = "re_chain.exportfile46"
	bl_label = "Export RE Chain (.chain.46)"
	bl_options = {'PRESET'}
	filename_ext = ".46"
	filter_glob: StringProperty(default="*.chain*", options={'HIDDEN'})

	def execute(self, context):
		success = exportChainFile(self.filepath, 46)
		if success:
			self.report({"INFO"},"Exported RE Chain successfully.")
		return {"FINISHED"}

class ExportREChain52(bpy.types.Operator, ExportHelper):
	'''Export RE Engine Chain File (Street Fighter 6 Beta)'''
	bl_idname = "re_chain.exportfile52"
	bl_label = "Export RE Chain (.chain.52)"
	bl_options = {'PRESET'}
	filename_ext = ".52"
	filter_glob: StringProperty(default="*.chain*", options={'HIDDEN'})

	def execute(self, context):
		success = exportChainFile(self.filepath, 52)
		if success:
			self.report({"INFO"},"Exported RE Chain successfully.")
		return {"FINISHED"}



# Registration
classes = [
	ImportREChain,
	ExportREChain,
	ExportREChain21,
	ExportREChain24,
	ExportREChain39,
	ExportREChain46,
	ExportREChain52,
	chainToolPanelPropertyGroup,
	chainHeaderPropertyGroup,
	chainWindSettingsPropertyGroup,
	chainSettingsPropertyGroup,
	chainGroupPropertyGroup,
	chainNodePropertyGroup,
	chainJigglePropertyGroup,
	chainCollisionPropertyGroup,
	chainLinkPropertyGroup,
	collisionSubDataPropertyGroup,
	chainClipboardPropertyGroup,
	OBJECT_PT_ChainObjectModePanel,
	OBJECT_PT_ChainClipboardPanel,
	OBJECT_PT_ChainPoseModePanel,
	OBJECT_PT_ChainPresetPanel,
	OBJECT_PT_ChainHeaderPanel,
	OBJECT_PT_WindSettingsPanel,
	OBJECT_PT_ChainSettingsPanel,
	OBJECT_PT_ChainGroupPanel,
	OBJECT_PT_ChainNodePanel,
	OBJECT_PT_ChainJigglePanel,
	OBJECT_PT_ChainCollisionPanel,
	OBJECT_PT_ChainLinkPanel,
	OBJECT_PT_ChainVisibilityPanel,
	OBJECT_PT_ChainCollisionSubDataPanel,
	WM_OT_ChainFromBone,
	WM_OT_CollisionFromBones,
	WM_OT_AlignChainsToBones,
	WM_OT_AlignFrames,
	WM_OT_PointFrame,
	WM_OT_NewChainHeader,
	WM_OT_NewChainSettings,
	WM_OT_NewWindSettings,
	WM_OT_NewChainJiggle,
	WM_OT_NewChainLink,
	WM_OT_CopyChainProperties,
	WM_OT_PasteChainProperties,
	WM_OT_ApplyChainSettingsPreset,
	WM_OT_ApplyChainGroupPreset,
	WM_OT_ApplyChainNodePreset,
	WM_OT_ApplyWindSettingsPreset,
	WM_OT_SavePreset,
	WM_OT_OpenPresetFolder,
	WM_OT_CreateChainBoneGroup,
	WM_OT_SwitchToPoseMode,
	WM_OT_SwitchToObjectMode,
	WM_OT_HideNonNodes,
	WM_OT_HideNonAngleLimits,
	WM_OT_UnhideAll,
	WM_OT_RenameBoneChain,
	WM_OT_ApplyAngleLimitRamp,
	WM_OT_AlignBoneTailsToAxis,
	WM_OT_SetAttrFlags,
	]


def re_chain_import(self, context):
	self.layout.operator(ImportREChain.bl_idname, text="RE Chain (.chain.*)")
	
def re_chain_export(self, context):
	self.layout.operator(ExportREChain21.bl_idname, text="RE Chain (.chain.21)")
	self.layout.operator(ExportREChain24.bl_idname, text="RE Chain (.chain.24)")
	self.layout.operator(ExportREChain39.bl_idname, text="RE Chain (.chain.39)")
	self.layout.operator(ExportREChain46.bl_idname, text="RE Chain (.chain.46)")
	self.layout.operator(ExportREChain.bl_idname, text="RE Chain (.chain.48)")
	self.layout.operator(ExportREChain52.bl_idname, text="RE Chain (.chain.52)")

def register():
	for classEntry in classes:
		bpy.utils.register_class(classEntry)
		
	bpy.types.TOPBAR_MT_file_import.append(re_chain_import)
	bpy.types.TOPBAR_MT_file_export.append(re_chain_export)
	
	bpy.types.Scene.re_chain_toolpanel = PointerProperty(type=chainToolPanelPropertyGroup)
	#bpy.context.scene.re_chain_toolpanel.clipboardType = "None"
	#REGISTER PROPERTY GROUP PROPERTIES
	bpy.types.Object.re_chain_header = bpy.props.PointerProperty(type=chainHeaderPropertyGroup)
	bpy.types.Object.re_chain_windsettings = bpy.props.PointerProperty(type=chainWindSettingsPropertyGroup)
	bpy.types.Object.re_chain_chainsettings = bpy.props.PointerProperty(type=chainSettingsPropertyGroup)
	bpy.types.Object.re_chain_chaingroup = bpy.props.PointerProperty(type=chainGroupPropertyGroup)
	bpy.types.Object.re_chain_chainnode = bpy.props.PointerProperty(type=chainNodePropertyGroup)
	bpy.types.Object.re_chain_chainjiggle = bpy.props.PointerProperty(type=chainJigglePropertyGroup)
	bpy.types.Object.re_chain_collision_subdata = bpy.props.PointerProperty(type=collisionSubDataPropertyGroup)
	bpy.types.Object.re_chain_chaincollision = bpy.props.PointerProperty(type=chainCollisionPropertyGroup)
	bpy.types.Object.re_chain_chainlink = bpy.props.PointerProperty(type=chainLinkPropertyGroup)
	
	bpy.types.Scene.re_chain_clipboard = bpy.props.PointerProperty(type=chainClipboardPropertyGroup)
	
def unregister():
	for classEntry in classes:
		bpy.utils.unregister_class(classEntry)
		
	bpy.types.TOPBAR_MT_file_import.remove(re_chain_import)
	bpy.types.TOPBAR_MT_file_export.remove(re_chain_export)
	
	#UNREGISTER PROPERTY GROUP PROPERTIES
	#del bpy.types.Object.re_chain_header
if __name__ == '__main__':
	register()