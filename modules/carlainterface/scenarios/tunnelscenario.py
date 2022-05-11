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

        self.agent_1_inside_tunnel = True

    def do_function(self, carla_interface_process: CarlaInterfaceProcess):

        if self.inside_tunnel:
            try:
                carla_interface_process.agent_objects['Ego Vehicle_1']
            except KeyError:
                pass

            agent = carla_interface_process.agent_objects['Ego Vehicle_1']
            print('%.2f' % agent.shared_variables.transform[0:3][0])

            if agent.shared_variables.transform[0:3][0] > 100.:
                # turn off auto pilot here
                agent.shared_variables.cruise_control_active = False
                print('Auto pilot is off')
                self.inside_tunnel = False


    @property
    def name(self):
        return 'Tunnel scenario'
