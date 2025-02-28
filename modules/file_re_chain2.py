#Author: NSA Cloud


from .gen_functions import textColors,raiseWarning,raiseError,getPaddingAmount,getPaddedPos,read_uint,read_int,read_uint64,read_int64,read_float,read_ushort,read_ubyte,read_unicode_string,read_byte,read_short,write_uint,write_int,write_uint64,write_int64,write_float,write_ushort,write_ubyte,write_unicode_string,write_byte,write_short

VERSION_DD2 = 4
VERSION_DR = 9
VERSION_MHWILDS = 12

supportedVersionSet = set([4,9,12])

#---CHAIN STRUCTS---#
class SIZE_DATA():
	def __init__(self,version):
		self.HEADER_SIZE = 112
		self.CHAIN_SETTING_SIZE = 136
		self.CHAIN_SETTING_SUBDATA_SIZE = 16
		self.CHAIN_GROUP_SIZE = 104
		self.CHAIN_SUBGROUP_SIZE = 16
		self.COLLISION_SIZE = 80
		self.COLLISION_SUBDATA_SIZE = 64
		self.NODE_SIZE = 96
		self.JIGGLE_SIZE = 72
		self.WIND_SIZE = 184
		self.CHAIN_LINK_SIZE = 32
		self.CHAIN_LINK_NODE_SIZE = 8
		
		if version >= VERSION_DR:
			self.CHAIN_SETTING_SIZE = 144
		
		if version >= VERSION_MHWILDS:
			self.HEADER_SIZE = 120
			self.CHAIN_SETTING_SIZE = 184
			self.CHAIN_LINK_SIZE = 40


