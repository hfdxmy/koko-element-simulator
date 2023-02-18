import attack
import dendro_core
import target
import numpy as np
import dendro_core as dc
dt = 0.02


def decrease_speed(element, element_mass):
    spd = 0
    if element == '水' or element == '火' or element == '雷' or element == '冰' or element == '草':  # 水，火，雷，冰，草附着
        spd = 0.8 * element_mass / (element_mass * 2.5 + 7)
    if element == '激':
        spd = element_mass / (5 * element_mass + 6)
    return spd


class Monitor:

    def __init__(self, bs, atk_set, log_place):  # bs short for basic setting
        self.time = 0
        self.max_time = bs.max_time
        self.target_num = bs.target_num
        self.attack_num = bs.attack_num
        self.atk_set = atk_set

        self.steps = int(bs.max_time / dt)
        self.attack_list: list[attack.Attack] = []
        self.target_list = [target.Target(self) for _ in range(bs.target_num)]
        self.flag_log_apply = bs.log_apply
        self.flag_log_quicken = bs.log_quicken
        self.log_place = log_place
        self.nilou = bs.nilou
        self.dcm = dendro_core.DCManager(self)

    def simulate(self):
        self.log_place.SetLabel('---模拟开始---\n')
        for a in range(self.attack_num):
            if self.atk_set[a].attack_mode == '草神协同':
                self.target_list[0].coordinate_nahida_list.append(a)
            elif self.atk_set[a].attack_mode == '雷神协同':
                self.target_list[0].coordinate_shogun_list.append(a)
            elif self.atk_set[a].attack_mode == '阿贝多协同':
                self.target_list[0].coordinate_albedo_list.append(a)

        for _ in range(self.steps):
            # deal with each attack
            for atk_s in self.atk_set:
                if atk_s.attack_mode == '定时触发':
                    atk = atk_s.generate_attack(self.time)
                    if atk is not None:
                        self.attack_list.append(atk)
                        self.process_attack()

            # element decrease
            for t in range(self.target_num):
                self.target_list[t].time_advance(dt, self.time)

            # cd decrease
            for a in range(self.attack_num):
                self.atk_set[a].time_advance(dt)

            # dendro-core life
            self.dcm.time_advance(dt)

            # time advance
            self.time += dt

            self.process_attack()  # 处理协同

        self.log_basic('---模拟结束---')
        pass

    def process_attack(self):
        while len(self.attack_list) > 0:
            atk = self.attack_list.pop(0)

            # 对atk的每个tgt id判断一次
            tgt = self.target_list[0]
            # 岩击碎冰
            if atk.element == '岩' and tgt.element[5] > 0:
                tgt.element[5] = 0
                self.log_action("%s使得%s碎冰，%s" % (atk.name, tgt.name, self.target_list[0].log_element_change()))
                self.attack_list.append(attack.Attack('碎冰'))  # 碎冰可以触发草神吗？

            if atk.element_mass > 0:
                # 如果带元素
                self.reaction(tgt, atk)
            if atk.element_mass > -1:
                # 先判断雷神协同
                tgt.coordinate('shogun')
                # 超烈绽放
                if atk.element == '火' or atk.element == '雷':
                    self.dcm.core_reaction(self.target_list[0], atk)
                # 反应的元素量都是-1，不会触发雷神协同
            if atk.element_mass > -2:
                # 阿贝多和迪姐协同
                tgt.coordinate('albedo')
                pass
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

    def log_quicken(self, info):
        if self.flag_log_quicken:
            self.log_action(info)

    def reaction(self, tgt, atk):
        reaction_flag = True
        if atk.element == '水':  # 水攻击
            if tgt.element[1] > 0:  # 目标有火元素附着
                tgt.element[1] = max(0, tgt.element[1] - 2 * atk.element_mass)
                self.log_action("%s在%s发生蒸发，%s" % (atk.name, tgt.name, tgt.log_element_change()))

            elif tgt.element[2] > 0:  # 目标有冰元素附着，冻结
                self.reaction_froze(tgt, atk)
                if (tgt.element[4] > 0 or tgt.element[6] > 0) and atk.element_mass > 0.01:  # 水过量，且有激草
                    self.reaction_bloom(tgt, atk)

            elif tgt.element[4] > 0 or tgt.element[6] > 0:  # 草元素或激元素
                self.reaction_bloom(tgt, atk)
                if atk.element_mass > 0.01 and tgt.element[3] > 0:  # 水过量，强制触发一次感电，不进行附着
                    if tgt.electro_charged_cd == 0:
                        self.log_action("%s感电，由%s触发" % (tgt.name, atk.name))
                        self.attack_list.append(attack.Attack('感电', '雷', -1))
                        tgt.electro_charged_cd = 1

            elif tgt.element[0] > 0:  # 目标有水附着
                if atk.element_mass * 0.8 > tgt.element[0]:
                    tgt.element[0] = atk.element_mass * 0.8
                    tgt.electro_charged_source = atk.name
                    self.log_apply("%s刷新%s的水元素量，%s" % (atk.name, tgt.name, tgt.log_element_change()))
                reaction_flag = False

            else:  # 目标无附着，造成水元素附着，计算衰减速度
                tgt.element[0] = atk.element_mass * 0.8
                tgt.decrease_spd[0] = decrease_speed(atk.element, atk.element_mass)
                tgt.electro_charged_source = atk.name
                self.log_apply("%s对%s造成水元素附着，%s" % (atk.name, tgt.name, tgt.log_element_change()))
                reaction_flag = False
                tgt.electro_charge()  # 可能产生感电

            if reaction_flag:
                tgt.coordinate('nahida')

        elif atk.element == '火':  # 火
            if tgt.element[3] > 0:  # 目标有雷附着，超载
                extra_element = 0
                if atk.element_mass > tgt.element[3]:
                    extra_element = atk.element_mass - tgt.element[3]
                    tgt.element[3] = 0
                else:
                    tgt.element[3] -= atk.element_mass

                self.attack_list.append(attack.Attack(name='超载', element='火', element_mass=-1, target=[0]))
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
                reaction_flag = False

            else:  # 目标无附着，造成火元素附着，计算衰减速度
                tgt.element[1] = atk.element_mass * 0.8
                tgt.decrease_spd[1] = decrease_speed(atk.element, atk.element_mass)
                self.log_apply("%s对%s造成火元素附着，%s" % (atk.name, tgt.name, tgt.log_element_change()))
                reaction_flag = False

            if reaction_flag:
                tgt.coordinate('nahida')

        elif atk.element == 3:  # 风
            pass

        elif atk.element == '雷':  # 雷
            quicken_flag = False
            if tgt.element[6] > 0:  # 超激化
                self.log_quicken("%s在%s触发超激化" % (atk.name, tgt.name))
                quicken_flag = True

            if tgt.element[1] > 0:  # 目标有火附着，超载
                tgt.element[1] = max(0, tgt.element[1] - atk.element_mass)
                self.attack_list.append(attack.Attack(name='超载', element='火', element_mass=-1, target=[0]))
                self.log_action("%s在%s触发超载，%s" % (atk.name, tgt.name, tgt.log_element_change()))

            elif tgt.element[2] > 0 or tgt.element[5] > 0:  # 目标有冰附着或冻附着，超导，先消耗藏冰
                quant = 0
                if tgt.element[5] > 0:  # 冻冰
                    if tgt.element[2] > atk.element_mass:  # 藏冰足量
                        quant = atk.element_mass
                        tgt.element[2] = max(0, tgt.element[2] - atk.element_mass)
                    else:
                        quant = min(atk.element_mass, tgt.element[2] + tgt.element[5])
                        tgt.element[5] = max(0, tgt.element[5] - (atk.element_mass - tgt.element[2]))
                        tgt.element[2] = 0
                else:  # 冰
                    quant = min(tgt.element[2], atk.element_mass)
                    tgt.element[2] = max(0, tgt.element[2] - atk.element_mass)

                self.attack_list.append(attack.Attack(name='超导', element='冰', element_mass=-1, target=[0]))
                self.log_action("%s在%s触发超导，%s" % (atk.name, tgt.name, tgt.log_element_change()))

                atk.element_mass -= quant
                if tgt.element[4] > 0 and atk.element_mass > 0.01:  # 过量雷和草激化
                    self.reaction_quicken(tgt, atk)

            elif tgt.element[4] > 0:  # 原激化
                self.reaction_quicken(tgt, atk)
            elif tgt.element[3] > 0:  # 目标有雷附着
                if atk.element_mass * 0.8 > tgt.element[3]:
                    tgt.element[3] = atk.element_mass * 0.8
                    tgt.electro_charged_source = atk.name
                    self.log_apply("%s刷新%s的雷元素量，%s" % (atk.name, tgt.name, tgt.log_element_change()))
                reaction_flag = False

            else:  # 目标无附着或水附着，造成雷元素附着，计算衰减速度
                tgt.element[3] = atk.element_mass * 0.8
                tgt.decrease_spd[3] = decrease_speed(atk.element, atk.element_mass)
                tgt.electro_charged_source = atk.name
                self.log_apply("%s对%s造成雷元素附着，%s" % (atk.name, tgt.name, tgt.log_element_change()))
                tgt.electro_charge()
                reaction_flag = False

            if quicken_flag or reaction_flag:
                tgt.coordinate('nahida')
            pass

        elif atk.element == '草':  # 草
            quicken_flag = False
            if tgt.element[6] > 0:  # 蔓激化
                self.log_quicken("%s在%s触发蔓激化" % (atk.name, tgt.name))
                quicken_flag = True
            if tgt.element[3] > 0:  # 原激化
                self.reaction_quicken(tgt, atk)
                if atk.element_mass > 0.01 and tgt.element[0] > 0:  # 草过量，继续和水反应
                    self.reaction_bloom(tgt, atk)
                if tgt.element[0] > 0:  # 激元素和多余的水反应，将激元素量作为攻击的元素量，代入这一次的草攻击计算
                    atk.element_mass = tgt.element[6]
                    self.reaction_bloom(tgt, atk, self_reaction=True)
            elif tgt.element[1] > 0:  # 燃烧
                pass
            elif tgt.element[0] > 0:  # 绽放
                self.reaction_bloom(tgt, atk)

            elif tgt.element[4] > 0:  # 刷新草量
                if atk.element_mass * 0.8 > tgt.element[4]:
                    tgt.element[4] = atk.element_mass * 0.8
                    self.log_apply("%s刷新%s的草元素量，%s" % (atk.name, tgt.name, tgt.log_element_change()))
                reaction_flag = False
            else:  # 草附着
                tgt.element[4] = atk.element_mass * 0.8
                tgt.decrease_spd[4] = decrease_speed(atk.element, atk.element_mass)
                self.log_apply("%s对%s造成草元素附着，%s" % (atk.name, tgt.name, tgt.log_element_change()))
                reaction_flag = False

            if quicken_flag or reaction_flag:
                tgt.coordinate('nahida')

        elif atk.element == '冰':  # 冰
            if tgt.element[3] > 0:  # 目标有雷附着，超导
                extra_element = 0
                if atk.element_mass > tgt.element[3]:
                    extra_element = atk.element_mass - tgt.element[3]
                    tgt.element[3] = 0
                else:
                    tgt.element[3] -= atk.element_mass

                self.attack_list.append(attack.Attack(name='超导', element='冰', element_mass=-1, target=[0]))
                self.log_action("%s在%s触发超导，%s" % (atk.name, tgt.name, tgt.log_element_change()))

                if extra_element > 0 and tgt.element[0] > 0:  # 过量冰继续冻结
                    atk.element_mass = extra_element
                    self.reaction_froze(tgt, atk)

            elif tgt.element[1] > 0:  # 目标有火附着，融化
                tgt.element[1] = max(0, tgt.element[1] - atk.element_mass / 2)
                self.log_action("%s在%s发生融化，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            elif tgt.element[0] > 0:  # 目标有水附着，冻结
                self.reaction_froze(tgt, atk)
            elif tgt.element[2] > 0:  # 目标有冰附着，判断是否覆盖
                if atk.element_mass * 0.8 > tgt.element[2]:
                    tgt.element[2] = atk.element_mass * 0.8
                    self.log_apply("%s刷新%s的冰元素量，%s" % (atk.name, tgt.name, tgt.log_element_change()))
                reaction_flag = False
            else:  # 目标无附着，造成火元素附着，计算衰减速度
                tgt.element[2] = atk.element_mass * 0.8
                tgt.decrease_spd[2] = decrease_speed(atk.element, atk.element_mass)
                self.log_apply("%s对%s造成冰元素附着，%s" % (atk.name, tgt.name, tgt.log_element_change()))
                reaction_flag = False

            if reaction_flag:
                tgt.coordinate('nahida')
            pass

        elif atk.element == '岩':  # 岩
            if tgt.geo_cd > 0:
                return
            if tgt.element[3] > 0:  # 结晶
                tgt.element[3] = max(0, tgt.element[3] - atk.element_mass / 2)
                tgt.geo_cd = 1
                self.log_action("%s在%s触发雷结晶，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            elif tgt.element[1] > 0:
                tgt.element[1] = max(0, tgt.element[1] - atk.element_mass / 2)
                tgt.geo_cd = 1
                self.log_action("%s在%s触发火结晶，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            elif tgt.element[0] > 0:
                tgt.element[0] = max(0, tgt.element[0] - atk.element_mass / 2)
                tgt.geo_cd = 1
                self.log_action("%s在%s触发水结晶，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            elif tgt.element[2] > 0:
                tgt.element[2] = max(0, tgt.element[2] - atk.element_mass / 2)
                tgt.geo_cd = 1
                self.log_action("%s在%s触发冰结晶，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            elif tgt.element[5] > 0:
                tgt.element[5] = max(0, tgt.element[5] - atk.element_mass / 2)
                tgt.geo_cd = 1
                self.log_action("%s在%s触发冻结晶，%s" % (atk.name, tgt.name, tgt.log_element_change()))
            else:
                reaction_flag = False

            if reaction_flag:
                tgt.coordinate('nahida')
            pass

    def reaction_froze(self, tgt, atk):
        quant = 0
        if atk.element == '冰':
            quant = min(tgt.element[0], atk.element_mass)  # 反应量是两元素中较少的
            tgt.element[0] = max(0, tgt.element[0] - quant)
        if atk.element == '水':
            quant = min(tgt.element[2], atk.element_mass)  # 反应量是两元素中较少的
            tgt.element[2] = max(0, tgt.element[2] - quant)

        atk.element_mass -= quant
        tgt.element[5] = max(tgt.element[5], 2 * quant)
        self.log_action("%s对%s造成冻结，%s" % (atk.name, tgt.name, tgt.log_element_change()))
        return quant

    def reaction_quicken(self, tgt, atk):
        quant = 0
        if atk.element == '雷':
            quant = min(tgt.element[4], atk.element_mass)
            tgt.element[4] = max(0, tgt.element[4] - quant)
        elif atk.element == '草':
            quant = min(tgt.element[3], atk.element_mass)
            tgt.element[3] = max(0, tgt.element[3] - quant)

        atk.element_mass -= quant
        if quant > tgt.element[6]:  # 覆盖，速度一同覆盖
            tgt.element[6] = quant
            tgt.decrease_spd[6] = decrease_speed('激', quant)
        self.log_action("%s在%s触发原激化，%s" % (atk.name, tgt.name, tgt.log_element_change()))

    def reaction_bloom(self, tgt, atk, self_reaction=False):
        quant = 0
        if atk.element == '水':
            quant = min(atk.element_mass, max(tgt.element[4], tgt.element[6]) * 2)
            tgt.element[4] = max(0, tgt.element[4] - atk.element_mass / 2)
            tgt.element[6] = max(0, tgt.element[6] - atk.element_mass / 2)
        elif atk.element == '草':
            quant = min(atk.element_mass, tgt.element[0] / 2)
            tgt.element[0] = max(0, tgt.element[0] - atk.element_mass * 2)

        atk.element_mass -= quant
        if self_reaction:
            tgt.element[6] = atk.element_mass  # 仅在草+水雷中使用
        self.log_action("%s在%s触发绽放产生草核%d，%s" % (atk.name, tgt.name, self.dcm.dc_count+1, tgt.log_element_change()))
        self.dcm.new_dc(atk.name, tgt)
