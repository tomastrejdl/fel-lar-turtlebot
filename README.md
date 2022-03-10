# fel-lar-turtlebot


## Robot tutorial
https://gitlab.fel.cvut.cz/robolab/lar/-/blob/master/README.md

## Robot documentation
https://gitlab.fel.cvut.cz/robolab/robolab_turtlebot

## 1. Connect to robot

```sh
# from lab computer
ssh -X [username]@[turtleName]

# from personal linux computer connected to lab wifi
ssh -X [username]@[turtleIP]
```

## 2. Enter singularity

```sh
# mount local partition, this might result in error if already mounted
mount /local

singularity shell /local/robolab_lar_noetic_2022.simg
```

## 3. Source ROS environment

```sh
source /opt/ros/lar/setup.bash
```

## 4. Start robot driver

```sh
roslaunch robolab_turtlebot bringup_realsense_D435.launch
````


## 5. Start app

```sh
python3 <file>.py
```
