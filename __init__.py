bl_info = {
	"name": "RE Chain Editor",
	"author": "NSA Cloud, alphaZomega",
	"version": (8, 1),
	"blender": (3, 1, 2),
	"location": "File > Import-Export",
	"description": "Import and export RE Engine chain files.",
	"warning": "",
	"wiki_url": "https://github.com/NSACloud/RE-Chain-Editor",
	"tracker_url": "https://github.com/NSACloud/RE-Chain-Editor/issues",
	"category": "Import-Export"}

#Modified by alphaZomega to support RE2R, RE3R, RE8, RE2-3-7 RT, DMC5 and SF6 

#TODO Fix Header only export

import bpy
from . import addon_updater_ops
import os

from bpy_extras.io_utils import ExportHelper,ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty,PointerProperty
from bpy.types import Operator, OperatorFileListElement,AddonPreferences

from .modules.gen_functions import textColors
from .modules.blender_re_chain import importChainFile,exportChainFile
from .modules.re_chain_propertyGroups import chainToolPanelPropertyGroup,chainHeaderPropertyGroup,chainWindSettingsPropertyGroup,chainSettingsPropertyGroup,chainGroupPropertyGroup,chainNodePropertyGroup,chainJigglePropertyGroup,chainCollisionPropertyGroup,chainClipboardPropertyGroup,chainLinkPropertyGroup,collisionSubDataPropertyGroup,chainLinkCollisionNodePropertyGroup
from .modules.ui_re_chain_panels import OBJECT_PT_ChainObjectModePanel,OBJECT_PT_ChainPoseModePanel,OBJECT_PT_ChainPresetPanel,OBJECT_PT_ChainHeaderPanel,OBJECT_PT_WindSettingsPanel,OBJECT_PT_ChainSettingsPanel,OBJECT_PT_ChainGroupPanel,OBJECT_PT_ChainNodePanel,OBJECT_PT_ChainJigglePanel,OBJECT_PT_ChainCollisionPanel,OBJECT_PT_ChainClipboardPanel,OBJECT_PT_ChainLinkPanel,OBJECT_PT_ChainVisibilityPanel,OBJECT_PT_ChainCollisionSubDataPanel,OBJECT_PT_ChainLinkCollisionPanel,OBJECT_PT_NodeVisPanel,OBJECT_PT_CollisionVisPanel,OBJECT_PT_AngleLimitVisPanel,OBJECT_PT_ColorVisPanel
from .modules.re_chain_operators import WM_OT_ChainFromBone,WM_OT_CollisionFromBones,WM_OT_AlignChainsToBones,WM_OT_AlignFrames,WM_OT_PointFrame,WM_OT_CopyChainProperties,WM_OT_PasteChainProperties,WM_OT_NewChainHeader,WM_OT_ApplyChainSettingsPreset,WM_OT_NewChainSettings,WM_OT_NewWindSettings,WM_OT_NewChainJiggle,WM_OT_ApplyChainGroupPreset,WM_OT_ApplyChainNodePreset,WM_OT_ApplyWindSettingsPreset,WM_OT_SavePreset,WM_OT_OpenPresetFolder,WM_OT_NewChainLink,WM_OT_CreateChainBoneGroup,WM_OT_SwitchToPoseMode,WM_OT_SwitchToObjectMode,WM_OT_HideNonNodes,WM_OT_HideNonAngleLimits,WM_OT_HideNonCollisions,WM_OT_UnhideAll,WM_OT_RenameBoneChain,WM_OT_ApplyAngleLimitRamp,WM_OT_AlignBoneTailsToAxis,WM_OT_SetAttrFlags,WM_OT_CreateChainLinkCollision

