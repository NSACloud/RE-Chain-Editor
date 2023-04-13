#Author: NSA Cloud

from .gen_functions import textColors,raiseWarning,raiseError,getPaddingAmount,read_uint,read_int,read_uint64,read_int64,read_float,read_ushort,read_ubyte,read_unicode_string,read_byte,read_short,write_uint,write_int,write_uint64,write_int64,write_float,write_ushort,write_ubyte,write_unicode_string,write_byte,write_short

version = 48

#---CHAIN STRUCTS---#
class SIZE_DATA():
	def __init__(self):
		self.HEADER_SIZE = 104
		self.CHAIN_SETTING_SIZE = 168
		self.CHAIN_GROUP_SIZE = 112
		self.COLLISION_SIZE = 80
		self.COLLISION_SUBDATA_SIZE = 64
		self.NODE_SIZE = 80
		self.JIGGLE_SIZE = 72
		self.WIND_SIZE = 184
	def setSizeData(self, ver):
		global version; version = ver
		if ver == 21:
			self.COLLISION_SIZE = 56
			self.CHAIN_SETTING_SIZE = 128
			self.CHAIN_GROUP_SIZE = 48
			self.NODE_SIZE = 64
		elif ver == 24:
			self.COLLISION_SIZE = 56
			self.CHAIN_SETTING_SIZE = 160
			self.CHAIN_GROUP_SIZE = 48
			self.NODE_SIZE = 64
		elif ver == 35:
			self.COLLISION_SIZE = 72
			self.CHAIN_SETTING_SIZE = 160
			self.CHAIN_GROUP_SIZE = 80
		elif ver == 39:
			self.CHAIN_SETTING_SIZE = 160
			self.CHAIN_GROUP_SIZE = 80
		elif ver == 46:
			self.CHAIN_GROUP_SIZE = 88
		elif ver == 52:
			self.CHAIN_SETTING_SIZE = 176
			self.CHAIN_GROUP_SIZE = 120
		elif ver == 53:
			self.HEADER_SIZE = 112
			self.CHAIN_SETTING_SIZE = 176
			self.CHAIN_GROUP_SIZE = 120


class ChainHeaderData():
	def __init__(self):
		self.version = 48
		self.magic = 1851877475
		self.errFlags = 0#ENUM
		self.masterSize = 0
		self.collisionAttrAssetOffset = 0
		self.chainModelCollisionOffset = 0
		self.chainSubDataOffset = 0 #For internal use, does not exist in file
		self.chainSubDataCount = 0 #For internal use, does not exist in file
		self.extraDataOffset = 0
		self.chainGroupOffset = 0
		self.chainLinkOffset = 0
		self.ver53UnknOffset = 0
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
		self.calculateStepTime = 2.0
		self.modelCollisionSearch = 0#BOOL
		self.legacyVersion = 0
		self.collisionFilterHit0 = 0
		self.collisionFilterHit1 = 0
		self.collisionFilterHit2 = 0
		self.collisionFilterHit3 = 0
		self.collisionFilterHit4 = 0
		self.collisionFilterHit5 = 0
		self.collisionFilterHit6 = 0
		self.collisionFilterHit7 = 0
		
	def read(self,file):
		global version
		print("Reading Header...")
		self.version = read_uint(file)
		version = self.version
		#if self.version != 48:
		#	raiseWarning("Unsupported chain version " + str(self.version) + ", file may not load correctly.")
		self.magic = read_uint(file)
		if self.magic != 1851877475:
			raiseError("File is not a chain file.")
		print("Version", version)
		self.errFlags = read_uint(file)#ENUM
		self.masterSize = read_uint(file)
		self.collisionAttrAssetOffset = read_uint64(file)
		self.chainModelCollisionOffset = read_uint64(file)
		self.extraDataOffset = read_uint64(file)
		self.chainGroupOffset = read_uint64(file)
		self.chainLinkOffset = read_uint64(file)
		if version >= 53:
			self.ver53UnknOffset = read_uint64(file)
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
		self.legacyVersion = read_ubyte(file)
		self.collisionFilterHit0 = read_ubyte(file)
		self.collisionFilterHit1 = read_ubyte(file)
		self.collisionFilterHit2 = read_ubyte(file)
		self.collisionFilterHit3 = read_ubyte(file)
		self.collisionFilterHit4 = read_ubyte(file)
		self.collisionFilterHit5 = read_ubyte(file)
		self.collisionFilterHit6 = read_ubyte(file)
		self.collisionFilterHit7 = read_ubyte(file)
		
	def write(self,file):
		write_uint(file, self.version)
		write_uint(file, self.magic)
		write_uint(file, self.errFlags)#ENUM
		write_uint(file, self.masterSize)
		write_uint64(file, self.collisionAttrAssetOffset)
		write_uint64(file, self.chainModelCollisionOffset)
		write_uint64(file, self.extraDataOffset)
		write_uint64(file, self.chainGroupOffset)
		write_uint64(file, self.chainLinkOffset)
		if version >= 53:
			write_uint64(file, self.ver53UnknOffset)
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
		write_ubyte(file, self.legacyVersion)
		write_ubyte(file, self.collisionFilterHit0)
		write_ubyte(file, self.collisionFilterHit1)
		write_ubyte(file, self.collisionFilterHit2)
		write_ubyte(file, self.collisionFilterHit3)
		write_ubyte(file, self.collisionFilterHit4)
		write_ubyte(file, self.collisionFilterHit5)
		write_ubyte(file, self.collisionFilterHit6)
		write_ubyte(file, self.collisionFilterHit7)

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class Joint():
	def __init__(self):
		self.offset = 0
		self.jointName = "READ_ERROR"
	def read(self,file):
		self.offset = read_uint64(file)
		currentPos = file.tell()
		file.seek(self.offset)
		self.jointName = read_unicode_string(file)
		file.seek(currentPos)
	def write(self,file):
		pass#TODO
	
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)
	
