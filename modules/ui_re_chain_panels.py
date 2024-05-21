import bpy

from bpy.types import (Panel,
					   Menu,
					   Operator,
					   PropertyGroup,
					   )

from .file_re_chain import version

def tag_redraw(context, space_type="PROPERTIES", region_type="WINDOW"):
	for window in context.window_manager.windows:
		for area in window.screen.areas:
			if area.spaces[0].type == space_type:
				for region in area.regions:
					if region.type == region_type:
						region.tag_redraw()


class OBJECT_PT_ChainObjectModePanel(Panel):
	bl_label = "RE Chain: Object Mode Tools"
	bl_idname = "OBJECT_PT_chain_object_mode_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   
	bl_context = "objectmode"

	@classmethod
	def poll(self,context):
		return context is not None and "HIDE_RE_CHAIN_EDITOR_TAB" not in context.scene

	def draw(self, context):
		scene = context.scene
		re_chain_toolpanel = scene.re_chain_toolpanel
		layout = self.layout
		layout.operator("re_chain.create_chain_header")
		layout.label(text = "Active Chain Collection")
		layout.prop_search(re_chain_toolpanel, "chainCollection",bpy.data,"collections",icon = "COLLECTION_COLOR_02")
		layout.operator("re_chain.create_chain_settings")
		layout.operator("re_chain.create_wind_settings")
		layout.operator("re_chain.create_chain_jiggle")
		layout.operator("re_chain.create_chain_link")
		layout.operator("re_chain.create_chain_link_collision")
		#layout.operator("re_chain.align_chains_to_bone")# Not needed anymore
		layout.operator("re_chain.align_frames")
		layout.operator("re_chain.apply_angle_limit_ramp")
		layout.label(text="Create new chains in Pose Mode.")
		layout.operator("re_chain.switch_to_pose")
		#Not implemented yet
		#layout.operator("re_chain.point_frame")#Not implemented yet

class OBJECT_PT_ChainClipboardPanel(Panel):
	bl_label = "RE Chain: Clipboard"
	bl_idname = "OBJECT_PT_chain_clipboard_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   
	bl_context = "objectmode"

	@classmethod
	def poll(self,context):
		return context is not None and "HIDE_RE_CHAIN_EDITOR_TAB" not in context.scene

	def draw(self, context):
		layout = self.layout
		layout.label(text="Copy Chain Object Properties")
		row = layout.row()
		row.operator("re_chain.copy_chain_properties")
		row.operator("re_chain.paste_chain_properties")
		layout.label(text="Clipboard Contents:")
		layout.label(text=str(context.scene.re_chain_clipboard.re_chain_type_name))
		
class OBJECT_PT_ChainPoseModePanel(Panel):
	bl_label = "RE Chain: Pose Mode Tools"
	bl_idname = "OBJECT_PT_chain_pose_mode_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   
	bl_context = "posemode"

	@classmethod
	def poll(self,context):
		return context.active_object is not None and "HIDE_RE_CHAIN_EDITOR_TAB" not in context.scene

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		re_chain_toolpanel = scene.re_chain_toolpanel
		layout.label(text="Chain Tools")
		layout.label(text = "Active Chain Collection")
		layout.prop_search(re_chain_toolpanel, "chainCollection",bpy.data,"collections",icon = "COLLECTION_COLOR_02")
		layout.operator("re_chain.chain_from_bone",text=re_chain_toolpanel.chainFromBoneLabelName)
		layout.label(text="Collision Tools")
		layout.prop(re_chain_toolpanel, "collisionShape")
		layout.operator("re_chain.collision_from_bone")
		layout.label(text="Extra Tools")
		layout.operator("re_chain.rename_bone_chain")
		layout.operator("re_chain.create_chain_bone_group")
		layout.operator("re_chain.align_bone_tails_to_axis")
		layout.prop(re_chain_toolpanel, "experimentalPoseModeOptions")
		layout.label(text="Configure chains in Object Mode.")
		layout.operator("re_chain.switch_to_object")

