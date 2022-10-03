#Author: NSA Cloud
import bpy
import os
from math import radians

from bpy.types import Operator

from .blender_re_chain import createEmpty,alignChains,alignCollisions,checkNameUsage,checkChainSettingsIDUsage,checkWindSettingsIDUsage,findHeaderObj,syncCollisionOffsets
from .file_re_chain import ChainHeaderData, ChainSettingsData,WindSettingsData,ChainGroupData,ChainNodeData,ChainCollisionData,ChainLinkData
from .re_chain_propertyGroups import getChainHeader,getWindSettings,getChainSettings,getChainGroup,getChainNode,getChainLink,getChainCollision
from .ui_re_chain_panels import tag_redraw
from .blender_utils import showErrorMessageBox
from .re_chain_presets import saveAsPreset,readPresetJSON

class WM_OT_ChainFromBone(Operator):
	bl_label = "Create Chain From Bone"
	bl_idname = "re_chain.chain_from_bone"
	bl_options = {'UNDO'}
	bl_description = "Create new chain group and chain node objects starting from the selected bone and ending at the last child bone. Note that chains cannot be branching. Must be parented to a chain settings object"
	def execute(self, context):
		selected = bpy.context.selected_pose_bones
		chainList = []
		headerObj = findHeaderObj()
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
			currentChainGroupIndex = 0
			subName = "CHAIN_GROUP_"+str(currentChainGroupIndex).zfill(2)
			while(checkNameUsage(subName,checkSubString=True)):
				currentChainGroupIndex +=1
				subName = "CHAIN_GROUP_"+str(currentChainGroupIndex).zfill(2)
			name = subName+"_"+chainList[len(chainList)-1].name.rsplit("_",1)[0]
				
			armature = chainList[0].id_data
			#print(armature)
			chainGroupObj = createEmpty(name, [("TYPE","RE_CHAIN_CHAINGROUP")],headerObj,"chainData")
			chainGroup = ChainGroupData()
			getChainGroup(chainGroup,chainGroupObj)
			nodeParent = chainGroupObj
			for bone in chainList:
				nodeObj = createEmpty(bone.name,[("TYPE","RE_CHAIN_NODE")],nodeParent,"chainData")
				node = ChainNodeData()
				getChainNode(node, nodeObj)
				nodeParent = nodeObj
				nodeObj.empty_display_size = 2
				nodeObj.empty_display_type = "SPHERE"
				#nodeObj.show_name = True
				nodeObj.show_name = bpy.context.scene.re_chain_toolpanel.showNodeNames
				nodeObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawNodesThroughObjects
				frame = createEmpty(nodeObj.name+"_ANGLE_LIMIT", [("TYPE","RE_CHAIN_NODE_FRAME")],nodeObj,"chainData")
				frame.empty_display_type = "ARROWS"
				frame.show_in_front = bpy.context.scene.re_chain_toolpanel.drawNodesThroughObjects
				frame.empty_display_size = bpy.context.scene.re_chain_toolpanel.angleLimitDisplaySize
				frame.rotation_euler.rotate_axis("Z", radians(-90))
				frame.rotation_mode = "QUATERNION"
				#frame.rotation_quaternion = (node.angleLimitDirectionX,node.angleLimitDirectionY,node.angleLimitDirectionZ,node.angleLimitDirectionW)
				constraint = nodeObj.constraints.new(type = "CHILD_OF")
				constraint.target = armature
				constraint.subtarget = bone.name
				constraint.name = "BoneName"
			alignChains()
		self.report({"INFO"},"Created chain group from bone.")
		return {'FINISHED'}

