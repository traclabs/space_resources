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

  urdf_path = LaunchConfiguration("urdf_file").perform(context) 
  x = LaunchConfiguration("x").perform(context)
  y = LaunchConfiguration("y").perform(context)
  z = LaunchConfiguration("z").perform(context)
  roll = LaunchConfiguration("roll").perform(context)
  pitch = LaunchConfiguration("pitch").perform(context)
  yaw = LaunchConfiguration("yaw").perform(context)
    

  hdu_mappings = {
      'x' : x,
      'y' : y,
      'z' : z,
      'R' : roll,
      'P' : pitch,
      'Y' : yaw,                        
  }
  hdu_doc = xacro.process_file(urdf_path, mappings=hdu_mappings)
  hdu_urdf_content = hdu_doc.toprettyxml(indent="  ")
      
  hdu_robot_state_publisher = Node(
      package="robot_state_publisher",
      executable="robot_state_publisher",
      name="hdu_robot_state_publisher",
      output="screen",
      parameters=[
        {"robot_description": hdu_urdf_content},
        {"use_sim_time": True},
      ],
      remappings=[('/robot_description', '/hdu/robot_description')],
      condition=IfCondition(LaunchConfiguration('spawn_urdf'))
  )
      
  return [hdu_robot_state_publisher]


def generate_launch_description():

  hdu_urdf_path = os.path.join(get_package_share_directory("space_resources"), "models", 
                  "habitat_demonstration_unit", "urdf", "habitat_demonstration_unit.urdf.xacro")

  launch_args = [
    DeclareLaunchArgument(name="urdf_file", default_value=hdu_urdf_path),
    DeclareLaunchArgument(name="spawn_urdf", default_value="True"),
    DeclareLaunchArgument(name="x", default_value="0.0"),
    DeclareLaunchArgument(name="y", default_value="0.0"),
    DeclareLaunchArgument(name="z", default_value="0.0"),
    DeclareLaunchArgument(name="roll", default_value="0.0"),
    DeclareLaunchArgument(name="pitch", default_value="0.0"),
    DeclareLaunchArgument(name="yaw", default_value="0.0"),                    
    DeclareLaunchArgument(name="world_name", default_value="default"), 
  ]

  # HDU -- Spawn from URDF
  hdu_rsp=OpaqueFunction(function=evaluate_rsp)
   
  spawn_hdu_urdf = Node(
      package="ros_gz_sim",
      executable="create",
      name="spawn",
      output="screen",
      arguments=[
        "-topic",
        "/hdu/robot_description",
        "-name", "hdu",
        "-allow_renaming", "true",
      ],
      condition=IfCondition(LaunchConfiguration('spawn_urdf'))
  ) 
 

  # HDU -- Spawn from SDF
  hdu_sdf = os.path.join(get_package_share_directory("space_resources"), "models", "habitat_demonstration_unit", "model.sdf")  
  spawn_hdu_sdf = IncludeLaunchDescription(
    PathJoinSubstitution([FindPackageShare("ros_gz_sim"), "launch", "gz_spawn_model.launch.py"]),
    launch_arguments={"world": LaunchConfiguration("world_name"),
    "file": hdu_sdf,
    "entity_name": "hdu",
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
    hdu_rsp,
    spawn_hdu_urdf,
    spawn_hdu_sdf    
  ])
