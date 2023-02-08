class Attack:
    def __init__(self,
                 attack_id=0,
                 is_active=True,
                 name='Default',
                 element=1,
                 element_mass=1,
                 attack_mode='Default',
                 time_start=0,
                 time_last=2,
                 attack_cd=1,
                 element_cd=2):
        self.attack_id = attack_id
        self.is_active = is_active
        self.name = name
        self.element = element
        self.element_mass = element_mass
        self.attack_mode = attack_mode
        self.time_start = time_start
        self.time_last = time_last
        self.attack_cd = attack_cd
        self.element_cd = element_cd

        self.current_attack_cd = 0
        self.current_element_cd = 0
        pass

    def set_attributes(self, attack_id, is_active, name, element, element_mass, attack_mode, time_start,
                       time_last, attack_cd, element_cd):
        self.attack_id = attack_id
        self.is_active = is_active
        self.name = name
        self.element = element
        self.element_mass = element_mass
        self.attack_mode = attack_mode
        self.time_start = time_start
        self.time_last = time_last
        self.attack_cd = attack_cd
        self.element_cd = element_cd

    def time_advance(self,dt):
        # 冷却减少
        if self.current_attack_cd > 0:
            self.current_attack_cd -= dt
            self.current_attack_cd = max(self.current_attack_cd, 0)
        if self.current_element_cd > 0:
            self.current_element_cd -= dt
            self.current_element_cd = max(self.current_element_cd, 0)

    def is_with_element(self):
        return self.element_cd < 0.01

    def is_triggered(self, time):
        if not self.is_active:
            return False
        if time < self.time_start or time > self.time_start + self.time_last or self.attack_cd > 0:
            return False
        return True