class ChainSettingsData():
	def __init__(self):
		self.jointList = []
		self.colliderFilterInfoPathOffset = 0
		self.colliderFilterInfoPath = ""
		self.sprayParameterArc = 0.0
		self.sprayParameterFrequency = 0.0
		self.sprayParameterCurve1 = 0.0
		self.sprayParameterCurve2 = 0.0
		self.id = 0
		self.chainType = 0 #ENUM
		self.settingsAttrFlags = 1 #ENUM
		self.muzzleDirection = 1 #ENUM
		self.windID = 0
		self.gravityX = 0.0
		self.gravityY = -9.8
		self.gravityZ = 0.0
		self.muzzleVelocityX = 0.0
		self.muzzleVelocityY = 0.0
		self.muzzleVelocityZ = 0.0
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
		self.springMaxVelocity = 0.0
		self.springCalcType = 0#ENUM
		self.unknFlag = 0#BOOL
		self.padding = 0
		self.reduceSelfDistanceRate = 0.0
		self.secondReduceDistanceRate = 0.0
		self.secondReduceDistanceSpeed = 0.0
		self.friction = 0.0
		self.shockAbsorptionRate = 0.0
		self.coefOfElasticity = 0.0
		self.coefOfExternalForces = 0.0
		self.stretchInteractionRatio = 0.5
		self.angleLimitInteractionRatio = 0.5
		self.shootingElasticLimitRate = 0.0
		self.groupDefaultAttr = 0#ENUM
		self.windEffectCoef = 0.0
		self.velocityLimit = 0.0
		self.hardness = 0.0
		self.unknChainSettingValue0 = 0.0
		self.unknChainSettingValue1 = 0.1#VERSION 48
		self.unknChainSettingValue2 = 0.0#VERSION 52
		self.unknChainSettingValue3 = 0.0#VERSION 52
	def read(self,file):
		self.jointList = []
		self.colliderFilterInfoPathOffset = read_uint64(file)
		if self.colliderFilterInfoPathOffset != 0:
			currentPos = file.tell()
			file.seek(self.colliderFilterInfoPathOffset)
			self.colliderFilterInfoPath = read_unicode_string(file)
			file.seek(currentPos)
		self.sprayParameterArc = read_float(file)
		self.sprayParameterFrequency = read_float(file)
		self.sprayParameterCurve1 = read_float(file)
		self.sprayParameterCurve2 = read_float(file)
		self.id = read_uint(file)
		self.chainType = read_ubyte(file)
		self.settingsAttrFlags = read_ubyte(file) #ENUM
		self.muzzleDirection = read_ubyte(file) #ENUM
		self.windID = read_byte(file)
		self.gravityX = read_float(file)
		self.gravityY = read_float(file)
		self.gravityZ = read_float(file)
		self.muzzleVelocityX = read_float(file)
		self.muzzleVelocityY = read_float(file)
		self.muzzleVelocityZ = read_float(file)
		self.damping = read_float(file)
		self.secondDamping = read_float(file)
		self.secondDampingSpeed = read_float(file)
		if version >= 24:
			self.minDamping = read_float(file)
			self.secondMinDamping = read_float(file)
			self.dampingPow = read_float(file)
			self.secondDampingPow = read_float(file)
			self.collideMaxVelocity = read_float(file)
		self.springForce = read_float(file)
		if version >= 24:
			self.springLimitRate = read_float(file)
			self.springMaxVelocity = read_float(file)
			self.springCalcType = read_ubyte(file) #ENUM
			self.unknFlag = read_ubyte(file)
			self.padding = read_ushort(file)
		if version >= 53:
			self.unknChainSettingValue2 = read_float(file)#VERSION 52
			self.unknChainSettingValue3 = read_float(file)#VERSION 52
		self.reduceSelfDistanceRate = read_float(file)
		self.secondReduceDistanceRate = read_float(file)
		self.secondReduceDistanceSpeed = read_float(file)
		self.friction = read_float(file)
		self.shockAbsorptionRate = read_float(file)
		self.coefOfElasticity = read_float(file)
		self.coefOfExternalForces = read_float(file)
		self.stretchInteractionRatio = read_float(file)
		self.angleLimitInteractionRatio = read_float(file)
		self.shootingElasticLimitRate = read_float(file)
		self.groupDefaultAttr = read_uint(file)
		self.windEffectCoef = read_float(file)
		self.velocityLimit = read_float(file)
		self.hardness = read_float(file)
		if version >= 46:
			self.unknChainSettingValue0 = read_float(file)#VERSION 48
			self.unknChainSettingValue1 = read_float(file)#VERSION 48
		if version == 52:
			self.unknChainSettingValue2 = read_float(file)#VERSION 52
			self.unknChainSettingValue3 = read_float(file)#VERSION 52
		
	def write(self,file):
		write_uint64(file, self.colliderFilterInfoPathOffset)
		write_float(file, self.sprayParameterArc)
		write_float(file, self.sprayParameterFrequency)
		write_float(file, self.sprayParameterCurve1)
		write_float(file, self.sprayParameterCurve2)
		write_uint(file, self.id)
		write_ubyte(file, self.chainType)
		write_ubyte(file, self.settingsAttrFlags) #ENUM
		write_ubyte(file, self.muzzleDirection) #ENUM
		write_byte(file, self.windID)
		write_float(file, self.gravityX)
		write_float(file, self.gravityY)
		write_float(file, self.gravityZ)
		write_float(file, self.muzzleVelocityX)
		write_float(file, self.muzzleVelocityY)
		write_float(file, self.muzzleVelocityZ)
		write_float(file, self.damping)
		write_float(file, self.secondDamping)
		write_float(file, self.secondDampingSpeed)
		if version >= 24:
			write_float(file, self.minDamping)
			write_float(file, self.secondMinDamping)
			write_float(file, self.dampingPow)
			write_float(file, self.secondDampingPow)
			write_float(file, self.collideMaxVelocity)
		write_float(file, self.springForce)
		if version >= 24:
			write_float(file, self.springLimitRate)
			write_float(file, self.springMaxVelocity)
			write_ubyte(file, self.springCalcType) #ENUM
			write_ubyte(file, self.unknFlag)
			write_ushort(file, self.padding)
		if version >= 53:
			write_float(file, self.unknChainSettingValue2)#VERSION 52
			write_float(file, self.unknChainSettingValue3)#VERSION 52
		write_float(file, self.reduceSelfDistanceRate)
		write_float(file, self.secondReduceDistanceRate)
		write_float(file, self.secondReduceDistanceSpeed)
		write_float(file, self.friction)
		write_float(file, self.shockAbsorptionRate)
		write_float(file, self.coefOfElasticity)
		write_float(file, self.coefOfExternalForces)
		write_float(file, self.stretchInteractionRatio)
		write_float(file, self.angleLimitInteractionRatio)
		write_float(file, self.shootingElasticLimitRate)
		write_uint(file, self.groupDefaultAttr)
		write_float(file, self.windEffectCoef)
		write_float(file, self.velocityLimit)
		write_float(file, self.hardness)
		if version >= 46:
			write_float(file, self.unknChainSettingValue0)#VERSION 48
			write_float(file, self.unknChainSettingValue1)#VERSION 48
		if version == 52:
			write_float(file, self.unknChainSettingValue2)#VERSION 52
			write_float(file, self.unknChainSettingValue3)#VERSION 52


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
		
		#if version >= 35:
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


