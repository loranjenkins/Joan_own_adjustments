import copy
import json

from core import Settings
from modules.experimentmanager.transitions import TransitionsList
from modules.joanmodules import JOANModules
from .condition import Condition, RemovedDictItem


class Experiment:
    """
    Experiment class
    An experiment consists of base settings, conditions, and transitions. The base settings represent the general state of all modules in the experiment.
    Conditions hold the differences in settings with respect to the base settings. The experiment has an active sequence the holds the conditions in the
    sequence in which they are used. A single condition can be used multiple times in the experiments sequence. Transitions hold actions that are executed when
    a new condition is activated. This can be anything from saving files to re-initializing objects.
    An experiment can be loaded from and saved to user-readable json files.
    """

    def __init__(self, modules_included: list):
        self.modules_included = modules_included
        self.base_settings = {}

        self.all_conditions = []
        self.active_condition_sequence = []

    def set_from_current_settings(self, settings_singleton: Settings):
        """
        Set the base settings
        :param settings_singleton:
        :return:
        """
        if self.all_conditions:
            raise RuntimeError("The base settings of an experiment can only be modified when no conditions exist.")

        for module in self.modules_included:
            self.base_settings[module] = copy.deepcopy(settings_singleton.get_settings(module).as_dict()[str(module)])  # not sure if .as_dict() is a good idea

    def save_to_file(self, file_path):
        dict_to_save = {'modules_included': [str(module) for module in self.modules_included],
                        'base_settings': {},
                        'conditions': {},
                        'active_condition_sequence': [condition.name for condition in self.active_condition_sequence], }

        for module in self.modules_included:
            dict_to_save['base_settings'].update({str(module): self.base_settings[module]})

        for condition in self.all_conditions:
            dict_to_save['conditions'][condition.name] = condition.get_savable_dict()

        with open(file_path, 'w') as settings_file:
            json.dump(dict_to_save, settings_file, indent=4)

    @staticmethod
    def _find_deleted_dict_items_in_diff(dictionary):
        for key, item in dictionary.items():
            if item == RemovedDictItem():
                dictionary[key] = RemovedDictItem()
            elif isinstance(item, dict):
                Experiment._find_deleted_dict_items_in_diff(item)

    @staticmethod
    def load_from_file(file_path):
        transitions_list = TransitionsList()
        with open(file_path, 'r') as settings_file:
            loaded_dict = json.load(settings_file)

        Experiment._find_deleted_dict_items_in_diff(loaded_dict)

        modules_included = [JOANModules.from_string_representation(string) for string in loaded_dict['modules_included']]
        new_experiment = Experiment(modules_included)

        for module in modules_included:
            new_experiment.base_settings[module] = loaded_dict['base_settings'][str(module)]

        for condition_name, diff_dict in loaded_dict['conditions'].items():
            if condition_name in [c.name for c in new_experiment.all_conditions]:
                print("WARNING: while loading an experiment from %s, two condition with the same name where found. The second was ignored. "
                      "Please edit the *.JSON file and give all conditions unique names" % file_path)
            else:
                new_condition = Condition(modules_included, condition_name)
                new_condition.set_from_loaded_dict(diff_dict)
                new_experiment.all_conditions.append(new_condition)

        for condition_name in loaded_dict['active_condition_sequence']:
            condition_found = False
            for condition in new_experiment.all_conditions:
                if condition_name == condition.name:
                    new_experiment.active_condition_sequence.append(condition)
                    condition_found = True

            if not condition_found:
                for transition in transitions_list:
                    if condition_name == transition.name:
                        new_experiment.active_condition_sequence.append(transition)
                        condition_found = True

            if not condition_found:
                print('WARNING: a condition named: "' + condition_name + '" was used in the loaded experiment. But this condition does not exist in the '
                                                                         'experiment. There are also no transitions known with this name. It was ignored. ')

        return new_experiment
