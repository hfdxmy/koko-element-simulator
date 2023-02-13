from const import ATTACH_ELEMENT_DICT
import numpy as np
import matplotlib.pyplot as plt


class Target:

    def __init__(self):
        self.element = [0, 0, 0, 0, 0, 0, 0, 0]  # 0水 1火 2冰 3雷 4草 5冻 6激 7燃
        self.decrease_spd = [0, 0, 0, 0, 0, 0.4, 0, 0]
        self.name = '目标1'
        self.name_eng = 'Target 1'
        self.element_string = "无元素附着"
        self.element_hist = [self.element.copy()]

    def time_advance(self, dt, time):
        # 冻结判断
        if self.element[5] > 0:
            self.decrease_spd[5] += 0.1 * dt
        else:
            if self.decrease_spd[5] > 0.4:
                self.decrease_spd[5] = max(0.4, self.decrease_spd[5] - 0.2 * dt)

        # 元素减少
        for i in range(8):
            if self.element[i] > 0:
                self.element[i] -= self.decrease_spd[i] * dt
            if self.element[i] < 0:
                self.element[i] = 0
                if i == 5:
                    print("(%.2fs)%s解冻" % (time, self.name))
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

        element_hist_max = [0, 0, 0, 0, 0, 0, 0]
        element_plot_color = {0: "blue", 1: "Red", 2: "lightblue", 3: "mediumpurple", 4: "lightgreen", 5: "deepskyblue", 6: "green", 7: "firebrick"}
        for i in range(7):
            element_hist_max[i] = max(element_hist[i])
            if element_hist_max[i] > 0.1:
                ax.plot(t, element_hist[i], color=element_plot_color[i], label='Hydro', linewidth=1)
        ax.legend(loc='upper right')
        ax.set_title(self.name_eng)
        canvas.canvas.draw()
        # ax.plot(t, element_hist[2], color="purple")
        # plt.show()
