# Copyright 2021 the Autoware Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Co-developed by Tier IV, Inc. and Apex.AI, Inc.


from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, EmitEvent,
                            RegisterEventHandler)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessStart
from launch.events import matches_action
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition


def generate_launch_description():
    pe_ars408_node = LifecycleNode(
        package='pe_ars408_ros',
        executable='pe_ars408_node',
        name='pe_ars408_node',
        namespace=TextSubstitution(text=''),
        parameters=[{
            'interface': LaunchConfiguration('interface'),
            'enable_can_fd': LaunchConfiguration('enable_can_fd'),
            'interval_sec':
            LaunchConfiguration('interval_sec'),
            'filters': LaunchConfiguration('filters'),
            'use_bus_time': LaunchConfiguration('use_bus_time'),
            'publish_radar_track': LaunchConfiguration('publish_radar_track'),
            'publish_radar_scan': LaunchConfiguration('publish_radar_scan'),
            'output_frame': LaunchConfiguration('output_frame'),
            'sequential_publish': LaunchConfiguration('sequential_publish'),
            'size_x': LaunchConfiguration('size_x'),
            'size_y': LaunchConfiguration('size_y'),
        }],
        remappings=[('from_can_bus', LaunchConfiguration('from_can_bus_topic')),
                    ('~/input/frame', LaunchConfiguration('input/frame')),
                    ('~/output/objects', LaunchConfiguration('output/objects')),
                    ('~/output/scan', LaunchConfiguration('output/scan'))],
        output='screen')

    pe_ars408_configure_event_handler = RegisterEventHandler(
        event_handler=OnProcessStart(
            target_action=pe_ars408_node,
            on_start=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(pe_ars408_node),
                        transition_id=Transition.TRANSITION_CONFIGURE,
                    ),
                ),
            ],
        ),
        condition=IfCondition(LaunchConfiguration('auto_configure')),
    )

    pe_ars408_activate_event_handler = RegisterEventHandler(
        event_handler=OnStateTransition(
            target_lifecycle_node=pe_ars408_node,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(pe_ars408_node),
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    ),
                ),
            ],
        ),
        condition=IfCondition(LaunchConfiguration('auto_activate')),
    )

    return LaunchDescription([
        DeclareLaunchArgument('interface', default_value='can0'),
        DeclareLaunchArgument('enable_can_fd', default_value='false'),
        DeclareLaunchArgument('interval_sec', default_value='0.01'),
        DeclareLaunchArgument('use_bus_time', default_value='false'),
        DeclareLaunchArgument('filters', default_value='0:0',
                              description='Comma separated filters can be specified for each given'
                                          ' CAN interface.\n'
                                          '\t<can_id>:<can_mask>\n'
                                          '\t\t(matches when <received_can_id> & mask == can_id & '
                                          'mask)\n'
                                          '\t<can_id>~<can_mask>\n'
                                          '\t\t(matches when <received_can_id> & mask != can_id & '
                                          'mask)\n'
                                          '\t#<error_mask>\n'
                                          '\t\t(set error frame filter, see include/linux/can/'
                                          'error.h)\n'
                                          '\t[j|J]\n'
                                          '\t\t(join the given CAN filters - logical AND '
                                          'semantic)\n\n'
                                          '\tCAN IDs, masks and data content are given and '
                                          'expected in hexadecimal values. When can_id and '
                                          'can_mask are both 8 digits, they are assumed to '
                                          "be 29 bit EFF. '0:0' default filter will accept "
                                          'all data frames.\n'
                                          '\tFor more information about syntax check: '
                                          'https://manpages.ubuntu.com/manpages/jammy/'
                                          'man1/candump.1.html'),
        DeclareLaunchArgument('auto_configure', default_value='true'),
        DeclareLaunchArgument('auto_activate', default_value='true'),
        DeclareLaunchArgument('from_can_bus_topic', default_value='from_can_bus'),
        DeclareLaunchArgument('input/frame', default_value='/sensing/radar/can_tx'),
        DeclareLaunchArgument('output/objects', default_value='objects_raw'),
        DeclareLaunchArgument('output/scan', default_value='scan'),
        DeclareLaunchArgument('output_frame', default_value='ars408'),
        DeclareLaunchArgument('publish_radar_track', default_value='true'),
        DeclareLaunchArgument('publish_radar_scan', default_value='false'),
        DeclareLaunchArgument('sequential_publish', default_value='false'),
        DeclareLaunchArgument('size_x', default_value='1.8'),
        DeclareLaunchArgument('size_y', default_value='1.8'),
        pe_ars408_node,
        pe_ars408_configure_event_handler,
        pe_ars408_activate_event_handler,
    ])
