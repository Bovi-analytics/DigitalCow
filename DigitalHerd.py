import numpy as np


class DigitalHerd:
    def __init__(self, mu_age_at_first_heat=365, sigma_age_at_first_heat=0, vwp=40):
        self.__mu_age_at_first_heat = mu_age_at_first_heat
        self.__sigma_age_at_first_heat = sigma_age_at_first_heat
        self.__voluntary_waiting_period = vwp
        self.__herd = []
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
            self.__herd.append(DigitalCow(dim_cows[i], lns_cows[i], dp_cows[i]))
        if cows is not None:
            for cow in cows:
                if isinstance(cow, DigitalCow):
                    self.__herd.append(cow)
        self.__set_herd_variables_in_cow()

    def get_herd(self):
        return self.__herd

    def __set_herd_variables_in_cow(self):
        from DigitalCow import DigitalCow
        for cow in self.__herd:
            if isinstance(cow, DigitalCow):
                cow.__voluntary_waiting_period = self.__voluntary_waiting_period
                cow.__mu_age_at_first_heat = self.__mu_age_at_first_heat
                cow.__sigma_age_at_first_heat = self.__sigma_age_at_first_heat

    def get_age_at_first_heat(self):
        return np.random.normal(self.__mu_age_at_first_heat, self.__sigma_age_at_first_heat)

    def get_voluntary_waiting_period(self):
        return self.__voluntary_waiting_period