class ChainCollisionData():
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
		self.radius = 0.15
		self.lerp = 0.0
		self.unknCollisionValue = 0.0#VERSION 48
		self.chainCollisionShape = 1#ENUM, sphere by default
		self.div = 0
		self.subDataCount = 0
		self.collisionFilterFlags = -1
		self.subDataFlag = 0
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
		
		if version >= 35:
			self.rotOffsetX = read_float(file)
			self.rotOffsetY = read_float(file)
			self.rotOffsetZ = read_float(file)
			self.rotOffsetW = read_float(file)
		if version >= 39:
			self.rotationOrder = read_uint(file)#VERSION 39
		
		self.jointNameHash = read_uint(file)#MURMUR HASH
		self.pairJointNameHash = read_uint(file)#MURMUR HASH
		self.radius = read_float(file)
		self.lerp = read_float(file)
		if version >= 48:
			self.unknCollisionValue = read_float(file)#VERSION 48
		
		self.chainCollisionShape = read_ubyte(file)#ENUM, sphere by default
		self.div = read_ubyte(file)
		self.subDataCount = read_ushort(file)
		self.collisionFilterFlags = read_short(file)
		self.subDataFlag = read_short(file)
		if version == 39 or version == 46:
			self.padding = read_int(file)
		
		if self.subDataFlag > 0:
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
		
		if version >= 35:
			write_float(file, self.rotOffsetX)
			write_float(file, self.rotOffsetY)
			write_float(file, self.rotOffsetZ)
			write_float(file, self.rotOffsetW)
		if version >= 39:
			write_uint(file, self.rotationOrder)#VERSION 39

		write_uint(file, self.jointNameHash)#MURMUR HASH
		write_uint(file, self.pairJointNameHash)#MURMUR HASH
		write_float(file, self.radius)
		write_float(file, self.lerp)
		if version >= 48:
			write_float(file,self.unknCollisionValue)#VERSION 48

		write_ubyte(file, self.chainCollisionShape)#ENUM, sphere by default
		write_ubyte(file, self.div)
		write_ushort(file, self.subDataCount)
		write_short(file, self.collisionFilterFlags)
		write_short(file, self.subDataFlag)
		if version == 39 or version == 46:
			write_int(file, self.padding)
		
		#Write subdata later
			
	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)



