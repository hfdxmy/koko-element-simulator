from const import ATTACH_ELEMENT_DICT


class Target:

    def __init__(self):
        self.element = [0, 0, 0, 0, 0, 0, 0, 0]  # 水 火 冰 雷 草 冻 激 燃
        self.decrease = [0, 0, 0, 0, 0, 0, 0, 0]
        self.name = '目标1'

    def time_advance(self):
        for i in range(0, 8):
            self.element[i] -= self.decrease[i]
            if self.element[i] < 0:
                self.element[i] = 0
                self.decrease[i] = 0

    def element_string(self):
        string = ""
        for i in [6, 7, 8, 5, 1, 2, 3, 4]:
            if self.element[i] > 0:
                string += ATTACH_ELEMENT_DICT[i]
                string += "%.1f" % (self.element[i])
        if string == "":
            string = "无元素附着"
        return string