class REChainPreferences(AddonPreferences):
	bl_idname = __name__
	
	# addon updater preferences
	auto_check_update: bpy.props.BoolProperty(
	    name = "Auto-check for Update",
	    description = "If enabled, auto-check for updates using an interval",
	    default = False,
	)
	
	updater_interval_months: bpy.props.IntProperty(
	    name='Months',
	    description = "Number of months between checking for updates",
	    default=0,
	    min=0
	)
	updater_interval_days: bpy.props.IntProperty(
	    name='Days',
	    description = "Number of days between checking for updates",
	    default=7,
	    min=0,
	)
	updater_interval_hours: bpy.props.IntProperty(
	    name='Hours',
	    description = "Number of hours between checking for updates",
	    default=0,
	    min=0,
	    max=23
	)
	updater_interval_minutes: bpy.props.IntProperty(
	    name='Minutes',
	    description = "Number of minutes between checking for updates",
	    default=0,
	    min=0,
	    max=59
	)
	def draw(self, context):
		layout = self.layout
		split = layout.split(factor = .3)
		col1 = split.column()
		col2 = split.column()
		col3 = split.column()
		op = col2.operator(
        'wm.url_open',
        text='Donate on Ko-fi',
        icon='FUND'
        )
		op.url = 'https://ko-fi.com/nsacloud'
		addon_updater_ops.update_settings_ui(self,context)
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
	targetArmature : StringProperty(
	   name = "",
	   description = "The armature to attach chain objects to.\nNOTE: If bones that are used by the chain file are missing on the armature, any chain groups or collisions using those bones won't be imported",
	   default = "")
	mergeChain : StringProperty(
	   name = "",
	   description = "Merges the imported chain with an existing chain collection.\nNote that the chain bones used by the imported file must be merged with the target armature.\nUse the Merge With Armature import option in RE Mesh Editor first.\n Leave blank if not merging a chain file",
	   default = "")
	def invoke(self, context, event):
		armature = None
		if bpy.data.armatures.get(self.targetArmature,None) == None:
			try:#Pick selected armature if one is selected
				if armature == None and bpy.context.active_object != None and bpy.context.active_object.type == "ARMATURE":
					armature = bpy.context.active_object
			except:
				pass
			if armature == None:
				for obj in bpy.context.scene.objects:
					if obj.type == "ARMATURE":
						armature = obj
			
			if armature != None:
				self.targetArmature = armature.data.name
			
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	
	def draw(self, context):
		layout = self.layout
		layout.label(text = "Target Armature:")
		layout.prop_search(self, "targetArmature",bpy.data,"armatures")
		layout.label(text = "Merge With Chain Collection:")
		layout.prop_search(self, "mergeChain",bpy.data,"collections",icon = "COLLECTION_COLOR_02")
	def execute(self, context):
		options = {"targetArmature":self.targetArmature,"mergeChain":self.mergeChain}
		editorVersion = str(bl_info["version"][0])+"."+str(bl_info["version"][1])
		print(f"\n{textColors.BOLD}RE Chain Editor V{editorVersion}{textColors.ENDC}")
		print(f"Blender Version {bpy.app.version[0]}.{bpy.app.version[1]}.{bpy.app.version[2]}")
		print("https://github.com/NSACloud/RE-Chain-Editor")
		success = importChainFile(self.filepath,options)
		if success:
			return {"FINISHED"}
		else:
			self.report({"INFO"},"Failed to import RE Chain. Make sure the mesh file is imported.")
			return {"CANCELLED"}