class OBJECT_PT_ChainPresetPanel(Panel):
	bl_label = "RE Chain: Presets"
	bl_idname = "OBJECT_PT_chain_presets_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   
	bl_context = "objectmode"

	@classmethod
	def poll(self,context):
		return context is not None and "HIDE_RE_CHAIN_EDITOR_TAB" not in context.scene

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		re_chain_toolpanel = scene.re_chain_toolpanel
		layout.operator("re_chain.save_selected_as_preset")
		layout.operator("re_chain.open_preset_folder")
		#layout.menu(OBJECT_MT_CustomMenu.bl_idname, text="Chain Group")
		layout.label(text="Chain Settings Preset")
		layout.prop(re_chain_toolpanel, "chainSettingsPresets")
		layout.operator("re_chain.apply_chain_settings_preset")
		layout.label(text="Chain Group Preset")
		layout.prop(re_chain_toolpanel, "chainGroupPresets")
		layout.operator("re_chain.apply_chain_group_preset")
		layout.label(text="Chain Node Preset")
		layout.prop(re_chain_toolpanel, "chainNodePresets")
		layout.prop(re_chain_toolpanel,"applyPresetToChildNodes")
		layout.operator("re_chain.apply_chain_node_preset")
		layout.label(text="Wind Settings Preset")
		layout.prop(re_chain_toolpanel, "chainWindSettingsPresets")
		layout.operator("re_chain.apply_wind_settings_preset")
"""
class OBJECT_PT_ChainUtilsPanel(Panel):
	bl_label = "Chain Tools"
	bl_idname = "OBJECT_PT_chain_utils_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   


	@classmethod
	def poll(self,context):
		return context.active_object is not None

	def draw(self, context):
		layout = self.layout
		scene = context.scene
		re_chain_toolpanel = scene.re_chain_toolpanel
		
		layout.label(text="Copy Chain Object Properties")
		row = layout.row()
		row.operator("re_chain.copy_chain_properties")
		row.operator("re_chain.paste_chain_properties")
		layout.label(text="Clipboard Contents: "+str(re_chain_toolpanel.clipboardType))
		layout.separator()
		layout.label(text="Object Mode Tools")
		layout.operator("re_chain.create_chain_header")
		layout.operator("re_chain.create_chain_settings")
		layout.operator("re_chain.create_wind_settings")
		layout.operator("re_chain.align_chains_to_bone")
		layout.operator("re_chain.align_frames")
		layout.operator("re_chain.point_frame")
		layout.label(text="Pose Mode Tools")
		layout.operator("re_chain.chain_from_bone")
		layout.label(text="Collision Shape")
		layout.prop(re_chain_toolpanel, "collisionShape")
		layout.operator("re_chain.collision_from_bone")
		
"""
class OBJECT_PT_ChainHeaderPanel(Panel):
	bl_label = "RE Chain Header Settings"
	bl_idname = "OBJECT_PT_chain_header_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Header Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.active_object and context.active_object.get and context.active_object.get("TYPE",None) == "RE_CHAIN_HEADER"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_header = object.re_chain_header

		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		#col2.prop(re_chain_header, "version")#Set by export
		col2.prop(re_chain_header, "errFlags") 
		col2.prop(re_chain_header, "masterSize")
		col2.prop(re_chain_header, "rotationOrder")
		col2.prop(re_chain_header, "defaultSettingIdx")
		col2.prop(re_chain_header, "calculateMode")
		col2.prop(re_chain_header, "chainAttrFlags")
		col2.prop(re_chain_header, "parameterFlag")
		col2.prop(re_chain_header, "calculateStepTime")
		col2.prop(re_chain_header, "modelCollisionSearch")
		col2.prop(re_chain_header, "legacyVersion")
		col2.prop(re_chain_header, "collisionFilterHit0")
		col2.prop(re_chain_header, "collisionFilterHit1")
		col2.prop(re_chain_header, "collisionFilterHit2")
		col2.prop(re_chain_header, "collisionFilterHit3")
		col2.prop(re_chain_header, "collisionFilterHit4")
		col2.prop(re_chain_header, "collisionFilterHit5")
		col2.prop(re_chain_header, "collisionFilterHit6")
		col2.prop(re_chain_header, "collisionFilterHit7")
		
