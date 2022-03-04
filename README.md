# infrastructure-raspi Door
## Overview
Contains hardware source code for the Door, a ROS node for controlling the Door within the infrastructure system, and urdf models for visualizing the Door (TODO). 

The [door_controller](https://github.com/OSUrobotics/infrastructure-raspi/blob/door/infrastructure_raspi/src/door_controller.py) node not only controlls the hardware for the Door, but also publishes the data to the _/hardware_infsensor_ topic as well as record the data in a csv file that's stored in a shared folder (_rem_home/_) between the PI and host machine.
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
- __data_pub__
  - Creates the _/hardware_infsensor_ topic and publishes all of the collected collected Door data. Uses the DoorSensors custom message.
### Subscribers:
- __stop_sleep_sub__
  - Listens to the _/start_data_collection/goal_ topic to know when to stop sleeping and start checking for whether or not it should start collecting and publishing the data from the Door.
  - Used to prevent the node from taking up too much time on the schedular.
- __start_sub__
  - Listens to the _/start_data_collection/result_ topic to know when to start collecting and publishing the data from the Door.
- __stop_sub__
  - Listens to the _/stop_data_collection/result_ topic to know when to stop collecting and publishing the data from the Door.
### Topics:
- /hardware_infsensor
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
