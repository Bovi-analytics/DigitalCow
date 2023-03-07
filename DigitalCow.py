import numpy as np
from DigitalHerd import DigitalHerd
from decimal import Decimal


class DigitalCow(DigitalHerd):

    def __init__(self, days_in_milk=0, lactation_number=0, current_days_pregnant=0,
                 age_at_first_heat=None, state='Open'):
        super().__init__()
        self._herd = []
        self._current_days_in_milk = days_in_milk
        self._current_lactation_number = lactation_number
        self._current_days_pregnant = current_days_pregnant
        self._current_state = state
        self._age_at_first_heat = age_at_first_heat
        self.__life_states = ['Open', 'Pregnant', 'DoNotBreed', 'Exit']
        self._total_states = ()

    def generate_total_states(self, dim_threshold=1000, ln_threshold=9):
        self._total_states = []
        new_days_in_milk = self._current_days_in_milk
        new_lactation_number = self._current_lactation_number
        while True:
            for state in self.__life_states:
                new_current_state = f"{state}_" \
                                    f"{new_days_in_milk}_" \
                                    f"{new_lactation_number}"
                self._total_states.append(new_current_state)
            if new_days_in_milk == dim_threshold:
                new_days_in_milk = 0
                if new_lactation_number < ln_threshold:
                    new_lactation_number += 1
                else:
                    break
            else:
                new_days_in_milk += 1
        self._total_states = tuple(self._total_states)

    def probability_state_change(self, current_state, new_state,
                                 dim=None, ln=None, dp=None) -> Decimal:
        if new_state.split('_')[0] not in self.__life_states:
            print('Error')
        if dim is None:
            dim = self._current_days_in_milk
        if ln is None:
            ln = self._current_lactation_number
        if dp is None:
            dp = self._current_days_pregnant

        if new_state.split('_')[1] != dim + 1 and new_state.split('_')[2] == ln and \
                current_state.split('_')[0] != 'Exit':
            return Decimal(0)

        if ln == 0:
            return self.__probability_state_change_heifer(current_state, new_state, dim, dp)
        # elif ln == 1:
        #     return self.__probability_state_change_first_lactation(new_state, dim, dp)
        # elif ln >= 2:
        #     return self.__probability_state_change_new_lactation(new_state, dim, dp)
        # else:
        #     #
        #     return

    def __probability_state_change_heifer(self, current_state, new_state, days_in_milk, days_pregnant) -> Decimal:
        age_at_first_heat = self.generate_age_at_first_heat()

        def __probability_heat():
            if days_in_milk < age_at_first_heat or days_pregnant > 0:
                return Decimal(0)
            else:
                return Decimal(0.8)

        def __probability_pregnancy():
            ##
            return Decimal(0.5)

        def __probability_birth():
            return Decimal(0.4)

        def __probability_abortion():
            if days_pregnant > 0:
                return Decimal(0.2)
            else:
                return Decimal(0)

        def __probability_exit():
            return Decimal(0.01)

        def __probability_dnb():
            return Decimal(0.001)

        def __probability_stay_open():
            return Decimal(0.5)

        def __probability_stay_pregnant():
            return Decimal(0.8)

        def __probability_stay_dnb():
            return Decimal(0.6)

        match current_state.split('_')[0]:
            case 'Open':
                match new_state.split('_')[0]:
                    case 'Open':
                        return __probability_stay_open()
                        # chance staying open
                    case 'Pregnant':
                        return __probability_heat() * __probability_pregnancy()
                        # chance becoming pregnant
                    case 'DoNotBreed':
                        return __probability_dnb()
                        # chance becoming dnb
                    case 'Exit':
                        return __probability_exit()
                        # mortality
            case 'Pregnant':
                match new_state.split('_')[0]:
                    case 'Open':
                        if days_pregnant > 279:
                            return __probability_birth()  # * __probability_abortion()
                            # chance aborting or calving
                        else:
                            return __probability_abortion()
                            # chance aborting
                    case 'Pregnant':
                        return __probability_stay_pregnant()
                        # chance staying pregnant
                    case 'DoNotBreed':
                        if days_pregnant > 279:
                            return __probability_birth() * __probability_dnb()
                            # chance calving and dnb or aborting dnb
                        else:
                            return __probability_abortion() * __probability_dnb()
                    case 'Exit':
                        return __probability_exit()
                        # mortality
            case 'DoNotBreed':
                match new_state.split('_')[0]:
                    case 'Open':
                        return Decimal(0)
                    case 'Pregnant':
                        return Decimal(0)
                    case 'DoNotBreed':
                        return __probability_stay_dnb()
                        # chance staying DoNotBreed
                    case 'Exit':
                        return __probability_exit()
                        # chance mortality or culling
            case 'Exit':
                match new_state.split('_')[0]:
                    case 'Exit':
                        return Decimal(1)
                    case ('Open' | 'Pregnant' | 'DoNotBreed'):
                        return Decimal(0)



























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
               f"\tDIM: {self._current_days_in_milk}\n" \
               f"\tLactation number: {self._current_lactation_number}\n" \
               f"\tDays pregnant: {self._current_days_pregnant}\n" \
               f"\tCurrent state: {self._current_state}"

    def __repr__(self):
        return f"DigitalCow(days_in_milk={self._current_days_in_milk}, " \
               f"lactation_number={self._current_lactation_number}, " \
               f"current_days_pregnant={self._current_days_pregnant}, " \
               f"age_at_first_heat={self._age_at_first_heat}, " \
               f"state={self._current_state})"

    @property
    def current_days_in_milk(self):
        return self._current_days_in_milk

    @current_days_in_milk.setter
    def current_days_in_milk(self, dim):
        self._current_days_in_milk = dim

    @property
    def current_days_pregnant(self):
        return self._current_days_pregnant

    @current_days_pregnant.setter
    def current_days_pregnant(self, dp):
        self._current_days_pregnant = dp

    @property
    def current_lactation_number(self):
        return self._current_lactation_number

    @current_lactation_number.setter
    def current_lactation_number(self, ln):
        self._current_lactation_number = ln

    @property
    def age_at_first_heat(self):
        return self._age_at_first_heat

    @age_at_first_heat.setter
    def age_at_first_heat(self, age_at_first_heat):
        self._age_at_first_heat = age_at_first_heat

    @property
    def current_state(self):
        return f"{self._current_state}_" \
               f"{self._current_days_in_milk}_" \
               f"{self._current_lactation_number}"

    @current_state.setter
    def current_state(self, state):
        self._current_state = state

    @property
    def total_states(self):
        return self._total_states

    @total_states.setter
    def total_states(self, states):
        self._total_states = states


