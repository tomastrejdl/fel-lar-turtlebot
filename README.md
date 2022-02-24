# fel-lar-turtlebot

## 1. Connect to robot

```sh
# from lab computer
ssh -X [username]@[turtleName]

# from personal linux computer connected to lab wifi
ssh -X [username]@[turtleIP]
```

## 2. Enter singularity

```sh
singularity shell /opt/singularity/robolab/robolab_noetic_2022-02-24
```

## 3. Source ROS environment

```sh
source /opt/ros/lar/setup.bash
```

## 4. Start robot driver

```sh
roslaunch robolab_turtlebot bringup_realsense_D435.launch
```


## 5. Start app

```sh
python3 <file>.py
```