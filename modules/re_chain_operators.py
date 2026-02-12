#Author: NSA Cloud
import bpy
import os
from math import radians
from mathutils import Matrix,Vector,Quaternion

from bpy.types import Operator

from .blender_re_chain import createEmpty,createCurve,alignChains,alignCollisions,checkNameUsage,checkChainSettingsIDUsage,checkWindSettingsIDUsage,findHeaderObj,syncCollisionOffsets,createChainCollection,getCollection,createCurveEmpty,createFakeEmptySphere,lockObjTransforms,setChainBoneColor
from .file_re_chain import ChainHeaderData,ChainSettingsData,WindSettingsData,ChainGroupData,ChainNodeData,ChainJiggleData,ChainCollisionData,ChainLinkData,ChainLinkNode
from .file_re_chain2 import Chain2HeaderData,Chain2SettingsData,Chain2WindSettingsData,Chain2GroupData,Chain2NodeData,Chain2JiggleData,Chain2CollisionData,Chain2LinkData,Chain2LinkNode
from .re_chain_propertyGroups import getChainHeader,getWindSettings,getChainSettings,getChainGroup,getChainNode,getChainJiggle,getChainLink,getChainCollision,getChainLinkCollisionNode
from .ui_re_chain_panels import tag_redraw
from .blender_utils import showErrorMessageBox,outlinerShowObject
from .re_chain_presets import saveAsPreset,readPresetJSON
from .re_chain_geoNodes import getColCapsuleGeoNodeTree,getColSphereGeoNodeTree,getChainLinkGeoNodeTree,getConeGeoNodeTree,getLinkColGeoNodeTree,getChainGroupMat


class WM_OT_ChainFromBone(Operator):
	bl_label = "Create Chain From Bone"
	bl_idname = "re_chain.chain_from_bone"
	bl_options = {'UNDO'}
	bl_description = "Create new chain group and chain node objects starting from the selected bone and ending at the last child bone. Note that chains cannot be branching. Must be parented to a chain settings object"
	def execute(self, context):
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		chainCollection = bpy.context.scene.re_chain_toolpanel.chainCollection
		headerObj = findHeaderObj()
		if chainCollection != None and headerObj != None:
			experimentalFeatures = bpy.context.scene.re_chain_toolpanel.experimentalPoseModeOptions
			selected = bpy.context.selected_pose_bones
			chainList = []
			
			if experimentalFeatures:
				if len(selected) >= 1:
					chainList = selected
					valid = True
				else:
					showErrorMessageBox("Must select pose bones to create a chain from selection.")
					return {'CANCELLED'}
			else:
				if len(selected) == 1:
					startBone = selected[0]
					
					chainList = startBone.children_recursive
					chainList.insert(0,startBone)
					#print(chainList)
				else:
					showErrorMessageBox("Select only the chain start bone.")
					return {'CANCELLED'}
				valid = True
				
				for bone in chainList:
					if len(bone.children) > 1:
						valid = False
			
			if not valid:
				showErrorMessageBox("Cannot have branching bones in a chain.")
				return {'CANCELLED'}
			else:
				#chainEntryCollection = getCollection(f"Chain Entries - {chainCollection.name}",chainCollection,makeNew = False)
				chainEntryCollection = chainCollection
				currentChainGroupIndex = 0
				subName = "CHAIN_GROUP_"+str(currentChainGroupIndex).zfill(2)
				while(checkNameUsage(subName,checkSubString=True)):
					currentChainGroupIndex +=1
					subName = "CHAIN_GROUP_"+str(currentChainGroupIndex).zfill(2)
				name = subName+"_"+chainList[len(chainList)-1].name.rsplit("_",1)[0]
					
				armature = chainList[0].id_data
				#print(armature)
				chainGroupObj = createCurve(name, [("TYPE","RE_CHAIN_CHAINGROUP")],bpy.context.scene.re_chain_toolpanel.chainSetting if bpy.context.scene.re_chain_toolpanel.chainSetting != None else headerObj,chainEntryCollection)
				if isChain2:
					chainGroup = Chain2GroupData()
				else:
					chainGroup = ChainGroupData()
				getChainGroup(chainGroup,chainGroupObj,isChain2)
				constraint = chainGroupObj.constraints.new("COPY_LOCATION")
				constraint.target = armature
				constraint.subtarget = chainList[-1].name
				chainGroupObj.show_in_front =  bpy.context.scene.re_chain_toolpanel.drawChainGroupsThroughObjects
				spline = chainGroupObj.data.splines.new("NURBS")
				spline.use_endpoint_u = True
				chainGroupObj.data.bevel_depth = bpy.context.scene.re_chain_toolpanel.groupDisplaySize
				chainGroupObj.data.dimensions = "3D"
				chainGroupObj.data.use_fill_caps = True
				chainGroupObj.data.materials.append(getChainGroupMat())
				spline.points.add(len(chainList) - 1)
				
				for i, o in enumerate(chainList):
					p = spline.points[i]
					objPos = list((armature.matrix_world @ o.matrix).to_translation())
					objPos.append(0.5)
					p.co = objPos
					h = chainGroupObj.modifiers.new(o.name, 'HOOK')
					h.object = armature
					h.subtarget = o.name
					h.vertex_indices_set([i])
				
				nodeParent = chainGroupObj
				lastBoneIndex = len(chainList) -1
				for boneIndex,bone in enumerate(chainList):
					nodeObj = createEmpty(bone.name,[("TYPE","RE_CHAIN_NODE")],nodeParent,chainEntryCollection)
					if isChain2:
						node = Chain2NodeData()
					else:
						node = ChainNodeData()
					getChainNode(node, nodeObj,isChain2)
					nodeParent = nodeObj
					nodeObj.empty_display_size = .02
					nodeObj.empty_display_type = "SPHERE"
					#nodeObj.show_name = True
					nodeObj.show_name = bpy.context.scene.re_chain_toolpanel.showNodeNames
					nodeObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawNodesThroughObjects
					
					#Constrain node to bone
					constraint = nodeObj.constraints.new(type = "COPY_LOCATION")
					constraint.target = armature
					constraint.subtarget = bone.name
					constraint.name = "BoneName"
					
					constraint = nodeObj.constraints.new(type = "COPY_ROTATION")
					constraint.target = armature
					constraint.subtarget = bone.name
					constraint.name = "BoneRotation"
					
					frame = createEmpty(nodeObj.name+"_ANGLE_LIMIT", [("TYPE","RE_CHAIN_NODE_FRAME")],nodeObj,chainEntryCollection)
					frame.empty_display_type = "ARROWS"
					frame.show_in_front = bpy.context.scene.re_chain_toolpanel.drawNodesThroughObjects
					frame.empty_display_size = bpy.context.scene.re_chain_toolpanel.angleLimitDisplaySize
					#frame.rotation_euler.rotate_axis("Z", radians(-90))
					
					bpy.context.evaluated_depsgraph_get().update()
					#Constrain frame location to node
						
					constraint = frame.constraints.new(type = "COPY_LOCATION")
					constraint.target = nodeObj
					
					constraint = frame.constraints.new(type = "COPY_SCALE")
					constraint.target = nodeObj
						
					if boneIndex == 0 and boneIndex == lastBoneIndex:
						#Get armature bone, not pose bone
						#Point X axis away from bone tail
						
						a = armature.matrix_world @ armature.data.bones[bone.name].head_local
						b = armature.matrix_world @ armature.data.bones[bone.name].tail_local
						
						direction  = (a - b).normalized()
						axis_align = Vector((1.0, 0.0, 0.0))
						
						angle = axis_align.angle(direction)
						axis  = axis_align.cross(direction)
						
						
						q = Quaternion(axis, angle)			
					
						
					else:
						if boneIndex != lastBoneIndex:
							#Point frame towards next bone head
							targetBone = chainList[boneIndex+1]
							a = armature.matrix_world @ armature.data.bones[bone.name].head_local
							b = armature.matrix_world @ armature.data.bones[targetBone.name].head_local
							direction  = (b - a).normalized()
							axis_align = Vector((1.0, 0.0, 0.0))
							
							angle = axis_align.angle(direction)
							axis  = axis_align.cross(direction)
							
							q = Quaternion(axis, angle)
							
					
					frame.rotation_mode = "XYZ"
					frame.rotation_euler = q.to_euler()
					#Apply additional local rotation to X axis, this is kind of an ugly solution but easier than messing with the matrices						
					frame.rotation_euler.rotate_axis("X", radians(90))
					frame.matrix_basis = nodeObj.matrix_world.inverted() @ frame.matrix_basis
					frame.location = nodeObj.location
					frame.scale = nodeObj.scale
					#Add angle limit cone
					"""
					light_data = bpy.data.lights.new(name=nodeObj.name+"_ANGLE_LIMIT_HELPER", type="SPOT")
					light_data.energy = 0.0
					light_data.use_shadow = False
					light_data.spot_blend = 0.0
					light_data.use_custom_distance = True
					light_data.cutoff_distance = 0.05
					#light_data.shadow_soft_size = nodeObj.parent.re_chain_chainnode.collisionRadius
					light_data.shadow_soft_size = 0.0
					light_data.spot_size = nodeObj.re_chain_chainnode.angleLimitRad
					# Create new object, pass the light data 
					lightObj = bpy.data.objects.new(name=nodeObj.name+"_ANGLE_LIMIT_HELPER", object_data=light_data)
					lightObj["TYPE"] = "RE_CHAIN_NODE_FRAME_HELPER"
					rotationMat = Matrix.Rotation(radians(-90.0),4,"Y")
					lightObj.parent = frame
					"""
					lightObj = createCurveEmpty(nodeObj.name+"_ANGLE_LIMIT_HELPER", [("TYPE","RE_CHAIN_NODE_FRAME_HELPER")],frame,chainEntryCollection)
					lightObj.show_wire = True
					lightObj.matrix_world = frame.matrix_world
					lightObj.hide_select = True#Disable ability to select to avoid it getting in the way
					
					lightObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawConesThroughObjects
					lightObj.hide_viewport = not bpy.context.scene.re_chain_toolpanel.showAngleLimitCones
					
					modifier = lightObj.modifiers.new(name="REChainGeometryNodes", type='NODES')
					nodeGroup = getConeGeoNodeTree()
					if modifier.node_group != None and modifier.node_group.name in bpy.data.node_groups:
						bpy.data.node_groups.remove(modifier.node_group)
					
					modifier.node_group = nodeGroup
					
					#Force update function to run so that the cone updates
					nodeObj.re_chain_chainnode.angleLimitRad = nodeObj.re_chain_chainnode.angleLimitRad
					#Determine cone scale
					xScaleModifier = 1.0
					yScaleModifier = 1.0
					zScaleModifier = 1.0
					if nodeObj.re_chain_chainnode.angleMode == "2":#Hinge angle mode
						yScaleModifier = .01
					elif nodeObj.re_chain_chainnode.angleMode == "4":#Limit oval angle mode
						zScaleModifier = .5
					elif nodeObj.re_chain_chainnode.angleMode == "5":#Limit elliptic angle mode
						yScaleModifier = .5
					lightObj.scale = (bpy.context.scene.re_chain_toolpanel.coneDisplaySize*xScaleModifier,bpy.context.scene.re_chain_toolpanel.coneDisplaySize*yScaleModifier,bpy.context.scene.re_chain_toolpanel.coneDisplaySize*zScaleModifier)
					
					#chainCollection.objects.link(lightObj)
				
				lightObj["isLastNode"] = 1
				#frame.hide_viewport = bpy.context.scene.re_chain_toolpanel.hideLastNodeAngleLimit
				lightObj.hide_viewport = bpy.context.scene.re_chain_toolpanel.hideLastNodeAngleLimit
				alignChains()
				setChainBoneColor(armature)
			self.report({"INFO"},"Created chain group from bone.")
		else:
			self.report({"ERROR"},"No chain group was created because the active chain collection is not set.")
		return {'FINISHED'}
	@classmethod
	def poll(self,context):
		return bpy.context.scene.re_chain_toolpanel.chainCollection is not None

