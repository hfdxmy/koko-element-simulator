from const import ATTACH_ELEMENT_DICT
import numpy as np
import matplotlib.pyplot as plt

class Target:

    def __init__(self):
        self.element = [0, 0, 0, 0, 0, 0, 0, 0]  # 水 火 冰 雷 草 冻 激 燃
        self.decrease_spd = [0, 0, 0, 0, 0, 0, 0, 0]
        self.name = '目标1'
        self.name_eng = 'Target 1'
        self.element_string = "无元素附着"
        self.element_hist = [self.element.copy()]

    def time_advance(self, dt):
        for i in range(8):
            self.element[i] -= self.decrease_spd[i] * dt
            if self.element[i] < 0:
                self.element[i] = 0
                self.decrease_spd[i] = 0
        self.get_element_string()
        self.element_hist.append(self.element.copy())

    def get_element_string(self):
        string = ""
        for i in [6, 7, 8, 5, 1, 2, 3, 4]:
            if self.element[i-1] > 0:
                string += ATTACH_ELEMENT_DICT[i]
                string += "%.2f" % (self.element[i-1])
        if string == "":
            string = "无元素附着"
        self.element_string = string
        return string

    def log_element_change(self):
        print("%s：(%s)->(%s)" % (self.name, self.element_string, self.get_element_string()))

    def print_element_hist(self, canvas, t):
        element_hist = np.array(self.element_hist).transpose()

        ax = canvas.axes
        ax.cla()
        ax.plot(t, element_hist[0], color="blue", label='Hydro', linewidth=1)
        ax.plot(t, element_hist[1], color="red", label='Pyro', linewidth=1)

        ax.legend(loc='upper right')
        ax.set_title(self.name_eng)
        canvas.canvas.draw()
        # ax.plot(t, element_hist[2], color="purple")
        # plt.show()
