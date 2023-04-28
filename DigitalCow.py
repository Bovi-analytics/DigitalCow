"""
:module: DigitalCow
   :synopsis: This module contains the DigitalCow class which represents a cow in a dairy herd.

:module author: Gabe van den Hoeven

======================
How To Use This Module
======================
(See the individual classes, methods, and attributes for details.)

1. Import the class DigitalCow: \n
``import DigitalCow.DigitalCow`` or ``from
DigitalCow import DigitalCow``.

You will also need the DigitalHerd class from the DigitalHerd module.

2. Create a DigitalCow object:

a) `Without a DigitalHerd object`:
        1) Without parameters:\n
        ``cow = DigitalCow()``\n
        2) With parameters:\n
        ``cow = DigitalCow(days_in_milk=245, lactation_number=3,
        current_days_pregnant=165, age_at_first_heat=371, state='Pregnant')``\n

b) `With a DigitalHerd object`:
    1) Without parameters\n
    a_herd = DigitalHerd()\n
    cow = DigitalCow(herd=a_herd)\n

    2) With parameters\n
    a_herd = DigitalHerd(vwp=50, insemination_window=300,
    milk_threshold=Decimal("30"))\n
    cow = DigitalCow(days_in_milk=67, lactation_number=1,
    current_days_pregnant=0, herd=a_herd, state='Open')\n

c) `Set the herd of the DigitalCow`:
    1) Sets the DigitalHerd as the herd of the DigitalCow\n

    ``a_herd = DigitalHerd()``\n
    ``cow = DigitalCow(herd=a_herd)``\n

    2) Overwrites the DigitalHerd as the herd of the DigitalCow\n

    ``a_herd = DigitalHerd()``\n
    ``another_herd = DigitalHerd()``\n
    ``cow = DigitalCow(herd=a_herd)``\n
    ``cow.herd = another_herd``\n

    3) Adds the DigitalCow objects to the DigitalHerd and sets the DigitalHerd as
    the herd of each DigitalCow

    ``a_herd = DigitalHerd()``\n
    ``cow = DigitalCow()``\n
    ``cow2 = DigitalCow()``\n
    ``a_herd.add_to_herd(cows=[cow, cow2])``\n

    4) Overwrites the list of DigitalCow objects as the herd of the DigitalHerd

    ``a_herd = DigitalHerd()``\n
    ``cow = DigitalCow()``\n
    ``cow2 = DigitalCow()``\n
    ``a_herd.herd = [cow, cow2]``\n

3.

"""

from decimal import Decimal
import DigitalHerd
import DairyState
import math
from typing import Generator


