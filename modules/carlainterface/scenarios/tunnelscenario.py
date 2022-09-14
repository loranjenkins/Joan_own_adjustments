
from .scenario import Scenario
from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess


import numpy as np
import shapely.affinity
import shapely.geometry
import shapely.ops


class TunnelScenario(Scenario):
    """
    A simple example scenario that checks if a keyboard is added to hardware manager and print a message if this is True. It shows how:
        1) a statement can be checked
        2) some code can be executed once, if True
        3) how other modules can be accessed from a scenario

    """
    def __init__(self):
        super().__init__()

        self.inside_tunnel_agent1 = True
        self.inside_tunnel_agent2 = True
        self.stop_signal_was_sent = False
        self.approach_angle_vehicle1 = 135 #this is mirrored in unreal
        self.approach_angle_vehicle2 = 45
        self.vehicle_width = (2 / 2) * 1.3 #+30% overlap
        self.vehicle_length = (4.7 / 2) * 1.3 #+30% overlap

    def do_function(self, carla_interface_process: CarlaInterfaceProcess):

        agent_1 = carla_interface_process.agent_objects['Ego Vehicle_1']
        agent_2 = carla_interface_process.agent_objects['Ego Vehicle_2']

        ##cruise control in tunnel agent 1
        if self.inside_tunnel_agent1:
            try:
                carla_interface_process.agent_objects['Ego Vehicle_1']
            except KeyError:
                pass

            agent_1 = carla_interface_process.agent_objects['Ego Vehicle_1']
            # print('%.2f' % agent_1.shared_variables.transform[0:3][1])

            if agent_1.shared_variables.transform[0:3][1] > 89: #or 100 or own map
                # turn off auto pilot here
                agent_1.shared_variables.cruise_control_active = False
                print('Auto pilot is off')
                self.inside_tunnel_agent1 = False

            if agent_1.shared_variables.transform[0:3][1] < -89: #or 100 or own map
                # turn off auto pilot here
                agent_1.shared_variables.cruise_control_active = False
                print('Auto pilot is off')
                self.inside_tunnel_agent1 = False


        #terminate process agent 1
        if agent_1.shared_variables.transform[0:3][1] > 400. and not self.stop_signal_was_sent:
            carla_interface_process.pipe_comm.send({"stop_all_modules": True})
            print('Trail is over')
            self.stop_signal_was_sent = True

        if agent_1.shared_variables.transform[0:3][1] < -400. and not self.stop_signal_was_sent:
            carla_interface_process.pipe_comm.send({"stop_all_modules": True})
            print('Trial is over')
            self.stop_signal_was_sent = True


        ##cruise control in tunnel agent 2
        if self.inside_tunnel_agent2:
            try:
                carla_interface_process.agent_objects['Ego Vehicle_2']
            except KeyError:
                pass

            agent_2 = carla_interface_process.agent_objects['Ego Vehicle_2']
            # print('%.2f' % agent_2.shared_variables.transform[0:3][0])

            if agent_2.shared_variables.transform[0:3][1] > 89.: #or 100 or own map
                # turn off auto pilot here
                agent_2.shared_variables.cruise_control_active = False
                print('Auto pilot is off')
                self.inside_tunnel_agent2 = False

            if agent_2.shared_variables.transform[0:3][1] < -89.: #or 100 or own map
                # turn off auto pilot here
                agent_2.shared_variables.cruise_control_active = False
                print('Auto pilot is off')
                self.inside_tunnel_agent2 = False

        # terminate process agent 2
        if agent_2.shared_variables.transform[0:3][1] > 400. and not self.stop_signal_was_sent:
            carla_interface_process.pipe_comm.send({"stop_all_modules": True})
            print('Trial is over')
            self.stop_signal_was_sent = True

        if agent_2.shared_variables.transform[0:3][1] < -400. and not self.stop_signal_was_sent:
            carla_interface_process.pipe_comm.send({"stop_all_modules": True})
            print('Trial is over')
            self.stop_signal_was_sent = True


        #Check for collisons
        vehicle_1 = shapely.geometry.box(-self.vehicle_width, -self.vehicle_length, self.vehicle_width, self.vehicle_length)
        vehicle_2 = shapely.geometry.box(-self.vehicle_width, -self.vehicle_length, self.vehicle_width, self.vehicle_length)

        if agent_1.shared_variables.transform[0:3][1] <= 250:
            vehicle_1 = shapely.affinity.rotate(vehicle_1, self.approach_angle_vehicle1, use_radians=True)
        if agent_2.shared_variables.transform[0:3][1] <= 250:
            vehicle_2 = shapely.affinity.rotate(vehicle_2, self.approach_angle_vehicle2, use_radians=True)

        vehicle_1 = shapely.affinity.translate(vehicle_1, agent_1.shared_variables.transform[0:3][0], agent_1.shared_variables.transform[0:3][1])
        vehicle_2 = shapely.affinity.translate(vehicle_2, agent_2.shared_variables.transform[0:3][0], agent_2.shared_variables.transform[0:3][1])

        check_for_intersection = vehicle_1.intersection(vehicle_2)

        if check_for_intersection.is_empty:
            return None
        if not check_for_intersection.is_empty and not self.stop_signal_was_sent:
            carla_interface_process.pipe_comm.send({"stop_all_modules": True})
            print('Collision occured')
            self.stop_signal_was_sent = True

    @property
    def name(self):
        return 'Tunnel scenario'
