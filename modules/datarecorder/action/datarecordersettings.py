from process import Control
import os
import json
from json import JSONDecoder, JSONDecodeError, JSONEncoder

'''
{ "modules": {
        "moduleKey1":{
            "item1": true,
            "item2": false
        },
        "moduleKey2":{
            "item1": false,
            "item2": true,
            "item3": true
        }
    }
}

'''
class DatarecorderSettings(Control):
    def __init__(self, *args, **kwargs):
        Control.__init__(self, *args, **kwargs)
        self.file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'modulesettings.json')
        self.settings = None

    def write(self, moduleKey=None, item=None):
        self.read()
        # add/remove/change content to self.settings
        if moduleKey:
            try:
                moduleData = {}
                if moduleKey in self.settings['modules'].keys():
                    moduleData = self.settings['modules'][moduleKey]
                else:
                    self.settings['modules'][moduleKey] = moduleData
                moduleData[item.text()] = item.isChecked()

                with open(self.file, 'w') as settingsFile:
                    json.dump(self.settings, settingsFile, sort_keys=True, indent=4)
            except Exception as inst:
                print(inst)
                return False
            return True
        else:
            return False

    def read(self):
        # read settings and return a json object
        try:
            with open(self.file, 'r') as settingsFile:
                self.settings = json.load(settingsFile)
        except Exception as inst:
            if self.settings == None:
                self.settings = {}
                self.settings['modules'] = {}
            print('reading', inst)
        return self.settings
