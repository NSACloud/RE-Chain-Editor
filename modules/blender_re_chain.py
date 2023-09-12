#---BLENDER FUNCTIONS---#
import bpy

from mathutils import Matrix
from math import radians

from .gen_functions import textColors,raiseWarning,raiseError
from .file_re_chain import readREChain,writeREChain
from .pymmh3 import hash_wide
from .blender_utils import showMessageBox,showErrorMessageBox
from .re_chain_propertyGroups import getChainHeader,getWindSettings,getChainSettings,getChainGroup,getChainNode,getChainJiggle,getChainCollision,getChainLink,setChainHeaderData,setWindSettingsData,setChainSettingsData,setChainGroupData,setChainNodeData,setChainJiggleData,setChainCollisionData,setChainLinkData

from .file_re_chain import ChainFile, SIZE_DATA, ChainHeaderData, ChainSettingsData, ChainCollisionData, ChainNodeData, ChainGroupData, ChainJiggleData, WindSettingsData,ChainLinkData


#TODO Add checking for chain groups with -1 chain settings ID

def findHeaderObj():
	if bpy.data.collections.get("chainData",None) != None:
		objList = bpy.data.collections["chainData"].all_objects
		headerList = [obj for obj in objList if obj.get("TYPE",None) == "RE_CHAIN_HEADER"]
		if len(headerList) >= 1:
			return headerList[0]
		else:
			return None


def checkNameUsage(baseName,checkSubString = True):
    if checkSubString:
        return any(baseName in name for name in [obj.name for obj in bpy.data.objects])
    else:
        return baseName in [obj.name for obj in bpy.data.objects]

def checkChainSettingsIDUsage(chainSettingsID):
	idList = [obj.re_chain_chainsettings.id for obj in bpy.context.scene.objects if obj.get("TYPE",None) == "RE_CHAIN_CHAINSETTINGS"]
	if chainSettingsID in idList:
		return True
	else:
		return False

def checkWindSettingsIDUsage(windSettingsID):
	idList = [obj.re_chain_windsettings.id for obj in bpy.context.scene.objects if obj.get("TYPE",None) == "RE_CHAIN_WINDSETTINGS"]
	if windSettingsID in idList:
		return True
	else:
		return False

def createEmpty(name,propertyList,parent = None,collectionName = None):
	obj = bpy.data.objects.new( name, None )
	bpy.context.scene.collection.objects.link(obj)
	obj.empty_display_size = .10
	obj.empty_display_type = 'PLAIN_AXES'
	obj.parent = parent
	for property in propertyList:#Reverse list so items get added in correct order
 
		obj[property[0]] = property[1]
	if collectionName != None:    
		master_collection = bpy.context.scene.collection
		
		if bpy.data.collections.get(collectionName,None) == None:#Create collection if the name given doesn't exist
			newCollection = bpy.data.collections.new(collectionName)
			bpy.context.scene.collection.children.link(newCollection)
		
		layer_collection = bpy.data.collections[collectionName]
		layer_collection.objects.link(obj) #link it with collection
		master_collection.objects.unlink(obj) #unlink it from master collection
		
	return obj
#parent = createEmpty("test",[("TestValue",0.34),("TestValue2",4)],None)

#createEmpty("test2",[("TestValue",0.42141),("TestValue2",1)],parent)

def findBone(boneName,armature = None):
	if armature == None:#Find an armature if one is not specified
		if bpy.context.active_object != None and bpy.context.active_object.type == "ARMATURE":
			armature = bpy.context.active_object
		else:
			for obj in bpy.context.scene.objects:
				if armature != None:
					raiseError("More than one armature was found in the scene. Select an armature before importing the chain.")
				if obj.type == "ARMATURE":
					armature = obj
	if armature != None:
		bones = armature.data.bones
		searchBone = bones.get(boneName,None)
		if searchBone == None:
			raiseWarning(str(boneName) + " is not a part of armature: " + armature.name)
		return searchBone
	else:#No armature in scene
		return None
def getBoneParentsRecursive(bone,boneList,recursionAmount):
	boneList.append(bone)
	if recursionAmount > 0:    
		try:
			getBoneParentsRecursive(bone.parent, boneList, recursionAmount - 1)
		except:
			raiseWarning("Could not get parent of bone " + bone.name)
def syncCollisionOffsets():
	collisionTypeList = [
		"RE_CHAIN_COLLISION_SINGLE",
		"RE_CHAIN_COLLISION_CAPSULE_ROOT",
		]
	for collisionObj in [obj for obj in bpy.context.scene.objects if (obj.get("TYPE",None) in collisionTypeList) and obj.parent != None] :
		if collisionObj.get("TYPE",None) != "RE_CHAIN_COLLISION_CAPSULE_ROOT":
			collisionObj.re_chain_chaincollision.collisionOffset = collisionObj.location * .01
		else:
			for child in collisionObj.children:
				if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
					collisionObj.re_chain_chaincollision.collisionOffset = child.location * .01
				elif child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
					collisionObj.re_chain_chaincollision.endCollisionOffset = child.location * .01
