import numpy as np
import DigitalCow


class DigitalHerd:
    def __init__(self, mu_age_at_first_heat=365, sigma_age_at_first_heat=0, vwp=40):
        self._mu_age_at_first_heat = mu_age_at_first_heat
        self._sigma_age_at_first_heat = sigma_age_at_first_heat
        self._voluntary_waiting_period = vwp
        self._herd = []
        # other general properties shared between the entities in the _herd

    def add_to_herd(self, cows=None, dim_cows=None, lns_cows=None, dp_cows=None):
        if dim_cows is None:
            dim_cows = []
        if lns_cows is None:
            lns_cows = []
        if dp_cows is None:
            dp_cows = []
        if not len(dim_cows) == len(lns_cows) == len(dp_cows):
            raise IndexError("Length of dim, lns and dp lists do not match")
        for i in range(len(dim_cows)):
            self._herd.append(DigitalCow.DigitalCow(dim_cows[i], lns_cows[i], dp_cows[i], herd=self))
        if cows is not None:
            for cow in cows:
                if isinstance(cow, DigitalCow.DigitalCow):
                    if cow not in self._herd:
                        self._herd.append(cow)
                        cow.herd = self

    @property
    def mu_age_at_first_heat(self):
        return self._mu_age_at_first_heat

    @mu_age_at_first_heat.setter
    def mu_age_at_first_heat(self, mu):
        self._mu_age_at_first_heat = mu

    @property
    def sigma_age_at_first_heat(self):
        return self._sigma_age_at_first_heat

    @sigma_age_at_first_heat.setter
    def sigma_age_at_first_heat(self, sigma):
        self._sigma_age_at_first_heat = sigma

    def calculate_mu_age_at_first_heat(self):
        mu_age_at_first_heat = 0
        for cow in self._herd:
            mu_age_at_first_heat += cow.age_at_first_heat
        mu_age_at_first_heat = mu_age_at_first_heat / len(self._herd)
        return mu_age_at_first_heat

    def generate_age_at_first_heat(self):
        return np.random.normal(self._mu_age_at_first_heat, self._sigma_age_at_first_heat)

    @property
    def herd(self):
        return self._herd

    @herd.setter
    def herd(self, herd):
        all_instances = True
        for cow in herd:
            if not isinstance(cow, DigitalCow.DigitalCow):
                all_instances = False
        if all_instances:
            self._herd = herd
        else:
            raise TypeError("Herd property has to be a list of DigitalCow objects")

    @property
    def voluntary_waiting_period(self):
        return self._voluntary_waiting_period

    @voluntary_waiting_period.setter
    def voluntary_waiting_period(self, vwp):
        self._voluntary_waiting_period = vwp
