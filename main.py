import wx
# import win32api
import sys, os

from wx import BoxSizer

import monitor
import target
import setting
from const import APP_TITLE, SETTING_TITLE
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from numpy import arange, sin, pi
import matplotlib
matplotlib.use('WXAgg')


class CanvasPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.figure = Figure(figsize=(4, 4))
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()

    # def draw(self):
    #     t = arange(0.0, 3.0, 0.01)
    #     s = sin(2 * pi * t)
    #     self.axes.plot(t, s)


class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, title=APP_TITLE)

        self.SetBackgroundColour(wx.Colour(224, 224, 224))
        self.SetSize((1200, 600))
        self.Center()
        self.make_menu_bar()
        self.CreateStatusBar()
        self.SetStatusText("就绪")

        self.panel = wx.Panel(self)

        self.runButton = wx.Button(self.panel, label="模拟")
        self.runButton.Bind(wx.EVT_BUTTON, self.start_simulation)
        self.addButton = wx.Button(self.panel, label="添加")
        self.addButton.Bind(wx.EVT_BUTTON, self.on_add_setting)
        self.clearButton = wx.Button(self.panel, label="重置")
        self.exitButton = wx.Button(self.panel, label="退出")
        self.exitButton.Bind(wx.EVT_BUTTON, self.on_exit)
        self.bs_action = wx.BoxSizer()
        self.bs_action.Add(self.runButton, flag=wx.EXPAND, border=5)
        self.bs_action.Add(self.addButton, flag=wx.EXPAND, border=5)
        self.bs_action.Add(self.clearButton, flag=wx.EXPAND, border=5)
        self.bs_action.Add(self.exitButton, flag=wx.EXPAND, border=5)

        # init setting area
        self.bs_setting = wx.BoxSizer(wx.VERTICAL)
        # .1 init basic setting
        self.basic_setting = setting.BasicSetting(self.panel)
        self.bs_setting.Add(self.basic_setting.bs, border=5)

        # .2 init setting title
        self.bs_setting_title = wx.BoxSizer()
        for i in range(0, 10):
            self.bs_setting_title.Add(wx.StaticText(self.panel, style=wx.ALIGN_CENTER, label=SETTING_TITLE[i]),
                                      proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.bs_setting.Add(self.bs_setting_title, flag=wx.EXPAND | wx.ALL, border=5)

        # .3 init setting list
        self.setting_num = 0
        self.attack_setting = []
        self.add_setting()

        self.canvas = CanvasPanel(self.panel)
        # self.canvas.draw()
        # apply BoxSizer
        self.bs = wx.BoxSizer(wx.VERTICAL)
        self.bs.Add(self.bs_action, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        self.bs.Add(self.bs_setting, proportion=5, flag=wx.EXPAND | wx.ALL, border=5)
        self.bs.Add(self.canvas, proportion=4, flag=wx.EXPAND | wx.ALL, border=5)

        self.bs_main = wx.BoxSizer()
        self.bs_main.Add(self.bs, proportion=6, flag=wx.EXPAND | wx.ALL, border=5)
        self.log_place = wx.StaticText(self.panel, label='----等待模拟----')
        self.bs_main.Add(self.log_place, proportion=4, flag=wx.EXPAND | wx.ALL, border=5)
        self.panel.SetSizer(self.bs_main)

    def add_setting(self):
        self.setting_num += 1
        new_as = setting.AttackSetting(self.panel, self.setting_num)
        self.attack_setting.append(new_as)
        self.bs_setting.Add(new_as.bs, flag=wx.EXPAND | wx.ALL, border=5)
        pass

    def remove_setting(self):
        pass

    def make_menu_bar(self):
        file_menu = wx.Menu()

        run_item = wx.MenuItem(file_menu, 100, text="开始模拟", helpString="进行元素反应模拟", kind=wx.ITEM_NORMAL)
        file_menu.Append(run_item)
        exit_item = file_menu.Append(wx.ID_EXIT)

        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT)

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "文件(&F)")
        menu_bar.Append(help_menu, "帮助(&H)")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def on_about(self, event):
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION)

    def on_exit(self, event):
        self.Close(True)

    def on_add_setting(self, event):
        self.add_setting()
        # self.bs_setting.Layout()
        self.bs.Layout()

    def start_simulation(self, event):
        self.basic_setting.target_num = 1
        self.basic_setting.attack_num = self.setting_num

        if not self.basic_setting.get_inputs():
            print('basic setting param error')
            return False

        for i in range(self.setting_num):
            if not self.attack_setting[i].get_inputs():
                print('attack setting %d error' % (i+1))
                return False

        m = monitor.Monitor(self.basic_setting, self.log_place)
        m.simulate(self.attack_setting)
        m.plot(self.canvas)
        self.bs_main.Layout()
class MainApp(wx.App):

    def OnInit(self):
        self.SetAppName(APP_TITLE)
        self.Frame = MainFrame()
        self.Frame.Show()
        return True


if __name__ == '__main__':
    # app = mainApp(redirect=True, filename="debug.txt")
    app = MainApp()
    app.MainLoop()
