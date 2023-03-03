import numpy as np
from DigitalHerd import DigitalHerd
from decimal import Decimal


class DigitalCow(DigitalHerd):

    def __init__(self, days_in_milk=0, lactation_number=0, current_days_pregnant=0,
                 age_at_first_heat=None, state='Open'):
        super().__init__()
        self.herd = None
        self.current_days_in_milk = days_in_milk
        self.current_lactation_number = lactation_number
        self.current_days_pregnant = current_days_pregnant
        self.current_state = state
        self._age_at_first_heat = age_at_first_heat
        self.__life_states = ['Open', 'Pregnant', 'DoNotBreed', 'Exit']
        self.total_states = ()

    def generate_total_states(self, days=1):
        self.total_states = []
        new_days_in_milk = self.current_days_in_milk
        new_lactation_number = self.current_lactation_number
        for day in range(days):
            for state in self.__life_states:
                new_current_state = f"{state}_{new_days_in_milk}_{new_lactation_number}"

                # Make a list with all new states new_current_state can transition to.
                match state:
                    case 'Open':
                        new_states = [
                            f"Open_{new_days_in_milk + 1}_{new_lactation_number}",
                            f"Pregnant_{new_days_in_milk + 1}_{new_lactation_number}",
                            f"DoNotBreed_{new_days_in_milk + 1}_{new_lactation_number}",
                            f"Exit_{new_days_in_milk + 1}_{new_lactation_number}"
                        ]
                    case 'Pregnant':
                        new_states = [
                            f"Open_{new_days_in_milk + 1}_{new_lactation_number}",
                            f"Pregnant_{new_days_in_milk + 1}_{new_lactation_number}",
                            f"DoNotBreed_{new_days_in_milk + 1}_{new_lactation_number}",
                            f"Exit_{new_days_in_milk + 1}_{new_lactation_number}",
                            f"Open_0_{new_lactation_number + 1}",
                            f"DoNotBreed_0_{new_lactation_number + 1}"
                        ]
                    case 'DoNotBreed':
                        new_states = [
                            f"DoNotBreed_{new_days_in_milk + 1}_{new_lactation_number}",
                            f"Exit_{new_days_in_milk + 1}_{new_lactation_number}"
                        ]
                    case 'Exit':
                        new_states = [
                            f"Exit_{new_days_in_milk}_{new_lactation_number}"
                        ]
                    case _:
                        new_states = []
                        print('Error')

                self.total_states.append(new_current_state)
                new_days_in_milk += 1
        self.total_states = tuple(self.total_states)

    def probability_state_change(self, current_state, new_state, dim=None, ln=None, dp=None):
        if new_state.split('_')[0] not in self.__life_states:
            print('Error')
        if dim is None:
            dim = self.current_days_in_milk
        if ln is None:
            ln = self.current_lactation_number
        if dp is None:
            dp = self.current_days_pregnant

        if new_state.split('_')[1] != dim + 1 and new_state.split('_')[2] == ln and \
                current_state.split('_')[0] != 'Exit':
            return 0.0

        if ln == 0:
            return self.__probability_state_change_heifer(current_state, new_state, dim, dp)
        # elif ln == 1:
        #     return self.__probability_state_change_first_lactation(new_state, dim, dp)
        # elif ln >= 2:
        #     return self.__probability_state_change_new_lactation(new_state, dim, dp)
        # else:
        #     #
        #     return

    def __probability_state_change_heifer(self, current_state, new_state, days_in_milk, days_pregnant):
        age_at_first_heat = self.generate_age_at_first_heat()

        def __probability_heat():
            if days_in_milk < age_at_first_heat or days_pregnant > 0:
                return 0.0
            else:
                return 0.8

        def __probability_pregnancy():
            ##
            return 0.5

        def __probability_birth():
            return 0.4

        def __probability_abortion():
            if days_pregnant > 0:
                return 0.2
            else:
                return 0.0

        def __probability_exit():
            return 0.01

        def __probability_dnb():
            return 0.0

        match current_state.split('_')[0]:
            case 'Open':
                match new_state.split('_')[0]:
                    case 'Open':
                        return  # chance staying open
                    case 'Pregnant':
                        return __probability_heat() * __probability_pregnancy()  # chance getting pregnant
                    case 'DoNotBreed':
                        return __probability_dnb()  # chance dnb
                    case 'Exit':
                        return __probability_exit()  # mortality
            case 'Pregnant':
                match new_state.split('_')[0]:
                    case 'Open':
                        if days_pregnant > 279:
                            return __probability_birth()  # * __probability_abortion() # either aborting or calving
                        else:
                            return __probability_abortion()  # aborting
                    case 'Pregnant':
                        return  # chance staying pregnant
                    case 'DoNotBreed':
                        if days_pregnant > 279:
                            return __probability_birth() * __probability_dnb()  # either calving and dnb or aborting dnb
                        else:
                            return __probability_abortion() * __probability_dnb()
                    case 'Exit':
                        return __probability_exit()  # mortality
            case 'DoNotBreed':
                match new_state.split('_')[0]:
                    case 'Open':
                        return 0.0
                    case 'Pregnant':
                        return 0.0
                    case 'DoNotBreed':
                        return  # staying DoNotBreed
                    case 'Exit':
                        return __probability_exit()  # either mortality or culling
            case 'Exit':
                match new_state.split('_')[0]:
                    case 'Exit':
                        return 1.0
                    case ('Open' | 'Pregnant' | 'DoNotBreed'):
                        return 0.0



























    def __probability_state_change_first_lactation(self, new_state, days_in_milk, days_pregnant):

        def __probability_heat():
            if days_in_milk < self.voluntary_waiting_period or days_pregnant > 0:
                return 0.0
            else:
                return 0.8

        def __probability_pregnancy():
            ##
            return 0.5

        def __probability_abortion():
            if days_pregnant > 0:
                return 0.2
            else:
                return 0.0

        def __probability_exit():
            return 0.01

        def __probability_dnb():
            return 0.0

        return __probability_heat() * __probability_pregnancy()

    def __probability_state_change_new_lactation(self, new_state, days_in_milk, days_pregnant):

        def __probability_heat():
            if days_in_milk < self.voluntary_waiting_period or days_pregnant > 0:
                return 0.0
            else:
                return 0.8

        def __probability_pregnancy():
            ##
            return 0.5

        def __probability_abortion():
            if days_pregnant > 0:
                return 0.2
            else:
                return 0.0

        def __probability_exit():
            return 0.01

        def __probability_dnb():
            return 0.0

        return __probability_heat() * __probability_pregnancy()

    def __str__(self):
        return f"DigitalCow:\n" \
               f"\tDIM: {self.current_days_in_milk}\n" \
               f"\tLactation number: {self.current_lactation_number}\n" \
               f"\tDays pregnant: {self.current_days_pregnant}\n" \
               f"\tCurrent state: {self.current_state}"

    def __repr__(self):
        return f"DigitalCow(days_in_milk={self.current_days_in_milk}, " \
               f"lactation_number={self.current_lactation_number}, " \
               f"current_days_pregnant={self.current_days_pregnant}, " \
               f"age_at_first_heat={self._age_at_first_heat}, " \
               f"state={self.current_state})"

    @property
    def current_days_in_milk(self):
        return self.current_days_in_milk

    @current_days_in_milk.setter
    def current_days_in_milk(self, dim):
        self.current_days_in_milk = dim

    @property
    def current_days_pregnant(self):
        return self.current_days_pregnant

    @current_days_pregnant.setter
    def current_days_pregnant(self, dp):
        self.current_days_pregnant = dp

    @property
    def current_lactation_number(self):
        return self.current_lactation_number

    @current_lactation_number.setter
    def current_lactation_number(self, ln):
        self.current_lactation_number = ln

    @property
    def age_at_first_heat(self):
        return self._age_at_first_heat

    @age_at_first_heat.setter
    def age_at_first_heat(self, age_at_first_heat):
        self._age_at_first_heat = age_at_first_heat

    @property
    def current_state(self):
        return f"{self.current_state}_{self.current_days_in_milk}_{self.current_lactation_number}"

    @current_state.setter
    def current_state(self, state):
        self.current_state = state

    @property
    def total_states(self):
        return self.total_states

    @total_states.setter
    def total_states(self, states):
        self.__total_states = states
