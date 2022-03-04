# infrastructure-raspi
## Overview
Contains branches for each apparatus that includes the hardware source code, a ROS node for controlling the apparatus within the infrastructure system, and urdf models for visualizing the apparatus (if applicable). 

The _main_ branch contains a template of how to set up a branch for an apparatus (see [template_controller.py](https://github.com/OSUrobotics/infrastructure-raspi/blob/main/infrastructure_raspi/src/template_controller.py)). The [apparatus](https://github.com/OSUrobotics/infrastructure-raspi/tree/main/infrastructure_raspi/src/apparatus) folder should contain all of the hardware source code.

## infrastructure_raspi Package Interface

__Note:__ depending on how the controller node is set up for the apparatus, it may have additional publishers/subscribers. Be sure to look at the README.md in the specific apparatus branch.

### Action Servers:
- __set_test_parameters__
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
