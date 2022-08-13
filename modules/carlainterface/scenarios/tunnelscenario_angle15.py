from core.hq.hq_manager import HQManager
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
        self.stop_signal_was_sent = False

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

            if agent_1.shared_variables.transform[0:3][1] < -134: #or 100 or own map
                # turn off auto pilot here
                agent_1.shared_variables.cruise_control_active = False
                print('Auto pilot is off')
                self.inside_tunnel_agent1 = False

            if agent_1.shared_variables.transform[0:3][1] > 134: #or 100 or own map
                # turn off auto pilot here
                agent_1.shared_variables.cruise_control_active = False
                print('Auto pilot is off')
                self.inside_tunnel_agent1 = False


        #terminate process agent 1
        if agent_1.shared_variables.transform[0:3][1] < -450. and not self.stop_signal_was_sent:
            carla_interface_process.pipe_comm.send({"stop_all_modules": True})
            print('Trail is over')
            self.stop_signal_was_sent = True

        if agent_1.shared_variables.transform[0:3][1] > 450. and not self.stop_signal_was_sent:
            carla_interface_process.pipe_comm.send({"stop_all_modules": True})
            print('Trail is over')
            self.stop_signal_was_sent = True


        ##cruise control in tunnel agent 2
        if self.inside_tunnel_agent2:
            try:
                carla_interface_process.agent_objects['Ego Vehicle_2']
            except KeyError:
                pass

            agent_2 = carla_interface_process.agent_objects['Ego Vehicle_2']
            # print('%.2f' % agent_2.shared_variables.transform[0:3][0])

            if agent_2.shared_variables.transform[0:3][1] < -134.: #or 100 or own map
                # turn off auto pilot here
                agent_2.shared_variables.cruise_control_active = False
                print('Auto pilot is off')
                self.inside_tunnel_agent2 = False

            if agent_2.shared_variables.transform[0:3][1] > 134.: #or 100 or own map
                # turn off auto pilot here
                agent_2.shared_variables.cruise_control_active = False
                print('Auto pilot is off')
                self.inside_tunnel_agent2 = False

        # terminate process agent 2
        if agent_2.shared_variables.transform[0:3][1] < -450. and not self.stop_signal_was_sent:
            carla_interface_process.pipe_comm.send({"stop_all_modules": True})
            print('Trail is over')
            self.stop_signal_was_sent = True

        if agent_2.shared_variables.transform[0:3][1] > 450. and not self.stop_signal_was_sent:
            carla_interface_process.pipe_comm.send({"stop_all_modules": True})
            print('Trail is over')
            self.stop_signal_was_sent = True



    @property
    def name(self):
        return 'Tunnel scenario'
