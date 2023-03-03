import numpy as np


class DigitalHerd:
    def __init__(self, mu_age_at_first_heat=365, sigma_age_at_first_heat=0, vwp=40):
        self._mu_age_at_first_heat = mu_age_at_first_heat
        self._sigma_age_at_first_heat = sigma_age_at_first_heat
        self.voluntary_waiting_period = vwp
        self.herd = []
        # other general properties shared between the entities in the herd

    def add_to_herd(self, size=0, cows=None, dim_cows=None, lns_cows=None, dp_cows=None):
        from DigitalCow import DigitalCow
        if dim_cows is None:
            dim_cows = [0]
        if lns_cows is None:
            lns_cows = [0]
        if dp_cows is None:
            dp_cows = [0]
        for i in range(size):
            self.herd.append(DigitalCow(dim_cows[i], lns_cows[i], dp_cows[i]))
        if cows is not None:
            for cow in cows:
                if isinstance(cow, DigitalCow):
                    self.herd.append(cow)
        self.__set_herd_variables_in_cow()

    def __set_herd_variables_in_cow(self):
        from DigitalCow import DigitalCow
        for cow in self.herd:
            if isinstance(cow, DigitalCow):
                cow.voluntary_waiting_period = self.voluntary_waiting_period
                cow._mu_age_at_first_heat = self._mu_age_at_first_heat
                cow._sigma_age_at_first_heat = self._sigma_age_at_first_heat
                for cow_ in self.herd:
                    if not cow == cow_:
                        cow.herd.append(cow_)

    @property
    def mu_age_at_first_heat(self):
        return self._mu_age_at_first_heat

    @mu_age_at_first_heat.setter
    def mu_age_at_first_heat(self, mu):
        self._mu_age_at_first_heat = mu
        self.__set_herd_variables_in_cow()

    @property
    def sigma_age_at_first_heat(self):
        return self._sigma_age_at_first_heat

    @sigma_age_at_first_heat.setter
    def sigma_age_at_first_heat(self, sigma):
        self._sigma_age_at_first_heat = sigma
        self.__set_herd_variables_in_cow()

    def calculate_mu_age_at_first_heat(self):
        mu_age_at_first_heat = 0
        for cow in self.herd:
            mu_age_at_first_heat += cow.age_at_first_heat
        mu_age_at_first_heat = mu_age_at_first_heat / len(self.herd)
        return mu_age_at_first_heat

    def generate_age_at_first_heat(self):
        return np.random.normal(self._mu_age_at_first_heat, self._sigma_age_at_first_heat)

    @property
    def herd(self):
        return self.herd

    @herd.setter
    def herd(self, herd):
        from DigitalCow import DigitalCow
        all_instances = True
        for cow in herd:
            if not isinstance(cow, DigitalCow):
                all_instances = False
        if all_instances:
            self.herd = herd
            self.__set_herd_variables_in_cow()
        else:
            # Error handling
            print()

    @property
    def voluntary_waiting_period(self):
        return self.voluntary_waiting_period

    @voluntary_waiting_period.setter
    def voluntary_waiting_period(self, vwp):
        self.voluntary_waiting_period = vwp
        self.__set_herd_variables_in_cow()
