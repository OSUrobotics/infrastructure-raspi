# infrastructure-raspi Template
## Overview
Contains branches for each apparatus that includes the hardware source code, a ROS node for controlling the apparatus within the infrastructure system, and [urdf](https://github.com/OSUrobotics/infrastructure-raspi/tree/main/infrastructure_raspi/urdf) as well as [STL](https://github.com/OSUrobotics/infrastructure-raspi/tree/main/infrastructure_raspi/meshes) files for visualizing the apparatus (if applicable). 

The _main_ branch contains a template of how to set up a branch for an apparatus (see [template_controller.py](https://github.com/OSUrobotics/infrastructure-raspi/blob/main/infrastructure_raspi/src/template_controller.py)). The [apparatus](https://github.com/OSUrobotics/infrastructure-raspi/tree/main/infrastructure_raspi/src/apparatus) folder should contain all of the hardware source code.

## infrastructure_raspi Package Interface

__Note:__ depending on how the controller node is set up for the apparatus, it may have additional publishers/subscribers. Be sure to look at the README.md in the specific apparatus branch.

### Action Servers:
- __set_test_parameters__
  - Action server that the _Set Test Parameters_ parameter action client sends a goal to.
  - Used to signal start of a trial. Runs any hardware code necessary for getting the apparatus ready for a trial. Sends result when hardware code has either finished executing or failed.
- __reset_hardware__
  - Action server that the _Reset_ stage action client sends a goal to.
  - Used to signal end of a trial. Runs any hardware code necessary for resetting the apparatus after a trial. Sends result when hardware code has either finished executing or failed.
### Services:
- None
### Publishers:
- None
### Subscribers:
- None
### Topics:
- /set_test_parameters/cancel
- /set_test_parameters/feedback
- /set_test_parameters/goal
- /set_test_parameters/result
- /set_test_parameters/status
- /reset_hardware/cancel
- /reset_hardware/feedback
- /reset_hardware/goal
- /reset_hardware/result
- /reset_hardware/status
