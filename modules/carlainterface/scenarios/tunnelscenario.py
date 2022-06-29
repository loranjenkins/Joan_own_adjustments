from .scenario import Scenario
from modules.carlainterface.carlainterface_process import CarlaInterfaceProcess


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

    def do_function(self, carla_interface_process: CarlaInterfaceProcess):
        agent_1 = carla_interface_process.agent_objects['Ego Vehicle_1']
        print('%.2f' % agent_1.shared_variables.transform[0:3][0])
        print('%.2f' % agent_1.shared_variables.transform[0:3][1])

        ##cruise control in tunnel agent 1
        if self.inside_tunnel_agent1:
            try:
                carla_interface_process.agent_objects['Ego Vehicle_1']
            except KeyError:
                pass

            agent_1 = carla_interface_process.agent_objects['Ego Vehicle_1']
            # print('%.2f' % agent_1.shared_variables.transform[0:3][0])


            #
            # if agent_1.shared_variables.transform[0:3][0] < 22: #or 100 or own map
            #     # turn off auto pilot here
            #     agent_1.shared_variables.cruise_control_active = False
            #     print('Auto pilot is off')
            #     self.inside_tunnel_agent1 = False

        ## check if agenta collide
        # ego_agent_key = 'Ego Vehicle_1'
        # ego_vehicle = carla_interface_process.agent_objects[ego_agent_key]
        # if ego_vehicle.spawned_vehicle.destroy():
        #     carla_interface_process.pipe_comm.send({"stop_all_modules": True})


        # ## Stop a trail agent1
        # agent_1 = carla_interface_process.agent_objects['Ego Vehicle_1']
        # # print('%.2f' % agent_1.shared_variables.transform[0:3][0])
        #
        # if agent_1.shared_variables.transform[0:3][0] <= -1000.:
        #     carla_interface_process.pipe_comm.send({"stop_all_modules": True})
        #     print('Trail is over')

        #
        # ##cruise control in tunnel agent 2
        # if self.inside_tunnel_agent2:
        #     try:
        #         carla_interface_process.agent_objects['Ego Vehicle_2']
        #     except KeyError:
        #         pass
        #
        #     agent_2 = carla_interface_process.agent_objects['Ego Vehicle_2']
        #     # print('%.2f' % agent_2.shared_variables.transform[0:3][0])
        #
        #     if agent_2.shared_variables.transform[0:3][0] < -350.: #or 100 or own map
        #         # turn off auto pilot here
        #         agent_2.shared_variables.cruise_control_active = False
        #         print('Auto pilot is off')
        #         self.inside_tunnel_agent2 = False
        #
        # ## Stop a trail agent2
        # agent_2 = carla_interface_process.agent_objects['Ego Vehicle_2']
        # # print('%.2f' % agent_2.shared_variables.transform[0:3][0])
        #
        # if agent_2.shared_variables.transform[0:3][0] <= -400.:
        #     carla_interface_process.pipe_comm.send({"stop_all_modules": True})
        #     print('Trail is over')






    @property
    def name(self):
        return 'Tunnel scenario'
