#---BLENDER FUNCTIONS---#
import bpy
import os
from mathutils import Matrix
from math import radians

from .gen_functions import textColors,raiseWarning,raiseError
from .file_re_chain import readREChain,writeREChain
from .file_re_chain2 import readREChain2,writeREChain2
from .pymmh3 import hash_wide
from .blender_utils import showMessageBox,showErrorMessageBox
from .re_chain_propertyGroups import (getChainHeader,
									  getWindSettings,
									  getChainSettings,
									  getChainGroup,
									  getChainNode,
									  getChainJiggle,
									  getChainCollision,
									  getChainLink,
									  
									  setChainHeaderData,
									  setWindSettingsData,
									  setChainSettingsData,
									  setChainGroupData,
									  setChainNodeData,
									  setChainJiggleData,
									  setChainCollisionData,
									  setChainLinkData,
									  getChainLinkCollisionNode,
									  setChainLinkCollisionNodeData)

from .re_chain_geoNodes import getColCapsuleGeoNodeTree,getColSphereGeoNodeTree,getChainLinkGeoNodeTree,getConeGeoNodeTree,getLinkColGeoNodeTree,getChainGroupMat

from .file_re_chain import ChainFile, ChainHeaderData, ChainSettingsData, ChainCollisionData, ChainNodeData, ChainGroupData, ChainJiggleData, WindSettingsData,ChainLinkData,ChainLinkNode,ChainSubGroupData
from .file_re_chain2 import Chain2File, Chain2HeaderData, Chain2SettingsData, Chain2CollisionData, Chain2NodeData, Chain2GroupData, Chain2JiggleData, Chain2WindSettingsData,Chain2LinkData,Chain2LinkNode,Chain2SubGroupData


#TODO Add checking for chain groups with -1 chain settings ID

def findArmatureObjFromData(armatureData):
	armatureObj = None
	for obj in bpy.context.scene.objects:
		if obj.type == "ARMATURE" and obj.data == armatureData:
			armatureObj = obj
			break
	return armatureObj

			
def findHeaderObj(chainCollection = None):
	if chainCollection == None:
		if bpy.context.scene.re_chain_toolpanel.chainCollection != None:
			chainCollection = bpy.context.scene.re_chain_toolpanel.chainCollection
	if chainCollection != None:
		objList = chainCollection.all_objects
		headerList = [obj for obj in objList if obj.get("TYPE",None) == "RE_CHAIN_HEADER"]
		if len(headerList) >= 1:
			return headerList[0]
		else:
			return None
	else:
		return None

def checkNameUsage(baseName,checkSubString = True, objList = None):
	if objList == None:
		objList = bpy.data.objects
	if checkSubString:
		return any(baseName in name for name in [obj.name for obj in objList])
	else:
		return baseName in [obj.name for obj in objList]


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

def createChainCollection(collectionName,parentCollection = None):
	collection = bpy.data.collections.new(collectionName)
	collection.color_tag = "COLOR_02"
	collection["~TYPE"] = "RE_CHAIN_COLLECTION"
	if parentCollection != None:
		parentCollection.children.link(collection)
	else:
		bpy.context.scene.collection.children.link(collection)
	#bpy.context.scene.re_chain_toolpanel.chainCollection = collection.name
	bpy.context.scene.re_chain_toolpanel.chainCollection = collection
	if not collectionName.endswith(".clsp"):
		if collectionName.endswith(".chain2"):
			bpy.context.scene.re_chain_toolpanel.chainFileType = "chain2"
		else:
			bpy.context.scene.re_chain_toolpanel.chainFileType = "chain"
	return collection
def getCollection(collectionName,parentCollection = None,makeNew = False):
	if makeNew or not bpy.data.collections.get(collectionName):
		collection = bpy.data.collections.new(collectionName)
		collectionName = collection.name
		if parentCollection != None:
			parentCollection.children.link(collection)
		else:
			bpy.context.scene.collection.children.link(collection)
	return bpy.data.collections[collectionName]
def createEmpty(name,propertyList,parent = None,collection = None):
	obj = bpy.data.objects.new( name, None )
	obj.empty_display_size = .10
	obj.empty_display_type = 'PLAIN_AXES'
	obj.parent = parent
	for property in propertyList:
 
		obj[property[0]] = property[1]
	if collection == None:
		collection = bpy.context.scene.collection
		
	collection.objects.link(obj)
		
		
	return obj

def createCurveEmpty(name,propertyList,parent = None,collection = None):
	CURVE_DATA_NAME = "emptyCurve"#Share the data for all empty curves since it's not needed and it prevents unnecessary duplicates
	if CURVE_DATA_NAME in bpy.data.curves:
		curveData = bpy.data.curves[CURVE_DATA_NAME]
	else:	
		curveData = bpy.data.curves.new(CURVE_DATA_NAME, 'CURVE')
		curveData.use_path = False
		
	
	obj = bpy.data.objects.new(name, curveData)
	obj.parent = parent
	for property in propertyList:
 
		obj[property[0]] = property[1]
	if collection == None:
		collection = bpy.context.scene.collection
		
	collection.objects.link(obj)
		
		
	return obj
#Create a fake empty sphere from a curve
#The point of this is that curves are colored differently from empties, so chain collisions can be distinguished from nodes
#Also it prevents users from screwing with the empty display size
splinePointList = [([(-1.1, 0.0, 0.0), (0.0, 1.1, 0.0), (1.1, 0.0, 0.0), (0.0, -1.1, 0.0)], [(-1.1, -0.6073, 0.0), (-0.6073, 1.1, 0.0), (1.1, 0.6073, 0.0), (0.6073, -1.1, 0.0)], [(-1.1, 0.6073, 0.0), (0.6073, 1.1, 0.0), (1.1, -0.6073, 0.0), (-0.6073, -1.1, 0.0)]), ([(-1.1, 0.0, 0.0), (0.0, -0.0, -1.1), (1.1, 0.0, 0.0), (0.0, 0.0, 1.1)], [(-1.1, 0.0, 0.6073), (-0.6073, -0.0, -1.1), (1.1, -0.0, -0.6073), (0.6073, 0.0, 1.1)], [(-1.1, -0.0, -0.6073), (0.6073, -0.0, -1.1), (1.1, 0.0, 0.6073), (-0.6073, 0.0, 1.1)]), ([(0.0, 0.0, 1.1), (0.0, 1.1, -0.0), (-0.0, -0.0, -1.1), (-0.0, -1.1, 0.0)], [(0.0, -0.6073, 1.1), (0.0, 1.1, 0.6073), (-0.0, 0.6073, -1.1), (-0.0, -1.1, -0.6073)], [(0.0, 0.6073, 1.1), (0.0, 1.1, -0.6073), (-0.0, -0.6073, -1.1), (-0.0, -1.1, 0.6073)])]
def createFakeEmptySphere(name,propertyList,parent = None,collection = None):
	CURVE_DATA_NAME = "fakeEmptySphere"#Share the data for all empty curves since it's not needed and it prevents unnecessary duplicates
	if CURVE_DATA_NAME in bpy.data.curves:
		curveData = bpy.data.curves[CURVE_DATA_NAME]
	else:	
		curveData = bpy.data.curves.new(CURVE_DATA_NAME, 'CURVE')
		curveData.dimensions = "3D"
		curveData.use_path = False
		for pointSet in splinePointList:
		    coordList = pointSet[0]
		    leftList = pointSet[1]
		    rightList = pointSet[2]
		    spline = curveData.splines.new(type='BEZIER')
		    spline.use_cyclic_u = True
		    spline.bezier_points.add(3)
		    for index, point in enumerate(spline.bezier_points):
		        point.co = coordList[index]
		        point.handle_left = leftList[index]
		        point.handle_right = rightList[index]
	
	obj = bpy.data.objects.new(name, curveData)
	obj.parent = parent
	for property in propertyList:
 
		obj[property[0]] = property[1]
	if collection == None:
		collection = bpy.context.scene.collection
		
	collection.objects.link(obj)
		
		
	return obj

