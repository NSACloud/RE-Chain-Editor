#Author: NSA Cloud
import json
import os
import re
import bpy

from .gen_functions import textColors,raiseWarning
from .blender_utils import showErrorMessageBox
#from .blender_re_chain import findHeaderObj

def findHeaderObj():
	if bpy.data.collections.get("chainData",None) != None:
		objList = bpy.data.collections["chainData"].all_objects
		headerList = [obj for obj in objList if obj.get("TYPE",None) == "RE_CHAIN_HEADER"]
		if len(headerList) >= 1:
			return headerList[0]
		else:
			return None
PRESET_VERSION = 3#To be changed when there are changes to chain object variables

def saveAsPreset(selection,presetName):
	if len(selection) == 1:
		activeObj = selection[0]
		chainObjType = activeObj.get("TYPE",None)
		if not re.search(r'^[\w,\s-]+\.[A-Za-z]{3}$',presetName) and not ".." in presetName:#Check that the preset name contains no invalid characters for a file name
			presetDict = {}
			folderPath = None
			variableList = []
			presetDict["presetVersion"] = PRESET_VERSION
			if chainObjType == "RE_CHAIN_WINDSETTINGS":
				folderPath = "WindSettings"
				presetDict["presetType"] = "RE_CHAIN_WINDSETTINGS"
				variableList = activeObj.re_chain_windsettings.items()
					
			elif chainObjType == "RE_CHAIN_CHAINSETTINGS":
				folderPath = "ChainSettings"
				presetDict["presetType"] = "RE_CHAIN_CHAINSETTINGS"
				variableList = activeObj.re_chain_chainsettings.items()
					
			elif chainObjType == "RE_CHAIN_CHAINGROUP":
				folderPath = "ChainGroup"
				presetDict["presetType"] = "RE_CHAIN_CHAINGROUP"
				variableList = activeObj.re_chain_chaingroup.items()
					
			elif chainObjType == "RE_CHAIN_NODE":
				folderPath = "ChainNode"
				presetDict["presetType"] = "RE_CHAIN_NODE"
				variableList = activeObj.re_chain_chainnode.items()
			else:
				showErrorMessageBox("Selected object can not be made into a preset.")
			
			if variableList != []:
				for key, value in variableList:
					if type(value).__name__ == "IDPropertyArray":
						
						presetDict[key] = value.to_list()
					else:
						presetDict[key] = value
				
				#Find chain header in scene and get the version
				chainHeader = findHeaderObj()
				if chainHeader != None:
					presetDict["chainVersion"] = chainHeader.re_chain_header.version
				presetDict["presetVersion"] = PRESET_VERSION
				jsonPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets",folderPath,presetName+".json")
				#print(presetDict)#debug
				try:
					os.makedirs(os.path.split(jsonPath)[0])
				except:
					pass
				with open(jsonPath, 'w', encoding='utf-8') as f:
					json.dump(presetDict, f, ensure_ascii=False, indent=4)
					print(textColors.OKGREEN+"Saved preset to " + str(jsonPath) + textColors.ENDC)
					return True
		else:
			showErrorMessageBox("Invalid preset file name. ")
	else:
		showErrorMessageBox("A chain object must be selected when saving a preset.")
		

def readPresetJSON(filepath,activeObj):
		try:
			with open(filepath) as jsonFile:
				jsonDict = json.load(jsonFile)
				if jsonDict["presetVersion"] > PRESET_VERSION:
					showErrorMessageBox("Preset was created in a newer version and cannot be used. Update to the latest version of the chain importer.")
					return False
				
		except Exception as err:
			showErrorMessageBox("Failed to read json file. \n" + str(err))
			return False
		
		if jsonDict["presetType"] != activeObj.get("TYPE",None):
			showErrorMessageBox("Preset type does not match selected object")
			return False
		propertyGroup = {}
		if jsonDict["presetType"] == "RE_CHAIN_WINDSETTINGS":
			propertyGroup = activeObj.re_chain_windsettings
				
		elif jsonDict["presetType"] == "RE_CHAIN_CHAINSETTINGS":
			propertyGroup = activeObj.re_chain_chainsettings
				
		elif jsonDict["presetType"] == "RE_CHAIN_CHAINGROUP":
			propertyGroup = activeObj.re_chain_chaingroup
				
		elif jsonDict["presetType"] == "RE_CHAIN_NODE":
			propertyGroup = activeObj.re_chain_chainnode
		else:
			showErrorMessageBox("Preset type is not supported")
			return False
		print("Applying preset to " + activeObj.name)
		chainVersion = jsonDict.get("chainVersion",None)
		if chainVersion != None:
			#Find chain header in scene and get the version
			chainHeader = findHeaderObj()
			if chainHeader != None:
				if chainVersion != chainHeader.re_chain_header.version:
					raiseWarning("Preset was created for chain version " + str(chainVersion)+ " while the current file is version " +str(chainHeader.re_chain_header.version)+".")
			else:
				raiseWarning("No chain header in scene, can't compare preset chain version to current file.")
		else:
			raiseWarning("Preset is missing the chain version.")
		for key in propertyGroup.keys():
			
			try:
				propertyGroup[key] = jsonDict[key]
			except:
				raiseWarning("Preset is missing key " + str(key) +", cannot set value on active object.")
		return True
def reloadPresets(folderPath):
	presetsPath = os.path.join(os.path.dirname(os.path.split(os.path.abspath(__file__))[0]),"Presets")
	presetList = []
	relPathStart = os.path.join(presetsPath,folderPath)
	if os.path.exists(relPathStart):
		for entry in os.scandir(relPathStart):
			if entry.name.endswith(".json") and entry.is_file():
				presetList.append((os.path.relpath(os.path.join(relPathStart,entry),start = presetsPath),os.path.splitext(entry.name)[0],""))
	#print("Loading " + folderPath + " presets...")
	#print("DEBUG:" + str(presetList)+"\n")#debug
	return presetList