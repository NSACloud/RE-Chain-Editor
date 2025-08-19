#Author: NSA Cloud
import bpy
from bpy.props import (StringProperty,
					   BoolProperty,
					   IntProperty,
					   FloatProperty,
					   FloatVectorProperty,
					   EnumProperty,
					   PointerProperty,
					   CollectionProperty,
					   )


from .pymmh3 import hash_wide

from .file_re_chain2 import Chain2SettingsSubData

from .re_chain_presets import reloadPresets

#V2 - Removed AttrFlags enum, replaced with a pseudo enum using int value and operator due to large variations in values

def filterChainCollection(self, collection):
	#I messed up with the mesh editor and accidentally left the type of mdf collections as RE_CHAIN_COLLECTION, so this long check is needed
    return True if ((collection.get("~TYPE") == "RE_CHAIN_COLLECTION" or collection.get("~TYPE") == "RE_CLSP_COLLECTION") and (".chain" in collection.name or ".clsp" in collection.name)) else False

def filterChainSetting(self, obj):
    return True if (obj.get("TYPE") == "RE_CHAIN_CHAINSETTINGS" and bpy.context.scene.re_chain_toolpanel.chainCollection != None and obj.name in bpy.context.scene.re_chain_toolpanel.chainCollection.all_objects) else False
def filterChainGroup(self, obj):
    return True if (obj.get("TYPE") == "RE_CHAIN_CHAINGROUP" and bpy.context.scene.re_chain_toolpanel.chainCollection != None and obj.name in bpy.context.scene.re_chain_toolpanel.chainCollection.all_objects) else False


def update_chainFromBoneName(self, context):
	if self.experimentalPoseModeOptions:
		self.chainFromBoneLabelName = "Create Chain From Selection"
	else:
		self.chainFromBoneLabelName = "Create Chain From Bone"