class OBJECT_PT_WindSettingsPanel(Panel):
	bl_label = "RE Chain Wind Settings"
	bl_idname = "OBJECT_PT_wind_settings_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Wind Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object and context.active_object.get("TYPE",None) == "RE_CHAIN_WINDSETTINGS"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_windsettings = object.re_chain_windsettings
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		col2.prop(re_chain_windsettings, "id")
		col2.prop(re_chain_windsettings, "windDirection") 
		col2.prop(re_chain_windsettings, "windCount")
		col2.prop(re_chain_windsettings, "windType")
		col2.prop(re_chain_windsettings, "randomDamping")
		col2.prop(re_chain_windsettings, "randomDampingCycle")
		col2.prop(re_chain_windsettings, "randomCycleScaling")
		col2.separator()
		col2.prop(re_chain_windsettings, "dir0")
		col2.prop(re_chain_windsettings, "min0")
		col2.prop(re_chain_windsettings, "max0")
		col2.prop(re_chain_windsettings, "phaseShift0")
		col2.prop(re_chain_windsettings, "cycle0")
		col2.prop(re_chain_windsettings, "interval0")
		col2.separator()
		col2.prop(re_chain_windsettings, "dir1")
		col2.prop(re_chain_windsettings, "min1")
		col2.prop(re_chain_windsettings, "max1")
		col2.prop(re_chain_windsettings, "phaseShift1")
		col2.prop(re_chain_windsettings, "cycle1")
		col2.prop(re_chain_windsettings, "interval1")
		col2.separator()
		col2.prop(re_chain_windsettings, "dir2")
		col2.prop(re_chain_windsettings, "min2")
		col2.prop(re_chain_windsettings, "max2")
		col2.prop(re_chain_windsettings, "phaseShift2")
		col2.prop(re_chain_windsettings, "cycle2")
		col2.prop(re_chain_windsettings, "interval2")
		col2.separator()
		col2.prop(re_chain_windsettings, "dir3")
		col2.prop(re_chain_windsettings, "min3")
		col2.prop(re_chain_windsettings, "max3")
		col2.prop(re_chain_windsettings, "phaseShift3")
		col2.prop(re_chain_windsettings, "cycle3")
		col2.prop(re_chain_windsettings, "interval3")
		col2.separator()
		col2.prop(re_chain_windsettings, "dir4")
		col2.prop(re_chain_windsettings, "min4")
		col2.prop(re_chain_windsettings, "max4")
		col2.prop(re_chain_windsettings, "phaseShift4")
		col2.prop(re_chain_windsettings, "cycle4")
		col2.prop(re_chain_windsettings, "interval4")