class Chain2HeaderData():
	def __init__(self):
		self.version = 9
		self.magic = 846096483
		self.errFlags = 0#ENUM
		self.masterSize = 0
		self.collisionAttrAssetOffset = 0
		self.chainModelCollisionOffset = 0
		self.chainSubDataOffset = 0 #For internal use, does not exist in file
		self.chainSubDataCount = 0 #For internal use, does not exist in file
		self.extraDataOffset = 0
		self.chainGroupOffset = 0
		self.chainLinkOffset = 0
		self.chainFreeLinkOffset = 0
		self.chainSettingsOffset = 0
		self.chainWindSettingsOffset = 0
		self.chainGroupCount = 0
		self.chainSettingsCount = 0
		self.chainModelCollisionCount = 0
		self.chainWindSettingsCount = 0
		self.chainLinkCount = 0
		self.rotationOrder = 0#ENUM
		self.defaultSettingIdx = 0
		self.calculateMode = 1#ENUM
		self.chainAttrFlags = 0#ENUM
		self.parameterFlag = 0#ENUM
		self.calculateStepTime = 1.0
		self.modelCollisionSearch = 0#BOOL
		self.taperedCollideMethod = 0
		self.freeLinkCount = 0
		self.freeLinkJoint = 0
		self.collisionFilterHit0 = 0
		self.collisionFilterHit1 = 0
		self.collisionFilterHit2 = 0
		self.collisionFilterHit3 = 0
		self.collisionFilterHit4 = 0
		self.collisionFilterHit5 = 0
		self.collisionFilterHit6 = 0
		self.collisionFilterHit7 = 0
		self.wilds_unkn0 = 0#Struct count, free links probably
		self.highFPSCalculateMode = 1#ENUM, WILDS
		self.wilds_unkn1 = 0
		self.wilds_unkn2 = 0
		self.padding0 = 0
		self.padding1 = 0
		self.padding2 = 0
	def read(self,file):
		print("Reading Header...")
		self.version = read_uint(file)
		version = self.version
		
		self.magic = read_uint(file)
		if self.magic != 846096483:
			raise Exception("File is not a chain2 file.")
		print("Version", version)
		if version not in supportedVersionSet:
			raiseWarning("Unsupported chain version " + str(self.version) + ", file may not load correctly.")
		self.errFlags = read_uint(file)#ENUM
		self.masterSize = read_uint(file)
		self.collisionAttrAssetOffset = read_uint64(file)
		self.chainModelCollisionOffset = read_uint64(file)
		self.extraDataOffset = read_uint64(file)
		self.chainGroupOffset = read_uint64(file)
		self.chainLinkOffset = read_uint64(file)
		self.chainFreeLinkOffset = read_uint64(file)
		self.chainSettingsOffset = read_uint64(file)
		self.chainWindSettingsOffset = read_uint64(file)
		self.chainGroupCount = read_ubyte(file)
		self.chainSettingsCount = read_ubyte(file)
		self.chainModelCollisionCount = read_ubyte(file)
		self.chainWindSettingsCount = read_ubyte(file)
		self.chainLinkCount = read_ubyte(file)
		self.rotationOrder = read_ubyte(file)#ENUM
		self.defaultSettingIdx = read_ubyte(file)
		self.calculateMode = read_ubyte(file)#ENUM
		self.chainAttrFlags = read_uint(file)#ENUM
		self.parameterFlag = read_uint(file)#ENUM
		self.calculateStepTime = read_float(file)
		self.modelCollisionSearch = read_ubyte(file)#BOOL
		self.taperedCollideMethod = read_ubyte(file)
		self.freeLinkCount = read_ubyte(file)
		self.freeLinkJoint = read_ubyte(file)
		self.collisionFilterHit0 = read_ubyte(file)
		self.collisionFilterHit1 = read_ubyte(file)
		self.collisionFilterHit2 = read_ubyte(file)
		self.collisionFilterHit3 = read_ubyte(file)
		self.collisionFilterHit4 = read_ubyte(file)
		self.collisionFilterHit5 = read_ubyte(file)
		self.collisionFilterHit6 = read_ubyte(file)
		self.collisionFilterHit7 = read_ubyte(file)
		if version >= VERSION_MHWILDS:
			self.wilds_unkn0 = read_ushort(file)
			self.highFPSCalculateMode = read_ushort(file)
			self.wilds_unkn1 = read_ubyte(file)
			self.wilds_unkn2 = read_ubyte(file)
			self.padding0 = read_ushort(file)
			self.padding1 = read_uint(file)
			self.padding2 = read_uint(file)
		
	def write(self,file):
		version = self.version
		write_uint(file, self.version)
		write_uint(file, self.magic)
		write_uint(file, self.errFlags)#ENUM
		write_uint(file, self.masterSize)
		write_uint64(file, self.collisionAttrAssetOffset)
		write_uint64(file, self.chainModelCollisionOffset)
		write_uint64(file, self.extraDataOffset)
		write_uint64(file, self.chainGroupOffset)
		write_uint64(file, self.chainLinkOffset)
		write_uint64(file, self.chainFreeLinkOffset)
		write_uint64(file, self.chainSettingsOffset)
		write_uint64(file, self.chainWindSettingsOffset)
		write_ubyte(file, self.chainGroupCount)
		write_ubyte(file, self.chainSettingsCount)
		write_ubyte(file, self.chainModelCollisionCount)
		write_ubyte(file, self.chainWindSettingsCount)
		write_ubyte(file, self.chainLinkCount)
		write_ubyte(file, self.rotationOrder)#ENUM
		write_ubyte(file, self.defaultSettingIdx)
		write_ubyte(file, self.calculateMode)#ENUM
		write_uint(file, self.chainAttrFlags)#ENUM
		write_uint(file, self.parameterFlag)#ENUM
		write_float(file, self.calculateStepTime)
		write_ubyte(file, self.modelCollisionSearch)#BOOL
		write_ubyte(file, self.taperedCollideMethod)
		write_ubyte(file, self.freeLinkCount)
		write_ubyte(file, self.freeLinkJoint)
		write_ubyte(file, self.collisionFilterHit0)
		write_ubyte(file, self.collisionFilterHit1)
		write_ubyte(file, self.collisionFilterHit2)
		write_ubyte(file, self.collisionFilterHit3)
		write_ubyte(file, self.collisionFilterHit4)
		write_ubyte(file, self.collisionFilterHit5)
		write_ubyte(file, self.collisionFilterHit6)
		write_ubyte(file, self.collisionFilterHit7)
		if version >= VERSION_MHWILDS:
			write_ushort(file, self.wilds_unkn0)
			write_ushort(file, self.highFPSCalculateMode)
			write_ubyte(file, self.wilds_unkn1)
			write_ubyte(file, self.wilds_unkn2)
			write_ushort(file, self.padding0)
			write_uint(file, self.padding1)
			write_uint(file, self.padding2)
			
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Chain2SettingsSubData():
	def __init__(self):
		self.unkn0 = 0
		self.unkn1A = 0
		self.unkn1B = 0
		self.unkn1C = 0
		self.unkn1D = 0
		self.unkn2 = 0
		self.unkn3 = 0
		
	def read(self,file):
		self.unkn0 = read_int(file)
		self.unkn1A = read_ubyte(file)
		self.unkn1B = read_ubyte(file)
		self.unkn1C = read_ubyte(file)
		self.unkn1D = read_ubyte(file)
		self.unkn2 = read_int(file)
		self.unkn3 = read_int(file)
		
	def write(self,file):
		write_uint(file, self.unkn0)
		write_ubyte(file, self.unkn1A)
		write_ubyte(file, self.unkn1B)
		write_ubyte(file, self.unkn1C)
		write_ubyte(file, self.unkn1D)
		write_uint(file, self.unkn2)
		write_uint(file, self.unkn3)
		
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Chain2SettingsData():
	def __init__(self):
		self.colliderFilterInfoPathOffset = 0
		self.colliderFilterInfoPath = ""
		self.id = 0
		self.settingsAttrFlags = 0 #ENUM
		self.springCalcType = 0
		self.windID = 0
		self.windDelayType = 0
		self.gravityX = 0.0
		self.gravityY = -9.8
		self.gravityZ = 0.0
		self.springMaxVelocity = 0.0
		self.damping = 0.2
		self.secondDamping = 0.05
		self.secondDampingSpeed = 0.0
		self.minDamping = 0.2
		self.secondMinDamping = 0.05
		self.dampingPow = 1.0
		self.secondDampingPow = 1.0
		self.collideMaxVelocity = 0.0
		self.springForce = 0.0
		self.springLimitRate = 0.0
		self.reduceSelfDistanceRate = 0.0
		self.secondReduceDistanceRate = 0.0
		self.secondReduceDistanceSpeed = 0.0
		self.friction = 0.0
		self.shockAbsorptionRate = 0.0
		self.coefOfElasticity = 0.0
		self.coefOfExternalForces = 0.0
		self.stretchInteractionRatio = 0.5
		self.angleLimitInteractionRatio = 0.5
		self.motionForce = 0.0
		self.groupDefaultAttr = 0#ENUM
		self.windEffectCoef = 0.0
		self.velocityLimit = 0.0
		self.hardness = 0.0
		self.windDelaySpeed = 0.0
		self.envWindEffectCoef = 1.0
		
		#DR
		self.motionForceCalcType = 0#Sometimes 1, Dead Rising npc57_Chain2
		self.padding = 0
		
		#MH Wilds
		#Not present on versions below 12
		self.subDataCount = 0
		
		#Quaternion probably
		self.subDataUnkn0 = 0.0#Always 0.0
		self.subDataUnkn1 = 0.0#Always 0.0
		self.subDataUnkn2 = 0.0#Always 0.0
		self.subDataUnkn3 = 1.0#Always 1.0
		#Pos probably
		self.subDataUnkn4 = 0.0#Always 0.0
		self.subDataUnkn5 = 0.0#Always 0.0
		self.subDataUnkn6 = 0.0#Always 0.0
		self.subDataOffset = 0
		self.subDataList = []
	def read(self,file,version):
		#print(file.tell())
		self.colliderFilterInfoPathOffset = read_uint64(file)
		if self.colliderFilterInfoPathOffset != 0:
			currentPos = file.tell()
			file.seek(self.colliderFilterInfoPathOffset)
			self.colliderFilterInfoPath = read_unicode_string(file)
			file.seek(currentPos)
		self.id = read_uint(file)	
		self.settingsAttrFlags = read_ubyte(file) #ENUM
		self.springCalcType = read_ubyte(file)
		self.windID = read_byte(file)
		self.windDelayType = read_ubyte(file)
		self.gravityX = read_float(file)
		self.gravityY = read_float(file)
		self.gravityZ = read_float(file)
		self.springMaxVelocity = read_float(file)
		self.damping = read_float(file)
		self.secondDamping = read_float(file)
		self.secondDampingSpeed = read_float(file)
		self.minDamping = read_float(file)
		self.secondMinDamping = read_float(file)
		self.dampingPow = read_float(file)
		self.secondDampingPow = read_float(file)
		self.collideMaxVelocity = read_float(file)
		self.springForce = read_float(file)
		self.springLimitRate = read_float(file)
		self.reduceSelfDistanceRate = read_float(file)
		self.secondReduceDistanceRate = read_float(file)
		self.secondReduceDistanceSpeed = read_float(file)
		self.friction = read_float(file)
		self.shockAbsorptionRate = read_float(file)
		self.coefOfElasticity = read_float(file)
		self.coefOfExternalForces = read_float(file)
		self.stretchInteractionRatio = read_float(file)
		self.angleLimitInteractionRatio = read_float(file)
		self.motionForce = read_float(file)
		self.groupDefaultAttr = read_uint(file)
		self.windEffectCoef = read_float(file)
		self.velocityLimit = read_float(file)
		self.hardness = read_float(file)
		self.windDelaySpeed = read_float(file)#VERSION 48
		self.envWindEffectCoef = read_float(file)#VERSION 48
		if version >= VERSION_MHWILDS:
			self.subDataCount = read_uint(file)
			self.subDataUnkn0 = read_float(file)
			self.subDataUnkn1 = read_float(file)
			self.subDataUnkn2 = read_float(file)
			self.subDataUnkn3 = read_float(file)
			self.subDataUnkn4 = read_float(file)
			self.subDataUnkn5 = read_float(file)
			self.subDataUnkn6 = read_float(file)
			self.subDataOffset = read_uint64(file)
			currentPos2 = file.tell()
			file.seek(self.subDataOffset)
			for i in range(0,self.subDataCount):
				entry = Chain2SettingsSubData()
				entry.read(file)
				self.subDataList.append(entry)
			file.seek(currentPos2)
		if version >= VERSION_DR:
			self.motionForceCalcType = read_uint(file)
			self.padding = read_uint(file)
			
		
	def write(self,file,version):#TODO Fix wilds write
		write_uint64(file, self.colliderFilterInfoPathOffset)
		write_uint(file, self.id)
		write_ubyte(file, self.settingsAttrFlags) #ENUM
		write_ubyte(file, self.springCalcType)
		write_byte(file, self.windID)
		write_ubyte(file, self.windDelayType)
		write_float(file, self.gravityX)
		write_float(file, self.gravityY)
		write_float(file, self.gravityZ)
		write_float(file, self.springMaxVelocity)
		write_float(file, self.damping)
		write_float(file, self.secondDamping)
		write_float(file, self.secondDampingSpeed)
		write_float(file, self.minDamping)
		write_float(file, self.secondMinDamping)
		write_float(file, self.dampingPow)
		write_float(file, self.secondDampingPow)
		write_float(file, self.collideMaxVelocity)
		write_float(file, self.springForce)
		write_float(file, self.springLimitRate)
		write_float(file, self.reduceSelfDistanceRate)
		write_float(file, self.secondReduceDistanceRate)
		write_float(file, self.secondReduceDistanceSpeed)
		write_float(file, self.friction)
		write_float(file, self.shockAbsorptionRate)
		write_float(file, self.coefOfElasticity)
		write_float(file, self.coefOfExternalForces)
		write_float(file, self.stretchInteractionRatio)
		write_float(file, self.angleLimitInteractionRatio)
		write_float(file, self.motionForce)
		write_uint(file, self.groupDefaultAttr)
		write_float(file, self.windEffectCoef)
		write_float(file, self.velocityLimit)
		write_float(file, self.hardness)
		write_float(file, self.windDelaySpeed)
		write_float(file, self.envWindEffectCoef)
		if version >= VERSION_MHWILDS:
			write_uint(file, self.subDataCount)
			write_float(file, self.subDataUnkn0)
			write_float(file, self.subDataUnkn1)
			write_float(file, self.subDataUnkn2)
			write_float(file, self.subDataUnkn3)
			write_float(file, self.subDataUnkn4)
			write_float(file, self.subDataUnkn5)
			write_float(file, self.subDataUnkn6)
			write_uint64(file, self.subDataOffset)
		if version >= VERSION_DR:
			write_uint(file, self.motionForceCalcType)
			write_uint(file, self.padding)
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class CollisionSubData():
	def __init__(self):
		self.posX = 0.0
		self.posY = 0.0
		self.posZ = 0.0
		self.pairPosX = 0.0
		self.pairPosY = 0.0
		self.pairPosZ = 0.0
		self.rotOffsetX = 0.0
		self.rotOffsetY = 0.0
		self.rotOffsetZ = 0.0
		self.rotOffsetW = 1.0
		self.radius = 0.12
		self.id = 0
		self.unknSubCollisionData0 = 0
		self.unknSubCollisionData1 = 0
		self.unknSubCollisionData2 = 0
		self.unknSubCollisionData3 = 0
		
	def read(self,file):
		self.posX = read_float(file)
		self.posY = read_float(file)
		self.posZ = read_float(file)
		self.pairPosX = read_float(file)
		self.pairPosY = read_float(file)
		self.pairPosZ = read_float(file)
		

		self.rotOffsetX = read_float(file)
		self.rotOffsetY = read_float(file)
		self.rotOffsetZ = read_float(file)
		self.rotOffsetW = read_float(file)
		
		self.radius = read_float(file)
		self.id = read_int(file)
		self.unknSubCollisionData0 = read_int(file)#MURMUR HASH
		self.unknSubCollisionData1 = read_int(file)
		self.unknSubCollisionData2 = read_int(file)
		self.unknSubCollisionData3 = read_int(file)
		
	def write(self,file):
		write_float(file, self.posX)
		write_float(file, self.posY)
		write_float(file, self.posZ)
		write_float(file, self.pairPosX)
		write_float(file, self.pairPosY)
		write_float(file, self.pairPosZ)
		
		#if version >= 35:
		write_float(file, self.rotOffsetX)
		write_float(file, self.rotOffsetY)
		write_float(file, self.rotOffsetZ)
		write_float(file, self.rotOffsetW)
		
		write_float(file, self.radius)
		write_int(file, self.id)
		write_int(file, self.unknSubCollisionData0)
		write_int(file, self.unknSubCollisionData1)
		write_int(file, self.unknSubCollisionData2)
		write_int(file, self.unknSubCollisionData3)
		
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)