class ChainJiggleData():
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
		self.springForce = 0.04
		self.gravityCoef = 1.0
		self.damping = 0.04
		self.attrFlags = 0
		self.padding2 = 0

	def read(self,file):
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
		self.springForce = read_float(file)
		self.gravityCoef = read_float(file)
		self.damping = read_float(file)
		self.attrFlags = read_uint(file)
		self.padding2 = read_uint(file)

	def write(self,file):
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
		write_float(file, self.springForce)
		write_float(file, self.gravityCoef)
		write_float(file, self.damping)
		write_uint(file, self.attrFlags)
		write_uint(file, self.padding2)

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class ChainNodeData():
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
		self.unknChainNodeValue0 = 1.0#VERSION 48
		self.unknChainNodeValue1 = 0.0#VERSION 48
		self.jiggleData = None
		
	def read(self,file):
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
		if version >= 35:
			self.jiggleDataOffset = read_uint64(file)
			self.unknChainNodeValue0 = read_float(file)#VERSION 48
			self.unknChainNodeValue1 = read_float(file)#VERSION 48
		if self.jiggleDataOffset != 0:
			currentPos = file.tell()
			self.jiggleData = ChainJiggleData()
			file.seek(self.jiggleDataOffset)
			self.jiggleData.read(file)
			file.seek(currentPos)

		file.seek(file.tell()+getPaddingAmount(file.tell(),16))#Skip padding
	def write(self,file):
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
		if version >= 35:
			write_uint64(file, self.jiggleDataOffset)
			write_float(file, self.unknChainNodeValue0)#VERSION 48
			write_float(file, self.unknChainNodeValue1)#VERSION 48
		file.write(b"\x00"*getPaddingAmount(file.tell(), 16))

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class ChainGroupData():
	def __init__(self):
		self.terminateNodeNameOffset = 0
		self.terminateNodeName = "READ_ERROR"
		self.nodeOffset = 0
		self.settingID = 0
		self.nodeCount = 0
		self.rotationOrder = 0#ENUM
		self.autoBlendCheckNodeNo = 0
		self.windID = 0
		self.terminateNodeNameHash = 0#MURMUR HASH
		self.attrFlags = 33971#ENUM
		self.collisionFilterFlags = 0#ENUM
		self.extraNodeLocalPosX = 0.0
		self.extraNodeLocalPosY = 0.0
		self.extraNodeLocalPosZ = 0.0
		self.tag0 = 0
		self.tag1 = 0
		self.tag2 = 0
		self.tag3 = 0
		self.dampingNoise0 = 0.0
		self.dampingNoise1 = 0.0
		self.endRotConstMax = 12.5
		self.tagCount = 0
		self.angleLimitDirectionMode = 0#ENUM
		self.padding = 0
		self.unknGroupValue0 = 0.0#VERSION 48
		self.unknGroupValue0B = 0.0#VERSION 48
		self.unknBoneHash = 1095307227#VERSION 48 MURMUR HASH
		self.unknGroupValue1 = 0#VERSION 48
		self.unknGroupValue2 = 0#VERSION 48
		self.unknGroupValue3 = 0#VERSION 52
		self.nextChainNameOffset = 0#VERSION 48
		self.nodeList = []

	def read(self,file):
		self.terminateNodeNameOffset = read_uint64(file)
		currentPos = file.tell()
		file.seek(self.terminateNodeNameOffset)
		self.terminateNodeName = read_unicode_string(file)
		file.seek(currentPos)
		self.nodeOffset = read_uint64(file)
		self.settingID = read_int(file)
		self.nodeCount = read_ubyte(file)
		self.rotationOrder = read_ubyte(file)#ENUM
		self.autoBlendCheckNodeNo = read_ubyte(file)
		self.windID = read_byte(file)
		self.terminateNodeNameHash = read_uint(file)#MURMUR HASH
		self.attrFlags = read_uint(file)#ENUM
		self.collisionFilterFlags = read_uint(file)#ENUM
		self.extraNodeLocalPosX = read_float(file)
		self.extraNodeLocalPosY = read_float(file)
		self.extraNodeLocalPosZ = read_float(file)
		if version >= 35:
			self.tag0 = read_int(file)
			self.tag1 = read_int(file)
			self.tag2 = read_int(file)
			self.tag3 = read_int(file)
			self.dampingNoise0 = read_float(file)
			self.dampingNoise1 = read_float(file)
			self.endRotConstMax = read_float(file)
			self.tagCount = read_ubyte(file)
			self.angleLimitDirectionMode = read_ubyte(file)#ENUM
			self.padding = read_ushort(file)
		if version >= 48:
			self.unknGroupValue0 = read_float(file)#VERSION 48
			self.unknGroupValue0B = read_float(file)#VERSION 48
			self.unknBoneHash = read_uint(file)#VERSION 48
			self.unknGroupValue1 = read_uint(file)#VERSION 48
			self.unknGroupValue2 = read_uint64(file)#VERSION 48
		if version >= 52:
			self.unknGroupValue3 = read_int64(file)#VERSION 52
		if version >= 46:
			self.nextChainName = read_uint64(file)#VERSION 46
		self.nodeList = []
		currentPos = file.tell()
		file.seek(self.nodeOffset)
		for i in range(0,self.nodeCount):
			newChainNode = ChainNodeData()
			newChainNode.read(file)
			self.nodeList.append(newChainNode)
		#paddingAmt = getPaddingAmount(currentPos,16) if version != 52 and version !=46 else 0

		#file.seek(currentPos+paddingAmt)#Go back to the end of chain group and skip padding
		file.seek(currentPos)
		
	def write(self,file):
		startPos = file.tell()    
		write_uint64(file, self.terminateNodeNameOffset)
		write_uint64(file, self.nodeOffset)
		write_int(file, self.settingID)
		write_ubyte(file, self.nodeCount)
		write_ubyte(file, self.rotationOrder)#ENUM
		write_ubyte(file, self.autoBlendCheckNodeNo)
		write_byte(file, self.windID)
		write_uint(file, self.terminateNodeNameHash)#MURMUR HASH
		write_uint(file, self.attrFlags)#ENUM
		write_uint(file, self.collisionFilterFlags)#ENUM
		write_float(file, self.extraNodeLocalPosX)
		write_float(file, self.extraNodeLocalPosY)
		write_float(file, self.extraNodeLocalPosZ)
		if version >= 35:
			write_int(file, self.tag0)
			write_int(file, self.tag1)
			write_int(file, self.tag2)
			write_int(file, self.tag3)
			write_float(file, self.dampingNoise0)
			write_float(file, self.dampingNoise1)
			write_float(file, self.endRotConstMax)
			write_ubyte(file, self.tagCount)
			write_ubyte(file, self.angleLimitDirectionMode)#ENUM
			write_ushort(file, self.padding)
		if version >= 48:
			write_float(file, self.unknGroupValue0)#VERSION 48
			write_float(file, self.unknGroupValue0B)#VERSION 48
			write_uint(file, self.unknBoneHash)#VERSION 48
			write_uint(file, self.unknGroupValue1)#VERSION 48
			write_uint64(file, self.unknGroupValue2)#VERSION 48
		if version >= 52:
			write_int64(file, self.unknGroupValue3)#VERSION 52
		if version >= 46:
			write_uint64(file, self.nextChainNameOffset)#VERSION 46
		

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class WindSettingsData():
	def __init__(self):
		self.id = 0
		self.jointList = []
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
		self.jointList = []
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

