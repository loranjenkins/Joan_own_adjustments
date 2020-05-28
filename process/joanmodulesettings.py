import inspect
import abc
import json

from enum import Enum

from modules.joanmodules import JOANModules


class JoanModuleSettings(abc.ABC):
    def __init__(self, module_enum: JOANModules):
        self._module_enum = module_enum

    def save_to_file(self, file_path, keys_to_omit=()):
        dict_to_save = self.as_dict()

        for key in keys_to_omit:
            try:
                del dict_to_save[key]
            except KeyError:
                pass

        with open(file_path, 'w') as settings_file:
            json.dump(dict_to_save, settings_file, sort_keys=True, indent=4)

    def load_from_file(self, file_path):
        with open(file_path, 'r') as settings_file:
            loaded_dict = json.load(settings_file)

        self.set_from_loaded_dict(loaded_dict)

    def set_from_loaded_dict(self, loaded_dict):
        try:
            self._copy_dict_to_class_dict(loaded_dict[str(self._module_enum)], self.__dict__)
        except KeyError:
            warning_message = "WARNING: loading settings for the " + str(self._module_enum) + \
                              " module from a dictionary failed. The loaded dictionary did not contain " + str(self._module_enum) + " settings." + \
                              (" It did contain settings for: " + ", ".join(loaded_dict.keys()) if loaded_dict.keys() else "")

            print(warning_message)

    def as_dict(self):
        output_dict = {str(self._module_enum): {}}

        # omit attributes of the ABC from the source dict since they are not of interest when displaying the settings as a dict
        source_dict = {key: item for key, item in self.__dict__.items() if key not in JoanModuleSettings(None).__dict__.keys()}

        self._copy_dict_to_dict(source_dict, output_dict[str(self._module_enum)])
        return output_dict

    def _copy_dict_to_class_dict(self, source, destination):
        """
        method to reconstruct a class dict from a saved dictionary. Recognizes custom class objects and loads their attributes recursively from the sub-dicts
        :param source (dict): saved variables
        :param destination (__dict__): class dict to restore
        :return: None
        """
        for key, value in source.items():
            try:
                if isinstance(destination[key], Enum):  # reconstruct the enum from its value
                    destination[key] = value.__class__(value)
                elif hasattr(destination[key], '__dict__') and not inspect.isclass(destination[key]):
                    # recognize child classes and reconstruct their class dicts from the saved dicts
                    self._copy_dict_to_class_dict(value, destination[key].__dict__)
                else:
                    destination[key] = value
            except KeyError:
                print("WARNING: a saved setting called " + key + " was found to restore in " + str(
                    self._module_enum) + " settings, but this setting did not exist. It was created.")
                destination[key] = value

    @staticmethod
    def _copy_dict_to_dict(source, destination):
        """
        Method to copy a (class) dict to another dictionary. Recognizes all custom classes in the dict and simplifies them to dicts themselves
        :param source (dict): (class) dict
        :param destination (dict): simplified dictionary containing only base type object
        :return: None
        """
        for key, value in source.items():
            if isinstance(value, list):
                destination[key] = JoanModuleSettings._copy_list_to_list(value)
            elif isinstance(value, dict):
                try:
                    destination[key]  # make sure that the destination dict has an entry at key
                except KeyError:
                    destination[key] = dict()
                JoanModuleSettings._copy_dict_to_dict(value, destination[key])
            elif isinstance(value, Enum):
                destination[key] = value.value
            elif hasattr(value, '__dict__') and not inspect.isclass(value):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    destination[key] = value.as_dict()
                except AttributeError:
                    destination[key] = dict()
                    JoanModuleSettings._copy_dict_to_dict(value.__dict__, destination[key])
            else:
                destination[key] = source[key]

    @staticmethod
    def _copy_list_to_list(source):
        """
        Copies a list and simplifies all objects within to base type objects.
        :param source (list): list to copy
        :return: a list containing only base type objects
        """
        output_list = []
        for index, item in enumerate(source):
            if isinstance(item, list):
                output_list.append(JoanModuleSettings._copy_list_to_list(item))
            elif isinstance(item, Enum):
                print('WARNING: JOAN settings cannot reconstruct enums embedded in lists from saved files, only the value of the enum will be saved')
                output_list.append(item.value)
            elif hasattr(item, '__dict__') and not inspect.isclass(item):
                # recognize custom class object by checking if these have a __dict__, Enums and static classes should be copied as a whole
                # convert custom classes to dictionaries
                try:
                    # make use of the as_dict function is it exists
                    output_list.append(item.as_dict())
                except AttributeError:
                    output_list.append(dict())
                    JoanModuleSettings._copy_dict_to_dict(item.__dict__, output_list[index])
            else:
                output_list.append(item)
        return output_list