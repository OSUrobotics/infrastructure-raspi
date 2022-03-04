# infrastructure-raspi
## Overview
Contains branches for each apparatus that includes the hardware source code, a ROS node for controlling the apparatus within the infrastructure system, and urdf models for visualizing the apparatus (if applicable). 

The _main_ branch contains a template of how to set up a branch for an apparatus. The [apparatus]() folder should contain all of the hardware source code. 

## infrastructure_raspi Package Interface
### Action Servers:
- __start_arm_sequence__
  - Action server that the _User Arm Control_ stage action client sends a goal to.
  - Used to signal start of arm control. Sends result once arm control has finished
### Services:
- None
### Publishers:
- None
### Subscribers:
- None
### Topics:
- /start_arm_sequence/cancel
- /start_arm_sequence/feedback
- /start_arm_sequence/goal
- /start_arm_sequence/result
- /start_arm_sequence/status
