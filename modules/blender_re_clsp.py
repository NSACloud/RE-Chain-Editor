#---BLENDER FUNCTIONS---#
import bpy
import os

from .gen_functions import textColors,raiseWarning,raiseError
from .file_re_clsp import readRECLSP,writeRECLSP,CLSPFile,CLSPEntry
from .pymmh3 import hash_wide
from .blender_utils import showMessageBox,showErrorMessageBox
from .re_chain_geoNodes import getColCapsuleGeoNodeTree,getColSphereGeoNodeTree


#TODO Clean this up, most of it is copied from chain stuff and a lot is redundant

def findArmatureObjFromData(armatureData):
	armatureObj = None
	for obj in bpy.context.scene.objects:
		if obj.type == "ARMATURE" and obj.data == armatureData:
			armatureObj = obj
			break
	return armatureObj

			
def findHeaderObj(chainCollection = None):
	if chainCollection == None:
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
	bpy.context.scene.re_chain_toolpanel.chainCollection = collection.name
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
	for collisionObj in [obj for obj in bpy.context.scene.objects if (obj.get("TYPE",None) in collisionTypeList)] :
		if collisionObj.get("TYPE",None) != "RE_CHAIN_COLLISION_CAPSULE_ROOT":
			collisionObj.re_chain_chaincollision.collisionOffset = collisionObj.location# * .01
			collisionObj.re_chain_chaincollision.chainCollisionShape.radius = collisionObj.scale[0]
		else:
			for child in collisionObj.children:
				if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
					collisionObj.re_chain_chaincollision.collisionOffset = child.location# * .01
					collisionObj.re_chain_chaincollision.radius = child.scale[0]
				elif child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
					collisionObj.re_chain_chaincollision.endCollisionOffset = child.location# * .01
					if collisionObj.re_chain_chaincollision.chainCollisionShape == "5":
						collisionObj.re_chain_chaincollision.endRadius = child.scale[0]
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
			collisionObj.constraints["BoneName"].inverse_matrix = collisionObj.constraints["BoneName"].target.matrix_world.inverted()
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
		
		

#---CLSP IMPORT---#
chainShapeEnumTranslationDict = {
	0:"1",#Sphere
	1:"2",#Capsule
	3:"5",#Tapered Capsule
	"1":0,
	"2":1,
	"5":3
	}
