cmake_minimum_required(VERSION 3.0.2)
project(kxr_cube_solver)

find_package(catkin REQUIRED COMPONENTS
  roseus
  rospy
  cv_bridge
  sensor_msgs
  message_generation
  std_msgs
)

add_service_files(
  DIRECTORY srv
  FILES SendCommand.srv
)

generate_messages(DEPENDENCIES std_msgs)