def alignChains():
	for chain in [obj for obj in bpy.context.scene.objects if obj.get("TYPE",None) =="RE_CHAIN_CHAINGROUP"]:
		if chain.children != []:
			currentNode = chain.children[0]
			nodeObjList = [currentNode]
			while len(currentNode.children) > 1:
				currentNode.location = (0.0,0.0,0.0)
				currentNode.rotation_euler = (0.0,0.0,0.0)
				currentNode.scale = (1.0,1.0,1.0)
				for child in currentNode.children:
					if child.get("TYPE",None) == "RE_CHAIN_NODE":
						nodeObjList.append(child)
						
						currentNode = child
			nodeObjList.reverse()
			for recurse in nodeObjList:
				if recurse.re_chain_chainnode.collisionRadius != 0:
					recurse.empty_display_size = recurse.re_chain_chainnode.collisionRadius * 100
				else:
					recurse.empty_display_size = 1
				for obj in nodeObjList:
					try:
						obj.constraints["BoneName"].inverse_matrix = obj.parent.matrix_world.inverted()
					except:
						pass
				bpy.context.view_layer.update()

def alignCollisions():#TODO Fix matrices
	collisionTypeList = [
		"RE_CHAIN_COLLISION_SINGLE",
		"RE_CHAIN_COLLISION_CAPSULE_ROOT",
		]
	for collisionObj in [obj for obj in bpy.context.scene.objects if (obj.get("TYPE",None) in collisionTypeList) and obj.parent != None] :
		if collisionObj.get("TYPE",None) == "RE_CHAIN_COLLISION_SINGLE":
			collisionObj.constraints["BoneName"].inverse_matrix = collisionObj.parent.matrix_world.inverted()
			if collisionObj.re_chain_chaincollision.radius != 0:
				collisionObj.empty_display_size = collisionObj.re_chain_chaincollision.radius * 100
			else:
				collisionObj.empty_display_size = 1
		else:#Capsule
			for child in collisionObj.children:
				if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END" or child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
					child.constraints["BoneName"].inverse_matrix = child.parent.matrix_world.inverted()
					
					if collisionObj.re_chain_chaincollision.radius != 0:
						child.empty_display_size = collisionObj.re_chain_chaincollision.radius * 100
					else:
						child.empty_display_size = 1
	bpy.context.view_layer.update()
def getArmatureHashList(armature):
	boneHashDict = {}
	for bone in armature.pose.bones:        
		boneHashDict[hash_wide(bone.name)] = bone
	return boneHashDict

#---CHAIN IMPORT---#