class OBJECT_PT_ChainSettingsPanel(Panel):
	bl_label = "RE Chain Settings"
	bl_idname = "OBJECT_PT_chain_settings_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_CHAINSETTINGS"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainsettings = object.re_chain_chainsettings
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		col2.prop(re_chain_chainsettings, "id")
		col2.prop(re_chain_chainsettings, "colliderFilterInfoPath")
		col2.prop(re_chain_chainsettings, "sprayParameterArc") 
		col2.prop(re_chain_chainsettings, "sprayParameterFrequency")
		col2.prop(re_chain_chainsettings, "sprayParameterCurve1")
		col2.prop(re_chain_chainsettings, "sprayParameterCurve2")
		col2.prop(re_chain_chainsettings, "chainType")
		col2.prop(re_chain_chainsettings, "settingsAttrFlags")
		col2.prop(re_chain_chainsettings, "muzzleDirection")
		col2.prop(re_chain_chainsettings, "gravity")
		col2.prop(re_chain_chainsettings, "muzzleVelocity")
		col2.prop(re_chain_chainsettings, "damping",slider=True)
		#if version >= 24:
		col2.prop(re_chain_chainsettings, "minDamping",slider=True)
		col2.prop(re_chain_chainsettings, "dampingPow")
		col2.prop(re_chain_chainsettings, "secondDamping",slider=True)
		#if version >= 24:
		col2.prop(re_chain_chainsettings, "secondMinDamping",slider=True)
		col2.prop(re_chain_chainsettings, "secondDampingSpeed")	
		#if version >= 24:	
		col2.prop(re_chain_chainsettings, "secondDampingPow")
		col2.prop(re_chain_chainsettings, "collideMaxVelocity")
		col2.prop(re_chain_chainsettings, "springForce")
		#if version >= 24:
		col2.prop(re_chain_chainsettings, "springLimitRate")
		col2.prop(re_chain_chainsettings, "springMaxVelocity")
		col2.prop(re_chain_chainsettings, "springCalcType")
		col2.prop(re_chain_chainsettings, "unknFlag")
		col2.prop(re_chain_chainsettings, "reduceSelfDistanceRate",slider=True)
		col2.prop(re_chain_chainsettings, "secondReduceDistanceRate",slider=True)
		col2.prop(re_chain_chainsettings, "secondReduceDistanceSpeed")
		col2.prop(re_chain_chainsettings, "friction",slider=True)
		col2.prop(re_chain_chainsettings, "shockAbsorptionRate",slider=True)
		col2.prop(re_chain_chainsettings, "coefOfElasticity",slider=True)
		col2.prop(re_chain_chainsettings, "coefOfExternalForces",slider=True)
		col2.prop(re_chain_chainsettings, "stretchInteractionRatio",slider=True)
		col2.prop(re_chain_chainsettings, "angleLimitInteractionRatio",slider=True)
		col2.prop(re_chain_chainsettings, "shootingElasticLimitRate")
		row = col2.row()
		row.prop(re_chain_chainsettings, "groupDefaultAttr")
		row.operator("re_chain.set_attr_flags",icon='DOWNARROW_HLT', text="")
		col2.prop(re_chain_chainsettings, "windEffectCoef",slider=True)
		col2.prop(re_chain_chainsettings, "unknChainSettingValue1",slider=True)
		col2.prop(re_chain_chainsettings, "unknChainSettingValue0")
		col2.prop(re_chain_chainsettings, "velocityLimit")
		col2.prop(re_chain_chainsettings, "hardness",slider=True)
		#if version >= 48:
		
		
		#if version >= 52:
		col2.prop(re_chain_chainsettings, "unknChainSettingValue2")
		col2.prop(re_chain_chainsettings, "unknChainSettingValue3")

