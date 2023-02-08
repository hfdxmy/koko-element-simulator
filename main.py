import wx
# import win32api
import sys,os

from wx import BoxSizer

import target

APP_TITLE = '元素反应模拟器'
ELEMENTS = ['水', '火', '风', '雷', '草', '冰', '岩']
ELEMENT_MASS = [1, 1.5, 2, 4]
SETTING_TITLE = ['启用', '序号', '名称', '元素', '元素量', '攻击方式', '起始时刻(s)', '持续时刻(s)', '攻击冷却(s)', '附着冷却(s)', '']


class MainFrame(wx.Frame):

    def __init__(self):

        wx.Frame.__init__(self, None, -1, title=APP_TITLE)

        self.SetBackgroundColour(wx.Colour(224, 224, 224))
        self.SetSize((1000, 600))
        self.Center()
        self.make_menu_bar()
        self.CreateStatusBar()
        self.SetStatusText("就绪")

        self.panel = wx.Panel(self)

        self.bs_action = wx.BoxSizer()
        self.runButton = wx.Button(self.panel, label="模拟")
        self.clearButton =wx.Button(self.panel, label="重置")
        self.exitButton = wx.Button(self.panel, label="退出")
        self.bs_action.Add(self.runButton, flag=wx.EXPAND, border=5)
        self.bs_action.Add(self.clearButton, flag=wx.EXPAND, border=5)
        self.bs_action.Add(self.exitButton, flag=wx.EXPAND, border=5)

        self.bs_setting = wx.BoxSizer(wx.VERTICAL)
        self.bs_setting_basic = wx.BoxSizer()
        self.bs_setting_basic.Add(wx.StaticText(self.panel, style=wx.ALIGN_LEFT, label="模拟时长(s)："), flag=wx.EXPAND | wx.ALL, border=5)
        self.bs_setting_basic.Add(wx.TextCtrl(self.panel, size=(40, 24)), flag=wx.EXPAND | wx.ALL, border=5)
        self.bs_setting.Add(self.bs_setting_basic, border=5)

        self.bs_setting_title = wx.BoxSizer()
        for i in range(0, 11):
            self.bs_setting_title.Add(wx.StaticText(self.panel, style=wx.ALIGN_CENTER, label=SETTING_TITLE[i]), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)

        self.bs_setting.Add(self.bs_setting_title, flag=wx.EXPAND | wx.ALL, border=5)

        self.bs = wx.BoxSizer(wx.VERTICAL)
        self.bs.Add(self.bs_action, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
        self.bs.Add(self.bs_setting, proportion=9, flag=wx.EXPAND | wx.ALL, border=5)
        self.panel.SetSizer(self.bs)

        self.setting_num = 0
        self.bs_setting_list = [wx.BoxSizer() for _ in range(20)]
        self.add_setting()
        self.add_setting()

    def add_setting(self):
        num = self.setting_num
        bs = self.bs_setting_list[num]
        bs.Add(wx.CheckBox(self.panel, label='启用'), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 启用
        bs.Add(wx.StaticText(self.panel, style=wx.ALIGN_CENTER, label=str(num+1)), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 序号
        bs.Add(wx.TextCtrl(self.panel, size=(40, 20)), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 名称
        bs.Add(wx.Choice(self.panel, choices=ELEMENTS), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 元素
        bs.Add(wx.TextCtrl(self.panel, size=(40, 20)), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 元素量
        bs.Add(wx.Choice(self.panel, choices=['定时触发', '其他']), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 攻击方式
        bs.Add(wx.TextCtrl(self.panel, size=(40, 20)), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 起始时间
        bs.Add(wx.TextCtrl(self.panel, size=(40, 20)), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 持续时间
        bs.Add(wx.TextCtrl(self.panel, size=(40, 20)), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 攻击冷却
        bs.Add(wx.TextCtrl(self.panel, size=(40, 20)), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 附着冷却
        bs.Add(wx.Button(self.panel, label='增加'), proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 添加删除
        self.bs_setting.Add(bs, flag=wx.EXPAND | wx.ALL, border=5)
        self.setting_num += 1

    def make_menu_bar(self):
        file_menu = wx.Menu()

        run_item = wx.MenuItem(file_menu, 100, text="开始模拟", helpString="进行元素反应模拟",kind=wx.ITEM_NORMAL)
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