def importChainFile(filepath):
	armature = None
	try:
		if bpy.context.active_object != None and bpy.context.active_object.type == "ARMATURE":
			armature = bpy.context.active_object
	except:
		pass
	if armature == None:#If an armature wasn't selected before import, check that there's one in the scene
		for obj in bpy.context.scene.objects:
			if obj.type == "ARMATURE" and armature != None:
				showErrorMessageBox("More than one armature was found in the scene. Select an armature before importing the chain.")
				return False
			if obj.type == "ARMATURE":
				armature = obj
	if armature == None:#If an armature is not found after searching, stop importing
		showErrorMessageBox("No armature in scene. The armature from the mesh file must be present in order to import the chain file.")
		return False
	#print(armature)
	#convert header to empty
	chainFile = readREChain(filepath)
	
	removedItems = []
	#Pre check to see if the chain bones are present before trying to import the chain
	for chainIndex,chainGroup in enumerate(chainFile.ChainGroupList):
		endBone = findBone(chainGroup.terminateNodeName,armature)
		if endBone == None:
			raiseWarning("Could not find " + chainGroup.terminateNodeName + " bone on an armature. Make sure the mesh file is imported and only a single armature is in the scene.")
			removedItems.append(chainGroup)
			#return False

	for item in removedItems:
		chainFile.ChainGroupList.remove(item)

	removedItems = []
	boneHashDict = getArmatureHashList(armature)

	#Pre check to see that all collision bone hashes match to bones
	for collisionIndex,chainCollision in enumerate(chainFile.ChainCollisionList):
		if chainCollision.jointNameHash not in boneHashDict.keys():
			raiseWarning("Collision Entry " + str(collisionIndex) + ": Joint hash ("+str(chainCollision.jointNameHash)+") does not match to any bones on the armature. The armature may be missing bones.")
			removedItems.append(chainCollision)
			#return False
		elif chainCollision.chainCollisionShape == 2 and chainCollision.pairJointNameHash not in boneHashDict.keys():#Capsule
			raiseWarning("Collision Entry " + str(collisionIndex) + ": Pair joint hash ("+str(chainCollision.pairJointNameHash)+") does not match to any bones on the armature. The armature may be missing bones.")
			removedItems.append(chainCollision)
			#return False

	for item in removedItems:
		chainFile.ChainCollisionList.remove(item)

	chainFile.Header.chainModelCollisionCount = len(chainFile.ChainCollisionList)
	chainFile.Header.chainGroupCount = len(chainFile.ChainGroupList)

	#HEADER IMPORT
	terminalNameHashDict = {}#Used for chain links
	"""
	for bone in armature.data.bones:
		terminalNameHashDict[hash_wide(bone.name)] = bone.name
		if "_end" in bone.name:
			terminalNameHashDict[hash_wide(bone.name.split("_end")[0])] = bone.name.split("_end")[0]
	"""
	headerPropertyList = [("TYPE","RE_CHAIN_HEADER")]
	headerObj = createEmpty("CHAIN_HEADER",headerPropertyList,None,"chainData")
	getChainHeader(chainFile.Header,headerObj)
	#WIND SETTINGS IMPORT
	for index, windSettings in enumerate(chainFile.WindSettingsList):
		name = "WIND_SETTINGS_"+str(index).zfill(2)
		windSettingsObj = createEmpty(name,[("TYPE","RE_CHAIN_WINDSETTINGS"),("tempID",windSettings.id)],headerObj,"chainData")
		getWindSettings(windSettings,windSettingsObj)
	
	#CHAIN SETTINGS IMPORT
	for index, chainSettings in enumerate(chainFile.ChainSettingsList):
		matchingWindSettingList = []
		matchingWindSettingList = [x for x in headerObj.children if x.get("TYPE") == "RE_CHAIN_WINDSETTINGS" and x.get("tempID") == chainSettings.windID]
		if matchingWindSettingList == []:
			chainSettingsParent = headerObj
		else:
			if len(matchingWindSettingList) > 1:
				raiseWarning("More than one wind settings object was found with an ID of " + str(chainSettings.windID))
			chainSettingsParent = matchingWindSettingList[0]
		name = "CHAIN_SETTINGS_" + str(index).zfill(2)
		chainSettingsObj = createEmpty(name, [("TYPE","RE_CHAIN_CHAINSETTINGS")],chainSettingsParent,"chainData")
		getChainSettings(chainSettings,chainSettingsObj)
	#CHAIN GROUPS IMPORT
		
		for groupIndex, chainGroup in enumerate(chainFile.ChainGroupList):
			#print(chainGroup)
			if chainGroup.settingID == chainSettings.id:
				name = "CHAIN_GROUP_" + str(groupIndex).zfill(2) + "_" + str(chainGroup.terminateNodeName.rsplit("_",1)[0])
				chainGroupObj = createEmpty(name, [("TYPE","RE_CHAIN_CHAINGROUP")],chainSettingsObj,"chainData")
				getChainGroup(chainGroup,chainGroupObj)
				endBone = findBone(chainGroup.terminateNodeName,armature)
				"""
				if endBone == None:
					showErrorMessageBox("Could not find " + chainGroup.terminateNodeName + " bone on an armature. Make sure the mesh file is imported and only a single armature is in the scene.")
					return False
				"""
				boneList = [endBone]#List of bones attached to the end bone
				
				getBoneParentsRecursive(endBone, boneList, chainGroup.nodeCount-1)
				boneList.reverse()#Reverse list so it starts with the start of the chain
				baseNodeName = chainGroup.terminateNodeName.split("_end")[0]
				nodeParent = chainGroupObj
				terminalNameHashDict[chainGroup.terminateNodeNameHash]=chainGroupObj.name
				
				#TODO Add chain group subdata import and export, currently the subdata count is set to 0 and not imported
	#CHAIN NODES IMPORT
				for nodeIndex,node in enumerate(chainGroup.nodeList):
					if boneList != [None]:
						name = boneList[nodeIndex].name
						currentBone = boneList[nodeIndex]
					else:
						raiseWarning("Could not find chain bones in armature, guessing node names.")
						if nodeIndex == len(chainGroup.nodeList)-1:
							name = baseNodeName + "_end"
						else:
							name = baseNodeName+"_"+str(nodeIndex).zfill(2)
					nodeObj = createEmpty(name,[("TYPE","RE_CHAIN_NODE")],nodeParent,"chainData")
					getChainNode(node, nodeObj)
					nodeParent = nodeObj
					nodeObj.empty_display_size = 2
					nodeObj.empty_display_type = "SPHERE"
					nodeObj.show_name = bpy.context.scene.re_chain_toolpanel.showNodeNames
					nodeObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawNodesThroughObjects
					#nodeObj.show_name = True
					frame = createEmpty(nodeObj.name+"_ANGLE_LIMIT", [("TYPE","RE_CHAIN_NODE_FRAME")],nodeObj,"chainData")
					frame.empty_display_type = "ARROWS"
					frame.empty_display_size = bpy.context.scene.re_chain_toolpanel.angleLimitDisplaySize
					frame.show_in_front = bpy.context.scene.re_chain_toolpanel.drawNodesThroughObjects
					frame.rotation_mode = "QUATERNION"
					frame.rotation_quaternion = (node.angleLimitDirectionW,node.angleLimitDirectionX,node.angleLimitDirectionY,node.angleLimitDirectionZ)
					frame.rotation_mode = "XYZ"
					#Constrain frame location to node
						
					constraint = frame.constraints.new(type = "COPY_LOCATION")
					constraint.target = nodeObj
					
					constraint = frame.constraints.new(type = "COPY_SCALE")
					constraint.target = nodeObj
					
					#Add angle limit cone
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
					lightObj.matrix_world = frame.matrix_world
					lightObj.matrix_local = lightObj.matrix_local @ rotationMat
					lightObj.hide_select = True#Disable ability to select to avoid it getting in the way
					
					lightObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawConesThroughObjects
					lightObj.hide_viewport = not bpy.context.scene.re_chain_toolpanel.showAngleLimitCones

					#Determine cone scale
					xScaleModifier = 1.0
					yScaleModifier = 1.0
					zScaleModifier = 1.0
					if nodeObj.re_chain_chainnode.angleMode == "2":#Hinge angle mode
						yScaleModifier = .01
					elif nodeObj.re_chain_chainnode.angleMode == "4":#Limit oval angle mode
						xScaleModifier = .5
					elif nodeObj.re_chain_chainnode.angleMode == "5":#Limit elliptic angle mode
						yScaleModifier = .5
					lightObj.scale = (bpy.context.scene.re_chain_toolpanel.coneDisplaySize*xScaleModifier,bpy.context.scene.re_chain_toolpanel.coneDisplaySize*yScaleModifier,bpy.context.scene.re_chain_toolpanel.coneDisplaySize*zScaleModifier)
					
					bpy.data.collections["chainData"].objects.link(lightObj)
					
					if currentBone != None:
						constraint = nodeObj.constraints.new(type = "COPY_TRANSFORMS")
						constraint.target = armature
						constraint.subtarget = currentBone.name #.split(":")[len(bone.name.split(":"))-1]
						#terminalNameHashDict[hash_wide(currentBone.name)] = nodeObj
						constraint.name = "BoneName"
					if node.jiggleData:
						jiggle = node.jiggleData
						jiggleObj = createEmpty(name+"_JIGGLE",[("TYPE","RE_CHAIN_JIGGLE")],nodeObj,"chainData")
						getChainJiggle(jiggle, jiggleObj)
						jiggleObj.empty_display_size = 40
						jiggleObj.empty_display_type = "SPHERE"
						jiggleObj.show_name = bpy.context.scene.re_chain_toolpanel.showNodeNames
						jiggleObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawNodesThroughObjects
						jiggleObj.rotation_mode = 'QUATERNION'
						jiggleObj.rotation_quaternion = (jiggle.rangeAxisW,jiggle.rangeAxisX,jiggle.rangeAxisY,jiggle.rangeAxisZ)
						jiggleObj.scale = (jiggle.rangeX, jiggle.rangeY, jiggle.rangeZ)
						jiggleObj.location = (jiggle.rangeOffsetX, jiggle.rangeOffsetY, jiggle.rangeOffsetZ)
		alignChains()
	#CHAIN COLLISION IMPORT
	
	singleObjectColList = ["SPHERE","OBB","PLANE","LINESPHERE","LERPSPHERE"]
	enumItemDict ={0:"NONE",1:"SPHERE",2:"CAPSULE",3:"OBB",4:"PLANE",5:"LINESPHERE",6:"LERPSPHERE",-1:"UNKNOWN"}
	for collisionIndex,chainCollision in enumerate(chainFile.ChainCollisionList):
		#print(chainCollision)
		currentCollisionIndex = collisionIndex
		subName = "COLLISION_"+str(currentCollisionIndex).zfill(2)
		while(checkNameUsage(subName,checkSubString=True)):
			currentCollisionIndex +=1
			subName = "COLLISION_"+str(currentCollisionIndex).zfill(2)
		
		shape = enumItemDict[chainCollision.chainCollisionShape]
		if shape != "CAPSULE" and chainCollision.pairJointNameHash == 0:
			name = "COLLISION_" +str(currentCollisionIndex).zfill(2)+ "_"+shape + " " + boneHashDict[chainCollision.jointNameHash].name
			colSphereObj = createEmpty(name, [("TYPE","RE_CHAIN_COLLISION_SINGLE")],headerObj,"chainData")
			getChainCollision(chainCollision,colSphereObj)
			colSphereObj.re_chain_chaincollision.chainCollisionShape = str(chainCollision.chainCollisionShape)
			colSphereObj.re_chain_chaincollision.collisionOffset = (chainCollision.posX,chainCollision.posY,chainCollision.posZ)
			colSphereObj.rotation_mode = "QUATERNION" 
			colSphereObj.rotation_quaternion = (chainCollision.rotOffsetW,chainCollision.rotOffsetX,chainCollision.rotOffsetY,chainCollision.rotOffsetZ)
			
			colSphereObj.empty_display_type = "SPHERE"
			colSphereObj.empty_display_size = 1
			constraint = colSphereObj.constraints.new(type = "CHILD_OF")
			constraint.target = armature
			constraint.subtarget = boneHashDict[chainCollision.jointNameHash].name
			constraint.name = "BoneName"
			#colSphereObj.show_name = True
			colSphereObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
			colSphereObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCollisionsThroughObjects
		else:#CAPSULE
			if chainCollision.chainCollisionShape == 0:
				subName +="_NONE"
			name = subName+ "_CAPSULE"
			colCapsuleRootObj = createEmpty(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_ROOT")],headerObj,"chainData")
			colCapsuleRootObj.empty_display_size = .1
			getChainCollision(chainCollision,colCapsuleRootObj)
			colCapsuleRootObj.re_chain_chaincollision.chainCollisionShape = str(chainCollision.chainCollisionShape)
			name = subName+ "_CAPSULE_START" + " " + boneHashDict[chainCollision.jointNameHash].name
			colCapsuleStartObj = createEmpty(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_START")],colCapsuleRootObj,"chainData")
			
			
			colCapsuleStartObj.re_chain_chaincollision.collisionOffset = (chainCollision.posX,chainCollision.posY,chainCollision.posZ)
			colCapsuleStartObj.rotation_mode = "QUATERNION" 
			colCapsuleStartObj.rotation_quaternion = (chainCollision.rotOffsetW,chainCollision.rotOffsetX,chainCollision.rotOffsetY,chainCollision.rotOffsetZ)
			
			colCapsuleStartObj.empty_display_type = "SPHERE"
			colCapsuleStartObj.empty_display_size = 1
			constraint = colCapsuleStartObj.constraints.new(type = "CHILD_OF")
			constraint.target = armature
			constraint.subtarget = boneHashDict[chainCollision.jointNameHash].name
			constraint.name = "BoneName"
			#colCapsuleStartObj.show_name = True
			colCapsuleStartObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
			colCapsuleStartObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCollisionsThroughObjects
			
			name = subName+ "_CAPSULE_END" + " " + boneHashDict[chainCollision.pairJointNameHash].name
			colCapsuleEndObj = createEmpty(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_END")],colCapsuleRootObj,"chainData")
			colCapsuleEndObj.re_chain_chaincollision.endCollisionOffset = (chainCollision.pairPosX,chainCollision.pairPosY,chainCollision.pairPosZ)
			colCapsuleEndObj.empty_display_type = "SPHERE"
			colCapsuleEndObj.empty_display_size = 1
			constraint = colCapsuleEndObj.constraints.new(type = "CHILD_OF")
			constraint.target = armature
			constraint.subtarget = boneHashDict[chainCollision.pairJointNameHash].name
			constraint.name = "BoneName"
			#colCapsuleEndObj.show_name = True
			colCapsuleEndObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
			colCapsuleEndObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCollisionsThroughObjects
		alignCollisions()
	#CHAIN LINK IMPORT
	#print(terminalNameHashDict)#debug
	
	for index, chainLink in enumerate(chainFile.ChainLinkList):
		name = "CHAIN_LINK_"+str(index).zfill(2)
		chainLinkObj = createEmpty(name, [("TYPE","RE_CHAIN_LINK")],headerObj,"chainData")
		getChainLink(chainLink,chainLinkObj)
		chainLinkObj.re_chain_chainlink.chainGroupAObject = terminalNameHashDict[chainLink.terminateNodeNameHashA] if chainLink.terminateNodeNameHashA in terminalNameHashDict else str(chainLink.terminateNodeNameHashA)
		chainLinkObj.re_chain_chainlink.chainGroupBObject = terminalNameHashDict[chainLink.terminateNodeNameHashB] if chainLink.terminateNodeNameHashB in terminalNameHashDict else str(chainLink.terminateNodeNameHashB)

	return True
def chainErrorCheck():
	print("\nChecking for problems with chain structure...")
	
	#Check that there is chain data collection
	#Check that there is only one header
	#Check that all nodes have one frame
	#Check that all 2 part chain collisions have both ends
	#Check that there is at least one chain group with 2 nodes
	#Check that all chain objects are parented to the header
	#Check that parenting structure is valid
	#Check that all nodes and collision objects have valid child of constraints
	#Check for duplicate chain and wind setting ids
	#TODO
	#Check that chain links are valid
	errorList = []
	if bpy.data.collections.get("chainData",None) != None:
		objList = bpy.data.collections["chainData"].all_objects
	else:
		errorList.append("Chain objects must be in a collection named \"chainData\".")
		objList = []
	headerCount = 0
	for obj in objList:
	
		
		
		if obj.get("TYPE",None) == "RE_CHAIN_HEADER":
			headerCount += 1
			if obj.parent != None:
				errorList.append("Chain header cannot be a child of another object.")
		
		elif obj.get("TYPE",None) == "RE_CHAIN_NODE":
			childFrame = None
			for child in obj.children:
				if child.get("TYPE",None) == "RE_CHAIN_NODE_FRAME":
					if childFrame != None:
						errorList.append("Chain node " + obj.name + " has more than one frame parented to it.")
					else:
						childFrame = child
			if childFrame == None:
				errorList.append("Chain node " + obj.name + " has no frame parented to it.")
			
			validParentTypeList = ["RE_CHAIN_CHAINGROUP","RE_CHAIN_NODE"]
			if obj.parent != None:    
				if obj.parent.get("TYPE",None) not in validParentTypeList:
					errorList.append(obj.name + " node cannot be parented to an object of type: "+str(obj.parent.get("TYPE",None)))
			else:
				errorList.append(obj.name + " node must be parented to a chain group or a chain node object.")
			
			if obj.constraints.get("BoneName",False):
				if obj.constraints["BoneName"].target == "" or obj.constraints["BoneName"].target == None or obj.constraints["BoneName"].subtarget == "":
					errorList.append("Invalid child of constraint on " + obj.name)
			else:
				errorList.append("Child of constraint missing on " + obj.name)
				
				
		elif obj.get("TYPE",None) == "RE_CHAIN_CHAINGROUP":
			
			validParentTypeList = ["RE_CHAIN_CHAINSETTINGS"]
			if obj.parent != None:    
				if obj.parent.get("TYPE",None) not in validParentTypeList:
					errorList.append(obj.name + " must be parented to a chain settings object.")
			else:
				errorList.append(obj.name + " must be parented to a chain settings object.")
				
			validChainGroup = False
			for child in obj.children:
				if child.get("TYPE") == "RE_CHAIN_NODE":
					for nodeChild in child.children:
						if nodeChild.get("TYPE") == "RE_CHAIN_NODE":
							validChainGroup = True
			if not validChainGroup:
				errorList.append("Chain group "+obj.name + " must contain at least two nodes.")
		
		elif obj.get("TYPE",None) == "RE_CHAIN_WINDSETTINGS":
			if obj.parent != None:
				if obj.parent.get("TYPE",None) != "RE_CHAIN_HEADER":
					errorList.append(obj.name + " object must be parented to a chain header object")
			else:
				errorList.append(obj.name + " object must be parented to a chain header object")
			
			idList = [chainObj.re_chain_windsettings.id for chainObj in objList if chainObj.get("TYPE",None) == "RE_CHAIN_WINDSETTINGS"]
			idChanged = False
			while idList.count(obj.re_chain_windsettings.id) > 1:
				obj.re_chain_windsettings.id += 1
				idChanged = True
			if idChanged:
				raiseWarning("ID of "+ obj.name + " changed to " + str(obj.re_chain_windsettings.id) + " to avoid ID conflicts.")
		
		elif obj.get("TYPE",None) == "RE_CHAIN_CHAINSETTINGS":
			validParentTypeList = ["RE_CHAIN_HEADER","RE_CHAIN_WINDSETTINGS"]
			if obj.parent != None:    
				if obj.parent.get("TYPE",None) not in validParentTypeList:
					errorList.append(obj.name + " object must be parented to a chain header or wind settings object.")
			else:
				errorList.append(obj.name + " object must be parented to a chain header or wind settings object.")
			
			idList = [chainObj.re_chain_chainsettings.id for chainObj in objList if chainObj.get("TYPE",None) == "RE_CHAIN_CHAINSETTINGS"]
			idChanged = False
			while idList.count(obj.re_chain_chainsettings.id) > 1:
				obj.re_chain_chainsettings.id += 1
				idChanged = True
			if idChanged:
				raiseWarning("ID of "+ obj.name + " changed to " + str(obj.re_chain_chainsettings.id) + " to avoid ID conflicts.")
		
		elif obj.get("TYPE",None) == "RE_CHAIN_COLLISION_SINGLE":
			if obj.parent != None:
				if obj.parent.get("TYPE",None) != "RE_CHAIN_HEADER":
					errorList.append(obj.name + " object must be parented to a chain header object")
			else:
				errorList.append(obj.name + " object must be parented to a chain header object")
			if obj.re_chain_chaincollision.chainCollisionShape == "2":#Capsule
				errorList.append(obj.name + " object collision shape is set to capsule, but is not a capsule. Create capsules by using the Create Collision From Bone button after selecting two bones")
			if obj.constraints.get("BoneName",False):
				if obj.constraints["BoneName"].target == "" or obj.constraints["BoneName"].target == None or obj.constraints["BoneName"].subtarget == "":
					errorList.append("Invalid child of constraint on " + obj.name)
			else:
				errorList.append("Child of constraint missing on " + obj.name)        
		
		elif obj.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_ROOT":
			if obj.parent != None:
				if obj.parent.get("TYPE",None) != "RE_CHAIN_HEADER":
					errorList.append(obj.name + " object must be parented to a chain header object")
			else:
				errorList.append(obj.name + " object must be parented to a chain header object")
			
			#if obj.re_chain_chaincollision.chainCollisionShape != "2" and obj.re_chain_chaincollision.chainCollisionShape != "0":#Capsule OR None
				#errorList.append(obj.name + " object collision shape is not set to capsule. Create other collision shapes by using the Create Collision From Bone button after selecting a single bone")
			startCapsule = None
			for child in obj.children:
				if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
					if startCapsule != None:
						errorList.append("Collision capsule " + obj.name + " has more than one start point parented to it.")
					else:
						startCapsule = child
			if startCapsule == None:
				errorList.append("Collision capsule " + obj.name + " has no start point parented to it.")
			else:
				if startCapsule.constraints.get("BoneName",False):
					if startCapsule.constraints["BoneName"].target == "" or startCapsule.constraints["BoneName"].target == None or startCapsule.constraints["BoneName"].subtarget == "":
						errorList.append("Invalid child of constraint on " + startCapsule.name)
				else:
					errorList.append("Child of constraint missing on " + startCapsule.name)
					
			endCapsule = None
			for child in obj.children:
				if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
					if endCapsule != None:
						errorList.append("Collision capsule " + obj.name + " has more than one end point parented to it.")
					else:
						endCapsule = child
			if endCapsule == None:
				errorList.append("Collision capsule " + obj.name + " has no end point parented to it.")
			else:
				if endCapsule.constraints.get("BoneName",False):
					if endCapsule.constraints["BoneName"].target == "" or endCapsule.constraints["BoneName"].target == None or endCapsule.constraints["BoneName"].subtarget == "":
						errorList.append("Invalid child of constraint on " + endCapsule.name)
				else:
					errorList.append("Child of constraint missing on " + endCapsule.name)
			
		elif obj.get("TYPE",None) == "RE_CHAIN_LINK":
			if obj.parent != None:
				if obj.parent.get("TYPE",None) != "RE_CHAIN_HEADER":
					errorList.append(obj.name + " object must be parented to a chain header object")
			else:
				errorList.append(obj.name + " object must be parented to a chain header object")
			if bpy.context.scene.objects.get(obj.re_chain_chainlink.chainGroupAObject,None) != None:
				if bpy.context.scene.objects[obj.re_chain_chainlink.chainGroupAObject].get("TYPE",None) != "RE_CHAIN_CHAINGROUP":
					errorList.append(obj.name + ": Chain Group A must be set to a Chain Group object")
			#else:
			#	errorList.append(obj.name + ": Chain Group A is not set or set to an object that doesn't exist")
				
			if bpy.context.scene.objects.get(obj.re_chain_chainlink.chainGroupBObject,None) != None:
				if bpy.context.scene.objects[obj.re_chain_chainlink.chainGroupBObject].get("TYPE",None) != "RE_CHAIN_CHAINGROUP":
					errorList.append(obj.name + ": Chain Group B must be set to a Chain Group object")
			#else:
			#	errorList.append(obj.name + ": Chain Group B is not set or set to an object that doesn't exist")
	if headerCount == 0:
		errorList.append("No chain header object in scene.")
		
	elif headerCount > 1:
		errorList.append("Cannot export with more than one chain header in a scene.")
	
	if errorList == []:
		print("No problems found.")
		syncCollisionOffsets()
		return True
	else:
		errorString = ""
		for error in errorList:
			errorString += textColors.FAIL +"ERROR: " + error + textColors.ENDC +"\n"
		showMessageBox("Chain structure contains errors and cannot export. Check Window > Toggle System Console for details.",title = "Export Error", icon = "ERROR")
		print(errorString)
		print(textColors.FAIL + "__________________________________\nChain export failed."+textColors.ENDC)
		return False

def exportChainFile(filepath, version):
	valid = chainErrorCheck()
	if valid:
		print(textColors.OKCYAN + "__________________________________\nChain export started."+textColors.ENDC)
		newChainFile = ChainFile()
		
		objList = bpy.data.collections["chainData"].all_objects
		
		windSettingsObjList = []
		chainSettingsObjList = []
		chainGroupObjList = []
		chainCollisionObjList = []
		chainLinkObjList = []
		
		collisionTypes = [
			"RE_CHAIN_COLLISION_SINGLE",
			"RE_CHAIN_COLLISION_CAPSULE_ROOT",
			]
		
		for obj in objList:
			objType = obj.get("TYPE",None)
			if objType == "RE_CHAIN_HEADER":
				headerObj = obj
			elif objType == "RE_CHAIN_WINDSETTINGS":
				windSettingsObjList.append(obj)
			elif objType == "RE_CHAIN_CHAINSETTINGS":
				chainSettingsObjList.append(obj)
			elif objType == "RE_CHAIN_CHAINGROUP":
				chainGroupObjList.append(obj)
			elif objType == "RE_CHAIN_LINK":
				chainLinkObjList.append(obj)
			elif objType in collisionTypes:
				chainCollisionObjList.append(obj)
				
		windSettingsObjList.sort(key = lambda item: item.name)
		chainSettingsObjList.sort(key = lambda item: item.name)
		chainGroupObjList.sort(key = lambda item: item.name)
		chainCollisionObjList.sort(key = lambda item: item.name)
		
		newChainFile.Header.chainWindSettingsCount = len(windSettingsObjList)
		newChainFile.Header.chainSettingsCount = len(chainSettingsObjList)
		newChainFile.Header.chainGroupCount = len(chainGroupObjList)
		newChainFile.Header.chainModelCollisionCount = len(chainCollisionObjList)
		newChainFile.Header.chainLinkCount = len(chainLinkObjList)
		newChainFile.Header.version = version
		
		
		#print(windSettingsObjList)
		#print(chainSettingsObjList)
		#print(chainGroupObjList)
		#print(chainCollisionObjList)
		headerObj.re_chain_header.version = str(version)
		setChainHeaderData(newChainFile.Header, headerObj)
		newChainFile.sizeData.setSizeData(newChainFile.Header.version)
		
		chainGroupTerminateNodeHashDict = {}#Used for chain links
		for windSettingsObj in windSettingsObjList:
			windSettings = WindSettingsData()
			setWindSettingsData(windSettings, windSettingsObj)
			newChainFile.WindSettingsList.append(windSettings)
		
		for chainSettingsObj in chainSettingsObjList:
			chainSettings = ChainSettingsData()
			setChainSettingsData(chainSettings, chainSettingsObj)
			newChainFile.ChainSettingsList.append(chainSettings)
		
		for chainGroupObj in chainGroupObjList:
			chainGroup = ChainGroupData()
			setChainGroupData(chainGroup, chainGroupObj)
			#Get nodes
			nodeObjList = []
			#TODO Add chain group subdata export
			currentNode = chainGroupObj.children[0]
			nodeObjList = [currentNode]
			hasChildNode = True
			while hasChildNode:
				currentNodeHasChildNode = False
				for child in currentNode.children:
					if child.get("TYPE",None) == "RE_CHAIN_NODE":
						nodeObjList.append(child)
						currentNode = child
						currentNodeHasChildNode = True
				if not currentNodeHasChildNode:
					hasChildNode = False
			for nodeObj in nodeObjList:
				node = ChainNodeData()
				setChainNodeData(node, nodeObj)
				chainGroup.nodeList.append(node)
				if version >= 35:
					for child in nodeObj.children:
						if child.get("TYPE",None) == "RE_CHAIN_JIGGLE":
							jiggle = ChainJiggleData()
							setChainJiggleData(jiggle, child)
							node.jiggleData = jiggle
							break

			chainGroup.terminateNodeNameHash = hash_wide(nodeObjList[len(nodeObjList)-1].name.split(".")[0])
			chainGroupTerminateNodeHashDict[chainGroupObj.name] = chainGroup.terminateNodeNameHash
			chainGroup.terminateNodeName = nodeObjList[len(nodeObjList)-1].name.split(".")[0]
			chainGroup.nodeCount = len(chainGroup.nodeList)
			newChainFile.ChainGroupList.append(chainGroup)
		
		for chainCollisionObj in chainCollisionObjList:
			chainCollision = ChainCollisionData()
			setChainCollisionData(chainCollision, chainCollisionObj)
			newChainFile.ChainCollisionList.append(chainCollision)
			
		for chainLinkObj in chainLinkObjList:
			chainLink = ChainLinkData()
			setChainLinkData(chainLink, chainLinkObj)
			newChainFile.ChainLinkList.append(chainLink)
			
			chainLink.terminateNodeNameHashA = chainGroupTerminateNodeHashDict[chainLinkObj.re_chain_chainlink.chainGroupAObject] if chainLinkObj.re_chain_chainlink.chainGroupAObject in chainGroupTerminateNodeHashDict else int(chainLinkObj.re_chain_chainlink.chainGroupAObject)
			chainLink.terminateNodeNameHashB = chainGroupTerminateNodeHashDict[chainLinkObj.re_chain_chainlink.chainGroupBObject] if chainLinkObj.re_chain_chainlink.chainGroupBObject in chainGroupTerminateNodeHashDict else int(chainLinkObj.re_chain_chainlink.chainGroupBObject)
			#print(nodeObjList)
		#Sort chain settings by ID, otherwise the chain groups will be assigned to the wrong chain settings in game
		newChainFile.ChainSettingsList.sort(key = lambda x: x.id)
		print("Chain Conversion Finished")
		writeREChain(newChainFile, filepath)
		return True
		#for newWindSetttings in newChainFile.WindSettingsList:
			#print(newWindSetttings)
		#for newChainSetttings in newChainFile.ChainSettingsList:
			#print(newChainSetttings)
		#for newChainGroup in newChainFile.ChainGroupList:
			#print(newChainGroup)
			#for newNode in newChainGroup.nodeList:
				#print(str(newNode)+"\n\n")