class OBJECT_PT_ChainGroupPanel(Panel):
	bl_label = "RE Chain Group Settings"
	bl_idname = "OBJECT_PT_chain_group_panel"
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Group Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_CHAINGROUP"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chaingroup = object.re_chain_chaingroup
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		
		col2.prop(re_chain_chaingroup, "rotationOrder")
		row = col2.row()
		row.prop(re_chain_chaingroup, "attrFlags")
		row.operator("re_chain.set_attr_flags",icon='DOWNARROW_HLT', text="")
		col2.prop(re_chain_chaingroup, "collisionFilterFlags")
		#if version >= 35:
		col2.prop(re_chain_chaingroup, "dampingNoise0")
		col2.prop(re_chain_chaingroup, "dampingNoise1")
		col2.prop(re_chain_chaingroup, "endRotConstMax")
		col2.prop(re_chain_chaingroup, "angleLimitDirectionMode")
		#if version >= 48:
		col2.prop(re_chain_chaingroup, "unknGroupValue0")
		col2.prop(re_chain_chaingroup, "unknGroupValue0B")
		col2.prop(re_chain_chaingroup, "unknGroupValue1")
		col2.prop(re_chain_chaingroup, "unknGroupValue2")
		#if version >= 52:
		col2.prop(re_chain_chaingroup, "unknGroupValue3")
		col2.prop(re_chain_chaingroup, "unknGroupValue4")
		col2.prop(re_chain_chaingroup, "extraNodeLocalPos")
		#if version >= 48:
		col2.prop(re_chain_chaingroup, "unknBoneHash")
		col2.prop(re_chain_chaingroup, "autoBlendCheckNodeNo") 
		#if version >= 35:
		col2.prop(re_chain_chaingroup, "tagCount")
		col2.prop(re_chain_chaingroup, "tag0")
		col2.prop(re_chain_chaingroup, "tag1")
		col2.prop(re_chain_chaingroup, "tag2")
		col2.prop(re_chain_chaingroup, "tag3")

class OBJECT_PT_ChainNodePanel(Panel):
	bl_label = "RE Chain Node Settings"
	bl_idname = "OBJECT_PT_chain_node_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Node Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_NODE"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainnode = object.re_chain_chainnode
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		col2.prop(re_chain_chainnode, "angleLimitRad")
		col2.prop(re_chain_chainnode, "angleLimitDistance") 
		col2.prop(re_chain_chainnode, "angleLimitRestitution")
		col2.prop(re_chain_chainnode, "angleLimitRestituteStopSpeed")
		col2.prop(re_chain_chainnode, "collisionRadius")
		col2.prop(re_chain_chainnode, "collisionFilterFlags")
		col2.prop(re_chain_chainnode, "capsuleStretchRate0",slider = True)
		col2.prop(re_chain_chainnode, "capsuleStretchRate1",slider = True)
		row = col2.row()
		row.prop(re_chain_chainnode, "attrFlags")
		row.operator("re_chain.set_attr_flags",icon='DOWNARROW_HLT', text="")
		col2.prop(re_chain_chainnode, "windCoef",slider = True)
		col2.prop(re_chain_chainnode, "angleMode")
		col2.prop(re_chain_chainnode, "collisionShape")
		col2.prop(re_chain_chainnode, "attachType")
		col2.prop(re_chain_chainnode, "rotationType")
		#col2.prop(re_chain_chainnode, "jiggleData")
		#if version >= 35:
		col2.prop(re_chain_chainnode, "unknChainNodeValue0")
		col2.prop(re_chain_chainnode, "unknChainNodeValue1")


class OBJECT_PT_ChainJigglePanel(Panel):
	bl_label = "RE Chain Jiggle Settings"
	bl_idname = "OBJECT_PT_chain_jiggle_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Jiggle Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_JIGGLE"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainjiggle = object.re_chain_chainjiggle
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		#col2.prop(re_chain_chainjiggle, "range")
		#col2.prop(re_chain_chainjiggle, "rangeOffset") 
		#col2.prop(re_chain_chainjiggle, "rangeAxis")
		col2.prop(re_chain_chainjiggle, "rangeShape")
		col2.prop(re_chain_chainjiggle, "springForce",slider = True)
		col2.prop(re_chain_chainjiggle, "gravityCoef",slider = True)
		col2.prop(re_chain_chainjiggle, "damping",slider = True)
		row = col2.row()
		row.prop(re_chain_chainjiggle, "attrFlags")
		row.operator("re_chain.set_attr_flags",icon='DOWNARROW_HLT', text="")
		
