import attack
import target

dt = 0.05


def decrease_speed(element, element_mass):
    spd = 0
    if element == 1 or element == 2 or element == 4 or element == 6:  # 水，火，雷，冰攻击
        spd = element_mass / (element_mass * 2.5 + 7) / (1 / dt)
    return spd


def reaction(tgt, atk, time):
    element_string_prev = tgt.element_string()

    if atk.element == 1:  # 水攻击
        if tgt.element[0] > 0:  # 目标有水附着
            if atk.element_mass * 0.8 > tgt.element[0]:
                tgt.element[0] = atk.element_mass * 0.8
                print("(%.1fs)%s对%s刷新水元素量" % (time, atk.name, tgt.name))
        else:  # 目标无附着，造成水元素附着，计算衰减速度
            tgt.element[0] = atk.element_mass * 0.8
            tgt.decrease[0] = decrease_speed(atk.element, atk.element_mass)
            print("(%.1fs)%s对%s造成水元素附着" % (time, atk.name, tgt.name))

        element_string = tgt.element_string()
        print("(%s)-->(%s)" % (element_string_prev, element_string))
        pass
    elif atk.element == 2:  # 火
        pass
    elif atk.element == 3:  # 风
        pass
    elif atk.element == 4:  # 雷
        pass
    elif atk.element == 5:  # 草
        pass
    elif atk.element == 6:  # 冰
        pass
    elif atk.element == 7:  # 岩
        pass


class Monitor:
    def __init__(self, bs):  # bs short for basic setting
        self.time = 0
        self.max_time = bs.max_time
        self.target_num = bs.target_num
        self.attack_num = bs.attack_num

        self.attack_list = [attack.Attack() for _ in range(attack_num)]
        self.target_list = [target.Target() for _ in range(target_num)]

        self.steps = max_time / dt + 1

    def simulate(self):
        for _ in range(self.steps):
            # deal with each attack
            for a in range(self.attack_num):
                atk = self.attack_list[a]
                if atk.is_triggered(self.time):
                    atk.current_attack_cd = atk.attack_cd
                    if atk.is_with_element(self):
                        # 如果带元素
                        reaction(self.target_list[0], atk, self.time)
                        atk.current_element_cd = atk.element_cd
                    else:
                        # 如果不带元素，只检查协同触发和草核
                        pass

            #  dendro-core check
            #  electro-hydro check

            # element decrease
            for t in range(self.target_num):
                self.target_list[t].time_advance()

            # time advance
            self.time += dt
