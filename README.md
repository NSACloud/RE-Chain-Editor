
# RE-Chain-Editor
## Multi-Game Version
This addon allows for importing and exporting of RE Engine chain (physics bone) files from Blender.

![Blender Preview](https://github.com/mhvuze/MonsterHunterRiseModding/blob/main/img/guides/models/REChainEditor/RE_Chain_Editor_Preview.png)
## Features
 - Allows for importing and exporting of RE Engine chain files.
 - Can create new chain files entirely within Blender.
 - Presets of chain configurations can be saved and shared.
 ### Supported Games

 - **Monster Hunter Rise: Sunbreak**
 - **Resident Evil 2 Remake**
 - **Resident Evil 3 Remake**
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
- [AlphaZomega](https://github.com/alphazolam) - RE Chain 010 Template, Modified this addon to work in all games
