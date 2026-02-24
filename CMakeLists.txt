cmake_minimum_required(VERSION 3.16.3)
project(space_resources)

add_compile_options(-std=c++17)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rviz_rendering REQUIRED)

# Adds shallow folders containing ogre_media such as meshes and scripts to Rviz
# so that they can be found at runtime. Requires rviz_rendering.
#register_rviz_ogre_media_exports(
#    DIRECTORIES
#    "meshes"
#  )


set(DEPS
  rclcpp
  rclpy
  geometry_msgs
  std_msgs
  std_srvs
)

foreach(dependency IN ITEMS ${DEPS})
  find_package(${dependency} REQUIRED)
endforeach()


#############
## Install ##
#############

#install(PROGRAMS
#  scripts/move_mss
#  scripts/move_sun.py
#  DESTINATION lib/${PROJECT_NAME}
#)

#install(DIRECTORY include/
#  DESTINATION include/
#)

install(
  DIRECTORY
  launch rviz worlds models launch
  DESTINATION share/${PROJECT_NAME}
)

ament_environment_hooks("${CMAKE_CURRENT_SOURCE_DIR}/hooks/${PROJECT_NAME}.dsv.in")

ament_export_dependencies(${THIS_PACKAGE_INCLUDE_DEPENDS})

ament_package()