class ChainLinkData():
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
		
	def read(self,file):
		self.nodeOffset = read_uint64(file)
		self.terminateNodeNameHashA = read_uint(file)#MURMUR HASH
		self.terminateNodeNameHashB = read_uint(file)#MURMUR HASH
		self.distanceShrinkLimitCoef = read_float(file)
		self.distanceExpandLimitCoef = read_float(file)
		self.linkMode = read_ubyte(file)#ENUM
		self.connectFlags = read_ubyte(file)#ENUM
		self.linkAttrFlags = read_ushort(file)#ENUM
		self.nodeCount = read_ubyte(file)
		self.skipGroupA = read_ubyte(file)
		self.skipGroupB = read_ubyte(file)
		self.linkOrder = read_ubyte(file)#ENUM
		
	def write(self,file):
		write_uint64(file, self.nodeOffset)
		write_uint(file, self.terminateNodeNameHashA)#MURMUR HASH
		write_uint(file, self.terminateNodeNameHashB)#MURMUR HASH
		write_float(file, self.distanceShrinkLimitCoef)
		write_float(file, self.distanceExpandLimitCoef)
		write_ubyte(file, self.linkMode)#ENUM
		write_ubyte(file, self.connectFlags)#ENUM
		write_ushort(file, self.linkAttrFlags)#ENUM
		write_ubyte(file, self.nodeCount)
		write_ubyte(file, self.skipGroupA)
		write_ubyte(file, self.skipGroupB)
		write_ubyte(file, self.linkOrder)#ENUM

	def __str__(self):
		return str(self.__class__) + ": " + str(self.__dict__)