class DigitalCow:
    """
    A digital twin of a cow used for simulation.

    Attributes:
        _herd : DigitalHerd.DigitalHerd
        The DigitalHerd instance representing the herd that the cow
        belongs to.
        _current_state : int
            The State instance representing the current state of the cow.
        _age_at_first_heat: int or None
            The age in days, at which the cow had her first
        heat. Defaults to None if it has not happened yet.
        __life_states: list of str
            A list of all possible life states the cow can be in.
        _total_states : tuple of DairyState.State
            A tuple of 'State' objects containing all possible states this cow can
            be in or transition to.
            Filled by 'self.generate_total_states()'.
        _milkbot_variables : tuple of Decimal
            A tuple of 4 'Decimal' numbers used for the 'self.milk_production'
            function.
            index = 0: scale,
            index = 1: ramp,
            index = 2: offset,
            index = 3: decay.
            Filled by 'self.__set_milkbot_variables()'.

    """

    def __init__(self, days_in_milk=0, lactation_number=0, current_days_pregnant=0,
                 age_at_first_heat=None, herd=None, state='Open', precision=10):
        """
        Initializes a new instance of a DigitalCow object.

        :param days_in_milk: The amount of days since the cow's last calving,
            or it's birth if it has not calved yet. Defaults to 0.
        :type days_in_milk: int
        :param lactation_number: The amount of lactation cycles the cow has completed.
            Defaults to 0.
        :type lactation_number: int
        :param current_days_pregnant: The amount of days that the cow is pregnant.
            Defaults to 0.
        :type current_days_pregnant: int
        :param age_at_first_heat: The age in days, at which the cow had her first heat.
            Defaults to None if it has not happened yet.
        :type age_at_first_heat: int or None
        :param herd: The herd to which the cow belongs. Contains variables that apply to all cows in the herd.
        :type herd: DigitalHerd.DigitalHerd
        :param state: The life state of the cow.
            This state should be one of the states defined in self.__life_states. Defaults to 'Open'.
        :type state: str
        :param precision: The amount of decimal places used for calculating transition probabilities. Defaults to 10.
        :type precision: int
        """
        self.herd = herd
        self.__life_states = ['Open', 'Pregnant', 'DoNotBreed', 'Exit']
        self._age_at_first_heat = age_at_first_heat
        self._total_states = None
        self._milkbot_variables = None
        self._generated_days_in_milk = None
        self._generated_lactation_numbers = None
        self._generated_days_pregnant_limit = None
        self.__decimalize_precision(precision)
        self.__set_milkbot_variables(lactation_number)
        temp_state = DairyState.State(state, days_in_milk, lactation_number,
                                      current_days_pregnant, Decimal("0"))
        milk_output = self.milk_production(temp_state)
        self._current_state = DairyState.State(state, days_in_milk,
                                               lactation_number,
                                               current_days_pregnant, milk_output)

    def generate_total_states(self, dim_limit=None, ln_limit=None) -> None:
        """
        Generates a tuple of DairyState.State objects that represent all possible states of the DigitalCow instance.

        :param dim_limit: The limit of days in milk for which states should be generated.
        :type dim_limit: int or None
        :param ln_limit: The limit of lactation numbers for which states should be generated.
        :type ln_limit: int or None

        """
        if dim_limit is None:
            dim_limit = self.herd.days_in_milk_limit
        if ln_limit is None:
            ln_limit = self.herd.lactation_number_limit
        total_states = []
        days_in_milk = 0
        lactation_number = 0
        days_pregnant_start = 1
        days_pregnant = 1
        simulated_dp_limit = 1
        dp_limit = None
        stop_pregnant_state = False
        last_pregnancy = False
        not_heifer = False

        while lactation_number <= ln_limit:
            dp_limit = self.herd.get_days_pregnant_limit(lactation_number)
            vwp = self.herd.get_voluntary_waiting_period(lactation_number)
            insemination_window = self.herd.get_insemination_window(lactation_number)
            for life_state in self.__life_states:
                self.__set_milkbot_variables(lactation_number)
                if life_state == 'Pregnant':
                    # The milk output may differ if the cow is pregnant
                    temp_state = DairyState.State(life_state, days_in_milk,
                                                  lactation_number, days_pregnant,
                                                  Decimal("0"))
                else:
                    temp_state = DairyState.State(life_state, days_in_milk,
                                                  lactation_number, 0, Decimal("0"))
                milk_output = self.milk_production(temp_state)
                # Calculates the milk output for the cow at every state.

                match life_state:
                    case 'Open':
                        if days_in_milk <= vwp + insemination_window:
                            new_state = DairyState.State(life_state, days_in_milk,
                                                         lactation_number, 0,
                                                         milk_output)
                            total_states.append(new_state)

                    case 'Pregnant':
                        if vwp < days_in_milk <= vwp + insemination_window + dp_limit:
                            if not stop_pregnant_state:
                                while days_pregnant <= simulated_dp_limit:
                                    new_state = DairyState.State(life_state,
                                                                 days_in_milk,
                                                                 lactation_number,
                                                                 days_pregnant,
                                                                 milk_output)
                                    total_states.append(new_state)
                                    days_pregnant += 1
                                if vwp + insemination_window < days_in_milk < vwp + insemination_window + dp_limit:
                                    days_pregnant_start += 1
                                days_pregnant = days_pregnant_start
                                if simulated_dp_limit != dp_limit:
                                    simulated_dp_limit += 1
                                elif lactation_number == ln_limit:
                                    if days_pregnant_start > dp_limit:
                                        stop_pregnant_state = True
                                    elif days_in_milk == vwp + dp_limit + 1:
                                        last_pregnancy = True
                    case 'DoNotBreed':
                        if days_in_milk > vwp + insemination_window and lactation_number != 0:
                            new_state = DairyState.State(life_state, days_in_milk,
                                                         lactation_number, 0,
                                                         milk_output)
                            total_states.append(new_state)
                            if last_pregnancy:
                                self.__set_milkbot_variables(lactation_number + 1)
                                temp_state = DairyState.State(life_state, days_in_milk,
                                                              lactation_number + 1, 0,
                                                              Decimal("0"))
                                milk_output = self.milk_production(temp_state)
                                new_state = DairyState.State(life_state, days_in_milk,
                                                             lactation_number + 1, 0,
                                                             milk_output)
                                total_states.append(new_state)
                    case 'Exit':
                        new_state = DairyState.State(life_state, days_in_milk,
                                                     lactation_number, 0,
                                                     milk_output)
                        total_states.append(new_state)
                        if last_pregnancy:
                            new_state = DairyState.State(life_state, days_in_milk,
                                                         lactation_number + 1, 0, milk_output)
                            total_states.append(new_state)

            if days_in_milk == dim_limit - 1 and not_heifer:
                new_state = DairyState.State('Exit', dim_limit,
                                             lactation_number, 0,
                                             Decimal("0"))
                total_states.append(new_state)
                if lactation_number == ln_limit:
                    new_state = DairyState.State('Exit', dim_limit,
                                                 lactation_number + 1, 0,
                                                 Decimal("0"))
                    total_states.append(new_state)
                days_in_milk = 0
                days_pregnant = 1
                days_pregnant_start = 1
                simulated_dp_limit = 1
                lactation_number += 1
            else:
                days_in_milk += 1
            if days_in_milk == vwp + insemination_window + dp_limit + 2 and lactation_number == 0:
                days_in_milk = 0
                days_pregnant = 1
                days_pregnant_start = 1
                simulated_dp_limit = 1
                lactation_number += 1
                not_heifer = True

        self.total_states = tuple(total_states)
        self._generated_days_in_milk = dim_limit
        self._generated_lactation_numbers = ln_limit
        self._generated_days_pregnant_limit = dp_limit

    def milk_production(self, state: DairyState.State) -> Decimal:
        """
        Calculates milk production for a given state using the
        milkbot algorithm.

        :param state: A state object for which milk production must be calculated.
        :type state: DairyState.State
        :returns: The milk production for the given days in milk.
            :rtype decimal.Decimal
        """
        if state.lactation_number == 0 or state.state == 'Exit':
            return Decimal("0")
        scale = self._milkbot_variables[0]
        ramp = self._milkbot_variables[1]
        offset = self._milkbot_variables[2]
        decay = self._milkbot_variables[3]
        return Decimal(scale * Decimal(Decimal("1") - (pow(Decimal(math.e), ((offset - Decimal(state.days_in_milk)) / ramp)) / Decimal("2"))) * pow(Decimal(math.e), -decay * Decimal(state.days_in_milk))).quantize(self._precision)

    def probability_state_change(self, state_from: DairyState.State,
                                 state_to: DairyState.State) -> Decimal:
        """
        Calculates the probability of transitioning from state_from to state_to.

        :param state_from: The state from which to transition.
        :type state_from: DairyState.State
        :param state_to: The state to transition into.
        :type state_to: DairyState.State
        :returns: The probability of transitioning from state_from to state_to.
            :rtype: decimal.Decimal
        :raises ValueError: If the state is not defined in self.__life_states.
        """
        if state_to.state not in self.__life_states or state_from.state not in self.__life_states:
            raise ValueError("State variables of a State object must be defined in "
                             "self.__life_states")
        vwp = self.herd.get_voluntary_waiting_period(state_from.lactation_number)
        insemination_window = self.herd.get_insemination_window(state_from.lactation_number)
        dp_limit = self.herd.get_days_pregnant_limit(state_from.lactation_number)
        if state_to not in self.possible_new_states(state_from):
            return Decimal("0")
        if state_from.days_in_milk == self._generated_days_in_milk or \
                (state_from.days_in_milk == vwp + insemination_window +
                 self._generated_days_pregnant_limit and
                 state_from.lactation_number == 0) and \
                state_to == DairyState.State('Exit', state_from.days_in_milk,
                                             state_from.lactation_number, 0,
                                             Decimal("0")):
            return Decimal("1")

        def __probability_insemination():
            """Returns the probability for getting inseminated."""
            if state_from.days_in_milk < vwp:
                return Decimal("0")
            else:
                match state_from.lactation_number:
                    case 0:
                        return Decimal("0.7")
                    case ln if 0 < ln:
                        return Decimal("0.5")

        def __probability_pregnancy():
            """Returns the probability of becoming pregnant from an insemination."""
            match state_from.lactation_number:
                case 0:
                    return Decimal("0.45")
                case ln if 0 < ln:
                    return Decimal("0.35")

        def __probability_birth():
            """Returns the probability of calving."""
            if state_from.days_pregnant == dp_limit:
                return Decimal("1")
            else:
                return Decimal("0")

        def __probability_abortion():
            """Returns the probability of aborting a pregnancy."""
            # dp 30-45 12.5%
            # dp 46-180 9.9%
            # dp 181-282 2%
            if state_from.days_pregnant < 30:
                return Decimal("0")
            elif 29 < state_from.days_pregnant < 46:
                return Decimal("0.125") / Decimal("15")
            elif 45 < state_from.days_pregnant < 181:
                return Decimal("0.099") / Decimal("135")
            elif 180 < state_from.days_pregnant < dp_limit + 1:
                return Decimal("0.02") / Decimal(f"{dp_limit - 180}")

        def __probability_above_insemination_cutoff():
            """Returns 1 if the days in milk is above the cutoff for insemination."""
            if state_from.days_in_milk > vwp + insemination_window:
                return Decimal("1")
            else:
                return Decimal("0")

        def __probability_milk_below_threshold():
            """Returns 1 if the milk production falls below the milk threshold for
            staying in the herd."""
            if state_from.milk_output < self.herd.milk_threshold and state_from.lactation_number != 0:
                return Decimal("1")
            else:
                return Decimal("0")

        def __probability_death():
            """Returns the probability of involuntary death."""
            # 0.05 / 1 y = 365 d for perinatal cows
            return Decimal("0.05") / Decimal("365")

        not_death_ = (Decimal("1") - __probability_death())
        pregnant_ = (__probability_insemination() * __probability_pregnancy())
        not_pregnant_ = (Decimal("1") - pregnant_)
        not_aborting_ = (Decimal("1") - __probability_abortion())
        not_below_milk_threshold_ = (
                Decimal("1") - __probability_milk_below_threshold())
        not_above_insemination_cutoff_ = (
                Decimal("1") - __probability_above_insemination_cutoff())

        match state_from.state:
            case 'Open':
                match state_to.state:
                    case 'Open':
                        if state_from.days_in_milk < vwp:
                            return (not_below_milk_threshold_ * not_death_).quantize(self._precision)
                        else:
                            return (not_pregnant_ * not_below_milk_threshold_ * not_above_insemination_cutoff_ * not_death_).quantize(self._precision)
                            # chance staying open
                    case 'Pregnant':
                        return (pregnant_ * not_below_milk_threshold_ * not_above_insemination_cutoff_ * not_death_).quantize(self._precision)
                        # chance becoming pregnant
                    case 'DoNotBreed':
                        if state_from.days_in_milk == vwp + insemination_window and state_from.lactation_number != 0:
                            return (not_pregnant_ * not_below_milk_threshold_ * not_death_).quantize(self._precision)
                        else:
                            return (__probability_above_insemination_cutoff() * not_below_milk_threshold_ * not_death_).quantize(self._precision)
                        # chance becoming dnb
                    case 'Exit':
                        if __probability_milk_below_threshold() == Decimal("1"):
                            return Decimal("1")
                            # culling
                        elif state_from.days_in_milk == vwp + insemination_window and state_from.lactation_number == 0:
                            return ((not_pregnant_ * not_death_) + __probability_death()).quantize(self._precision)
                        else:
                            return __probability_death().quantize(self._precision)
                            # chance mortality

            case 'Pregnant':
                match state_to.state:
                    case 'Open':
                        if state_to.lactation_number == state_from.lactation_number + 1:
                            return (__probability_birth() * not_below_milk_threshold_ * not_death_).quantize(self._precision)
                        else:
                            return (__probability_abortion() * not_below_milk_threshold_ * not_death_).quantize(self._precision)
                    case 'Pregnant':
                        return (not_aborting_ * not_below_milk_threshold_ * not_death_).quantize(self._precision)
                        # chance staying pregnant
                    case 'DoNotBreed':
                        # !!! calving or aborting?
                        if state_to.lactation_number == state_from.lactation_number + 1:
                            return (__probability_birth() * not_below_milk_threshold_ * not_death_).quantize(self._precision)
                        else:
                            # !!!!
                            return (__probability_abortion() * not_below_milk_threshold_ * not_death_).quantize(self._precision)
                    case 'Exit':
                        if __probability_milk_below_threshold() == Decimal("1"):
                            return Decimal("1")
                            # culling
                        elif state_from.days_pregnant == dp_limit and state_from.lactation_number == 0:
                            return __probability_death().quantize(self._precision)
                        elif state_from.days_in_milk >= vwp + insemination_window and state_from.lactation_number == 0:
                            return ((__probability_abortion() * not_death_) + __probability_death()).quantize(self._precision)
                        else:
                            return __probability_death().quantize(self._precision)
                            # chance mortality

            case 'DoNotBreed':
                match state_to.state:
                    case 'Open':
                        return Decimal("0")
                    case 'Pregnant':
                        return Decimal("0")
                    case 'DoNotBreed':
                        return (not_below_milk_threshold_ * not_death_).quantize(self._precision)
                        # chance staying DoNotBreed
                    case 'Exit':
                        if __probability_milk_below_threshold() == Decimal("1"):
                            return Decimal("1")
                            # culling
                        else:
                            return __probability_death().quantize(self._precision)
                            # chance mortality

            case 'Exit':
                match state_to.state:
                    case 'Open':
                        if state_to.days_in_milk == 0 and state_to.lactation_number == 0:
                            return Decimal("1")
                    case ('Exit' | 'Pregnant' | 'DoNotBreed'):
                        return Decimal("0")

    def possible_new_states(self, state_from: DairyState.State) -> tuple:
        """
        Returns a tuple with all states state_from can transition into.

        :param state_from: The state from which to transition.
        :type state_from: DairyState.State
        :returns states_to: A tuple containing all states that state_from can
            transition into.
        :rtype: tuple
        :raises ValueError: If the state of state_from is not valid.
        """

        states_to = [DairyState.State('Exit',
                                      state_from.days_in_milk + 1,
                                      state_from.lactation_number, 0,
                                      Decimal("0"))]
        if state_from.days_in_milk == self._generated_days_in_milk - 1 and state_from.state != 'Exit':
            return tuple(states_to)
        vwp = self.herd.get_voluntary_waiting_period(state_from.lactation_number)
        dp_limit = self.herd.get_days_pregnant_limit(state_from.lactation_number)
        insemination_window = self.herd.get_insemination_window(state_from.lactation_number)
        match state_from.state:
            case 'Open':
                if state_from.milk_output > self.herd.milk_threshold or state_from.lactation_number == 0:
                    if vwp <= state_from.days_in_milk <= vwp + insemination_window:
                        self.__set_milkbot_variables(state_from.lactation_number)
                        temp_state = DairyState.State('Pregnant',
                                                      state_from.days_in_milk + 1,
                                                      state_from.lactation_number,
                                                      1,
                                                      Decimal("0"))
                        milk_output = self.milk_production(temp_state)
                        states_to.append(DairyState.State(
                            'Pregnant',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number, 1, milk_output))
                    if state_from.days_in_milk >= vwp + insemination_window and \
                            state_from.lactation_number != 0:
                        self.__set_milkbot_variables(state_from.lactation_number)
                        temp_state = DairyState.State('DoNotBreed',
                                                      state_from.days_in_milk + 1,
                                                      state_from.lactation_number,
                                                      0,
                                                      Decimal("0"))
                        milk_output = self.milk_production(temp_state)
                        states_to.append(DairyState.State(
                            'DoNotBreed',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number, 0, milk_output))
                    elif state_from.days_in_milk < vwp + insemination_window:
                        self.__set_milkbot_variables(state_from.lactation_number)
                        temp_state = DairyState.State('Open',
                                                      state_from.days_in_milk + 1,
                                                      state_from.lactation_number,
                                                      0,
                                                      Decimal("0"))
                        milk_output = self.milk_production(temp_state)
                        states_to.append(DairyState.State(
                            'Open',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number, 0, milk_output))
            case 'Pregnant':
                if state_from.milk_output > self.herd.milk_threshold or state_from.lactation_number == 0:
                    if state_from.days_pregnant == dp_limit and state_from.lactation_number <= self._generated_lactation_numbers:
                        self.__set_milkbot_variables(state_from.lactation_number + 1)
                        # !!!!!!!!
                        if state_from.lactation_number == self._generated_lactation_numbers:
                            temp_state = DairyState.State(
                                'DoNotBreed', state_from.days_in_milk + 1,
                                              state_from.lactation_number + 1, 0,
                                Decimal("0"))
                            milk_output = self.milk_production(temp_state)
                            states_to.append(DairyState.State(
                                'DoNotBreed', state_from.days_in_milk + 1,
                                state_from.lactation_number + 1, 0, milk_output))
                        else:
                            temp_state = DairyState.State(
                                'Open', 0,
                                state_from.lactation_number + 1, 0,
                                Decimal("0"))
                            milk_output = self.milk_production(temp_state)
                            states_to.append(DairyState.State(
                                'Open',
                                0, state_from.lactation_number + 1,
                                0, milk_output))
                    elif state_from.days_pregnant < dp_limit:
                        self.__set_milkbot_variables(state_from.lactation_number)
                        temp_state = DairyState.State('Pregnant',
                                                      state_from.days_in_milk + 1,
                                                      state_from.lactation_number,
                                                      state_from.days_pregnant + 1,
                                                      Decimal("0"))
                        milk_output = self.milk_production(temp_state)
                        states_to.append(DairyState.State(
                            'Pregnant',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number,
                            state_from.days_pregnant + 1, milk_output))
                        if state_from.days_in_milk < vwp + insemination_window:
                            self.__set_milkbot_variables(state_from.lactation_number)
                            temp_state = DairyState.State('Open',
                                                          state_from.days_in_milk + 1,
                                                          state_from.lactation_number,
                                                          0,
                                                          Decimal("0"))
                            milk_output = self.milk_production(temp_state)
                            states_to.append(DairyState.State(
                                'Open',
                                state_from.days_in_milk + 1,
                                state_from.lactation_number, 0, milk_output))
                        elif state_from.days_in_milk >= vwp + insemination_window and state_from.lactation_number != 0:
                            self.__set_milkbot_variables(state_from.lactation_number)
                            temp_state = DairyState.State('DoNotBreed',
                                                          state_from.days_in_milk + 1,
                                                          state_from.lactation_number,
                                                          0,
                                                          Decimal("0"))
                            milk_output = self.milk_production(temp_state)
                            states_to.append(DairyState.State(
                                'DoNotBreed',
                                state_from.days_in_milk + 1,
                                state_from.lactation_number, 0, milk_output))
            case 'DoNotBreed':
                if state_from.milk_output > self.herd.milk_threshold:
                    self.__set_milkbot_variables(state_from.lactation_number)
                    temp_state = DairyState.State('DoNotBreed',
                                                  state_from.days_in_milk + 1,
                                                  state_from.lactation_number,
                                                  0,
                                                  Decimal("0"))
                    milk_output = self.milk_production(temp_state)
                    states_to.append(DairyState.State(
                        'DoNotBreed',
                        state_from.days_in_milk + 1,
                        state_from.lactation_number, 0, milk_output))
            case 'Exit':
                states_to[0] = DairyState.State('Open', 0, 0, 0, Decimal("0"))
            case _:
                raise ValueError('The current state given is invalid.')
        return tuple(states_to)

    def __set_milkbot_variables(self, lactation_number: int) -> None:
        """
        Sets the milkbot variables for the cow, based on its lactation number.

        :param lactation_number: The number of lactation cycles the cow has completed.
        :raises ValueError: If the lactation number is larger than the lactation
            number limit.
        """
        match lactation_number:
            case 0:
                self.milkbot_variables = (
                    Decimal("0"), Decimal("1"), Decimal("1"), Decimal("1"))
            case 1:
                decay = Decimal("0.693") / Decimal("358")
                self.milkbot_variables = (
                    Decimal("34.8"), Decimal("29.6"), Decimal("0"), decay)
            case ln if 1 < ln < self.herd.lactation_number_limit + 2:
                decay = Decimal("0.693") / Decimal("240")
                self.milkbot_variables = (
                    Decimal("47.7"), Decimal("22.1"), Decimal("0"), decay)
            case _:
                raise ValueError

    def __decimalize_precision(self, dec: int) -> None:
        """
        Sets the instance variable _precision.
        This will be used by Decimals during the calculations of transition probabilities as the precision of
        floating-point numbers.

        :param dec: The amount of decimal places to be used in calculations.
            :type dec: int
        """
        precision = "."
        dec = dec * [0]
        dec[-1] = 1
        for decimal in dec:
            precision += str(decimal)
        self._precision = Decimal(precision)

    def __str__(self):
        return f"DigitalCow:\n" \
               f"\tDIM: {self.current_days_in_milk}\n" \
               f"\tLactation number: {self.current_lactation_number}\n" \
               f"\tDays pregnant: {self.current_days_pregnant}\n" \
               f"\tHerd: {self.herd}\n" \
               f"\tCurrent state: {self.current_life_state}"

    def __repr__(self):
        return f"DigitalCow(days_in_milk={self.current_days_in_milk}, " \
               f"lactation_number={self.current_lactation_number}, " \
               f"current_days_pregnant={self.current_days_pregnant}, " \
               f"age_at_first_heat={self._age_at_first_heat}, " \
               f"herd={self.herd}, " \
               f"state={self.current_life_state}," \
               f"precision={len(str(self._precision)) - 1})"

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
        self._current_state = self._current_state.mutate(days_in_milk=dim)
        milk_output = self.milk_production(self._current_state)
        self.current_milk_output = milk_output

    @property
    def current_days_pregnant(self) -> int:
        return self._current_state.days_pregnant

    @current_days_pregnant.setter
    def current_days_pregnant(self, dp):
        self._current_state = self._current_state.mutate(days_pregnant=dp)

    @property
    def current_lactation_number(self) -> int:
        return self._current_state.lactation_number

    @current_lactation_number.setter
    def current_lactation_number(self, ln):
        self._current_state = self._current_state.mutate(lactation_number=ln)

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
        self._current_state = self._current_state.mutate(state=state)

    @property
    def current_milk_output(self) -> Decimal:
        return self._current_state.milk_output

    @current_milk_output.setter
    def current_milk_output(self, mo):
        self._current_state = self._current_state.mutate(milk_output=mo)

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
    def milkbot_variables(self) -> tuple:
        return self._milkbot_variables

    @milkbot_variables.setter
    def milkbot_variables(self, var):
        if type(var) == tuple and len(var) == 4:
            self._milkbot_variables = var

    @property
    def edge_count(self) -> int:
        edge_count = 0
        for state in self.total_states:
            edge_count += len(self.possible_new_states(state))
        return edge_count

    @property
    def node_count(self) -> int:
        return len(self.total_states)

    @property
    def initial_state_vector(self) -> tuple:
        index = self.total_states.index(self.current_state)
        vector = len(self.total_states) * [0]
        vector[index] = 1
        return tuple(vector)


def state_probability_generator(digital_cow: DigitalCow) -> Generator[tuple[int, int, Decimal], None, None]:
    """
    A generator that iterates over a tuple of states. It determines the states each
    state can transition into, and calculates the probability of the state change for
    each pair. It returns the indexes of the state pair in the tuple of states and
    their probability.

    :param digital_cow: A DigitalCow object for which the states are generated and
        transition probabilities must be calculated.
    :type digital_cow: DigitalCow
    :return: index(state_from), index(state_to), probability
    """

    state_index = {
        state: index for index, state in enumerate(digital_cow.total_states)
    }
    for state_from in state_index:
        new_states = digital_cow.possible_new_states(state_from)
        for state_to in new_states:
            probability = digital_cow.probability_state_change(state_from, state_to)
            yield state_index[state_from], \
                state_index[state_to], \
                float(probability)