def createCurve(name,propertyList,parent = None,collection = None):
    curveData = bpy.data.curves.new(name, 'CURVE')
    curveData.use_path = False
        
    
    obj = bpy.data.objects.new(name, curveData)
    obj.parent = parent
    for property in propertyList:
 
        obj[property[0]] = property[1]
    if collection == None:
        collection = bpy.context.scene.collection
        
    collection.objects.link(obj)
        
        
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
			
			for bone in armature.data.bones:#If the armature has bone numbers, loop through every bone with bone numbers removed
				if bone.name.startswith("b") and ":" in bone.name and bone.name.split(":")[1] == boneName:
					searchBone = bone
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
			collisionObj.re_chain_chaincollision.collisionOffset = collisionObj.location# * .01
		else:
			for child in collisionObj.children:
				if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
					collisionObj.re_chain_chaincollision.collisionOffset = child.location# * .01
				elif child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
					collisionObj.re_chain_chaincollision.endCollisionOffset = child.location# * .01
def alignChains():
	for chain in [obj for obj in bpy.context.scene.objects if obj.get("TYPE",None) =="RE_CHAIN_CHAINGROUP"]:
		if len(chain.children) > 0:
			currentNode = chain.children[0]
			nodeObjList = [currentNode]
			while len(currentNode.children) > 1:
				currentNode.location = (0.0,0.0,0.0)
				currentNode.rotation_euler = (0.0,0.0,0.0)
				currentNode.scale = (1.0,1.0,1.0)
				
				hasNodeChild = False
				for child in currentNode.children:
					if child.get("TYPE",None) == "RE_CHAIN_NODE":
						nodeObjList.append(child)
						hasNodeChild = True
						
						currentNode = child
				if not hasNodeChild:#Avoid infinite loop in the case of a chain group consisting of a single node that contains a jiggle node
					break
			nodeObjList.reverse()
			for recurse in nodeObjList:
				if recurse.re_chain_chainnode.collisionRadius != 0:
					recurse.empty_display_size = recurse.re_chain_chainnode.collisionRadius# * 100
				else:
					recurse.empty_display_size = .01
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
	for collisionObj in [obj for obj in bpy.context.scene.objects if (obj.get("TYPE",None) in collisionTypeList)] :
		if collisionObj.get("TYPE",None) == "RE_CHAIN_COLLISION_SINGLE":
			if collisionObj.parent != None:
				collisionObj.constraints["BoneName"].inverse_matrix = collisionObj.parent.matrix_world.inverted()
			else:
				collisionObj.constraints["BoneName"].inverse_matrix = ((1.0,0.0,0.0,0.0),(0.0,1.0,0.0,0.0),(0.0,0.0,1.0,0.0),(0.0,0.0,0.0,1.0))
			#collisionObj.re_chain_chaincollision.radius = collisionObj.scale = [collisionObj.re_chain_chaincollision.radius]*3
			collisionObj.re_chain_chaincollision.radius = collisionObj.scale[0]
			#if collisionObj.re_chain_chaincollision.radius != 0:
				#collisionObj.empty_display_size = collisionObj.re_chain_chaincollision.radius# * 100
			#else:
				#collisionObj.empty_display_size = .01
		else:#Capsule
			for child in collisionObj.children:
				if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END" or child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
					child.constraints["BoneName"].inverse_matrix = child.parent.matrix_world.inverted()
					if child["TYPE"] == "RE_CHAIN_COLLISION_CAPSULE_START":
						collisionObj.re_chain_chaincollision.radius = child.scale[0]
					#child.scale = [collisionObj.re_chain_chaincollision.radius] * 3
					#if collisionObj.re_chain_chaincollision.radius != 0:
						#child.empty_display_size = collisionObj.re_chain_chaincollision.radius# * 100
					#else:
						#child.empty_display_size = .01
	bpy.context.view_layer.update()
def getArmatureHashList(armature):
	boneHashDict = {}
	for bone in armature.pose.bones:
		if bone.name.startswith("b") and ":" in bone.name:
			boneName = bone.name.split(":",1)[1]
		else:
			boneName = bone.name
		boneHashDict[hash_wide(boneName)] = bone
	return boneHashDict

def lockObjTransforms(obj,lockLocation = True,lockRotation = True,lockScale = True):
	if lockLocation:
		constraint = obj.constraints.new(type = "LIMIT_LOCATION")
		constraint.use_min_x = True
		constraint.use_min_y = True
		constraint.use_min_z = True
		
		constraint.use_max_x = True
		constraint.use_max_y = True
		constraint.use_max_z = True
	if lockRotation:
		constraint = obj.constraints.new(type = "LIMIT_ROTATION")
		constraint.use_limit_x = True
		constraint.use_limit_y = True
		constraint.use_limit_z = True
	
	if lockScale:
		constraint = obj.constraints.new(type = "LIMIT_SCALE")
		constraint.use_min_x = True
		constraint.use_min_y = True
		constraint.use_min_z = True
		
		constraint.use_max_x = True
		constraint.use_max_y = True
		constraint.use_max_z = True
		
		constraint.min_x = 1.0
		constraint.max_x = 1.0
		constraint.min_y = 1.0
		constraint.max_y = 1.0
		constraint.min_z = 1.0
		constraint.max_z = 1.0
		
		
def setChainBoneColor(armatureObj):
	#TODO Add theme option in preferences
	THEME = "THEME03"
	if armatureObj != None:
		if bpy.app.version < (4,0,0):
			if armatureObj.pose.bone_groups.get("Chain Bones",None) != None:
			    boneGroup = armatureObj.pose.bone_groups["Chain Bones"]
			else:
			    boneGroup = armatureObj.pose.bone_groups.new(name = "Chain Bones")
			boneGroup.color_set = THEME
		#chainCollection = bpy.data.collections.get(bpy.context.scene.re_chain_toolpanel.chainCollection)
		chainCollection = bpy.context.scene.re_chain_toolpanel.chainCollection
		if chainCollection != None:
			objList = chainCollection.all_objects
		else:
			objList = bpy.data.objects
		try:
			chainBoneList = [obj.constraints["BoneName"].subtarget for obj in objList if obj.get("TYPE",None) == "RE_CHAIN_NODE"]
		except:
			chainBoneList = []
		for chainBone in chainBoneList:
			if bpy.app.version < (4,0,0):
				poseBone = armatureObj.pose.bones.get(chainBone,None)
				if poseBone != None:
					poseBone.bone_group = boneGroup
			else:
				if chainBone in armatureObj.data.bones:
					bone = armatureObj.data.bones[chainBone]
					bone.color.palette = THEME
#---CHAIN IMPORT---#

