import wx
from validator import NumberValidator
from const import ELEMENTS, BASIC_ELEMENT_DICT
from attack import Attack
import random as rand


class AttackSetting:

    def __init__(self, parent, num, log_place):
        self.log_place = log_place
        self.bs = wx.BoxSizer()
        self.input_is_active = wx.CheckBox(parent, label='启用')  # 启用
        self.input_name = wx.TextCtrl(parent, size=(40, 20))  # 名称
        self.input_element = wx.Choice(parent, choices=ELEMENTS)  # 元素
        self.input_element_mass = wx.TextCtrl(parent, validator=NumberValidator(), size=(40, 20))  # 元素量
        self.input_attack_mode = wx.Choice(parent, choices=['定时触发', '草神协同', '雷神协同', '阿贝多协同'])  # 攻击方式
        self.input_time_start = wx.TextCtrl(parent, validator=NumberValidator(), size=(40, 20))  # 起始时间
        self.input_time_last = wx.TextCtrl(parent, validator=NumberValidator(), size=(40, 20))  # 持续时间
        self.input_attack_cd = wx.TextCtrl(parent, validator=NumberValidator(), size=(40, 20))  # 攻击冷却
        self.input_element_cd = wx.TextCtrl(parent, validator=NumberValidator(), size=(40, 20))  # 附着冷却

        self.bs.Add(self.input_is_active, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 启用
        self.bs.Add(wx.StaticText(parent, style=wx.ALIGN_CENTER, label=str(num)), proportion=1,
                    flag=wx.EXPAND | wx.ALL, border=5)  # 序号
        self.bs.Add(self.input_name, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 名称
        self.bs.Add(self.input_element, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 元素
        self.bs.Add(self.input_element_mass, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 元素量
        self.bs.Add(self.input_attack_mode, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 攻击方式
        self.bs.Add(self.input_time_start, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 起始时间
        self.bs.Add(self.input_time_last, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 持续时间
        self.bs.Add(self.input_attack_cd, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 攻击冷却
        self.bs.Add(self.input_element_cd, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)  # 附着冷却

        # default value
        self.input_is_active.SetValue(True)
        self.input_name.SetValue('技能')
        self.input_element.SetSelection(0)
        self.input_element_mass.SetValue('1')
        self.input_attack_mode.SetSelection(0)
        self.input_time_start.SetValue(str(rand.randint(0, 30)/10))
        self.input_time_last.SetValue('15')
        self.input_attack_cd.SetValue(str(rand.randint(10, 20)/10))
        self.input_element_cd.SetValue('0')

        self.setting_id = num
        self.is_active = False
        self.name = 'Default'
        self.element = 'Default'
        self.element_mass = 1
        self.attack_mode = 'Default'
        self.time_start = 0
        self.time_last = 1
        self.attack_cd = 1
        self.element_cd = 2.5

        self.current_attack_cd = 0
        self.current_element_cd = 0
        pass

    def get_inputs(self):
        try:
            self.is_active = self.input_is_active.GetValue()
            self.name = self.input_name.GetValue()
            self.element = self.input_element.GetString(self.input_element.GetSelection())
            self.attack_mode = self.input_attack_mode.GetString(self.input_attack_mode.GetSelection())
            self.element_mass = float(self.input_element_mass.GetValue())
            self.time_start = float(self.input_time_start.GetValue())
            self.time_last = float(self.input_time_last.GetValue())
            self.attack_cd = float(self.input_attack_cd.GetValue())
            self.element_cd = float(self.input_element_cd.GetValue())
        except ValueError:
            self.error_log('数值输入错误')
            return False
        except:
            self.error_log('数据格式错误')
            return False

        if self.element_mass > 4:
            self.error_log('元素量过大')
            return False

        if self.attack_cd < 0.5:
            self.error_log('攻击频率过快')
            return False

        # restart simulation reset cd
        self.current_attack_cd = 0
        self.current_element_cd = 0
        return True

    def error_log(self, info):
        self.log_place.SetLabel('第%d条设置：“%s” %s' % (self.setting_id, self.name, info))

    def remove(self):
        pass

    def time_advance(self, dt):
        # 冷却减少
        if self.current_attack_cd > 0:
            self.current_attack_cd -= dt
            self.current_attack_cd = max(self.current_attack_cd, 0)
        if self.current_element_cd > 0:
            self.current_element_cd -= dt
            self.current_element_cd = max(self.current_element_cd, 0)
        pass

    def generate_attack(self, time):
        if not self.is_active:
            return None
        if time < self.time_start - 0.001 or time > self.time_start + self.time_last + 0.001:
            return None
        if self.current_attack_cd > 0.001:
            return None

        self.current_attack_cd = self.attack_cd
        if self.current_element_cd < 0.001:
            self.current_element_cd = self.element_cd
            return Attack(self.name, self.element, self.element_mass)
        else:
            return Attack(self.name, self.element, element_mass=0)

    pass


class BasicSetting:

    def __init__(self, parent, log_place):
        self.bs = wx.BoxSizer()
        self.bs.Add(wx.StaticText(parent, style=wx.ALIGN_LEFT, label="模拟时长(s)："),
                    flag=wx.EXPAND | wx.ALL, border=5)
        self.input_max_time = wx.TextCtrl(parent, validator=NumberValidator(), size=(30, 24))
        self.input_max_time.SetValue('20')
        self.bs.Add(self.input_max_time, flag=wx.EXPAND | wx.ALL, border=5)
        self.input_log_apply = wx.CheckBox(parent, label='记录附着')
        self.bs.Add(self.input_log_apply)
        self.input_log_quicken = wx.CheckBox(parent, label='记录激化')
        self.bs.Add(self.input_log_quicken)
        self.input_nilou = wx.CheckBox(parent, label='妮绽放')
        self.bs.Add(self.input_nilou)
        self.max_time = 0
        self.target_num = 1
        self.attack_num = 1
        self.log_place = log_place
        self.log_apply = True
        self.log_quicken = True
        self.nilou = False

    def get_inputs(self):
        try:
            max_time = float(self.input_max_time.GetValue())
        except ValueError:
            self.log_place.SetLabel('max time error')
            return False
        if max_time > 40:
            self.log_place.SetLabel('max time too long')
            return False
        self.max_time = max_time

        self.log_apply = self.input_log_apply.GetValue()
        self.log_quicken = self.input_log_quicken.GetValue()
        self.nilou = self.input_nilou.GetValue()
        return True