def update_angleLimitSize(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_NODE_FRAME":
			obj.empty_display_size = self.angleLimitDisplaySize

def update_angleLimitConeVis(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_NODE_FRAME_HELPER" and not obj.get("isLastNode"):
			obj.hide_viewport = not self.showAngleLimitCones

def update_collisionColor(self, context):
	if "ChainCollisionMat" in bpy.data.materials:
		mat = bpy.data.materials["ChainCollisionMat"]
		mat.diffuse_color = self.collisionColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.collisionColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.collisionColor[3]
def update_chainLinkColor(self, context):
	if "ChainLinkMat" in bpy.data.materials:
		mat = bpy.data.materials["ChainLinkMat"]
		mat.diffuse_color = self.chainLinkColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.chainLinkColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.chainLinkColor[3]
def update_chainLinkCollisionColor(self, context):
	if "ChainLinkColMat" in bpy.data.materials:
		mat = bpy.data.materials["ChainLinkColMat"]
		mat.diffuse_color = self.chainLinkCollisionColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.chainLinkCollisionColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.chainLinkCollisionColor[3]
def update_coneColor(self, context):
	if "ChainConeMat" in bpy.data.materials:
		mat = bpy.data.materials["ChainConeMat"]
		mat.diffuse_color = self.coneColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.coneColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.coneColor[3]

def update_coneSubGroupColor(self, context):
	if "ChainConeSubGroupMat" in bpy.data.materials:
		mat = bpy.data.materials["ChainConeSubGroupMat"]
		mat.diffuse_color = self.coneSubGroupColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.coneSubGroupColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.coneSubGroupColor[3]
			
def update_chainGroupColor(self, context):
	if "ChainGroupMat" in bpy.data.materials:
		mat = bpy.data.materials["ChainGroupMat"]
		mat.diffuse_color = self.chainGroupColor
		mat.node_tree.nodes[0].inputs["Base Color"].default_value = bpy.context.scene.re_chain_toolpanel.chainGroupColor
		mat.node_tree.nodes[0].inputs["Alpha"].default_value = bpy.context.scene.re_chain_toolpanel.chainGroupColor[3]
def update_RelationLinesVis(self, context):
	bpy.context.space_data.overlay.show_relationship_lines = self.showRelationLines


def update_coneSize(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_NODE_FRAME_HELPER":
			
			xScaleModifier = 1.0
			yScaleModifier = 1.0
			zScaleModifier = 1.0
			
			#Get chain node to check settings
			if obj.parent != None and obj.parent.parent != None and obj.parent.parent.get("TYPE") == "RE_CHAIN_NODE":
				nodeObj = obj.parent.parent
				if nodeObj.re_chain_chainnode.angleMode == "2":#Hinge angle mode
					yScaleModifier = .01
				elif nodeObj.re_chain_chainnode.angleMode == "4":#Limit oval angle mode
					zScaleModifier = .5
				elif nodeObj.re_chain_chainnode.angleMode == "5":#Limit elliptic angle mode
					yScaleModifier = .5
			obj.scale = (self.coneDisplaySize*xScaleModifier,self.coneDisplaySize*yScaleModifier,self.coneDisplaySize*zScaleModifier)
def update_groupSize(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_CHAINGROUP" and obj.type == "CURVE":
			
			obj.data.bevel_depth = self.groupDisplaySize

def update_AngleLimitMode(self, context):
	obj = self.id_data
	#Get child frame, then get the angle limt cone from frame
	if type(obj).__name__ == "Object":#Check if it's an object to prevent issues with clipboard 
		if obj.get("TYPE",None) == "RE_CHAIN_NODE":
			for child in obj.children:
				if child.get("TYPE",None) == "RE_CHAIN_NODE_FRAME":
					for frameChild in child.children:
						if frameChild.get("TYPE",None) == "RE_CHAIN_NODE_FRAME_HELPER":					
							#Determine cone scale
							xScaleModifier = 1.0
							yScaleModifier = 1.0
							zScaleModifier = 1.0
							if obj.re_chain_chainnode.angleMode == "2":#Hinge angle mode
								yScaleModifier = .01
							elif obj.re_chain_chainnode.angleMode == "4":#Limit oval angle mode
								zScaleModifier = .5
							elif obj.re_chain_chainnode.angleMode == "5":#Limit elliptic angle mode
								yScaleModifier = .5
							frameChild.scale = (bpy.context.scene.re_chain_toolpanel.coneDisplaySize*xScaleModifier,bpy.context.scene.re_chain_toolpanel.coneDisplaySize*yScaleModifier,bpy.context.scene.re_chain_toolpanel.coneDisplaySize*zScaleModifier)
							
def update_AngleLimitRad(self, context):
	obj = self.id_data
	#Get child frame, then get the angle limt cone from frame
	if type(obj).__name__ == "Object":#Check if it's an object to prevent issues with clipboard 
		if obj.get("TYPE",None) == "RE_CHAIN_NODE":
			for child in obj.children:
				if child.get("TYPE",None) == "RE_CHAIN_NODE_FRAME":
					for frameChild in child.children:
						if frameChild.get("TYPE",None) == "RE_CHAIN_NODE_FRAME_HELPER":
							
							if "REChainGeometryNodes" in frameChild.modifiers:
								modifier = frameChild.modifiers["REChainGeometryNodes"]
								if bpy.app.version < (4,0,0):
									modifier["Input_0"] = obj.re_chain_chainnode.angleLimitRad
								else:
									modifier["Socket_0"] = obj.re_chain_chainnode.angleLimitRad
								modifier.node_group.interface_update(context)
								#print("Set modifier value")
							#frameChild.data.spot_size = obj.re_chain_chainnode.angleLimitRad

def update_NodeRadius(self, context):
	obj = self.id_data
	if type(obj).__name__ == "Object":#Check if it's an object to prevent issues with clipboard 
		if obj.re_chain_chainnode.collisionRadius != 0:
			obj.empty_display_size = obj.re_chain_chainnode.collisionRadius# * 100
		else:
			obj.empty_display_size = 0.01


def update_CollisionRadius(self, context):
	obj = self.id_data
	if type(obj).__name__ == "Object":#Check if it's an object to prevent issues with clipboard 
		if obj.get("TYPE",None) != "RE_CHAIN_COLLISION_CAPSULE_ROOT":
			#if obj.re_chain_chaincollision.radius != 0:
				#obj.empty_display_size = obj.re_chain_chaincollision.radius# * 100
			#else:
				#obj.empty_display_size = 0.01
			obj.scale = [obj.re_chain_chaincollision.radius]*3
		else:
			for child in obj.children:
				if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START" or child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
					#if obj.re_chain_chaincollision.radius != 0:
						#child.empty_display_size = obj.re_chain_chaincollision.radius# * 100
					#else:
						#child.empty_display_size = 0.01
					if obj.re_chain_chaincollision.chainCollisionShape != "5":
						child.scale = [obj.re_chain_chaincollision.radius]*3#If tapered capsule, don't scale end bone
					else:
						if child.get("TYPE") == "RE_CHAIN_COLLISION_CAPSULE_START":
							child.scale = [obj.re_chain_chaincollision.radius]*3
						 
def update_EndCollisionRadius(self, context):
	obj = self.id_data
	if type(obj).__name__ == "Object":#Check if it's an object to prevent issues with clipboard 
		if obj.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_ROOT":
			for child in obj.children:
				if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END" and obj.re_chain_chaincollision.chainCollisionShape == "5":
					child.scale = [obj.re_chain_chaincollision.endRadius]*3#If tapered capsule, don't scale end bone
def update_NodeNameVis(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_NODE" and not obj.get("isSubGroupNode"):
			obj.show_name = self.showNodeNames

def update_CollisionNameVis(self, context):
	collisionTypes = [
		"RE_CHAIN_COLLISION_SINGLE",
		"RE_CHAIN_COLLISION_CAPSULE_START",
		"RE_CHAIN_COLLISION_CAPSULE_END"]
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) in collisionTypes:
			obj.show_name = self.showCollisionNames
def update_DrawNodesThroughObjects(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_NODE" or obj.get("TYPE",None) == "RE_CHAIN_NODE_FRAME":
			obj.show_in_front = self.drawNodesThroughObjects
def update_DrawChainGroupsThroughObjects(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_CHAINGROUP":
			obj.show_in_front = self.drawChainGroupsThroughObjects
				
def update_DrawConesThroughObjects(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_NODE_FRAME_HELPER":
			obj.show_in_front = self.drawConesThroughObjects

def update_DrawCollisionsThroughObjects(self, context):
	collisionTypes = [
		"RE_CHAIN_COLLISION_SINGLE",
		#"RE_CHAIN_COLLISION_CAPSULE_START",
		#"RE_CHAIN_COLLISION_CAPSULE_END",
		"RE_CHAIN_COLLISION_CAPSULE_ROOT",
		]
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) in collisionTypes:
			obj.show_in_front = self.drawCollisionsThroughObjects

def update_DrawCapsuleHandlesThroughObjects(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START" or obj.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
			obj.show_in_front = self.drawCapsuleHandlesThroughObjects
def update_DrawLinkCollisionsThroughObjects(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_LINK_COLLISION":
			obj.show_in_front = self.drawLinkCollisionsThroughObjects
def update_CollisionOffset(self, context):
	obj = self.id_data
	if obj.get("TYPE",None) != "RE_CHAIN_COLLISION_CAPSULE_ROOT":
		obj.location = obj.re_chain_chaincollision.collisionOffset# * 100
	else:
		for child in obj.children:
			if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
				child.location = obj.re_chain_chaincollision.collisionOffset# * 100

def update_EndCollisionOffset(self, context):
	obj = self.id_data
	if obj.get("TYPE",None) != "RE_CHAIN_COLLISION_CAPSULE_ROOT" and obj.get("TYPE",None) != "RE_CHAIN_COLLISION_SINGLE":
		obj.location = obj.re_chain_chaincollision.endCollisionOffset# * 100
	else:
		for child in obj.children:
			if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
				child.location = obj.re_chain_chaincollision.endCollisionOffset# * 100

def update_ChainGroupA(self, context):
	obj = self.id_data
	if type(obj).__name__ == "Object":#Check if it's an object to prevent issues with clipboard 
		if obj.get("TYPE",None) == "RE_CHAIN_LINK":
			oldName = obj.name
			linkIndex = 0
			if "LINK_" in oldName:
				num = oldName.split("LINK_")[1].split(" -",1)[0]
				if num.isdigit():
					linkIndex = int(num)
			shortNameA = "INVALID"
			shortNameB = "INVALID"
			if obj.re_chain_chainlink.chainGroupBObject in bpy.data.objects and bpy.data.objects[obj.re_chain_chainlink.chainGroupBObject].get("TYPE") == "RE_CHAIN_CHAINGROUP":
				groupBObj = bpy.data.objects[obj.re_chain_chainlink.chainGroupBObject]
				shortNameB = groupBObj.name.replace("CHAIN_GROUP_","")
			if obj.re_chain_chainlink.chainGroupAObject in bpy.data.objects and bpy.data.objects[obj.re_chain_chainlink.chainGroupAObject].get("TYPE") == "RE_CHAIN_CHAINGROUP":
				groupAObj = bpy.data.objects[obj.re_chain_chainlink.chainGroupAObject]
				shortNameA = groupAObj.name.replace("CHAIN_GROUP_","")
				nodeObj = None
				for childObj in groupAObj.children:
					if childObj.get("TYPE") == "RE_CHAIN_NODE":
						nodeObj = childObj
						break
				if nodeObj != None:
					if "REChainGeometryNodes" in obj.modifiers:
						if bpy.app.version < (4,0,0):
							obj.modifiers["REChainGeometryNodes"]["Input_0"] = nodeObj
						else:
							obj.modifiers["REChainGeometryNodes"]["Socket_0"] = nodeObj
						obj.modifiers["REChainGeometryNodes"].node_group.interface_update(context)
			obj.name = f"LINK_{str(linkIndex).zfill(2)} - {shortNameA} > {shortNameB}"
def update_ChainGroupB(self, context):
	obj = self.id_data
	if type(obj).__name__ == "Object":#Check if it's an object to prevent issues with clipboard 
		if obj.get("TYPE",None) == "RE_CHAIN_LINK":
			oldName = obj.name
			linkIndex = 0
			if "LINK_" in oldName:
				num = oldName.split("LINK_")[1].split(" -",1)[0]
				if num.isdigit():
					linkIndex = int(num)
			shortNameA = "INVALID"
			shortNameB = "INVALID"
			if obj.re_chain_chainlink.chainGroupBObject in bpy.data.objects and bpy.data.objects[obj.re_chain_chainlink.chainGroupBObject].get("TYPE") == "RE_CHAIN_CHAINGROUP":
				groupBObj = bpy.data.objects[obj.re_chain_chainlink.chainGroupBObject]
				shortNameB = groupBObj.name.replace("CHAIN_GROUP_","")
				nodeObj = None
				for childObj in groupBObj.children:
					if childObj.get("TYPE") == "RE_CHAIN_NODE":
						nodeObj = childObj
						break
				if nodeObj != None:
					if "REChainGeometryNodes" in obj.modifiers:
						if bpy.app.version < (4,0,0):
							obj.modifiers["REChainGeometryNodes"]["Input_1"] = nodeObj
						else:
							obj.modifiers["REChainGeometryNodes"]["Socket_1"] = nodeObj
						obj.modifiers["REChainGeometryNodes"].node_group.interface_update(context)
			if obj.re_chain_chainlink.chainGroupAObject in bpy.data.objects and bpy.data.objects[obj.re_chain_chainlink.chainGroupAObject].get("TYPE") == "RE_CHAIN_CHAINGROUP":
				groupAObj = bpy.data.objects[obj.re_chain_chainlink.chainGroupAObject]
				shortNameA = groupAObj.name.replace("CHAIN_GROUP_","")
				
			obj.name = f"LINK_{str(linkIndex).zfill(2)} - {shortNameA} > {shortNameB}"
			
def update_ChainLinkCollisionRadius(self, context):
	obj = self.id_data
	if type(obj).__name__ == "Object":#Check if it's an object to prevent issues with clipboard 
		if obj.get("TYPE",None) == "RE_CHAIN_LINK_COLLISION":
			if "REChainGeometryNodes" in obj.modifiers:
				if bpy.app.version < (4,0,0):
					obj.modifiers["REChainGeometryNodes"]["Input_2"] = obj.re_chain_chainlink_collision.collisionRadius
				else:
					obj.modifiers["REChainGeometryNodes"]["Socket_2"] = obj.re_chain_chainlink_collision.collisionRadius
				obj.modifiers["REChainGeometryNodes"].node_group.interface_update(context)

def update_hideLastNodeAngleLimit(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_NODE_FRAME_HELPER" and obj.get("isLastNode"):
			obj.hide_viewport = self.hideLastNodeAngleLimit
class chainToolPanelPropertyGroup(bpy.types.PropertyGroup):
	
	def getChainGroupPresets(self,context):
		return reloadPresets("ChainGroup")
	
	def getChainSettingsPresets(self,context):
		return reloadPresets("ChainSettings")
	
	def getChainNodePresets(self,context):
		return reloadPresets("ChainNode")
	
	def getWindSettingsPresets(self,context):
		return reloadPresets("WindSettings")
	
	collisionShape: EnumProperty(
		name="",
		description="Set collision shape to be used by Create Collision From Bone button",
		items=[("SPHERE", "Sphere", ""),
			   ("CAPSULE", "Capsule", ""),
			   ("TCAPSULE", "Tapered Capsule", ""),
			   ("OBB", "OBB", ""),
			   ("PLANE", "Plane", ""),
			   ("LINESPHERE", "Line Sphere", ""),
			   ("LERPSPHERE", "Lerp Sphere", ""),
			   ]
		)
	
	chainSettingsPresets: EnumProperty(
		name="",
		description="Set preset to be used by Apply Chain Settings Preset button",
		items= getChainSettingsPresets
		)
	chainGroupPresets: EnumProperty(
		name="",
		description="Set preset to be used by Apply Chain Group Preset button",
		items=getChainGroupPresets
		)
	chainNodePresets: EnumProperty(
		name="",
		description="Set preset to be used by Apply Chain Node Preset button",
		items=getChainNodePresets
		)
	applyPresetToChildNodes: BoolProperty(
		name="Apply to Child Nodes",
		description="Apply chain node preset to all nodes that are a child of the selected node",
		default = False
		)
	chainWindSettingsPresets: EnumProperty(
		name="",
		description="Set preset to be used by Apply Wind Settings Preset button",
		items=getWindSettingsPresets
		)
	showNodeNames: BoolProperty(
		name="Show Node Names",
		description="Show Node Names in 3D View",
		default = True,
		update = update_NodeNameVis
		)
	drawNodesThroughObjects: BoolProperty(
		name="Draw Nodes Through Objects",
		description="Make all chain node and frame objects render through any objects in front of them",
		default = True,
		update = update_DrawNodesThroughObjects
		)
	drawChainGroupsThroughObjects: BoolProperty(
		name="Draw Groups Through Objects",
		description="Make all chain group objects render through any objects in front of them",
		default = True,
		update = update_DrawChainGroupsThroughObjects
		)
	showCollisionNames: BoolProperty(
		name="Show Collision Names",
		description="Show Collision Names in 3D View",
		default = True,
		update = update_CollisionNameVis
		)
	drawCollisionsThroughObjects: BoolProperty(
		name="Draw Collisions Through Objects",
		description="Make all collision objects render through any objects in front of them",
		default = False,
		update = update_DrawCollisionsThroughObjects
		)
	drawLinkCollisionsThroughObjects: BoolProperty(
		name="Draw Link Collisions Through Objects",
		description="Make all chain link collisions render through any objects in front of them",
		default = True,
		update = update_DrawLinkCollisionsThroughObjects
		)
	drawCapsuleHandlesThroughObjects: BoolProperty(
		name="Draw Handles Through Objects",
		description="Make all capsule handle objects render through any objects in front of them",
		default = True,
		update = update_DrawCapsuleHandlesThroughObjects
		)
	showAngleLimitCones: BoolProperty(
		name="Show Cones",
		description="Show Angle Limit Cones in 3D View",
		default = True,
		update = update_angleLimitConeVis
		)
	drawConesThroughObjects: BoolProperty(
		name="Draw Cones Through Objects",
		description="Make all angle limit cones render through any objects in front of them",
		default = True,
		update = update_DrawConesThroughObjects
		)
	angleLimitDisplaySize: FloatProperty(
		name="Angle Limit Size",
		description="Set the display size of node angle limits",
		default = 0.04,
		soft_min = 0.0,
		soft_max = .4,
		precision = 3,
		step = .005,
		update = update_angleLimitSize
		)
	
	coneDisplaySize: FloatProperty(
		name="Cone Size",
		description="Set the display size of node angle limit cones",
		default = 0.004,
		soft_min = 0.0,
		soft_max = .2,
		precision = 3,
		step = .005,
		update = update_coneSize
		)
	groupDisplaySize: FloatProperty(
		name="Group Size",
		description="Set the thickness of chain group lines",
		default = 0.006,
		soft_min = 0.0,
		soft_max = .2,
		precision = 3,
		step = .005,
		update = update_groupSize
		)
	experimentalPoseModeOptions: BoolProperty(
		name="Enable Experimental Features",
		description="READ THIS BEFORE ENABLING.\n\nThis button allows for chains to be created from selected bones only.\n\nWith this, you can have multiple chains starting from the same bone and have chains attached to chains.\n\nYou have to select every chain bone in order from top to bottom when creating a new chain.\n\nThere is no error checking on this, if you make a mistake, it will cause issues with the chain.\n\nThis option also enables the ability to create a collision capsule on a single bone.\n\nThese changes are not fully tested and may have issues",
		default = False,
		update = update_chainFromBoneName
		)
	chainFromBoneLabelName: StringProperty(
		name="chainFromBoneLabelName",
		default = "Create Chain From Bone",
		
		)
	"""
	chainCollection: bpy.props.StringProperty(
		name="",
		description = "Set the collection containing the chain file to edit.\nHint: Chain collections are orange.\nYou can create a new chain collection by pressing the \"Create Chain Header\" button.\nThis can also be set to a .clsp collection to create collisions for .clsp files",
		
		)
	"""
	chainCollection: bpy.props.PointerProperty(
		name="",
		description = "Set the collection containing the chain file to edit.\nHint: Chain collections are orange.\nYou can create a new chain collection by pressing the \"Create Chain Header\" button.\nThis can also be set to a .clsp collection to create collisions for .clsp files",
		type=bpy.types.Collection,
		poll = filterChainCollection
		)
	chainSetting: bpy.props.PointerProperty(
		name="",
		description = "Select the chain setting to use for a newly created chain group. You can create a new chain setting by pressing the + button",
		type=bpy.types.Object,
		poll = filterChainSetting
		)
	chainFileType: EnumProperty(
		name="Type",
		description="Chain File Type\nThis determines what fields are usable on chain objects",
		items=[("chain", "Chain", "Old chain file format, use for anything older than MH Wilds/Dead Rising"),
			   ("chain2", "Chain2", "New chain file format, use for MH Wilds/Dead Rising and newer"),
			   ]
		)
	collisionColor: bpy.props.FloatVectorProperty(
        name="Collision Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
		default = (0.003,0.426,0.8,0.3),
		update = update_collisionColor
    )
	chainLinkColor: bpy.props.FloatVectorProperty(
        name="Chain Link Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
		default = (0.0,0.8,0.02,0.40),
		update = update_chainLinkColor
    )
	chainLinkCollisionColor: bpy.props.FloatVectorProperty(
        name="Link Collision Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
		default = (0.8,0.0,0.02,0.40),
		update = update_chainLinkCollisionColor
    )
	coneColor: bpy.props.FloatVectorProperty(
        name="Angle Limit Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
		default = (0.8,0.6,0.0,0.4),
		update = update_coneColor
    )
	coneSubGroupColor: bpy.props.FloatVectorProperty(
        name="Sub Group Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
		default = (0.5,0.0,0.8,0.4),
		update = update_coneSubGroupColor
    )
	chainGroupColor: bpy.props.FloatVectorProperty(
        name="Chain Group Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
		default = (0.8,0.3,0.0,0.47),
		update = update_chainGroupColor
    )
	showRelationLines: BoolProperty(
		name="Show Relation Lines",
		description="Show dotted lines indicating object parents. Recommended to disable since they can be very obtrusive with many objects.\nNote that this affects all objects, not just chain objects",
		default = True,
		update = update_RelationLinesVis,
	)
	hideLastNodeAngleLimit: BoolProperty(
		name="Hide Last Node Cone",
		description="Hides the last chain node's angle limit cone. This is because the last node is typically unused and has a dummy rotation value",
		default = True,
		update = update_hideLastNodeAngleLimit,
	)
class chainHeaderPropertyGroup(bpy.types.PropertyGroup):

	'''version: IntProperty(
		name = "Chain Version",
		description="Chain Version",#TODO Add description
		#default = 35,
		)'''
	"""
	version: EnumProperty(
		name = "Chain Version",
		description="Chain Version",#TODO Add description
		items=[ ("21", ".21 (RE2R, DMC5)", ""),
				("24", ".24 (RE3R, Resistance)", ""),
				("35", ".35 (MHRise)", ""),
				("39", ".39 (RE8)", ""),
				("46", ".46 (Ray Tracing RE2,3,7)", ""),
				("48", ".48 (MHRise Sunbreak)", ""),
				("52", ".52 (Street Fighter 6 Beta)", ""),
				("53", ".53 (RE4)", ""),
				("54", ".54 (Dragon's Dogma 2')", ""),
				("44", ".44 (RE:Verse)", ""),
			   ]
		)
	"""
	errFlags: EnumProperty(
		name="Error Flags",
		description="Apply Data to attribute.",
		items=[ ("0", "ErrFlags_None", ""),
				("1", "ErrFlags_Empty", ""),
				("2", "ErrFlags_NotFoundRefAsset", ""),
				("4", "ErrFlags_NotFoundIncludeAsset", ""),
			   ]
		)
	masterSize: IntProperty(
		name = "Master Size",
		description="Do not change unless you know what you're doing",
		default = 0,
		)
	rotationOrder: EnumProperty(
		name="Rotation Order",
		description="Apply Data to attribute.",
		items=[ ("0", "RotationOrder_XYZ", ""),
				("1", "RotationOrder_YZX", ""),
				("2", "RotationOrder_ZXY", ""),
				("3", "RotationOrder_ZYX", ""),
				("4", "RotationOrder_YXZ", ""),
				("5", "RotationOrder_XZY", ""),
			   ]
		)
	defaultSettingIdx: IntProperty(
		name = "Default Setting Index",
		description="Default Setting Index",#TODO Add description
		default = 0,
		)
	calculateMode: EnumProperty(
		name="Calculate Mode",
		description="Apply Data to attribute.",
		items=[ ("0", "CalculateMode_Default", ""),
				("1", "CalculateMode_Performance", ""),
				("2", "CalculateMode_Balance", ""),
				("3", "CalculateMode_Quality", ""),
			   ]
		)
	chainAttrFlags: EnumProperty(
		name="Chain Attribute Flags",
		description="Apply Data to attribute.",
		items=[ ("0", "ChainAttrFlags_None", ""),
				("1", "ChainAttrFlags_ModelCollisionPreset", ""),
				("2", "ChainAttrFlags_UNKN2", ""),
				("3", "ChainAttrFlags_UNKN3", ""),
				("4", "ChainAttrFlags_UNKN4", ""),
				("5", "ChainAttrFlags_UNKN5", ""),
				("6", "ChainAttrFlags_UNKN6", ""),
			   ]
		)
	parameterFlag: EnumProperty(
		name="Chain Parameter Flags",
		description="Apply Data to attribute.",
		items=[ ("0", "ChainParamFlags_None", ""),
				("1", "ChainParamFlags_ReflectEnviromental", ""),
			   ]
		)
	calculateStepTime: FloatProperty(
		name = "Calculate Step Time",
		description = "Calculate Step Time",#TODO Add description
		default = 2.0,
		)
	modelCollisionSearch: IntProperty(
		name="Model Collision Search",
		description="Model Collision Search",#TODO Add description
		default = 0,
		min = 0,
		max = 255,
		)
	legacyVersion: EnumProperty(
		name="Legacy Version",
		description="Apply Data to attribute.",
		items=[ ("0", "LegacyVersion_Latest", ""),
				("1", "LegacyVersion_Legacy1", ""),
			  ]
		)
	
	collisionFilterHit0: EnumProperty(
		name="Collision Hit Flag 0",
		description="Apply Data to attribute.",
		items=[ ("0", "HitFlags_None", ""),
				("2", "HitFlags_Self", ""),
				("4", "HitFlags_Model", ""),
				("8", "HitFlags_Collider", ""),
				("16", "HitFlags_Angle", ""),
				("32", "HitFlags_Group", ""),
				("64", "HitFlags_VGround", ""),
				("110", "HitFlags_Collision", ""),
			   ]
		)
	collisionFilterHit1: EnumProperty(
		name="Collision Hit Flag 1",
		description="Apply Data to attribute.",
		items=[ ("0", "HitFlags_None", ""),
				("2", "HitFlags_Self", ""),
				("4", "HitFlags_Model", ""),
				("8", "HitFlags_Collider", ""),
				("16", "HitFlags_Angle", ""),
				("32", "HitFlags_Group", ""),
				("64", "HitFlags_VGround", ""),
				("110", "HitFlags_Collision", ""),
			   ]
		)
	collisionFilterHit2: EnumProperty(
		name="Collision Hit Flag 2",
		description="Apply Data to attribute.",
		items=[ ("0", "HitFlags_None", ""),
				("2", "HitFlags_Self", ""),
				("4", "HitFlags_Model", ""),
				("8", "HitFlags_Collider", ""),
				("16", "HitFlags_Angle", ""),
				("32", "HitFlags_Group", ""),
				("64", "HitFlags_VGround", ""),
				("110", "HitFlags_Collision", ""),
			   ]
		)
	collisionFilterHit3: EnumProperty(
		name="Collision Hit Flag 3",
		description="Apply Data to attribute.",
		items=[ ("0", "HitFlags_None", ""),
				("2", "HitFlags_Self", ""),
				("4", "HitFlags_Model", ""),
				("8", "HitFlags_Collider", ""),
				("16", "HitFlags_Angle", ""),
				("32", "HitFlags_Group", ""),
				("64", "HitFlags_VGround", ""),
				("110", "HitFlags_Collision", ""),
			   ]
		)
	collisionFilterHit4: EnumProperty(
		name="Collision Hit Flag 4",
		description="Apply Data to attribute.",
		items=[ ("0", "HitFlags_None", ""),
				("2", "HitFlags_Self", ""),
				("4", "HitFlags_Model", ""),
				("8", "HitFlags_Collider", ""),
				("16", "HitFlags_Angle", ""),
				("32", "HitFlags_Group", ""),
				("64", "HitFlags_VGround", ""),
				("110", "HitFlags_Collision", ""),
			   ]
		)
	collisionFilterHit5: EnumProperty(
		name="Collision Hit Flag 5",
		description="Apply Data to attribute.",
		items=[ ("0", "HitFlags_None", ""),
				("2", "HitFlags_Self", ""),
				("4", "HitFlags_Model", ""),
				("8", "HitFlags_Collider", ""),
				("16", "HitFlags_Angle", ""),
				("32", "HitFlags_Group", ""),
				("64", "HitFlags_VGround", ""),
				("110", "HitFlags_Collision", ""),
			   ]
		)
	collisionFilterHit6: EnumProperty(
		name="Collision Hit Flag 6",
		description="Apply Data to attribute.",
		items=[ ("0", "HitFlags_None", ""),
				("2", "HitFlags_Self", ""),
				("4", "HitFlags_Model", ""),
				("8", "HitFlags_Collider", ""),
				("16", "HitFlags_Angle", ""),
				("32", "HitFlags_Group", ""),
				("64", "HitFlags_VGround", ""),
				("110", "HitFlags_Collision", ""),
			   ]
		)
	collisionFilterHit7: EnumProperty(
		name="Collision Hit Flag 7",
		description="Apply Data to attribute.",
		items=[ ("0", "HitFlags_None", ""),
				("2", "HitFlags_Self", ""),
				("4", "HitFlags_Model", ""),
				("8", "HitFlags_Collider", ""),
				("16", "HitFlags_Angle", ""),
				("32", "HitFlags_Group", ""),
				("64", "HitFlags_VGround", ""),
				("110", "HitFlags_Collision", ""),
			   ]
		)
	#chain2
	highFPSCalculateMode: EnumProperty(
		name="High FPS Calculate Mode",
		description="Apply Data to attribute.",
		items=[ ("0", "HighFpsCalculateMode_Default", ""),
				("1", "HighFpsCalculateMode_LimitedVariableStepTime", ""),
				("2", "HighFpsCalculateMode_VariableStepTime", ""),
			  ],
		default = "1"
		
		)
	
	wilds_unkn1: IntProperty(
		name="Wilds Unknown",
		description="Likely a flag",
		default = 0,
		min = 0,
		max = 255,
		)
	wilds_unkn2: IntProperty(
		name="Wilds Unknown 2",
		description="Likely a flag",
		default = 0,
		min = 0,
		max = 255,
		)
def getChainHeader(ChainHeaderData,targetObject,isChain2 = False):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_header.errFlags = str(ChainHeaderData.errFlags)
	targetObject.re_chain_header.masterSize = ChainHeaderData.masterSize
	targetObject.re_chain_header.rotationOrder = str(ChainHeaderData.rotationOrder)
	targetObject.re_chain_header.defaultSettingIdx = ChainHeaderData.defaultSettingIdx
	targetObject.re_chain_header.calculateMode = str(ChainHeaderData.calculateMode)
	targetObject.re_chain_header.chainAttrFlags = str(ChainHeaderData.chainAttrFlags)
	targetObject.re_chain_header.parameterFlag = str(ChainHeaderData.parameterFlag)
	targetObject.re_chain_header.calculateStepTime = ChainHeaderData.calculateStepTime
	targetObject.re_chain_header.modelCollisionSearch = ChainHeaderData.modelCollisionSearch
	if not isChain2:
		targetObject.re_chain_header.legacyVersion = str(ChainHeaderData.legacyVersion)
	else:
		targetObject.re_chain_header.highFPSCalculateMode = str(ChainHeaderData.highFPSCalculateMode)
		targetObject.re_chain_header.wilds_unkn1 = ChainHeaderData.wilds_unkn1
		targetObject.re_chain_header.wilds_unkn2 = ChainHeaderData.wilds_unkn2
	targetObject.re_chain_header.collisionFilterHit0 = str(ChainHeaderData.collisionFilterHit0)
	targetObject.re_chain_header.collisionFilterHit1 = str(ChainHeaderData.collisionFilterHit1)
	targetObject.re_chain_header.collisionFilterHit2 = str(ChainHeaderData.collisionFilterHit2)
	targetObject.re_chain_header.collisionFilterHit3 = str(ChainHeaderData.collisionFilterHit3)
	targetObject.re_chain_header.collisionFilterHit4 = str(ChainHeaderData.collisionFilterHit4)
	targetObject.re_chain_header.collisionFilterHit5 = str(ChainHeaderData.collisionFilterHit5)
	targetObject.re_chain_header.collisionFilterHit6 = str(ChainHeaderData.collisionFilterHit6)
	targetObject.re_chain_header.collisionFilterHit7 = str(ChainHeaderData.collisionFilterHit7)


def setChainHeaderData(ChainHeaderData,targetObject,isChain2 = False):
	ChainHeaderData.errFlags = int(targetObject.re_chain_header.errFlags)
	ChainHeaderData.masterSize = targetObject.re_chain_header.masterSize 
	ChainHeaderData.rotationOrder = int(targetObject.re_chain_header.rotationOrder)
	ChainHeaderData.defaultSettingIdx = targetObject.re_chain_header.defaultSettingIdx 
	ChainHeaderData.calculateMode = int(targetObject.re_chain_header.calculateMode)
	ChainHeaderData.chainAttrFlags = int(targetObject.re_chain_header.chainAttrFlags)
	ChainHeaderData.parameterFlag = int(targetObject.re_chain_header.parameterFlag)
	ChainHeaderData.calculateStepTime = targetObject.re_chain_header.calculateStepTime
	ChainHeaderData.modelCollisionSearch = int(targetObject.re_chain_header.modelCollisionSearch)
	if not isChain2:
		ChainHeaderData.legacyVersion = int(targetObject.re_chain_header.legacyVersion)
	else:
		ChainHeaderData.highFPSCalculateMode = int(targetObject.re_chain_header.highFPSCalculateMode)
		ChainHeaderData.wilds_unkn1 = targetObject.re_chain_header.wilds_unkn1
		ChainHeaderData.wilds_unkn2 = targetObject.re_chain_header.wilds_unkn2
	ChainHeaderData.collisionFilterHit0 = int(targetObject.re_chain_header.collisionFilterHit0)
	ChainHeaderData.collisionFilterHit1 = int(targetObject.re_chain_header.collisionFilterHit1)
	ChainHeaderData.collisionFilterHit2 = int(targetObject.re_chain_header.collisionFilterHit2)
	ChainHeaderData.collisionFilterHit3 = int(targetObject.re_chain_header.collisionFilterHit3)
	ChainHeaderData.collisionFilterHit4 = int(targetObject.re_chain_header.collisionFilterHit4)
	ChainHeaderData.collisionFilterHit5 = int(targetObject.re_chain_header.collisionFilterHit5)
	ChainHeaderData.collisionFilterHit6 = int(targetObject.re_chain_header.collisionFilterHit6)
	ChainHeaderData.collisionFilterHit7 = int(targetObject.re_chain_header.collisionFilterHit7)
	

class chainWindSettingsPropertyGroup(bpy.types.PropertyGroup):

	id: IntProperty(
		name = "ID",
		description="Set the ID of the wind settings. Note that ID conflicts are resolved automatically upon export, so changing it is not necessary",#TODO Add description
		default = 1,
		)
	windDirection: EnumProperty(
		name="Wind Direction",
		description="Apply Data to attribute.",
		items=[ ("0", "WindDirection_Global", ""),
				("1", "WindDirection_Local", ""),
			  ]
		)
	windCount: IntProperty(
		name = "Wind Count",
		description="Wind Count",#TODO Add description
		default = 1,
		)
	windType: EnumProperty(
		name="Wind Type",
		description="Apply Data to attribute.",
		items=[ ("0", "WindType_None", ""),
				("1", "WindType_WindOrSpring", ""),
				("2", "WindType_GravityWave", ""),
				("3", "WindType_WindWave", ""),
			  ]
		)
	randomDamping: FloatProperty(
		name = "Random Damping",
		description="Random Damping",#TODO Add description
		default = 0.5,
		)
	randomDampingCycle: FloatProperty(
		name = "Random Damping Cycle",
		description="Random Damping Cycle",#TODO Add description
		default = 3.0,
		)
	randomCycleScaling: FloatProperty(
		name = "Random Cycle Scaling",
		description="Random Cycle Scaling",#TODO Add description
		default = 0.0,
		)
	
	dir0: FloatVectorProperty(
		name = "Direction 0",
		description="Direction 0",#TODO Add description
		default = (0.0,0.0,0.0),
		subtype = "XYZ",
		)
	min0: FloatProperty(
		name = "Direction 0 Min",
		description="Direction 0 Min",#TODO Add description
		default = 0.0,
		)
	max0: FloatProperty(
		name = "Direction 0 Max",
		description="Direction 0 Max",#TODO Add description
		default = 0.0,
		)
	phaseShift0: FloatProperty(
		name = "Direction 0 Phase Shift",
		description="Direction 0 Phase Shift",#TODO Add description
		default = 0.0,
		)
	cycle0: FloatProperty(
		name = "Direction 0 Cycle",
		description="Direction 0 Cycle",#TODO Add description
		default = 0.0,
		)
	interval0: FloatProperty(
		name = "Direction 0 Interval",
		description="Direction 0 Interval",#TODO Add description
		default = 0.0,
		)
	
	dir1: FloatVectorProperty(
		name = "Direction 1",
		description="Direction 1",#TODO Add description
		default = (0.0,0.0,0.0),
		subtype = "XYZ"
		)
	min1: FloatProperty(
		name = "Direction 1 Min",
		description="Direction 1 Min",#TODO Add description
		default = 0.0,
		)
	max1: FloatProperty(
		name = "Direction 1 Max",
		description="Direction 1 Max",#TODO Add description
		default = 0.0,
		)
	phaseShift1: FloatProperty(
		name = "Direction 1 Phase Shift",
		description="Direction 1 Phase Shift",#TODO Add description
		default = 0.0,
		)
	cycle1: FloatProperty(
		name = "Direction 1 Cycle",
		description="Direction 1 Cycle",#TODO Add description
		default = 0.0,
		)
	interval1: FloatProperty(
		name = "Direction 1 Interval",
		description="Direction 1 Interval",#TODO Add description
		default = 0.0,
		)
	
	dir2: FloatVectorProperty(
		name = "Direction 2",
		description="Direction 2",#TODO Add description
		default = (0.0,0.0,0.0),
		subtype = "XYZ"
		)
	min2: FloatProperty(
		name = "Direction 2 Min",
		description="Direction 2 Min",#TODO Add description
		default = 0.0,
		)
	max2: FloatProperty(
		name = "Direction 2 Max",
		description="Direction 2 Max",#TODO Add description
		default = 0.0,
		)
	phaseShift2: FloatProperty(
		name = "Direction 2 Phase Shift",
		description="Direction 2 Phase Shift",#TODO Add description
		default = 0.0,
		)
	cycle2: FloatProperty(
		name = "Direction 2 Cycle",
		description="Direction 2 Cycle",#TODO Add description
		default = 0.0,
		)
	interval2: FloatProperty(
		name = "Direction 2 Interval",
		description="Direction 2 Interval",#TODO Add description
		default = 0.0,
		)
	
	dir3: FloatVectorProperty(
		name = "Direction 3",
		description="Direction 3",#TODO Add description
		default = (0.0,0.0,0.0),
		subtype = "XYZ"
		)
	min3: FloatProperty(
		name = "Direction 3 Min",
		description="Direction 3 Min",#TODO Add description
		default = 0.0,
		)
	max3: FloatProperty(
		name = "Direction 3 Max",
		description="Direction 3 Max",#TODO Add description
		default = 0.0,
		)
	phaseShift3: FloatProperty(
		name = "Direction 3 Phase Shift",
		description="Direction 3 Phase Shift",#TODO Add description
		default = 0.0,
		)
	cycle3: FloatProperty(
		name = "Direction 3 Cycle",
		description="Direction 3 Cycle",#TODO Add description
		default = 0.0,
		)
	interval3: FloatProperty(
		name = "Direction 3 Interval",
		description="Direction 3 Interval",#TODO Add description
		default = 0.0,
		)
	
	dir4: FloatVectorProperty(
		name = "Direction 4",
		description="Direction 4",#TODO Add description
		default = (0.0,0.0,0.0),
		subtype = "XYZ"
		)
	min4: FloatProperty(
		name = "Direction 4 Min",
		description="Direction 4 Min",#TODO Add description
		default = 0.0,
		)
	max4: FloatProperty(
		name = "Direction 4 Max",
		description="Direction 4 Max",#TODO Add description
		default = 0.0,
		)
	phaseShift4: FloatProperty(
		name = "Direction 4 Phase Shift",
		description="Direction 4 Phase Shift",#TODO Add description
		default = 0.0,
		)
	cycle4: FloatProperty(
		name = "Direction 4 Cycle",
		description="Direction 4 Cycle",#TODO Add description
		default = 0.0,
		)
	interval4: FloatProperty(
		name = "Direction 4 Interval",
		description="Direction 4 Interval",#TODO Add description
		default = 0.0,
		)
	
  
def getWindSettings(WindSettingsData,targetObject,isChain2 = False):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_windsettings.id = WindSettingsData.id
	targetObject.re_chain_windsettings.windDirection = str(WindSettingsData.windDirection)
	targetObject.re_chain_windsettings.windCount = WindSettingsData.windCount
	targetObject.re_chain_windsettings.windType = str(WindSettingsData.windType)
	targetObject.re_chain_windsettings.randomDamping = WindSettingsData.randomDamping
	targetObject.re_chain_windsettings.randomDampingCycle = WindSettingsData.randomDampingCycle
	targetObject.re_chain_windsettings.randomCycleScaling = WindSettingsData.randomCycleScaling
	
	targetObject.re_chain_windsettings.dir0 = (WindSettingsData.dir0X,WindSettingsData.dir0Y,WindSettingsData.dir0Z)
	targetObject.re_chain_windsettings.min0 = WindSettingsData.min0
	targetObject.re_chain_windsettings.max0 = WindSettingsData.max0
	targetObject.re_chain_windsettings.phaseShift0 = WindSettingsData.phaseShift0
	targetObject.re_chain_windsettings.cycle0 = WindSettingsData.cycle0
	targetObject.re_chain_windsettings.interval0 = WindSettingsData.interval0
	
	targetObject.re_chain_windsettings.dir1 = (WindSettingsData.dir1X,WindSettingsData.dir1Y,WindSettingsData.dir1Z)
	targetObject.re_chain_windsettings.min1 = WindSettingsData.min1
	targetObject.re_chain_windsettings.max1 = WindSettingsData.max1
	targetObject.re_chain_windsettings.phaseShift1 = WindSettingsData.phaseShift1
	targetObject.re_chain_windsettings.cycle1 = WindSettingsData.cycle1
	targetObject.re_chain_windsettings.interval1 = WindSettingsData.interval1
	
	targetObject.re_chain_windsettings.dir2 = (WindSettingsData.dir2X,WindSettingsData.dir2Y,WindSettingsData.dir2Z)
	targetObject.re_chain_windsettings.min2 = WindSettingsData.min2
	targetObject.re_chain_windsettings.max2 = WindSettingsData.max2
	targetObject.re_chain_windsettings.phaseShift2 = WindSettingsData.phaseShift2
	targetObject.re_chain_windsettings.cycle2 = WindSettingsData.cycle2
	targetObject.re_chain_windsettings.interval2 = WindSettingsData.interval2
	
	targetObject.re_chain_windsettings.dir3 = (WindSettingsData.dir3X,WindSettingsData.dir3Y,WindSettingsData.dir3Z)
	targetObject.re_chain_windsettings.min3 = WindSettingsData.min3
	targetObject.re_chain_windsettings.max3 = WindSettingsData.max3
	targetObject.re_chain_windsettings.phaseShift3 = WindSettingsData.phaseShift3
	targetObject.re_chain_windsettings.cycle3 = WindSettingsData.cycle3
	targetObject.re_chain_windsettings.interval3 = WindSettingsData.interval3
	
	targetObject.re_chain_windsettings.dir4 = (WindSettingsData.dir4X,WindSettingsData.dir4Y,WindSettingsData.dir4Z)
	targetObject.re_chain_windsettings.min4 = WindSettingsData.min4
	targetObject.re_chain_windsettings.max4 = WindSettingsData.max4
	targetObject.re_chain_windsettings.phaseShift4 = WindSettingsData.phaseShift4
	targetObject.re_chain_windsettings.cycle4 = WindSettingsData.cycle4
	targetObject.re_chain_windsettings.interval4 = WindSettingsData.interval4
	
def setWindSettingsData(WindSettingsData,targetObject,isChain2 = False):
	WindSettingsData.id = targetObject.re_chain_windsettings.id 
	WindSettingsData.windDirection = int(targetObject.re_chain_windsettings.windDirection)
	WindSettingsData.windCount = targetObject.re_chain_windsettings.windCount 
	WindSettingsData.windType = int(targetObject.re_chain_windsettings.windType)
	WindSettingsData.randomDamping = targetObject.re_chain_windsettings.randomDamping 
	WindSettingsData.randomDampingCycle = targetObject.re_chain_windsettings.randomDampingCycle 
	WindSettingsData.randomCycleScaling = targetObject.re_chain_windsettings.randomCycleScaling 
	
	WindSettingsData.dir0X = targetObject.re_chain_windsettings.dir0[0]
	WindSettingsData.dir0Y = targetObject.re_chain_windsettings.dir0[1]
	WindSettingsData.dir0Z = targetObject.re_chain_windsettings.dir0[2]
	
	WindSettingsData.min0 = targetObject.re_chain_windsettings.min0 
	WindSettingsData.max0 = targetObject.re_chain_windsettings.max0 
	WindSettingsData.phaseShift0 = targetObject.re_chain_windsettings.phaseShift0 
	WindSettingsData.cycle0 = targetObject.re_chain_windsettings.cycle0 
	WindSettingsData.interval0 = targetObject.re_chain_windsettings.interval0 
	
	WindSettingsData.dir1X = targetObject.re_chain_windsettings.dir1[0]
	WindSettingsData.dir1Y = targetObject.re_chain_windsettings.dir1[1]
	WindSettingsData.dir1Z = targetObject.re_chain_windsettings.dir1[2]
	
	WindSettingsData.min1 = targetObject.re_chain_windsettings.min1 
	WindSettingsData.max1 = targetObject.re_chain_windsettings.max1 
	WindSettingsData.phaseShift1 = targetObject.re_chain_windsettings.phaseShift1 
	WindSettingsData.cycle1 = targetObject.re_chain_windsettings.cycle1 
	WindSettingsData.interval1 = targetObject.re_chain_windsettings.interval1 
	
	WindSettingsData.dir2X = targetObject.re_chain_windsettings.dir2[0]
	WindSettingsData.dir2Y = targetObject.re_chain_windsettings.dir2[1]
	WindSettingsData.dir2Z = targetObject.re_chain_windsettings.dir2[2]
	
	WindSettingsData.min2 = targetObject.re_chain_windsettings.min2 
	WindSettingsData.max2 = targetObject.re_chain_windsettings.max2 
	WindSettingsData.phaseShift2 = targetObject.re_chain_windsettings.phaseShift2 
	WindSettingsData.cycle2 = targetObject.re_chain_windsettings.cycle2 
	WindSettingsData.interval2 = targetObject.re_chain_windsettings.interval2 
	
	WindSettingsData.dir3X = targetObject.re_chain_windsettings.dir3[0]
	WindSettingsData.dir3Y = targetObject.re_chain_windsettings.dir3[1]
	WindSettingsData.dir3Z = targetObject.re_chain_windsettings.dir3[2]
	
	WindSettingsData.min3 = targetObject.re_chain_windsettings.min3 
	WindSettingsData.max3 = targetObject.re_chain_windsettings.max3 
	WindSettingsData.phaseShift3 = targetObject.re_chain_windsettings.phaseShift3 
	WindSettingsData.cycle3 = targetObject.re_chain_windsettings.cycle3 
	WindSettingsData.interval3 = targetObject.re_chain_windsettings.interval3 
	
	WindSettingsData.dir4X = targetObject.re_chain_windsettings.dir4[0]
	WindSettingsData.dir4Y = targetObject.re_chain_windsettings.dir4[1]
	WindSettingsData.dir4Z = targetObject.re_chain_windsettings.dir4[2]
	
	WindSettingsData.min4 = targetObject.re_chain_windsettings.min4 
	WindSettingsData.max4 = targetObject.re_chain_windsettings.max4 
	WindSettingsData.phaseShift4 = targetObject.re_chain_windsettings.phaseShift4 
	WindSettingsData.cycle4 = targetObject.re_chain_windsettings.cycle4 
	WindSettingsData.interval4 = targetObject.re_chain_windsettings.interval4 

class ChainSettingSubDataPropertyGroup(bpy.types.PropertyGroup):

    values: bpy.props.IntVectorProperty(
		name = "Values",
        size = 7,
		min = 0,
		max = 255,
    )
class CHAIN_UL_ChainSettingsSubDataList(bpy.types.UIList):
	
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # Display the properties of each item in the UIList
		layout.prop(item,"values")
	# Disable double-click to rename
	def invoke(self, context, event):
		return {'PASS_THROUGH'}


class chainSettingsPropertyGroup(bpy.types.PropertyGroup):

	id: IntProperty(
		name = "ID",
		description="Set the ID of the chain settings. Note that ID conflicts are resolved automatically upon export, so changing it is not necessary",
		default = 0,
		)
	colliderFilterInfoPath: StringProperty(
		name = "Collider Filter Info",
		description = "Set the file path of collider filter file (.cfil)",
		default = "",
		)
	sprayParameterArc: FloatProperty(
		name = "Spray Parameter Arc",
		description = "Spray Parameter Arc",#TODO Add description
		default = 0.0,
		)
	sprayParameterFrequency: FloatProperty(
		name = "Spray Parameter Frequency",
		description = "Spray Parameter Frequency",#TODO Add description
		default = 0.0,
		)
	sprayParameterCurve1: FloatProperty(
		name = "Spray Parameter Curve 1",
		description = "Spray Parameter Curve 1",#TODO Add description
		default = 0.0,
		)
	sprayParameterCurve2: FloatProperty(
		name = "Spray Parameter Curve 2",
		description = "Spray Parameter Curve 2",#TODO Add description
		default = 0.0,
		)
	chainType: EnumProperty(
		name="Chain Type",
		description="Apply Data to attribute.",
		items=[ ("0", "ChainType_Chain", ""),
				("1", "ChainType_Shooter", ""),
			  ]
		)
	settingsAttrFlags: IntProperty(
		name="Setting Attribute Flags",
		description="",
		default = 0,
		)
	muzzleDirection: EnumProperty(
		name="Muzzle Direction",
		description="Apply Data to attribute.",
		items=[ ("0", "DirectionOfEmission_Global", ""),
				("1", "DirectionOfEmission_Local", ""),
				("2", "DirectionOfEmission_GroupLocal", ""),
			  ]
		)
	gravity: FloatVectorProperty(
		name = "Gravity",
		description="Gravity",#TODO Add description
		default = (0.0,-9.8,0.0),
		subtype = "XYZ"
		)
	muzzleVelocity: FloatVectorProperty(
		name = "Muzzle Velocity",
		description="Muzzle Velocity",#TODO Add description
		default = (0.0,0.0,3.0),
		subtype = "XYZ",
		unit = "VELOCITY"
		)
	damping: FloatProperty(
		name = "Damping",
		description = "Reduces movement of nodes",#TODO Add description
		default = 0.2,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	secondDamping: FloatProperty(
		name = "Second Damping",
		description = "Reduces movement of nodes",#TODO Add description
		default = 0.05,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	secondDampingSpeed: FloatProperty(
		name = "Second Damping Speed",
		description = "Second Damping Speed",#TODO Add description
		default = 0.00,
		)
	minDamping: FloatProperty(
		name = "Min Damping",
		description = "Minimum amount of damping to be applied\nVersion 24 and above only",#TODO Add description
		default = 0.2,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	secondMinDamping: FloatProperty(
		name = "Second Min Damping",
		description = "Minimum amount of damping to be applied\nVersion 24 and above only",#TODO Add description
		default = 0.00,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	dampingPow: FloatProperty(
		name = "Damping Power",
		description = "Damping Power\nVersion 24 and above only",#TODO Add description
		default = 1.00,
		)
	secondDampingPow: FloatProperty(
		name = "Second Damping Power",
		description = "Second Damping Power\nVersion 24 and above only",#TODO Add description
		default = 0.00,
		)
	collideMaxVelocity: FloatProperty(
		name = "Collide Max Velocity",
		description = "Collide Max Velocity\nVersion 24 and above only",#TODO Add description
		default = 0.00,
		unit = "VELOCITY"
		)
	
	springForce: FloatProperty(
		name = "Spring Force",
		description = "How hard nodes will spring back to their resting position",
		default = 0.00,
		)
	springLimitRate: FloatProperty(
		name = "Spring Limit Rate",
		description = "Spring Limit Rate\nVersion 24 and above only",#TODO Add description
		default = 0.00,
		)
	springMaxVelocity: FloatProperty(
		name = "Spring Max Velocity",
		description = "Spring Max Velocity\nVersion 24 and above only",#TODO Add description
		default = 0.00,
		unit = "VELOCITY"
		)
	springCalcType: EnumProperty(
		name="Spring Calculation Type",
		description="Spring Calculation Type.\nVersion 24 and above only",
		items=[ ("0", "ChainSpringCalcType_Position", ""),
				("1", "ChainSpringCalcType_Rotation", ""),
				("2", "ChainSpringCalcType_VFRPosition", ""),
				("3", "ChainSpringCalcType_VFRRotation", ""),
			   ]
		)
	windDelayType: EnumProperty(
		name="Wind Delay Type",
		description="Version 24 and above",
		items=[ ("0", "WindDelayType_None", ""),
				("1", "WindDelayType_Auto", ""),
				("2", "WindDelayType_Manual", ""),
			  ]
		)
	reduceSelfDistanceRate: FloatProperty(
		name = "Reduce Self Distance Rate",
		description = "Reduce Self Distance Rate",#TODO Add description
		default = 0.00,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	secondReduceDistanceRate: FloatProperty(
		name = "Second Reduce Distance Rate",
		description = "Second Reduce Distance Rate",#TODO Add description
		default = 0.00,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	secondReduceDistanceSpeed: FloatProperty(
		name = "Second Reduce Distance Speed",
		description = "Second Reduce Distance Speed",#TODO Add description
		default = 0.00,
		)
	friction: FloatProperty(
		name = "Friction",
		description = "Friction",#TODO Add description
		default = 0.00,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	shockAbsorptionRate: FloatProperty(
		name = "Shock Absorption Rate",
		description = "Shock Absorption Rate",#TODO Add description
		default = 0.00,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	coefOfElasticity: FloatProperty(
		name = "Coefficient Of Elasticity",
		description = "Affects bounciness of spring force",#TODO Add description
		default = 0.00,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	coefOfExternalForces: FloatProperty(
		name = "Coefficient Of External Forces",
		description = "Coefficient Of External Forces",#TODO Add description
		default = 0.00,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	stretchInteractionRatio: FloatProperty(
		name = "Stretch Interaction Ratio",
		description = "Stretch Interaction Ratio",#TODO Add description
		default = 0.5,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	angleLimitInteractionRatio: FloatProperty(
		name = "Angle Limit Interaction Ratio",
		description = "Angle Limit Interaction Ratio",#TODO Add description
		default = 0.5,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	shootingElasticLimitRate: FloatProperty(
		name = "Shooting Elastic Limit Rate",
		description = "Shooting Elastic Limit Rate",#TODO Add description
		default = 0.00,
		
		)

	groupDefaultAttr: IntProperty(
		name="Group Default Attribute",
		description="Controls how chain groups interact. Also affects whether nodes can collide",
		default = 0,
		)
	windEffectCoef: FloatProperty(
		name = "Wind Effect Coefficient",
		description = "Affects how much stage wind affects chain. NOTE: Applies to chain even if it is not parented to wind settings",#TODO Add description
		default = 0.00,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	velocityLimit: FloatProperty(
		name = "Velocity Limit",
		description = "Velocity Limit",#TODO Add description
		default = 0.00,
		unit = "VELOCITY"
		)
	hardness: FloatProperty(
		name = "Hardness",
		description = "Hardness",#TODO Add description
		default = 0.00,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	windDelaySpeed: FloatProperty(
		name = "Wind Delay Speed",
		description = "Capcom Example Values RE4: [0.0]\nVersion 48 and above only",#TODO Add description
		default = 0.00,
		)
	envWindEffectCoef: FloatProperty(
		name = "Env Wind Effect Coefficient",
		description = "Capcom Example Values RE4: [0.0, 0.003000000026077032, 0.004999999888241291, 0.009999999776482582, 0.019999999552965164, 0.029999999329447746, 0.03500000014901161, 0.03999999910593033, 0.05000000074505806, 0.10000000149011612, 0.5]\nVersion 48 and above only",
		default = 0.10,
		)
	motionForce: FloatProperty(
		name = "Motion Force",
		description = "Capcom Example Values RE4: [0.0, 1.0, 5.0, 20.0, 30.0, 40.0, 41.0, 45.0, 50.0, 53.0, 60.0, 65.0]\nVersion 52 and above only",
		default = 0.00,
		)
	
	windDelayType: EnumProperty(
		name="Wind Delay Type",
		description="Version 24 and above",
		items=[ ("0", "WindDelayType_None", ""),
				("1", "WindDelayType_Auto", ""),
				("2", "WindDelayType_Manual", ""),
			  ]
		)
	motionForceCalcType: EnumProperty(
		name="Motion Force Calculation Type (chain2)",
		description="*This value might not be motion force calc type\nVersion 9 and above",
		items=[ ("0", "MotionForceCalcType_MotionForce", ""),
				("1", "MotionForceCalcType_InitShapeForce", ""),
			  ]
		)
	#chain2 subdata
	unknQuaternion: FloatVectorProperty(
		name = "Unknown 0",
		description="Quaternion Maybe (Always (0.0,0.0,0.0,1.0))",
		default = (0.0,0.0,0.0,1.0),
		subtype = "XYZ",
		size = 4,
		)
	unknPos: FloatVectorProperty(
		name = "Unknown 1",
		description="Position Maybe (Always (0.0,0.0,0.0))",
		default = (0.0,0.0,0.0),
		subtype = "XYZ",
		)
	subDataList_items: CollectionProperty(type=ChainSettingSubDataPropertyGroup)
	subDataList_index: IntProperty(name="")
def getChainSettings(ChainSettingsData,targetObject,isChain2 = False):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chainsettings.id = ChainSettingsData.id
	targetObject.re_chain_chainsettings.colliderFilterInfoPath = str(ChainSettingsData.colliderFilterInfoPath)
	if not isChain2:
		targetObject.re_chain_chainsettings.sprayParameterArc = ChainSettingsData.sprayParameterArc
		targetObject.re_chain_chainsettings.sprayParameterFrequency = ChainSettingsData.sprayParameterFrequency
		targetObject.re_chain_chainsettings.sprayParameterCurve1 = ChainSettingsData.sprayParameterCurve1
		targetObject.re_chain_chainsettings.sprayParameterCurve2 = ChainSettingsData.sprayParameterCurve2
		targetObject.re_chain_chainsettings.chainType = str(ChainSettingsData.chainType)
		targetObject.re_chain_chainsettings.muzzleDirection = str(ChainSettingsData.muzzleDirection)
		targetObject.re_chain_chainsettings.shootingElasticLimitRate = ChainSettingsData.shootingElasticLimitRate
		targetObject.re_chain_chainsettings.muzzleVelocity = (ChainSettingsData.muzzleVelocityX,ChainSettingsData.muzzleVelocityY,ChainSettingsData.muzzleVelocityZ)
	else:
		targetObject.re_chain_chainsettings.motionForceCalcType = str(ChainSettingsData.motionForceCalcType)
		targetObject.re_chain_chainsettings.unknQuaternion = (ChainSettingsData.subDataUnkn0,ChainSettingsData.subDataUnkn1,ChainSettingsData.subDataUnkn2,ChainSettingsData.subDataUnkn3)
		targetObject.re_chain_chainsettings.unknPos = (ChainSettingsData.subDataUnkn4,ChainSettingsData.subDataUnkn5,ChainSettingsData.subDataUnkn6)
		for subData in ChainSettingsData.subDataList:
			newListItem = targetObject.re_chain_chainsettings.subDataList_items.add()
			newListItem.values = (subData.unkn0,subData.unkn1A,subData.unkn1B,subData.unkn1C,subData.unkn1D,subData.unkn2,subData.unkn3)
	targetObject.re_chain_chainsettings.settingsAttrFlags = ChainSettingsData.settingsAttrFlags
	
	targetObject.re_chain_chainsettings.gravity = (ChainSettingsData.gravityX,ChainSettingsData.gravityY,ChainSettingsData.gravityZ)
	
	targetObject.re_chain_chainsettings.damping = ChainSettingsData.damping
	targetObject.re_chain_chainsettings.secondDamping = ChainSettingsData.secondDamping
	targetObject.re_chain_chainsettings.secondDampingSpeed = ChainSettingsData.secondDampingSpeed
	targetObject.re_chain_chainsettings.minDamping = ChainSettingsData.minDamping
	targetObject.re_chain_chainsettings.secondMinDamping = ChainSettingsData.secondMinDamping
	targetObject.re_chain_chainsettings.dampingPow = ChainSettingsData.dampingPow
	targetObject.re_chain_chainsettings.secondDampingPow = ChainSettingsData.secondDampingPow
	targetObject.re_chain_chainsettings.collideMaxVelocity = ChainSettingsData.collideMaxVelocity
	targetObject.re_chain_chainsettings.springForce = ChainSettingsData.springForce
	targetObject.re_chain_chainsettings.springLimitRate = ChainSettingsData.springLimitRate
	targetObject.re_chain_chainsettings.springMaxVelocity = ChainSettingsData.springMaxVelocity
	targetObject.re_chain_chainsettings.springCalcType = str(ChainSettingsData.springCalcType)
	targetObject.re_chain_chainsettings.windDelayType = str(ChainSettingsData.windDelayType)
	targetObject.re_chain_chainsettings.reduceSelfDistanceRate = ChainSettingsData.reduceSelfDistanceRate
	targetObject.re_chain_chainsettings.secondReduceDistanceRate = ChainSettingsData.secondReduceDistanceRate
	targetObject.re_chain_chainsettings.secondReduceDistanceSpeed = ChainSettingsData.secondReduceDistanceSpeed
	targetObject.re_chain_chainsettings.friction = ChainSettingsData.friction
	targetObject.re_chain_chainsettings.shockAbsorptionRate = ChainSettingsData.shockAbsorptionRate
	targetObject.re_chain_chainsettings.coefOfElasticity = ChainSettingsData.coefOfElasticity
	targetObject.re_chain_chainsettings.coefOfExternalForces = ChainSettingsData.coefOfExternalForces
	targetObject.re_chain_chainsettings.stretchInteractionRatio = ChainSettingsData.stretchInteractionRatio
	targetObject.re_chain_chainsettings.angleLimitInteractionRatio = ChainSettingsData.angleLimitInteractionRatio
		
	targetObject.re_chain_chainsettings.groupDefaultAttr = ChainSettingsData.groupDefaultAttr

	targetObject.re_chain_chainsettings.windEffectCoef = ChainSettingsData.windEffectCoef
	targetObject.re_chain_chainsettings.velocityLimit = ChainSettingsData.velocityLimit
	targetObject.re_chain_chainsettings.hardness = ChainSettingsData.hardness
	targetObject.re_chain_chainsettings.windDelaySpeed = ChainSettingsData.windDelaySpeed
	targetObject.re_chain_chainsettings.envWindEffectCoef = ChainSettingsData.envWindEffectCoef
	targetObject.re_chain_chainsettings.motionForce = ChainSettingsData.motionForce

def setChainSettingsData(ChainSettingsData,targetObject,isChain2 = False):
	ChainSettingsData.id = targetObject.re_chain_chainsettings.id 
	ChainSettingsData.colliderFilterInfoPath = str(targetObject.re_chain_chainsettings.colliderFilterInfoPath) 
	if not isChain2:
		ChainSettingsData.sprayParameterArc = targetObject.re_chain_chainsettings.sprayParameterArc 
		ChainSettingsData.sprayParameterFrequency = targetObject.re_chain_chainsettings.sprayParameterFrequency 
		ChainSettingsData.sprayParameterCurve1 = targetObject.re_chain_chainsettings.sprayParameterCurve1 
		ChainSettingsData.sprayParameterCurve2 = targetObject.re_chain_chainsettings.sprayParameterCurve2 
		ChainSettingsData.chainType = int(targetObject.re_chain_chainsettings.chainType)
		ChainSettingsData.muzzleDirection = int(targetObject.re_chain_chainsettings.muzzleDirection)
		ChainSettingsData.muzzleVelocityX = targetObject.re_chain_chainsettings.muzzleVelocity[0]
		ChainSettingsData.muzzleVelocityY = targetObject.re_chain_chainsettings.muzzleVelocity[1]
		ChainSettingsData.muzzleVelocityZ = targetObject.re_chain_chainsettings.muzzleVelocity[2]
		ChainSettingsData.shootingElasticLimitRate = targetObject.re_chain_chainsettings.shootingElasticLimitRate 
	else:
		ChainSettingsData.motionForceCalcType = int(targetObject.re_chain_chainsettings.motionForceCalcType)
		ChainSettingsData.subDataUnkn0 = targetObject.re_chain_chainsettings.unknQuaternion[0]
		ChainSettingsData.subDataUnkn1 = targetObject.re_chain_chainsettings.unknQuaternion[1]
		ChainSettingsData.subDataUnkn2 = targetObject.re_chain_chainsettings.unknQuaternion[2]
		ChainSettingsData.subDataUnkn3 = targetObject.re_chain_chainsettings.unknQuaternion[3]
		ChainSettingsData.subDataUnkn4 = targetObject.re_chain_chainsettings.unknPos[0]
		ChainSettingsData.subDataUnkn5 = targetObject.re_chain_chainsettings.unknPos[1]
		ChainSettingsData.subDataUnkn6 = targetObject.re_chain_chainsettings.unknPos[2]
		ChainSettingsData.subDataList = []
		for item in targetObject.re_chain_chainsettings.subDataList_items:
			entry = Chain2SettingsSubData()
			#print(list(item.values))
			entry.unkn0 = item.values[0]
			entry.unkn1A = item.values[1]
			entry.unkn1B = item.values[2]
			entry.unkn1C = item.values[3]
			entry.unkn1D = item.values[4]
			entry.unkn2 = item.values[5]
			entry.unkn3 = item.values[6]
			ChainSettingsData.subDataList.append(entry)
		ChainSettingsData.subDataCount = len(ChainSettingsData.subDataList)
	ChainSettingsData.settingsAttrFlags = targetObject.re_chain_chainsettings.settingsAttrFlags
	
	
	ChainSettingsData.gravityX = targetObject.re_chain_chainsettings.gravity[0]
	ChainSettingsData.gravityY = targetObject.re_chain_chainsettings.gravity[1]
	ChainSettingsData.gravityZ = targetObject.re_chain_chainsettings.gravity[2]
	
	
	ChainSettingsData.damping = targetObject.re_chain_chainsettings.damping 
	ChainSettingsData.secondDamping = targetObject.re_chain_chainsettings.secondDamping 
	ChainSettingsData.secondDampingSpeed = targetObject.re_chain_chainsettings.secondDampingSpeed 
	ChainSettingsData.minDamping = targetObject.re_chain_chainsettings.minDamping 
	ChainSettingsData.secondMinDamping = targetObject.re_chain_chainsettings.secondMinDamping 
	ChainSettingsData.dampingPow = targetObject.re_chain_chainsettings.dampingPow 
	ChainSettingsData.secondDampingPow = targetObject.re_chain_chainsettings.secondDampingPow 
	ChainSettingsData.collideMaxVelocity = targetObject.re_chain_chainsettings.collideMaxVelocity 
	ChainSettingsData.springForce = targetObject.re_chain_chainsettings.springForce 
	ChainSettingsData.springLimitRate = targetObject.re_chain_chainsettings.springLimitRate 
	ChainSettingsData.springMaxVelocity = targetObject.re_chain_chainsettings.springMaxVelocity 
	ChainSettingsData.springCalcType = int(targetObject.re_chain_chainsettings.springCalcType)
	ChainSettingsData.windDelayType = int(targetObject.re_chain_chainsettings.windDelayType)
	ChainSettingsData.reduceSelfDistanceRate = targetObject.re_chain_chainsettings.reduceSelfDistanceRate 
	ChainSettingsData.secondReduceDistanceRate = targetObject.re_chain_chainsettings.secondReduceDistanceRate 
	ChainSettingsData.secondReduceDistanceSpeed = targetObject.re_chain_chainsettings.secondReduceDistanceSpeed 
	ChainSettingsData.friction = targetObject.re_chain_chainsettings.friction 
	ChainSettingsData.shockAbsorptionRate = targetObject.re_chain_chainsettings.shockAbsorptionRate 
	ChainSettingsData.coefOfElasticity = targetObject.re_chain_chainsettings.coefOfElasticity 
	ChainSettingsData.coefOfExternalForces = targetObject.re_chain_chainsettings.coefOfExternalForces 
	ChainSettingsData.stretchInteractionRatio = targetObject.re_chain_chainsettings.stretchInteractionRatio 
	ChainSettingsData.angleLimitInteractionRatio = targetObject.re_chain_chainsettings.angleLimitInteractionRatio 
	ChainSettingsData.groupDefaultAttr = targetObject.re_chain_chainsettings.groupDefaultAttr
	ChainSettingsData.windEffectCoef = targetObject.re_chain_chainsettings.windEffectCoef 
	ChainSettingsData.velocityLimit = targetObject.re_chain_chainsettings.velocityLimit 
	ChainSettingsData.hardness = targetObject.re_chain_chainsettings.hardness
	ChainSettingsData.windDelaySpeed = targetObject.re_chain_chainsettings.windDelaySpeed 
	ChainSettingsData.envWindEffectCoef = targetObject.re_chain_chainsettings.envWindEffectCoef 
	ChainSettingsData.motionForce = targetObject.re_chain_chainsettings.motionForce 
	if targetObject.parent.get("TYPE",None) == "RE_CHAIN_WINDSETTINGS":
		ChainSettingsData.windID = targetObject.parent.re_chain_windsettings.id
	else:
		ChainSettingsData.windID = 0
	
class chainSubGroupPropertyGroup(bpy.types.PropertyGroup):

	subGroupID: IntProperty(
		name = "Sub Group ID",
		description="",
		default = 1,
		)
	parentGroup: PointerProperty(
		name="Parent Chain Group",
		description = "Set the chain group that this subgroup belongs to",
		type=bpy.types.Object,
		poll = filterChainGroup
		)

class chainGroupPropertyGroup(bpy.types.PropertyGroup):

	rotationOrder: EnumProperty(
		name="Rotation Order",
		description="Apply Data to attribute.",
		items=[ ("0", "RotationOrder_XYZ", ""),
				("1", "RotationOrder_YZX", ""),
				("2", "RotationOrder_ZXY", ""),
				("3", "RotationOrder_ZYX", ""),
				("4", "RotationOrder_YXZ", ""),
				("5", "RotationOrder_XZY", ""),
			   ]
		)
	autoBlendCheckNodeNo: IntProperty(
		name = "Auto Blend Check Node Number",
		description="Auto Blend Check Node Number",#TODO Add description
		default = 0,
		)
	attrFlags: IntProperty(
		name="Attribute Flags",
		description="Controls how chain groups interact. Also affects whether nodes can collide",
		default = 0,
		)
	collisionFilterFlags: IntProperty(
		name="Collision Filter Flags",
		description="Controls how collisions will interact with surroundings",
		default = -1,
		)
	extraNodeLocalPos: FloatVectorProperty(
		name = "Extra Node Local Pos",
		description="For chain only",#TODO Add description
		default = (0.0,0.0,0.0),
		)
	tag0: IntProperty(
		name = "Tag 0",
		description="Tag 0\nVersion 35 and above only",#TODO Add description
		default = 0,
		)
	tag1: IntProperty(
		name = "Tag 1",
		description="Tag 1\nVersion 35 and above only",#TODO Add description
		default = 0,
		)
	tag2: IntProperty(
		name = "Tag 2",
		description="Tag 2\nVersion 35 and above only",#TODO Add description
		default = 0,
		)
	tag3: IntProperty(
		name = "Tag 3",
		description="Tag 3\nVersion 35 and above only",#TODO Add description
		default = 0,
		)
	hierarchyHash0: IntProperty(
		name = "Hierarchy Hash 0",
		description="Tag 0\nVersion 35 and above only",#TODO Add description
		default = 0,
		)
	hierarchyHash1: IntProperty(
		name = "Hierarchy Hash 1",
		description="Tag 1\nVersion 35 and above only",#TODO Add description
		default = 0,
		)
	hierarchyHash2: IntProperty(
		name = "Hierarchy Hash 2",
		description="Tag 2\nVersion 35 and above only",#TODO Add description
		default = 0,
		)
	hierarchyHash3: IntProperty(
		name = "Hierarchy Hash 3",
		description="Tag 3\nVersion 35 and above only",#TODO Add description
		default = 0,
		)
	dampingNoise0: FloatProperty(
		name = "Damping Noise 0",
		description = "Damping Noise 0\nVersion 35 and above only",#TODO Add description
		default = 0.00,
		)
	dampingNoise1: FloatProperty(
		name = "Damping Noise 1",
		description = "Damping Noise 1\nVersion 35 and above only",#TODO Add description
		default = 0.00,
		)
	endRotConstMax: FloatProperty(
		name = "End Rotation Constant Max",
		description = "End Rotation Constant Max\nVersion 35 and above only",#TODO Add description
		default = 0.00,
		)
	tagCount: IntProperty(
		name = "Tag Count",
		description="Tag Count\nVersion 35 and above only",#TODO Add description
		default = 0,
		)
	angleLimitDirectionMode: EnumProperty(
		name="Angle Limit Direction Mode",
		description="Apply Data to attribute.\nVersion 35 and above only",
		items=[ ("0", "AngleLimitDirectionMode_BasePose", ""),
				("1", "AngleLimitDirectionMode_MotionPose", ""),
			  ]
		)
	colliderQualityLevel: IntProperty(
		name = "Collider Quality Level",
		description="Version 48 and above only",#TODO Add description
		default = 0,
		)
	
	clspFlags0: IntProperty(
		name = "CLSP Flags A",
		description="Bitflag that determines what CLSP Tag Groups to collide with. -1 on files that don't use CLSP.\nVersion 52 and above only",#TODO Add description
		default = 0,
		)
	clspFlags1: IntProperty(
		name = "CLSP Flags B",
		description="Bitflag that determines what CLSP Tag Groups to collide with. -1 on files that don't use CLSP.\nVersion 52 and above only",#TODO Add description
		default = 0,
		)
	
	#Chain2
	interpCount: IntProperty(
		name = "Interpolation Count (chain2)",
		description="For chain2 only",
		default = 0,
		)
	nodeInterpolationMode: EnumProperty(
		name="Node Interpolation Mode (chain2)",
		description="For chain2 only",
		items=[ ("0", "NodeInterpolationMode_None", ""),
				("1", "NodeInterpolationMode_Linear", ""),
				("2", "NodeInterpolationMode_SplineLerp", ""),
				("3", "NodeInterpolationMode_FastSpline", ""),
			  ]
		)
def getChainGroup(ChainGroupData,targetObject,isChain2 = False):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chaingroup.rotationOrder = str(ChainGroupData.rotationOrder)
	targetObject.re_chain_chaingroup.autoBlendCheckNodeNo = ChainGroupData.autoBlendCheckNodeNo
	targetObject.re_chain_chaingroup.attrFlags = ChainGroupData.attrFlags
	if not isChain2:
		targetObject.re_chain_chaingroup.collisionFilterFlags = ChainGroupData.collisionFilterFlags
		targetObject.re_chain_chaingroup.extraNodeLocalPos = (ChainGroupData.extraNodeLocalPosX,ChainGroupData.extraNodeLocalPosY,ChainGroupData.extraNodeLocalPosZ)
	targetObject.re_chain_chaingroup.tag0 = ChainGroupData.tag0
	targetObject.re_chain_chaingroup.tag1 = ChainGroupData.tag1
	targetObject.re_chain_chaingroup.tag2 = ChainGroupData.tag2
	targetObject.re_chain_chaingroup.tag3 = ChainGroupData.tag3
	targetObject.re_chain_chaingroup.hierarchyHash0 = ChainGroupData.hierarchyHash0
	targetObject.re_chain_chaingroup.hierarchyHash1 = ChainGroupData.hierarchyHash1
	targetObject.re_chain_chaingroup.hierarchyHash2 = ChainGroupData.hierarchyHash2
	targetObject.re_chain_chaingroup.hierarchyHash3 = ChainGroupData.hierarchyHash3
	targetObject.re_chain_chaingroup.dampingNoise0 = ChainGroupData.dampingNoise0
	targetObject.re_chain_chaingroup.dampingNoise1 = ChainGroupData.dampingNoise1
	targetObject.re_chain_chaingroup.endRotConstMax = ChainGroupData.endRotConstMax
	targetObject.re_chain_chaingroup.tagCount = ChainGroupData.tagCount
	targetObject.re_chain_chaingroup.angleLimitDirectionMode = str(ChainGroupData.angleLimitDirectionMode)
	targetObject.re_chain_chaingroup.colliderQualityLevel = ChainGroupData.colliderQualityLevel
	targetObject.re_chain_chaingroup.clspFlags0 = ChainGroupData.clspFlags0
	targetObject.re_chain_chaingroup.clspFlags1 = ChainGroupData.clspFlags1
	if isChain2:
		targetObject.re_chain_chaingroup.interpCount = ChainGroupData.interpCount
		targetObject.re_chain_chaingroup.nodeInterpolationMode = str(ChainGroupData.nodeInterpolationMode)
	
	
def setChainGroupData(ChainGroupData,targetObject,isChain2 = False):
	ChainGroupData.rotationOrder = int(targetObject.re_chain_chaingroup.rotationOrder)
	ChainGroupData.autoBlendCheckNodeNo = targetObject.re_chain_chaingroup.autoBlendCheckNodeNo 
	ChainGroupData.attrFlags = targetObject.re_chain_chaingroup.attrFlags
	if not isChain2:
		ChainGroupData.collisionFilterFlags = targetObject.re_chain_chaingroup.collisionFilterFlags
		
		ChainGroupData.extraNodeLocalPosX = targetObject.re_chain_chaingroup.extraNodeLocalPos[0] 
		ChainGroupData.extraNodeLocalPosY = targetObject.re_chain_chaingroup.extraNodeLocalPos[1]
		ChainGroupData.extraNodeLocalPosZ = targetObject.re_chain_chaingroup.extraNodeLocalPos[2] 
	
	ChainGroupData.tag0 = targetObject.re_chain_chaingroup.tag0
	ChainGroupData.tag1 = targetObject.re_chain_chaingroup.tag1
	ChainGroupData.tag2 = targetObject.re_chain_chaingroup.tag2
	ChainGroupData.tag3 = targetObject.re_chain_chaingroup.tag3
	ChainGroupData.hierarchyHash0 = targetObject.re_chain_chaingroup.hierarchyHash0 
	ChainGroupData.hierarchyHash1 = targetObject.re_chain_chaingroup.hierarchyHash1 
	ChainGroupData.hierarchyHash2 = targetObject.re_chain_chaingroup.hierarchyHash2 
	ChainGroupData.hierarchyHash3 = targetObject.re_chain_chaingroup.hierarchyHash3 
	ChainGroupData.dampingNoise0 = targetObject.re_chain_chaingroup.dampingNoise0 
	ChainGroupData.dampingNoise1 = targetObject.re_chain_chaingroup.dampingNoise1 
	ChainGroupData.endRotConstMax = targetObject.re_chain_chaingroup.endRotConstMax 
	ChainGroupData.tagCount = targetObject.re_chain_chaingroup.tagCount 
	ChainGroupData.angleLimitDirectionMode = int(targetObject.re_chain_chaingroup.angleLimitDirectionMode)
	
	ChainGroupData.clspFlags0 = targetObject.re_chain_chaingroup.clspFlags0 
	ChainGroupData.clspFlags1 = targetObject.re_chain_chaingroup.clspFlags1
	
	if isChain2:
		ChainGroupData.interpCount = targetObject.re_chain_chaingroup.interpCount 
		ChainGroupData.nodeInterpolationMode = int(targetObject.re_chain_chaingroup.nodeInterpolationMode)
		
	if targetObject.parent.get("TYPE",None) == "RE_CHAIN_WINDSETTINGS":
		ChainGroupData.windID = targetObject.parent.re_chain_windsettings.id
		
	elif targetObject.parent.parent.get("TYPE",None) == "RE_CHAIN_WINDSETTINGS":
		ChainGroupData.windID = targetObject.parent.parent.re_chain_windsettings.id
		
	else:
		ChainGroupData.windID = 0


class chainNodePropertyGroup(bpy.types.PropertyGroup):
	angleLimitRad: FloatProperty(
		name = "Angle Limit Radius",
		description = "The amount the node is allowed to rotate from it's angle limit direction",
		default = 0.0,
		soft_min=0.0,
		soft_max=180.0,
        subtype = "ANGLE",
		update = update_AngleLimitRad
		)
	angleLimitDistance: FloatProperty(
		name = "Angle Limit Distance",
		description = "Angle Limit Distance",#TODO Add description
		default = 0.00,
		)
	angleLimitRestitution: FloatProperty(
		name = "Angle Limit Restitution",
		description = "Angle Limit Restitution",#TODO Add description
		default = 0.00,
		)
	angleLimitRestituteStopSpeed: FloatProperty(
		name = "Angle Limit Restitute Stop Speed",
		description = "Angle Limit Restitute Stop Speed",#TODO Add description
		default = 0.00,
		)
	collisionRadius: FloatProperty(
		name = "Collision Radius",
		description = "Collision Radius",#TODO Add description
		default = 0.00,
		update=update_NodeRadius,
		step = .1,
		soft_min = 0.00
		)
	collisionFilterFlags: IntProperty(
		name="Collision Filter Flags",
		description="Controls how collisions will interact with surroundings",
		default = -1,
		)
	capsuleStretchRate0: FloatProperty(
		name = "Capsule Stretch Rate 0",
		description = "Capsule Stretch Rate 0",#TODO Add description
		default = 0.00,
		soft_min=0.000,
		soft_max=1.000
		)
	capsuleStretchRate1: FloatProperty(
		name = "Capsule Stretch Rate 1",
		description = "Capsule Stretch Rate 1",#TODO Add description
		default = 0.00,
		soft_min=0.000,
		soft_max=1.000
		)
	attrFlags: IntProperty(
		name="Attribute Flags",
		description="Controls how chain groups interact. Also affects whether nodes can collide",
		default = 0,
		)
	windCoef: FloatProperty(
		name = "Wind Coefficient",
		description = "Wind Coefficient",#TODO Add description
		default = 1.0,
		soft_min=0.000,
		soft_max=20.000
		)
	angleMode: EnumProperty(
		name="Angle Mode",
		description="Apply Data to attribute.",
		items=[ ("0", "AngleMode_Free", "Any Direction"),
				("1", "AngleMode_LimitCone", "Limit Node Direction to Cone"),
				("2", "AngleMode_LimitHinge", "Hinge on Z Axis"),
				("3", "AngleMode_LimitConeBox", ""),
				("4", "AngleMode_LimitOval", "Y Axis Compressed"),
				("5", "AngleMode_LimitElliptic", "Z Axis Compressed"),
			   ],
		update = update_AngleLimitMode
		)
		
	collisionShape: EnumProperty(
		name="Collision Shape",
		description="Apply Data to attribute.",
		items=[ ("0", "ChainNodeCollisionShape_None", ""),
				("1", "ChainNodeCollisionShape_Sphere", ""),
				("2", "ChainNodeCollisionShape_Capsule", ""),
				("3", "ChainNodeCollisionShape_StretchCapsule", ""),
			   ]
		)
	attachType: IntProperty(
		name = "Attach Type",
		description="Attach Type",#TODO Add description
		default = 0,
		)
	rotationType: IntProperty(
		name = "Rotation Type",
		description="Rotation Type",#TODO Add description
		default = 0,
		)
	gravityCoef: FloatProperty(
		name = "Gravity Coefficient",
		description="Version 35 and above only",#TODO Add description
		default = 1.0,
		)
	
	constraintJntName: StringProperty(
		name="Constraint Joint Name",
		description="Constraint joint, if the bone is not on the armature when the chain is imported, this will be an integer hash value",
		default = "",
		)
	
	#chain2
	jointHash: StringProperty(
		name = "Joint Name Hash (chain2)",
		description="The default value is a hash of a string that seems to mean None.\nIf a string is entered into this field, it will be hashed upon export",
		default = "2180083513",
		)
	basePos: FloatVectorProperty(
		name = "Base Position (chain2)",
		description="For chain2 files only",#TODO Add description
		default = (0.0,0.0,0.0),
		subtype = "XYZ",
		)
	
def getChainNode(ChainNodeData,targetObject,isChain2 = False):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chainnode.angleLimitRad = ChainNodeData.angleLimitRad
	targetObject.re_chain_chainnode.angleLimitDistance = ChainNodeData.angleLimitDistance
	targetObject.re_chain_chainnode.angleLimitRestitution = ChainNodeData.angleLimitRestitution
	targetObject.re_chain_chainnode.angleLimitRestituteStopSpeed = ChainNodeData.angleLimitRestituteStopSpeed
	targetObject.re_chain_chainnode.collisionRadius = ChainNodeData.collisionRadius
	targetObject.re_chain_chainnode.collisionFilterFlags = ChainNodeData.collisionFilterFlags
	targetObject.re_chain_chainnode.capsuleStretchRate0 = ChainNodeData.capsuleStretchRate0
	targetObject.re_chain_chainnode.capsuleStretchRate1 = ChainNodeData.capsuleStretchRate1
	targetObject.re_chain_chainnode.attrFlags = ChainNodeData.attrFlags
	targetObject.re_chain_chainnode.windCoef = ChainNodeData.windCoef
	targetObject.re_chain_chainnode.angleMode = str(ChainNodeData.angleMode)
	targetObject.re_chain_chainnode.collisionShape = str(ChainNodeData.collisionShape)
	targetObject.re_chain_chainnode.attachType = ChainNodeData.attachType
	targetObject.re_chain_chainnode.rotationType = ChainNodeData.rotationType
	targetObject.re_chain_chainnode.gravityCoef = ChainNodeData.gravityCoef
	if isChain2:
		targetObject.re_chain_chainnode.basePos = ChainNodeData.basePos
	
def setChainNodeData(ChainNodeData,targetObject, isChain2 = False):
	ChainNodeData.angleLimitRad = targetObject.re_chain_chainnode.angleLimitRad 
	ChainNodeData.angleLimitDistance = targetObject.re_chain_chainnode.angleLimitDistance 
	ChainNodeData.angleLimitRestitution = targetObject.re_chain_chainnode.angleLimitRestitution 
	ChainNodeData.angleLimitRestituteStopSpeed = targetObject.re_chain_chainnode.angleLimitRestituteStopSpeed 
	ChainNodeData.collisionRadius = targetObject.re_chain_chainnode.collisionRadius * targetObject.scale[0]
	ChainNodeData.collisionFilterFlags = targetObject.re_chain_chainnode.collisionFilterFlags
	ChainNodeData.capsuleStretchRate0 = targetObject.re_chain_chainnode.capsuleStretchRate0 
	ChainNodeData.capsuleStretchRate1 = targetObject.re_chain_chainnode.capsuleStretchRate1 
	ChainNodeData.attrFlags = int(targetObject.re_chain_chainnode.attrFlags)
	ChainNodeData.windCoef = targetObject.re_chain_chainnode.windCoef 
	ChainNodeData.angleMode = int(targetObject.re_chain_chainnode.angleMode)
	ChainNodeData.collisionShape = int(targetObject.re_chain_chainnode.collisionShape)
	ChainNodeData.attachType = targetObject.re_chain_chainnode.attachType 
	ChainNodeData.rotationType = targetObject.re_chain_chainnode.rotationType
	ChainNodeData.gravityCoef = targetObject.re_chain_chainnode.gravityCoef

	for child in targetObject.children:
		if child.get("TYPE",None) == "RE_CHAIN_NODE_FRAME":
			frame = child
	frame.rotation_mode = "QUATERNION"#Have to set rotation mode to quaternion in case euler rotation is used, rotation wouldn't export properly in that case
	ChainNodeData.angleLimitDirectionX = frame.rotation_quaternion[1]
	ChainNodeData.angleLimitDirectionY = frame.rotation_quaternion[2]
	ChainNodeData.angleLimitDirectionZ = frame.rotation_quaternion[3]
	ChainNodeData.angleLimitDirectionW = frame.rotation_quaternion[0]
	frame.rotation_mode = "XYZ"
	if isChain2:
		ChainNodeData.basePos = (targetObject.re_chain_chainnode.basePos[0],targetObject.re_chain_chainnode.basePos[1],targetObject.re_chain_chainnode.basePos[2])
class chainJigglePropertyGroup(bpy.types.PropertyGroup):
	'''range: FloatVectorProperty(
		name = "Jiggle Range",
		description="Jiggle Range",#TODO Add description
		#default = (0.0,0.0,0.0),
		step = .1,
		subtype = "XYZ",
		)
	rangeOffset: FloatVectorProperty(
		name = "Jiggle Range Offset",
		description="Jiggle Range Offset",#TODO Add description
		#default = (0.0,0.0,0.0),
		step = .1,
		subtype = "XYZ"
		)
	rangeAxis: FloatVectorProperty(
		name = "Jiggle Range Axis",
		description="Jiggle Range Axis",#TODO Add description
		#default = (0.0,0.0,0.0,1.0),
		step = .1,
		subtype = "QUATERNION"
		)'''
	rangeShape: EnumProperty(
		name="Collision Shape",
		description="Apply Data to attribute.",
		items=[ ("0", "ChainJiggleRangeShape_None", ""),
				("1", "ChainJiggleRangeShape_OBB", ""),
				("2", "ChainJiggleRangeShape_Sphere", ""),
				("3", "ChainJiggleRangeShape_Cone", ""),
			   ]
		)
	springForce: FloatProperty(
		name = "Spring Force",
		description = "Jiggle Spring Force",#TODO Add description
		default = 0.00,
		soft_min=0.000,
		soft_max=1.000
		)
	gravityCoef: FloatProperty(
		name = "Gravity Coefficient",
		description = "Jiggle Gravity Coefficient",#TODO Add description
		default = 0.00,
		soft_min=0.000,
		soft_max=1.000
		)
	damping: FloatProperty(
		name = "Damping",
		description = "Jiggle Damping",#TODO Add description
		default = 0.00,
		soft_min=0.000,
		soft_max=1.000
		)
	attrFlags: IntProperty(
		name="Attribute Flags",
		description="Controls how chain groups interact. Also affects whether nodes can collide",
		default = 0,
		)
	windCoef: FloatProperty(
		name = "Wind Coefficient",
		description = "Wind Coefficient",#TODO Add description
		default = 0.00,
		soft_min=0.000,
		soft_max=1.000
		)
def getChainJiggle(ChainJiggleData,targetObject):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chainjiggle.rangeShape = str(ChainJiggleData.rangeShape)
	targetObject.re_chain_chainjiggle.springForce = ChainJiggleData.springForce
	targetObject.re_chain_chainjiggle.gravityCoef = ChainJiggleData.gravityCoef
	targetObject.re_chain_chainjiggle.damping = ChainJiggleData.damping
	targetObject.re_chain_chainjiggle.attrFlags = ChainJiggleData.attrFlags
	targetObject.re_chain_chainjiggle.windCoef = ChainJiggleData.windCoef
	

def setChainJiggleData(ChainJiggleData,targetObject):
	ChainJiggleData.rangeX = targetObject.scale[0]
	ChainJiggleData.rangeY = targetObject.scale[1]
	ChainJiggleData.rangeZ = targetObject.scale[2]

	ChainJiggleData.rangeOffsetX = targetObject.location[0]
	ChainJiggleData.rangeOffsetY = targetObject.location[1]
	ChainJiggleData.rangeOffsetZ = targetObject.location[2]

	ChainJiggleData.rangeAxisX = targetObject.rotation_quaternion[1]
	ChainJiggleData.rangeAxisY = targetObject.rotation_quaternion[2]
	ChainJiggleData.rangeAxisZ = targetObject.rotation_quaternion[3]
	ChainJiggleData.rangeAxisW = targetObject.rotation_quaternion[0]

	ChainJiggleData.rangeShape = int(targetObject.re_chain_chainjiggle.rangeShape)
	ChainJiggleData.springForce = targetObject.re_chain_chainjiggle.springForce
	ChainJiggleData.gravityCoef = targetObject.re_chain_chainjiggle.gravityCoef
	ChainJiggleData.damping = targetObject.re_chain_chainjiggle.damping
	ChainJiggleData.attrFlags = targetObject.re_chain_chainjiggle.attrFlags
	ChainJiggleData.windCoef = targetObject.re_chain_chainjiggle.windCoef

class collisionSubDataPropertyGroup(bpy.types.PropertyGroup):
	pos: FloatVectorProperty(
		name = "Collision Offset",
		description="Set the positional offset of the collision from the bone",
		#default = (0.0,0.0,0.0),
		step = .1,
		subtype = "XYZ",
		)
	pairPos: FloatVectorProperty(
		name = "End Collision Offset",
		description="Set the collision offset from the end bone for collision capsules",
		#default = (0.0,0.0,0.0),
		step = .1,
		subtype = "XYZ",
		)
	rotOffset: FloatVectorProperty(
		name = "Rotation Offset",
		description="Set collision rotation (Quaternion)",
		#default = (1.0,0.0,0.0),
		size = 4,
		subtype = "QUATERNION",
		)
	radius: FloatProperty(
		name = "Radius",
		description = "Radius",#TODO Add description
		default = 0.00,
		update = update_CollisionRadius,
		step = .1,
		soft_min = 0.00
		)
	id: IntProperty(
		name = "ID",
		description = "Unknown Collision Value",#TODO Add description
		default = 0,
		)
	unknSubCollisionData0: IntProperty(
		name = "Unknown Collision Sub Data 0",
		description = "Unknown Collision Value",#TODO Add description
		default = 0,
		)
	unknSubCollisionData1: IntProperty(
		name = "Unknown Collision Sub Data 1",
		description = "Unknown Collision Value",#TODO Add description
		default = 0,
		)
	unknSubCollisionData2: IntProperty(
		name = "Unknown Collision Sub Data 2",
		description = "Unknown Collision Value",#TODO Add description
		default = 0,
		)
	unknSubCollisionData3: IntProperty(
		name = "Unknown Collision Sub Data 3",
		description = "Unknown Collision Value",#TODO Add description
		default = 0,
		)

class chainCollisionPropertyGroup(bpy.types.PropertyGroup):
	rotationOrder: EnumProperty(
		name="Rotation Order",
		description="Apply Data to attribute.\nVersion 48 and above only",
		items=[ ("0", "RotationOrder_XYZ", ""),
				("1", "RotationOrder_YZX", ""),
				("2", "RotationOrder_ZXY", ""),
				("3", "RotationOrder_ZYX", ""),
				("4", "RotationOrder_YXZ", ""),
				("5", "RotationOrder_XZY", ""),
			   ]
		)
	collisionOffset: FloatVectorProperty(
		name = "Collision Offset",
		description="Set the positional offset of the collision from the bone",
		#default = (0.0,0.0,0.0),
		step = .1,
		subtype = "XYZ",
		update = update_CollisionOffset
		)
	endCollisionOffset: FloatVectorProperty(
		name = "End Collision Offset",
		description="Set the collision offset from the end bone for collision capsules",
		#default = (0.0,0.0,0.0),
		step = .1,
		subtype = "XYZ",
		update = update_EndCollisionOffset
		)
	radius: FloatProperty(
		name = "Radius",
		description = "Radius",#TODO Add description
		default = 0.00,
		update = update_CollisionRadius,
		step = .1,
		soft_min = 0.00
		)
	endRadius: FloatProperty(
		name = "End Radius",
		description = "Radius of end of capsule. Collision shape must be set to tapered capsule for this to do anything\nVersion 46 and above only",#TODO Add description
		default = 0.00,
		update = update_EndCollisionRadius,
		step = .1,
		soft_min = 0.00
		)
	lerp: FloatProperty(
		name = "Lerp",
		description = "Lerp",#TODO Add description
		default = 0.00,
		)
	chainCollisionShape: EnumProperty(
		name="Chain Collision Shape",
		description="Apply Data to attribute.",
		items=[ ("0", "ChainCollisionShape_None", ""),
				("1", "ChainCollisionShape_Sphere", ""),
				("2", "ChainCollisionShape_Capsule", ""),
				("3", "ChainCollisionShape_OBB", ""),
				("4", "ChainCollisionShape_Plane", ""),
				("5", "ChainCollisionShape_TaperedCapsule", ""),
				("6", "ChainCollisionShape_LineSphere", ""),
				("7", "ChainCollisionShape_LerpSphere", ""),
			   ]
		)
	subDataCount: IntProperty(
		name = "Sub Data Count",
		description = "Sub Data Count",#TODO Add description
		default = 0,
		min = 0,
		max = 1,#Max shouldn't be 1 but I would have to rewrite the way subdata works otherwise. Barely anything has a subdata count of more than 1 so I don't think it matters
		)
	collisionFilterFlags: IntProperty(
		name="Collision Filter Flags",
		description="Controls how collisions will interact with surroundings",
		default = -1,
		)
	"""
	subDataFlag: IntProperty(
		name = "Use Sub Data Flag",
		description = "Set to 1 to enable subdata",
		default = -1,
		min = -1,
		max = 1,
		)
	"""
	
	#CLSP
	clspBitFlag0: IntProperty(
		name = "CLSP BitFlag A",
		description = "Flags for exported .clsp files, has no effect on chain files",#TODO Add description
		default = 0,
		)
	clspBitFlag1: IntProperty(
		name = "CLSP BitFlag B",
		description = "Flags for exported .clsp files, has no effect on chain files",#TODO Add description
		default = 0,
		)

def getChainCollision(ChainCollisionData,targetObject,isChain2 = False):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chaincollision.rotationOrder = str(ChainCollisionData.rotationOrder)
	targetObject.re_chain_chaincollision.radius = ChainCollisionData.radius
	targetObject.re_chain_chaincollision.endRadius = ChainCollisionData.endRadius
	targetObject.re_chain_chaincollision.lerp = ChainCollisionData.lerp
	targetObject.re_chain_chaincollision.chainCollisionShape = str(ChainCollisionData.chainCollisionShape)
	targetObject.re_chain_chaincollision.subDataCount = ChainCollisionData.subDataCount
	targetObject.re_chain_chaincollision.collisionFilterFlags = ChainCollisionData.collisionFilterFlags
	
	if ChainCollisionData.subDataCount >= 1:
		targetObject.re_chain_collision_subdata.pos = (ChainCollisionData.subData.posX,ChainCollisionData.subData.posY,ChainCollisionData.subData.posZ)
		targetObject.re_chain_collision_subdata.pairPos = (ChainCollisionData.subData.pairPosX,ChainCollisionData.subData.pairPosY,ChainCollisionData.subData.pairPosZ)
		targetObject.re_chain_collision_subdata.rotOffset = (ChainCollisionData.subData.rotOffsetW,ChainCollisionData.subData.rotOffsetX,ChainCollisionData.subData.rotOffsetY,ChainCollisionData.subData.rotOffsetZ)
		targetObject.re_chain_collision_subdata.radius = ChainCollisionData.subData.radius
		targetObject.re_chain_collision_subdata.id = ChainCollisionData.subData.id
		targetObject.re_chain_collision_subdata.unknSubCollisionData0 = ChainCollisionData.subData.unknSubCollisionData0
		targetObject.re_chain_collision_subdata.unknSubCollisionData1 = ChainCollisionData.subData.unknSubCollisionData1
		targetObject.re_chain_collision_subdata.unknSubCollisionData2 = ChainCollisionData.subData.unknSubCollisionData2
		targetObject.re_chain_collision_subdata.unknSubCollisionData3 = ChainCollisionData.subData.unknSubCollisionData3

def setChainCollisionData(ChainCollisionData,targetObject,isChain2 = False):
	ChainCollisionData.rotationOrder = int(targetObject.re_chain_chaincollision.rotationOrder)
	ChainCollisionData.radius = targetObject.scale[0]
	ChainCollisionData.endRadius = targetObject.re_chain_chaincollision.endRadius
	ChainCollisionData.lerp = targetObject.re_chain_chaincollision.lerp
	ChainCollisionData.chainCollisionShape = int(targetObject.re_chain_chaincollision.chainCollisionShape)
	ChainCollisionData.subDataCount = targetObject.re_chain_chaincollision.subDataCount 
	ChainCollisionData.collisionFilterFlags = targetObject.re_chain_chaincollision.collisionFilterFlags
	
	
	
	#ChainCollisionData.posX = targetObject.re_chain_chaincollision.collisionOffset[0]
	#ChainCollisionData.posY = targetObject.re_chain_chaincollision.collisionOffset[1]
	#ChainCollisionData.posZ = targetObject.re_chain_chaincollision.collisionOffset[2]
	ChainCollisionData.posX = targetObject.location[0]
	ChainCollisionData.posY = targetObject.location[1]
	ChainCollisionData.posZ = targetObject.location[2]
	
	ChainCollisionData.pairPosX = targetObject.re_chain_chaincollision.endCollisionOffset[0]
	ChainCollisionData.pairPosY = targetObject.re_chain_chaincollision.endCollisionOffset[1]
	ChainCollisionData.pairPosZ = targetObject.re_chain_chaincollision.endCollisionOffset[2]
	if targetObject.get("TYPE",None) != "RE_CHAIN_COLLISION_CAPSULE_ROOT":
		ChainCollisionData.jointNameHash = hash_wide(targetObject.constraints["BoneName"].subtarget)		
		ChainCollisionData.rotOffsetX = targetObject.rotation_quaternion[1]
		ChainCollisionData.rotOffsetY = targetObject.rotation_quaternion[2]
		ChainCollisionData.rotOffsetZ = targetObject.rotation_quaternion[3]
		ChainCollisionData.rotOffsetW = targetObject.rotation_quaternion[0]
		targetObject.re_chain_chaincollision.collisionOffset = targetObject.location
		targetObject.re_chain_chaincollision.radius = targetObject.scale[0]
	else:
		startCapsule = None
		endCapsule = None
		for child in targetObject.children: 
			if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
				startCapsule = child
			elif child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
				endCapsule = child
				
		if startCapsule != None:
			ChainCollisionData.radius = startCapsule.scale[0]
			boneName = startCapsule.constraints["BoneName"].subtarget
			if boneName.startswith("b") and ":" in boneName:
				boneName = boneName.split(":",1)[1]
			ChainCollisionData.jointNameHash = hash_wide(boneName)		
			ChainCollisionData.rotOffsetX = startCapsule.rotation_quaternion[1]
			ChainCollisionData.rotOffsetY = startCapsule.rotation_quaternion[2]
			ChainCollisionData.rotOffsetZ = startCapsule.rotation_quaternion[3]
			ChainCollisionData.rotOffsetW = startCapsule.rotation_quaternion[0]
			ChainCollisionData.posX = startCapsule.location[0]
			ChainCollisionData.posY = startCapsule.location[1]
			ChainCollisionData.posZ = startCapsule.location[2]
			#Update UI value if the user moved the collision via the grab tool
			targetObject.re_chain_chaincollision.collisionOffset = startCapsule.location
			targetObject.re_chain_chaincollision.radius = startCapsule.scale[0]
		if endCapsule != None:
			if ChainCollisionData.chainCollisionShape == 5:
				ChainCollisionData.endRadius = endCapsule.scale[0]
				targetObject.re_chain_chaincollision.endRadius = endCapsule.scale[0]
			boneName = endCapsule.constraints["BoneName"].subtarget
			if boneName.startswith("b") and ":" in boneName:
				boneName = boneName.split(":",1)[1]
			ChainCollisionData.pairJointNameHash = hash_wide(boneName)
			ChainCollisionData.pairPosX = endCapsule.location[0]
			ChainCollisionData.pairPosY = endCapsule.location[1]
			ChainCollisionData.pairPosZ = endCapsule.location[2]
			#Update UI value if the user moved the collision via the grab tool
			targetObject.re_chain_chaincollision.endCollisionOffset = endCapsule.location
		else:
			ChainCollisionData.pairPosX = 0.0
			ChainCollisionData.pairPosY = 0.0
			ChainCollisionData.pairPosZ = 0.0
			ChainCollisionData.pairJointNameHash = 0
	
	ChainCollisionData.subDataCount = targetObject.re_chain_chaincollision.subDataCount
	if targetObject.re_chain_chaincollision.subDataCount:
		ChainCollisionData.subData.posX = targetObject.re_chain_collision_subdata.pos[0]
		ChainCollisionData.subData.posY = targetObject.re_chain_collision_subdata.pos[1]
		ChainCollisionData.subData.posZ = targetObject.re_chain_collision_subdata.pos[2]
		ChainCollisionData.subData.pairPosX = targetObject.re_chain_collision_subdata.pairPos[0]
		ChainCollisionData.subData.pairPosY = targetObject.re_chain_collision_subdata.pairPos[1]
		ChainCollisionData.subData.pairPosZ = targetObject.re_chain_collision_subdata.pairPos[2]
		ChainCollisionData.subData.rotOffsetX = targetObject.re_chain_collision_subdata.rotOffset[1]
		ChainCollisionData.subData.rotOffsetY = targetObject.re_chain_collision_subdata.rotOffset[2]
		ChainCollisionData.subData.rotOffsetZ = targetObject.re_chain_collision_subdata.rotOffset[3]
		ChainCollisionData.subData.rotOffsetW = targetObject.re_chain_collision_subdata.rotOffset[0]
		ChainCollisionData.subData.radius = targetObject.re_chain_collision_subdata.radius
		ChainCollisionData.subData.id = targetObject.re_chain_collision_subdata.id
		ChainCollisionData.subData.unknSubCollisionData0 = targetObject.re_chain_collision_subdata.unknSubCollisionData0
		ChainCollisionData.subData.unknSubCollisionData1 = targetObject.re_chain_collision_subdata.unknSubCollisionData1
		ChainCollisionData.subData.unknSubCollisionData2 = targetObject.re_chain_collision_subdata.unknSubCollisionData2
		ChainCollisionData.subData.unknSubCollisionData3 = targetObject.re_chain_collision_subdata.unknSubCollisionData3

class chainLinkCollisionNodePropertyGroup(bpy.types.PropertyGroup):
	collisionRadius: FloatProperty(
		name = "Collision Radius",
		description = "Collision Radius",#TODO Add description
		default = 0.01,
		min=0.000,
		step = 0.01,
		update = update_ChainLinkCollisionRadius
		)
	collisionFilterFlags: IntProperty(
		name="Collision Filter Flags",
		description="Controls how collisions will interact with surroundings",
		default = 4,
		)

def getChainLinkCollisionNode(ChainLinkNodeData,targetObject,isChain2 = False):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chainlink.collisionRadius = ChainLinkNodeData.collisionRadius
	targetObject.re_chain_chainlink.collisionFilterFlags = ChainLinkNodeData.collisionFilterFlags
	

def setChainLinkCollisionNodeData(ChainLinkNodeData,targetObject,isChain2 = False):
	#TODO get chain group links
	ChainLinkNodeData.collisionRadius = targetObject.re_chain_chainlink_collision.collisionRadius 
	ChainLinkNodeData.collisionFilterFlags = targetObject.re_chain_chainlink_collision.collisionFilterFlags 

class chainLinkPropertyGroup(bpy.types.PropertyGroup):
	chainGroupAObject: StringProperty(
		name = "Chain Group A",
		description = "Chain Group A",#TODO Add description
		default = "",
		update = update_ChainGroupA
		)
	chainGroupBObject: StringProperty(
		name = "Chain Group B",
		description = "Chain Group B",#TODO Add description
		default = "",
		update = update_ChainGroupB
		)
	
	distanceShrinkLimitCoef: FloatProperty(
		name = "Distance Shrink Limit Coefficient",
		description = "Distance Shrink Limit Coefficient",#TODO Add description
		default = 0.5,
		)
	distanceExpandLimitCoef: FloatProperty(
		name = "Distance Expand Limit Coefficient",
		description = "Distance Expand Limit Coefficient",#TODO Add description
		default = 1.00,
		)
	linkMode: EnumProperty(
		name="Link Mode",
		description="Apply Data to attribute.",
		items=[ ("0", "LinkMode_TopToBottom", ""),
				("1", "LinkMode_BottomToTop", ""),
				("2", "LinkMode_Manual", ""),
			   ]
		)
	connectFlags: EnumProperty(
		name="Connection Flags",
		description="Apply Data to attribute.",
		items=[ ("1", "ConnectionFlags_Neighbour", ""),
				("2", "ConnectionFlags_Upper", ""),
				("4", "ConnectionFlags_Bottom", ""),
				("7", "ConnectionFlags_UNKNOWNFLAG_7", ""),
			   ]
		)
	linkAttrFlags: EnumProperty(
		name="Link Attribute Flags",
		description="Apply Data to attribute.",
		items=[ ("0", "AttrFlags_Null", ""),
				("1", "AttrFlags_EnableStretch", ""),
			   ]
		)
	skipGroupA: IntProperty(
		name = "Skip Group A",
		description = "Skip Group A",#TODO Add description
		default = 0,
		)
	skipGroupB: IntProperty(
		name = "Skip Group B",
		description = "Skip Group B",#TODO Add description
		default = 0,
		)
	linkOrder: EnumProperty(
		name="Link Rotation Order",
		description="Apply Data to attribute.",
		items=[ ("0", "RotationOrder_XYZ", ""),
				("1", "RotationOrder_YZX", ""),
				("2", "RotationOrder_ZXY", ""),
				("3", "RotationOrder_ZYX", ""),
				("4", "RotationOrder_YXZ", ""),
				("5", "RotationOrder_XZY", ""),
			   ]
		)
def getChainLink(ChainLinkData,targetObject,isChain2 = False):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chainlink.distanceShrinkLimitCoef = ChainLinkData.distanceShrinkLimitCoef
	targetObject.re_chain_chainlink.distanceExpandLimitCoef = ChainLinkData.distanceExpandLimitCoef
	targetObject.re_chain_chainlink.linkMode = str(ChainLinkData.linkMode)
	targetObject.re_chain_chainlink.connectFlags = str(ChainLinkData.connectFlags)
	targetObject.re_chain_chainlink.linkAttrFlags = str(ChainLinkData.linkAttrFlags)
	targetObject.re_chain_chainlink.skipGroupA = ChainLinkData.skipGroupA
	targetObject.re_chain_chainlink.skipGroupB = ChainLinkData.skipGroupB
	targetObject.re_chain_chainlink.linkOrder = str(ChainLinkData.linkOrder)
	

def setChainLinkData(ChainLinkData,targetObject,isChain2 = False):
	#TODO get chain group links
	ChainLinkData.distanceShrinkLimitCoef = targetObject.re_chain_chainlink.distanceShrinkLimitCoef 
	ChainLinkData.distanceExpandLimitCoef = targetObject.re_chain_chainlink.distanceExpandLimitCoef 
	ChainLinkData.linkMode = int(targetObject.re_chain_chainlink.linkMode) 
	ChainLinkData.connectFlags = int(targetObject.re_chain_chainlink.connectFlags)
	ChainLinkData.linkAttrFlags = int(targetObject.re_chain_chainlink.linkAttrFlags)
	ChainLinkData.skipGroupA = targetObject.re_chain_chainlink.skipGroupA 
	ChainLinkData.skipGroupB = targetObject.re_chain_chainlink.skipGroupB 
	ChainLinkData.linkOrder = int(targetObject.re_chain_chainlink.linkOrder)
	
		
class chainClipboardPropertyGroup(bpy.types.PropertyGroup):
	re_chain_type : StringProperty(default="NONE", options={'HIDDEN'})
	re_chain_type_name : StringProperty(default="None", options={'HIDDEN'})
	re_chain_header : PointerProperty(type=chainHeaderPropertyGroup)
	re_chain_windsettings : PointerProperty(type=chainWindSettingsPropertyGroup)
	re_chain_chainsettings : PointerProperty(type=chainSettingsPropertyGroup)
	re_chain_chaingroup : PointerProperty(type=chainGroupPropertyGroup)
	re_chain_chainsubgroup : PointerProperty(type=chainSubGroupPropertyGroup)
	re_chain_chainnode : PointerProperty(type=chainNodePropertyGroup)
	re_chain_chainjiggle : PointerProperty(type=chainJigglePropertyGroup)
	re_chain_collision_subdata : PointerProperty(type=collisionSubDataPropertyGroup)
	re_chain_chaincollision : PointerProperty(type=chainCollisionPropertyGroup)
	re_chain_chainlink : PointerProperty(type=chainLinkPropertyGroup)
	re_chain_chainlink_collision : PointerProperty(type=chainLinkCollisionNodePropertyGroup)
	frameOrientation: FloatVectorProperty(
		name = "Frame Orientation",
		size = 3,
		subtype = "XYZ"
		)