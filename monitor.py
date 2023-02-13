import attack
import target
import numpy as np

dt = 0.02


def decrease_speed(element, element_mass):
    spd = 0
    if element == '水' or element == '火' or element == '雷' or element == '冰':  # 水，火，雷，冰附着
        spd = 0.8 * element_mass / (element_mass * 2.5 + 7)
    return spd


class Monitor:
    def __init__(self, bs, log_place):  # bs short for basic setting
        self.time = 0
        self.max_time = bs.max_time
        self.target_num = bs.target_num
        self.attack_num = bs.attack_num

        self.steps = int(bs.max_time / dt)
        self.attack_list: list[attack.Attack] = []
        self.target_list = [target.Target() for _ in range(bs.target_num)]
        self.flag_log_apply = bs.log_apply
        self.log_place = log_place
        pass

    def simulate(self, atk_set):
        self.log_place.SetLabel('---模拟开始---\n')
        for _ in range(self.steps):
            # deal with each attack
            for a in range(self.attack_num):
                atk = atk_set[a].generate_attack(self.time)
                if atk is not None:
                    self.attack_list.append(atk)
                    self.process_attack()

            #  dendro-core check
            #  electro-hydro check

            # element decrease
            for t in range(self.target_num):
                self.target_list[t].time_advance(dt, self.time, self.log_action)

            # cd decrease
            for a in range(self.attack_num):
                atk_set[a].time_advance(dt)
            # time advance
            self.time += dt
        self.log_basic('---模拟结束---')
        pass

    def plot(self, canvas):
        t = np.linspace(0, self.max_time, self.steps + 1)
        self.target_list[0].print_element_hist(canvas, t)

    def log_basic(self, info):
        self.log_place.SetLabel(self.log_place.GetLabel()+info)

    def log_action(self, info):
        self.log_basic("(%.2fs)%s\n" % (self.time, info))

    def log_apply(self, info):
        if self.flag_log_apply:
            self.log_action(info)

    def process_attack(self):
        while len(self.attack_list) > 0:
            atk = self.attack_list.pop(0)
            if atk.element_mass > 0:
                # 如果带元素
                self.reaction(self.target_list[0], atk)
            else:
                # 如果不带元素，只检查协同触发和草核
                pass
        pass

    def reaction(self, tgt, atk):
        if atk.element == '水':  # 水攻击
            if tgt.element[1] > 0:  # 目标有火元素附着
                tgt.element[1] = max(0, tgt.element[1] - 2 * atk.element_mass)
                self.log_action("%s在%s发生蒸发，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            elif tgt.element[2] > 0:  # 目标有冰元素附着，冻结
                self.reaction_froze(tgt,atk)
            elif tgt.element[0] > 0:  # 目标有水附着
                if atk.element_mass * 0.8 > tgt.element[0]:
                    tgt.element[0] = atk.element_mass * 0.8
                    tgt.electro_charged_source = atk.name
                    self.log_apply("%s刷新%s的水元素量，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            else:  # 目标无附着，造成水元素附着，计算衰减速度
                tgt.element[0] = atk.element_mass * 0.8
                tgt.decrease_spd[0] = decrease_speed(atk.element, atk.element_mass)
                tgt.electro_charged_source = atk.name
                self.log_apply("%s对%s造成水元素附着，%s" % (atk.name, tgt.name, tgt.log_element_change()))
                tgt.electro_charge(self.log_action)  # 可能产生感电
            pass
        elif atk.element == '火':  # 火
            if tgt.element[3] > 0:  # 目标有雷附着，超载
                extra_element = 0
                if atk.element_mass > tgt.element[3]:
                    extra_element = atk.element_mass - tgt.element[3]
                    tgt.element[3] = 0
                else:
                    tgt.element[3] -= atk.element_mass

                self.attack_list.append(attack.Attack(name='超载', element='火', element_mass=0, target=[0]))
                self.log_action("%s在%s触发超载，%s" % (atk.name, tgt.name, tgt.log_element_change()))

                if extra_element > 0 and tgt.element[0] > 0:  # 过量火继续蒸发
                    tgt.element[0] = max(0, tgt.element[0] - extra_element / 2)
                    self.log_action("%s在%s发生蒸发，%s" % (atk.name, tgt.name, tgt.log_element_change()))

            elif tgt.element[2] > 0 or tgt.element[5] > 0:  # 目标有冰或冻附着，融化
                tgt.element[2] = max(0, tgt.element[2] - atk.element_mass * 2)
                tgt.element[5] = max(0, tgt.element[5] - atk.element_mass * 2)
                self.log_action("%s在%s发生融化，%s" % (atk.name, tgt.name, tgt.log_element_change()))

            elif tgt.element[0] > 0:  # 目标有水附着
                tgt.element[0] = max(0, tgt.element[0] - atk.element_mass / 2)
                self.log_action("%s在%s发生蒸发，%s" % (atk.name, tgt.name, tgt.log_element_change()))

            elif tgt.element[1] > 0:  # 目标有火附着
                if atk.element_mass * 0.8 > tgt.element[1]:
                    tgt.element[1] = atk.element_mass * 0.8
                    tgt.decrease_spd[1] = decrease_speed(atk.element, atk.element_mass)  # 3.0后衰减速度也覆盖
                    self.log_apply("%s刷新%s的火元素量，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            else:  # 目标无附着，造成火元素附着，计算衰减速度
                tgt.element[1] = atk.element_mass * 0.8
                tgt.decrease_spd[1] = decrease_speed(atk.element, atk.element_mass)
                self.log_apply("%s对%s造成火元素附着，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            pass
        elif atk.element == 3:  # 风
            pass
        elif atk.element == '雷':  # 雷
            if tgt.element[1] > 0:  # 目标有火附着，超载
                tgt.element[1] = max(0, tgt.element[1] - atk.element_mass)
                self.attack_list.append(attack.Attack(name='超载', element='火', element_mass=0, target=[0]))
                self.log_action("%s在%s触发超载，%s" % (atk.name, tgt.name, tgt.log_element_change()))

            elif tgt.element[2] > 0 or tgt.element[5] > 0:  # 目标有冰附着或冻附着，超导，先消耗藏冰
                if tgt.element[5] > 0:
                    if tgt.element[2] > atk.element_mass:
                        tgt.element[2] = max(0, tgt.element[2] - atk.element_mass)
                    else:
                        tgt.element[5] = max(0, tgt.element[5] - (atk.element_mass - tgt.element[2]))
                        tgt.element[2] = 0
                else:
                    tgt.element[2] = max(0, tgt.element[2] - atk.element_mass)

                self.attack_list.append(attack.Attack(name='超导', element='冰', element_mass=0, target=[0]))
                self.log_action("%s在%s触发超导，%s" % (atk.name, tgt.name, tgt.log_element_change()))

            elif tgt.element[3] > 0:  # 目标有雷附着
                if atk.element_mass * 0.8 > tgt.element[3]:
                    tgt.element[3] = atk.element_mass * 0.8
                    tgt.electro_charged_source = atk.name
                    self.log_apply("%s刷新%s的雷元素量，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            else:  # 目标无附着或水附着，造成雷元素附着，计算衰减速度
                tgt.element[3] = atk.element_mass * 0.8
                tgt.decrease_spd[3] = decrease_speed(atk.element, atk.element_mass)
                tgt.electro_charged_source = atk.name
                self.log_apply("%s对%s造成雷元素附着，%s" % (atk.name, tgt.name, tgt.log_element_change()))
                tgt.electro_charge(self.log_action)
            pass
        elif atk.element == 5:  # 草
            pass
        elif atk.element == '冰':  # 冰
            if tgt.element[3] > 0:  # 目标有雷附着，超导
                extra_element = 0
                if atk.element_mass > tgt.element[3]:
                    extra_element = atk.element_mass - tgt.element[3]
                    tgt.element[3] = 0
                else:
                    tgt.element[3] -= atk.element_mass

                self.attack_list.append(attack.Attack(name='超导', element='冰', element_mass=0, target=[0]))
                self.log_action("%s在%s触发超导，%s" % (atk.name, tgt.name, tgt.log_element_change()))

                if extra_element > 0 and tgt.element[0] > 0:  # 过量冰继续冻结
                    atk.element_mass = extra_element
                    self.reaction_froze(tgt, atk)

            elif tgt.element[1] > 0:  # 目标有火附着，融化
                tgt.element[1] = max(0, tgt.element[1] - atk.element_mass / 2)
                self.log_action("%s在%s发生融化，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            elif tgt.element[0] > 0:  # 目标有水附着，冻结
                self.reaction_froze(tgt,atk)
            elif tgt.element[2] > 0:  # 目标有冰附着，判断是否覆盖
                if atk.element_mass * 0.8 > tgt.element[2]:
                    tgt.element[2] = atk.element_mass * 0.8
                    self.log_apply("%s刷新%s的冰元素量，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            else:  # 目标无附着，造成火元素附着，计算衰减速度
                tgt.element[2] = atk.element_mass * 0.8
                tgt.decrease_spd[2] = decrease_speed(atk.element, atk.element_mass)
                self.log_apply("%s对%s造成冰元素附着，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            pass
        elif atk.element == 7:  # 岩
            pass

    def reaction_froze(self, tgt, atk):
        tgt_elem_id = 2  # 冰
        if atk.element == '冰':
            tgt_elem_id = 0  # 水
        quant = min(tgt.element[tgt_elem_id], atk.element_mass)  # 反应量是两元素中较少的
        tgt.element[tgt_elem_id] = max(0, tgt.element[tgt_elem_id] - quant)
        tgt.element[5] = max(tgt.element[5], 2 * quant)
        self.log_action("%s对%s造成冻结，%s" % (atk.name, tgt.name, tgt.log_element_change()))