class ChainFile():
	def __init__(self):
		self.Header = ChainHeaderData()
		self.sizeData = SIZE_DATA()
		self.sizeData.setSizeData(self.Header.version)
		self.ChainSettingsList = []
		self.ChainCollisionList = []
		self.ChainGroupList = []
		self.WindSettingsList = []
		self.ChainLinkList = []
	def read(self,file):
		self.Header.read(file)
		self.sizeData.setSizeData(self.Header.version)
		if self.Header.chainSettingsCount > 0:
			print("Reading Chain Settings...")
		file.seek(self.Header.chainSettingsOffset)
		for i in range(0,self.Header.chainSettingsCount):
			newChainSettings = ChainSettingsData()
			newChainSettings.read(file)
			currentPos = file.tell()
			for j in range(0,self.Header.chainGroupCount):#Add joints to chain settings
				file.seek(self.Header.chainGroupOffset + j * self.sizeData.CHAIN_GROUP_SIZE + 16)
				if read_uint(file) == i:
					file.seek(self.Header.chainGroupOffset + j * self.sizeData.CHAIN_GROUP_SIZE)
					newJoint = Joint()
					newJoint.read(file)
					newChainSettings.jointList.append(newJoint)
					
			file.seek(currentPos)
			self.ChainSettingsList.append(newChainSettings)
		if self.Header.chainModelCollisionCount > 0:
			print("Reading Chain Collisions...")
		file.seek(self.Header.chainModelCollisionOffset)
		for i in range(0,self.Header.chainModelCollisionCount):
			newChainCollision = ChainCollisionData()
			newChainCollision.read(file)
			self.ChainCollisionList.append(newChainCollision)
			#print (newChainCollision.jointNameHash)
		if self.Header.chainGroupCount > 0:
			print("Reading Chain Groups...")
		file.seek(self.Header.chainGroupOffset)
		for i in range(0,self.Header.chainGroupCount):
			newChainGroup = ChainGroupData()
			newChainGroup.read(file)
			self.ChainGroupList.append(newChainGroup)
		if self.Header.chainWindSettingsCount > 0:
			print("Reading Wind Settings...")
		file.seek(self.Header.chainWindSettingsOffset)
		for i in range(0,self.Header.chainWindSettingsCount):
			newWindSettings = WindSettingsData()
			newWindSettings.read(file)
			"""
			currentPos = file.tell()
			for j in range(0,self.Header.chainGroupCount):#Add joints to wind settings
				file.seek(self.Header.chainGroupOffset + j * self.sizeData.CHAIN_GROUP_SIZE + 23)
				if read_ubyte(file) == newWindSettings.id:
					file.seek(self.Header.chainGroupOffset + j * self.sizeData.CHAIN_GROUP_SIZE)
					newJoint = Joint()
					newJoint.read(file)
					newWindSettings.jointList.append(newJoint)
			file.seek(currentPos)
			"""
			self.WindSettingsList.append(newWindSettings)
		if self.Header.chainLinkCount > 0:
			print("Reading Chain Links...")
		file.seek(self.Header.chainLinkOffset)
		for i in range(0,self.Header.chainLinkCount):
			newChainLink = ChainLinkData()
			newChainLink.read(file)
			self.ChainLinkList.append(newChainLink)

	def recalculateOffsets(self):
		self.sizeData.setSizeData(self.Header.version)
		#Update header offsets
		self.Header.chainSettingsOffset = self.sizeData.HEADER_SIZE + getPaddingAmount(self.sizeData.HEADER_SIZE, 16)
		
		currentFilterPathOffset = self.Header.chainSettingsOffset + self.Header.chainSettingsCount*self.sizeData.CHAIN_SETTING_SIZE + getPaddingAmount(self.Header.chainSettingsOffset + self.Header.chainSettingsCount*self.sizeData.CHAIN_SETTING_SIZE, 16)
		for chainSetting in self.ChainSettingsList:
			if chainSetting.colliderFilterInfoPath != "":
				chainSetting.colliderFilterInfoPathOffset = currentFilterPathOffset
				currentFilterPathOffset = currentFilterPathOffset + (len(chainSetting.colliderFilterInfoPath)*2 + 2) + getPaddingAmount(currentFilterPathOffset + (len(chainSetting.colliderFilterInfoPath)*2 + 2), 16)
		
		self.Header.chainModelCollisionOffset = currentFilterPathOffset
		self.Header.chainSubDataOffset = self.Header.chainModelCollisionOffset + self.Header.chainModelCollisionCount*self.sizeData.COLLISION_SIZE + getPaddingAmount(self.Header.chainModelCollisionOffset+self.Header.chainModelCollisionCount*self.sizeData.COLLISION_SIZE, 16)
		currentSubDataOffset = self.Header.chainSubDataOffset
		for collision in self.ChainCollisionList:
			if collision.subDataFlag > 0:
				self.Header.chainSubDataCount += collision.subDataFlag
				collision.subDataOffset = currentSubDataOffset
				currentSubDataOffset += self.sizeData.COLLISION_SUBDATA_SIZE
		self.Header.chainGroupOffset = self.Header.chainSubDataOffset + self.Header.chainSubDataCount*self.sizeData.COLLISION_SUBDATA_SIZE + getPaddingAmount(self.Header.chainSubDataOffset + self.Header.chainSubDataCount*self.sizeData.COLLISION_SUBDATA_SIZE, 16)
		currentNameOffset = self.Header.chainGroupOffset + self.Header.chainGroupCount * self.sizeData.CHAIN_GROUP_SIZE + getPaddingAmount(self.Header.chainGroupOffset + self.Header.chainGroupCount * self.sizeData.CHAIN_GROUP_SIZE, 16)
		currentNodeOffset = 0 #TEMP
		for chainGroup in self.ChainGroupList:
			chainGroup.terminateNodeNameOffset = currentNameOffset
			currentNodeOffset = currentNameOffset + (len(chainGroup.terminateNodeName)*2+2)+getPaddingAmount(currentNameOffset + (len(chainGroup.terminateNodeName)*2+2), 16)
			chainGroup.nodeOffset = currentNodeOffset
			nextOffset = currentNodeOffset + chainGroup.nodeCount * self.sizeData.NODE_SIZE
			for chainNode in chainGroup.nodeList: 
				#TODO Export chainJiggles
				if chainNode.jiggleData != None:
					chainNode.jiggleDataOffset = nextOffset
					nextOffset += self.sizeData.JIGGLE_SIZE
			currentNameOffset = nextOffset + getPaddingAmount(nextOffset, 16)
			chainGroup.nextChainNameOffset = nextOffset #chainGroup.nodeOffset + (self.sizeData.NODE_SIZE * chainGroup.nodeCount)#VERSION 48
		for chainLink in self.ChainLinkList:
			#TODO Set nodeOffset for chain links
			pass
		self.Header.chainWindSettingsOffset = currentNameOffset
		self.Header.chainLinkOffset = self.Header.chainWindSettingsOffset + (self.sizeData.WIND_SIZE*self.Header.chainWindSettingsCount) + getPaddingAmount(self.Header.chainWindSettingsOffset + (self.sizeData.WIND_SIZE*self.Header.chainWindSettingsCount), 16)
		
	def write(self,file):
		self.recalculateOffsets()
		#print(self.Header)
		self.Header.write(file)
		file.seek(self.Header.chainSettingsOffset)
		for chainSettings in self.ChainSettingsList:
			chainSettings.write(file)
		
		#Loop over chain settings again to write filter paths
		for chainSettings in self.ChainSettingsList:
			if chainSettings.colliderFilterInfoPathOffset != 0:
				file.seek(chainSettings.colliderFilterInfoPathOffset)
				write_unicode_string(file, chainSettings.colliderFilterInfoPath)
		
		file.seek(self.Header.chainModelCollisionOffset)
		for chainCollision in self.ChainCollisionList:
			chainCollision.write(file)
			
		file.seek(self.Header.chainSubDataOffset)
		#Loop over again to write subdata
		for chainCollision in self.ChainCollisionList:
			if chainCollision.subDataFlag:	
				chainCollision.subData.write(file)
		
		file.seek(self.Header.chainGroupOffset)
		for chainGroup in self.ChainGroupList:
			chainGroup.write(file)
		#Loop over chain group again to write the nodes
		for c, chainGroup in enumerate(self.ChainGroupList):
			#print("Node Name Offset:" + str(chainGroup.terminateNodeNameOffset))
			#print("Node Offset:" + str(chainGroup.nodeOffset))
			file.seek(chainGroup.terminateNodeNameOffset)
			write_unicode_string(file, chainGroup.terminateNodeName)
			file.seek(chainGroup.nodeOffset)
			
			for i, node in enumerate(chainGroup.nodeList):
				node.write(file)
			for i, node in enumerate(chainGroup.nodeList):
				if node.jiggleData != None:
					node.jiggleData.write(file)

		file.seek(self.Header.chainWindSettingsOffset)
		for windSettings in self.WindSettingsList:
			windSettings.write(file)
		file.seek(self.Header.chainLinkOffset)
		for chainLink in self.ChainLinkList:
			chainLink.write(file)
#---CHAIN IO FUNCTIONS---#

def readREChain(filepath):
	print(textColors.OKCYAN + "__________________________________\nChain read started." + textColors.ENDC)
	print("Opening " + filepath)
	try:  
		file = open(filepath,"rb")
	except:
		raiseError("Failed to open " + filepath)
	
	chainFile = ChainFile()
	chainFile.read(file)
	file.close()
	print(textColors.OKGREEN + "__________________________________\nChain read finished." + textColors.ENDC)
	return chainFile
def writeREChain(chainFile,filepath):
	print(textColors.OKCYAN + "__________________________________\nChain write started." + textColors.ENDC)
	print("Opening " + filepath)
	try:
		file = open(filepath,"wb")
	except:
		raiseError("Failed to open " + filepath)
	
	chainFile.write(file)
	file.close()
	print(textColors.OKGREEN + "__________________________________\nChain write finished." + textColors.ENDC)