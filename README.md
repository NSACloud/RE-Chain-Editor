
![REChainEditorTitle](https://github.com/NSACloud/RE-Chain-Editor/assets/46909075/e74f6ac0-e7c7-4f26-94af-0cf1ff9e95ee)

This addon allows for importing and exporting of RE Engine chain (physics bone) files from Blender.

![Blender Preview](https://github.com/NSACloud/RE-Chain-Editor/assets/46909075/82f76e5a-cddb-4c09-92e2-2a7cbca97599)

## Features
 - Allows for importing and exporting of RE Engine chain files.
 - Can create new chain files entirely within Blender.
 - Presets of chain configurations can be saved and shared.
 
## Change Log

### V7 - 4/28/2024

* Added RE Toolbox integration. Any chain files exported will be added to RE Toolbox's batch export list.
* Fixed bug with getting the armature object to attach chains to.

<details>
  <summary>Older Version Change Logs</summary>

### V6 - 4/20/2024

If you are updating to V6, uncheck RE Chain Editor in the addons menu and restart Blender before installing the new version.

* Added support for meshes imported with RE Mesh Editor.
* Added addon updater functionality, the addon can now be updated directly from Preferences > Add-ons > RE Chain Editor
* Chains now use collections. This allows for multiple chain files to be in a scene at the same time.
* Added Target Armature import option. This allows you to specify which armature to attach the chain to.
* Added Merge Chain Collection import option. This allows for newly chain files to be merged with an existing chain collection.
* Added Active Chain Collection field to the Object Mode Tools and Pose Mode Tools panels. This determines where newly created chain objects will be assigned.
* Added Chain Collection export option. This allows you to specify which chain collection to export.
* Added Hide Non Collisions option to the Visibility panel.
* Chain collisions can now be moved and scaled like normal objects to set their position and radius. Previously, these would have to be set in collision settings menu.
* The default angle limit orientation for newly created chains has been altered so that the first angle limit points towards the next bone.
* Added Dragon's Dogma 2 support (untested)
* Various bug fixes

### V5 - 9/11/2023

* Fixed an issue where Street Fighter 6 chain settings did not import or export correctly. Any previously imported chains saved in a blend file should be reimported.
* Fixed issue causing crashes with SF6 due to certain data being missing when importing certain chain files.
* Chain collisions now show the bone they're connected to in their name.

NOTE: Due to them containing lots of currently unmapped data, certain SF6 chain files such as Kimberly's cannot be imported without them having issues in game when exported.

### V4 - 4/16/2023

* Added support for RE:Verse.
* Added experimental features under the Pose Mode tools. This allows for things such as chains connected to chains and single bone capsule collisions. Be warned that there is no error checking if you make a mistake. Use at your own risk.
* Minor bug fixes.

### V3 - 4/13/2023

* Added support for Resident Evil 4.
* Moved exporting of all chain versions to a single export menu. Choose which game to export for in the top right when exporting.
 
### V2 - 2/18/2023

If you are updating to V2 from a previous version, any chain files previously saved to Blender have to be reimported.

This is because certain settings have been stored differently compared to the previous version and it will cause issues when exporting.

**New Features:**
* Angle limit orientation is now set automatically when creating new chains. Manual adjustments may still be required at times.
* Chain nodes now have cones to display angle limits.
* In the Object Mode Tools panel, added 2 new buttons for aligning angle limits and setting an angle limit radius ramp across a chain.
* In the Object Mode Visibility panel, added buttons for hiding non chain objects to make selecting things quicker.
* In the Pose Mode Tools panel, added 2 new buttons for renaming bone chains and aligning bone tails to an axis.
* Angle limit object orientations can now be copied and pasted using the clipboard.
* Added support for collision filter file (.cfil) paths to chain settings.
* Added support for collision subdata (For RE2 RT).
* Several minor bug fixes.
 
 </details>
 
 ## Supported Games
 - **Monster Hunter Rise: Sunbreak**
 - **Resident Evil 2 Remake**
 - **Resident Evil 3 Remake**
 - **Resident Evil 4 Remake**
 - **Resident Evil 8**
 - **Devil May Cry 5**
 - **Street Fighter 6**  (Street Fighter 6 is only partially supported at the moment and has issues with certain files.)
 - **Dragon's Dogma 2**
 
Support for more games may be added in the future.

## Requirements
* [Blender 2.8 or higher](https://www.blender.org/download/)
* [RE Mesh Editor](https://github.com/NSACloud/RE-Mesh-Editor)

OR
* [Blender RE Mesh Noesis Wrapper (Deprecated)](https://github.com/NSACloud/Blender-RE-Mesh-Noesis-Wrapper)
## Installation
Download the addon by clicking Code > Download Zip.

In Blender, go to Edit > Preferences > Addons, then click "Install" in the top right.

Navigate to the downloaded zip file for this addon and click "Install Addon". The addon should then be usable.

To update this addon, navigate to Preferences > Add-ons > RE Chain Editor and press the "Check for update" button.

## Usage Guide

The full guide can be found here.

https://github.com/mhvuze/MonsterHunterRiseModding/wiki/Editing-Chains-with-RE-Chain-Editor

**TL;DR Usage Guide**

1. Import a mesh and add bones to be used as physics bones to the armature.
2. Create a chain header, then a chain settings object in the RE Chain tab in Object mode.
3. Switch to pose mode, select the start bone and press "Create Chain From Bone" for each chain.
4. (Optional) Add collisions to bones by selecting a bone and pressing "Create Collision From Bone".
5. Parent the chain group objects to the chain settings objects in the outliner
6. (Optional) Create wind settings and parent the chain settings to it to give it wind effects.
7. Configure chain objects in the Object properties tab, or apply presets
8. Adjust the chain node XYZ angle limits if necessary
9. Export from File > Export > RE Chain

 ## Credits
[Monster Hunter Modding Discord](https://discord.gg/gJwMdhK)
 - [AsteriskAmpersand](https://github.com/AsteriskAmpersand) - Advice and inspiration from CTC Editor
- [Statyk](https://www.youtube.com/channel/UC2nEkiSL_X7xh6QHJcS0Wjw) - Beta testing and feedback
- [AlphaZomega](https://github.com/alphazolam/) - RE Chain 010 Template, Modified this addon to work in all games and other bugfixes/additions
- [CG Cookie](https://github.com/CGCookie) - Addon updater module