def importCLSPFile(filepath,options):
	
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
				showErrorMessageBox("More than one armature was found in the scene. Select an armature before importing the CLSP.")
				return False
			if obj.type == "ARMATURE":
				armature = obj
	if armature == None:#If an armature is not found after searching, stop importing
		showErrorMessageBox("No armature in scene. The armature from the mesh file must be present in order to import the CLSP file.")
		return False
	#print(armature)
	#convert header to empty
	clspFile = readRECLSP(filepath)
	clspFileName = os.path.splitext(os.path.split(filepath)[1])[0]
	try:
		chainVersion = int(os.path.splitext(filepath)[1].replace(".",""))
	except:
		print("Unable to parse chain version number in file path.")
		chainVersion = None
	if chainVersion != None:
		bpy.context.scene["REChainLastImportedCLSPVersion"] = chainVersion
	removedItems = []
	removedItems = []
	boneHashDict = getArmatureHashList(armature)
			#return False


	#CHAIN COLLISION IMPORT
	if len(clspFile.clspEntryList) > 0:
		parentCollection = None
		if len(armature.users_collection) > 0 and armature.users_collection[0].get("~TYPE") == "RE_MESH_COLLECTION":
			for collection in bpy.data.collections:
				if armature.users_collection[0].name in collection.children:
					parentCollection = collection
					break
		collisionCollection = getCollection(clspFileName,parentCollection,makeNew = True)
		collisionCollection.color_tag = "COLOR_02"
		collisionCollection["~TYPE"] = "RE_CLSP_COLLECTION"
		bpy.context.scene.re_chain_toolpanel.chainCollection = collisionCollection
	singleObjectColList = ["SPHERE","OBB","PLANE","LINESPHERE","LERPSPHERE"]
	
	enumItemDict ={0:"SPHERE",1:"CAPSULE",2:"BOX",3:"TCAPSULE",4:"PLANE"}
	missingHashWarning = False
	for collisionIndex,chainCollision in enumerate(clspFile.clspEntryList):
		if chainCollision.jointNameHash in boneHashDict:
			jointName = boneHashDict[chainCollision.jointNameHash].name
		else:
			missingHashWarning = True
			jointName = "HASH_"+str(chainCollision.jointNameHash)
		if chainCollision.pairJointNameHash in boneHashDict:
			pairJointName = boneHashDict[chainCollision.pairJointNameHash].name
		else:
			if chainCollision.chainCollisionShape != 0:
				missingHashWarning = True
			pairJointName = "HASH_"+str(chainCollision.pairJointNameHash)
		#print(chainCollision)
		currentCollisionIndex = collisionIndex
		subName = "COL_"+str(currentCollisionIndex).zfill(2)
		while(checkNameUsage(subName,checkSubString=True)):
			currentCollisionIndex +=1
			subName = "COL_"+str(currentCollisionIndex).zfill(2)
		
		shape = enumItemDict[chainCollision.chainCollisionShape]
		translatedShape = chainShapeEnumTranslationDict.get(chainCollision.chainCollisionShape)
		
		if (shape == "SPHERE"):
			name = "COL_" +str(currentCollisionIndex).zfill(2)+ "_"+shape + " " + jointName
			#colSphereObj = createFakeEmptySphere(name, [("TYPE","RE_CHAIN_COLLISION_SINGLE")],headerObj,collisionCollection)
			colSphereObj = createCurveEmpty(name, [("TYPE","RE_CHAIN_COLLISION_SINGLE")],None,collisionCollection)
			#getChainCollision(chainCollision,colSphereObj)
			colSphereObj.re_chain_chaincollision.radius = chainCollision.collisionCapsuleStartRadius
			colSphereObj.re_chain_chaincollision.chainCollisionShape = translatedShape
			colSphereObj.re_chain_chaincollision.collisionOffset = (chainCollision.x1,chainCollision.y1,chainCollision.z1)
			colSphereObj.re_chain_chaincollision.endCollisionOffset = (chainCollision.x2,chainCollision.y2,chainCollision.z2)
			colSphereObj.rotation_mode = "QUATERNION" 
			#colSphereObj.rotation_quaternion = (chainCollision.rotOffsetW,chainCollision.rotOffsetX,chainCollision.rotOffsetY,chainCollision.rotOffsetZ)
			
			#colSphereObj.empty_display_type = "SPHERE"
			#colSphereObj.empty_display_size = 1.1
			constraint = colSphereObj.constraints.new(type = "CHILD_OF")
			constraint.target = armature
			constraint.subtarget = jointName
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
			colSphereObj.re_chain_chaincollision.clspBitFlag0 = chainCollision.unknBitFlag0
			colSphereObj.re_chain_chaincollision.clspBitFlag1 = chainCollision.unknBitFlag1
			#modifier["Input_0"] = colSphereObj
		elif shape == "CAPSULE" or shape == "TCAPSULE":#CAPSULE
			
			name = subName+ f"_{shape} - {jointName} > {pairJointName}" 
			colCapsuleRootObj = createCurveEmpty(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_ROOT")],None,collisionCollection)
			lockObjTransforms(colCapsuleRootObj)
			#colCapsuleRootObj.empty_display_size = .1
			#getChainCollision(chainCollision,colCapsuleRootObj)
			
			colCapsuleRootObj.re_chain_chaincollision.chainCollisionShape = translatedShape
			name = subName+ f"_{shape}_BEGIN" + " " +jointName
			colCapsuleStartObj = createFakeEmptySphere(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_START")],colCapsuleRootObj,collisionCollection)
			colCapsuleRootObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCollisionsThroughObjects
			if shape == "CAPSULE":
				colCapsuleRootObj.re_chain_chaincollision.radius = chainCollision.collisionSphereRadius
			else:
				colCapsuleRootObj.re_chain_chaincollision.radius = chainCollision.collisionCapsuleStartRadius
				colCapsuleRootObj.re_chain_chaincollision.endRadius = chainCollision.collisionCapsuleEndRadius
			#colCapsuleStartObj.re_chain_chaincollision.collisionOffset = (chainCollision.posX,chainCollision.posY,chainCollision.posZ)
			colCapsuleStartObj.rotation_mode = "QUATERNION" 
			#colCapsuleStartObj.rotation_quaternion = (chainCollision.rotOffsetW,chainCollision.rotOffsetX,chainCollision.rotOffsetY,chainCollision.rotOffsetZ)
			
			#colCapsuleStartObj.empty_display_type = "SPHERE"
			#colCapsuleStartObj.empty_display_size = 1.1
			constraint = colCapsuleStartObj.constraints.new(type = "CHILD_OF")
			constraint.target = armature
			constraint.subtarget = jointName
			constraint.name = "BoneName"
			
			constraint.use_scale_x = False
			constraint.use_scale_y = False
			constraint.use_scale_z = False
			#colCapsuleStartObj.show_name = True
			colCapsuleStartObj.show_name = bpy.context.scene.re_chain_toolpanel.showCollisionNames
			colCapsuleStartObj.show_in_front = bpy.context.scene.re_chain_toolpanel.drawCapsuleHandlesThroughObjects
			
			name = subName+ f"_{shape}_END" + " " + pairJointName
			colCapsuleEndObj = createFakeEmptySphere(name, [("TYPE","RE_CHAIN_COLLISION_CAPSULE_END")],colCapsuleRootObj,collisionCollection)
			#colCapsuleEndObj.re_chain_chaincollision.endCollisionOffset = (chainCollision.pairPosX,chainCollision.pairPosY,chainCollision.pairPosZ)
			#colCapsuleEndObj.empty_display_type = "SPHERE"
			#colCapsuleEndObj.empty_display_size = 1.1
			constraint = colCapsuleEndObj.constraints.new(type = "CHILD_OF")
			constraint.target = armature
			
			constraint.subtarget = pairJointName
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
			if (shape == "CAPSULE"):
				colCapsuleRootObj.re_chain_chaincollision.radius = chainCollision.collisionSphereRadius
			else:
				colCapsuleRootObj.re_chain_chaincollision.radius = colCapsuleRootObj.re_chain_chaincollision.radius
			colCapsuleRootObj.re_chain_chaincollision.endRadius = colCapsuleRootObj.re_chain_chaincollision.endRadius
			colCapsuleRootObj.re_chain_chaincollision.collisionOffset = (chainCollision.x1,chainCollision.y1,chainCollision.z1)
			colCapsuleRootObj.re_chain_chaincollision.endCollisionOffset = (chainCollision.x2,chainCollision.y2,chainCollision.z2)
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
				
			colCapsuleRootObj.re_chain_chaincollision.clspBitFlag0 = chainCollision.unknBitFlag0
			colCapsuleRootObj.re_chain_chaincollision.clspBitFlag1 = chainCollision.unknBitFlag1
		else:
			raiseWarning(f"Unsupported collision shape ({shape}) on collision {str(collisionIndex)}, skipping...")
	bpy.context.view_layer.update()
	alignCollisions()
	if missingHashWarning:
		showMessageBox("WARNING: Required bones are missing from the armature. See the console for details. Window > Toggle System Console")
		raiseWarning("The armature the CLSP was applied to does not have all of the required bones.\nSome collisions will not be attached correctly unless the necessary bones are present on the armature.\n\nConsider importing the base mesh (body_000_m.mesh if DD2) so that all collisions can be properly attached to bones.\nBe sure to set the Target Armature field to the base armature when importing the .clsp file.")
	return True
def clspErrorCheck(chainCollectionName):
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

		if obj.get("TYPE",None) == "RE_CHAIN_COLLISION_SINGLE":
			
			if obj.re_chain_chaincollision.chainCollisionShape == "2":#Capsule
				errorList.append(obj.name + " object collision shape is set to capsule, but is not a capsule. Create capsules by using the Create Collision From Bone button after selecting two bones")
			if obj.constraints.get("BoneName",False):
				if obj.constraints["BoneName"].target == "" or obj.constraints["BoneName"].target == None or obj.constraints["BoneName"].subtarget == "":
					errorList.append("Invalid child of constraint on " + obj.name)
			else:
				errorList.append("Child of constraint missing on " + obj.name)        
		
		elif obj.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_ROOT":
			
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
					
	if errorList == []:
		print("No problems found.")
		return True
	else:
		errorString = ""
		for error in errorList:
			errorString += textColors.FAIL +"ERROR: " + error + textColors.ENDC +"\n"
		showMessageBox("Chain structure contains errors and cannot export. Check Window > Toggle System Console for details.",title = "Export Error", icon = "ERROR")
		print(errorString)
		print(textColors.FAIL + "__________________________________\nChain export failed."+textColors.ENDC)
		return False

def fixTaperedCapsules(chainCollisionObjList,version):
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
					print(f"Start and end radius do not match on {chainCollisionObj.name}, changed to a tapered capsule")
					chainCollisionObj.re_chain_chaincollision.chainCollisionShape = "5"
					chainCollisionObj.name = chainCollisionObj.name.replace("_CAPSULE","_TCAPSULE")
					startCapsule.name = startCapsule.name.replace("_CAPSULE","_TCAPSULE")
					endCapsule.name = endCapsule.name.replace("_CAPSULE","_TCAPSULE")
				
def exportCLSPFile(filepath,options, version):
	valid = clspErrorCheck(options["targetCollection"])
	chainCollection = bpy.data.collections.get(options["targetCollection"],None)
	if valid and chainCollection != None:
		syncCollisionOffsets()
		print(textColors.OKCYAN + "__________________________________\nCLSP export started."+textColors.ENDC)
		newCLSPFile = CLSPFile()
		
		objList = chainCollection.all_objects
		
		chainCollisionObjList = []
		
		collisionTypes = [
			"RE_CHAIN_COLLISION_SINGLE",
			"RE_CHAIN_COLLISION_CAPSULE_ROOT",
			]
		
		for obj in objList:
			objType = obj.get("TYPE",None)
			if objType in collisionTypes:
				chainCollisionObjList.append(obj)
				
		chainCollisionObjList.sort(key = lambda item: item.name)
		
		#newCLSPFile.header.entryCount = len(chainCollisionObjList)
		
		
		#print(windSettingsObjList)
		#print(chainSettingsObjList)
		#print(chainGroupObjList)
		#print(chainCollisionObjList)
		
		
		fixTaperedCapsules(chainCollisionObjList,version)
		showWarningMessage = False
		for chainCollisionObj in chainCollisionObjList:
			
			translatedShapeType = chainShapeEnumTranslationDict.get(chainCollisionObj.re_chain_chaincollision.chainCollisionShape,-1)
			if translatedShapeType != -1:
				clspEntry = CLSPEntry()
				clspEntry.chainCollisionShape = translatedShapeType
				clspEntry.x1 = chainCollisionObj.re_chain_chaincollision.collisionOffset[0]
				clspEntry.y1 = chainCollisionObj.re_chain_chaincollision.collisionOffset[1]
				clspEntry.z1 = chainCollisionObj.re_chain_chaincollision.collisionOffset[2]
				clspEntry.x2 = chainCollisionObj.re_chain_chaincollision.endCollisionOffset[0]
				clspEntry.y2 = chainCollisionObj.re_chain_chaincollision.endCollisionOffset[1]
				clspEntry.z2 = chainCollisionObj.re_chain_chaincollision.endCollisionOffset[2]
				clspEntry.unknBitFlag0 = chainCollisionObj.re_chain_chaincollision.clspBitFlag0
				clspEntry.unknBitFlag1 = chainCollisionObj.re_chain_chaincollision.clspBitFlag1
				#Sphere
				if translatedShapeType == 0 and chainCollisionObj["TYPE"] == "RE_CHAIN_COLLISION_SINGLE":
					clspEntry.collisionCapsuleStartRadius = chainCollisionObj.re_chain_chaincollision.radius
					if "HASH_" in chainCollisionObj.constraints["BoneName"].subtarget:
						clspEntry.jointNameHash = int(chainCollisionObj.constraints["BoneName"].subtarget.split("HASH_")[1])
					else:
						clspEntry.jointNameHash = hash_wide(chainCollisionObj.constraints["BoneName"].subtarget)
					clspEntry.pairJointNameHash = 2180083513
				#Capsule/Tapered Capsule
				elif translatedShapeType == 1 or translatedShapeType == 3 and chainCollisionObj["TYPE"] == "RE_CHAIN_COLLISION_CAPSULE_ROOT":
					
					for child in chainCollisionObj.children: 
						if child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_START":
							startCapsule = child
						elif child.get("TYPE",None) == "RE_CHAIN_COLLISION_CAPSULE_END":
							endCapsule = child
					if "HASH_" in startCapsule.constraints["BoneName"].subtarget:
						clspEntry.jointNameHash = int(startCapsule.constraints["BoneName"].subtarget.split("HASH_")[1])
					else:
						clspEntry.jointNameHash = hash_wide(startCapsule.constraints["BoneName"].subtarget)
						
					if "HASH_" in startCapsule.constraints["BoneName"].subtarget:
						clspEntry.pairJointNameHash = int(endCapsule.constraints["BoneName"].subtarget.split("HASH_")[1])
					else:
						clspEntry.pairJointNameHash = hash_wide(endCapsule.constraints["BoneName"].subtarget)
						
					if translatedShapeType == 1:
						clspEntry.collisionSphereRadius = chainCollisionObj.re_chain_chaincollision.radius
					else:
						clspEntry.collisionCapsuleStartRadius = chainCollisionObj.re_chain_chaincollision.radius
						clspEntry.collisionCapsuleEndRadius = chainCollisionObj.re_chain_chaincollision.endRadius
				newCLSPFile.clspEntryList.append(clspEntry)
			else:
				showWarningMessage = True
				raiseWarning(f"Skipped {chainCollisionObj.name} because it contains an unsupported collision shape type for CLSP")
				
			
		newCLSPFile.header.entryCount = len(newCLSPFile.clspEntryList)
		print("Writing CLSP...")
		writeRECLSP(newCLSPFile, filepath)
		if showWarningMessage:
			showMessageBox("CLSP exported with warnings. Check the console for details. Window > Toggle System Console",title = "Export Warning", icon = "ERROR")
		return True
		#for newWindSetttings in newChainFile.WindSettingsList:
			#print(newWindSetttings)
		#for newChainSetttings in newChainFile.ChainSettingsList:
			#print(newChainSetttings)
		#for newChainGroup in newChainFile.ChainGroupList:
			#print(newChainGroup)
			#for newNode in newChainGroup.nodeList:
				#print(str(newNode)+"\n\n")