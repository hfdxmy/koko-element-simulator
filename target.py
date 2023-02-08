element_dict = {0: '水', 1: '火', 2: '冰', 3: '雷', 4: '草', 5: '冻', 6: '激', 7: '燃'}


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
        for i in range(8):
            if self.element[i] > 0:
                string += element_dict[i]
                string += "%.1f" % (self.element[i])
        if string == "":
            string = "无元素附着"
        return string