supportedChainVersions = set([54,53,48,52,39,46,24,44,21])		
class ExportREChain(bpy.types.Operator, ExportHelper):
	'''Export RE Engine Chain File'''
	bl_idname = "re_chain.exportfile"
	bl_label = "Export RE Chain"
	bl_options = {'PRESET'}
	
	filename_ext: EnumProperty(
		name="",
		description="Set which game to export the chain for",
		items=[ (".54", "Dragon's Dogma 2", "Dragon's Dogma 2"),
				(".53", "Resident Evil 4 Remake", "Resident Evil 4 Remake"),
				(".48", "Monster Hunter Rise", "Monster Hunter Rise"),
				(".52", "Street Fighter 6", "Street Fighter 6"),
				(".39", "Resident Evil 8", "Resident Evil 8"),
				(".46", "Resident Evil 2/3/7 Ray Tracing", "Resident Evil 2/3/7 Ray Tracing Update"),
				(".44", "RE:Verse", "RE:Verse"),
				(".24", "RE3 / Resistance", "Resident Evil 3 / RE Resistance"),
				(".21", "Devil May Cry 5 /  RE2", "Devil May Cry 5 / Resident Evil 2"),
			   ],
		default = ".53"
		)
	targetCollection : StringProperty(
	   name = "",
	   description = "Set the chain collection to be exported",
	   default = "")
	filter_glob: StringProperty(default="*.chain*", options={'HIDDEN'})
	def invoke(self, context, event):
		
		if bpy.data.collections.get(self.targetCollection,None) == None:
			if bpy.data.collections.get(bpy.context.scene.re_chain_toolpanel.chainCollection):
				self.targetCollection = bpy.context.scene.re_chain_toolpanel.chainCollection
				if ".chain" in self.targetCollection:#Remove blender suffix after .mesh if it exists
					self.filepath = self.targetCollection.split(".chain")[0]+".chain" + self.filename_ext
					
				
		if context.scene.get("REChainLastImportedChainVersion",0) in supportedChainVersions:
			self.filename_ext = "."+str(context.scene["REChainLastImportedChainVersion"])
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
	def draw(self, context):
		layout = self.layout
		layout.label(text = "Chain Version:")
		layout.prop(self,"filename_ext")
		layout.label(text = "Chain Collection:")
		layout.prop_search(self, "targetCollection",bpy.data,"collections",icon = "COLLECTION_COLOR_02")
		
	def execute(self, context):
		options = {"targetCollection":self.targetCollection}
		try:
			chainVersion = int(os.path.splitext(self.filepath)[1].replace(".",""))
		except:
			self.report({"INFO"},"Chain file path is missing number extension. Cannot export.")
			return{"CANCELLED"}
		editorVersion = str(bl_info["version"][0])+"."+str(bl_info["version"][1])
		print(f"\n{textColors.BOLD}RE Chain Editor V{editorVersion}{textColors.ENDC}")
		print(f"Blender Version {bpy.app.version[0]}.{bpy.app.version[1]}.{bpy.app.version[2]}")
		print("https://github.com/NSACloud/RE-Chain-Editor")
		success = exportChainFile(self.filepath,options, chainVersion)
		if success:
			self.report({"INFO"},"Exported RE Chain successfully.")
			#Add batch export entry to RE Toolbox if it doesn't already have one
			if hasattr(bpy.types, "OBJECT_PT_re_tools_quick_export_panel"):
				if not any(item.path == self.filepath for item in bpy.context.scene.re_toolbox_toolpanel.batchExportList_items):
					newExportItem = bpy.context.scene.re_toolbox_toolpanel.batchExportList_items.add()
					newExportItem.fileType = "CHAIN"
					newExportItem.path = self.filepath
					newExportItem.chainCollection = self.targetCollection
					print("Added path to RE Toolbox Batch Export list.")
		else:
			self.report({"INFO"},"RE Chain export failed. See Window > Toggle System Console for details.")
		return {"FINISHED"}

# Registration
classes = [
	REChainPreferences,
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
	chainLinkCollisionNodePropertyGroup,
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
	OBJECT_PT_ChainLinkCollisionPanel,
	OBJECT_PT_NodeVisPanel,
	OBJECT_PT_CollisionVisPanel,
	OBJECT_PT_AngleLimitVisPanel,
	OBJECT_PT_ColorVisPanel,
	WM_OT_ChainFromBone,
	WM_OT_CollisionFromBones,
	#WM_OT_AlignChainsToBones,
	WM_OT_AlignFrames,
	#WM_OT_PointFrame,
	WM_OT_NewChainHeader,
	WM_OT_NewChainSettings,
	WM_OT_NewWindSettings,
	WM_OT_NewChainJiggle,
	WM_OT_NewChainLink,
	WM_OT_CreateChainLinkCollision,
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
	WM_OT_HideNonCollisions,
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
	addon_updater_ops.register(bl_info)
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
	bpy.types.Object.re_chain_chainlink_collision = bpy.props.PointerProperty(type=chainLinkCollisionNodePropertyGroup)
	
	bpy.types.Scene.re_chain_clipboard = bpy.props.PointerProperty(type=chainClipboardPropertyGroup)
	
def unregister():
	addon_updater_ops.unregister()
	for classEntry in classes:
		bpy.utils.unregister_class(classEntry)
		
	bpy.types.TOPBAR_MT_file_import.remove(re_chain_import)
	bpy.types.TOPBAR_MT_file_export.remove(re_chain_export)
	
	#UNREGISTER PROPERTY GROUP PROPERTIES
	#del bpy.types.Object.re_chain_header
if __name__ == '__main__':
	register()