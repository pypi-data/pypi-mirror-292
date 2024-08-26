from .MyNet import MyNet
from .MySimulator import MySimulator
from pytessng.DLLs.Tessng import TessPlugin
from pytessng.UserInterface import MyMenu
from pytessng.GlobalVar import GlobalVar


class MyPlugin(TessPlugin):
    def __init__(self, extension: bool):
        super(MyPlugin, self).__init__()
        # 是否为拓展版
        self.extension: bool = extension

        self.my_menu = None
        self.my_net = None
        self.my_simulator = None

    # 过载父类方法，在TESSNG工厂类创建TESSNG对象时调用
    def init(self):
        # 菜单栏
        self.my_menu = MyMenu(extension=self.extension)

        # 路网类和仿真类
        self.my_net = MyNet()
        self.my_simulator = MySimulator()

        # 添加全局函数
        GlobalVar.actions_related_to_mouse_event = self.my_menu.actions_related_to_mouse_event
        GlobalVar.actions_only_official_version = self.my_menu.actions_only_official_version
        GlobalVar.attach_observer_of_my_net = self.my_net.attach_observer
        GlobalVar.detach_observer_of_my_net = self.my_net.detach_observer
        GlobalVar.attach_observer_of_my_simulator = self.my_simulator.attach_observer
        GlobalVar.detach_observer_of_my_simulator = self.my_simulator.detach_observer

    # 过载父类方法，返回插件路网子接口，此方法由TESSNG调用
    def customerNet(self):
        return self.my_net

    # 过载父类方法，返回插件仿真子接口，此方法由TESSNG调用
    def customerSimulator(self):
        return self.my_simulator