class OBJECT_PT_ChainCollisionPanel(Panel):
	bl_label = "RE Chain Collision Settings"
	bl_idname = "OBJECT_PT_chain_collision_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Collision Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and (context.active_object.get("TYPE",None) == "RE_CHAIN_COLLISION_SINGLE" or context.active_object.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_ROOT")

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chaincollision = object.re_chain_chaincollision
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		#if version >= 48:
		col2.prop(re_chain_chaincollision, "rotationOrder")
		col2.prop(re_chain_chaincollision, "radius")
		col2.prop(re_chain_chaincollision, "collisionOffset")
		col2.prop(re_chain_chaincollision, "endCollisionOffset")	
		col2.prop(re_chain_chaincollision, "endRadius")
		#if version >= 48:
		col2.prop(re_chain_chaincollision, "lerp") 
		col2.prop(re_chain_chaincollision, "chainCollisionShape")
		col2.prop(re_chain_chaincollision, "subDataCount")
		col2.prop(re_chain_chaincollision, "collisionFilterFlags")
		#col2.prop(re_chain_chaincollision, "subDataFlag")
		
class OBJECT_PT_ChainCollisionSubDataPanel(Panel):
	bl_label = "RE Chain Collision Subdata Settings"
	bl_idname = "OBJECT_PT_chain_collision_subdata_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Collision Subdata Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and ((context.active_object.get("TYPE",None) == "RE_CHAIN_COLLISION_SINGLE" or context.active_object.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_ROOT") and context.active_object.re_chain_chaincollision.subDataCount == 1)

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_collision_subdata = object.re_chain_collision_subdata
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		col2.prop(re_chain_collision_subdata, "pos")
		col2.prop(re_chain_collision_subdata, "pairPos")
		col2.prop(re_chain_collision_subdata, "rotOffset")	
		col2.prop(re_chain_collision_subdata, "radius")
		col2.prop(re_chain_collision_subdata, "id")
		col2.prop(re_chain_collision_subdata, "unknSubCollisionData0")
		col2.prop(re_chain_collision_subdata, "unknSubCollisionData1")
		col2.prop(re_chain_collision_subdata, "unknSubCollisionData2")
		col2.prop(re_chain_collision_subdata, "unknSubCollisionData3")
		
class OBJECT_PT_ChainLinkPanel(Panel):
	bl_label = "RE Chain Link Settings"
	bl_idname = "OBJECT_PT_chain_link_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Link Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_LINK"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainlink = object.re_chain_chainlink
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		col2.prop_search(re_chain_chainlink, "chainGroupAObject",bpy.context.scene,"objects")
		col2.prop_search(re_chain_chainlink, "chainGroupBObject",bpy.context.scene,"objects")
		col2.prop(re_chain_chainlink, "distanceShrinkLimitCoef")
		col2.prop(re_chain_chainlink, "distanceExpandLimitCoef") 
		col2.prop(re_chain_chainlink, "linkMode")
		col2.prop(re_chain_chainlink, "connectFlags")
		col2.prop(re_chain_chainlink, "linkAttrFlags")
		col2.prop(re_chain_chainlink, "skipGroupA")
		col2.prop(re_chain_chainlink, "skipGroupB")
		col2.prop(re_chain_chainlink, "linkOrder")

class OBJECT_PT_ChainLinkCollisionPanel(Panel):
	bl_label = "RE Chain Link Collision Settings"
	bl_idname = "OBJECT_PT_chain_link_collision_panel"
	bl_space_type = "PROPERTIES"   
	bl_region_type = "WINDOW"
	bl_category = "RE Chain Link Collision Settings"
	bl_context = "object"


	@classmethod
	def poll(self,context):
		
		return context and context.object.mode == "OBJECT" and context.active_object.get("TYPE",None) == "RE_CHAIN_LINK_COLLISION"

	def draw(self, context):
		layout = self.layout
		object = context.active_object
		re_chain_chainlink = object.re_chain_chainlink_collision
		
		split = layout.split(factor=0.01)
		col1 = split.column()
		col2 = split.column()
		col2.alignment='RIGHT'
		col2.use_property_split = True
		col2.prop(re_chain_chainlink, "collisionRadius")
		col2.prop(re_chain_chainlink, "collisionFilterFlags") 