def possible_new_states(current_state: str) -> tuple | str:
    # Make a list with all new states new_current_state can transition to.
    state, days_in_milk, lactation_number = current_state.split('_')
    days_in_milk = int(days_in_milk)
    lactation_number = int(lactation_number)
    match state:
        case 'Open':
            return (
                f"Open_{days_in_milk + 1}_{lactation_number}",
                f"Pregnant_{days_in_milk + 1}_{lactation_number}",
                f"DoNotBreed_{days_in_milk + 1}_{lactation_number}",
                f"Exit_{days_in_milk + 1}_{lactation_number}"
            )
        case 'Pregnant':
            return (
                f"Open_{days_in_milk + 1}_{lactation_number}",
                f"Pregnant_{days_in_milk + 1}_{lactation_number}",
                f"DoNotBreed_{days_in_milk + 1}_{lactation_number}",
                f"Exit_{days_in_milk + 1}_{lactation_number}",
                f"Open_0_{lactation_number + 1}",
                f"DoNotBreed_0_{lactation_number + 1}"
            )
        case 'DoNotBreed':
            return (
                f"DoNotBreed_{days_in_milk + 1}_{lactation_number}",
                f"Exit_{days_in_milk + 1}_{lactation_number}"
            )
        case 'Exit':
            return (
                f"Exit_{days_in_milk}_{lactation_number}"
            )
        case _:
            raise Exception
