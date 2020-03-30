from signals import Pulsar
from .statehandler import StateHandler, MasterStates
from PyQt5 import uic, QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from .mainmodulewidget import MainModuleWidget
from pathlib import Path
#from queue import Queue

import os 

class News:
    '''
    The News class is a singleton that holds all most recent status data
    Every class has its own writing area; the key of the class
    Oll other classes may read the value
    '''
    instance = None

    def __new__(klass, *args, **kwargs):
        if not klass.instance:
            klass.instance = object.__new__(News)
            klass.news = {}
            #klass.availableKeys = klass.news.keys()
        return klass.instance

    def __init__(self, recentNewsDict, *args, **kwargs):
        self.news.update(recentNewsDict)


class Status:
    '''
    The Status class is a singleton that handles all states as defined in the MasterStates class
    To change states the StateHandler class is used
    '''
    instance = None

    def __new__(klass, *args, **kwargs):
        if not klass.instance:
            klass.instance = object.__new__(Status)
            #klass.gui = {}
            klass.masterStates = MasterStates()
            klass.masterStateHandler = StateHandler(firstState=MasterStates.VOID, statesDict=klass.masterStates.getStates())
            #klass.masterStates = MasterStates()
            klass.moduleStatePackages = {}
        return klass.instance

    def __init__(self, moduleStatePackage, *args, **kwargs):
        # TODO find out if self.gui is necessary, also see klass.gui
        #self.gui.update(guiDict)
        self.moduleStatePackages.update(moduleStatePackage)

class Control(Pulsar):

    def __init__(self, *args, **kwargs):
        kwargs['millis'] = 'millis' in kwargs.keys() and kwargs['millis'] or 1
        kwargs['callback'] = 'callback' in kwargs.keys() and kwargs['callback'] or []
        Pulsar.__init__(self, *args, **kwargs)

        # for use in child classes
        self.singletonStatus = Status({})
        self.singletonNews = News({})
        self.masterStateHandler = self.singletonStatus.masterStateHandler
        self.masterStates = self.singletonStatus.masterStates

        self.window = None # main widget (container for widget and controlWidget)
        self.widget = None  # will contain a value after calling createWidget
        self.mainwidget= None
        self.moduleStateHandler = None # will contain  a value after calling defineModuleStateHandler
        self.moduleStates = None # will contain  a value after calling defineModuleStateHandler

   
    def createWidget(self, ui=''):       
        assert ui != '', 'argument "ui" should point to a PyQt ui file (e.g. ui=<absolute path>menu.ui)' 
        
        self.mainwidget = self._getGui((os.path.join(os.path.dirname(os.path.realpath(__file__)),"MainWindowWidget.ui")))
        self.widget = self._getGui(ui)

        self.mainwidget.vLayout.addWidget(self.widget)
        self.mainwidget.lineTick.setPlaceholderText(str(self.millis))

        self.mainwidget.btnStart.clicked.connect(self.start)
        self.mainwidget.btnStop.clicked.connect(self.stop)

        self.mainwidget.btnStart.clicked.connect(self.disableLineTick)
        self.mainwidget.btnStop.clicked.connect(self.enableLineTick)

        self.mainwidget.btnStop.clicked.connect(self.mainwidget.lineTick.clear)
        self.mainwidget.btnStart.clicked.connect(self.mainwidget.lineTick.clear)
        self.mainwidget.btnStart.clicked.connect(self.mainwidget.lineTick.clearFocus)
        
        
        self.mainwidget.btnStart.clicked.connect(self.setTicktext)
        self.mainwidget.btnStop.clicked.connect(self.setTicktext)
        
        self.mainwidget.lineTick.textChanged.connect(self._setmillis)
        
        
        
        assert self.widget != None, 'could not create a widget, is %s the correct filename?' % ui

        # window is a QMainWindow, and the container for all widgets
        self.window = MainModuleWidget()
        self.stateWidget = self._getGui(os.path.join(os.path.dirname(os.path.realpath(__file__)),"statewidget.ui"))
        
        self.window.addWidget(self.stateWidget, 'State widget')
        self.window.addWidget(self.widget, 'Module widget')
        
        # connect self.window close signal to the widget's _close function (if defined): this will also call self._close in case the user closes the window
        try:
            self.window.closed.connect(self._close)
        except:
            pass

        '''
        # TODO find out if Status needs to have a dictionary with widgets
        # self.singletonStatus = Status()

        uiKey = os.path.basename(os.path.realpath(ui))
        # put widgets in SingletonStatus object for setting state of widgets 
        self.singletonStatus = Status({uiKey: self.widget})
        '''
    def disableLineTick(self):
        self.mainwidget.lineTick.setEnabled(False)

    def enableLineTick(self):
        self.mainwidget.lineTick.setEnabled(True)


    def _getGui(self, ui=''):
        '''
        return a Qwidget which can be shown
        '''
        try:
            return uic.loadUi(ui)
        except Exception as inst:
            print(inst)
            return None


    def defineModuleStateHandler(self, module='', moduleStates=None):
        assert module != '', 'argument "module" should containt the name of the module, which is the calling class'
        # states example:     VOID = State(0, translate('BootStates', 'Null state'), -1,150)
        moduleStatesDict = moduleStates.getStates()
        self.moduleStateHandler = StateHandler(firstState=MasterStates.VOID, statesDict=moduleStatesDict)
        self.moduleStates = moduleStates
        #print(type(moduleStates))
        #assert type(moduleStates) == dict, 'argument "moduleStates" should be of type StateHandler (key = State())'
        #self.moduleStates = self.moduleStateHandler.states
        try:
            moduleKey = '%s.%s' % (module.__class__.__module__ , module.__class__.__name__)
            moduleStatePackage = {}
            moduleStatePackage['moduleStates'] = moduleStates
            moduleStatePackage['moduleStateHandler'] = self.moduleStateHandler
            self.singletonStatus = Status({moduleKey: moduleStatePackage})
        except Exception as inst:
            print('Exception in Control',inst)

    def setTicktext(self):
        self.mainwidget.lineTick.setPlaceholderText(str(self.millis))

    def writeNews(self, channel='', news={}):
        assert channel != '', 'argument "channel" should be the writer class'
        assert type(news) == dict, 'argument "news" should be of type dict and will contain news(=data) of this channel'
        try:
            channelKey = '%s.%s' % (channel.__class__.__module__ , channel.__class__.__name__)
            #if channelKey not in self.getAvailableNewsChannels():
            self.singletonNews = News({channelKey: news})
        except Exception as inst:
            print(inst)


    ''' 20200316 deprecated
    def getAllGui(self):
        return self.singletonStatus.gui
    '''

    def getAllNews(self):
        return self.singletonNews.news

    def getAvailableNewsChannels(self):
        return self.singletonNews.news.keys()

    def readNews(self, channel=''):
        return channel in self.getAvailableNewsChannels() and self.singletonNews.news[channel] or {}

    def getAllModuleStatePackages(self):
        return self.singletonStatus.moduleStatePackages

    def getAvailableModuleStatePackages(self):
        return self.singletonStatus.moduleStatePackages.keys()

    def getModuleStatePackage(self, module=''):
        return module in self.getAvailableModuleStatePackages() and self.singletonStatus.moduleStatePackages[module] or {}

