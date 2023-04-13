
# RE-Chain-Editor

This addon allows for importing and exporting of RE Engine chain (physics bone) files from Blender.

![Blender Preview](https://user-images.githubusercontent.com/46909075/219907729-70494035-68e8-419b-a000-58503fd7727f.png)

## Features
 - Allows for importing and exporting of RE Engine chain files.
 - Can create new chain files entirely within Blender.
 - Presets of chain configurations can be saved and shared.
 
 ## Change Log
### V3 - 4/13/2023

If you are updating to V3, uncheck RE Chain Editor in the addons menu and restart Blender before installing the new version.

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
 
 ## Supported Games
 - **Monster Hunter Rise: Sunbreak**
 - **Resident Evil 2 Remake**
 - **Resident Evil 3 Remake**
 - **Resident Evil 4 Remake**
 - **Resident Evil 8**
 - **Devil May Cry 5**
 - **Street Fighter 6 Beta**
 
Support for more games may be added in the future.

## Requirements
* [Blender 2.8 or higher (version 2.93.0 recommended)](https://www.blender.org/download/)
* [Blender RE Mesh Noesis Wrapper](https://github.com/NSACloud/Blender-RE-Mesh-Noesis-Wrapper)

## Installation
Download the addon by clicking Code > Download Zip.

In Blender, go to Edit > Preferences > Addons, then click "Install" in the top right.

Navigate to the downloaded zip file for this addon and click "Install Addon". The addon should then be usable.

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
- [AlphaZomega](https://github.com/alphazolam/RE-Chain-Editor) - RE Chain 010 Template, Modified this addon to work in all games and other bugfixes/additions
