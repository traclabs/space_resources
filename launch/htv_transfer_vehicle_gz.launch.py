from launch import LaunchDescription
from launch.actions import SetEnvironmentVariable, IncludeLaunchDescription, DeclareLaunchArgument
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.actions import Node, SetParameter
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition, UnlessCondition

from ament_index_python.packages import get_package_share_directory

import os
import xacro


def generate_launch_description():

  launch_args = [
    DeclareLaunchArgument(name="gz_gui", default_value="True"),
    DeclareLaunchArgument(name="rviz", default_value="True"),
  ]

  pkg_dir = get_package_share_directory("space_resources")
  
  # World
  world_sdf = os.path.join(pkg_dir, "worlds/htv_simple.sdf")

  # Launch gazebo world
  gz_launch_gui = IncludeLaunchDescription(
    PathJoinSubstitution([FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]),
    launch_arguments=[
      ("gz_args", [
          world_sdf,
          " -r",
          " -v 4",
      ])
    ],
    condition=IfCondition(LaunchConfiguration('gz_gui'))
  )

  # Launch gazebo world
  gz_launch_headless = IncludeLaunchDescription(
    PathJoinSubstitution([FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]),
    launch_arguments=[
      ("gz_args", [
          world_sdf,
          " -r",
          " -v 4",
          " -s"
      ])
    ],
    condition=UnlessCondition(LaunchConfiguration('gz_gui'))
  )

  # Spawn HTV
  spawn_htv = IncludeLaunchDescription(
    PathJoinSubstitution([
      FindPackageShare("space_resources"), "launch", "spawn_htv_transfer_vehicle.launch.py"
    ])
  )

  # Make the /clock topic available in ROS
  gz_sim_bridge = Node(
    package="ros_gz_bridge",
    executable="parameter_bridge",
    arguments=[
      "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
    ],
    output="screen",
  )
  
  # Rviz
  rviz_config = os.path.join(pkg_dir, "rviz/htv_transfer_vehicle.rviz")
  rviz = Node(
      package="rviz2",
      executable="rviz2",
      name="rviz2",
      output="log",
      arguments=["-d", rviz_config],
      parameters=[
      {"use_sim_time": True}
      ],
      condition=IfCondition(LaunchConfiguration('rviz'))
  )  

  return LaunchDescription(
    launch_args + 
    [
      gz_launch_gui,
      gz_launch_headless,
      spawn_htv,
      gz_sim_bridge,
      rviz
    ])
