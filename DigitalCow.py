from _decimal import Decimal
from decimal import Decimal, getcontext
from typing import Tuple

import DigitalHerd
import DairyState
import math


class DigitalCow:

    def __init__(self, days_in_milk=0, lactation_number=0, current_days_pregnant=0,
                 age_at_first_heat=None, herd=None, state='Open'):
        """

        :param days_in_milk:
        :param lactation_number:
        :param current_days_pregnant:
        :param age_at_first_heat:
        :param herd:
        :param state:
        """
        self._herd = herd
        self._current_state = DairyState.State(state, days_in_milk,
                                               lactation_number,
                                               current_days_pregnant)
        self._age_at_first_heat = age_at_first_heat
        self.__life_states = ['Open', 'Pregnant', 'DoNotBreed', 'Exit']
        self._total_states = ()
        self._milkbot_variables = (Decimal("30.0"), Decimal("0.5"),
                                   Decimal("0.0"), Decimal("0.01"))

    def generate_total_states(self, dim_limit=999, ln_limit=8) -> None:
        """

        :param dim_limit:
        :param ln_limit:
        :return:
        """
        self._total_states = []
        new_days_in_milk = self.current_days_in_milk
        new_lactation_number = self.current_lactation_number
        days_pregnant_limit = self.current_days_pregnant + 1
        new_days_pregnant = 1
        # pregnant? !!!!
        #
        # !!!!!!!!!
        while not new_lactation_number > ln_limit:
            for state in self.__life_states:
                if state == 'Pregnant':
                    if new_days_in_milk > self.voluntary_waiting_period:
                        while not new_days_pregnant > days_pregnant_limit:
                            new_current_state = DairyState.State(state,
                                                                 new_days_in_milk,
                                                                 new_lactation_number,
                                                                 new_days_pregnant)
                            self._total_states.append(new_current_state)
                            new_days_pregnant += 1
                        new_days_pregnant = 1
                        days_pregnant_limit += 1
                    else:
                        new_current_state = DairyState.State(state, new_days_in_milk,
                                                             new_lactation_number)
                        self._total_states.append(new_current_state)
                else:
                    new_current_state = DairyState.State(state, new_days_in_milk,
                                                         new_lactation_number)
                    self._total_states.append(new_current_state)
            if new_days_in_milk == dim_limit:
                new_days_in_milk = 0
                new_lactation_number += 1
            else:
                new_days_in_milk += 1
        self._total_states = tuple(self._total_states)

    def milk_production(self, days_in_milk: int):
        """

        :param days_in_milk:
        :return:
        """
        # precision
        scale = self._milkbot_variables[0]
        ramp = self._milkbot_variables[1]
        offset = self._milkbot_variables[2]
        decay = self._milkbot_variables[3]
        return scale * Decimal(Decimal("1") - (pow(Decimal(math.e),
                                                   ((offset -
                                                     Decimal(days_in_milk))
                                                    / ramp)
                                                   )
                                               / Decimal("2"))
                               ) * pow(Decimal(math.e),
                                       -decay * Decimal(days_in_milk))

    def probability_state_change(self, current_state, new_state) -> Decimal:
        """

        :param current_state:
        :param new_state:
        :return:
        """
        getcontext().prec = 4

        if new_state.state not in self.__life_states:
            raise ValueError("new_state must be defined in self.__life_states")

        vwp = self.voluntary_waiting_period
        if new_state.days_in_milk < vwp and (new_state.state == 'Pregnant' or
                                             current_state.state == 'Pregnant'):
            return Decimal("0")
        # !!!!!!!
        if (new_state.days_in_milk != current_state.days_in_milk + 1 and
                new_state.lactation_number != current_state.lactation_number + 1
                and current_state.state != 'Exit'):
            return Decimal("0")
        if new_state not in self.possible_new_states(current_state):
            return Decimal("0")

        def __probability_insemination():
            if current_state.days_in_milk < vwp:
                return Decimal("0")
            else:
                match current_state.lactation_number:
                    case 0:
                        return Decimal("0.7")
                    case range(1, 9):
                        return Decimal("0.5")

        def __probability_pregnancy():
            match current_state.lactation_number:
                case 0:
                    return Decimal("0.45")
                case range(1, 9):
                    return Decimal("0.35")

        def __probability_birth():
            # !!!!!!
            if current_state.days_pregnant > 282:
                return Decimal("1")
            else:
                return Decimal("0")

        def __probability_abortion():
            # dp 30-45 12.5%
            # dp 46-180 9.9%
            # dp 181-282 2%
            if 29 < current_state.days_pregnant < 45:
                return Decimal("0.0083333")
            elif 45 < current_state.days_pregnant < 180:
                return Decimal("0.0007333")
            elif 180 < current_state.days_pregnant < 283:
                return Decimal("0.0001961")
            else:
                return Decimal("0")

        def __probability_above_insemination_cutoff():
            # !!!!!
            if current_state.state == 'Open' and current_state.days_in_milk > self.herd.insemination_dim_cutoff:
                return Decimal("1")
            else:
                return Decimal("0")

        def __probability_milk_below_threshold():
            if current_state.milk_output < self.herd.milk_threshold and not current_state.days_in_milk < vwp:
                return Decimal("1")
            else:
                return Decimal("0")

        def __probability_death():
            # 5% / y
            # !!!!!!!!!!!!!!
            match current_state.lactation_number:
                case 0:
                    return Decimal("0.0001369")
                case range(1, 9):
                    return Decimal("0")

        match current_state.state:
            case 'Open':
                match new_state.state:
                    case 'Open':
                        if current_state.days_in_milk < vwp:
                            return (Decimal("1") - __probability_death()) * (Decimal(
                                "1") - __probability_milk_below_threshold())
                        else:
                            return (Decimal("1") - __probability_death()) * (
                                    Decimal("1") - (
                                    __probability_insemination() * __probability_pregnancy())) * (
                                    Decimal(
                                        "1") - __probability_milk_below_threshold()) * (
                                    Decimal(
                                        "1") - __probability_above_insemination_cutoff())
                        # chance staying open
                    case 'Pregnant':
                        return (
                                __probability_insemination() * __probability_pregnancy()) * (
                                Decimal("1") - __probability_death()) * (Decimal(
                            "1") - __probability_milk_below_threshold()) * (Decimal(
                            "1") - __probability_above_insemination_cutoff())
                        # chance becoming pregnant
                    case 'DoNotBreed':
                        return __probability_above_insemination_cutoff() * (
                                Decimal("1") - __probability_death()) * (Decimal(
                            "1") - __probability_milk_below_threshold())
                        # chance becoming dnb
                    case 'Exit':
                        # !!!!!!!
                        if current_state.milk_output < self.herd.milk_threshold and not current_state.days_in_milk < vwp:
                            return Decimal("1")
                        else:
                            return __probability_death()
                        # chance mortality or culling

            case 'Pregnant':
                match new_state.state:
                    case 'Open':
                        if new_state.lactation_number == current_state.lactation_number + 1:
                            return __probability_birth() * (
                                    Decimal("1") - __probability_death())
                        else:
                            return __probability_abortion() * (
                                    Decimal("1") - __probability_death())
                    case 'Pregnant':
                        return (Decimal("1") - __probability_death()) * (
                                Decimal("1") - __probability_abortion())
                        # chance staying pregnant
                    case 'DoNotBreed':
                        # !!!!!!!
                        return Decimal("0")
                    case 'Exit':
                        # !!!!!!!
                        if current_state.milk_output < self.herd.milk_threshold and not current_state.days_in_milk < vwp:
                            return Decimal("1")
                        else:
                            return __probability_death()
                        # chance mortality or culling

            case 'DoNotBreed':
                match new_state.state:
                    case 'Open':
                        return Decimal("0")
                    case 'Pregnant':
                        return Decimal("0")
                    case 'DoNotBreed':
                        return Decimal("1") - __probability_milk_below_threshold()
                        # chance staying DoNotBreed
                    case 'Exit':
                        # !!!!!!!
                        if current_state.milk_output < self.herd.milk_threshold and not current_state.days_in_milk < vwp:
                            return Decimal("1")
                        else:
                            return __probability_death()
                        # chance mortality or culling

            case 'Exit':
                # !!!!!!!
                match new_state.state:
                    case 'Exit':
                        return Decimal("1")
                    case ('Open' | 'Pregnant' | 'DoNotBreed'):
                        return Decimal("0")

    def __str__(self):
        return f"DigitalCow:\n" \
               f"\tDIM: {self.current_days_in_milk}\n" \
               f"\tLactation number: {self.current_lactation_number}\n" \
               f"\tDays pregnant: {self.current_days_pregnant}\n" \
               f"\tHerd: {self._herd}\n" \
               f"\tCurrent state: {self.current_life_state}"

    def __repr__(self):
        return f"DigitalCow(days_in_milk={self.current_days_in_milk}, " \
               f"lactation_number={self.current_lactation_number}, " \
               f"current_days_pregnant={self.current_days_pregnant}, " \
               f"age_at_first_heat={self._age_at_first_heat}, " \
               f"herd={self._herd}, " \
               f"state={self.current_life_state})"

    @property
    def herd(self) -> DigitalHerd.DigitalHerd:
        return self._herd

    @herd.setter
    def herd(self, herd):
        if isinstance(herd, DigitalHerd.DigitalHerd):
            self._herd = herd
            self._herd.add_to_herd([self])

    @property
    def current_days_in_milk(self) -> int:
        return self._current_state.days_in_milk

    @current_days_in_milk.setter
    def current_days_in_milk(self, dim):
        self._current_state.days_in_milk = dim

    @property
    def current_days_pregnant(self) -> int:
        return self._current_state.days_pregnant

    @current_days_pregnant.setter
    def current_days_pregnant(self, dp):
        self._current_state.days_pregnant = dp

    @property
    def current_lactation_number(self) -> int:
        return self._current_state.lactation_number

    @current_lactation_number.setter
    def current_lactation_number(self, ln):
        self._current_state.lactation_number = ln

    @property
    def age_at_first_heat(self) -> int | None:
        if self._age_at_first_heat is None:
            return self._age_at_first_heat
        else:
            return int(self._age_at_first_heat)

    @age_at_first_heat.setter
    def age_at_first_heat(self, age_at_first_heat):
        self._age_at_first_heat = age_at_first_heat

    @property
    def current_life_state(self) -> str:
        return self._current_state.state

    @current_life_state.setter
    def current_life_state(self, state):
        if isinstance(state, DairyState.State):
            self._current_state = state
        elif type(state) == str:
            self._current_state.state = state

    @property
    def current_state(self) -> DairyState.State:
        return self._current_state

    @property
    def total_states(self) -> tuple:
        return self._total_states

    @total_states.setter
    def total_states(self, states):
        self._total_states = states

    @property
    def milkbot_variables(self) -> tuple[Decimal, Decimal, Decimal, Decimal]:
        return self._milkbot_variables

    @milkbot_variables.setter
    def milkbot_variables(self, var):
        if type(var) == tuple[Decimal] and len(var) == 4:
            self._milkbot_variables = var

    @property
    def voluntary_waiting_period(self) -> int:
        if self.current_state.lactation_number == 0:
            if self._age_at_first_heat is None:
                self._age_at_first_heat = self.herd.generate_age_at_first_heat()
            return self.age_at_first_heat
        else:
            return self.herd.voluntary_waiting_period

    def possible_new_states(self, current_state: DairyState.State) -> tuple:
        """

        :param current_state:
        :return:
        """
        if current_state is None:
            current_state = self.current_state
        match current_state.state:
            case 'Open':
                return (
                    DairyState.State('Open', current_state.days_in_milk + 1,
                                     current_state.lactation_number),
                    DairyState.State('Pregnant', current_state.days_in_milk + 1,
                                     current_state.lactation_number, 1),
                    DairyState.State('DoNotBreed', current_state.days_in_milk + 1,
                                     current_state.lactation_number),
                    DairyState.State('Exit', current_state.days_in_milk + 1,
                                     current_state.lactation_number)
                )
            case 'Pregnant':
                return (
                    DairyState.State('Open', current_state.days_in_milk + 1,
                                     current_state.lactation_number),
                    DairyState.State('Pregnant', current_state.days_in_milk + 1,
                                     current_state.lactation_number,
                                     current_state.days_pregnant + 1),
                    DairyState.State('DoNotBreed', current_state.days_in_milk + 1,
                                     current_state.lactation_number),
                    DairyState.State('Exit', current_state.days_in_milk + 1,
                                     current_state.lactation_number),
                    DairyState.State('Open', 0, current_state.lactation_number + 1),
                    DairyState.State('DoNotBreed', 0,
                                     current_state.lactation_number + 1)
                )
            case 'DoNotBreed':
                return (
                    DairyState.State('DoNotBreed', current_state.days_in_milk + 1,
                                     current_state.lactation_number),
                    DairyState.State('Exit', current_state.days_in_milk + 1,
                                     current_state.lactation_number)
                )
            case 'Exit':
                return (
                    DairyState.State('Exit', current_state.days_in_milk,
                                     current_state.lactation_number),
                )
            case _:
                raise ValueError('The current state given is invalid.')
