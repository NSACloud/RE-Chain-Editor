#Author: NSA Cloud
import bpy
from bpy.props import (StringProperty,
					   BoolProperty,
					   IntProperty,
					   FloatProperty,
					   FloatVectorProperty,
					   EnumProperty,
					   PointerProperty,
					   )


from .pymmh3 import hash_wide

from .re_chain_presets import reloadPresets

#V2 - Removed AttrFlags enum, replaced with a pseudo enum using int value and operator due to large variations in values

def update_angleLimitSize(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_NODE_FRAME":
			obj.empty_display_size = self.angleLimitDisplaySize

def update_angleLimitConeVis(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_NODE_FRAME_HELPER":
			obj.hide_viewport = not self.showAngleLimitCones

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
					xScaleModifier = .5
				elif nodeObj.re_chain_chainnode.angleMode == "5":#Limit elliptic angle mode
					yScaleModifier = .5
			obj.scale = (self.coneDisplaySize*xScaleModifier,self.coneDisplaySize*yScaleModifier,self.coneDisplaySize*zScaleModifier)


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
								xScaleModifier = .5
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
							frameChild.data.spot_size = obj.re_chain_chainnode.angleLimitRad

def update_NodeRadius(self, context):
	obj = self.id_data
	if type(obj).__name__ == "Object":#Check if it's an object to prevent issues with clipboard 
		if obj.re_chain_chainnode.collisionRadius != 0:
			obj.empty_display_size = obj.re_chain_chainnode.collisionRadius * 100
		else:
			obj.empty_display_size = 1


def update_CollisionRadius(self, context):
	obj = self.id_data
	if type(obj).__name__ == "Object":#Check if it's an object to prevent issues with clipboard 
		if obj.get("TYPE",None) != "RE_CHAIN_COLLISION_CAPSULE_ROOT":
			if obj.re_chain_chaincollision.radius != 0:
				obj.empty_display_size = obj.re_chain_chaincollision.radius * 100
			else:
				obj.empty_display_size = 1
		else:
			for child in obj.children:
				if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START" or child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
					if obj.re_chain_chaincollision.radius != 0:
						child.empty_display_size = obj.re_chain_chaincollision.radius * 100
					else:
						child.empty_display_size = 1
						
def update_NodeNameVis(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_NODE":
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
			
def update_DrawConesThroughObjects(self, context):
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) == "RE_CHAIN_NODE_FRAME_HELPER":
			obj.show_in_front = self.drawConesThroughObjects

def update_DrawCollisionsThroughObjects(self, context):
	collisionTypes = [
		"RE_CHAIN_COLLISION_SINGLE",
		"RE_CHAIN_COLLISION_CAPSULE_START",
		"RE_CHAIN_COLLISION_CAPSULE_END"]
	for obj in bpy.data.objects:
		if obj.get("TYPE",None) in collisionTypes:
			obj.show_in_front = self.drawCollisionsThroughObjects

def update_CollisionOffset(self, context):
	obj = self.id_data
	if obj.get("TYPE",None) != "RE_CHAIN_COLLISION_CAPSULE_ROOT":
		obj.location = obj.re_chain_chaincollision.collisionOffset * 100
	else:
		for child in obj.children:
			if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
				child.location = obj.re_chain_chaincollision.collisionOffset * 100

def update_EndCollisionOffset(self, context):
	obj = self.id_data
	if obj.get("TYPE",None) != "RE_CHAIN_COLLISION_CAPSULE_ROOT":
		obj.location = obj.re_chain_chaincollision.endCollisionOffset * 100
	else:
		for child in obj.children:
			if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
				child.location = obj.re_chain_chaincollision.endCollisionOffset * 100
			
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
			   ("OBB", "OBB", ""),
			   ("PLANE", "Plane", ""),
			   ("LINESPHERE", "LineSphere", ""),
			   ("LERPSPHERE", "LerpSphere", ""),
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
	showAngleLimitCones: BoolProperty(
		name="Show Cones",
		description="Show Angle Limit Cones in 3D View",
		default = True,
		update = update_angleLimitConeVis
		)
	drawConesThroughObjects: BoolProperty(
		name="Draw Cones Through Objects",
		description="Make all angle limit cones render through any objects in front of them",
		default = False,
		update = update_DrawConesThroughObjects
		)
	angleLimitDisplaySize: FloatProperty(
		name="Angle Limit Size",
		description="Set the display size of node angle limits",
		default = 4.0,
		soft_min = 0.0,
		soft_max = 30.0,
		update = update_angleLimitSize
		)
	
	coneDisplaySize: FloatProperty(
		name="Cone Size",
		description="Set the display size of node angle limit cones",
		default = 0.75,
		soft_min = 0.0,
		soft_max = 30.0,
		update = update_coneSize
		)
class chainHeaderPropertyGroup(bpy.types.PropertyGroup):

	'''version: IntProperty(
		name = "Chain Version",
		description="Chain Version",#TODO Add description
		#default = 35,
		)'''
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
			   ]
		)
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
	modelCollisionSearch: BoolProperty(
		name="Model Collision Search",
		description="Model Collision Search",#TODO Add description
		default = False
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
  
def getChainHeader(ChainHeaderData,targetObject):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_header.version = str(ChainHeaderData.version)
	targetObject.re_chain_header.errFlags = str(ChainHeaderData.errFlags)
	targetObject.re_chain_header.masterSize = ChainHeaderData.masterSize
	targetObject.re_chain_header.rotationOrder = str(ChainHeaderData.rotationOrder)
	targetObject.re_chain_header.defaultSettingIdx = ChainHeaderData.defaultSettingIdx
	targetObject.re_chain_header.calculateMode = str(ChainHeaderData.calculateMode)
	targetObject.re_chain_header.chainAttrFlags = str(ChainHeaderData.chainAttrFlags)
	targetObject.re_chain_header.parameterFlag = str(ChainHeaderData.parameterFlag)
	targetObject.re_chain_header.calculateStepTime = ChainHeaderData.calculateStepTime
	targetObject.re_chain_header.modelCollisionSearch = ChainHeaderData.modelCollisionSearch
	targetObject.re_chain_header.legacyVersion = str(ChainHeaderData.legacyVersion)
	targetObject.re_chain_header.collisionFilterHit0 = str(ChainHeaderData.collisionFilterHit0)
	targetObject.re_chain_header.collisionFilterHit1 = str(ChainHeaderData.collisionFilterHit1)
	targetObject.re_chain_header.collisionFilterHit2 = str(ChainHeaderData.collisionFilterHit2)
	targetObject.re_chain_header.collisionFilterHit3 = str(ChainHeaderData.collisionFilterHit3)
	targetObject.re_chain_header.collisionFilterHit4 = str(ChainHeaderData.collisionFilterHit4)
	targetObject.re_chain_header.collisionFilterHit5 = str(ChainHeaderData.collisionFilterHit5)
	targetObject.re_chain_header.collisionFilterHit6 = str(ChainHeaderData.collisionFilterHit6)
	targetObject.re_chain_header.collisionFilterHit7 = str(ChainHeaderData.collisionFilterHit7)


def setChainHeaderData(ChainHeaderData,targetObject):
	ChainHeaderData.version = int(targetObject.re_chain_header.version) 
	ChainHeaderData.errFlags = int(targetObject.re_chain_header.errFlags)
	ChainHeaderData.masterSize = targetObject.re_chain_header.masterSize 
	ChainHeaderData.rotationOrder = int(targetObject.re_chain_header.rotationOrder)
	ChainHeaderData.defaultSettingIdx = targetObject.re_chain_header.defaultSettingIdx 
	ChainHeaderData.calculateMode = int(targetObject.re_chain_header.calculateMode)
	ChainHeaderData.chainAttrFlags = int(targetObject.re_chain_header.chainAttrFlags)
	ChainHeaderData.parameterFlag = int(targetObject.re_chain_header.parameterFlag)
	ChainHeaderData.calculateStepTime = targetObject.re_chain_header.calculateStepTime
	ChainHeaderData.modelCollisionSearch = int(targetObject.re_chain_header.modelCollisionSearch)
	ChainHeaderData.legacyVersion = int(targetObject.re_chain_header.legacyVersion)
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
	
  
def getWindSettings(WindSettingsData,targetObject):
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
	


def setWindSettingsData(WindSettingsData,targetObject):
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
	settingsAttrFlags: EnumProperty(
		name="Settings Attribute Flags",
		description="Apply Data to attribute.",
		items=[ ("0", "SettingAttrFlags_None", ""),
				("1", "SettingAttrFlags_Default", ""),
				("2", "SettingAttrFlags_VirtualGroundRoot", ""),
				("3", "SettingAttrFlags_UNKNOWNFLAG_3", ""),
				("4", "SettingAttrFlags_VirtualGroundTarget", ""),
				("5", "SettingAttrFlags_UNKNOWNFLAG_4", ""),
				("8", "SettingAttrFlags_IgnoreSameGroupCollision", ""),
				("9", "SettingAttrFlags_UNKNOWNFLAG_9", ""),
				("6", "SettingAttrFlags_VirtualGroundMask", ""),
				("10", "SettingAttrFlags_UNKNOWNFLAG_10", ""),
				("11", "SettingAttrFlags_UNKNOWNFLAG_11", ""),
				("12", "SettingAttrFlags_UNKNOWNFLAG_12", ""),
				("13", "SettingAttrFlags_UNKNOWNFLAG_13", ""),
			  ]
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
		default = (0.0,9.8,0.0),
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
		description = "Minimum amount of damping to be applied",#TODO Add description
		default = 0.2,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	secondMinDamping: FloatProperty(
		name = "Second Min Damping",
		description = "Minimum amount of damping to be applied",#TODO Add description
		default = 0.00,
		soft_min = 0.00,
		soft_max = 1.00,
		)
	dampingPow: FloatProperty(
		name = "Damping Power",
		description = "Damping Power",#TODO Add description
		default = 1.00,
		)
	secondDampingPow: FloatProperty(
		name = "Second Damping Power",
		description = "Second Damping Power",#TODO Add description
		default = 0.00,
		)
	collideMaxVelocity: FloatProperty(
		name = "Collide Max Velocity",
		description = "Collide Max Velocity",#TODO Add description
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
		description = "Spring Limit Rate",#TODO Add description
		default = 0.00,
		)
	springMaxVelocity: FloatProperty(
		name = "Spring Max Velocity",
		description = "Spring Max Velocity",#TODO Add description
		default = 0.00,
		unit = "VELOCITY"
		)
	springCalcType: EnumProperty(
		name="Spring Calculation Type",
		description="Apply Data to attribute.",
		items=[ ("0", "ChainSpringCalcType_Position", ""),
				("1", "ChainSpringCalcType_Rotation", ""),
				("2", "ChainSpringCalcType_VFRPosition", ""),
				("3", "ChainSpringCalcType_VFRRotation", ""),
			   ]
		)
	unknFlag: BoolProperty(
		name="Unknown Spring Calculation Flag",
		description="Model Collision Search",#TODO Add description
		default = False
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
		description = "Wind Effect Coefficient",#TODO Add description
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
	unknChainSettingValue0: FloatProperty(
		name = "Unknown 0",
		description = "Capcom Example Values RE4: [0.0]",#TODO Add description
		default = 0.00,
		)
	unknChainSettingValue1: FloatProperty(
		name = "Env Wind Effect Coefficient",
		description = "Capcom Example Values RE4: [0.0, 0.003000000026077032, 0.004999999888241291, 0.009999999776482582, 0.019999999552965164, 0.029999999329447746, 0.03500000014901161, 0.03999999910593033, 0.05000000074505806, 0.10000000149011612, 0.5]",
		default = 0.10,
		)
	unknChainSettingValue2: FloatProperty(
		name = "Unknown 2",
		description = "Capcom Example Values RE4: [0.0, 1.0, 5.0, 20.0, 30.0, 40.0, 41.0, 45.0, 50.0, 53.0, 60.0, 65.0]",
		default = 0.00,
		)
	unknChainSettingValue3: FloatProperty(
		name = "Unknown 3",
		description = "Capcom Example Values RE4: [0.0]",
		default = 0.00,
		)
	
def getChainSettings(ChainSettingsData,targetObject):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chainsettings.id = ChainSettingsData.id
	targetObject.re_chain_chainsettings.colliderFilterInfoPath = str(ChainSettingsData.colliderFilterInfoPath)
	targetObject.re_chain_chainsettings.sprayParameterArc = ChainSettingsData.sprayParameterArc
	targetObject.re_chain_chainsettings.sprayParameterFrequency = ChainSettingsData.sprayParameterFrequency
	targetObject.re_chain_chainsettings.sprayParameterCurve1 = ChainSettingsData.sprayParameterCurve1
	targetObject.re_chain_chainsettings.sprayParameterCurve2 = ChainSettingsData.sprayParameterCurve2
	targetObject.re_chain_chainsettings.chainType = str(ChainSettingsData.chainType)
	targetObject.re_chain_chainsettings.settingsAttrFlags = str(ChainSettingsData.settingsAttrFlags)
	targetObject.re_chain_chainsettings.muzzleDirection = str(ChainSettingsData.muzzleDirection)
	targetObject.re_chain_chainsettings.gravity = (ChainSettingsData.gravityX,ChainSettingsData.gravityY,ChainSettingsData.gravityZ)
	targetObject.re_chain_chainsettings.muzzleVelocity = (ChainSettingsData.muzzleVelocityX,ChainSettingsData.muzzleVelocityY,ChainSettingsData.muzzleVelocityZ)
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
	targetObject.re_chain_chainsettings.unknFlag = ChainSettingsData.unknFlag
	targetObject.re_chain_chainsettings.reduceSelfDistanceRate = ChainSettingsData.reduceSelfDistanceRate
	targetObject.re_chain_chainsettings.secondReduceDistanceRate = ChainSettingsData.secondReduceDistanceRate
	targetObject.re_chain_chainsettings.secondReduceDistanceSpeed = ChainSettingsData.secondReduceDistanceSpeed
	targetObject.re_chain_chainsettings.friction = ChainSettingsData.friction
	targetObject.re_chain_chainsettings.shockAbsorptionRate = ChainSettingsData.shockAbsorptionRate
	targetObject.re_chain_chainsettings.coefOfElasticity = ChainSettingsData.coefOfElasticity
	targetObject.re_chain_chainsettings.coefOfExternalForces = ChainSettingsData.coefOfExternalForces
	targetObject.re_chain_chainsettings.stretchInteractionRatio = ChainSettingsData.stretchInteractionRatio
	targetObject.re_chain_chainsettings.angleLimitInteractionRatio = ChainSettingsData.angleLimitInteractionRatio
	targetObject.re_chain_chainsettings.shootingElasticLimitRate = ChainSettingsData.shootingElasticLimitRate
	targetObject.re_chain_chainsettings.groupDefaultAttr = ChainSettingsData.groupDefaultAttr

	targetObject.re_chain_chainsettings.windEffectCoef = ChainSettingsData.windEffectCoef
	targetObject.re_chain_chainsettings.velocityLimit = ChainSettingsData.velocityLimit
	targetObject.re_chain_chainsettings.hardness = ChainSettingsData.hardness
	targetObject.re_chain_chainsettings.unknChainSettingValue0 = ChainSettingsData.unknChainSettingValue0
	targetObject.re_chain_chainsettings.unknChainSettingValue1 = ChainSettingsData.unknChainSettingValue1
	targetObject.re_chain_chainsettings.unknChainSettingValue2 = ChainSettingsData.unknChainSettingValue2
	targetObject.re_chain_chainsettings.unknChainSettingValue3 = ChainSettingsData.unknChainSettingValue3
def setChainSettingsData(ChainSettingsData,targetObject):
	ChainSettingsData.id = targetObject.re_chain_chainsettings.id 
	ChainSettingsData.colliderFilterInfoPath = str(targetObject.re_chain_chainsettings.colliderFilterInfoPath) 
	ChainSettingsData.sprayParameterArc = targetObject.re_chain_chainsettings.sprayParameterArc 
	ChainSettingsData.sprayParameterFrequency = targetObject.re_chain_chainsettings.sprayParameterFrequency 
	ChainSettingsData.sprayParameterCurve1 = targetObject.re_chain_chainsettings.sprayParameterCurve1 
	ChainSettingsData.sprayParameterCurve2 = targetObject.re_chain_chainsettings.sprayParameterCurve2 
	ChainSettingsData.chainType = int(targetObject.re_chain_chainsettings.chainType)
	ChainSettingsData.settingsAttrFlags = int(targetObject.re_chain_chainsettings.settingsAttrFlags)
	ChainSettingsData.muzzleDirection = int(targetObject.re_chain_chainsettings.muzzleDirection)
	
	ChainSettingsData.gravityX = targetObject.re_chain_chainsettings.gravity[0]
	ChainSettingsData.gravityY = targetObject.re_chain_chainsettings.gravity[1]
	ChainSettingsData.gravityZ = targetObject.re_chain_chainsettings.gravity[2]
	
	ChainSettingsData.muzzleVelocityX = targetObject.re_chain_chainsettings.muzzleVelocity[0]
	ChainSettingsData.muzzleVelocityY = targetObject.re_chain_chainsettings.muzzleVelocity[1]
	ChainSettingsData.muzzleVelocityZ = targetObject.re_chain_chainsettings.muzzleVelocity[2]
	
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
	ChainSettingsData.unknFlag = int(targetObject.re_chain_chainsettings.unknFlag)
	ChainSettingsData.reduceSelfDistanceRate = targetObject.re_chain_chainsettings.reduceSelfDistanceRate 
	ChainSettingsData.secondReduceDistanceRate = targetObject.re_chain_chainsettings.secondReduceDistanceRate 
	ChainSettingsData.secondReduceDistanceSpeed = targetObject.re_chain_chainsettings.secondReduceDistanceSpeed 
	ChainSettingsData.friction = targetObject.re_chain_chainsettings.friction 
	ChainSettingsData.shockAbsorptionRate = targetObject.re_chain_chainsettings.shockAbsorptionRate 
	ChainSettingsData.coefOfElasticity = targetObject.re_chain_chainsettings.coefOfElasticity 
	ChainSettingsData.coefOfExternalForces = targetObject.re_chain_chainsettings.coefOfExternalForces 
	ChainSettingsData.stretchInteractionRatio = targetObject.re_chain_chainsettings.stretchInteractionRatio 
	ChainSettingsData.angleLimitInteractionRatio = targetObject.re_chain_chainsettings.angleLimitInteractionRatio 
	ChainSettingsData.shootingElasticLimitRate = targetObject.re_chain_chainsettings.shootingElasticLimitRate 
	ChainSettingsData.groupDefaultAttr = targetObject.re_chain_chainsettings.groupDefaultAttr
	ChainSettingsData.windEffectCoef = targetObject.re_chain_chainsettings.windEffectCoef 
	ChainSettingsData.velocityLimit = targetObject.re_chain_chainsettings.velocityLimit 
	ChainSettingsData.hardness = targetObject.re_chain_chainsettings.hardness
	ChainSettingsData.unknChainSettingValue0 = targetObject.re_chain_chainsettings.unknChainSettingValue0 
	ChainSettingsData.unknChainSettingValue1 = targetObject.re_chain_chainsettings.unknChainSettingValue1 
	ChainSettingsData.unknChainSettingValue2 = targetObject.re_chain_chainsettings.unknChainSettingValue2 
	ChainSettingsData.unknChainSettingValue3 = targetObject.re_chain_chainsettings.unknChainSettingValue3 
	if targetObject.parent.get("TYPE",None) == "RE_CHAIN_WINDSETTINGS":
		ChainSettingsData.windID = targetObject.parent.re_chain_windsettings.id
	else:
		ChainSettingsData.windID = -1
	
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
	collisionFilterFlags: EnumProperty(
		name="Collision Filter Flags",
		description="Apply Data to attribute.",
		items=[ ("0", "ChainCollisionType_Self", ""),
				("1", "ChainCollisionType_Model", ""),
				("2", "ChainCollisionType_Collider", ""),
				("3", "ChainCollisionType_VGround", ""),
			   ]
		)
	extraNodeLocalPos: FloatVectorProperty(
		name = "Extra Node Local Pos",
		description="Extra Node Local Pos",#TODO Add description
		default = (0.0,0.0,0.0),
		)
	tag0: IntProperty(
		name = "Tag 0",
		description="Tag 0",#TODO Add description
		default = 0,
		)
	tag1: IntProperty(
		name = "Tag 1",
		description="Tag 1",#TODO Add description
		default = 0,
		)
	tag2: IntProperty(
		name = "Tag 2",
		description="Tag 2",#TODO Add description
		default = 0,
		)
	tag3: IntProperty(
		name = "Tag 3",
		description="Tag 3",#TODO Add description
		default = 0,
		)
	dampingNoise0: FloatProperty(
		name = "Damping Noise 0",
		description = "Damping Noise 0",#TODO Add description
		default = 0.00,
		)
	dampingNoise1: FloatProperty(
		name = "Damping Noise 1",
		description = "Damping Noise 1",#TODO Add description
		default = 0.00,
		)
	endRotConstMax: FloatProperty(
		name = "End Rotation Constant Max",
		description = "Damping Noise 1",#TODO Add description
		default = 0.00,
		)
	tagCount: IntProperty(
		name = "Tag Count",
		description="Tag Count",#TODO Add description
		default = 0,
		)
	angleLimitDirectionMode: EnumProperty(
		name="Angle Limit Direction Mode",
		description="Apply Data to attribute.",
		items=[ ("0", "AngleLimitDirectionMode_BasePose", ""),
				("1", "AngleLimitDirectionMode_MotionPose", ""),
			  ]
		)
	unknGroupValue0: FloatProperty(
		name = "Unknown 0 A",
		description="Unknown 0 A",#TODO Add description
		default = 0.0,
		)
	unknGroupValue0B: FloatProperty(
		name = "Unknown 0 B",
		description="Unknown 0 B",#TODO Add description
		default = 0.0,
		)
	unknBoneHash: IntProperty(
		name = "Unknown Bone Hash",
		description="Unknown Bone Hash",#TODO Add description
		default = 1095307227,
		)
	unknGroupValue1: IntProperty(
		name = "Unknown 1",
		description="Unknown 1",#TODO Add description
		default = 0,
		)
	unknGroupValue2: IntProperty(
		name = "Unknown 2",
		description="Unknown 2",#TODO Add description
		default = 0,
		)
	unknGroupValue3: IntProperty(
		name = "Unknown 3",
		description="Unknown 3",#TODO Add description
		default = 0,
		)

def getChainGroup(ChainGroupData,targetObject):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chaingroup.rotationOrder = str(ChainGroupData.rotationOrder)
	targetObject.re_chain_chaingroup.autoBlendCheckNodeNo = ChainGroupData.autoBlendCheckNodeNo
	targetObject.re_chain_chaingroup.attrFlags = ChainGroupData.attrFlags
	targetObject.re_chain_chaingroup.collisionFilterFlags = str(ChainGroupData.collisionFilterFlags)
	targetObject.re_chain_chaingroup.extraNodeLocalPos = (ChainGroupData.extraNodeLocalPosX,ChainGroupData.extraNodeLocalPosY,ChainGroupData.extraNodeLocalPosZ)
	targetObject.re_chain_chaingroup.tag0 = ChainGroupData.tag0
	targetObject.re_chain_chaingroup.tag1 = ChainGroupData.tag1
	targetObject.re_chain_chaingroup.tag2 = ChainGroupData.tag2
	targetObject.re_chain_chaingroup.tag3 = ChainGroupData.tag3
	targetObject.re_chain_chaingroup.dampingNoise0 = ChainGroupData.dampingNoise0
	targetObject.re_chain_chaingroup.dampingNoise1 = ChainGroupData.dampingNoise1
	targetObject.re_chain_chaingroup.endRotConstMax = ChainGroupData.endRotConstMax
	targetObject.re_chain_chaingroup.tagCount = ChainGroupData.tagCount
	targetObject.re_chain_chaingroup.angleLimitDirectionMode = str(ChainGroupData.angleLimitDirectionMode)
	targetObject.re_chain_chaingroup.unknGroupValue0 = ChainGroupData.unknGroupValue0
	targetObject.re_chain_chaingroup.unknGroupValue0B = ChainGroupData.unknGroupValue0B
	targetObject.re_chain_chaingroup.unknBoneHash = ChainGroupData.unknBoneHash
	targetObject.re_chain_chaingroup.unknGroupValue1 = ChainGroupData.unknGroupValue1
	targetObject.re_chain_chaingroup.unknGroupValue2 = ChainGroupData.unknGroupValue2
	targetObject.re_chain_chaingroup.unknGroupValue3 = ChainGroupData.unknGroupValue3
def setChainGroupData(ChainGroupData,targetObject):
	ChainGroupData.rotationOrder = int(targetObject.re_chain_chaingroup.rotationOrder)
	ChainGroupData.autoBlendCheckNodeNo = targetObject.re_chain_chaingroup.autoBlendCheckNodeNo 
	ChainGroupData.attrFlags = targetObject.re_chain_chaingroup.attrFlags
	ChainGroupData.collisionFilterFlags = int(targetObject.re_chain_chaingroup.collisionFilterFlags)
	
	ChainGroupData.extraNodeLocalPosX = targetObject.re_chain_chaingroup.extraNodeLocalPos[0] 
	ChainGroupData.extraNodeLocalPosY = targetObject.re_chain_chaingroup.extraNodeLocalPos[1]
	ChainGroupData.extraNodeLocalPosZ = targetObject.re_chain_chaingroup.extraNodeLocalPos[2] 
	
	ChainGroupData.tag0 = targetObject.re_chain_chaingroup.tag0 
	ChainGroupData.tag1 = targetObject.re_chain_chaingroup.tag1 
	ChainGroupData.tag2 = targetObject.re_chain_chaingroup.tag2 
	ChainGroupData.tag3 = targetObject.re_chain_chaingroup.tag3 
	ChainGroupData.dampingNoise0 = targetObject.re_chain_chaingroup.dampingNoise0 
	ChainGroupData.dampingNoise1 = targetObject.re_chain_chaingroup.dampingNoise1 
	ChainGroupData.endRotConstMax = targetObject.re_chain_chaingroup.endRotConstMax 
	ChainGroupData.tagCount = targetObject.re_chain_chaingroup.tagCount 
	ChainGroupData.angleLimitDirectionMode = int(targetObject.re_chain_chaingroup.angleLimitDirectionMode)
	
	ChainGroupData.unknGroupValue0 = targetObject.re_chain_chaingroup.unknGroupValue0
	ChainGroupData.unknGroupValue0B = targetObject.re_chain_chaingroup.unknGroupValue0B
	ChainGroupData.unknBoneHash = targetObject.re_chain_chaingroup.unknBoneHash 
	ChainGroupData.unknGroupValue1 = targetObject.re_chain_chaingroup.unknGroupValue1 
	ChainGroupData.unknGroupValue2 = targetObject.re_chain_chaingroup.unknGroupValue2 
	ChainGroupData.unknGroupValue3 = targetObject.re_chain_chaingroup.unknGroupValue3 

	if targetObject.parent.get("TYPE",None) == "RE_CHAIN_WINDSETTINGS":
		ChainGroupData.windID = targetObject.parent.re_chain_windsettings.id
		
	elif targetObject.parent.parent.get("TYPE",None) == "RE_CHAIN_WINDSETTINGS":
		ChainGroupData.windID = targetObject.parent.parent.re_chain_windsettings.id
		
	else:
		ChainGroupData.windID = -1

	if targetObject.parent.get("TYPE",None) == "RE_CHAIN_CHAINSETTINGS":
		ChainGroupData.settingID = targetObject.parent.re_chain_chainsettings.id
	else:
		ChainGroupData.settingID = -1
	
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
	collisionFilterFlags: EnumProperty(
		name="Collision Filter Flags",
		description="Apply Data to attribute.",
		items=[ ("-1", "ChainCollisionType_None", ""),
				("0", "ChainCollisionType_Self", ""),
				("1", "ChainCollisionType_Model", ""),
				("2", "ChainCollisionType_Collider", ""),
				("3", "ChainCollisionType_VGround", ""),
				("4", "ChainCollisionType_UNKNOWN4", ""),
				("5", "ChainCollisionType_UNKNOWN5", ""),
				("6", "ChainCollisionType_UNKNOWN6", ""),
				("7", "ChainCollisionType_UNKNOWN7", ""),
			   ]
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
	unknChainNodeValue0: FloatProperty(
		name = "Unknown 0",
		description="Unknown 0",#TODO Add description
		default = 1.0,
		)
	unknChainNodeValue1: FloatProperty(
		name = "Unknown 1",
		description="Unknown 1",#TODO Add description
		default = 0.0,
		)
def getChainNode(ChainNodeData,targetObject):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chainnode.angleLimitRad = ChainNodeData.angleLimitRad
	targetObject.re_chain_chainnode.angleLimitDistance = ChainNodeData.angleLimitDistance
	targetObject.re_chain_chainnode.angleLimitRestitution = ChainNodeData.angleLimitRestitution
	targetObject.re_chain_chainnode.angleLimitRestituteStopSpeed = ChainNodeData.angleLimitRestituteStopSpeed
	targetObject.re_chain_chainnode.collisionRadius = ChainNodeData.collisionRadius
	targetObject.re_chain_chainnode.collisionFilterFlags = str(ChainNodeData.collisionFilterFlags)
	targetObject.re_chain_chainnode.capsuleStretchRate0 = ChainNodeData.capsuleStretchRate0
	targetObject.re_chain_chainnode.capsuleStretchRate1 = ChainNodeData.capsuleStretchRate1
	targetObject.re_chain_chainnode.attrFlags = ChainNodeData.attrFlags
	targetObject.re_chain_chainnode.windCoef = ChainNodeData.windCoef
	targetObject.re_chain_chainnode.angleMode = str(ChainNodeData.angleMode)
	targetObject.re_chain_chainnode.collisionShape = str(ChainNodeData.collisionShape)
	targetObject.re_chain_chainnode.attachType = ChainNodeData.attachType
	targetObject.re_chain_chainnode.rotationType = ChainNodeData.rotationType
	targetObject.re_chain_chainnode.unknChainNodeValue0 = ChainNodeData.unknChainNodeValue0
	targetObject.re_chain_chainnode.unknChainNodeValue1 = ChainNodeData.unknChainNodeValue1
	
def setChainNodeData(ChainNodeData,targetObject):
	ChainNodeData.angleLimitRad = targetObject.re_chain_chainnode.angleLimitRad 
	ChainNodeData.angleLimitDistance = targetObject.re_chain_chainnode.angleLimitDistance 
	ChainNodeData.angleLimitRestitution = targetObject.re_chain_chainnode.angleLimitRestitution 
	ChainNodeData.angleLimitRestituteStopSpeed = targetObject.re_chain_chainnode.angleLimitRestituteStopSpeed 
	ChainNodeData.collisionRadius = targetObject.re_chain_chainnode.collisionRadius 
	ChainNodeData.collisionFilterFlags = int(targetObject.re_chain_chainnode.collisionFilterFlags)
	ChainNodeData.capsuleStretchRate0 = targetObject.re_chain_chainnode.capsuleStretchRate0 
	ChainNodeData.capsuleStretchRate1 = targetObject.re_chain_chainnode.capsuleStretchRate1 
	ChainNodeData.attrFlags = int(targetObject.re_chain_chainnode.attrFlags)
	ChainNodeData.windCoef = targetObject.re_chain_chainnode.windCoef 
	ChainNodeData.angleMode = int(targetObject.re_chain_chainnode.angleMode)
	ChainNodeData.collisionShape = int(targetObject.re_chain_chainnode.collisionShape)
	ChainNodeData.attachType = targetObject.re_chain_chainnode.attachType 
	ChainNodeData.rotationType = targetObject.re_chain_chainnode.rotationType
	ChainNodeData.unknChainNodeValue0 = targetObject.re_chain_chainnode.unknChainNodeValue0
	ChainNodeData.unknChainNodeValue1 = targetObject.re_chain_chainnode.unknChainNodeValue1

	for child in targetObject.children:
		if child.get("TYPE",None) == "RE_CHAIN_NODE_FRAME":
			frame = child
	frame.rotation_mode = "QUATERNION"#Have to set rotation mode to quaternion in case euler rotation is used, rotation wouldn't export properly in that case
	ChainNodeData.angleLimitDirectionX = frame.rotation_quaternion[1]
	ChainNodeData.angleLimitDirectionY = frame.rotation_quaternion[2]
	ChainNodeData.angleLimitDirectionZ = frame.rotation_quaternion[3]
	ChainNodeData.angleLimitDirectionW = frame.rotation_quaternion[0]
	frame.rotation_mode = "XYZ"
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

def getChainJiggle(ChainJiggleData,targetObject):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chainjiggle.rangeShape = str(ChainJiggleData.rangeShape)
	targetObject.re_chain_chainjiggle.springForce = ChainJiggleData.springForce
	targetObject.re_chain_chainjiggle.gravityCoef = ChainJiggleData.gravityCoef
	targetObject.re_chain_chainjiggle.damping = ChainJiggleData.damping
	targetObject.re_chain_chainjiggle.attrFlags = ChainJiggleData.attrFlags

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
		description="Apply Data to attribute.",
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
	lerp: FloatProperty(
		name = "Lerp",
		description = "Lerp",#TODO Add description
		default = 0.00,
		)
	unknCollisionValue: FloatProperty(
		name = "Unknown Collision Value",
		description = "Unknown Collision Value",#TODO Add description
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
				("5", "ChainCollisionShape_LineSphere", ""),
				("6", "ChainCollisionShape_LerpSphere", ""),
			   ]
		)
	subDataCount: IntProperty(
		name = "Unknown Count",
		description = "SubData Count?",#TODO Add description
		default = 0,
		)
	collisionFilterFlags: EnumProperty(
		name="Collision Filter Flags",
		description="Apply Data to attribute.",
		items=[ ("-1", "ChainCollisionType_None", ""),
				("0", "ChainCollisionType_Self", ""),
				("1", "ChainCollisionType_Model", ""),
				("2", "ChainCollisionType_Collider", ""),
				("3", "ChainCollisionType_VGround", ""),
			   ]
		)
	subDataFlag: IntProperty(
		name = "Use Sub Data Flag",
		description = "Set to 1 to enable subdata",
		default = -1,
		min = -1,
		max = 1,
		)

def getChainCollision(ChainCollisionData,targetObject):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chaincollision.rotationOrder = str(ChainCollisionData.rotationOrder)
	targetObject.re_chain_chaincollision.radius = ChainCollisionData.radius
	targetObject.re_chain_chaincollision.lerp = ChainCollisionData.lerp
	targetObject.re_chain_chaincollision.unknCollisionValue = ChainCollisionData.unknCollisionValue
	targetObject.re_chain_chaincollision.chainCollisionShape = str(ChainCollisionData.chainCollisionShape)
	targetObject.re_chain_chaincollision.subDataCount = ChainCollisionData.subDataCount
	targetObject.re_chain_chaincollision.collisionFilterFlags = str(ChainCollisionData.collisionFilterFlags)
	targetObject.re_chain_chaincollision.subDataFlag = ChainCollisionData.subDataFlag
	
	if ChainCollisionData.subDataFlag >= 1:
		targetObject.re_chain_collision_subdata.pos = (ChainCollisionData.subData.posX,ChainCollisionData.subData.posY,ChainCollisionData.subData.posZ)
		targetObject.re_chain_collision_subdata.pairPos = (ChainCollisionData.subData.pairPosX,ChainCollisionData.subData.pairPosY,ChainCollisionData.subData.pairPosZ)
		targetObject.re_chain_collision_subdata.rotOffset = (ChainCollisionData.subData.rotOffsetW,ChainCollisionData.subData.rotOffsetX,ChainCollisionData.subData.rotOffsetY,ChainCollisionData.subData.rotOffsetZ)
		targetObject.re_chain_collision_subdata.radius = ChainCollisionData.subData.radius
		targetObject.re_chain_collision_subdata.id = ChainCollisionData.subData.id
		targetObject.re_chain_collision_subdata.unknSubCollisionData0 = ChainCollisionData.subData.unknSubCollisionData0
		targetObject.re_chain_collision_subdata.unknSubCollisionData1 = ChainCollisionData.subData.unknSubCollisionData1
		targetObject.re_chain_collision_subdata.unknSubCollisionData2 = ChainCollisionData.subData.unknSubCollisionData2
		targetObject.re_chain_collision_subdata.unknSubCollisionData3 = ChainCollisionData.subData.unknSubCollisionData3

def setChainCollisionData(ChainCollisionData,targetObject):
	ChainCollisionData.rotationOrder = int(targetObject.re_chain_chaincollision.rotationOrder)
	ChainCollisionData.radius = targetObject.re_chain_chaincollision.radius
	ChainCollisionData.lerp = targetObject.re_chain_chaincollision.lerp
	ChainCollisionData.unknCollisionValue = targetObject.re_chain_chaincollision.unknCollisionValue
	ChainCollisionData.chainCollisionShape = int(targetObject.re_chain_chaincollision.chainCollisionShape)
	ChainCollisionData.subDataCount = targetObject.re_chain_chaincollision.subDataCount 
	ChainCollisionData.collisionFilterFlags = int(targetObject.re_chain_chaincollision.collisionFilterFlags)
	
	
	ChainCollisionData.posX = targetObject.re_chain_chaincollision.collisionOffset[0]
	ChainCollisionData.posY = targetObject.re_chain_chaincollision.collisionOffset[1]
	ChainCollisionData.posZ = targetObject.re_chain_chaincollision.collisionOffset[2]
	
	ChainCollisionData.pairPosX = targetObject.re_chain_chaincollision.endCollisionOffset[0]
	ChainCollisionData.pairPosY = targetObject.re_chain_chaincollision.endCollisionOffset[1]
	ChainCollisionData.pairPosZ = targetObject.re_chain_chaincollision.endCollisionOffset[2]
	if targetObject.get("TYPE",None) != "RE_CHAIN_COLLISION_CAPSULE_ROOT":
		ChainCollisionData.jointNameHash = hash_wide(targetObject.constraints["BoneName"].subtarget)		
		ChainCollisionData.rotOffsetX = targetObject.rotation_quaternion[1]
		ChainCollisionData.rotOffsetY = targetObject.rotation_quaternion[2]
		ChainCollisionData.rotOffsetZ = targetObject.rotation_quaternion[3]
		ChainCollisionData.rotOffsetW = targetObject.rotation_quaternion[0]
	else:
		startCapsule = None
		endCapsule = None
		for child in targetObject.children: 
			if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
				startCapsule = child
			elif child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
				endCapsule = child
				
		if startCapsule != None:
			ChainCollisionData.jointNameHash = hash_wide(startCapsule.constraints["BoneName"].subtarget)		
			ChainCollisionData.rotOffsetX = startCapsule.rotation_quaternion[1]
			ChainCollisionData.rotOffsetY = startCapsule.rotation_quaternion[2]
			ChainCollisionData.rotOffsetZ = startCapsule.rotation_quaternion[3]
			ChainCollisionData.rotOffsetW = startCapsule.rotation_quaternion[0]
		if endCapsule != None:
			ChainCollisionData.pairJointNameHash = hash_wide(endCapsule.constraints["BoneName"].subtarget)
		else:
			ChainCollisionData.pairPosX = 0.0
			ChainCollisionData.pairPosY = 0.0
			ChainCollisionData.pairPosZ = 0.0
			ChainCollisionData.pairJointNameHash = 0
	
	ChainCollisionData.subDataFlag = targetObject.re_chain_chaincollision.subDataFlag
	if targetObject.re_chain_chaincollision.subDataFlag:
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

class chainLinkPropertyGroup(bpy.types.PropertyGroup):
	chainGroupAObject: StringProperty(
		name = "Chain Group A",
		description = "Chain Group A",#TODO Add description
		default = "",
		)
	chainGroupBObject: StringProperty(
		name = "Chain Group B",
		description = "Chain Group B",#TODO Add description
		default = "",
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
def getChainLink(ChainLinkData,targetObject):
	#Done manually to be able to account for chain version differences eventually
	targetObject.re_chain_chainlink.distanceShrinkLimitCoef = ChainLinkData.distanceShrinkLimitCoef
	targetObject.re_chain_chainlink.distanceExpandLimitCoef = ChainLinkData.distanceExpandLimitCoef
	targetObject.re_chain_chainlink.linkMode = str(ChainLinkData.linkMode)
	targetObject.re_chain_chainlink.connectFlags = str(ChainLinkData.connectFlags)
	targetObject.re_chain_chainlink.linkAttrFlags = str(ChainLinkData.linkAttrFlags)
	targetObject.re_chain_chainlink.skipGroupA = ChainLinkData.skipGroupA
	targetObject.re_chain_chainlink.skipGroupB = ChainLinkData.skipGroupB
	targetObject.re_chain_chainlink.linkOrder = str(ChainLinkData.linkOrder)
	

def setChainLinkData(ChainLinkData,targetObject):
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
	re_chain_chainnode : PointerProperty(type=chainNodePropertyGroup)
	re_chain_chainjiggle : PointerProperty(type=chainJigglePropertyGroup)
	re_chain_collision_subdata : PointerProperty(type=collisionSubDataPropertyGroup)
	re_chain_chaincollision : PointerProperty(type=chainCollisionPropertyGroup)
	re_chain_chainlink : PointerProperty(type=chainLinkPropertyGroup)
	frameOrientation: FloatVectorProperty(
		name = "Frame Orientation",
		size = 3,
		subtype = "XYZ"
		)