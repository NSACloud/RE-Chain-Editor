bl_info = {
	"name": "RE Chain Editor",
	"author": "NSA Cloud, alphaZomega",
	"version": (3, 0),
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
	bl_label = "Import RE Chain"
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
		success = importChainFile(self.filepath)
		if success:
			return {"FINISHED"}
		else:
			self.report({"INFO"},"Failed to import RE Chain. Make sure the mesh file is imported.")
			return {"CANCELLED"}
		
class ExportREChain(bpy.types.Operator, ExportHelper):
	'''Export RE Engine Chain File'''
	bl_idname = "re_chain.exportfile"
	bl_label = "Export RE Chain"
	bl_options = {'PRESET'}
	default = ".53"
	filename_ext: EnumProperty(
		name="Chain Version",
		description="Set which game to export the chain for",
		items=[ (".53", "RE4", "Resident Evil 4 Remake"),
				(".48", "MH Rise", "Monster Hunter Rise"),
				(".52", "SF6", "Street Fighter 6"),
				(".39", "RE8", "Resident Evil 8"),
				(".46", "RE2/3/7 Ray Tracing", "Resident Evil 2/3/7 Ray Tracing Update"),
				(".24", "RE3 / Resistance", "Resident Evil 3 / RE Resistance"),
				(".21", "DMC 5 /  RE2", "Devil May Cry 5 / Resident Evil 2"),
			   ]
		)
	filter_glob: StringProperty(default="*.chain*", options={'HIDDEN'})

	def execute(self, context):
		try:
			chainVersion = int(os.path.splitext(self.filepath)[1].replace(".",""))
		except:
			self.report({"INFO"},"Chain file path is missing number extension. Cannot export.")
			return{"CANCELLED"}
		success = exportChainFile(self.filepath, chainVersion)
		if success:
			self.report({"INFO"},"Exported RE Chain successfully.")
		else:
			self.report({"INFO"},"RE Chain export failed. See Window > Toggle System Console for details.")
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
	self.layout.operator(ImportREChain.bl_idname, text="RE Chain (.chain.x)")
	
def re_chain_export(self, context):
	self.layout.operator(ExportREChain.bl_idname, text="RE Chain (.chain.x)")

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