class WM_OT_CollisionFromBones(Operator):
	bl_label = "Create Collision From Bone"
	bl_idname = "re_chain.collision_from_bone"
	bl_options = {'UNDO'}
	bl_description = "Create collision object from selected bone(s). Select one bone to create a sphere and two bones to create a collision capsule"
	def execute(self, context):
		selected = bpy.context.selected_pose_bones
		headerObj = findHeaderObj()
		if len(selected) == 1:
			startBone = selected[0]
			valid = True
			shape = str(bpy.context.scene.re_chain_toolpanel.collisionShape)
			if shape == "CAPSULE":#Two bones need to be selected to make a capsule
				valid = False
			#print(chainList)
		elif len(selected) == 2:#Force capsule if two bones are selected
			startBone = selected[0]
			endBone = selected[1]
			valid = True
			shape = "CAPSULE"#capsule
		else:
			valid = False
		
		
		if not valid:
			showErrorMessageBox("Select one bone to make a sphere or two to make a capsule.")
		else:
			currentCollisionIndex = 0
			subName = "COLLISION_"+str(currentCollisionIndex).zfill(2)
			while(checkNameUsage(subName,checkSubString=True)):
				currentCollisionIndex +=1
				subName = "COLLISION_"+str(currentCollisionIndex).zfill(2)
			name = subName+"_"+shape
			armature = startBone.id_data
			#print(armature)
			singleObjectColList = ["SPHERE","OBB","PLANE","LINESPHERE","LERPSPHERE"]
			enumItemDict ={"SPHERE":"1","CAPSULE":"2","OBB":"3","PLANE":"4","LINESPHERE":"5","LERPSPHERE":"6"}#For setting shape enum value
			if shape in singleObjectColList:
				name = "COLLISION_" +str(currentCollisionIndex).zfill(2)+ "_"+shape
				colSphereObj = createEmpty(name, [("TYPE","RE_CHAIN_COLLISION_SINGLE")],headerObj,"chainData")
				chainCollision = ChainCollisionData()
				getChainCollision(chainCollision,colSphereObj)
				colSphereObj.re_chain_chaincollision.chainCollisionShape = enumItemDict[shape]
				colSphereObj.re_chain_chaincollision.collisionOffset = (chainCollision.posX,chainCollision.posY,chainCollision.posZ)
				colSphereObj.rotation_mode = "QUATERNION" 
				colSphereObj.rotation_quaternion = (chainCollision.rotOffsetX,chainCollision.rotOffsetY,chainCollision.rotOffsetZ,chainCollision.rotOffsetW)
				
				colSphereObj.empty_display_type = "SPHERE"
				colSphereObj.empty_display_size = 1
				constraint = colSphereObj.constraints.new(type = "CHILD_OF")
				constraint.target = armature
				constraint.subtarget = startBone.name
				constraint.name = "BoneName"
				#colSphereObj.show_name = True
				colSphereObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
				colSphereObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCollisionsThroughObjects
			elif shape == "CAPSULE":#CAPSULE
				name = subName+ "_CAPSULE"
				colCapsuleRootObj = createEmpty(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_ROOT")],headerObj,"chainData")
				colCapsuleRootObj.empty_display_size = .1
				chainCollision = ChainCollisionData()
				getChainCollision(chainCollision,colCapsuleRootObj)
				name = subName+ "_CAPSULE_START"
				colCapsuleStartObj = createEmpty(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_START")],colCapsuleRootObj,"chainData")
				
				colCapsuleRootObj.re_chain_chaincollision.chainCollisionShape = enumItemDict[shape]
				colCapsuleStartObj.re_chain_chaincollision.collisionOffset = (chainCollision.posX,chainCollision.posY,chainCollision.posZ)
				colCapsuleStartObj.rotation_mode = "QUATERNION" 
				colCapsuleStartObj.rotation_quaternion = (chainCollision.rotOffsetX,chainCollision.rotOffsetY,chainCollision.rotOffsetZ,chainCollision.rotOffsetW)
				
				colCapsuleStartObj.empty_display_type = "SPHERE"
				colCapsuleStartObj.empty_display_size = 1
				constraint = colCapsuleStartObj.constraints.new(type = "CHILD_OF")
				constraint.target = armature
				constraint.subtarget = startBone.name
				constraint.name = "BoneName"
				#colCapsuleStartObj.show_name = True
				colCapsuleStartObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
				colCapsuleStartObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCollisionsThroughObjects
				
				name = subName+ "_CAPSULE_END"
				colCapsuleEndObj = createEmpty(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_END")],colCapsuleRootObj,"chainData")
				colCapsuleEndObj.re_chain_chaincollision.endCollisionOffset = (chainCollision.pairPosX,chainCollision.pairPosY,chainCollision.pairPosZ)
				colCapsuleEndObj.empty_display_type = "SPHERE"
				colCapsuleEndObj.empty_display_size = 1
				constraint = colCapsuleEndObj.constraints.new(type = "CHILD_OF")
				constraint.target = armature
				constraint.subtarget = endBone.name
				constraint.name = "BoneName"
				#colCapsuleEndObj.show_name = True
				colCapsuleEndObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
				colCapsuleEndObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCollisionsThroughObjects
			alignCollisions()
			self.report({"INFO"},"Created collision from bone.")
		return {'FINISHED'}

class WM_OT_NewChainHeader(Operator):
	bl_label = "Create Chain Header"
	bl_idname = "re_chain.create_chain_header"
	bl_options = {'UNDO'}
	bl_description = "Create a chain header object. All chain objects must be parented to this. There can only be one chain header in a scene upon export"
	def execute(self, context):
		chainHeaderObj = createEmpty("CHAIN_HEADER", [("TYPE","RE_CHAIN_HEADER")],None,"chainData")
		chainHeader = ChainHeaderData()
		getChainHeader(chainHeader,chainHeaderObj)
		return {'FINISHED'}
class WM_OT_NewChainSettings(Operator):
	bl_label = "Create Chain Settings"
	bl_idname = "re_chain.create_chain_settings"
	bl_options = {'UNDO'}
	bl_description = "Create a chain settings object. Contains parameters to determine how chain groups should behave. Must be parented to either a chain header or wind settings object"
	def execute(self, context):
		headerObj = findHeaderObj()
		currentIndex = 0
		name = "CHAIN_SETTINGS_" + str(currentIndex).zfill(2)
		while(checkNameUsage(name,checkSubString=True)):
			currentIndex +=1
			name = "CHAIN_SETTINGS_" + str(currentIndex).zfill(2)
		
		currentSettingID = 0
		while checkChainSettingsIDUsage(currentSettingID):
			currentSettingID += 1
			
		
		chainSettings = ChainSettingsData()
		chainSettingsObj = createEmpty(name, [("TYPE","RE_CHAIN_CHAINSETTINGS")],headerObj,"chainData")
		getChainSettings(chainSettings,chainSettingsObj)
		chainSettingsObj.re_chain_chainsettings.id = currentSettingID

		return {'FINISHED'}
class WM_OT_NewWindSettings(Operator):
	bl_label = "Create Wind Settings"
	bl_idname = "re_chain.create_wind_settings"
	bl_options = {'UNDO'}
	bl_description = "Create a wind settings object. Allows for wind effects on chain groups. For wind to take effect, chain settings objects must be parented to this. Must be parented to a chain header"
	def execute(self, context):
		headerObj = findHeaderObj()
		currentIndex = 0
		name = "WIND_SETTINGS_" + str(currentIndex).zfill(2)
		while(checkNameUsage(name,checkSubString=True)):
			currentIndex +=1
			name = "WIND_SETTINGS_" + str(currentIndex).zfill(2)
		
		currentSettingID = 0
		while checkWindSettingsIDUsage(currentSettingID):
			currentSettingID += 1
			
		windSettings = WindSettingsData()
		windSettingsObj = createEmpty(name, [("TYPE","RE_CHAIN_WINDSETTINGS")],headerObj,"chainData")
		getWindSettings(windSettings,windSettingsObj)
		windSettingsObj.re_chain_windsettings.id = currentSettingID
		return {'FINISHED'}
class WM_OT_NewChainLink(Operator):
	bl_label = "Create Chain Link"
	bl_idname = "re_chain.create_chain_link"
	bl_description = "Create a chain link object to make two chain groups move together. Must be parented to a chain header"
	bl_options = {'UNDO'}
	def execute(self, context):
		headerObj = findHeaderObj()
		currentIndex = 0
		name = "CHAIN_LINK_" + str(currentIndex).zfill(2)
		while(checkNameUsage(name,checkSubString=True)):
			currentIndex +=1
			name = "CHAIN_LINK_" + str(currentIndex).zfill(2)
		
		chainLink = ChainLinkData()
		chainLinkObj = createEmpty(name, [("TYPE","RE_CHAIN_LINK")],headerObj,"chainData")
		getChainLink(chainLink,chainLinkObj)
		if len(bpy.context.selected_objects) == 2:
			if bpy.context.selected_objects[0].get("TYPE",None) == "RE_CHAIN_CHAINGROUP" and bpy.context.selected_objects[1].get("TYPE",None) == "RE_CHAIN_CHAINGROUP":
				chainLinkObj.re_chain_chainlink.chainGroupAObject = bpy.context.selected_objects[0].name
				chainLinkObj.re_chain_chainlink.chainGroupBObject = bpy.context.selected_objects[1].name

		return {'FINISHED'}
class WM_OT_CopyChainProperties(Operator):
	bl_label = "Copy"
	bl_idname = "re_chain.copy_chain_properties"
	bl_description = "Copy properties from a chain object"
	@classmethod
	def poll(cls, context):
		return bpy.context.object.mode == "OBJECT"
	
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
		elif chainObjType == "RE_CHAIN_LINK":
			clipboard.re_chain_type = chainObjType
			clipboard.re_chain_type_name = "Chain Link"
			#initialize clipboard entry
			chainLink = ChainLinkData()
			getChainLink(chainLink, clipboard)
			for key, value in activeObj.re_chain_chainlink.items():
				clipboard.re_chain_chainlink[key] = value	
		elif chainObjType in collisionTypes:
			clipboard.re_chain_type = chainObjType
			clipboard.re_chain_type_name = "Collision Data"
			#initialize clipboard entry
			chainCollision = ChainCollisionData()
			getChainCollision(chainCollision, clipboard)
			for key, value in activeObj.re_chain_chaincollision.items():
				clipboard.re_chain_chaincollision[key] = value
		else:
			showErrorMessageBox("A chain object must be selected.")
			return{'CANCELLED'}
		self.report({"INFO"},"Copied properties of " + str(clipboard.re_chain_type_name)+" object to clipboard.")
		return {'FINISHED'}

class WM_OT_PasteChainProperties(Operator):
	bl_label = "Paste"
	bl_idname = "re_chain.paste_chain_properties"
	bl_options = {'UNDO'}
	bl_description = "Paste properties from a chain object to selected objects. The type of chain object must be the same as the object copied from"
	@classmethod
	def poll(cls, context):
		return bpy.context.object.mode == "OBJECT"
	
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
						
				elif chainObjType == "RE_CHAIN_LINK":
					for key, value in clipboard.re_chain_chainlink.items():
						activeObj.re_chain_chainlink[key] = value
					
				elif chainObjType in collisionTypes:
					for key, value in clipboard.re_chain_chaincollision.items():
						activeObj.re_chain_chaincollision[key] = value
						
						#I know this looks pointless but the purpose of this is force the update function to trigger, otherwise the position doesn't update
						#activeObj.re_chain_chaincollision.collisionOffset = activeObj.re_chain_chaincollision.collisionOffset
						#activeObj.re_chain_chaincollision.endCollisionOffset = activeObj.re_chain_chaincollision.endCollisionOffset
						#activeObj.re_chain_chaincollision.radius = activeObj.re_chain_chaincollision.radius
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

class WM_OT_AlignFrames(Operator):
	bl_label = "Point Frames to Next Node"
	bl_idname = "re_chain.align_frames"

	def execute(self, context):
		pass#TODO

		return {'FINISHED'}
class WM_OT_PointFrame(Operator):
	bl_label = "Point Frame to Selected"
	bl_idname = "re_chain.point_frame"

	def execute(self, context):
		pass#TODO

		return {'FINISHED'}
	
class WM_OT_ApplyChainSettingsPreset(Operator):
	bl_label = "Apply Chain Settings Preset"
	bl_idname = "re_chain.apply_chain_settings_preset"
	bl_description = "Apply preset to selected chain settings objects"
	def execute(self, context):
		enumValue = bpy.context.scene.re_chain_toolpanel.chainSettingsPresets
		
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
							if child["TYPE"] == "RE_CHAIN_NODE":
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
	bl_description = "Creates a bone group on the armature of all chain bones and colors them"
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
				poseBone = armature.pose.bones.get(chainBone,None)
				if poseBone != None:
					poseBone.bone_group = boneGroup
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
		armature = None
		if bpy.context.active_object.type == "ARMATURE":
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
		return {'FINISHED'}
	
class WM_OT_SwitchToObjectMode(Operator):#Made a button for this to make it clear that chains have to be configured in object mode
	bl_label = "Switch to Object Mode"
	bl_description = "Switch to Object Mode to configure chain objects"
	bl_idname = "re_chain.switch_to_object"

	def execute(self, context):
		bpy.ops.object.mode_set(mode='OBJECT')
		return {'FINISHED'}