class OBJECT_PT_ChainVisibilityPanel(Panel):
	bl_label = "RE Chain: Visibility"
	bl_idname = "OBJECT_PT_chain_visibility_panel"
	bl_space_type = "VIEW_3D"   
	bl_region_type = "UI"
	bl_category = "RE Chain"   
	bl_context = "objectmode"

	@classmethod
	def poll(self,context):
		return context is not None and "HIDE_RE_CHAIN_EDITOR_TAB" not in context.scene

	def draw(self, context):
		re_chain_toolpanel = context.scene.re_chain_toolpanel
		layout = self.layout
		layout.operator("re_chain.hide_non_nodes")
		layout.operator("re_chain.hide_non_angle_limits")
		layout.operator("re_chain.hide_non_collisions")
		layout.operator("re_chain.unhide_all")
		
		
class OBJECT_PT_NodeVisPanel(Panel):
	bl_label = "Chain Node Settings"
	bl_idname = "OBJECT_PT_chain_node_vis_panel"
	bl_parent_id = "OBJECT_PT_chain_visibility_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		layout = self.layout
		obj = context.active_object
		re_chain_toolpanel = context.scene.re_chain_toolpanel
		layout.prop(re_chain_toolpanel, "showRelationLines")
		layout.prop(re_chain_toolpanel, "showNodeNames")
		layout.prop(re_chain_toolpanel, "drawNodesThroughObjects")
		
class OBJECT_PT_CollisionVisPanel(Panel):
	bl_label = "Collision Settings"
	bl_idname = "OBJECT_PT_chain_collision_vis_panel"
	bl_parent_id = "OBJECT_PT_chain_visibility_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		layout = self.layout
		obj = context.active_object
		re_chain_toolpanel = context.scene.re_chain_toolpanel
		
		layout.prop(re_chain_toolpanel, "showCollisionNames")
		layout.prop(re_chain_toolpanel, "drawCollisionsThroughObjects")
		layout.prop(re_chain_toolpanel, "drawCapsuleHandlesThroughObjects")
		layout.prop(re_chain_toolpanel, "drawLinkCollisionsThroughObjects")
		
class OBJECT_PT_AngleLimitVisPanel(Panel):
	bl_label = "Angle Limit Settings"
	bl_idname = "OBJECT_PT_chain_angle_limit_vis_panel"
	bl_parent_id = "OBJECT_PT_chain_visibility_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		layout = self.layout
		obj = context.active_object
		re_chain_toolpanel = context.scene.re_chain_toolpanel
		layout.prop(re_chain_toolpanel, "showAngleLimitCones")
		layout.prop(re_chain_toolpanel, "drawConesThroughObjects")
		layout.prop(re_chain_toolpanel, "hideLastNodeAngleLimit")
		layout.prop(re_chain_toolpanel, "angleLimitDisplaySize")
		layout.prop(re_chain_toolpanel, "coneDisplaySize")
		
class OBJECT_PT_ColorVisPanel(Panel):
	bl_label = "Color Settings"
	bl_idname = "OBJECT_PT_chain_color_vis_panel"
	bl_parent_id = "OBJECT_PT_chain_visibility_panel"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_options = {'DEFAULT_CLOSED'}
	def draw(self, context):
		layout = self.layout
		obj = context.active_object
		re_chain_toolpanel = context.scene.re_chain_toolpanel
		
		layout.prop(re_chain_toolpanel, "collisionColor")
		layout.prop(re_chain_toolpanel, "chainLinkColor")
		layout.prop(re_chain_toolpanel, "chainLinkCollisionColor")
		layout.prop(re_chain_toolpanel, "coneColor")