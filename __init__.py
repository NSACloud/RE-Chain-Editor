bl_info = {
	"name": "RE Chain Editor",
	"author": "NSA Cloud",
	"version": (1, 0),
	"blender": (2, 93, 0),
	"location": "File > Import-Export",
	"description": "Import and export RE Engine chain files.",
	"warning": "",
	"wiki_url": "https://github.com/NSACloud/RE-Chain-Editor",
	"tracker_url": "",
	"category": "Import-Export"}

#TODO Fix Header only export

import bpy
import os

from bpy_extras.io_utils import ExportHelper,ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty,PointerProperty
from bpy.types import Operator, OperatorFileListElement

from .modules.blender_re_chain import importChainFile,exportChainFile
from .modules.re_chain_propertyGroups import chainToolPanelPropertyGroup,chainHeaderPropertyGroup,chainWindSettingsPropertyGroup,chainSettingsPropertyGroup,chainGroupPropertyGroup,chainNodePropertyGroup,chainCollisionPropertyGroup,chainClipboardPropertyGroup,chainLinkPropertyGroup
from .modules.ui_re_chain_panels import OBJECT_PT_ChainObjectModePanel,OBJECT_PT_ChainPoseModePanel,OBJECT_PT_ChainPresetPanel,OBJECT_PT_ChainHeaderPanel,OBJECT_PT_WindSettingsPanel,OBJECT_PT_ChainSettingsPanel,OBJECT_PT_ChainGroupPanel,OBJECT_PT_ChainNodePanel,OBJECT_PT_ChainCollisionPanel,OBJECT_PT_ChainClipboardPanel,OBJECT_PT_ChainLinkPanel,OBJECT_PT_ChainVisibilityPanel
from .modules.re_chain_operators import WM_OT_ChainFromBone,WM_OT_CollisionFromBones,WM_OT_AlignChainsToBones,WM_OT_AlignFrames,WM_OT_PointFrame,WM_OT_CopyChainProperties,WM_OT_PasteChainProperties,WM_OT_NewChainHeader,WM_OT_ApplyChainSettingsPreset,WM_OT_NewChainSettings,WM_OT_NewWindSettings,WM_OT_ApplyChainGroupPreset,WM_OT_ApplyChainNodePreset,WM_OT_ApplyWindSettingsPreset,WM_OT_SavePreset,WM_OT_OpenPresetFolder,WM_OT_NewChainLink,WM_OT_CreateChainBoneGroup,WM_OT_SwitchToPoseMode,WM_OT_SwitchToObjectMode
class ImportREChain(bpy.types.Operator, ImportHelper):
	'''Import RE Engine Chain File'''
	bl_idname = "re_chain.importfile"
	bl_label = "Import RE Chain (.chain.48)"
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
	'''Export RE Engine Chain File'''
	bl_idname = "re_chain.exportfile"
	bl_label = "Export RE Chain (.chain.48)"
	bl_options = {'PRESET'}
	filename_ext = ".48"
	filter_glob: StringProperty(default="*.chain*", options={'HIDDEN'})

	def execute(self, context):
		success = exportChainFile(self.filepath)
		if success:
			self.report({"INFO"},"Exported RE Chain successfully.")
		return {"FINISHED"}



# Registration
classes = [
	ImportREChain,
	ExportREChain,
	chainToolPanelPropertyGroup,
	chainHeaderPropertyGroup,
	chainWindSettingsPropertyGroup,
	chainSettingsPropertyGroup,
	chainGroupPropertyGroup,
	chainNodePropertyGroup,
	chainCollisionPropertyGroup,
	chainLinkPropertyGroup,
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
	OBJECT_PT_ChainCollisionPanel,
	OBJECT_PT_ChainLinkPanel,
	OBJECT_PT_ChainVisibilityPanel,
	WM_OT_ChainFromBone,
	WM_OT_CollisionFromBones,
	WM_OT_AlignChainsToBones,
	WM_OT_AlignFrames,
	WM_OT_PointFrame,
	WM_OT_NewChainHeader,
	WM_OT_NewChainSettings,
	WM_OT_NewWindSettings,
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
	]


def re_chain_import(self, context):
	self.layout.operator(ImportREChain.bl_idname, text="RE Chain (.chain.48)")
	
def re_chain_export(self, context):
	self.layout.operator(ExportREChain.bl_idname, text="RE Chain (.chain.48)")

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