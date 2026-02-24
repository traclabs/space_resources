from launch import LaunchDescription
from launch.actions import RegisterEventHandler, DeclareLaunchArgument, OpaqueFunction, IncludeLaunchDescription
from launch_ros.actions import Node, SetParameter
from launch.event_handlers import OnProcessExit
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import PathJoinSubstitution, LaunchConfiguration
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory

import os
import xacro

def evaluate_rsp(context, *args, **kwargs):

  x = LaunchConfiguration("x").perform(context)
  y = LaunchConfiguration("y").perform(context)
  z = LaunchConfiguration("z").perform(context)
  roll = LaunchConfiguration("roll").perform(context)
  pitch = LaunchConfiguration("pitch").perform(context)
  yaw = LaunchConfiguration("yaw").perform(context)
    

  htv_urdf_path = os.path.join(get_package_share_directory("space_resources"), "models", 
                  "htv_transfer_vehicle", "urdf", "htv1.urdf.xacro")
  htv_mappings = {
      'x' : x,
      'y' : y,
      'z' : z,
      'R' : roll,
      'P' : pitch,
      'Y' : yaw,                        
  }
  htv_doc = xacro.process_file(htv_urdf_path, mappings=htv_mappings)
  htv_urdf_content = htv_doc.toprettyxml(indent="  ")
      
  htv_robot_state_publisher = Node(
      package="robot_state_publisher",
      executable="robot_state_publisher",
      name="htv_robot_state_publisher",
      output="screen",
      parameters=[
        {"robot_description": htv_urdf_content},
        {"use_sim_time": True},
      ],
      remappings=[('/robot_description', '/htv/robot_description')],
      condition=IfCondition(LaunchConfiguration('spawn_urdf'))
  )
      
  return [htv_robot_state_publisher]


def generate_launch_description():

  launch_args = [
    DeclareLaunchArgument(name="spawn_urdf", default_value="True"),
    DeclareLaunchArgument(name="x", default_value="0.0"),
    DeclareLaunchArgument(name="y", default_value="0.0"),
    DeclareLaunchArgument(name="z", default_value="0.0"),
    DeclareLaunchArgument(name="roll", default_value="0.0"),
    DeclareLaunchArgument(name="pitch", default_value="0.0"),
    DeclareLaunchArgument(name="yaw", default_value="0.0"),                    
    DeclareLaunchArgument(name="world_name", default_value="default"), 
  ]

  # HTV -- Spawn from URDF
  htv_rsp=OpaqueFunction(function=evaluate_rsp)
   
  spawn_htv_urdf = Node(
      package="ros_gz_sim",
      executable="create",
      name="spawn",
      output="screen",
      arguments=[
        "-topic",
        "/htv/robot_description",
        "-name", "htv",
        "-allow_renaming", "true",
      ],
      condition=IfCondition(LaunchConfiguration('spawn_urdf'))
  ) 
 

  # HTV -- Spawn from SDF
  htv_sdf = os.path.join(get_package_share_directory("space_resources"), "models", "htv_transport_vehicle", "model.sdf")  
  spawn_htv_sdf = IncludeLaunchDescription(
    PathJoinSubstitution([FindPackageShare("ros_gz_sim"), "launch", "gz_spawn_model.launch.py"]),
    launch_arguments={"world": LaunchConfiguration("world_name"),
    "file": htv_sdf,
    "entity_name": "htv",
    "x": LaunchConfiguration("x"),
    "y": LaunchConfiguration("y"),
    "z": LaunchConfiguration("z"),
    "R": LaunchConfiguration("roll"),
    "P": LaunchConfiguration("pitch"),
    "Y": LaunchConfiguration("yaw")        
    }.items(),
    condition=UnlessCondition(LaunchConfiguration('spawn_urdf'))
  )

  return LaunchDescription( launch_args + [
    htv_rsp,
    spawn_htv_urdf,
    spawn_htv_sdf    
  ])