class Chain2CollisionData():
	def __init__(self):
		self.subDataOffset = 0
		self.posX = 0.0
		self.posY = 0.0
		self.posZ = 0.0
		self.pairPosX = 0.0
		self.pairPosY = 0.0
		self.pairPosZ = 0.0
		self.rotOffsetX = 0.0
		self.rotOffsetY = 0.0
		self.rotOffsetZ = 0.0
		self.rotOffsetW = 0.0
		self.rotationOrder = 0#VERSION 48
		self.jointNameHash = 0#MURMUR HASH
		self.pairJointNameHash = 0#MURMUR HASH
		self.radius = 0.08
		self.endRadius = 0.1#VERSION 46
		self.lerp = 0.0
		self.chainCollisionShape = 1#ENUM, sphere by default
		self.div = 0
		self.subDataCount = 0
		self.collisionFilterFlags = -1
		#self.subDataFlag = 0
		self.padding = -1
		self.subData = CollisionSubData()
		
		
	def read(self,file):
		self.subDataOffset = read_uint64(file)
		self.posX = read_float(file)
		self.posY = read_float(file)
		self.posZ = read_float(file)
		self.pairPosX = read_float(file)
		self.pairPosY = read_float(file)
		self.pairPosZ = read_float(file)
		
		self.rotOffsetX = read_float(file)
		self.rotOffsetY = read_float(file)
		self.rotOffsetZ = read_float(file)
		self.rotOffsetW = read_float(file)
		self.rotationOrder = read_uint(file)#VERSION 39
		
		self.jointNameHash = read_uint(file)#MURMUR HASH
		self.pairJointNameHash = read_uint(file)#MURMUR HASH
		self.radius = read_float(file)
		self.endRadius = read_float(file)
		
		self.lerp = read_float(file)#VERSION 48
		
		self.chainCollisionShape = read_ubyte(file)#ENUM, sphere by default
		self.div = read_ubyte(file)
		self.subDataCount = read_ushort(file)
		self.collisionFilterFlags = read_int(file)
		#self.subDataFlag = read_short(file)
		
		if self.subDataCount > 0:
			currentPos = file.tell()
			file.seek(self.subDataOffset)
			self.subData.read(file)
			file.seek(currentPos)
		
	def write(self,file):
		write_uint64(file, self.subDataOffset)
		write_float(file, self.posX)
		write_float(file, self.posY)
		write_float(file, self.posZ)
		write_float(file, self.pairPosX)
		write_float(file, self.pairPosY)
		write_float(file, self.pairPosZ)
		
		write_float(file, self.rotOffsetX)
		write_float(file, self.rotOffsetY)
		write_float(file, self.rotOffsetZ)
		write_float(file, self.rotOffsetW)
		write_uint(file, self.rotationOrder)#VERSION 39

		write_uint(file, self.jointNameHash)#MURMUR HASH
		write_uint(file, self.pairJointNameHash)#MURMUR HASH
		write_float(file, self.radius)
		write_float(file, self.endRadius)
		write_float(file,self.lerp)#VERSION 48

		write_ubyte(file, self.chainCollisionShape)#ENUM, sphere by default
		write_ubyte(file, self.div)
		write_ushort(file, self.subDataCount)
		write_int(file, self.collisionFilterFlags)
		#write_short(file, self.subDataFlag)
		
		#Write subdata later
			
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)