def importChainFile(filepath,options,isChain2 = False):
	
	armature = None
	if bpy.data.armatures.get(options["targetArmature"]) != None:
		
		armature = findArmatureObjFromData(bpy.data.armatures[options["targetArmature"]])
	try:
		if armature == None and bpy.context.active_object != None and bpy.context.active_object.type == "ARMATURE":
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
	if not isChain2:
		chainFile = readREChain(filepath)
	else:
		chainFile = readREChain2(filepath)
	try:
		chainVersion = int(os.path.splitext(filepath)[1].replace(".",""))
	except:
		print("Unable to parse chain version number in file path.")
		chainVersion = None
	if chainVersion != None:
		if isChain2:
			bpy.context.scene["REChainLastImportedChain2Version"] = chainVersion
		else:
			bpy.context.scene["REChainLastImportedChainVersion"] = chainVersion
	removedItems = []
	#Pre check to see if the chain bones are present before trying to import the chain
	boneHashDict = getArmatureHashList(armature)
	for chainIndex,chainGroup in enumerate(chainFile.ChainGroupList):
		if not isChain2:
			endBone = findBone(chainGroup.terminateNodeName,armature)
			if endBone == None:
				raiseWarning("Could not find " + chainGroup.terminateNodeName + " bone on an armature. Make sure the mesh file is imported and only a single armature is in the scene.")
				removedItems.append(chainGroup)
			#return False
		else:
			if chainGroup.terminateNodeNameHash not in boneHashDict:
				raiseWarning(f"Could not find hashed bone ({str(chainGroup.terminateNodeNameHash)}) on an armature. Make sure the mesh file is imported and only a single armature is in the scene.")
				removedItems.append(chainGroup)
	if not options["importUnknowns"]:
		for item in removedItems:
			chainFile.ChainGroupList.remove(item)

	removedItems = []
	

	#Pre check to see that all collision bone hashes match to bones
	for collisionIndex,chainCollision in enumerate(chainFile.ChainCollisionList):
		if chainCollision.jointNameHash not in boneHashDict:
			raiseWarning("Collision Entry " + str(collisionIndex) + ": Joint hash ("+str(chainCollision.jointNameHash)+") does not match to any bones on the armature. The armature may be missing bones.")
			removedItems.append(chainCollision)
			#return False
		elif chainCollision.chainCollisionShape == 2 and chainCollision.pairJointNameHash not in boneHashDict:#Capsule
			raiseWarning("Collision Entry " + str(collisionIndex) + ": Pair joint hash ("+str(chainCollision.pairJointNameHash)+") does not match to any bones on the armature. The armature may be missing bones.")
			removedItems.append(chainCollision)
			#return False

	if not options["importUnknowns"]:
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
	
	headerObj = None
	if bpy.data.collections.get(options["mergeChain"]):#Merge with existing chain header if this is set
		headerObj = findHeaderObj(bpy.data.collections[options["mergeChain"]])
		chainCollection = bpy.data.collections[options["mergeChain"]]
		mergedChain = True
	
	if headerObj == None:
		mergedChain = False
		chainFileName = os.path.splitext(os.path.split(filepath)[1])[0]
		#Check if collections are grouped
		parentCollection = None
		if len(armature.users_collection) > 0 and armature.users_collection[0].get("~TYPE") == "RE_MESH_COLLECTION":
			for collection in bpy.data.collections:
				if armature.users_collection[0].name in collection.children:
					parentCollection = collection
					break
		chainCollection = createChainCollection(chainFileName,parentCollection)
		headerPropertyList = [("TYPE","RE_CHAIN_HEADER")]
		headerObj = createEmpty(f"CHAIN_HEADER {chainFileName}",headerPropertyList,None,chainCollection)
		
		getChainHeader(chainFile.Header,headerObj,isChain2)
		lockObjTransforms(headerObj)
		
	"""	
	if len(chainFile.ChainGroupList) > 0:
		chainEntryCollection = getCollection(f"Chain Entries - {chainCollection.name}",chainCollection,makeNew = not mergedChain)
		chainEntryCollection["TYPE"] = "RE_CHAIN_ENTRY_COLLECTION"
	else:
	"""
	chainEntryCollection = chainCollection
	print(f"Group Count: {len(chainFile.ChainGroupList)}")
	#WIND SETTINGS IMPORT
	currentWindSettingsNameIndex = 0
	windSettingsObjList = []
	for index, windSettings in enumerate(chainFile.WindSettingsList):
		name = "WIND_SETTINGS_"+str(currentWindSettingsNameIndex).zfill(2)
		if mergedChain:
			while(checkNameUsage(name,checkSubString=True)):
				currentWindSettingsNameIndex += 1
				name = "WIND_SETTINGS_"+str(currentWindSettingsNameIndex).zfill(2)
		else:
			currentWindSettingsNameIndex += 1
		windSettingsObj = createEmpty(name,[("TYPE","RE_CHAIN_WINDSETTINGS"),("tempID",windSettings.id)],headerObj,chainEntryCollection)
		#if isChain2:
			#getChain2WindSettings(windSettings,windSettingsObj)
		#else:
		getWindSettings(windSettings,windSettingsObj)
		lockObjTransforms(windSettingsObj)
		windSettingsObjList.append(windSettingsObj)
	#CHAIN SETTINGS IMPORT
	chainSettingsObjList = []
	chainSettingIDDict = dict()
	currentChainSettingsNameIndex = 0
	for settingsIndex, chainSettings in enumerate(chainFile.ChainSettingsList):
		
		#if chainSettings.windID >= len(windSettingsObjList):#Handle old incorrect chain exports that used the wind ID rather than index
		matchingWindSettingList = []
		matchingWindSettingList = [x for x in headerObj.children if x.get("TYPE") == "RE_CHAIN_WINDSETTINGS" and x.get("tempID") == chainSettings.windID]
		if matchingWindSettingList == []:
			chainSettingsParent = headerObj
		else:
			if len(matchingWindSettingList) > 1:
				raiseWarning("More than one wind settings object was found with an ID of " + str(chainSettings.windID))
			chainSettingsParent = matchingWindSettingList[0]
		"""
		else:
			if chainSettings.windID != -1 and chainSettings.windID < len(windSettingsObjList):
				chainSettingsParent = windSettingsObjList[chainSettings.windID]
			else:
				chainSettingsParent = headerObj
		"""
		name = "CHAIN_SETTINGS_"+str(currentChainSettingsNameIndex).zfill(2)
		if mergedChain:
			while(checkNameUsage(name,checkSubString=True)):
				currentChainSettingsNameIndex += 1
				name = "CHAIN_SETTINGS_"+str(currentChainSettingsNameIndex).zfill(2)
		else:
			currentChainSettingsNameIndex += 1
		chainSettingsObj = createEmpty(name, [("TYPE","RE_CHAIN_CHAINSETTINGS")],chainSettingsParent,chainEntryCollection)
		getChainSettings(chainSettings,chainSettingsObj,isChain2)
		lockObjTransforms(chainSettingsObj,lockLocation = False,lockRotation = True,lockScale = True)
		chainSettingsObjList.append(chainSettings)
		chainSettingIDDict[chainSettings.id] = chainSettingsObj
	#CHAIN GROUPS IMPORT
	currentChainGroupNameIndex = 0
	
	for groupIndex, chainGroup in enumerate(chainFile.ChainGroupList):
		#print(chainGroup)
		#if chainGroup.settingID == settingsIndex:
		if chainGroup.settingID in chainSettingIDDict:
			chainGroupParent = chainSettingIDDict[chainGroup.settingID]
		else:
			chainGroupParent = headerObj
			raiseWarning("Chain group attached to non existent chain setting id, Group: {groupIndex}, ID:{chainGroup.settingID}")
		subName = "CHAIN_GROUP_"+str(groupIndex).zfill(2)
		if mergedChain:
			while(checkNameUsage(subName,checkSubString=True)):
				currentChainGroupNameIndex +=1
				subName = "CHAIN_GROUP_"+str(currentChainGroupNameIndex).zfill(2)
		else:
			currentChainGroupNameIndex += 1
		if chainGroup.terminateNodeNameHash in boneHashDict:
			terminateNodeName = boneHashDict[chainGroup.terminateNodeNameHash].name
		else:
			terminateNodeName = str(chainGroup.terminateNodeNameHash)
		if terminateNodeName.count("_") > 1:
			name = subName + "_" + str(terminateNodeName.rsplit("_",1)[0])
		else:
			name = subName + "_" + str(terminateNodeName)
		chainGroupObj = createCurve(name, [("TYPE","RE_CHAIN_CHAINGROUP")],chainGroupParent,chainEntryCollection)
		getChainGroup(chainGroup,chainGroupObj,isChain2)
		endBone = findBone(terminateNodeName,armature)


		boneList = [endBone]#List of bones attached to the end bone
		if endBone != None:
			getBoneParentsRecursive(endBone, boneList, chainGroup.nodeCount-1)
			isGroupHashMissing = False
		else:
			isGroupHashMissing = True
		#Set up curve
		constraint = chainGroupObj.constraints.new("COPY_LOCATION")
		constraint.target = armature
		if not isGroupHashMissing:
			constraint.subtarget = boneList[-1].name
		chainGroupObj.show_in_front =  bpy.context.scene.re_chain_toolpanel.drawChainGroupsThroughObjects
		spline = chainGroupObj.data.splines.new("NURBS")
		spline.use_endpoint_u = True
		chainGroupObj.data.bevel_depth = bpy.context.scene.re_chain_toolpanel.groupDisplaySize
		chainGroupObj.data.dimensions = "3D"
		chainGroupObj.data.use_fill_caps = True
		chainGroupObj.data.materials.append(getChainGroupMat())
		if not isGroupHashMissing:
			spline.points.add(len(boneList) - 1)
			
			for i, o in enumerate(boneList):
				p = spline.points[i]
				objPos = list((armature.matrix_world @ o.matrix_local).to_translation())
				objPos.append(0.5)
				p.co = objPos
				h = chainGroupObj.modifiers.new(o.name, 'HOOK')
				h.object = armature
				h.subtarget = o.name
				h.vertex_indices_set([i])
		
		boneList.reverse()#Reverse list so it starts with the start of the chain
		baseNodeName = terminateNodeName.split("_end")[0]
		nodeParent = chainGroupObj
		
		terminalNameHashDict[chainGroup.terminateNodeNameHash]=chainGroupObj.name
		
		#TODO Add chain group subdata import and export, currently the subdata count is set to 0 and not imported
		#CHAIN NODES IMPORT
		subGroupList = [chainGroup.nodeList]
		subGroupObjList = []
		for subGroup in chainGroup.subGroupList:
			subGroupList.append(subGroup.nodeList) 
			chainSubGroupObj = createEmpty(f"CHAIN_GROUP_{str(groupIndex).zfill(2)}_SUBGROUP_{subGroup.subGroupID}", [("TYPE","RE_CHAIN_SUBGROUP")],chainSettingIDDict.get(subGroup.settingID,headerObj),chainEntryCollection)
			chainSubGroupObj.re_chain_chainsubgroup.parentGroup = chainGroupObj
			chainSubGroupObj.re_chain_chainsubgroup.subGroupID = subGroup.subGroupID
			constraint = chainSubGroupObj.constraints.new("COPY_LOCATION")
			constraint.target = armature
			if not isGroupHashMissing:
				constraint.subtarget = boneList[-1].name
			subGroupObjList.append(chainSubGroupObj)
		for subGroupIndex,nodeList in enumerate(subGroupList):
			if subGroupIndex == 0:
				nodeSubName = ""
				nodeParent = chainGroupObj
			else:
				nodeSubName = f"SUBGROUP_{subGroupObjList[subGroupIndex-1].re_chain_chainsubgroup.subGroupID}_"
				nodeParent = subGroupObjList[subGroupIndex-1]
			for nodeIndex,node in enumerate(nodeList):
				if boneList != [None]:
					name = boneList[nodeIndex].name
					currentBone = boneList[nodeIndex]
				else:
					currentBone = None
					raiseWarning("Could not find chain bones in armature, guessing node names.")
					if nodeIndex == len(chainGroup.nodeList)-1:
						name = baseNodeName + "_end"
					else:
						name = baseNodeName+"_"+str(nodeIndex).zfill(2)
				nodeObj = createEmpty(nodeSubName+name,[("TYPE","RE_CHAIN_NODE")],nodeParent,chainEntryCollection)
				
				getChainNode(node, nodeObj,isChain2)
				
				nodeParent = nodeObj
				
				nodeObj.empty_display_size = 2
				nodeObj.empty_display_type = "SPHERE"
				if subGroupIndex > 0:
					nodeObj["isSubGroupNode"] = 1
				else:
					nodeObj.show_name = bpy.context.scene.re_chain_toolpanel.showNodeNames
				nodeObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawNodesThroughObjects
				#nodeObj.show_name = True
				
				if node.constraintJntNameHash not in boneHashDict:
					
					if node.constraintJntNameHash == 0:
						nodeObj.re_chain_chainnode.constraintJntName = ""
					else:
						nodeObj.re_chain_chainnode.constraintJntName = str(node.constraintJntNameHash)
					
				else:
					nodeObj.re_chain_chainnode.constraintJntName = boneHashDict[node.constraintJntNameHash].name
				
				if isChain2:
					if node.jointHash not in boneHashDict:
						
						if node.jointHash == 0:
							nodeObj.re_chain_chainnode.jointHash = ""
						else:
							nodeObj.re_chain_chainnode.jointHash = str(node.jointHash)
						
					else:
						nodeObj.re_chain_chainnode.jointHash = boneHashDict[node.jointHash].name
				frame = createEmpty(nodeObj.name+"_ANGLE_LIMIT", [("TYPE","RE_CHAIN_NODE_FRAME")],nodeObj,chainEntryCollection)
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
				"""
				# Create new object, pass the light data 
				#lightObj = bpy.data.objects.new(name=nodeObj.name+"_ANGLE_LIMIT_HELPER", object_data=light_data)
				#lightObj["TYPE"] = "RE_CHAIN_NODE_FRAME_HELPER"
				#rotationMat = Matrix.Rotation(radians(-90.0),4,"Y")
				
				#lightObj.parent = frame
				lightObj = createCurveEmpty(nodeObj.name+"_ANGLE_LIMIT_HELPER", [("TYPE","RE_CHAIN_NODE_FRAME_HELPER")],frame,chainEntryCollection)
				lightObj.matrix_world = frame.matrix_world
				lightObj.show_wire = True
				#lightObj.matrix_local = lightObj.matrix_local @ rotationMat
				lightObj.hide_select = True#Disable ability to select to avoid it getting in the way
				
				lightObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawConesThroughObjects
				lightObj.hide_viewport = not bpy.context.scene.re_chain_toolpanel.showAngleLimitCones
				modifier = lightObj.modifiers.new(name="REChainGeometryNodes", type='NODES')
				nodeGroup = getConeGeoNodeTree(isSubGroup = subGroupIndex > 0)
				if modifier.node_group != None and modifier.node_group.name in bpy.data.node_groups:
					bpy.data.node_groups.remove(modifier.node_group)
				
				modifier.node_group = nodeGroup
				
				#Force update function to run so that the cone updates
				nodeObj.re_chain_chainnode.angleLimitRad = nodeObj.re_chain_chainnode.angleLimitRad
				nodeObj.re_chain_chainnode.collisionRadius = nodeObj.re_chain_chainnode.collisionRadius
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
				
				#chainEntryCollection.objects.link(lightObj)
				
				
				constraint = nodeObj.constraints.new(type = "COPY_LOCATION")
				constraint.target = armature
				if currentBone != None:
					constraint.subtarget = currentBone.name #.split(":")[len(bone.name.split(":"))-1]
				#terminalNameHashDict[hash_wide(currentBone.name)] = nodeObj
				constraint.name = "BoneName"
				
				constraint = nodeObj.constraints.new(type = "COPY_ROTATION")
				constraint.target = armature
				if currentBone != None:
					constraint.subtarget = currentBone.name #.split(":")[len(bone.name.split(":"))-1]
				#terminalNameHashDict[hash_wide(currentBone.name)] = nodeObj
				constraint.name = "BoneRotation"
				
				constraint = nodeObj.constraints.new(type = "COPY_SCALE")
				constraint.target = chainGroupObj
				constraint.name = "BoneScale"
					
					
				if node.jiggleData:
					jiggle = node.jiggleData
					jiggleObj = createEmpty(name+"_JIGGLE",[("TYPE","RE_CHAIN_JIGGLE")],nodeObj,chainEntryCollection)
					#if isChain2:
						#getChain2Jiggle(jiggle, jiggleObj)
					#else:
					getChainJiggle(jiggle, jiggleObj)
					jiggleObj.empty_display_size = .2
					jiggleObj.show_name = bpy.context.scene.re_chain_toolpanel.showNodeNames
					jiggleObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawNodesThroughObjects
					jiggleObj.rotation_mode = 'QUATERNION'
					jiggleObj.rotation_quaternion = (jiggle.rangeAxisW,jiggle.rangeAxisX,jiggle.rangeAxisY,jiggle.rangeAxisZ)
					jiggleObj.scale = (jiggle.rangeX, jiggle.rangeY, jiggle.rangeZ)
					jiggleObj.location = (jiggle.rangeOffsetX, jiggle.rangeOffsetY, jiggle.rangeOffsetZ)
					
			if len(chainGroup.nodeList) > 0:
				lightObj["isLastNode"] = 1
				if isGroupHashMissing:
					constraint = nodeObj.constraints.new(type = "COPY_LOCATION")
					constraint.target = armature
					constraint.subtarget = str(chainGroup.terminateNodeNameHash) #.split(":")[len(bone.name.split(":"))-1]
					#terminalNameHashDict[hash_wide(currentBone.name)] = nodeObj
					constraint.name = "BoneName"
				#frame.hide_viewport = bpy.context.scene.re_chain_toolpanel.hideLastNodeAngleLimit
				lightObj.hide_viewport = bpy.context.scene.re_chain_toolpanel.hideLastNodeAngleLimit
		alignChains()
	#CHAIN COLLISION IMPORT
	if len(chainFile.ChainCollisionList) > 0:
		collisionCollection = getCollection(f"Chain Collisions - {chainCollection.name}",chainCollection,makeNew = not mergedChain)
		collisionCollection["TYPE"] = "RE_CHAIN_COLLISION_COLLECTION"
	singleObjectColList = ["SPHERE","OBB","PLANE","LINESPHERE","LERPSPHERE"]
	enumItemDict ={0:"NONE",1:"SPHERE",2:"CAPSULE",3:"OBB",4:"PLANE",5:"TCAPSULE",6:"LINESPHERE",7:"LERPSPHERE",-1:"UNKNOWN"}
	for collisionIndex,chainCollision in enumerate(chainFile.ChainCollisionList):
		#print(chainCollision)
		currentCollisionIndex = collisionIndex
		subName = "COL_"+str(currentCollisionIndex).zfill(2)
		while(checkNameUsage(subName,checkSubString=True)):
			currentCollisionIndex +=1
			subName = "COL_"+str(currentCollisionIndex).zfill(2)
		
		shape = enumItemDict[chainCollision.chainCollisionShape]
		
		if chainCollision.jointNameHash in boneHashDict and (chainCollision.pairJointNameHash in boneHashDict or chainCollision.pairJointNameHash == 0):
			if (shape != "CAPSULE" and shape != "TCAPSULE") and chainCollision.pairJointNameHash == 0:
				name = "COL_" +str(currentCollisionIndex).zfill(2)+ "_"+shape + " " + boneHashDict[chainCollision.jointNameHash].name
				#colSphereObj = createFakeEmptySphere(name, [("TYPE","RE_CHAIN_COLLISION_SINGLE")],headerObj,collisionCollection)
				colSphereObj = createCurveEmpty(name, [("TYPE","RE_CHAIN_COLLISION_SINGLE")],headerObj,collisionCollection)
				
				#if isChain2:
					#getChain2Collision(chainCollision,colSphereObj)
				#else:
				getChainCollision(chainCollision,colSphereObj)
				colSphereObj.re_chain_chaincollision.chainCollisionShape = str(chainCollision.chainCollisionShape)
				colSphereObj.re_chain_chaincollision.collisionOffset = (chainCollision.posX,chainCollision.posY,chainCollision.posZ)
				colSphereObj.rotation_mode = "QUATERNION" 
				colSphereObj.rotation_quaternion = (chainCollision.rotOffsetW,chainCollision.rotOffsetX,chainCollision.rotOffsetY,chainCollision.rotOffsetZ)
				
				#colSphereObj.empty_display_type = "SPHERE"
				#colSphereObj.empty_display_size = 1.1
				constraint = colSphereObj.constraints.new(type = "CHILD_OF")
				constraint.target = armature
				constraint.subtarget = boneHashDict[chainCollision.jointNameHash].name
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
				
				#modifier["Input_0"] = colSphereObj
			else:#CAPSULE
				if chainCollision.chainCollisionShape == 0:
					subName +="_NONE"
				name = subName+ f"_{shape} - {boneHashDict[chainCollision.jointNameHash].name} > {boneHashDict[chainCollision.pairJointNameHash].name}" 
				colCapsuleRootObj = createCurveEmpty(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_ROOT")],headerObj,collisionCollection)
				lockObjTransforms(colCapsuleRootObj)
				#colCapsuleRootObj.empty_display_size = .1
				#if isChain2:
					#getChain2Collision(chainCollision,colCapsuleRootObj)
				#else:
				getChainCollision(chainCollision,colCapsuleRootObj)
				colCapsuleRootObj.re_chain_chaincollision.chainCollisionShape = str(chainCollision.chainCollisionShape)
				name = subName+ f"_{shape}_BEGIN" + " " + boneHashDict[chainCollision.jointNameHash].name
				colCapsuleStartObj = createFakeEmptySphere(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_START")],colCapsuleRootObj,collisionCollection)
				colCapsuleRootObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCollisionsThroughObjects
				
				colCapsuleStartObj.re_chain_chaincollision.collisionOffset = (chainCollision.posX,chainCollision.posY,chainCollision.posZ)
				colCapsuleStartObj.rotation_mode = "QUATERNION" 
				colCapsuleStartObj.rotation_quaternion = (chainCollision.rotOffsetW,chainCollision.rotOffsetX,chainCollision.rotOffsetY,chainCollision.rotOffsetZ)
				
				#colCapsuleStartObj.empty_display_type = "SPHERE"
				#colCapsuleStartObj.empty_display_size = 1.1
				constraint = colCapsuleStartObj.constraints.new(type = "CHILD_OF")
				constraint.target = armature
				constraint.subtarget = boneHashDict[chainCollision.jointNameHash].name
				constraint.name = "BoneName"
				
				constraint.use_scale_x = False
				constraint.use_scale_y = False
				constraint.use_scale_z = False
				#colCapsuleStartObj.show_name = True
				colCapsuleStartObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
				colCapsuleStartObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCapsuleHandlesThroughObjects
				
				name = subName+ f"_{shape}_END" + " " + boneHashDict[chainCollision.pairJointNameHash].name
				colCapsuleEndObj = createFakeEmptySphere(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_END")],colCapsuleRootObj,collisionCollection)
				colCapsuleEndObj.re_chain_chaincollision.endCollisionOffset = (chainCollision.pairPosX,chainCollision.pairPosY,chainCollision.pairPosZ)
				#colCapsuleEndObj.empty_display_type = "SPHERE"
				#colCapsuleEndObj.empty_display_size = 1.1
				constraint = colCapsuleEndObj.constraints.new(type = "CHILD_OF")
				constraint.target = armature
				constraint.subtarget = boneHashDict[chainCollision.pairJointNameHash].name
				constraint.name = "BoneName"
				
				constraint.use_scale_x = False
				constraint.use_scale_y = False
				constraint.use_scale_z = False
				#colCapsuleEndObj.show_name = True
				colCapsuleEndObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
				colCapsuleEndObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCapsuleHandlesThroughObjects
				
				#constraint = colCapsuleEndObj.constraints.new(type = "COPY_SCALE")
				#constraint.target = colCapsuleStartObj
				#constraint.name = "CopyRadius"
				
				#Update start and end obj 
				colCapsuleRootObj.re_chain_chaincollision.radius = colCapsuleRootObj.re_chain_chaincollision.radius
				colCapsuleRootObj.re_chain_chaincollision.endRadius = colCapsuleRootObj.re_chain_chaincollision.endRadius
				
				#colCapsuleRootObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCollisionsThroughObjects
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
	#CHAIN LINK IMPORT
	#print(terminalNameHashDict)#debug
	currentChainLinkNameIndex = 0
	if len(chainFile.ChainLinkList) > 0:
		linkCollection = getCollection(f"Chain Links - {chainCollection.name}",chainCollection,makeNew = not mergedChain)
		linkCollection["TYPE"] = "RE_CHAIN_LINK_COLLECTION"
	for index, chainLink in enumerate(chainFile.ChainLinkList):
		name = "LINK_"+str(currentChainLinkNameIndex).zfill(2)
		if mergedChain:
			while(checkNameUsage(name,checkSubString=True)):
				currentChainLinkNameIndex += 1
				name = "LINK_"+str(currentChainLinkNameIndex).zfill(2)
		else:
			currentChainLinkNameIndex += 1
		
		shortNameA = (terminalNameHashDict[chainLink.terminateNodeNameHashA] if chainLink.terminateNodeNameHashA in terminalNameHashDict else str(chainLink.terminateNodeNameHashA)).replace("CHAIN_GROUP_","")
		shortNameB = (terminalNameHashDict[chainLink.terminateNodeNameHashB] if chainLink.terminateNodeNameHashB in terminalNameHashDict else str(chainLink.terminateNodeNameHashB)).replace("CHAIN_GROUP_","")
		chainLinkObj = createCurveEmpty(f"{name} - {shortNameA} > {shortNameB}", [("TYPE","RE_CHAIN_LINK")],headerObj,linkCollection)
		#if isChain2:
			#getChain2Link(chainLink,chainLinkObj)
		#else:
		getChainLink(chainLink,chainLinkObj)
		lockObjTransforms(chainLinkObj)
		chainLinkObj.re_chain_chainlink.chainGroupAObject = terminalNameHashDict[chainLink.terminateNodeNameHashA] if chainLink.terminateNodeNameHashA in terminalNameHashDict else str(chainLink.terminateNodeNameHashA)
		chainLinkObj.re_chain_chainlink.chainGroupBObject = terminalNameHashDict[chainLink.terminateNodeNameHashB] if chainLink.terminateNodeNameHashB in terminalNameHashDict else str(chainLink.terminateNodeNameHashB)
		
		groupAObj = bpy.data.objects.get(chainLinkObj.re_chain_chainlink.chainGroupAObject)
		groupBObj = bpy.data.objects.get(chainLinkObj.re_chain_chainlink.chainGroupBObject)
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
		
		#Import link collision
		if chainLink.nodeColLinkList != []:
			chainLinkANodeObjList = []
			chainLinkBNodeObjList = []
			if groupAObj != None and len(groupAObj.children) > 0:
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
			if groupBObj != None and len(groupBObj.children) > 0:
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
			for index,linkCollision in enumerate(chainLink.nodeColLinkList):
				
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
				linkCollisionObj.re_chain_chainlink_collision.collisionRadius = linkCollision.collisionRadius
				linkCollisionObj.re_chain_chainlink_collision.collisionFilterFlags = linkCollision.collisionFilterFlags
				linkCollisionObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawLinkCollisionsThroughObjects
	
	setChainBoneColor(armature)
	windSettingsObjList.clear()
	chainSettingsObjList.clear()
	return True
def chainErrorCheck(chainCollectionName):
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
	if bpy.data.collections.get(chainCollectionName) != None:
		objList = bpy.data.collections[chainCollectionName].all_objects
	else:
		errorList.append("Chain objects must be contained in a collection.")
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
			
			validParentTypeList = ["RE_CHAIN_CHAINGROUP","RE_CHAIN_NODE","RE_CHAIN_SUBGROUP"]
			if obj.parent != None:    
				if obj.parent.get("TYPE",None) not in validParentTypeList:
					errorList.append(obj.name + " node cannot be parented to an object of type: "+str(obj.parent.get("TYPE",None)))
			else:
				errorList.append(obj.name + " node must be parented to a chain group or a chain node object.")
			
			if obj.constraints.get("BoneName",False):
				pass
				#if obj.constraints["BoneName"].target == "" or obj.constraints["BoneName"].target == None or obj.constraints["BoneName"].subtarget == "":
					#errorList.append("Invalid child of constraint on " + obj.name)
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
					validChainGroup = True
					#for nodeChild in child.children:
						#if nodeChild.get("TYPE") == "RE_CHAIN_NODE":
							#validChainGroup = True
			if not validChainGroup:
				#errorList.append("Chain group "+obj.name + " must contain at least two nodes.")
				errorList.append("Chain group "+obj.name + " must contain at least one node.")#Thank SF6 and it's weird chains for this
		
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
			elif obj.re_chain_chainlink.chainGroupAObject != "":
				raiseWarning(obj.name + ": Chain Group A is set to an object that doesn't exist")
				#errorList.append(obj.name + ": Chain Group A is set to an object that doesn't exist")
				
			if bpy.context.scene.objects.get(obj.re_chain_chainlink.chainGroupBObject,None) != None:
				if bpy.context.scene.objects[obj.re_chain_chainlink.chainGroupBObject].get("TYPE",None) != "RE_CHAIN_CHAINGROUP":
					errorList.append(obj.name + ": Chain Group B must be set to a Chain Group object")
			elif obj.re_chain_chainlink.chainGroupBObject != "":
				#errorList.append(obj.name + ": Chain Group B is set to an object that doesn't exist")
				raiseWarning(obj.name + ": Chain Group B is set to an object that doesn't exist")
	if headerCount == 0:
		errorList.append("No chain header object in collection.")
		
	elif headerCount > 1:
		errorList.append("Cannot export with more than one chain header in a collection.")
	
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

def fixTaperedCapsules(chainCollisionObjList,version,isChain2):
	for chainCollisionObj in chainCollisionObjList:
		if chainCollisionObj.get("TYPE") == "RE_CHAIN_COLLISION_CAPSULE_ROOT":
			startCapsule = None
			endCapsule = None
			for child in chainCollisionObj.children: 
				if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
					startCapsule = child
				elif child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
					endCapsule = child
			if startCapsule != None and endCapsule != None:
				if chainCollisionObj.re_chain_chaincollision.chainCollisionShape != "5" and startCapsule.scale[0] != endCapsule.scale[0]:
					if version >= 46 or isChain2:
						print(f"Start and end radius do not match on {chainCollisionObj.name}, changed to a tapered capsule")
						chainCollisionObj.re_chain_chaincollision.chainCollisionShape = "5"
						chainCollisionObj.name = chainCollisionObj.name.replace("_CAPSULE","_TCAPSULE")
						startCapsule.name = startCapsule.name.replace("_CAPSULE","_TCAPSULE")
						endCapsule.name = endCapsule.name.replace("_CAPSULE","_TCAPSULE")
					else:
						print(f"Tapered capsules are not supported on versions lower than 46, {chainCollisionObj.name} changed to normal capsule")
						chainCollisionObj.re_chain_chaincollision.chainCollisionShape = "2"
						chainCollisionObj.name = chainCollisionObj.name.replace("_TCAPSULE","_CAPSULE")
						startCapsule.name = startCapsule.name.replace("_TCAPSULE","_CAPSULE")
						endCapsule.name = endCapsule.name.replace("_TCAPSULE","_CAPSULE")
						endCapsule.scale = startCapsule.scale
				elif version < 46 and chainCollisionObj.re_chain_chaincollision.chainCollisionShape == "5" and not isChain2:
					print(f"Tapered capsules are not supported on versions lower than 46, {chainCollisionObj.name} changed to normal capsule")
					chainCollisionObj.re_chain_chaincollision.chainCollisionShape = "2"
					chainCollisionObj.name = chainCollisionObj.name.replace("_TCAPSULE","_CAPSULE")
					startCapsule.name = startCapsule.name.replace("_TCAPSULE","_CAPSULE")
					endCapsule.name = endCapsule.name.replace("_TCAPSULE","_CAPSULE")
					endCapsule.scale = startCapsule.scale
def exportChainFile(filepath,options, version, isChain2 = False):
	valid = chainErrorCheck(options["targetCollection"])
	chainCollection = bpy.data.collections.get(options["targetCollection"],None)
	if valid and chainCollection != None:
		print(textColors.OKCYAN + "__________________________________\nChain export started."+textColors.ENDC)
		if isChain2:
			newChainFile = Chain2File()
		else:
			newChainFile = ChainFile()
		
		objList = chainCollection.all_objects
		
		windSettingsObjList = []
		chainSettingsObjList = []
		chainGroupObjList = []
		chainSubGroupObjList = []
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
			elif objType == "RE_CHAIN_SUBGROUP":
				chainSubGroupObjList.append(obj)
			elif objType == "RE_CHAIN_LINK":
				chainLinkObjList.append(obj)
			elif objType in collisionTypes:
				chainCollisionObjList.append(obj)
				
		windSettingsObjList.sort(key = lambda item: item.name)
		chainSettingsObjList.sort(key = lambda item: item.name)
		chainGroupObjList.sort(key = lambda item: item.name)
		chainCollisionObjList.sort(key = lambda item: item.name)
		
		childSubGroupDict = dict()
		for subGroupObj in chainSubGroupObjList:
			if subGroupObj.re_chain_chainsubgroup.parentGroup != None:
				if subGroupObj.re_chain_chainsubgroup.parentGroup in childSubGroupDict:
					childSubGroupDict[subGroupObj.re_chain_chainsubgroup.parentGroup].append(subGroupObj)
				else:
					childSubGroupDict[subGroupObj.re_chain_chainsubgroup.parentGroup] = [subGroupObj]
			
		
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
		setChainHeaderData(newChainFile.Header, headerObj,isChain2)
		
		chainGroupTerminateNodeHashDict = {}#Used for chain links
		for windSettingsObj in windSettingsObjList:
			if isChain2:
				windSettings = Chain2WindSettingsData()
			else:
				windSettings = WindSettingsData()
			setWindSettingsData(windSettings, windSettingsObj,isChain2)
			newChainFile.WindSettingsList.append(windSettings)
		
		for chainSettingsObj in chainSettingsObjList:
			if isChain2:
				chainSettings = Chain2SettingsData()
				
				#MHWilds automatic fix for missing chain setting subdata
				if len(chainSettingsObj.re_chain_chainsettings.subDataList_items) == 0 and version == 12:
					newListItem = chainSettingsObj.re_chain_chainsettings.subDataList_items.add()
					newListItem.values = (0,1,0,0,0,0,0)
					
					newListItem = chainSettingsObj.re_chain_chainsettings.subDataList_items.add()
					newListItem.values = (0,1,0,0,77,0,0)
				print(f"Detected missing MH Wilds chain setting subdata, added missing subdata to {chainSettingsObj.name}")
			else:
				chainSettings = ChainSettingsData()
				
			setChainSettingsData(chainSettings, chainSettingsObj,isChain2)
			
			
			
			newChainFile.ChainSettingsList.append(chainSettings)
		
		for chainGroupObj in chainGroupObjList:
			if isChain2:
				chainGroup = Chain2GroupData()
			else:
				chainGroup = ChainGroupData()
			setChainGroupData(chainGroup, chainGroupObj,isChain2)

			
			if chainGroupObj.parent != None and chainGroupObj.parent.get("TYPE") == "RE_CHAIN_CHAINSETTINGS":
				chainGroup.settingID = chainGroupObj.parent.re_chain_chainsettings.id
			else:
				chainGroup.settingID = -1
			
			windSettingsParentObj = None
			if chainGroupObj.parent != None and chainGroupObj.parent.parent != None and chainGroupObj.parent.parent.get("TYPE") == "RE_CHAIN_WINDSETTINGS":
				windSettingsParentObj = chainGroupObj.parent.parent
			
			if windSettingsParentObj != None:
				chainGroup.windID = windSettingsParentObj.re_chain_windsettings.id

			else:
				chainGroup.windID = 0
			
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
				if isChain2:
					node = Chain2NodeData()
				else:
					node = ChainNodeData()
				setChainNodeData(node, nodeObj,isChain2)
				if nodeObj.re_chain_chainnode.constraintJntName.isdigit():
					node.constraintJntNameHash = int(nodeObj.re_chain_chainnode.constraintJntName)
					
				else:
					node.constraintJntNameHash = hash_wide(nodeObj.re_chain_chainnode.constraintJntName)
				
				if nodeObj.re_chain_chainnode.constraintJntName.strip() == "":
					node.constraintJntNameHash = 0
				
				#chain2
				if isChain2:
					if nodeObj.re_chain_chainnode.jointHash.isdigit():
						node.jointHash = int(nodeObj.re_chain_chainnode.jointHash)
						
					else:
						node.jointHash = hash_wide(nodeObj.re_chain_chainnode.jointHash)
					
					if nodeObj.re_chain_chainnode.jointHash.strip() == "":
						node.jointHash = 0
				
				
				chainGroup.nodeList.append(node)
				if version >= 35 or isChain2:
					for child in nodeObj.children:
						if child.get("TYPE",None) == "RE_CHAIN_JIGGLE":
							if isChain2:
								jiggle = Chain2JiggleData()
							else:
								jiggle = ChainJiggleData()
							setChainJiggleData(jiggle, child)
							node.jiggleData = jiggle
							break
			
			
			#Get subgroups if present
			if chainGroupObj in childSubGroupDict:
				childSubGroupDict[chainGroupObj].sort(key = lambda item: item.re_chain_chainsubgroup.subGroupID)
				
				for subGroupObj in childSubGroupDict[chainGroupObj]:
					if isChain2:
						subGroupData = Chain2SubGroupData()
					else:
						subGroupData = ChainSubGroupData()
						
					subGroupData.subGroupID = subGroupObj.re_chain_chainsubgroup.subGroupID
					if subGroupObj.parent != None and subGroupObj.parent.get("TYPE") == "RE_CHAIN_CHAINSETTINGS":
						subGroupData.settingID = subGroupObj.parent.re_chain_chainsettings.id
					else:
						subGroupData.settingID = -1
					nodeObjList = []
					currentNode = subGroupObj.children[0]
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
						if isChain2:
							node = Chain2NodeData()
						else:
							node = ChainNodeData()
						setChainNodeData(node, nodeObj,isChain2)
						if nodeObj.re_chain_chainnode.constraintJntName.isdigit():
							node.constraintJntNameHash = int(nodeObj.re_chain_chainnode.constraintJntName)
							
						else:
							node.constraintJntNameHash = hash_wide(nodeObj.re_chain_chainnode.constraintJntName)
						
						if nodeObj.re_chain_chainnode.constraintJntName.strip() == "":
							node.constraintJntNameHash = 0
						
						#chain2
						if isChain2:
							if nodeObj.re_chain_chainnode.jointHash.isdigit():
								node.jointHash = int(nodeObj.re_chain_chainnode.jointHash)
								
							else:
								node.jointHash = hash_wide(nodeObj.re_chain_chainnode.jointHash)
							
							if nodeObj.re_chain_chainnode.jointHash.strip() == "":
								node.jointHash = 0
						
						
						subGroupData.nodeList.append(node)
						if version >= 35 or isChain2:
							for child in nodeObj.children:
								if child.get("TYPE",None) == "RE_CHAIN_JIGGLE":
									if isChain2:
										jiggle = Chain2JiggleData()
									else:
										jiggle = ChainJiggleData()
									setChainJiggleData(jiggle, child)
									node.jiggleData = jiggle
									break
					
					if len(subGroupData.nodeList) == len(chainGroup.nodeList):
						chainGroup.subGroupList.append(subGroupData)
					else:
						raiseWarning(f"Skipped subgroup {subGroupData.subGroupID} on {chainGroupObj.name} because the amount of nodes on the sub group does not match the parent chain group.")
						
			
			if "BoneName" in nodeObjList[-1].constraints:
				terminateNodeName =  nodeObjList[-1].constraints["BoneName"].subtarget
			else:
				terminateNodeName = nodeObjList[-1].name.split(".")[0]
			
			if terminateNodeName.startswith("b") and ":" in terminateNodeName:
				terminateNodeName = terminateNodeName.split(":",1)[1]
			if terminateNodeName.isdigit() and int(terminateNodeName) <= 4294967295:
				chainGroup.terminateNodeNameHash = int(terminateNodeName)
			else:
				chainGroup.terminateNodeNameHash = hash_wide(terminateNodeName)
			chainGroupTerminateNodeHashDict[chainGroupObj.name] = chainGroup.terminateNodeNameHash
			chainGroup.terminateNodeName = terminateNodeName
			chainGroup.nodeCount = len(chainGroup.nodeList)
			newChainFile.ChainGroupList.append(chainGroup)

		fixTaperedCapsules(chainCollisionObjList,version,isChain2)
		
		for chainCollisionObj in chainCollisionObjList:
			if isChain2:
				chainCollision = Chain2CollisionData()
			else:
				chainCollision = ChainCollisionData()
			setChainCollisionData(chainCollision, chainCollisionObj,isChain2)
			newChainFile.ChainCollisionList.append(chainCollision)
			
		for chainLinkObj in chainLinkObjList:
			if isChain2:
				chainLink = Chain2LinkData()
			else:
				chainLink = ChainLinkData()
			setChainLinkData(chainLink, chainLinkObj,isChain2)
			colObjList = []
			for obj in chainLinkObj.children:
				if obj.get("TYPE") == "RE_CHAIN_LINK_COLLISION":
					colObjList.append(obj)
			colObjList.sort(key = lambda item: item.name)
			
			for colObj in colObjList:
				linkNode = ChainLinkNode()
				setChainLinkCollisionNodeData(linkNode, colObj)
				chainLink.nodeColLinkList.append(linkNode)
			
			
			chainLink.terminateNodeNameHashA = chainGroupTerminateNodeHashDict[chainLinkObj.re_chain_chainlink.chainGroupAObject] if chainLinkObj.re_chain_chainlink.chainGroupAObject in chainGroupTerminateNodeHashDict else int(chainLinkObj.re_chain_chainlink.chainGroupAObject) if chainLinkObj.re_chain_chainlink.chainGroupAObject.isdigit() else 0
			chainLink.terminateNodeNameHashB = chainGroupTerminateNodeHashDict[chainLinkObj.re_chain_chainlink.chainGroupBObject] if chainLinkObj.re_chain_chainlink.chainGroupBObject in chainGroupTerminateNodeHashDict else int(chainLinkObj.re_chain_chainlink.chainGroupBObject) if chainLinkObj.re_chain_chainlink.chainGroupBObject.isdigit() else 0
			
			chainLink.nodeCount = len(colObjList)
			if chainLink.nodeCount == 0:
				for chainGroup in newChainFile.ChainGroupList:
					if chainLink.terminateNodeNameHashA == chainGroup.terminateNodeNameHash:
						chainLink.nodeCount = chainGroup.nodeCount
						break
			newChainFile.ChainLinkList.append(chainLink)
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