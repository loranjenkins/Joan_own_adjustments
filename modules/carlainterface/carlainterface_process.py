import glob
import os
import sys
import time
import platform

from core.module_process import ModuleProcess
from core.statesenum import State
from modules.carlainterface.carlainterface_agenttypes import AgentTypes
from modules.joanmodules import JOANModules
from core.exceptionhook import exception_log_and_kill_hook
if platform.system() == 'Windows':
    import wres

try:
    sys.path.append(glob.glob('carla_pythonapi/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
    import carla
except IndexError as inst:
    print("CarlaAPI could not be loaded:", inst)


class CarlaInterfaceProcess(ModuleProcess):

    def __init__(self, module: JOANModules, time_step_in_ms, news, settings, events, settings_singleton):
        super().__init__(module, time_step_in_ms=time_step_in_ms, news=news, settings=settings, events=events, settings_singleton=settings_singleton)

        # it is possible to read from other modules
        # do_while_running NOT WRITE to other modules' news to prevent spaghetti-code
        self.shared_variables_hardware = news.read_news(JOANModules.HARDWARE_MANAGER)
        self.vehicle_blueprint_library = None
        self.spawn_point_objects = None
        self.spawn_points = None
        self.world = None
        self.agent_objects = {}

    def get_ready(self):
        """
        When instantiating the ModuleProcess, the settings ar converted to type di ct
        The super().get_ready() method converts the module_settings back to the appropriate settings object
        """
        # first we make a connection with carla in this multiprocess to get the valid objects we need to spawn our agents
        host = 'localhost'
        port = 2000

        [self.vehicle_blueprint_library, self.spawn_point_objects, self.world, self.spawn_points] = self.connect_carla(host=host, port=port)
        # TODO check whether this is a good idea
        # settings = self.world.get_settings()
        # settings.synchronous_mode = True  # Enables synchronous mode
        # settings.fixed_delta_seconds = 0.01666 # set fixed time steep of 0.05
        # self.world.apply_settings(settings)
        # Now we create our agents and directly spawn them
        for key, value in self._settings_as_object.agents.items():
            self.agent_objects[key] = AgentTypes(value.agent_type).process(self, settings=value, shared_variables=self._module_shared_variables.agents[key])

    def run(self):
        """
        Run function, starts once start() is called.
        Note: anything you created in __init__ and you want to use in run() needs to be picklable. Failing the 'picklable' requirement will result in errors.
        If you need to use an object from __init__ that is not picklable, see if you can translate your object into something
        picklable (lists, dicts, primitives etc) and create a new object in here. Example: settings in get_ready. This function is overwritten in carlainterface
        because we need to be able to destroy our actors in the READY state as well as in the RUNNING state
        :return:
        """
        try:
            self._get_ready()

            self._events.start.wait()

            # run
            if platform.system() == 'Windows':
                with wres.set_resolution(10000):
                    self._run_loop()

                    if self._module_shared_variables.state == State.STOPPED.value:
                        self.destroy_agents()
            else:
                self._run_loop()
        except:
            # sys.excepthook is not called from within processes so can't be overridden. instead, catch all exceptions here and call the new excepthook manually
            exception_log_and_kill_hook(*sys.exc_info(), self.module, self._events.exception)


    def destroy_agents(self):
        for agents in self.agent_objects:
            self.agent_objects[agents].destroy()

    def do_while_running(self):
        """
        do_while_running something and write the result in a shared_variable
        """
        self.world.tick()
        for agents in self.agent_objects:
            # will perform the mp input class for eaach available input
            self.agent_objects[agents].do()

        if self._module_shared_variables.state == State.STOPPED.value:
            for agents in self.agent_objects:
                self.agent_objects[agents].destroy()

    def connect_carla(self, host, port):
        "We also want a connection to carla in our multiprocess therefore we need this function here"
        vehicle_tags = []
        spawn_points = []
        client = carla.Client(host, port)  # connecting to server
        client.set_timeout(2.0)
        time.sleep(2)
        world = client.get_world()  # get world object (contains everything)
        blueprint_library = world.get_blueprint_library()
        vehicle_bp_library = blueprint_library.filter('vehicle.*')
        for items in vehicle_bp_library:
            vehicle_tags.append(items.id[8:])
        world_map = world.get_map()
        spawn_point_objects = world_map.get_spawn_points()
        for item in spawn_point_objects:
            spawn_points.append("Spawnpoint " + str(spawn_point_objects.index(item)))

        return vehicle_bp_library, spawn_point_objects, world, spawn_points