class Chain2JiggleData():
	def __init__(self):
		self.rangeX = 0.0#Vec3
		self.rangeY = 0.0
		self.rangeZ = 0.0
		self.padding0 = 0
		self.rangeOffsetX = 0.0#Vec3
		self.rangeOffsetY = 0.0
		self.rangeOffsetZ = 0.0
		self.padding1 = 0
		self.rangeAxisX = 0.0#Quaternion
		self.rangeAxisY = 0.0
		self.rangeAxisZ = 0.0
		self.rangeAxisW = 1.0
		self.rangeShape = 2
		self.attrFlags = 0
		self.springForce = 0.04
		self.gravityCoef = 1.0
		self.damping = 0.04
		self.windCoef = 0

	def read(self,file,version):
		self.rangeX = read_float(file)#Vec3
		self.rangeY = read_float(file)
		self.rangeZ = read_float(file)
		self.padding0 = read_float(file)
		self.rangeOffsetX = read_float(file)#Vec3
		self.rangeOffsetY = read_float(file)
		self.rangeOffsetZ = read_float(file)
		self.padding1 = read_float(file)
		self.rangeAxisX = read_float(file)#Quaternion
		self.rangeAxisY = read_float(file)
		self.rangeAxisZ = read_float(file)
		self.rangeAxisW = read_float(file)
		self.rangeShape = read_uint(file)
		self.attrFlags = read_uint(file)
		self.springForce = read_float(file)
		self.gravityCoef = read_float(file)
		self.damping = read_float(file)
		self.windCoef = read_float(file)

	def write(self,file,version):
		write_float(file, self.rangeX)#Vec3
		write_float(file, self.rangeY)
		write_float(file, self.rangeZ)
		write_float(file, self.padding0)
		write_float(file, self.rangeOffsetX)#Vec3
		write_float(file, self.rangeOffsetY)
		write_float(file, self.rangeOffsetZ)
		write_float(file, self.padding1)
		write_float(file, self.rangeAxisX)#Quaternion
		write_float(file, self.rangeAxisY)
		write_float(file, self.rangeAxisZ)
		write_float(file, self.rangeAxisW)
		write_uint(file, self.rangeShape)
		write_uint(file, self.attrFlags)
		write_float(file, self.springForce)
		write_float(file, self.gravityCoef)
		write_float(file, self.damping)	
		write_float(file, self.windCoef)

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Chain2NodeData():
	def __init__(self):
		self.angleLimitDirectionX = 0.0#Quaternion
		self.angleLimitDirectionY = 0.0
		self.angleLimitDirectionZ = 0.0
		self.angleLimitDirectionW = 0.0
		self.angleLimitRad = 0.0
		self.angleLimitDistance = 0.0
		self.angleLimitRestitution = 0.0
		self.angleLimitRestituteStopSpeed = 0.1
		self.collisionRadius = 0.03
		self.collisionFilterFlags = -1#ENUM
		self.capsuleStretchRate0 = 1.0
		self.capsuleStretchRate1 = 1.0
		self.attrFlags = 0
		self.constraintJntNameHash = 0#MURMUR HASH
		self.windCoef = 1.0
		self.angleMode = 1#ENUM
		self.collisionShape = 1 #ENUM sphere by default
		self.attachType = 0
		self.rotationType = 0
		self.jiggleDataOffset = 0
		self.gravityCoef = 1.0#VERSION 48
		self.jointHash = 2180083513#Hash is of something that means None
		self.basePos = (0.0,0.0,0.0)
		self.padding = 0#VERSION 48
		self.jiggleData = None
	def read(self,file,version):
		self.angleLimitDirectionX = read_float(file)#Quaternion
		self.angleLimitDirectionY = read_float(file)
		self.angleLimitDirectionZ = read_float(file)
		self.angleLimitDirectionW = read_float(file)
		self.angleLimitRad = read_float(file)
		self.angleLimitDistance = read_float(file)
		self.angleLimitRestitution = read_float(file)
		self.angleLimitRestituteStopSpeed = read_float(file)
		self.collisionRadius = read_float(file)
		self.collisionFilterFlags = read_int(file)#ENUM
		self.capsuleStretchRate0 = read_float(file)
		self.capsuleStretchRate1 = read_float(file)
		self.attrFlags = read_uint(file)
		self.constraintJntNameHash = read_uint(file)#MURMUR HASH
		self.windCoef = read_float(file)
		self.angleMode = read_ubyte(file)#ENUM
		self.collisionShape = read_ubyte(file) #ENUM sphere by default
		self.attachType = read_ubyte(file)
		self.rotationType = read_ubyte(file)
		self.jiggleDataOffset = read_uint64(file)
		self.gravityCoef = read_float(file)#VERSION 48
		self.jointHash = read_uint(file)
		self.basePos = (read_float(file),read_float(file),read_float(file))
		self.padding = read_uint(file)#VERSION 48
		if self.jiggleDataOffset != 0:
			currentPos = file.tell()
			self.jiggleData = Chain2JiggleData()
			file.seek(self.jiggleDataOffset)
			self.jiggleData.read(file,version)
			file.seek(currentPos)
		
		file.seek(file.tell()+getPaddingAmount(file.tell(),16))#Skip padding
	def write(self,file,version):
		write_float(file, self.angleLimitDirectionX)#Quaternion
		write_float(file, self.angleLimitDirectionY)
		write_float(file, self.angleLimitDirectionZ)
		write_float(file, self.angleLimitDirectionW)
		write_float(file, self.angleLimitRad)
		write_float(file, self.angleLimitDistance)
		write_float(file, self.angleLimitRestitution)
		write_float(file, self.angleLimitRestituteStopSpeed)
		write_float(file, self.collisionRadius)
		write_int(file, self.collisionFilterFlags)#ENUM
		write_float(file, self.capsuleStretchRate0)
		write_float(file, self.capsuleStretchRate1)
		write_uint(file, self.attrFlags)
		write_uint(file, self.constraintJntNameHash)#MURMUR HASH
		write_float(file, self.windCoef)
		write_ubyte(file, self.angleMode)#ENUM
		write_ubyte(file, self.collisionShape) #ENUM sphere by default
		write_ubyte(file, self.attachType)
		write_ubyte(file, self.rotationType)
		write_uint64(file, self.jiggleDataOffset)
		write_float(file, self.gravityCoef)#VERSION 48
		write_uint(file,self.jointHash)
		for val in self.basePos:
			write_float(file,val)
		write_float(file, self.padding)#VERSION 48
		file.write(b"\x00"*getPaddingAmount(file.tell(), 16))

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Chain2SubGroupData():
	def __init__(self):
		self.nodeOffset = 0
		self.subGroupID = 0
		self.settingID = 0
		self.nodeList = []
		
	def read(self,file,version,nodeCount):
		self.nodeOffset = read_uint64(file)
		self.subGroupID = read_int(file)
		self.settingID = read_int(file)
		currentPos = file.tell()
		file.seek(self.nodeOffset)
		for i in range(0,nodeCount):
			newChainNode = Chain2NodeData()
			newChainNode.read(file,version)
			self.nodeList.append(newChainNode)
		file.seek(currentPos)
	def write(self,file,version):
		write_uint64(file, self.nodeOffset)
		write_int(file, self.subGroupID)
		write_int(file, self.settingID)

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Chain2GroupData():
	def __init__(self):
		self.terminateNodeName = ""#Not included in chain2
		self.nodeOffset = 0
		self.settingID = 0
		self.nodeCount = 0
		self.rotationOrder = 0#ENUM
		self.autoBlendCheckNodeNo = 0
		self.windID = 0
		self.tag0 = 0
		self.tag1 = 0
		self.tag2 = 0
		self.tag3 = 0
		self.hierarchyHash0 = 0
		self.hierarchyHash1 = 0
		self.hierarchyHash2 = 0
		self.hierarchyHash3 = 0
		self.dampingNoise0 = 0.0
		self.dampingNoise1 = 0.0
		self.endRotConstMax = 12.5
		self.tagCount = 0
		self.angleLimitDirectionMode = 0
		self.subGroupCount = 0
		self.colliderQualityLevel = 0
		
		self.attrFlags = 99339#ENUM
		self.clspFlags0 = -1#VERSION 52
		self.clspFlags1 = -1#VERSION 52
		self.subGroupDataOffset = 0#VERSION 48

		self.terminateNodeNameHash = 0#MURMUR HASH
		self.interpCount = 0
		self.nodeInterpolationMode = 3
		self.padding = 0
		
		
		self.nodeList = []
		self.subGroupList = []
		
	def read(self,file,version):
		self.nodeOffset = read_uint64(file)
		self.settingID = read_int(file)
		self.nodeCount = read_ubyte(file)
		self.rotationOrder = read_ubyte(file)
		self.autoBlendCheckNodeNo = read_ubyte(file)
		self.windID = read_byte(file)
		self.tag0 = read_int(file)
		self.tag1 = read_int(file)
		self.tag2 = read_int(file)
		self.tag3 = read_int(file)
		self.hierarchyHash0 = read_int(file)
		self.hierarchyHash1 = read_int(file)
		self.hierarchyHash2 = read_int(file)
		self.hierarchyHash3 = read_int(file)
		self.dampingNoise0 = read_float(file)
		self.dampingNoise1 = read_float(file)
		self.endRotConstMax = read_float(file)
		self.tagCount = read_ubyte(file)
		self.angleLimitDirectionMode = read_ubyte(file)
		self.subGroupCount = read_ushort(file)
		self.colliderQualityLevel = read_uint(file)
		
		self.attrFlags = read_int(file)
		self.clspFlags0 = read_int(file)
		self.clspFlags1 = read_int(file)
		self.subGroupDataOffset = read_uint64(file)

		self.terminateNodeNameHash = read_uint(file)
		self.interpCount = read_uint(file)
		self.nodeInterpolationMode = read_uint(file)
		self.padding = read_uint(file)
		self.nodeList = []
		currentPos = file.tell()
		file.seek(self.nodeOffset)
		for i in range(0,self.nodeCount):
			newChainNode = Chain2NodeData()
			newChainNode.read(file,version)
			self.nodeList.append(newChainNode)
		file.seek(self.subGroupDataOffset)
		self.subGroupList = []
		for i in range(0,self.subGroupCount):
			entry = Chain2SubGroupData()
			entry.read(file,version,self.nodeCount)
			self.subGroupList.append(entry)
		file.seek(currentPos)
		
		
	def write(self,file,version):
		write_uint64(file, self.nodeOffset)
		write_int(file, self.settingID)
		write_ubyte(file, self.nodeCount)
		write_ubyte(file, self.rotationOrder)
		write_ubyte(file, self.autoBlendCheckNodeNo)
		write_byte(file, self.windID)
		write_int(file, self.tag0)
		write_int(file, self.tag1)
		write_int(file, self.tag2)
		write_int(file, self.tag3)
		write_int(file, self.hierarchyHash0)
		write_int(file, self.hierarchyHash1)
		write_int(file, self.hierarchyHash2)
		write_int(file, self.hierarchyHash3)
		write_float(file, self.dampingNoise0)
		write_float(file, self.dampingNoise1)
		write_float(file, self.endRotConstMax)
		write_ubyte(file, self.tagCount)
		write_ubyte(file, self.angleLimitDirectionMode)
		write_ushort(file, self.subGroupCount)
		write_uint(file, self.colliderQualityLevel)
		write_int(file, self.attrFlags)
		write_int(file, self.clspFlags0)
		write_int(file, self.clspFlags1)
		write_uint64(file, self.subGroupDataOffset)
		write_uint(file, self.terminateNodeNameHash)
		write_uint(file, self.interpCount)
		write_uint(file, self.nodeInterpolationMode)
		write_uint(file, self.padding)
		

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Chain2WindSettingsData():
	def __init__(self):
		self.id = 0
		self.windDirection = 1#ENUM
		self.windCount = 1
		self.windType = 3#ENUM
		self.randomDamping = 0.5
		self.randomDampingCycle = 3.0
		self.randomCycleScaling = 1.0
		self.null = 0
		self.dir0X = 0.9284768
		self.dir0Y = 0.0
		self.dir0Z = 0.3713907
		self.dir1X = 0.0
		self.dir1Y = 0.0
		self.dir1Z = 1.0
		self.dir2X = 0.0
		self.dir2Y = 0.0
		self.dir2Z = 1.0
		self.dir3X = 0.0
		self.dir3Y = 0.0
		self.dir3Z = 1.0
		self.dir4X = 0.0
		self.dir4Y = 0.0
		self.dir4Z = 1.0
		self.min0 = 0.2
		self.min1 = 0.0
		self.min2 = 0.0
		self.min3 = 0.0
		self.min4 = 0.0
		self.max0 = 1.0
		self.max1 = 1.0
		self.max2 = 1.0
		self.max3 = 1.0
		self.max4 = 1.0
		self.phaseShift0 = 0.0
		self.phaseShift1 = 0.0
		self.phaseShift2 = 0.0
		self.phaseShift3 = 0.0
		self.phaseShift4 = 0.0
		self.cycle0 = 240.0
		self.cycle1 = 60.0
		self.cycle2 = 60.0
		self.cycle3 = 60.0
		self.cycle4 = 60.0
		self.interval0 = 30.0
		self.interval1 = 0.0
		self.interval2 = 0.0
		self.interval3 = 0.0
		self.interval4 = 0.0
	def read(self,file):
		self.id = read_uint(file)
		self.windDirection = read_ubyte(file)#ENUM
		self.windCount = read_ubyte(file)
		self.windType = read_ushort(file)#ENUM
		self.randomDamping = read_float(file)
		self.randomDampingCycle = read_float(file)
		self.randomCycleScaling = read_float(file)
		self.null = read_float(file)
		self.dir0X = read_float(file)
		self.dir0Y = read_float(file)
		self.dir0Z = read_float(file)
		self.dir1X = read_float(file)
		self.dir1Y = read_float(file)
		self.dir1Z = read_float(file)
		self.dir2X = read_float(file)
		self.dir2Y = read_float(file)
		self.dir2Z = read_float(file)
		self.dir3X = read_float(file)
		self.dir3Y = read_float(file)
		self.dir3Z = read_float(file)
		self.dir4X = read_float(file)
		self.dir4Y = read_float(file)
		self.dir4Z = read_float(file)
		self.min0 = read_float(file)
		self.min1 = read_float(file)
		self.min2 = read_float(file)
		self.min3 = read_float(file)
		self.min4 = read_float(file)
		self.max0 = read_float(file)
		self.max1 = read_float(file)
		self.max2 = read_float(file)
		self.max3 = read_float(file)
		self.max4 = read_float(file)
		self.phaseShift0 = read_float(file)
		self.phaseShift1 = read_float(file)
		self.phaseShift2 = read_float(file)
		self.phaseShift3 = read_float(file)
		self.phaseShift4 = read_float(file)
		self.cycle0 = read_float(file)
		self.cycle1 = read_float(file)
		self.cycle2 = read_float(file)
		self.cycle3 = read_float(file)
		self.cycle4 = read_float(file)
		self.interval0 = read_float(file)
		self.interval1 = read_float(file)
		self.interval2 = read_float(file)
		self.interval3 = read_float(file)
		self.interval4 = read_float(file)
		#file.seek(file.tell()+getPaddingAmount(file.tell(),16))#Skip padding
	def write(self,file):
		write_uint(file, self.id)
		write_ubyte(file, self.windDirection)#ENUM
		write_ubyte(file, self.windCount)
		write_ushort(file, self.windType)#ENUM
		write_float(file, self.randomDamping)
		write_float(file, self.randomDampingCycle)
		write_float(file, self.randomCycleScaling)
		write_float(file, self.null)
		write_float(file, self.dir0X)
		write_float(file, self.dir0Y)
		write_float(file, self.dir0Z)
		write_float(file, self.dir1X)
		write_float(file, self.dir1Y)
		write_float(file, self.dir1Z)
		write_float(file, self.dir2X)
		write_float(file, self.dir2Y)
		write_float(file, self.dir2Z)
		write_float(file, self.dir3X)
		write_float(file, self.dir3Y)
		write_float(file, self.dir3Z)
		write_float(file, self.dir4X)
		write_float(file, self.dir4Y)
		write_float(file, self.dir4Z)
		write_float(file, self.min0)
		write_float(file, self.min1)
		write_float(file, self.min2)
		write_float(file, self.min3)
		write_float(file, self.min4)
		write_float(file, self.max0)
		write_float(file, self.max1)
		write_float(file, self.max2)
		write_float(file, self.max3)
		write_float(file, self.max4)
		write_float(file, self.phaseShift0)
		write_float(file, self.phaseShift1)
		write_float(file, self.phaseShift2)
		write_float(file, self.phaseShift3)
		write_float(file, self.phaseShift4)
		write_float(file, self.cycle0)
		write_float(file, self.cycle1)
		write_float(file, self.cycle2)
		write_float(file, self.cycle3)
		write_float(file, self.cycle4)
		write_float(file, self.interval0)
		write_float(file, self.interval1)
		write_float(file, self.interval2)
		write_float(file, self.interval3)
		write_float(file, self.interval4)
		#file.seek(file.tell()+getPaddingAmount(file.tell(),16))#Skip padding

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Chain2LinkNode():
	def __init__(self):
		self.collisionRadius = 0.01
		self.collisionFilterFlags = 4
		
	def read(self,file):
		self.collisionRadius = read_float(file)
		self.collisionFilterFlags = read_int(file)
		
	def write(self,file):
		write_float(file, self.collisionRadius)
		write_int(file, self.collisionFilterFlags)

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Chain2LinkData():
	def __init__(self):
		self.nodeOffset = 0
		self.terminateNodeNameHashA = 0#MURMUR HASH
		self.terminateNodeNameHashB = 0#MURMUR HASH
		self.distanceShrinkLimitCoef = 0.5
		self.distanceExpandLimitCoef = 1.0
		self.linkMode = 0#ENUM
		self.connectFlags = 1#ENUM
		self.linkAttrFlags = 1#ENUM
		self.nodeCount = 0
		self.skipGroupA = 0
		self.skipGroupB = 0
		self.linkOrder = 0#ENUM
		self.nodeColLinkList = []
		#wilds
		self.clspFlags0 = -1
		self.clspFlags1 = -1
		
	def read(self,file,version):
		self.nodeOffset = read_uint64(file)
		self.terminateNodeNameHashA = read_uint(file)#MURMUR HASH
		self.terminateNodeNameHashB = read_uint(file)#MURMUR HASH
		self.distanceShrinkLimitCoef = read_float(file)
		self.distanceExpandLimitCoef = read_float(file)
		if version >= VERSION_MHWILDS:
			self.clspFlags0 = read_int(file)
			self.clspFlags1 = read_int(file)
		self.linkMode = read_ubyte(file)#ENUM
		self.connectFlags = read_ubyte(file)#ENUM
		self.linkAttrFlags = read_ushort(file)#ENUM
		self.nodeCount = read_ubyte(file)
		self.skipGroupA = read_ubyte(file)
		self.skipGroupB = read_ubyte(file)
		self.linkOrder = read_ubyte(file)#ENUM
		if self.nodeOffset and self.nodeCount != 0:
			startPos = file.tell()
			file.seek(self.nodeOffset)
			for i in range(0,self.nodeCount):
				linkNodeEntry = Chain2LinkNode()
				linkNodeEntry.read(file)
				self.nodeColLinkList.append(linkNodeEntry)
			file.seek(startPos)
		
	def write(self,file,version):
		write_uint64(file, self.nodeOffset)
		write_uint(file, self.terminateNodeNameHashA)#MURMUR HASH
		write_uint(file, self.terminateNodeNameHashB)#MURMUR HASH
		write_float(file, self.distanceShrinkLimitCoef)
		write_float(file, self.distanceExpandLimitCoef)
		if version >= VERSION_MHWILDS:
			write_int(file, self.clspFlags0)
			write_int(file, self.clspFlags1)
		write_ubyte(file, self.linkMode)#ENUM
		write_ubyte(file, self.connectFlags)#ENUM
		write_ushort(file, self.linkAttrFlags)#ENUM
		write_ubyte(file, self.nodeCount)
		write_ubyte(file, self.skipGroupA)
		write_ubyte(file, self.skipGroupB)
		write_ubyte(file, self.linkOrder)#ENUM

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Chain2File():
	def __init__(self):
		self.Header = Chain2HeaderData()

		self.ChainSettingsList = []
		self.ChainCollisionList = []
		self.ChainGroupList = []
		self.WindSettingsList = []
		self.ChainLinkList = []
	def read(self,file):
		self.Header.read(file)
		
		version = self.Header.version
		if self.Header.chainSettingsCount > 0:
			print("Reading Chain Settings...")
		file.seek(self.Header.chainSettingsOffset)
		for i in range(0,self.Header.chainSettingsCount):
			newChainSettings = Chain2SettingsData()
			newChainSettings.read(file,version)
			self.ChainSettingsList.append(newChainSettings)
		if self.Header.chainModelCollisionCount > 0:
			print("Reading Chain Collisions...")
		file.seek(self.Header.chainModelCollisionOffset)
		for i in range(0,self.Header.chainModelCollisionCount):
			newChainCollision = Chain2CollisionData()
			newChainCollision.read(file)
			self.ChainCollisionList.append(newChainCollision)
			#print (newChainCollision.jointNameHash)
		if self.Header.chainGroupCount > 0:
			print("Reading Chain Groups...")
		file.seek(self.Header.chainGroupOffset)
		for i in range(0,self.Header.chainGroupCount):
			newChainGroup = Chain2GroupData()
			newChainGroup.read(file,version)
			self.ChainGroupList.append(newChainGroup)
		if self.Header.chainWindSettingsCount > 0:
			print("Reading Wind Settings...")
		file.seek(self.Header.chainWindSettingsOffset)
		for i in range(0,self.Header.chainWindSettingsCount):
			newWindSettings = Chain2WindSettingsData()
			newWindSettings.read(file)
			self.WindSettingsList.append(newWindSettings)
		if self.Header.chainLinkCount > 0:
			print("Reading Chain Links...")
		file.seek(self.Header.chainLinkOffset)
		for i in range(0,self.Header.chainLinkCount):
			newChainLink = Chain2LinkData()
			newChainLink.read(file,version)
			self.ChainLinkList.append(newChainLink)

	def recalculateOffsets(self):
		sizeData = SIZE_DATA(self.Header.version)
		version = self.Header.version
		#Update header offsets
		self.Header.chainSettingsOffset = sizeData.HEADER_SIZE + getPaddingAmount(sizeData.HEADER_SIZE, 16)
		
		currentFilterPathOffset = self.Header.chainSettingsOffset + self.Header.chainSettingsCount*sizeData.CHAIN_SETTING_SIZE# + getPaddingAmount(self.Header.chainSettingsOffset + self.Header.chainSettingsCount*sizeData.CHAIN_SETTING_SIZE, 16)
		for chainSetting in self.ChainSettingsList:
			if chainSetting.colliderFilterInfoPath != "":
				chainSetting.colliderFilterInfoPathOffset = currentFilterPathOffset
				currentFilterPathOffset = getPaddedPos(currentFilterPathOffset + (len(chainSetting.colliderFilterInfoPath)*2 + 2), 8)
			if len(chainSetting.subDataList) != 0 and version >= VERSION_MHWILDS:
				
				chainSetting.subDataOffset = currentFilterPathOffset
				currentFilterPathOffset += len(chainSetting.subDataList) * sizeData.CHAIN_SETTING_SUBDATA_SIZE
		self.Header.chainModelCollisionOffset = getPaddedPos(currentFilterPathOffset,16)
		self.Header.chainSubDataOffset = self.Header.chainModelCollisionOffset + self.Header.chainModelCollisionCount*sizeData.COLLISION_SIZE + getPaddingAmount(self.Header.chainModelCollisionOffset+self.Header.chainModelCollisionCount*sizeData.COLLISION_SIZE, 16)
		currentSubDataOffset = self.Header.chainSubDataOffset
		for collision in self.ChainCollisionList:
			if collision.subDataCount > 0:
				self.Header.chainSubDataCount += collision.subDataCount
				collision.subDataOffset = currentSubDataOffset
				currentSubDataOffset += sizeData.COLLISION_SUBDATA_SIZE
		self.Header.chainGroupOffset = getPaddedPos(self.Header.chainSubDataOffset + self.Header.chainSubDataCount*sizeData.COLLISION_SUBDATA_SIZE,16)
		currentNameOffset = self.Header.chainGroupOffset + self.Header.chainGroupCount * sizeData.CHAIN_GROUP_SIZE + getPaddingAmount(self.Header.chainGroupOffset + self.Header.chainGroupCount * sizeData.CHAIN_GROUP_SIZE, 16)
		currentNodeOffset = 0 #TEMP
		for chainGroup in self.ChainGroupList:
			#chainGroup.terminateNodeNameOffset = currentNameOffset
			currentNodeOffset = currentNameOffset + getPaddingAmount(currentNameOffset, 16)
			chainGroup.nodeOffset = currentNodeOffset
			nextOffset = currentNodeOffset + chainGroup.nodeCount * sizeData.NODE_SIZE
			for chainNode in chainGroup.nodeList: 
				#TODO Export chainJiggles
				if chainNode.jiggleData != None:
					chainNode.jiggleDataOffset = nextOffset
					nextOffset += sizeData.JIGGLE_SIZE
			currentNameOffset = nextOffset + getPaddingAmount(nextOffset, 16)
			
			chainGroup.subGroupDataOffset = currentNameOffset #chainGroup.nodeOffset + (sizeData.NODE_SIZE * chainGroup.nodeCount)#VERSION 48
			chainGroup.subGroupCount = len(chainGroup.subGroupList)
			
			currentNameOffset += (chainGroup.subGroupCount * sizeData.CHAIN_SUBGROUP_SIZE)
			for subGroup in chainGroup.subGroupList:
				currentNodeOffset = currentNameOffset
				subGroup.nodeOffset = currentNodeOffset
				nextOffset = currentNodeOffset + len(subGroup.nodeList) * sizeData.NODE_SIZE
				for chainNode in subGroup.nodeList: 
					if chainNode.jiggleData != None:
						chainNode.jiggleDataOffset = nextOffset
						nextOffset += sizeData.JIGGLE_SIZE
				currentNameOffset = nextOffset + getPaddingAmount(nextOffset, 16)
			
		self.Header.chainWindSettingsOffset = currentNameOffset
		if len(self.ChainLinkList) > 0:
			self.Header.chainLinkOffset = self.Header.chainWindSettingsOffset + (sizeData.WIND_SIZE*self.Header.chainWindSettingsCount) + getPaddingAmount(self.Header.chainWindSettingsOffset + (sizeData.WIND_SIZE*self.Header.chainWindSettingsCount), 16)
			currentLinkDataOffset = self.Header.chainLinkOffset + sizeData.CHAIN_LINK_SIZE * len(self.ChainLinkList)
			for chainLink in self.ChainLinkList:
				if len(chainLink.nodeColLinkList) != 0:
					chainLink.nodeOffset = currentLinkDataOffset
					currentLinkDataOffset += sizeData.CHAIN_LINK_NODE_SIZE * len(chainLink.nodeColLinkList)
				
	def write(self,file):
		version = self.Header.version
		self.recalculateOffsets()
		#print(self.Header)
		self.Header.write(file)
		file.seek(self.Header.chainSettingsOffset)
		for chainSettings in self.ChainSettingsList:
			chainSettings.write(file,version)
		
		#Loop over chain settings again to write filter paths
		for chainSettings in self.ChainSettingsList:
			
			if chainSettings.colliderFilterInfoPathOffset != 0:
				file.seek(chainSettings.colliderFilterInfoPathOffset)
				write_unicode_string(file, chainSettings.colliderFilterInfoPath)
			if len(chainSettings.subDataList) != 0 and chainSettings.subDataOffset != 0:
				file.seek(chainSettings.subDataOffset)
				for subDataEntry in chainSettings.subDataList:
					subDataEntry.write(file)
		file.seek(self.Header.chainModelCollisionOffset)
		for chainCollision in self.ChainCollisionList:
			chainCollision.write(file)
			
		file.seek(self.Header.chainSubDataOffset)
		#Loop over again to write subdata
		for chainCollision in self.ChainCollisionList:
			if chainCollision.subDataCount:	
				chainCollision.subData.write(file)
		
		file.seek(self.Header.chainGroupOffset)
		for chainGroup in self.ChainGroupList:
			chainGroup.write(file,version)
		#Loop over chain group again to write the nodes
		for c, chainGroup in enumerate(self.ChainGroupList):
			#print("Node Name Offset:" + str(chainGroup.terminateNodeNameOffset))
			#print("Node Offset:" + str(chainGroup.nodeOffset))
			#file.seek(chainGroup.terminateNodeNameOffset)
			#write_unicode_string(file, chainGroup.terminateNodeName)
			file.seek(chainGroup.nodeOffset)
			
			for i, node in enumerate(chainGroup.nodeList):
				node.write(file,version)
			for i, node in enumerate(chainGroup.nodeList):
				if node.jiggleData != None:
					node.jiggleData.write(file,version)
			if chainGroup.subGroupCount != 0:
				file.seek(chainGroup.subGroupDataOffset)
				for subGroup in chainGroup.subGroupList:
					subGroup.write(file,version)		
				#Loop again to write sub group nodes
				for subGroup in chainGroup.subGroupList:
					file.seek(subGroup.nodeOffset)
					for i, node in enumerate(subGroup.nodeList):
						node.write(file,version)
					for i, node in enumerate(subGroup.nodeList):
						if node.jiggleData != None:
							node.jiggleData.write(file,version)

		file.seek(self.Header.chainWindSettingsOffset)
		for windSettings in self.WindSettingsList:
			windSettings.write(file)
		file.seek(self.Header.chainLinkOffset)
		for chainLink in self.ChainLinkList:
			chainLink.write(file,version)
		
		#Loop again to write link nodes
		for chainLink in self.ChainLinkList:
			for linkNode in chainLink.nodeColLinkList:
				linkNode.write(file)
				
#---CHAIN IO FUNCTIONS---#

def readREChain2(filepath):
	print(textColors.OKCYAN + "__________________________________\nChain2 read started." + textColors.ENDC)
	print("Opening " + filepath)
	try:  
		file = open(filepath,"rb")
	except:
		raiseError("Failed to open " + filepath)
	
	chainFile = Chain2File()
	chainFile.read(file)
	file.close()
	print(textColors.OKGREEN + "__________________________________\nChain2 read finished." + textColors.ENDC)
	return chainFile
def writeREChain2(chainFile,filepath):
	print(textColors.OKCYAN + "__________________________________\nChain2 write started." + textColors.ENDC)
	print("Opening " + filepath)
	try:
		file = open(filepath,"wb")
	except:
		raiseError("Failed to open " + filepath)
	
	chainFile.write(file)
	file.close()
	print(textColors.OKGREEN + "__________________________________\nChain2 write finished." + textColors.ENDC)