class WM_OT_CollisionFromBones(Operator):
	bl_label = "Create Collision From Bone"
	bl_idname = "re_chain.collision_from_bone"
	bl_options = {'UNDO'}
	bl_description = "Create collision object from selected bone(s). Select one bone to create a sphere and two bones to create a collision capsule"
	def execute(self, context):
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		experimentalFeatures = bpy.context.scene.re_chain_toolpanel.experimentalPoseModeOptions
		selected = bpy.context.selected_pose_bones
		chainCollection = bpy.context.scene.re_chain_toolpanel.chainCollection
		if chainCollection != None and chainCollection.name.endswith(".clsp"):
			isCLSP = True
		else:
			isCLSP = False
		headerObj = findHeaderObj(chainCollection)
		if chainCollection != None and (headerObj != None or isCLSP):
			shape = str(bpy.context.scene.re_chain_toolpanel.collisionShape)
			if len(selected) == 1:
				startBone = selected[0]
				valid = True
				
				if shape == "CAPSULE":
						startBone = selected[0]
						endBone = selected[0]
						valid = True
				#print(chainList)
			elif len(selected) == 2:#Force capsule if two bones are selected
				startBone = selected[0]
				endBone = selected[1]
				valid = True
				if shape != "TCAPSULE":
					shape = "CAPSULE"#capsule
			else:
				valid = False
			
			
			if not valid:
				showErrorMessageBox("Select one bone to make a sphere or two to make a capsule.")
			else:
				if not isCLSP:
					collisionCollection = getCollection(f"Chain Collisions - {chainCollection.name}",chainCollection,makeNew = False)
				else:
					collisionCollection = chainCollection
				currentCollisionIndex = 0
				subName = "COL_"+str(currentCollisionIndex).zfill(2)
				while(checkNameUsage(subName,checkSubString=True)):
					currentCollisionIndex +=1
					subName = "COL_"+str(currentCollisionIndex).zfill(2)
				name = subName+"_"+shape
				armature = startBone.id_data
				#print(armature)
				singleObjectColList = ["SPHERE","OBB","PLANE","LINESPHERE","LERPSPHERE"]
				enumItemDict ={"SPHERE":"1","CAPSULE":"2","OBB":"3","PLANE":"4","TCAPSULE":"5","LINESPHERE":"6","LERPSPHERE":"7"}#For setting shape enum value
				if shape in singleObjectColList:
					name = "COL_" +str(currentCollisionIndex).zfill(2)+ "_"+shape +" " + startBone.name
					colSphereObj = createCurveEmpty(name, [("TYPE","RE_CHAIN_COLLISION_SINGLE")],headerObj,collisionCollection)
					if isChain2:
						chainCollision = Chain2CollisionData()
					else:
						chainCollision = ChainCollisionData()
					getChainCollision(chainCollision,colSphereObj,isChain2)
					colSphereObj.re_chain_chaincollision.chainCollisionShape = enumItemDict[shape]
					colSphereObj.re_chain_chaincollision.collisionOffset = (chainCollision.posX,chainCollision.posY,chainCollision.posZ)
					colSphereObj.rotation_mode = "QUATERNION" 
					colSphereObj.rotation_quaternion = (chainCollision.rotOffsetX,chainCollision.rotOffsetY,chainCollision.rotOffsetZ,chainCollision.rotOffsetW)
					
					#colSphereObj.empty_display_type = "SPHERE"
					#colSphereObj.empty_display_size = 1
					constraint = colSphereObj.constraints.new(type = "CHILD_OF")
					constraint.target = armature
					constraint.subtarget = startBone.name
					constraint.name = "BoneName"
					
					constraint.use_scale_x = False
					constraint.use_scale_y = False
					constraint.use_scale_z = False
					#colSphereObj.show_name = True
					colSphereObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
					colSphereObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCollisionsThroughObjects
					
					modifier = colSphereObj.modifiers.new(name="REChainGeometryNodes", type='NODES')
					nodeGroup = getColSphereGeoNodeTree()
					if modifier.node_group != None and modifier.node_group.name in bpy.data.node_groups:
						bpy.data.node_groups.remove(modifier.node_group)
					modifier.node_group = nodeGroup
				elif shape == "CAPSULE" or shape == "TCAPSULE":#CAPSULE
					name = subName+ f"_{shape} - {startBone.name} > {endBone.name}" 
					colCapsuleRootObj = createCurveEmpty(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_ROOT")],headerObj,collisionCollection)
					lockObjTransforms(colCapsuleRootObj)
					#colCapsuleRootObj.empty_display_size = .1
					if isChain2:
						chainCollision = Chain2CollisionData()
					else:
						chainCollision = ChainCollisionData()
					getChainCollision(chainCollision,colCapsuleRootObj,isChain2)
					name = subName+ f"_{shape}_BEGIN" + " " + startBone.name
					colCapsuleStartObj = createFakeEmptySphere(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_START")],colCapsuleRootObj,collisionCollection)
					
					colCapsuleRootObj.re_chain_chaincollision.chainCollisionShape = enumItemDict[shape]
					
					colCapsuleStartObj.re_chain_chaincollision.collisionOffset = (chainCollision.posX,chainCollision.posY,chainCollision.posZ)
					colCapsuleStartObj.rotation_mode = "QUATERNION" 
					colCapsuleStartObj.rotation_quaternion = (chainCollision.rotOffsetX,chainCollision.rotOffsetY,chainCollision.rotOffsetZ,chainCollision.rotOffsetW)
					
					
					
					#colCapsuleStartObj.empty_display_type = "SPHERE"
					#colCapsuleStartObj.empty_display_size = 1
					constraint = colCapsuleStartObj.constraints.new(type = "CHILD_OF")
					constraint.target = armature
					constraint.subtarget = startBone.name
					constraint.name = "BoneName"
					
					constraint.use_scale_x = False
					constraint.use_scale_y = False
					constraint.use_scale_z = False
					#colCapsuleStartObj.show_name = True
					colCapsuleStartObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
					colCapsuleStartObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCapsuleHandlesThroughObjects
					
					name = subName+ f"_{shape}_END" + " " + endBone.name
					colCapsuleEndObj = createFakeEmptySphere(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_END")],colCapsuleRootObj,collisionCollection)
					colCapsuleEndObj.re_chain_chaincollision.endCollisionOffset = (chainCollision.pairPosX,chainCollision.pairPosY,chainCollision.pairPosZ)
					#colCapsuleEndObj.empty_display_type = "SPHERE"
					#colCapsuleEndObj.empty_display_size = 1
					constraint = colCapsuleEndObj.constraints.new(type = "CHILD_OF")
					constraint.target = armature
					constraint.subtarget = endBone.name
					constraint.name = "BoneName"
					
					constraint.use_scale_x = False
					constraint.use_scale_y = False
					constraint.use_scale_z = False
					#colCapsuleEndObj.show_name = True
					colCapsuleEndObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
					colCapsuleEndObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCapsuleHandlesThroughObjects
					
				
					#Update start and end obj scale
					colCapsuleRootObj.re_chain_chaincollision.radius = colCapsuleRootObj.re_chain_chaincollision.radius
					colCapsuleRootObj.re_chain_chaincollision.endRadius = colCapsuleRootObj.re_chain_chaincollision.endRadius 
				
					modifier = colCapsuleRootObj.modifiers.new(name="REChainGeometryNodes", type='NODES')
					nodeGroup = getColCapsuleGeoNodeTree()
					if modifier.node_group != None and modifier.node_group.name in bpy.data.node_groups:
						bpy.data.node_groups.remove(modifier.node_group)
					modifier.node_group = nodeGroup
					
					#modifier["Start Object"] = startObj.name
					#modifier["End Object"] = endObj.name
					#Can't access group inputs by name, have to use blender's auto generated names because ???
					if bpy.app.version < (4,0,0):
						modifier["Input_0"] = colCapsuleStartObj
						modifier["Input_1"] = colCapsuleEndObj
					else:
						modifier["Socket_0"] = colCapsuleStartObj
						modifier["Socket_1"] = colCapsuleEndObj
				alignCollisions()
				self.report({"INFO"},"Created collision from bone.")
		else:
			self.report({"ERROR"},"No collision was created because the active chain collection is not set.")
		return {'FINISHED'}
	@classmethod
	def poll(self,context):
		return bpy.context.scene.re_chain_toolpanel.chainCollection is not None

class WM_OT_NewChainHeader(Operator):
	bl_label = "Create Chain Header"
	bl_idname = "re_chain.create_chain_header"
	bl_options = {'UNDO'}
	bl_description = "Create a chain header object. All chain objects must be parented to this. A new chain collection will be created"
	collectionName : bpy.props.StringProperty(name = "Chain Name",
										 description = "The name of the newly created chain collection.\nUse the same name as the mesh file",
										 default = "newChain"
										 )
	chainFormat: bpy.props.EnumProperty(
		name="File Type",
		description="Apply Data to attribute.",
		items=[ (".chain", "Chain", "Old chain file format, use for anything older than MH Wilds/Dead Rising"),
				(".chain2", "Chain2", "New chain file format, use for MH Wilds/Dead Rising and newer"),
				(".clsp", "CLSP", "Chain collision file format, used in DD2 and MH Wilds.\nFor these games, put all collisions in this collection, otherwise they wont have any effect"),
			   ]
		)
	def execute(self, context):
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		if self.collectionName.strip() != "":
			if self.collectionName in bpy.data.collections:
				parentCollection = bpy.data.collections[self.collectionName.strip()]
			else:
				parentCollection = None
			chainCollection = createChainCollection(self.collectionName.strip() + self.chainFormat,parentCollection)
			if self.chainFormat != ".clsp":
				chainHeaderObj = createEmpty(f"CHAIN_HEADER {self.collectionName}{self.chainFormat}", [("TYPE","RE_CHAIN_HEADER")],None,chainCollection)
				if isChain2:
					chainHeader = Chain2HeaderData()
				else:
					chainHeader = ChainHeaderData()
				
				getChainHeader(chainHeader,chainHeaderObj,isChain2)
				lockObjTransforms(chainHeaderObj)
				bpy.context.view_layer.objects.active = chainHeaderObj
			self.report({"INFO"},"Created new RE chain collection.")
			return {'FINISHED'}
		else:
			self.report({"ERROR"},"Invalid chain collection name.")
			return {'CANCELLED'}
	def invoke(self,context,event):
		meshCollectionName = context.scene.get("REMeshLastImportedCollection")
		if meshCollectionName != None and ".mesh" in meshCollectionName:
			self.collectionName = meshCollectionName.split(".mesh")[0]
		return context.window_manager.invoke_props_dialog(self)
class WM_OT_NewChainSettings(Operator):
	bl_label = "Create Chain Settings"
	bl_idname = "re_chain.create_chain_settings"
	bl_options = {'UNDO'}
	bl_description = "Create a chain settings object. Contains parameters to determine how chain groups should behave. Must be parented to either a chain header or wind settings object"
	def execute(self, context):
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		chainCollection = bpy.context.scene.re_chain_toolpanel.chainCollection
		headerObj = findHeaderObj()
		if chainCollection != None and headerObj != None:
			#chainEntryCollection = getCollection(f"Chain Entries - {chainCollection.name}",chainCollection,makeNew = False)
			chainEntryCollection = chainCollection
			currentIndex = 0
			name = "CHAIN_SETTINGS_" + str(currentIndex).zfill(2)
			while(checkNameUsage(name,checkSubString=True)):
				currentIndex +=1
				name = "CHAIN_SETTINGS_" + str(currentIndex).zfill(2)
			
			currentSettingID = 0
			while checkChainSettingsIDUsage(currentSettingID):
				currentSettingID += 1
			if isChain2:
				chainSettings = Chain2SettingsData()
			else:
				chainSettings = ChainSettingsData()
			chainSettingsObj = createEmpty(name, [("TYPE","RE_CHAIN_CHAINSETTINGS")],headerObj,chainEntryCollection)
			getChainSettings(chainSettings,chainSettingsObj,isChain2)
			lockObjTransforms(chainSettingsObj,lockLocation = False,lockRotation = True,lockScale = True)
			chainSettingsObj.re_chain_chainsettings.id = currentSettingID
			self.report({"INFO"},"Created chain settings object.")
			if bpy.context.mode == "OBJECT":	
				bpy.context.view_layer.objects.active = chainSettingsObj
			bpy.context.scene.re_chain_toolpanel.chainSetting = chainSettingsObj
		else:
			self.report({"ERROR"},"No chain settings object was created because the active chain collection is not set.")
		return {'FINISHED'}
	@classmethod
	def poll(self,context):
		return bpy.context.scene.re_chain_toolpanel.chainCollection is not None

class WM_OT_NewWindSettings(Operator):
	bl_label = "Create Wind Settings"
	bl_idname = "re_chain.create_wind_settings"
	bl_options = {'UNDO'}
	bl_description = "Create a wind settings object. Allows for wind effects on chain groups. For wind to take effect, chain settings objects must be parented to this. Must be parented to a chain header"
	def execute(self, context):
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		chainCollection = bpy.context.scene.re_chain_toolpanel.chainCollection
		headerObj = findHeaderObj()
		if chainCollection != None and headerObj != None:
			#chainEntryCollection = getCollection(f"Chain Entries - {chainCollection.name}",chainCollection,makeNew = False)
			chainEntryCollection = chainCollection
			currentIndex = 0
			name = "WIND_SETTINGS_" + str(currentIndex).zfill(2)
			while(checkNameUsage(name,checkSubString=True)):
				currentIndex +=1
				name = "WIND_SETTINGS_" + str(currentIndex).zfill(2)
			
			currentSettingID = 0
			while checkWindSettingsIDUsage(currentSettingID):
				currentSettingID += 1
			if isChain2:	
				windSettings = Chain2WindSettingsData()
			else:
				windSettings = WindSettingsData()
			windSettingsObj = createEmpty(name, [("TYPE","RE_CHAIN_WINDSETTINGS")],headerObj,chainEntryCollection)
			lockObjTransforms(windSettingsObj)
			getWindSettings(windSettings,windSettingsObj,isChain2)
			windSettingsObj.re_chain_windsettings.id = currentSettingID
			self.report({"INFO"},"Created wind settings object.")
			bpy.context.view_layer.objects.active = windSettingsObj
		else:
			self.report({"ERROR"},"No wind settings object was created because the active chain collection is not set.")
		return {'FINISHED'}
	@classmethod
	def poll(self,context):
		return bpy.context.scene.re_chain_toolpanel.chainCollection is not None

class WM_OT_NewChainJiggle(Operator):
	bl_label = "Create Chain Jiggle"
	bl_idname = "re_chain.create_chain_jiggle"
	bl_options = {'UNDO'}
	bl_description = "Create a chain jiggle object. Adds special jiggle simulation to its chain node parent.\nJiggle range is controlled by the location and scale of the object.\nCan be used on chain versions 35+.\nA chain node must be selected"
	
	@classmethod
	def poll(self,context):
		return context.active_object is not None and context.active_object.get("TYPE") == "RE_CHAIN_NODE" and bpy.context.scene.re_chain_toolpanel.chainCollection is not None
	
	def execute(self, context):
		
		chainCollection = bpy.context.scene.re_chain_toolpanel.chainCollection
		if chainCollection != None:
			parent = None
			name = "CHAIN_JIGGLE"
			if bpy.context.active_object != None:
				if bpy.context.active_object.get("TYPE",None) == "RE_CHAIN_NODE":
					parent = bpy.context.active_object
					name = str(parent.constraints["BoneName"].subtarget)+"_JIGGLE"
					
			chainJiggleObj = createEmpty(name, [("TYPE","RE_CHAIN_JIGGLE")],parent,chainCollection)
			chainJiggle = ChainJiggleData()
			getChainJiggle(chainJiggle,chainJiggleObj)
			chainJiggleObj.empty_display_size = .2
			chainJiggleObj.show_name = bpy.context.scene.re_chain_toolpanel.showNodeNames
			chainJiggleObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawNodesThroughObjects
			chainJiggleObj.rotation_mode = 'QUATERNION'
			chainJiggleObj.rotation_quaternion = (chainJiggle.rangeAxisW,chainJiggle.rangeAxisX,chainJiggle.rangeAxisY,chainJiggle.rangeAxisZ)
			chainJiggleObj.scale = (chainJiggle.rangeX, chainJiggle.rangeY, chainJiggle.rangeZ)
			chainJiggleObj.location = (chainJiggle.rangeOffsetX, chainJiggle.rangeOffsetY, chainJiggle.rangeOffsetZ)
			
			self.report({"INFO"},"Created chain jiggle object.")
			bpy.context.view_layer.objects.active = chainJiggleObj
		else:
			self.report({"ERROR"},"No chain jiggle object was created because the active chain collection is not set.")
		return {'FINISHED'}

class WM_OT_NewChainLink(Operator):
	bl_label = "Create Chain Link"
	bl_idname = "re_chain.create_chain_link"
	bl_description = "Create a chain link object to make two chain groups move together. Must be parented to a chain header.\nTwo chain groups must be selected to create a chain link"
	bl_options = {'UNDO'}
	def execute(self, context):
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		chainCollection = bpy.context.scene.re_chain_toolpanel.chainCollection
		headerObj = findHeaderObj()
		if chainCollection != None and headerObj != None:
			linkCollection = getCollection(f"Chain Links - {chainCollection.name}",chainCollection,makeNew = False)
			
			groupAObj = None
			groupBObj = None
			if len(bpy.context.selected_objects) == 2:
				if bpy.context.selected_objects[0].get("TYPE",None) == "RE_CHAIN_CHAINGROUP" and bpy.context.selected_objects[1].get("TYPE",None) == "RE_CHAIN_CHAINGROUP":
					groupAObj = bpy.context.selected_objects[0]
					groupBObj = bpy.context.selected_objects[1]
			currentIndex = 0
			name = "LINK_" + str(currentIndex).zfill(2)
			while(checkNameUsage(name,checkSubString=True)):
				currentIndex +=1
				name = "LINK_" + str(currentIndex).zfill(2)
			if isChain2:
				chainLink = Chain2LinkData()
			else:
				chainLink = ChainLinkData()
			if groupAObj != None:
				shortNameA = groupAObj.name.replace("CHAIN_GROUP_","")
				shortNameB = groupBObj.name.replace("CHAIN_GROUP_","")
			else:
				shortNameA = "NONE"
				shortNameB = "NONE"
			chainLinkObj = createCurveEmpty(f"{name} - {shortNameA} > {shortNameB}", [("TYPE","RE_CHAIN_LINK")],headerObj,linkCollection)
			getChainLink(chainLink,chainLinkObj,isChain2)
			lockObjTransforms(chainLinkObj)
			if groupAObj != None:
				chainLinkObj.re_chain_chainlink.chainGroupAObject = groupAObj.name
				chainLinkObj.re_chain_chainlink.chainGroupBObject = groupBObj.name
			
			startObj = None
			endObj = None
			if groupAObj != None:
				for child in groupAObj.children:
					if child.get("TYPE") == "RE_CHAIN_NODE":
						startObj = child
						break
			if groupBObj != None:
				for child in groupBObj.children:
					if child.get("TYPE") == "RE_CHAIN_NODE":
						endObj = child
						break
			chainLinkObj.show_in_front = True
			modifier = chainLinkObj.modifiers.new(name="REChainGeometryNodes", type='NODES')
			nodeGroup = getChainLinkGeoNodeTree()
			if modifier.node_group != None and modifier.node_group.name in bpy.data.node_groups:
				bpy.data.node_groups.remove(modifier.node_group)
			modifier.node_group = nodeGroup
			
			#if startObj != None and endObj != None:
				#modifier["Input_0"] = startObj
				#modifier["Input_1"] = endObj
			#Force update
			chainLinkObj.re_chain_chainlink.chainGroupAObject = chainLinkObj.re_chain_chainlink.chainGroupAObject
			chainLinkObj.re_chain_chainlink.chainGroupBObject = chainLinkObj.re_chain_chainlink.chainGroupBObject
			
			getChainLink(chainLink,chainLinkObj)
			
			self.report({"INFO"},"Created chain link object.")
			bpy.context.view_layer.objects.active = chainLinkObj
		else:
			self.report({"ERROR"},"No chain link object was created because the active chain collection is not set.")
		return {'FINISHED'}
	@classmethod
	def poll(self,context):
		return context.active_object != None and len(context.selected_objects) == 2 and (context.selected_objects[0].get("TYPE") == "RE_CHAIN_CHAINGROUP" and context.selected_objects[1].get("TYPE") == "RE_CHAIN_CHAINGROUP")

class WM_OT_CreateChainLinkCollision(Operator):
	bl_label = "Create Chain Link Collision"
	bl_idname = "re_chain.create_chain_link_collision"
	bl_description = "Adds collision to the selected chain link(s).\nBoth chain groups must have the same amount of bones and cannot contain branching bones"
	bl_options = {'UNDO'}
	def execute(self, context):
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		chainCollection = bpy.context.scene.re_chain_toolpanel.chainCollection
		chainLinkObjList = []
		
		for obj in context.selected_objects:
			if obj.get("TYPE") == "RE_CHAIN_LINK":
				chainLinkObjList.append(obj)
				
		if chainLinkObjList != []:
			linkCollection = getCollection(f"Chain Links - {chainCollection.name}",chainCollection,makeNew = False)
			for chainLinkObj in chainLinkObjList:
				removeExistingCollisionList = []
				for child in chainLinkObj.children:
					if child.get("TYPE") == "RE_CHAIN_LINK_COLLISION":
						removeExistingCollisionList.append(child)
				for existingCollisionObj in removeExistingCollisionList:
					bpy.data.objects.remove(existingCollisionObj)
						
				groupAObj = bpy.data.objects.get(chainLinkObj.re_chain_chainlink.chainGroupAObject)
				groupBObj = bpy.data.objects.get(chainLinkObj.re_chain_chainlink.chainGroupBObject)
			
				chainLinkANodeObjList = []
				chainLinkBNodeObjList = []
				if groupAObj != None and groupAObj.get("TYPE") == "RE_CHAIN_CHAINGROUP" and len(groupAObj.children) > 0:
					#TODO Add chain group subdata export
					currentNode = groupAObj.children[0]
					chainLinkANodeObjList = [currentNode]
					hasChildNode = True
					while hasChildNode:
						currentNodeHasChildNode = False
						for child in currentNode.children:
							if child.get("TYPE",None) == "RE_CHAIN_NODE":
								chainLinkANodeObjList.append(child)
								currentNode = child
								currentNodeHasChildNode = True
						if not currentNodeHasChildNode:
							hasChildNode = False
				if groupBObj != None and groupBObj.get("TYPE") == "RE_CHAIN_CHAINGROUP" and len(groupBObj.children) > 0:
					#TODO Add chain group subdata export
					currentNode = groupBObj.children[0]
					chainLinkBNodeObjList = [currentNode]
					hasChildNode = True
					while hasChildNode:
						currentNodeHasChildNode = False
						for child in currentNode.children:
							if child.get("TYPE",None) == "RE_CHAIN_NODE":
								chainLinkBNodeObjList.append(child)
								currentNode = child
								currentNodeHasChildNode = True
						if not currentNodeHasChildNode:
							hasChildNode = False
				if chainLinkANodeObjList != [] and len(chainLinkANodeObjList) == len(chainLinkBNodeObjList):
					for index in range(len(chainLinkANodeObjList)):
						try:
							objA = chainLinkANodeObjList[index]
							nameA = objA.constraints["BoneName"].subtarget
						except:
							objA = None
							nameA = "INVALID"
							
						try:
							objB = chainLinkBNodeObjList[index]
							nameB = objB.constraints["BoneName"].subtarget
						except:
							objB = None
							nameB = "INVALID"
							
						if "LINK_" in chainLinkObj.name:
							linkIndex = 0
							num = chainLinkObj.name.split("LINK_")[1].split(" -",1)[0]
							if num.isdigit():
								linkIndex = int(num)
						name = f"LINK_{str(linkIndex).zfill(2)}"
						linkCollisionObj = createCurveEmpty(f"{name}_COL_{str(index).zfill(2)} - {nameA} > {nameB}", [("TYPE","RE_CHAIN_LINK_COLLISION")],chainLinkObj,linkCollection)
						lockObjTransforms(linkCollisionObj)
						modifier = linkCollisionObj.modifiers.new(name="REChainGeometryNodes", type='NODES')
						nodeGroup = getLinkColGeoNodeTree()
						if modifier.node_group != None and modifier.node_group.name in bpy.data.node_groups:
							bpy.data.node_groups.remove(modifier.node_group)
						modifier.node_group = nodeGroup
						
						if bpy.app.version < (4,0,0):
							if objA != None:
								modifier["Input_0"] = objA
							if objB != None:
								modifier["Input_1"] = objB
							
						else:
							if objA != None:
								modifier["Socket_0"] = objA
							if objB != None:
								modifier["Socket_1"] = objB
						modifier.node_group.interface_update(bpy.context)
						if isChain2:
							linkCollision = Chain2LinkNode()
						else:
							linkCollision = ChainLinkNode()
						linkCollisionObj.re_chain_chainlink_collision.collisionRadius = linkCollision.collisionRadius
						linkCollisionObj.re_chain_chainlink_collision.collisionFilterFlags = linkCollision.collisionFilterFlags
						linkCollisionObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawLinkCollisionsThroughObjects
					self.report({"INFO"},"Created chain link collision.")
				else:
					self.report({"ERROR"},"The chain groups do not have the same amount of bones or are not set in the chain link.")
			
			self.report({"INFO"},"Created chain link collision.")
		else:
			self.report({"ERROR"},"No chain link object was created because the active chain collection is not set.")
		return {'FINISHED'}
	@classmethod
	def poll(self,context):
		return context.active_object != None and context.active_object.get("TYPE") == "RE_CHAIN_LINK"

class WM_OT_CopyChainProperties(Operator):
	bl_label = "Copy"
	bl_idname = "re_chain.copy_chain_properties"
	bl_context = "objectmode"
	bl_description = "Copy properties from a chain object"
	
	@classmethod
	def poll(cls, context):
		return bpy.context.selected_objects != []
	
	def execute(self, context):
		activeObj = bpy.context.active_object
		chainObjType = activeObj.get("TYPE",None)
		clipboard = bpy.context.scene.re_chain_clipboard
		
		collisionTypes = [
			"RE_CHAIN_COLLISION_SINGLE",
			"RE_CHAIN_COLLISION_CAPSULE_ROOT",
			]
		
		if chainObjType == "RE_CHAIN_HEADER":
			clipboard.re_chain_type = chainObjType
			clipboard.re_chain_type_name = "Chain Header"
			#initialize clipboard entry
			chainHeader = ChainHeaderData()
			getChainHeader(chainHeader, clipboard)
			for key, value in activeObj.re_chain_header.items():
				clipboard.re_chain_header[key] = value
		elif chainObjType == "RE_CHAIN_WINDSETTINGS":
			clipboard.re_chain_type = chainObjType
			clipboard.re_chain_type_name = "Wind Settings"
			#initialize clipboard entry
			windSettings = WindSettingsData()
			getWindSettings(windSettings, clipboard)
			for key, value in activeObj.re_chain_windsettings.items():
				clipboard.re_chain_windsettings[key] = value
			
		elif chainObjType == "RE_CHAIN_CHAINSETTINGS":
			clipboard.re_chain_type = chainObjType
			clipboard.re_chain_type_name = "Chain Settings"
			#initialize clipboard entry
			chainSettings = ChainSettingsData()
			getChainSettings(chainSettings, clipboard)
			for key, value in activeObj.re_chain_chainsettings.items():
				clipboard.re_chain_chainsettings[key] = value
		
		elif chainObjType == "RE_CHAIN_CHAINGROUP":
			clipboard.re_chain_type = chainObjType
			clipboard.re_chain_type_name = "Chain Group"
			#initialize clipboard entry
			chainGroup = ChainGroupData()
			getChainGroup(chainGroup, clipboard)
			for key, value in activeObj.re_chain_chaingroup.items():
				clipboard.re_chain_chaingroup[key] = value
				
		elif chainObjType == "RE_CHAIN_NODE":
			clipboard.re_chain_type = chainObjType
			clipboard.re_chain_type_name = "Chain Node"
			#initialize clipboard entry
			chainNode = ChainNodeData()
			getChainNode(chainNode, clipboard)
			for key, value in activeObj.re_chain_chainnode.items():
				clipboard.re_chain_chainnode[key] = value

		elif chainObjType == "RE_CHAIN_JIGGLE":
			clipboard.re_chain_type = chainObjType
			clipboard.re_chain_type_name = "Chain Jiggle"
			#initialize clipboard entry
			chainJiggle = ChainJiggleData()
			getChainJiggle(chainJiggle, clipboard)
			for key, value in activeObj.re_chain_chainjiggle.items():
				clipboard.re_chain_chainjiggle[key] = value

		elif chainObjType == "RE_CHAIN_LINK":
			clipboard.re_chain_type = chainObjType
			clipboard.re_chain_type_name = "Chain Link"
			#initialize clipboard entry
			chainLink = ChainLinkData()
			getChainLink(chainLink, clipboard)
			for key, value in activeObj.re_chain_chainlink.items():
				clipboard.re_chain_chainlink[key] = value	
		elif chainObjType == "RE_CHAIN_LINK_COLLISION":
			clipboard.re_chain_type = chainObjType
			clipboard.re_chain_type_name = "Chain Link Collision Data"
			#initialize clipboard entry
			chainLinkNode = ChainLinkNode()
			getChainLinkCollisionNode(chainLinkNode, clipboard)
			for key, value in activeObj.re_chain_chainlink_collision.items():
				clipboard.re_chain_chainlink_collision[key] = value	
		
		elif chainObjType == "RE_CHAIN_NODE_FRAME":
			clipboard.re_chain_type = chainObjType
			clipboard.re_chain_type_name = "Angle Limit Orientation"
			activeObj.rotation_mode = "XYZ"
			clipboard.frameOrientation = activeObj.rotation_euler
		elif chainObjType in collisionTypes:
			clipboard.re_chain_type = chainObjType
			#initialize clipboard entry
			chainCollision = ChainCollisionData()
			getChainCollision(chainCollision, clipboard)
			for key, value in activeObj.re_chain_chaincollision.items():
				clipboard.re_chain_chaincollision[key] = value
			if activeObj.re_chain_chaincollision.subDataCount != 0:
				clipboard.re_chain_type_name = "Collision Data + Subdata"
				for key, value in activeObj.re_chain_collision_subdata.items():
					clipboard.re_chain_collision_subdata[key] = value
			else:
				clipboard.re_chain_type_name = "Collision Data"
				
		else:
			showErrorMessageBox("A chain object must be selected.")
			return{'CANCELLED'}
		self.report({"INFO"},"Copied properties of " + str(clipboard.re_chain_type_name)+" object to clipboard.")
		return {'FINISHED'}

class WM_OT_PasteChainProperties(Operator):
	bl_label = "Paste"
	bl_idname = "re_chain.paste_chain_properties"
	bl_options = {'UNDO'}
	bl_context = "objectmode"
	bl_description = "Paste properties from a chain object to selected objects. The type of chain object must be the same as the object copied from"
	@classmethod
	def poll(cls, context):
		return bpy.context.selected_objects != []
	
	def execute(self, context):
		clipboard = bpy.context.scene.re_chain_clipboard
		#activeObj = bpy.context.active_object
		for activeObj in bpy.context.selected_objects:
			chainObjType = activeObj.get("TYPE",None)
			
			
			collisionTypes = [
				"RE_CHAIN_COLLISION_SINGLE",
				"RE_CHAIN_COLLISION_CAPSULE_ROOT",
				]
			if clipboard.re_chain_type == chainObjType:
				if chainObjType == "RE_CHAIN_HEADER":
					for key, value in clipboard.re_chain_header.items():
						activeObj.re_chain_header[key] = value
				elif chainObjType == "RE_CHAIN_WINDSETTINGS":
					for key, value in clipboard.re_chain_windsettings.items():
						activeObj.re_chain_windsettings[key] = value
					
				elif chainObjType == "RE_CHAIN_CHAINSETTINGS":
					for key, value in clipboard.re_chain_chainsettings.items():
						activeObj.re_chain_chainsettings[key] = value
				
				elif chainObjType == "RE_CHAIN_CHAINGROUP":
					for key, value in clipboard.re_chain_chaingroup.items():
						activeObj.re_chain_chaingroup[key] = value
						
				elif chainObjType == "RE_CHAIN_NODE":
					for key, value in clipboard.re_chain_chainnode.items():
						activeObj.re_chain_chainnode[key] = value
					#Force update functions to run
					activeObj.re_chain_chainnode.angleLimitRad = activeObj.re_chain_chainnode.angleLimitRad
					activeObj.re_chain_chainnode.angleMode = activeObj.re_chain_chainnode.angleMode
					activeObj.re_chain_chainnode.collisionRadius = activeObj.re_chain_chainnode.collisionRadius

				elif chainObjType == "RE_CHAIN_JIGGLE":
					for key, value in clipboard.re_chain_chainjiggle.items():
						activeObj.re_chain_chainjiggle[key] = value
						
				elif chainObjType == "RE_CHAIN_LINK":
					for key, value in clipboard.re_chain_chainlink.items():
						activeObj.re_chain_chainlink[key] = value
						
				elif chainObjType == "RE_CHAIN_LINK_COLLISION":
					for key, value in clipboard.re_chain_chainlink_collision.items():
						activeObj.re_chain_chainlink_collision[key] = value
					activeObj.re_chain_chainlink_collision.collisionRadius = activeObj.re_chain_chainlink_collision.collisionRadius
				elif chainObjType == "RE_CHAIN_NODE_FRAME":
					activeObj.rotation_mode = "XYZ"
					activeObj.rotation_euler =	clipboard.frameOrientation
				
				elif chainObjType in collisionTypes:
					for key, value in clipboard.re_chain_chaincollision.items():
						activeObj.re_chain_chaincollision[key] = value
						
					if clipboard.re_chain_chaincollision.subDataCount != 0:
						for key, value in clipboard.re_chain_collision_subdata.items():
							activeObj.re_chain_collision_subdata[key] = value
					#I know this looks pointless but the purpose of this is force the update function to trigger, otherwise the position doesn't update
					activeObj.re_chain_chaincollision.collisionOffset = activeObj.re_chain_chaincollision.collisionOffset
					activeObj.re_chain_chaincollision.endCollisionOffset = activeObj.re_chain_chaincollision.endCollisionOffset
					activeObj.re_chain_chaincollision.radius = activeObj.re_chain_chaincollision.radius
				tag_redraw(bpy.context)#Redraw property panel
				self.report({"INFO"},"Pasted properties of " + str(clipboard.re_chain_type_name)+" object from clipboard.")
			else:
				showErrorMessageBox("The contents stored in the clipboard can't be applied to the selected object.")
		
		return {'FINISHED'}

class WM_OT_AlignChainsToBones(Operator):
	bl_label = "Align Chains to Bones"
	bl_idname = "re_chain.align_chains_to_bone"
	bl_description = "Reset node positions to align to bones. Also synchronizes collision offsets with their location"

	def execute(self, context):
		alignChains()
		syncCollisionOffsets()
		alignCollisions()
		self.report({"INFO"},"Aligned chain objects to bones.")
		return {'FINISHED'}

def hasChildNode(obj):
	result = False
	for child in obj.children:
		if child.get("TYPE",None) == "RE_CHAIN_NODE":
			result = True
			break
	return result

class WM_OT_AlignFrames(Operator):
	bl_label = "Align Angle Limits to Next Node"
	bl_idname = "re_chain.align_frames"
	bl_description = "Aligns each angle limit direction with the next node in the chain. Note that additional adjustments may be required for the angle limit to work properly. You can select chain group objects to alter only specific groups"
	bl_context = "objectmode"
	bl_options = {'UNDO'}
	def execute(self, context):
		chainGroupList = []#List of lists of nodes
		#If objects are already selected and chain groups are in the selection, only alter those chain groups
		if bpy.context.selected_objects != []:
			for selectedObject in bpy.context.selected_objects:
				if selectedObject.get("TYPE",None) == "RE_CHAIN_CHAINGROUP":
					for childObject in selectedObject.children:
						if childObject.get("TYPE",None) == "RE_CHAIN_NODE":		
							currentNode = childObject
							currentNodeObjList = [childObject]
							while hasChildNode(currentNode):
								for child in currentNode.children:
									if child.get("TYPE",None) == "RE_CHAIN_NODE":
										currentNodeObjList.append(child)
										currentNode = child
							chainGroupList.append(currentNodeObjList)
		
		if chainGroupList == []:#No chain group objects selected
			chainCollection = bpy.context.scene.re_chain_toolpanel.chainCollection
			if chainCollection != None:
				for selectedObject in chainCollection.all_objects:
					if selectedObject.get("TYPE",None) == "RE_CHAIN_CHAINGROUP":
						for childObject in selectedObject.children:
							if childObject.get("TYPE",None) == "RE_CHAIN_NODE":		
								currentNode = childObject
								currentNodeObjList = [childObject]
								while hasChildNode(currentNode):
									for child in currentNode.children:
										if child.get("TYPE",None) == "RE_CHAIN_NODE":
											currentNodeObjList.append(child)
											currentNode = child
								chainGroupList.append(currentNodeObjList)
		if chainGroupList != []:
			for chainGroup in chainGroupList:
				lastNodeIndex = len(chainGroup) -1
				for nodeIndex, chainNode in enumerate(chainGroup):
					frame = None
					for child in chainNode.children:
						if child.get("TYPE",None) == "RE_CHAIN_NODE_FRAME":
							frame = child
					
					
					armature = chainNode.constraints["BoneName"].target
					boneName = str(chainNode.constraints["BoneName"].subtarget)
					
					
					if nodeIndex == 0 and nodeIndex == lastNodeIndex:
						#Get armature bone, not pose bone
						#Point X axis away from bone tail
						
						a = armature.matrix_world @ armature.data.bones[boneName].head_local
						b = armature.matrix_world @ armature.data.bones[boneName].tail_local
						
						direction  = (a - b).normalized()
						axis_align = Vector((1.0, 0.0, 0.0))
						
						angle = axis_align.angle(direction)
						axis  = axis_align.cross(direction)
						
						
						q = Quaternion(axis, angle)
						
					else:
						if nodeIndex != lastNodeIndex:
							#Point frame towards next bone head
							targetBoneName = chainGroup[nodeIndex+1].constraints["BoneName"].subtarget
							a = armature.matrix_world @ armature.data.bones[boneName].head_local
							b = armature.matrix_world @ armature.data.bones[targetBoneName].head_local
							direction  = (b - a).normalized()
							axis_align = Vector((1.0, 0.0, 0.0))
							
							angle = axis_align.angle(direction)
							axis  = axis_align.cross(direction)
							
							q = Quaternion(axis, angle)
					if frame != None:	
						frame.rotation_mode = "XYZ"
						frame.rotation_euler = q.to_euler()
						#Apply additional local rotation to X axis, this is kind of an ugly solution but easier than messing with the matrices						
						frame.rotation_euler.rotate_axis("X", radians(90))
						frame.matrix_basis = chainNode.matrix_world.inverted() @ frame.matrix_basis
						frame.location = chainNode.location
						frame.scale = chainNode.scale
			self.report({"INFO"},"Aligned angle limit directions.")
			return {'FINISHED'}
		else:
			showErrorMessageBox("No chains found in selection or collection.")
			return {'CANCELLED'}
	@classmethod
	def poll(self,context):
		return bpy.context.scene.re_chain_toolpanel.chainCollection is not None
class WM_OT_PointFrame(Operator):
	bl_label = "Point Frame to Selected"
	bl_idname = "re_chain.point_frame"
	bl_options = {'INTERNAL'}
	def execute(self, context):
		pass#TODO

		return {'FINISHED'}
	
class WM_OT_ApplyChainSettingsPreset(Operator):
	bl_label = "Apply Chain Settings Preset"
	bl_idname = "re_chain.apply_chain_settings_preset"
	bl_description = "Apply preset to selected chain settings objects"
	def execute(self, context):
		enumValue = bpy.context.scene.re_chain_toolpanel.chainSettingsPresets
		finished = False
		presetsPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets")    
		#activeObj = bpy.context.active_object
		print("Reading Preset: " + enumValue)
		for activeObj in bpy.context.selected_objects:
			finished = readPresetJSON(os.path.join(presetsPath,enumValue),activeObj)
		tag_redraw(bpy.context)
		if finished:
			self.report({"INFO"},"Applied chain settings preset.")
			return {'FINISHED'}
		else:
			return {'CANCELLED'}

class WM_OT_ApplyChainGroupPreset(Operator):
	bl_label = "Apply Chain Group Preset"
	bl_idname = "re_chain.apply_chain_group_preset"
	bl_description = "Apply preset to selected chain group objects"
	def execute(self, context):
		enumValue = bpy.context.scene.re_chain_toolpanel.chainGroupPresets
		
		presetsPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets")    
		finished = False
		#activeObj = bpy.context.active_object
		print("Reading Preset: " + enumValue)
		for activeObj in bpy.context.selected_objects:
			finished = readPresetJSON(os.path.join(presetsPath,enumValue),activeObj)
		tag_redraw(bpy.context)
		if finished:
			self.report({"INFO"},"Applied chain group preset.")
			return {'FINISHED'}
		else:
			return {'CANCELLED'}

class WM_OT_ApplyChainNodePreset(Operator):
	bl_label = "Apply Chain Node Preset"
	bl_idname = "re_chain.apply_chain_node_preset"
	bl_description = "Apply preset to selected chain node objects. Note that frame orientations are not changed by presets"
	def execute(self, context):
		enumValue = bpy.context.scene.re_chain_toolpanel.chainNodePresets
		
		presetsPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets")    
		#activeObj = bpy.context.active_object
		finished = False
		print("Reading Preset: " + enumValue)
		for activeObj in bpy.context.selected_objects:
			if activeObj.get("TYPE",None) == "RE_CHAIN_NODE":
				currentNode = activeObj
				nodeObjList = [currentNode]
				if bpy.context.scene.re_chain_toolpanel.applyPresetToChildNodes:
					while len(currentNode.children) > 1:
						for child in currentNode.children:
							if child.get("TYPE",None) == "RE_CHAIN_NODE":
								nodeObjList.append(child)
								currentNode = child
				#print(nodeObjList)
				for nodeObj in nodeObjList:
					finished = readPresetJSON(os.path.join(presetsPath,enumValue),nodeObj)
				tag_redraw(bpy.context)
		if finished:
			self.report({"INFO"},"Applied chain node preset.")
			return {'FINISHED'}
		else:
			showErrorMessageBox("Must select a chain node in order to apply the preset to it.")
			return {'CANCELLED'}
class WM_OT_ApplyWindSettingsPreset(Operator):
	bl_label = "Apply Wind Settings Preset"
	bl_idname = "re_chain.apply_wind_settings_preset"
	bl_description = "Apply preset to selected wind settings objects"
	def execute(self, context):
		enumValue = bpy.context.scene.re_chain_toolpanel.chainWindSettingsPresets
		
		presetsPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets")    
		finished = False
		print("Reading Preset: " + enumValue)
		for activeObj in bpy.context.selected_objects:
			finished = readPresetJSON(os.path.join(presetsPath,enumValue),activeObj)
		tag_redraw(bpy.context)
		if finished:
			self.report({"INFO"},"Applied wind settings preset.")
			return {'FINISHED'}
		else:
			return {'CANCELLED'}

class WM_OT_OpenPresetFolder(Operator):
	bl_label = "Open Preset Folder"
	bl_description = "Opens the preset folder in File Explorer"
	bl_idname = "re_chain.open_preset_folder"

	def execute(self, context):
		presetsPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets")
		os.startfile(presetsPath)
		return {'FINISHED'}

class WM_OT_SavePreset(Operator):
	bl_label = "Save Selected As Preset"
	bl_idname = "re_chain.save_selected_as_preset"
	bl_context = "objectmode"
	bl_description = "Save selected chain object as a preset for easy reuse and sharing. Presets can be accessed using the Open Preset Folder button"
	presetName : bpy.props.StringProperty(name = "Enter Preset Name",default = "newPreset")
	
	@classmethod
	def poll(self,context):
		return context.active_object is not None
	
	def execute(self, context):
		finished = saveAsPreset(context.selected_objects, self.presetName)
		if finished:
			self.report({"INFO"},"Saved preset.")
			return {'FINISHED'}
		else:
			return {'CANCELLED'}
	def invoke(self,context,event):
		return context.window_manager.invoke_props_dialog(self)

		return {'FINISHED'}
class WM_OT_CreateChainBoneGroup(Operator):
	bl_label = "Create Bone Group From Chains"
	bl_idname = "re_chain.create_chain_bone_group"
	bl_description = "Creates a bone group on the armature of all chain bones and colors them.\nNOTE: In Blender 4.0+, bone groups don't exist anymore so this will only color the bones"
	def execute(self, context):
		armature = None
		if bpy.context.active_object.type == "ARMATURE":
			armature = bpy.context.active_object
		else:
			for obj in bpy.data.objects:
				if armature != None:
					self.report({"WARNING"},"More than one armature was found in the scene. Select an armature before using this button.")
					return {'CANCELLED'}
				if obj.type == "ARMATURE":
					armature = obj
		if armature != None:
			if bpy.app.version < (4,0,0):
				if armature.pose.bone_groups.get("Chain Bones",None) != None:
				    boneGroup = armature.pose.bone_groups["Chain Bones"]
				else:
				    boneGroup = armature.pose.bone_groups.new(name = "Chain Bones")
				boneGroup.color_set = "THEME03"
			try:
				chainBoneList = [obj.constraints["BoneName"].subtarget for obj in bpy.data.objects if obj.get("TYPE",None) == "RE_CHAIN_NODE"]
			except:
				chainBoneList = []
			for chainBone in chainBoneList:
				if bpy.app.version < (4,0,0):
					poseBone = armature.pose.bones.get(chainBone,None)
					if poseBone != None:
						poseBone.bone_group = boneGroup
				else:
					bone = armature.data.bones[chainBone]
					bone.color.palette = "THEME03"
			self.report({"INFO"},"Created bone group on armature from chain bones.")
			return {'FINISHED'}
		else:
			self.report({"WARNING"},"No armatures were found in the scene.")
			return {'CANCELLED'}


class WM_OT_SwitchToPoseMode(Operator):#Made a button for this to make it clear that chains have to be created in pose mode
	bl_label = "Switch to Pose Mode"
	bl_description = "Switch to Pose Mode to add new chain bones and chain collisions"
	bl_idname = "re_chain.switch_to_pose"

	def execute(self, context):
		try:
			armature = None
			if bpy.context.active_object != None and bpy.context.active_object.type == "ARMATURE":
				armature = bpy.context.active_object
			else:
				for obj in bpy.context.scene.objects:
					if obj.type == "ARMATURE":
						armature = obj
						break
			if armature != None:
				bpy.ops.object.select_all(action='DESELECT')
				bpy.context.view_layer.objects.active = armature
					
				bpy.ops.object.mode_set(mode='POSE')
		except:
			pass
		return {'FINISHED'}
	
class WM_OT_SwitchToObjectMode(Operator):#Made a button for this to make it clear that chains have to be configured in object mode
	bl_label = "Switch to Object Mode"
	bl_description = "Switch to Object Mode to configure chain objects"
	bl_idname = "re_chain.switch_to_object"

	def execute(self, context):
		try:
			bpy.ops.object.mode_set(mode='OBJECT')
		except:
			pass
		return {'FINISHED'}
	
class WM_OT_HideNonNodes(Operator):
	bl_label = "Hide Non Nodes"
	bl_description = "Hide all objects that aren't chain nodes to make selecting and configuring them easier. Press the \"Unhide All\" button to unhide or check the Viewports box in the Object tab under Visibility"
	bl_idname = "re_chain.hide_non_nodes"
	bl_options = {'UNDO'}
	def execute(self, context):
		for obj in bpy.context.scene.objects:
			if obj.get("TYPE",None) != "RE_CHAIN_NODE" and obj.get("TYPE",None) != "RE_CHAIN_NODE_FRAME_HELPER":
				obj.hide_viewport = True
			else:
				if not obj.get("isLastNode") and bpy.context.scene.re_chain_toolpanel.hideLastNodeAngleLimit:
					obj.hide_viewport = False
		self.report({"INFO"},"Hid all non chain node objects.")
		return {'FINISHED'}

class WM_OT_HideNonCollisions(Operator):
	bl_label = "Hide Non Collisions"
	bl_description = "Hide all objects that aren't collision spheres or capsules to make selecting and configuring them easier. Press the \"Unhide All\" button to unhide or check the Viewports box in the Object tab under Visibility"
	bl_idname = "re_chain.hide_non_collisions"
	bl_options = {'UNDO'}
	def execute(self, context):
		
		for obj in bpy.context.scene.objects:
			objType = obj.get("TYPE",None)
			if objType == "RE_CHAIN_COLLISION_SINGLE" or objType == "RE_CHAIN_COLLISION_CAPSULE_ROOT" or objType == "RE_CHAIN_COLLISION_CAPSULE_START" or objType == "RE_CHAIN_COLLISION_CAPSULE_END" :
				obj.hide_viewport = False
			else:
				obj.hide_viewport = True
		self.report({"INFO"},"Hid all non collision objects.")
		return {'FINISHED'}
class WM_OT_HideNonAngleLimits(Operator):
	bl_label = "Hide Non Angle Limits"
	bl_description = "Hide all objects that aren't chain node angle limits to make selecting and configuring them easier. Press the \"Unhide All\" button to unhide or check the Viewports box in the Object tab under Visibility"
	bl_idname = "re_chain.hide_non_angle_limits"
	bl_options = {'UNDO'}
	def execute(self, context):
		for obj in bpy.context.scene.objects:
			if obj.get("TYPE",None) != "RE_CHAIN_NODE_FRAME" and obj.get("TYPE",None) != "RE_CHAIN_NODE_FRAME_HELPER":
					obj.hide_viewport = True
			else:
				if not obj.get("isLastNode") and bpy.context.scene.re_chain_toolpanel.hideLastNodeAngleLimit:
					obj.hide_viewport = False
				#obj.show_name = bpy.context.scene.re_chain_toolpanel.showNodeNames
				
		self.report({"INFO"},"Hid all non chain angle limit objects.")
		return {'FINISHED'}
class WM_OT_UnhideAll(Operator):
	bl_label = "Unhide All"
	bl_description = "Unhide all objects hidden with \"Hide Non Nodes\" or \"Hide Non Angle Limits\""
	bl_idname = "re_chain.unhide_all"
	bl_options = {'UNDO'}
	def execute(self, context):
		for obj in bpy.context.scene.objects:
			if obj.get("TYPE",None) != "RE_CHAIN_NODE_FRAME_HELPER":
				obj.hide_viewport = False
			else:
				if bpy.context.scene.re_chain_toolpanel.showAngleLimitCones and not (obj.get("isLastNode") and bpy.context.scene.re_chain_toolpanel.hideLastNodeAngleLimit):
					obj.hide_viewport = False
		self.report({"INFO"},"Unhid all objects.")
		return {'FINISHED'}

class WM_OT_RenameBoneChain(Operator):
	bl_label = "Rename Bone Chain"
	bl_description = "Renames all bones that are a child of the selected bone. The bones cannot be branching. Note that chain bone names are not signifcant, they can be named in any way and still work"
	bl_idname = "re_chain.rename_bone_chain"
	bl_context = "posemode"
	bl_options = {'UNDO'}
	newBoneChainName : bpy.props.StringProperty(name = "Enter Chain Name",default = "newBoneChain")
	
	@classmethod
	def poll(self,context):
		return context.active_object is not None
	def execute(self, context):
		selected = bpy.context.selected_pose_bones
		chainList = []
		if len(selected) == 1:
			startBone = selected[0]
			
			chainList = startBone.children_recursive
			chainList.insert(0,startBone)
			#print(chainList)
		else:
			showErrorMessageBox("Select only the chain start bone.")
			return {'CANCELLED'}
		valid = True
		
		for bone in chainList:
			if len(bone.children) > 1:
				valid = False
		
		if not valid:
			showErrorMessageBox("Cannot have branching bones in a chain.")
			return {'CANCELLED'}
		else:
			
			#Attempt to get chain group from first node if it exists
			nodeObj = bpy.data.objects.get(chainList[0].name,None)
			if nodeObj != None and nodeObj.get("TYPE",None) == "RE_CHAIN_NODE":
				if nodeObj.parent != None and nodeObj.parent.get("TYPE",None) == "RE_CHAIN_CHAINGROUP":
					try:
						#Attempt to split group index from chain group name, if it can't, find next available chain group number
						nodeObj.parent.name = "CHAIN_GROUP_" + str(nodeObj.parent.name.split[2])+"_"+self.newBoneChainName
					except:
						currentChainGroupIndex = 0
						subName = "CHAIN_GROUP_"+str(currentChainGroupIndex).zfill(2)
						while(checkNameUsage(subName,checkSubString=True)):
							currentChainGroupIndex +=1
							subName = "CHAIN_GROUP_"+str(currentChainGroupIndex).zfill(2)
						nodeObj.parent.name = subName+"_"+self.newBoneChainName
			lastIndex = len(chainList)-1
			for index,bone in enumerate(chainList):
				if index != lastIndex:
					newBoneName = self.newBoneChainName+"_"+str(index).zfill(2)
				else:
					newBoneName = self.newBoneChainName+"_end"
				
				
				#If a chain node already exists, rename the chain node
				nodeObj = bpy.data.objects.get(bone.name,None)
				if nodeObj != None and nodeObj.get("TYPE",None) == "RE_CHAIN_NODE":
					nodeObj.name = newBoneName
				
				nodeAngleLimitObj = bpy.data.objects.get(bone.name+"_ANGLE_LIMIT",None)
				if nodeAngleLimitObj != None and nodeAngleLimitObj.get("TYPE",None) == "RE_CHAIN_NODE_FRAME":
					nodeAngleLimitObj.name = newBoneName+"_ANGLE_LIMIT"
				elif nodeObj != None:#In case of blender . suffix
					for child in nodeObj.children:
						if child.get("TYPE",None) == "RE_CHAIN_NODE_FRAME":
							child.name = newBoneName+"_ANGLE_LIMIT"
							
				nodeJiggleObj = bpy.data.objects.get(bone.name+"_JIGGLE",None)
				if nodeJiggleObj != None and nodeJiggleObj.get("TYPE",None) == "RE_CHAIN_JIGGLE":
					nodeJiggleObj.name = newBoneName+"_JIGGLE"
				elif nodeObj != None:#In case of blender . suffix
					for child in nodeObj.children:
						if child.get("TYPE",None) == "RE_CHAIN_JIGGLE":
							child.name = newBoneName+"_JIGGLE"
				
				nodeAngleLimitConeObj = bpy.data.objects.get(bone.name+"_ANGLE_LIMIT_HELPER",None)
				if nodeAngleLimitConeObj != None and nodeAngleLimitConeObj.get("TYPE",None) == "RE_CHAIN_NODE_FRAME_HELPER":
					nodeAngleLimitConeObj.name = newBoneName+"_ANGLE_LIMIT_HELPER"
				elif nodeObj != None and nodeAngleLimitObj != None:#In case of blender . suffix
					for child in nodeAngleLimitObj.children:
						if child.get("TYPE",None) == "RE_CHAIN_NODE_FRAME_HELPER":
							child.name = newBoneName+"_ANGLE_LIMIT_HELPER"
				bone.name = newBoneName
		self.report({"INFO"},"Renamed bone chain.")
		return {'FINISHED'}
	
	def invoke(self,context,event):
		return context.window_manager.invoke_props_dialog(self)
	
class WM_OT_ApplyAngleLimitRamp(Operator):
	bl_label = "Apply Angle Limit Ramp"
	bl_description = "Apply an increasing angle limit on each chain node as it gets further away.\nA chain group must be selected. If multiple chain groups are selected, the angle limits will be applied to all of them"
	bl_idname = "re_chain.apply_angle_limit_ramp"
	bl_context = "objectmode"
	bl_options = {'UNDO'}
	maxAngleLimit : bpy.props.FloatProperty(name = "Max Angle Limit",
										 description = "The maximum angle limit radius after the max iteration number is reached. For example, if the max angle limit is 60 and the max iteration is 4, the first node angle limit will be 15, the second will be 30 and so on. Once the max iteration is reached, all nodes after that will be the max angle limit value",
										 default = 1.047198,#60 degrees
										 min=0.0,
										 soft_max=180.0,
										 subtype = "ANGLE",)
	maxIteration : bpy.props.IntProperty(name = "Max Iteration",
									  description = "The amount of chain nodes until the angle limit radius is at it's maximum value",
									  default = 4,
									  min = 1)
	
	@classmethod
	def poll(self,context):
		return context.active_object is not None and (context.active_object.get("TYPE") == "RE_CHAIN_CHAINGROUP" or context.active_object.get("TYPE") == "RE_CHAIN_SUBGROUP")
	def execute(self, context):
		chainGroupList = []#List of lists of nodes
		for selectedObject in bpy.context.selected_objects:
			if selectedObject.get("TYPE",None) == "RE_CHAIN_CHAINGROUP" or selectedObject.get("TYPE",None) == "RE_CHAIN_SUBGROUP":
				for childObject in selectedObject.children:
					if childObject.get("TYPE",None) == "RE_CHAIN_NODE":		
						currentNode = childObject
						currentNodeObjList = [childObject]
						while len(currentNode.children) > 1:
							for child in currentNode.children:
								if child.get("TYPE",None) == "RE_CHAIN_NODE":
									currentNodeObjList.append(child)
									currentNode = child
						chainGroupList.append(currentNodeObjList)
				#print(nodeObjList)
		if chainGroupList != []:
			angleLimitStep = self.maxAngleLimit / self.maxIteration
			for chainGroup in chainGroupList:
				for nodeIndex, chainNode in enumerate(chainGroup):
					if nodeIndex + 1 < self.maxIteration:
						chainNode.re_chain_chainnode.angleLimitRad = angleLimitStep * (nodeIndex + 1)
					else:
						chainNode.re_chain_chainnode.angleLimitRad = self.maxAngleLimit
			self.report({"INFO"},"Applied angle limit ramp to selected chain group(s).")
			return {'FINISHED'}
		else:
			showErrorMessageBox("Chain Group object(s) must be selected to apply an angle limit ramp.")
			return {'CANCELLED'}
	
	def invoke(self,context,event):
		return context.window_manager.invoke_props_dialog(self)
	

class WM_OT_AlignBoneTailsToAxis(Operator):
	bl_label = "Align Tails to Axis"
	bl_description = "Aligns all bones that are a child of the selected bone to a specified axis. This is how Capcom usually has their chain bones and it may help you get a better result with angle limits"
	bl_idname = "re_chain.align_bone_tails_to_axis"
	bl_context = "posemode"
	bl_options = {'UNDO'}
	alignAxis: bpy.props.EnumProperty(
		name="Tail Align Axis",
		description="Aligns bone tails to the bone head on the specified axis",
		items=[ ("X", "X", ""),
				("-X", "-X", ""),
				("Y", "Y", ""),
				("-Y", "-Y", ""),
				("Z", "Z", ""),
				("-Z", "-Z", "")
				],
		default = "Z")
		
	
	@classmethod
	def poll(self,context):
		return context.active_object is not None
	def execute(self, context):
		selected = bpy.context.selected_pose_bones
		chainList = []
		if len(selected) == 1:
			startBone = selected[0]
			
			chainList = startBone.children_recursive
			chainList.insert(0,startBone)
		else:
			showErrorMessageBox("Select only the chain start bone.")
			return {'CANCELLED'}
		
		armature = startBone.id_data
		
		if self.alignAxis == "X":
			alignVector = Vector((1.0,0.0,0.0))
		elif self.alignAxis == "-X":
			alignVector = Vector((-1.0,0.0,0.0))
		elif self.alignAxis == "Y":
			alignVector = Vector((0.0,1.0,0.0))
		elif self.alignAxis == "-Y":
			alignVector = Vector((0.0,-1.0,0.0))
		elif self.alignAxis == "Z":
			alignVector = Vector((0.0,0.0,1.0))
		elif self.alignAxis == "-Z":
			alignVector = Vector((0.0,0.0,-1.0))
		
		
		bpy.ops.object.mode_set(mode="EDIT")#Have to be in edit mode to alter edit_bones
		#Disconnect all bones from eachother before changing tails
		for bone in chainList:
			editBone = armature.data.edit_bones[bone.name]
			editBone.use_connect = False #Disconnect bones if they're already connected
		
		for bone in chainList:
			editBone = armature.data.edit_bones[bone.name]		
			#boneLength = sqrt((editBone.tail[0] - editBone.head[0])**2 + (editBone.tail[1] - editBone.head[1])**2 + (editBone.tail[2] - editBone.head[2])**2)
			boneLength = editBone.length
			tailAddVector = Vector((boneLength,boneLength,boneLength)) * alignVector
			armature.data.edit_bones[bone.name].tail = editBone.head + tailAddVector
		bpy.ops.object.mode_set(mode="POSE")#Switch back to pose mode after finished editing bones
		self.report({"INFO"},"Aligned bone tails to axis.")
		return {'FINISHED'}
	def invoke(self,context,event):
		return context.window_manager.invoke_props_dialog(self)

def getChainSettingObjects(self,context):
	objectList = []
	if context.scene.re_chain_toolpanel.chainCollection != None:
		for obj in context.active_object.users_collection[0].all_objects:
			if obj.get("TYPE") == "RE_CHAIN_CHAINSETTINGS":
				objectList.append((obj.name,obj.name,""))
	return objectList
class WM_OT_CreateChainSubGroup(Operator):
	bl_label = "Create Chain Sub Group"
	bl_description = "Create a sub group from a chain group. Sub groups allow for a chain group to use a different set of chain settings and node parameters dependent on it's Sub Group ID.\nA chain group must be selected"
	bl_idname = "re_chain.create_sub_group"
	bl_context = "objectmode"
	bl_options = {'UNDO'}
	chainSettingObjectName: bpy.props.EnumProperty(
		name="",
		description="Choose which chain setting the newly created subgroup will use",
		items= getChainSettingObjects
		)
	
	subGroupID : bpy.props.IntProperty(name = "Sub Group ID",
									  description = "The ID to assign to this sub group. If the chosen ID is already in use, the next unused subgroup ID will be used",
									  default = 1,
									  min = 1)
	multiplyAngleLimit : bpy.props.FloatProperty(name = "Angle Limit Multiplier",
										 description = "Multiply the angle limit values of the chain group by this value.\nSet to 1.0 to keep angle limits the same",
										 default = .60,
										 min=0.0,
										 soft_max=4.0)
	
	def draw(self,context):
		layout = self.layout
		layout.label(text="Chain Setting")
		layout.prop(self,"chainSettingObjectName",icon = "DECORATE_LINKED")
		layout.prop(self,"subGroupID")
		layout.prop(self,"multiplyAngleLimit")
		
	@classmethod
	def poll(self,context):
		return context.active_object is not None and context.active_object.get("TYPE") == "RE_CHAIN_CHAINGROUP"
	def execute(self, context):
		chainCollection = context.active_object.users_collection[0]
		chainSettingsObj = bpy.data.objects.get(self.chainSettingObjectName,None)
		chainGroupList = []#List of lists of nodes
		chainGroupObjList = []
		for selectedObject in bpy.context.selected_objects:
			if selectedObject.get("TYPE",None) == "RE_CHAIN_CHAINGROUP":
				chainGroupObjList.append(selectedObject)
				for childObject in selectedObject.children:
					if childObject.get("TYPE",None) == "RE_CHAIN_NODE":		
						currentNode = childObject
						currentNodeObjList = [childObject]
						while len(currentNode.children) > 1:
							for child in currentNode.children:
								if child.get("TYPE",None) == "RE_CHAIN_NODE":
									currentNodeObjList.append(child)
									currentNode = child
						chainGroupList.append(currentNodeObjList)
				#print(nodeObjList)
		if chainGroupList != [] and chainSettingsObj != None:
			
			for index, nodeList in enumerate(chainGroupList):
				
				chainGroupObj = chainGroupObjList[index]
				#get group index from chain group obj
				try:
					groupIndex = int(chainGroupObj.name.split("CHAIN_GROUP_")[1].split("_")[0])
				except:
					groupIndex = 0
				
				currentSubGroupID = self.subGroupID
				#Check if subgroup ID is already used with chain group
				idList = [chainObj.re_chain_chainsubgroup.subGroupID for chainObj in chainCollection.all_objects if (chainObj.get("TYPE",None) == "RE_CHAIN_SUBGROUP" and chainObj.re_chain_chainsubgroup.parentGroup == chainGroupObj)]
				idChanged = False
				while idList.count(currentSubGroupID) >= 1:
					currentSubGroupID += 1
					idChanged = True
				if idChanged:
					print("ID of "+ str(self.subGroupID) + " changed to " + str(currentSubGroupID) + " to avoid ID conflicts.")
			
				
				chainSubGroupObj = createEmpty(f"CHAIN_GROUP_{str(groupIndex).zfill(2)}_SUBGROUP_{currentSubGroupID}", [("TYPE","RE_CHAIN_SUBGROUP")],chainSettingsObj,chainCollection)
				chainSubGroupObj.re_chain_chainsubgroup.subGroupID = currentSubGroupID
				chainSubGroupObj.re_chain_chainsubgroup.parentGroup = chainGroupObj
				if bpy.context.mode == "OBJECT":	
					bpy.context.view_layer.objects.active = chainSubGroupObj
				nodeParent = chainSubGroupObj
				for node in nodeList:
					angleLimitObj = None
					angleLimitHelperObj = None
					for child in node.children:
						#find angle limit obj
						if child.get("TYPE") == "RE_CHAIN_NODE_FRAME":
							angleLimitObj = child
							for obj in angleLimitObj.children:
								if obj.get("TYPE") == "RE_CHAIN_NODE_FRAME_HELPER":
									angleLimitHelperObj = obj
									break
							break
					
					#Create copy of node
					newNode = node.copy()
					newNode.show_name = False
					newNode.name = f"SUBGROUP_{currentSubGroupID}_{node.name}"
					chainCollection.objects.link(newNode)
					newNode.parent = nodeParent
					if angleLimitObj != None:
						#Create copy of angle limit obj
						newAngleLimitObj = angleLimitObj.copy()
						newAngleLimitObj.name = f"SUBGROUP_{currentSubGroupID}_{angleLimitObj.name}"
						chainCollection.objects.link(newAngleLimitObj)
						if "Copy Location" in newAngleLimitObj.constraints:
							newAngleLimitObj.constraints["Copy Location"].target = newNode
						if "Copy Scale" in newAngleLimitObj.constraints:
							newAngleLimitObj.constraints["Copy Scale"].target = newNode
						newAngleLimitObj.parent = newNode
						
						if angleLimitHelperObj != None:
							#Create copy of angle limit helper obj
							newAngleLimitHelperObj = angleLimitHelperObj.copy()
							newAngleLimitHelperObj.name = f"SUBGROUP_{currentSubGroupID}_{newAngleLimitHelperObj.name}"
							chainCollection.objects.link(newAngleLimitHelperObj)
							if "REChainGeometryNodes" in newAngleLimitHelperObj.modifiers:
								newAngleLimitHelperObj.modifiers["REChainGeometryNodes"].node_group = getConeGeoNodeTree(isSubGroup=True)
							newAngleLimitHelperObj.parent = newAngleLimitObj
					
					newNode.re_chain_chainnode.angleLimitRad *= self.multiplyAngleLimit 
					nodeParent = newNode
			self.report({"INFO"},"Created chain subgroup.")
			return {'FINISHED'}
		else:
			showErrorMessageBox("Chain Group object(s) must be selected to create a sub group.")
			return {'CANCELLED'}
	
	def invoke(self,context,event):
		return context.window_manager.invoke_props_dialog(self)


#Flags Setters
class AndFlags:
	def __init__(self):
		self.flagDict = {}
		
	def setFlagsFromInt(self,bitFlag):
		for key in self.flagDict:
			self.flagDict[key]["enabled"] = bool(bitFlag & self.flagDict[key]["andFlag"])
			#print(key+" = "+str(self.flagDict[key]["enabled"]))
	
	
	def getIntFromFlags(self):
		intValue = 0
		for key in self.flagDict:
			if self.flagDict[key]["enabled"]:
				intValue += self.flagDict[key]["andFlag"]
		return intValue
	def clearFlags(self,bitFlag):
		for key in self.flagDict:
			self.flagDict[key]["enabled"] = False
class chainGroupAttrFlags(AndFlags):
	def __init__(self):
		self.flagDict = {
			"None":{"enabled":False,"andFlag":0},
			"RootRotation":{"enabled":False,"andFlag":1},
			"AngleLimit":{"enabled":False,"andFlag":2},
			"ExtraNode":{"enabled":False,"andFlag":4},
			"CollisionDefault":{"enabled":False,"andFlag":8},
			"CollisionSelf":{"enabled":False,"andFlag":16},
			"CollisionModel":{"enabled":False,"andFlag":32},
			"CollisionVGround":{"enabled":False,"andFlag":64},
			"CollisionCollider":{"enabled":False,"andFlag":128},
			"CollisionGroup":{"enabled":False,"andFlag":256},
			"EnablePartBlend":{"enabled":False,"andFlag":512},
			"WindDefault":{"enabled":False,"andFlag":1024},
			"TransAnimation":{"enabled":False,"andFlag":2048},
			"AngleLimitRestitution":{"enabled":False,"andFlag":4096},
			"StretchBoth":{"enabled":False,"andFlag":8192},
			"EndRotConstraint":{"enabled":False,"andFlag":16384},
			"EnableEnvWind":{"enabled":False,"andFlag":32768},
			"ScaleAnimation":{"enabled":False,"andFlag":65536},
			"CollisionCharacter":{"enabled":False,"andFlag":131072},
			}
	

class chain2GroupAttrFlags(AndFlags):
	def __init__(self):
		self.flagDict = {
			"None":{"enabled":False,"andFlag":0},
			"RootRotation":{"enabled":False,"andFlag":1},
			"AngleLimit":{"enabled":False,"andFlag":2},
			"ScaleAnimation":{"enabled":False,"andFlag":4},
			"CollisionDefault":{"enabled":False,"andFlag":8},
			"CollisionSelf":{"enabled":False,"andFlag":16},
			"CollisionModel":{"enabled":False,"andFlag":32},
			"CollisionVGround":{"enabled":False,"andFlag":64},
			"CollisionCollider":{"enabled":False,"andFlag":128},
			"CollisionGroup":{"enabled":False,"andFlag":256},
			"EnablePartBlend":{"enabled":False,"andFlag":512},
			"WindDefault":{"enabled":False,"andFlag":1024},
			"TransAnimation":{"enabled":False,"andFlag":2048},
			"AngleLimitRestitution":{"enabled":False,"andFlag":4096},
			"StretchBoth":{"enabled":False,"andFlag":8192},
			"EndRotConstraint":{"enabled":False,"andFlag":16384},
			"EnableEnvWind":{"enabled":False,"andFlag":32768},
			"CollisionCharacter":{"enabled":False,"andFlag":65536},
			"ExtraNode":{"enabled":False,"andFlag":131072},
			"UseBitFlag":{"enabled":False,"andFlag":262144},
			"StretchBothAutoScale":{"enabled":False,"andFlag":524288},
			}

#Chain Group
class WM_OT_SetAttrFlags(Operator):
	bl_label = "Set Attribute Flag"
	bl_description = "Set chain group attribute flags"
	bl_idname = "re_chain.set_attr_flags"
	bl_context = "objectmode"
	bl_options = {'UNDO','INTERNAL'}
	#TODO Add which chain versions can use each flag
	RootRotation : bpy.props.BoolProperty(
		name="Root Rotation",
		description="",
		default = False)
	AngleLimit : bpy.props.BoolProperty(
		name="Angle Limit",
		description="",
		default = False)
	ExtraNode : bpy.props.BoolProperty(
		name="Extra Node",
		description="",
		default = False)
	CollisionDefault : bpy.props.BoolProperty(
		name="Collision Default",
		description="",
		default = False)
	CollisionSelf : bpy.props.BoolProperty(
		name="Collision Self",
		description="",
		default = False)
	CollisionModel : bpy.props.BoolProperty(
		name="Collision Model",
		description="",
		default = False)
	CollisionVGround : bpy.props.BoolProperty(
		name="Collision VGround",
		description="",
		default = False)
	CollisionCollider : bpy.props.BoolProperty(
		name="Collision Collider",
		description="",
		default = False)
	CollisionGroup : bpy.props.BoolProperty(
		name="Collision Group",
		description="",
		default = False)
	EnablePartBlend : bpy.props.BoolProperty(
		name="Enable Part Blend",
		description="",
		default = False)
	WindDefault : bpy.props.BoolProperty(
		name="Wind Default",
		description="",
		default = False)
	TransAnimation : bpy.props.BoolProperty(
		name="Trans Animation",
		description="",
		default = False)
	AngleLimitRestitution : bpy.props.BoolProperty(
		name="Angle Limit Restitution",
		description="",
		default = False)
	StretchBoth : bpy.props.BoolProperty(
		name="Stretch Both",
		description="",
		default = False)
	EndRotConstraint : bpy.props.BoolProperty(
		name="End Rot Constraint",
		description="",
		default = False)
	EnableEnvWind : bpy.props.BoolProperty(
		name="Enable Env Wind",
		description="",
		default = False)
	ScaleAnimation : bpy.props.BoolProperty(
		name="Scale Animation",
		description="",
		default = False)
	CollisionCharacter : bpy.props.BoolProperty(
		name="Collision Character",
		description="",
		default = False)
	#chain2
	UseBitFlag : bpy.props.BoolProperty(
		name="Use Bit Flag",
		description="",
		default = False)
	StretchBothAutoScale : bpy.props.BoolProperty(
		name="Stretch Both Auto Scale",
		description="",
		default = False)
	
	def draw(self,context):
		layout = self.layout
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		layout.label(text="Type: chain2" if isChain2 else "Type: chain")
		layout.label(text="Older chain versions may not support all options.",icon = "ERROR")
		layout.prop(self,"RootRotation")
		layout.prop(self,"AngleLimit")
		layout.prop(self,"ExtraNode")
		layout.prop(self,"CollisionDefault")
		layout.prop(self,"CollisionSelf")
		layout.prop(self,"CollisionModel")
		layout.prop(self,"CollisionVGround")
		layout.prop(self,"CollisionCollider")
		layout.prop(self,"CollisionGroup")
		layout.prop(self,"CollisionCharacter")
		layout.prop(self,"EnablePartBlend")
		layout.prop(self,"WindDefault")
		layout.prop(self,"EnableEnvWind")
		layout.prop(self,"TransAnimation")
		layout.prop(self,"AngleLimitRestitution")
		layout.prop(self,"StretchBoth")
		if isChain2:
			layout.prop(self,"StretchBothAutoScale")
		layout.prop(self,"EndRotConstraint")
		layout.prop(self,"ScaleAnimation")
		if isChain2:
			layout.prop(self,"UseBitFlag")
		
	@classmethod
	def poll(self,context):
		return context.active_object is not None and (context.active_object.get("TYPE") == "RE_CHAIN_CHAINGROUP" or context.active_object.get("TYPE") == "RE_CHAIN_CHAINSETTINGS")
	def execute(self, context):
		
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		if isChain2:
			flagClass = chain2GroupAttrFlags()
		else:
			flagClass = chainGroupAttrFlags()
		for key in flagClass.flagDict:
			if hasattr(self,key):
				#print(key)
				flagClass.flagDict[key]["enabled"] = getattr(self,key)
		bitFlag = flagClass.getIntFromFlags()
		
		
		#If more than one object is selected, apply the attribute flag to it if the type is the same
		activeObject = bpy.context.active_object
		if activeObject != None:
			activeObjectType = activeObject.get("TYPE",None)
			if activeObjectType == "RE_CHAIN_CHAINGROUP":
				activeObject.re_chain_chaingroup.attrFlags = bitFlag
			else:
				activeObject.re_chain_chainsettings.groupDefaultAttr = bitFlag
			for selectedObject in bpy.context.selected_objects:
				selectedObjectType = selectedObject.get("TYPE",None)
				if selectedObjectType == activeObjectType:
					if selectedObjectType == "RE_CHAIN_CHAINGROUP":
						selectedObject.re_chain_chaingroup.attrFlags = bitFlag
					else:
						selectedObject.re_chain_chainsettings.groupDefaultAttr = bitFlag
			self.report({"INFO"},"Set attribute flags.")
			tag_redraw(bpy.context)
		return {'FINISHED'}
	
	def invoke(self,context,event):
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		if isChain2:
			flagClass = chain2GroupAttrFlags()
		else:
			flagClass = chainGroupAttrFlags()
		
		flagClass.setFlagsFromInt(context.active_object.re_chain_chaingroup.attrFlags if context.active_object.get("TYPE") == "RE_CHAIN_CHAINGROUP" else context.active_object.re_chain_chainsettings.groupDefaultAttr)
		for key in flagClass.flagDict:
			if hasattr(self,key):
				#print(key)
				setattr(self,key,flagClass.flagDict[key]["enabled"])
			
		return context.window_manager.invoke_props_dialog(self)
	
#Chain Node
class chainNodeAttrFlags(AndFlags):
	def __init__(self):
		self.flagDict = {
			"PartMotionBlend":{"enabled":False,"andFlag":1},
			"Jiggle":{"enabled":False,"andFlag":2},
			}
	
class WM_OT_SetNodeAttrFlags(Operator):
	bl_label = "Set Node Attribute Flag"
	bl_description = "Set chain node attribute flags"
	bl_idname = "re_chain.set_node_attr_flags"
	bl_context = "objectmode"
	bl_options = {'UNDO','INTERNAL'}
	PartMotionBlend : bpy.props.BoolProperty(
		name="Part Motion Blend",
		description="",
		default = False)
	Jiggle : bpy.props.BoolProperty(
		name="Jiggle",
		description="",
		default = False)
	
	def draw(self,context):
		layout = self.layout
		layout.prop(self,"PartMotionBlend")
		layout.prop(self,"Jiggle")
		
	@classmethod
	def poll(self,context):
		return context.active_object is not None and context.active_object.get("TYPE") == "RE_CHAIN_NODE"
	def execute(self, context):
		
	
		flagClass = chainNodeAttrFlags()
		for key in flagClass.flagDict:
			if hasattr(self,key):
				#print(key)
				flagClass.flagDict[key]["enabled"] = getattr(self,key)
		bitFlag = flagClass.getIntFromFlags()
		
		
		#If more than one object is selected, apply the attribute flag to it if the type is the same
		activeObject = bpy.context.active_object
		if activeObject != None:
			activeObjectType = activeObject.get("TYPE",None)
			if activeObjectType == "RE_CHAIN_NODE":
				activeObject.re_chain_chainnode.attrFlags = bitFlag
			
			for selectedObject in bpy.context.selected_objects:
				selectedObjectType = selectedObject.get("TYPE",None)
				if selectedObjectType == "RE_CHAIN_NODE":
					selectedObject.re_chain_chainnode.attrFlags = bitFlag
			self.report({"INFO"},"Set attribute flags.")
			tag_redraw(bpy.context)
		return {'FINISHED'}
	
	def invoke(self,context,event):
		flagClass = chainNodeAttrFlags()
		
		flagClass.setFlagsFromInt(context.active_object.re_chain_chainnode.attrFlags)
		for key in flagClass.flagDict:
			if hasattr(self,key):
				#print(key)
				setattr(self,key,flagClass.flagDict[key]["enabled"])
			
		return context.window_manager.invoke_props_dialog(self)
	
#Chain Settings
class chainSettingsAttrFlags(AndFlags):
	def __init__(self):
		self.flagDict = {
			"Default":{"enabled":False,"andFlag":1},
			"VirtualGroundRoot":{"enabled":False,"andFlag":2},
			"VirtualGroundTarget":{"enabled":False,"andFlag":4},
			"IgnoreSameGroupCollision":{"enabled":False,"andFlag":8},
			"UseReduceDistanceCurve":{"enabled":False,"andFlag":16},#chain2
			#"VirtualGroundMask":{"enabled":False,"andFlag":6},#chain2
			}
	
class WM_OT_SetSettingAttrFlags(Operator):
	bl_label = "Set Settings Attribute Flag"
	bl_description = "Set chain settings attribute flags"
	bl_idname = "re_chain.set_settings_attr_flags"
	bl_context = "objectmode"
	bl_options = {'UNDO','INTERNAL'}
	Default : bpy.props.BoolProperty(
		name="Default",
		description="",
		default = False)
	VirtualGroundRoot : bpy.props.BoolProperty(
		name="Virtual Ground Root",
		description="",
		default = False)
	VirtualGroundTarget : bpy.props.BoolProperty(
		name="Virtual Ground Target",
		description="",
		default = False)
	IgnoreSameGroupCollision : bpy.props.BoolProperty(
		name="Ignore Same Group Collision",
		description="",
		default = False)
	UseReduceDistanceCurve : bpy.props.BoolProperty(
		name="Use Reduce Distance Curve",
		description="",
		default = False)
	"""
	VirtualGroundMask : bpy.props.BoolProperty(
		name="Virtual Ground Mask",
		description="",
		default = False)
	"""
	def draw(self,context):
		isChain2 = context.scene.re_chain_toolpanel.chainFileType == "chain2"
		layout = self.layout
		layout.prop(self,"Default")
		layout.prop(self,"VirtualGroundRoot")
		layout.prop(self,"VirtualGroundTarget")
		layout.prop(self,"IgnoreSameGroupCollision")
		if isChain2:
			layout.prop(self,"UseReduceDistanceCurve")
			#layout.prop(self,"VirtualGroundMask")
		
		
	@classmethod
	def poll(self,context):
		return context.active_object is not None and context.active_object.get("TYPE") == "RE_CHAIN_CHAINSETTINGS"
	def execute(self, context):
		
	
		flagClass = chainSettingsAttrFlags()
		for key in flagClass.flagDict:
			if hasattr(self,key):
				#print(key)
				flagClass.flagDict[key]["enabled"] = getattr(self,key)
		bitFlag = flagClass.getIntFromFlags()
		
		
		#If more than one object is selected, apply the attribute flag to it if the type is the same
		activeObject = bpy.context.active_object
		if activeObject != None:
			activeObjectType = activeObject.get("TYPE",None)
			if activeObjectType == "RE_CHAIN_CHAINSETTINGS":
				activeObject.re_chain_chainsettings.settingsAttrFlags = bitFlag
			
			for selectedObject in bpy.context.selected_objects:
				selectedObjectType = selectedObject.get("TYPE",None)
				if selectedObjectType == "RE_CHAIN_CHAINSETTINGS":
					selectedObject.re_chain_chainsettings.settingsAttrFlags = bitFlag
			self.report({"INFO"},"Set attribute flags.")
			tag_redraw(bpy.context)
		return {'FINISHED'}
	
	def invoke(self,context,event):
		flagClass = chainSettingsAttrFlags()
		
		flagClass.setFlagsFromInt(context.active_object.re_chain_chainsettings.settingsAttrFlags)
		for key in flagClass.flagDict:
			if hasattr(self,key):
				#print(key)
				setattr(self,key,flagClass.flagDict[key]["enabled"])
			
		return context.window_manager.invoke_props_dialog(self)
	
#Chain Jiggle
class chainJiggleAttrFlags(AndFlags):
	def __init__(self):
		self.flagDict = {
			"OverrideDamping":{"enabled":False,"andFlag":1},
			}
	
class WM_OT_SetJiggleAttrFlags(Operator):
	bl_label = "Set Jiggle Attribute Flag"
	bl_description = "Set chain jiggle attribute flags"
	bl_idname = "re_chain.set_jiggle_attr_flags"
	bl_context = "objectmode"
	bl_options = {'UNDO','INTERNAL'}
	OverrideDamping : bpy.props.BoolProperty(
		name="Override Damping",
		description="",
		default = False)
	
	def draw(self,context):
		layout = self.layout
		layout.prop(self,"OverrideDamping")
		
	@classmethod
	def poll(self,context):
		return context.active_object is not None and context.active_object.get("TYPE") == "RE_CHAIN_JIGGLE"
	def execute(self, context):
		
	
		flagClass = chainJiggleAttrFlags()
		for key in flagClass.flagDict:
			if hasattr(self,key):
				#print(key)
				flagClass.flagDict[key]["enabled"] = getattr(self,key)
		bitFlag = flagClass.getIntFromFlags()
		
		
		#If more than one object is selected, apply the attribute flag to it if the type is the same
		activeObject = bpy.context.active_object
		if activeObject != None:
			activeObjectType = activeObject.get("TYPE",None)
			if activeObjectType == "RE_CHAIN_JIGGLE":
				activeObject.re_chain_chainjiggle.attrFlags = bitFlag
			
			for selectedObject in bpy.context.selected_objects:
				selectedObjectType = selectedObject.get("TYPE",None)
				if selectedObjectType == "RE_CHAIN_JIGGLE":
					selectedObject.re_chain_chainjiggle.attrFlags = bitFlag
			self.report({"INFO"},"Set attribute flags.")
			tag_redraw(bpy.context)
		return {'FINISHED'}
	
	def invoke(self,context,event):
		flagClass = chainJiggleAttrFlags()
		
		flagClass.setFlagsFromInt(context.active_object.re_chain_chainjiggle.attrFlags)
		for key in flagClass.flagDict:
			if hasattr(self,key):
				#print(key)
				setattr(self,key,flagClass.flagDict[key]["enabled"])
			
		return context.window_manager.invoke_props_dialog(self)
	
	
class WM_OT_SetCFILPath(Operator):
	bl_label = "Set CFIL Path"
	bl_description = "Choose .cfil path from list of known paths.\nNote that if this file does not exist for the game you're modding, the game will infinitely load"
	bl_idname = "re_chain.set_cfil_path"
	bl_context = "objectmode"
	bl_options = {'UNDO','INTERNAL'}
	cfilPath: bpy.props.EnumProperty(
		name="CFIL Type",
		description="Set collider filter info path of chain settings",
		items=[	("System/Collision/Filter/Character/Character_Chain.cfil", "MH Wilds Character CFIL", ""),
		        ("Collision/CollisionFilter/Chain/ChainCloth.cfil", "DMC5 Character CFIL", ""),
			   ]
		)
	
	def draw(self,context):
		layout = self.layout
		layout.prop(self,"cfilPath")
		
	@classmethod
	def poll(self,context):
		return context.active_object is not None and context.active_object.get("TYPE") == "RE_CHAIN_CHAINSETTINGS"
	def execute(self, context):
		
		
		for selectedObject in bpy.context.selected_objects:
			selectedObjectType = selectedObject.get("TYPE",None)
			if selectedObjectType == "RE_CHAIN_CHAINSETTINGS":
				selectedObject.re_chain_chainsettings.colliderFilterInfoPath = self.cfilPath
		self.report({"INFO"},"Set cfil path flags.")
		tag_redraw(bpy.context)
		return {'FINISHED'}
	
	def invoke(self,context,event):
		return context.window_manager.invoke_props_dialog(self)