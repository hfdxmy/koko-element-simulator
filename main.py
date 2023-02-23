import json

import wx
# import win32api
import sys, os

from wx import BoxSizer
import pyperclip
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
        # self.CreateStatusBar()
        # self.SetStatusText("就绪")

        splitter = wx.SplitterWindow(self)
        self.panel_setting = wx.Panel(splitter)
        panel_info = wx.Panel(splitter)

        # 先建立右侧的消息区
        bs_info = wx.BoxSizer(wx.VERTICAL)
        self.info_place = wx.TextCtrl(panel_info, value='----消息区----\n 就绪。', size=(-1, 50),
                                      style=wx.TE_READONLY | wx.TE_MULTILINE | wx.HSCROLL | wx.EXPAND | wx.ALL)
        self.log_place = wx.TextCtrl(panel_info, value='----日志----',
                                     style=wx.TE_READONLY | wx.TE_MULTILINE | wx.HSCROLL | wx.EXPAND | wx.ALL)
        static_line = wx.StaticLine(panel_info, style=wx.LI_HORIZONTAL)

        bs_info.Add(self.info_place, 0, wx.EXPAND | wx.ALL, 5)
        bs_info.Add(static_line, flag=wx.ALL | wx.EXPAND, border=5)
        bs_info.Add(self.log_place, 9, wx.EXPAND | wx.ALL, 5)

        # 左侧的由上到下，1. 按钮

        bs_buttons = wx.BoxSizer()
        self.init_buttons(bs_buttons, self.panel_setting)

        # 2. 基本设置

        bs_basic_setting = wx.BoxSizer()
        self.basic_setting = setting.BasicSetting(self.panel_setting, self.info_place, bs_basic_setting)

        # 3. 攻击设置
        self.gs_atk_set = wx.FlexGridSizer(rows=11, cols=11, hgap=5, vgap=5)
        # 3.1 标题
        for i in range(0, 11):
            prop = 2
            if i < 2:
                prop = 1
            self.gs_atk_set.Add(wx.StaticText(self.panel_setting, style=wx.ALIGN_CENTER, label=SETTING_TITLE[i]),
                           flag=wx.EXPAND | wx.ALL, border=5)

        # 3.2 攻击列表
        self.setting_num = 0
        self.attack_setting = []
        for i in range(5):
            self.add_setting(self.panel_setting, self.gs_atk_set)

        # self.canvas = CanvasPanel(self.panel_setting)

        # 加入整体sizer
        self.bs_setting = wx.BoxSizer(wx.VERTICAL)
        self.bs_setting.Add(bs_buttons, flag=wx.EXPAND | wx.ALL, border=5)
        self.bs_setting.Add(bs_basic_setting, border=5)
        self.bs_setting.Add(self.gs_atk_set, flag=wx.EXPAND | wx.ALL, border=5)

        self.panel_setting.SetSizer(self.bs_setting)

        panel_info.SetSizer(bs_info)
        splitter.SplitVertically(self.panel_setting, panel_info)
        splitter.SetMinimumPaneSize(800)
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.GetSizer().Add(splitter, 1, wx.EXPAND)

        self.m = None
        self.flag_simulation = False

    def init_buttons(self, sizer, parent):
        # Buttons
        runButton = wx.Button(parent, label="开始模拟")
        runButton.Bind(wx.EVT_BUTTON, self.start_simulation)
        plotButton = wx.Button(parent, label="绘制图线")
        plotButton.Bind(wx.EVT_BUTTON, self.on_plot)
        addButton = wx.Button(parent, label="添加一行")
        addButton.Bind(wx.EVT_BUTTON, self.on_add_setting)
        applyButton = wx.Button(parent, label="加载配置\n从剪贴板\n")
        applyButton.Bind(wx.EVT_BUTTON, self.on_apply_setting)
        saveSetButton = wx.Button(parent, label="保存配置\n到剪贴板")
        saveSetButton.Bind(wx.EVT_BUTTON, self.on_copy_setting)
        presetButton = wx.Button(parent, label="加载预设")
        saveButton = wx.Button(parent, label="保存结果")
        saveButton.Bind(wx.EVT_BUTTON, self.on_save)
        exitButton = wx.Button(parent, label="退出")
        exitButton.Bind(wx.EVT_BUTTON, self.on_exit)

        sizer.Add(runButton, flag=wx.EXPAND, border=5)
        sizer.Add(plotButton, flag=wx.EXPAND, border=5)
        sizer.Add(addButton, flag=wx.EXPAND, border=5)
        sizer.Add(applyButton, flag=wx.EXPAND, border=5)
        sizer.Add(saveSetButton, flag=wx.EXPAND, border=5)
        sizer.Add(saveButton, flag=wx.EXPAND, border=5)
        sizer.Add(presetButton, flag=wx.EXPAND, border=5)
        sizer.Add(exitButton, flag=wx.EXPAND, border=5)

    def apply_setting(self, text):
        try:
            sets = json.loads(text)
            self.basic_setting.set_inputs(sets.pop(0))

            # 如果配置比当前多，就添加
            if len(sets) > len(self.attack_setting):
                while len(sets) > len(self.attack_setting):
                    self.add_setting(self.panel_setting, self.gs_atk_set)
                self.bs_setting.Layout()

            for i in range(len(sets)):
                self.attack_setting[i].set_inputs(sets[i])
        except:
            self.log_info("配置应用错误，请检查剪贴板内容。")

    def add_setting(self, parent, sizer):
        self.setting_num += 1
        new_as = setting.AttackSetting(parent, self.setting_num, self.info_place, sizer)
        self.attack_setting.append(new_as)
        # self.bs_setting.Add(new_as.bs, flag=wx.EXPAND | wx.ALL, border=5)

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

    def on_save(self, event):
        # Bring up the system's native file save dialog
        dialog = wx.FileDialog(self, "保存结果", "", "", "Text files (*.txt)|*.txt",
                               wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            # User clicked OK, get the selected filename
            filename = dialog.GetPath()
            string_to_save = "This is the string to save."
            # Save the string to the file
            with open(filename, 'w') as f:
                f.write(string_to_save)
            self.log_place.SetLabel("保存到%s" % filename)
        # Destroy the file dialog
        dialog.Destroy()

    def on_exit(self, event):
        self.Close(True)

    def on_add_setting(self, event):
        self.add_setting(self.panel_setting, self.gs_atk_set)
        self.bs_setting.Layout()

    def on_copy_setting(self, event):
        sets = [self.basic_setting.get_string()]
        for atk in self.attack_setting:
            # if atk.input_is_active.GetValue:
            sets.append(atk.get_string())
        text = json.dumps(sets)
        pyperclip.copy(text)

        self.log_info("已将当前配置保存到剪贴板。")

    def on_apply_setting(self, event):
        text = pyperclip.paste()
        self.apply_setting(text)

    def on_plot(self, event):
        if self.flag_simulation:
            self.m.plot()
        else:
            self.log_info("请先执行模拟！")
    def log_info(self, info):
        self.info_place.SetLabel(info)

    def start_simulation(self, event):
        self.basic_setting.attack_num = self.setting_num

        if not self.basic_setting.get_inputs():
            self.log_info('基础参数设置错误')
            return False

        for i in range(self.setting_num):
            if not self.attack_setting[i].get_inputs():
                self.log_info('第%d个攻击设置参数设置错误' % (i + 1))
                return False

        self.m = monitor.Monitor(self)
        self.m.simulate()
        self.log_info("模拟完成！")
        self.flag_simulation = True
        # m.plot(self.canvas)
        # self.bs_main.Layout()


class MainApp(wx.App):

    def OnInit(self):
        self.SetAppName(APP_TITLE)
        self.Frame = MainFrame()
        self.Frame.Show()
        return True


if __name__ == '__main__':
    app = MainApp()
    app.MainLoop()
