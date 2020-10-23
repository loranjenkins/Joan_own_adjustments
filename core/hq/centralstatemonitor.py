from core.statemachine import StateMachine
from core.statesenum import State
from modules.joanmodules import JOANModules


class CentralStateMonitor:
    """
    Monitors states of all instantiated modules, by registering _state_changed to each module's state machine.
    """
    def __init__(self):
        self._all_state_machines = {}

    def register_state_machine(self, module: JOANModules, state_machine: StateMachine):
        """
        Register to a state machine
        :param module: the module
        :param state_machine:  and the module's state machine
        :return:
        """
        state_machine.add_state_change_listener(lambda: self._state_changed(module, state_machine))
        self._all_state_machines[module] = state_machine

    def _state_changed(self, module: JOANModules, state_machine: StateMachine):
        """
        Called when one of the module's states changes. Checks if a module is in error. If so, request state transition to STOPPED for all modules
        :param module: the module
        :param state_machine:  and the module's state machine
        :return:
        """
        new_state = state_machine.current_state

        if new_state == State.ERROR:
            for other_module, other_state_machine in self._all_state_machines.items():
                if other_module != module:
                    other_state_machine.request_state_change(State.STOPPED)