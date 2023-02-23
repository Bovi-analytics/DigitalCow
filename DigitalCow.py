import numpy as np
from DigitalHerd import DigitalHerd


# class DigitalCow:
class DigitalCow(DigitalHerd):

    def __init__(self, days_in_milk=0, lactation_number=0, current_days_pregnant=0):
        super().__init__()
        self.__current_days_in_milk = days_in_milk
        self.__current_lactation_number = lactation_number
        self.__current_days_pregnant = current_days_pregnant
        self.__life_states = {'Open', 'Pregnant', 'DoNotBreed', 'Exit'}
        self.__total_states = {}

    def probability_state_change(self, dim=None, ln=None, dp=None):

        if dim is None:
            dim = self.__current_days_in_milk
        if ln is None:
            ln = self.__current_lactation_number
        if dp is None:
            dp = self.__current_days_pregnant

        if ln == 0:
            return self.__probability_state_change_heifer(dim, dp)
        elif ln == 1:
            return self.__probability_state_change_first_lactation(dim, dp)
        elif ln >= 2:
            return self.__probability_state_change_new_lactation(dim, dp)
        else:
            #
            return

    def __probability_state_change_heifer(self, days_in_milk, days_pregnant):
        age_at_first_heat = DigitalHerd.get_age_at_first_heat(self.__herd)

        def __probability_heat():
            if days_in_milk < age_at_first_heat or days_pregnant > 0:
                return 0.0
            else:
                return 0.8

        def __probability_pregnancy():
            ##
            return 0.5

        return __probability_heat() * __probability_pregnancy()

    def __probability_state_change_first_lactation(self, days_in_milk, days_pregnant):
        vwp = DigitalHerd.get_voluntary_waiting_period(self.__herd)

        def __probability_heat():
            if days_in_milk < vwp or days_pregnant > 0:
                return 0.0
            else:
                return 0.8

        def __probability_pregnancy():
            ##
            return 0.5

        return __probability_heat() * __probability_pregnancy()

    def __probability_state_change_new_lactation(self, days_in_milk, days_pregnant):
        vwp = DigitalHerd.get_voluntary_waiting_period(self.__herd)

        def __probability_heat():
            if days_in_milk < vwp or days_pregnant > 0:
                return 0.0
            else:
                return 0.8

        def __probability_pregnancy():
            ##
            return 0.5

        return __probability_heat() * __probability_pregnancy()

    def __str__(self):
        return f""

    # def __repr__(self):
    #     return 'Digital twin of a dairy cow'

    def get_current_days_in_milk(self):
        return self.__current_days_in_milk

    def get_current_days_pregnant(self):
        return self.__current_days_pregnant

    def get_current_lactation_number(self):
        return self.__current_lactation_number

    def age(self, days=1):
        for i in range(days):
            self.__current_days_in_milk += 1
            new_open_state = f"Open_{self.__current_days_in_milk}_{self.__current_lactation_number}"
            new_pregnant_state = f"Pregnant_{self.__current_days_in_milk}_{self.__current_lactation_number}"
            new_dnb_state = f"Do_Not_Breed{self.__current_days_in_milk}_{self.__current_lactation_number}"
            new_exit_state = f"Exit{self.__current_days_in_milk}_{self.__current_lactation_number}"
            prob_state_change = self.probability_state_change()
            new_states = {
                new_open_state: [],
                new_pregnant_state: [],
                new_dnb_state: [],
                new_exit_state: []
            }
            self.__total_states.update(new_states)




