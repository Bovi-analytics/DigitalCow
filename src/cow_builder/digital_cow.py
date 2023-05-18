"""
:module: digital_cow
:module author: Gabe van den Hoeven
:synopsis: This module contains the DigitalCow class which represents a cow in a
   dairy herd, as well as some functions that it uses.


======================
How To Use This Module
======================
(See the individual classes, methods, and attributes for details.)\n
*Values in this HowTo are examples, see documentation of each class or function
for details on the default values.*

1. Import the classes DigitalCow and DigitalHerd:
*************************************************
First import the DigitalCow class:

    ``from cow_builder.digital_cow import DigitalCow``

You will also need to import the DigitalHerd class from the digital_herd module:

    ``from cow_builder.digital_herd import DigitalHerd``

************************************************************

2. Create a DigitalCow and DigitalHerd object:
**********************************************
A DigitalCow object can be made without a DigitalHerd object,
however it won't have full functionality until a DigitalHerd is added as its herd.

a) Without a DigitalHerd object:
    1) Without parameters:

        ``cow = DigitalCow()``\n

    2) With parameters:

        ``cow = DigitalCow(days_in_milk=245, lactation_number=3,
        days_pregnant=165, age_at_first_heat=371, age=2079, state='Pregnant')``\n

    *These parameters may not be all available parameters. Look at each class'
    documentation for details.*

b) With a DigitalHerd object:
    1) Without parameters:

        ``a_herd = DigitalHerd()``\n
        ``cow = DigitalCow(herd=a_herd)``\n

    2) With parameters:

        ``a_herd = DigitalHerd(vwp=[365, 90, 70], insemination_window=[110, 100, 90],
        milk_threshold=Decimal("12"), duration_dry=[70, 50])``\n
        ``cow = DigitalCow(days_in_milk=67, lactation_number=1,
        days_pregnant=0, age=767, herd=a_herd, state='Open')``\n

    *These parameters may not be all available parameters. Look at each class'
    documentation for details.*

c) Set the herd of the DigitalCow:
    1) Sets the DigitalHerd as the herd of the DigitalCow:

        ``a_herd = DigitalHerd()``\n
        ``cow = DigitalCow(herd=a_herd)``\n

    2) Overwrites the DigitalHerd as the herd of the DigitalCow:

        ``a_herd = DigitalHerd()``\n
        ``another_herd = DigitalHerd()``\n
        ``cow = DigitalCow(herd=a_herd)``\n
        ``cow.herd = another_herd``\n

    *There are other methods that alter the herd of the cow using functions from the
    DigitalHerd class. These are described in the digital_herd module.*

************************************************************

3. Generate states for the DigitalCow object:
*********************************************
Generate states for the cow with using the ``generate_total_states()`` function:

a) without parameters:

    ``cow.generate_total_state()``

Here the ``days_in_milk_limit`` and ``lactation_number_limit`` variables from the
herd are used.\n

b) with parameters:

    ``cow.generate_total_states(dim_limit=750, ln_limit=9)``

************************************************************

4. Create a transition matrix using the ``chain_simulator`` package:
********************************************************************
To create a transition matrix from the states of the DigitalCow object the
``chain_simulator`` package must be used.\n
1) Import ``array_assembler`` from the ``chain_simulator`` package:

    ``from chain_simulator.assembly import array_assembler``

2) Import the ``state_probability_generator`` function from this module:

    ``from cow_builder.digital_cow import state_probability_generator``

3) Use ``array_assembler`` to create a transition matrix:

    ``tm = array_assembler(cow.node_count, state_probability_generator(cow))``

*For details on the parameters of functions from the* \ ``chain_simulator``\  *package,
see the corresponding documentation of the* \ ``chain_simulator``\  *package:*
TODO LINK

************************************************************

5. Perform a simulation using the ``chain_simulator`` package to get a final state vector:
******************************************************************************************
1) Import ``state_vector_processor`` from the ``chain_simulator`` package:

    ``from chain_simulator.simulation import state_vector_processor``

2) Use the transition matrix and the cow's initial state vector to simulate the cow over a given number of days:

    ``simulation = state_vector_processor(cow.initial_state_vector, tm, 140, 7)``

3) ``simulation`` here is a generator. Iterate over ``simulation`` to get the final state vectors:

``final_state_vector, day = next(simulation)``\n
or\n
``for final_state_vector, day in simulation:``\n

*For details on the parameters of functions from the* \ ``chain_simulator``\  *package,
see the corresponding documentation of the* \ ``chain_simulator``\  *package:*
TODO LINK


************************************************************

6. Get phenotypes from the final state vector:
**********************************************

"""

from decimal import Decimal

import numpy
from cow_builder.digital_herd import DigitalHerd
from cow_builder.state import State
import math
from typing import Generator
import numpy as np


class DigitalCow:
    """
    A digital twin representing a dairy cow.

    :Attributes:
        :var _herd: The DigitalHerd instance representing the herd that the cow
            belongs to.
        :type _herd: digital_herd.DigitalHerd
        :var _current_state: The State instance representing the current state of
            the cow.
        :type _current_state: State
        :var _age_at_first_heat: The age in days, at which the cow had her first
            estrus. Defaults to None if it has not happened yet.
        :type _age_at_first_heat: int | None
        :var __life_states: A list of all possible life states the cow can be in.
        :type __life_states: list[str, str, str, str]
        :var _total_states: A tuple of 'State' objects containing all possible
            states this cow can be in or transition to. Filled by
            ``self.generate_total_states()``.
        :type _total_states: tuple[State]
        :var _milkbot_variables: A tuple of 4 'Decimal' numbers used for the
            'self.milk_production' function.
            index = 0: scale,
            index = 1: ramp,
            index = 2: offset,
            index = 3: decay.
            Filled by ``self.__set_milkbot_variables()``.
        :type _milkbot_variables: tuple[Decimal, Decimal, Decimal, Decimal]

    :Methods:
        __init__(days_in_milk, lactation_number, days_pregnant, age_at_first_heat,
        herd, state, precision)\n
        generate_total_states(dim_limit, ln_limit)\n
        probability_state_change(state_from, state_to)\n
        possible_new_states(state_from)\n
    """

    def __init__(self, days_in_milk=0, lactation_number=0, days_pregnant=0,
                 age_at_first_heat=None, age=0, herd=None, state='Open'):
        """
        Initializes a new instance of a DigitalCow object.

        :param days_in_milk: The number of days since the cow's last calving,
            or it's birth if it has not calved yet. Defaults to 0.
        :type days_in_milk: int
        :param lactation_number: The number of lactation cycles the cow has completed.
            Defaults to 0.
        :type lactation_number: int
        :param days_pregnant: The number of days that the cow is pregnant.
            Defaults to 0.
        :type days_pregnant: int
        :param age_at_first_heat: The age in days, at which the cow had her first
            estrus. Defaults to None.
        :type age_at_first_heat: int | None
        :param age: The age of the cow in days. Defaults to 0.
        :type age: int
        :param herd: The herd to which the cow belongs.
            Contains variables that apply to all cows in the herd. Defaults to None.
        :type herd: digital_herd.DigitalHerd | None
        :param state: The life state of the cow.
            This state should be one of the states defined in self.__life_states.
            Defaults to 'Open'.
        :type state: str
        """
        self._herd = herd
        self.__life_states = ['Open', 'Pregnant', 'DoNotBreed', 'Exit']
        self._age_at_first_heat = age_at_first_heat
        self._total_states = None
        self._generated_days_in_milk = None
        self._generated_lactation_numbers = None
        self._precision = decimalize_precision()
        self._age = age
        temp_state = State(state, days_in_milk, lactation_number,
                           days_pregnant, Decimal("0"))
        if herd is not None:
            self.milkbot_variables = set_milkbot_variables(
                lactation_number,
                herd.lactation_number_limit)
            milk_output = milk_production(self.milkbot_variables,
                                          temp_state,
                                          self.herd.get_days_pregnant_limit(
                                              temp_state.lactation_number),
                                          self.herd.get_duration_dry(
                                              temp_state.lactation_number),
                                          self.precision)
            self._current_state = State(state, days_in_milk,
                                        lactation_number,
                                        days_pregnant, milk_output)
            self.herd = herd
        else:
            self._current_state = temp_state

    def generate_total_states(self, dim_limit=None, ln_limit=None) -> None:
        """
        Generates a tuple of State objects that represent all possible
        states of the DigitalCow instance.

        :param dim_limit: The limit of days in milk for which states should
            be generated. Defaults to the limit of its herd.
        :type dim_limit: int | None
        :param ln_limit: The limit of lactation numbers for which states should
            be generated. Defaults to the limit of its herd.
        :type ln_limit: int | None
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
        stop_pregnant_state = False
        last_pregnancy = False
        not_heifer = False
        dp_limit = self.herd.get_days_pregnant_limit(lactation_number)
        vwp = self.herd.get_voluntary_waiting_period(lactation_number)
        insemination_window = self.herd.get_insemination_window(lactation_number)

        while lactation_number <= ln_limit:
            for life_state in self.__life_states:
                self.milkbot_variables = set_milkbot_variables(
                    lactation_number, self.herd.lactation_number_limit)
                if life_state == 'Pregnant':
                    milk_output = Decimal("0")
                else:
                    temp_state = State(life_state, days_in_milk,
                                       lactation_number, 0, Decimal("0"))
                    milk_output = milk_production(self.milkbot_variables,
                                                  temp_state,
                                                  self.herd.get_days_pregnant_limit(
                                                      temp_state.lactation_number),
                                                  self.herd.get_duration_dry(
                                                      temp_state.lactation_number),
                                                  self._precision)
                # Calculates the milk output for the cow at every state.

                match life_state:
                    case 'Open':
                        if days_in_milk <= vwp + insemination_window + 1:
                            if milk_output >= self.herd.milk_threshold or \
                                    lactation_number == 0:
                                new_state = State(life_state, days_in_milk,
                                                  lactation_number, 0,
                                                  milk_output)
                                total_states.append(new_state)

                    case 'Pregnant':
                        if vwp < days_in_milk <= vwp + insemination_window + dp_limit:
                            if not stop_pregnant_state:
                                while days_pregnant <= simulated_dp_limit:
                                    temp_state = State(life_state,
                                                       days_in_milk,
                                                       lactation_number,
                                                       days_pregnant,
                                                       Decimal("0"))
                                    milk_output = milk_production(
                                        self.milkbot_variables,
                                        temp_state,
                                        self.herd.get_days_pregnant_limit(
                                            temp_state.lactation_number),
                                        self.herd.get_duration_dry(
                                            temp_state.lactation_number),
                                        self._precision)
                                    new_state = State(life_state,
                                                      days_in_milk,
                                                      lactation_number,
                                                      days_pregnant,
                                                      milk_output)
                                    total_states.append(new_state)
                                    days_pregnant += 1
                                if vwp + insemination_window < days_in_milk < vwp + \
                                        insemination_window + dp_limit:
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
                        if days_in_milk > vwp + insemination_window + 1 and \
                                lactation_number != 0:
                            if milk_output >= self.herd.milk_threshold or \
                                    lactation_number == 0:
                                new_state = State(life_state, days_in_milk,
                                                  lactation_number, 0,
                                                  milk_output)
                                total_states.append(new_state)
                            if last_pregnancy:
                                self.milkbot_variables = set_milkbot_variables(
                                    lactation_number + 1,
                                    self.herd.lactation_number_limit)
                                temp_state = State(life_state,
                                                   days_in_milk,
                                                   lactation_number + 1, 0,
                                                   Decimal("0"))
                                milk_output = milk_production(
                                    self.milkbot_variables,
                                    temp_state,
                                    self.herd.get_days_pregnant_limit(
                                        temp_state.lactation_number),
                                    self.herd.get_duration_dry(
                                        temp_state.lactation_number),
                                    self._precision)
                                if milk_output >= self.herd.milk_threshold or \
                                        lactation_number == 0:
                                    new_state = State(life_state,
                                                      days_in_milk,
                                                      lactation_number + 1,
                                                      0,
                                                      milk_output)
                                    total_states.append(new_state)
                    case 'Exit':
                        new_state = State(life_state, days_in_milk,
                                          lactation_number, 0,
                                          milk_output)
                        total_states.append(new_state)
                        if last_pregnancy:
                            new_state = State(life_state, days_in_milk,
                                              lactation_number + 1, 0,
                                              milk_output)
                            total_states.append(new_state)

            if days_in_milk == dim_limit - 1 and not_heifer:
                new_state = State('Exit', dim_limit,
                                  lactation_number, 0,
                                  Decimal("0"))
                total_states.append(new_state)
                if lactation_number == ln_limit:
                    new_state = State('Exit', dim_limit,
                                      lactation_number + 1, 0,
                                      Decimal("0"))
                    total_states.append(new_state)
                days_in_milk = 0
                days_pregnant = 1
                days_pregnant_start = 1
                simulated_dp_limit = 1
                lactation_number += 1
                dp_limit = self.herd.get_days_pregnant_limit(lactation_number)
                vwp = self.herd.get_voluntary_waiting_period(lactation_number)
                insemination_window = self.herd.get_insemination_window(
                    lactation_number)
            else:
                days_in_milk += 1

            temp_state = State('DoNotBreed', days_in_milk - 1,
                               lactation_number, 0, Decimal("0"))
            milk_output = milk_production(self.milkbot_variables,
                                          temp_state,
                                          self.herd.get_days_pregnant_limit(
                                              temp_state.lactation_number),
                                          self.herd.get_duration_dry(
                                              temp_state.lactation_number),
                                          self._precision)
            if milk_output < self.herd.milk_threshold and not_heifer:
                days_in_milk = 0
                days_pregnant = 1
                days_pregnant_start = 1
                simulated_dp_limit = 1
                lactation_number += 1
                dp_limit = self.herd.get_days_pregnant_limit(lactation_number)
                vwp = self.herd.get_voluntary_waiting_period(lactation_number)
                insemination_window = self.herd.get_insemination_window(
                    lactation_number)

            if days_in_milk == vwp + insemination_window + dp_limit + 2 and \
                    lactation_number == 0:
                days_in_milk = 0
                days_pregnant = 1
                days_pregnant_start = 1
                simulated_dp_limit = 1
                lactation_number += 1
                dp_limit = self.herd.get_days_pregnant_limit(lactation_number)
                vwp = self.herd.get_voluntary_waiting_period(lactation_number)
                insemination_window = self.herd.get_insemination_window(
                    lactation_number)
                not_heifer = True

        self.total_states = tuple(total_states)
        self._generated_days_in_milk = dim_limit
        self._generated_lactation_numbers = ln_limit

    def probability_state_change(self, state_from: State, state_to: State) -> Decimal:
        """
        Calculates the probability of transitioning from ``state_from`` to
        ``state_to``.

        :param state_from: The state from which to transition.
        :type state_from: State
        :param state_to: The state to transition into.
        :type state_to: State
        :returns: The probability of transitioning from ``state_from`` to
            ``state_to``.
        :rtype: Decimal
        :raises ValueError: If the state is not defined in ``self.__life_states``.
        """
        if state_to.state not in self.__life_states or state_from.state not \
                in self.__life_states:
            raise ValueError("State variables of a State object must be defined in "
                             "self.__life_states")
        vwp = self.herd.get_voluntary_waiting_period(state_from.lactation_number)
        insemination_window = self.herd.get_insemination_window(
            state_from.lactation_number)
        dp_limit = self.herd.get_days_pregnant_limit(state_from.lactation_number)
        duration_dry = self.herd.get_duration_dry(state_from.lactation_number)
        if state_to not in self.possible_new_states(state_from):
            return Decimal("0")
        if state_from.days_in_milk == self._generated_days_in_milk or \
                (state_from.days_in_milk == vwp + insemination_window +
                 dp_limit and state_from.lactation_number == 0) and \
                state_to == State('Exit', state_from.days_in_milk,
                                  state_from.lactation_number, 0,
                                  Decimal("0")):
            return Decimal("1")

        def __probability_ovulation():
            """Returns the probability for ovulating."""
            match state_from.lactation_number:
                case 0:
                    return Decimal("1") / Decimal("19")
                case ln if ln > 0:
                    return Decimal("1") / Decimal("21")

        def __probability_insemination():
            """Returns the probability for getting inseminated."""
            if state_from.days_in_milk < vwp:
                return Decimal("0")
            else:
                match state_from.lactation_number:
                    case 0:
                        return Decimal("0.85")
                    case ln if 0 < ln:
                        return Decimal("0.65")

        def __probability_pregnancy():
            """Returns the probability of becoming pregnant from an insemination."""
            match state_from.lactation_number:
                case 0:
                    return Decimal("0.5")
                case 1:
                    return Decimal("0.45")
                case ln if 1 < ln:
                    return Decimal("0.35")

        def __probability_birth():
            """Returns 1 if the cow has reached the day of calving."""
            if state_from.days_pregnant == dp_limit:
                return Decimal("1")
            else:
                return Decimal("0")

        def __probability_abortion():
            """Returns the probability of aborting a pregnancy."""
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
            if state_from.milk_output < self.herd.milk_threshold and \
                    state_from.lactation_number != 0 and \
                    state_from.days_pregnant < dp_limit - duration_dry:
                return Decimal("1")
            else:
                return Decimal("0")

        def __probability_death():
            """Returns the probability of involuntary death."""
            # 5% per 1 y = 365 d for perinatal cows
            return Decimal("0.05") / Decimal("365")

        not_death_ = (Decimal("1") - __probability_death())
        pregnant_ = (__probability_ovulation() * __probability_insemination() *
                     __probability_pregnancy())
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
                            return (not_below_milk_threshold_ *
                                    not_death_).quantize(self._precision)
                        else:
                            return (not_pregnant_ * not_below_milk_threshold_ *
                                    not_above_insemination_cutoff_ *
                                    not_death_).quantize(self._precision)
                            # chance staying open
                    case 'Pregnant':
                        return (pregnant_ *
                                not_below_milk_threshold_ *
                                not_above_insemination_cutoff_ *
                                not_death_).quantize(self._precision)
                        # chance becoming pregnant
                    case 'DoNotBreed':
                        if state_from.days_in_milk == vwp + insemination_window \
                                and state_from.lactation_number != 0:
                            return (not_pregnant_ *
                                    not_below_milk_threshold_ *
                                    not_death_).quantize(self._precision)
                        else:
                            return (__probability_above_insemination_cutoff() *
                                    not_below_milk_threshold_ *
                                    not_death_).quantize(self._precision)
                        # chance becoming dnb
                    case 'Exit':
                        if __probability_milk_below_threshold() == Decimal("1"):
                            return Decimal("1")
                            # culling
                        elif state_from.days_in_milk == vwp + insemination_window \
                                + 1 and state_from.lactation_number == 0:
                            return ((not_pregnant_ * not_death_)
                                    + __probability_death()).quantize(self._precision)
                        else:
                            return __probability_death().quantize(self._precision)
                            # chance mortality

            case 'Pregnant':
                match state_to.state:
                    case 'Open':
                        if state_to.lactation_number == \
                                state_from.lactation_number + 1:
                            return (__probability_birth() *
                                    not_below_milk_threshold_ *
                                    not_death_).quantize(self._precision)
                            # chance calving
                        else:
                            return (__probability_abortion() *
                                    not_below_milk_threshold_ *
                                    not_death_).quantize(self._precision)
                            # chance aborting the pregnancy
                    case 'Pregnant':
                        return (not_aborting_ *
                                not_below_milk_threshold_ *
                                not_death_).quantize(self._precision)
                        # chance staying pregnant
                    case 'DoNotBreed':
                        if state_to.lactation_number == \
                                state_from.lactation_number + 1:
                            return (__probability_birth() *
                                    not_below_milk_threshold_ *
                                    not_death_).quantize(self._precision)
                            # chance calving and becoming DNB !
                        else:
                            return (__probability_abortion() *
                                    not_below_milk_threshold_ *
                                    not_death_).quantize(self._precision)
                            # chance aborting and becoming DNB !
                    case 'Exit':
                        if __probability_milk_below_threshold() == Decimal("1"):
                            return Decimal("1")
                            # culling
                        elif state_from.days_pregnant == dp_limit \
                                and state_from.lactation_number == 0:
                            return __probability_death().quantize(self._precision)
                        elif state_from.days_in_milk >= vwp + insemination_window \
                                + 1 and state_from.lactation_number == 0:
                            return ((__probability_abortion() * not_death_)
                                    + __probability_death()).quantize(self._precision)
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
                        return (not_below_milk_threshold_ * not_death_).quantize(
                            self._precision)
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
                        if state_to == State('Open', 0, 0, 0,
                                             Decimal("0")):
                            return Decimal("1")
                    case _:
                        return Decimal("0")

    def possible_new_states(self, state_from: State) -> tuple:
        """
        Returns a tuple with all states ``state_from`` can transition into.

        :param state_from: The state from which to transition.
        :type state_from: State
        :returns states_to: A tuple containing all states that ``state_from`` can
            transition into.
        :rtype: tuple[State]
        :raises ValueError: If the state of ``state_from`` is not valid.
        """

        states_to = [State('Exit',
                           state_from.days_in_milk + 1,
                           state_from.lactation_number, 0,
                           Decimal("0"))]
        if state_from.days_in_milk == self._generated_days_in_milk - 1 and \
                state_from.state != 'Exit':
            return tuple(states_to)
        vwp = self.herd.get_voluntary_waiting_period(state_from.lactation_number)
        dp_limit = self.herd.get_days_pregnant_limit(state_from.lactation_number)
        insemination_window = self.herd.get_insemination_window(
            state_from.lactation_number)
        duration_dry = self.herd.get_duration_dry(state_from.lactation_number)
        match state_from.state:
            case 'Open':
                if state_from.milk_output > self.herd.milk_threshold or \
                        state_from.lactation_number == 0:
                    if vwp <= state_from.days_in_milk <= vwp + insemination_window:
                        self.milkbot_variables = set_milkbot_variables(
                            state_from.lactation_number,
                            self.herd.lactation_number_limit)
                        temp_state = State('Pregnant',
                                           state_from.days_in_milk + 1,
                                           state_from.lactation_number,
                                           1,
                                           Decimal("0"))
                        milk_output = milk_production(
                            self.milkbot_variables,
                            temp_state,
                            self.herd.get_days_pregnant_limit(
                                temp_state.lactation_number),
                            self.herd.get_duration_dry(
                                temp_state.lactation_number),
                            self._precision)
                        states_to.append(State(
                            'Pregnant',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number, 1, milk_output))
                    if state_from.days_in_milk >= vwp + insemination_window + 1 and \
                            state_from.lactation_number != 0:
                        self.milkbot_variables = set_milkbot_variables(
                            state_from.lactation_number,
                            self.herd.lactation_number_limit)
                        temp_state = State('DoNotBreed',
                                           state_from.days_in_milk + 1,
                                           state_from.lactation_number,
                                           0,
                                           Decimal("0"))
                        milk_output = milk_production(
                            self.milkbot_variables,
                            temp_state,
                            self.herd.get_days_pregnant_limit(
                                temp_state.lactation_number),
                            self.herd.get_duration_dry(
                                temp_state.lactation_number),
                            self._precision)

                        states_to.append(State(
                            'DoNotBreed',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number, 0, milk_output))
                    elif state_from.days_in_milk < vwp + insemination_window + 1:
                        self.milkbot_variables = set_milkbot_variables(
                            state_from.lactation_number,
                            self.herd.lactation_number_limit)
                        temp_state = State('Open',
                                           state_from.days_in_milk + 1,
                                           state_from.lactation_number,
                                           0,
                                           Decimal("0"))
                        milk_output = milk_production(
                            self.milkbot_variables,
                            temp_state,
                            self.herd.get_days_pregnant_limit(
                                temp_state.lactation_number),
                            self.herd.get_duration_dry(
                                temp_state.lactation_number),
                            self._precision)
                        states_to.append(State(
                            'Open',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number, 0, milk_output))
            case 'Pregnant':
                if state_from.milk_output > self.herd.milk_threshold \
                        or state_from.lactation_number == 0 \
                        or state_from.days_pregnant >= dp_limit - duration_dry:
                    if state_from.days_pregnant == dp_limit \
                            and state_from.lactation_number <= \
                            self._generated_lactation_numbers:
                        self.milkbot_variables = set_milkbot_variables(
                            state_from.lactation_number + 1,
                            self.herd.lactation_number_limit)
                        # !!!!!!!!
                        if state_from.lactation_number == \
                                self._generated_lactation_numbers:
                            temp_state = State(
                                'DoNotBreed', state_from.days_in_milk + 1,
                                state_from.lactation_number + 1, 0,
                                Decimal("0"))
                            milk_output = milk_production(
                                self.milkbot_variables,
                                temp_state,
                                self.herd.get_days_pregnant_limit(
                                    temp_state.lactation_number),
                                self.herd.get_duration_dry(
                                    temp_state.lactation_number),
                                self._precision)
                            states_to.append(State(
                                'DoNotBreed', state_from.days_in_milk + 1,
                                state_from.lactation_number + 1, 0,
                                milk_output))
                        else:
                            temp_state = State(
                                'Open', 0,
                                state_from.lactation_number + 1, 0,
                                Decimal("0"))
                            milk_output = milk_production(
                                self.milkbot_variables,
                                temp_state,
                                self.herd.get_days_pregnant_limit(
                                    temp_state.lactation_number),
                                self.herd.get_duration_dry(
                                    temp_state.lactation_number),
                                self._precision)
                            states_to.append(State(
                                'Open',
                                0, state_from.lactation_number + 1,
                                0, milk_output))
                    elif state_from.days_pregnant < dp_limit:
                        self.milkbot_variables = set_milkbot_variables(
                            state_from.lactation_number,
                            self.herd.lactation_number_limit)
                        temp_state = State('Pregnant',
                                           state_from.days_in_milk + 1,
                                           state_from.lactation_number,
                                           state_from.days_pregnant + 1,
                                           Decimal("0"))
                        milk_output = milk_production(
                            self.milkbot_variables,
                            temp_state,
                            self.herd.get_days_pregnant_limit(
                                temp_state.lactation_number),
                            self.herd.get_duration_dry(
                                temp_state.lactation_number),
                            self._precision)
                        states_to.append(State(
                            'Pregnant',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number,
                            state_from.days_pregnant + 1, milk_output))
                        if state_from.days_in_milk < vwp + insemination_window + 1:
                            self.milkbot_variables = set_milkbot_variables(
                                state_from.lactation_number,
                                self.herd.lactation_number_limit)
                            temp_state = State('Open',
                                               state_from.days_in_milk + 1,
                                               state_from.lactation_number,
                                               0,
                                               Decimal("0"))
                            milk_output = milk_production(
                                self.milkbot_variables,
                                temp_state,
                                self.herd.get_days_pregnant_limit(
                                    temp_state.lactation_number),
                                self.herd.get_duration_dry(
                                    temp_state.lactation_number),
                                self._precision)
                            states_to.append(State(
                                'Open',
                                state_from.days_in_milk + 1,
                                state_from.lactation_number, 0, milk_output))
                        elif state_from.days_in_milk >= vwp + insemination_window \
                                + 1 and state_from.lactation_number != 0:
                            self.milkbot_variables = set_milkbot_variables(
                                state_from.lactation_number,
                                self.herd.lactation_number_limit)
                            temp_state = State('DoNotBreed',
                                               state_from.days_in_milk + 1,
                                               state_from.lactation_number,
                                               0,
                                               Decimal("0"))
                            milk_output = milk_production(
                                self.milkbot_variables,
                                temp_state,
                                self.herd.get_days_pregnant_limit(
                                    temp_state.lactation_number),
                                self.herd.get_duration_dry(
                                    temp_state.lactation_number),
                                self._precision)
                            states_to.append(State(
                                'DoNotBreed',
                                state_from.days_in_milk + 1,
                                state_from.lactation_number, 0, milk_output))
            case 'DoNotBreed':
                if state_from.milk_output > self.herd.milk_threshold:
                    self.milkbot_variables = set_milkbot_variables(
                        state_from.lactation_number,
                        self.herd.lactation_number_limit)
                    temp_state = State('DoNotBreed',
                                       state_from.days_in_milk + 1,
                                       state_from.lactation_number,
                                       0,
                                       Decimal("0"))
                    milk_output = milk_production(
                        self.milkbot_variables,
                        temp_state,
                        self.herd.get_days_pregnant_limit(
                            temp_state.lactation_number),
                        self.herd.get_duration_dry(
                            temp_state.lactation_number),
                        self._precision)
                    if milk_output >= self.herd.milk_threshold:
                        states_to.append(State(
                            'DoNotBreed',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number, 0, milk_output))
            case 'Exit':
                states_to[0] = State('Open', 0, 0, 0, Decimal("0"))
            case _:
                raise ValueError('The current state given is invalid.')
        return tuple(states_to)

    def __str__(self):
        return f"DigitalCow:\n" \
               f"\tDIM: {self.current_days_in_milk}\n" \
               f"\tLactation number: {self.current_lactation_number}\n" \
               f"\tDays pregnant: {self.current_days_pregnant}\n" \
               f"\tAge: {self._age}\n" \
               f"\tHerd: {self.herd}\n" \
               f"\tCurrent state: {self.current_life_state}"

    def __repr__(self):
        return f"DigitalCow(days_in_milk={self.current_days_in_milk}, " \
               f"lactation_number={self.current_lactation_number}, " \
               f"days_pregnant={self.current_days_pregnant}, " \
               f"age_at_first_heat={self._age_at_first_heat}, " \
               f"age={self._age}, " \
               f"herd={self.herd}, " \
               f"state={self.current_life_state})"

    @property
    def herd(self) -> DigitalHerd:
        """The herd object representing the herd of the cow."""
        return self._herd

    @herd.setter
    def herd(self, herd):
        if isinstance(herd, DigitalHerd):
            if self._herd is not None:
                self._herd.remove_from_herd([self])
            herd.add_to_herd([self])
            self.milkbot_variables = set_milkbot_variables(
                self.current_lactation_number, herd.lactation_number_limit)
            milk_output = milk_production(
                self.milkbot_variables,
                self.current_state,
                self.herd.get_days_pregnant_limit(
                    self.current_state.lactation_number),
                self.herd.get_duration_dry(
                    self.current_state.lactation_number),
                self.precision)
            self.current_milk_output = milk_output

    @property
    def current_days_in_milk(self) -> int:
        """The current number of days since last calving, or the cow's birth if it
        has not calved yet."""
        return self._current_state.days_in_milk

    @current_days_in_milk.setter
    def current_days_in_milk(self, dim):
        self._current_state = self._current_state.mutate(days_in_milk=dim)
        milk_output = milk_production(self.milkbot_variables, self._current_state,
                                      self.herd.get_days_pregnant_limit(
                                          self.current_state.lactation_number),
                                      self.herd.get_duration_dry(
                                          self.current_state.lactation_number),
                                      self._precision)
        self.current_milk_output = milk_output

    @property
    def current_days_pregnant(self) -> int:
        """The current number of days in pregnancy of the cow."""
        return self._current_state.days_pregnant

    @current_days_pregnant.setter
    def current_days_pregnant(self, dp):
        self._current_state = self._current_state.mutate(days_pregnant=dp)

    @property
    def current_lactation_number(self) -> int:
        """The current number of lactation cycles the cow has completed."""
        return self._current_state.lactation_number

    @current_lactation_number.setter
    def current_lactation_number(self, ln):
        self._current_state = self._current_state.mutate(lactation_number=ln)

    @property
    def age_at_first_heat(self) -> int | None:
        """The age in days at which the cow experienced its first heat."""
        if self._age_at_first_heat is None:
            return self._age_at_first_heat
        else:
            return int(self._age_at_first_heat)

    @age_at_first_heat.setter
    def age_at_first_heat(self, age_at_first_heat):
        self._age_at_first_heat = age_at_first_heat

    @property
    def current_life_state(self) -> str:
        """The current life_state the cow is in."""
        return self._current_state.state

    @current_life_state.setter
    def current_life_state(self, state):
        self._current_state = self._current_state.mutate(state=state)

    @property
    def current_milk_output(self) -> Decimal:
        """The current milk output of the cow."""
        return self._current_state.milk_output

    @current_milk_output.setter
    def current_milk_output(self, mo):
        self._current_state = self._current_state.mutate(milk_output=mo)

    @property
    def current_state(self) -> State:
        """The current state of the cow, as a State object."""
        return self._current_state

    @property
    def total_states(self) -> tuple:
        """A generated tuple of State objects that the cow can be in."""
        return self._total_states

    @total_states.setter
    def total_states(self, states):
        self._total_states = states

    @property
    def milkbot_variables(self) -> tuple:
        """A tuple containing parameters used to calculate milk output."""
        return self._milkbot_variables

    @milkbot_variables.setter
    def milkbot_variables(self, var):
        if type(var) == tuple and len(var) == 4:
            self._milkbot_variables = var

    @property
    def edge_count(self) -> int:
        """The total number of possible transitions."""
        edge_count = 0
        for state in self.total_states:
            edge_count += len(self.possible_new_states(state))
        return edge_count

    @property
    def node_count(self) -> int:
        """The total number of States in ``total_states``."""
        return len(self.total_states)

    @property
    def initial_state_vector(self) -> numpy.array:
        """A numpy array indicating which state of all states in ``total_states``
        the cow is in."""
        index = self.total_states.index(self.current_state)
        vector = len(self.total_states) * [0]
        vector[index] = 1
        return np.asarray(vector)

    @property
    def precision(self) -> Decimal:
        """The Decimal object indicating the amount of decimal places used in
        calculations."""
        return self._precision

    @precision.setter
    def precision(self, precision):
        self._precision = decimalize_precision(precision)

    @property
    def age(self) -> int:
        """The age of the cow in days."""
        return self._age

    @age.setter
    def age(self, age):
        self._age = age


def state_probability_generator(digital_cow: DigitalCow) -> \
        Generator[tuple[int, int, Decimal], None, None]:
    """
    A generator that iterates over a tuple of states. It determines the states
    each state can transition into, and calculates the probability of the state
    change for each pair.
    It returns the indexes of the state pair in the tuple of states and their
    probability.

    :param digital_cow: A DigitalCow object for which the states are generated and
        transition probabilities must be calculated.
    :type digital_cow: DigitalCow
    :return:
        - state_index[state_from]: The index of the 'state_from' state in the tuple of
            states.
        - state_index[state_to]: The index of the 'state_to' state in the tuple of
            states.
        - probability: The probability of moving from 'state_from' to 'state_to'.
    :rtype:
        - state_index[state_from]: int
        - state_index[state_to]: int
        - probability: float
    """
    state_index = {
        state: index for index, state in enumerate(digital_cow.total_states)
    }
    for state_from in state_index:
        new_states = digital_cow.possible_new_states(state_from)
        for state_to in new_states:
            probability = digital_cow.probability_state_change(state_from, state_to)
            if len(new_states) == 1:
                probability = Decimal("1")
            yield state_index[state_from], \
                state_index[state_to], \
                float(probability)


def convert_final_state_vector(vector: tuple, total_states: tuple, group_by: int):
    """
    Converts a final state vector to 1 dimension by adding the probabilities
    different states with the same value on the chosen dimension together. Which
    dimension this is depends on the ``group_by`` parameter.

    :param vector: A tuple that contains a vector as well as the day in
        simulation that the vector is from.
    :type vector: tuple
    :param total_states: A generated tuple of State objects that the cow can be in.
    :type total_states: tuple
    :param group_by: An int that indicates what dimension to group the states by.
        TODO
        0: days_in_milk
        1: lactation_number
        2: days_pregnant
        3: life_state
    :type group_by: int
    :returns: The value of the chosen dimension with the corresponding probability
        of being in a state with that specific value
    :rtype: dict
    """
    final_state_vector, day = vector
    state_index = {
        state: index for index, state in enumerate(total_states)
    }
    vector_index = {
        index: probability for index, probability in enumerate(final_state_vector)
    }
    one_dimensional_vector = {}
    for state in state_index:
        index = state_index[state]
        probability = vector_index[index]
        match group_by:
            case 0:
                days_in_milk = state.days_in_milk
                try:
                    one_dimensional_vector[days_in_milk] = one_dimensional_vector[
                        days_in_milk] + probability
                except KeyError as error:
                    one_dimensional_vector.update({days_in_milk: probability})
            case 1:
                lactation_number = state.lactation_number
                try:
                    one_dimensional_vector[lactation_number] = one_dimensional_vector[
                        lactation_number] + probability
                except KeyError as error:
                    one_dimensional_vector.update({lactation_number: probability})
            case 2:
                days_pregnant = state.days_pregnant
                try:
                    one_dimensional_vector[days_pregnant] = one_dimensional_vector[
                        days_pregnant] + probability
                except KeyError as error:
                    one_dimensional_vector.update({days_pregnant: probability})
            case 3:
                life_state = state.state
                try:
                    one_dimensional_vector[life_state] = one_dimensional_vector[
                                                             life_state] + probability
                except KeyError as error:
                    one_dimensional_vector.update({life_state: probability})

    return one_dimensional_vector


def decimalize_precision(dec=10) -> Decimal:
    """
    Returns a Decimal number used to set the number of decimal places for
    calculations.

    :param dec: The number of decimal places to be used in calculations.
        Defaults to 10. Maximum is 25.
    :type dec: int
    :return: A Decimal object to be used for setting the number of decimal places
        in calculations.
    :rtype: Decimal
    """
    precision = "."
    dec = dec * [0]
    if not dec:
        precision = "1"
    else:
        dec[-1] = 1
        for decimal in dec:
            precision += str(decimal)
    return Decimal(precision)


def set_korver_function_variables(lactation_number: int):
    """
    Returns a set of variables used for the Korver function based on a given
    lactation number.

    :param lactation_number: The lactation number of a cow.
    :type lactation_number: int
    :return:
        - birth_weight: The weight of the cow at birth in kg.
        - mature_live_weight: The weight of a mature cow in kg.
        - growth_rate: A variable that describes the speed at which the weight of
            the cow increases.
        - pregnancy_parameter: A variable that describes that decrease in weight of
            the cow after calving.
        - max_decrease_live_weight: The maximum decrease in live weight during a
            lactation cycle in kg.
        - duration_minimum_live_weight: The number of days for which the live weight
            is lowest.
    :rtype:
        - birth_weight: Decimal
        - mature_live_weight: Decimal | None
        - growth_rate: Decimal | None
        - pregnancy_parameter: Decimal | None
        - max_decrease_live_weight: Decimal | None
        - duration_minimum_live_weight: Decimal | None
    """
    # birth_weight = 42
    # mature_live_weight = 600
    # growth_rate = 0.0028
    # pregnancy_parameter = 0.0187
    # max_decrease_live_weight = 50
    # duration_minimum_live_weight = 75

    match lactation_number:
        case 0:
            birth_weight = Decimal(np.random.normal(42, 0))
            mature_live_weight = None
            growth_rate = None
            pregnancy_parameter = None
            max_decrease_live_weight = None
            duration_minimum_live_weight = None
        case 1:
            birth_weight = Decimal(np.random.normal(42, 0))
            mature_live_weight = Decimal(np.random.normal(600, 0))
            growth_rate = Decimal(f"{np.random.normal(0.0039, 0)}")
            pregnancy_parameter = Decimal(f"{np.random.normal(0.0187, 0)}")
            max_decrease_live_weight = Decimal(np.random.normal(20, 0))
            duration_minimum_live_weight = Decimal(np.random.normal(65, 0))
        case ln if ln > 1:
            birth_weight = Decimal(np.random.normal(42, 0))
            mature_live_weight = Decimal(np.random.normal(640, 0))
            growth_rate = Decimal(f"{np.random.normal(0.006, 0)}")
            pregnancy_parameter = Decimal(f"{np.random.normal(0.0187, 0)}")
            max_decrease_live_weight = Decimal(np.random.normal(40, 0))
            duration_minimum_live_weight = Decimal(np.random.normal(70, 0))
        case _:
            raise ValueError

    return birth_weight, mature_live_weight, growth_rate, pregnancy_parameter, \
        max_decrease_live_weight, duration_minimum_live_weight


def calculate_body_weight(state: State, age: int, vwp: int,
                          precision: Decimal) -> Decimal:
    """
    Calculates the body weight of a cow for a specific state.
    
    :param state: The State object that represents the specific day for which the
        body weight must be calculated.
    :type state: State
    :param age: The age of the cow in days.
    :type age: int
    :param vwp: The voluntary waiting period of the cow for the specific lactation 
        of the state.
    :type vwp: int
    :param precision: A Decimal number that determines the number of decimal places
        to be used.
    :type precision: Decimal
    :return: The body weight of the cow in kg in the state that is given.
    :rtype: Decimal
    """
    # Source
    #
    birth_weight, mature_live_weight, growth_rate, pregnancy_parameter, \
        max_decrease_live_weight, duration_minimum_live_weight = \
        set_korver_function_variables(state.lactation_number)
    if state.lactation_number == 0:
        max_weight = Decimal("1270")
        bw = Decimal(min(max(birth_weight, Decimal("27.2") + (Decimal("0.822") *
                                                              state.days_in_milk)),
                         max_weight))
    else:
        dpc = (state.days_in_milk - vwp - 50)  # d after conception - 50
        if dpc < 0:
            dpc = 0
        bw = Decimal(mature_live_weight *
                     Decimal((1 - (1 - math.pow((birth_weight / mature_live_weight),
                                                (Decimal("1") / Decimal("3")))) *
                              math.pow(math.exp(-growth_rate * age), 3))) +
                     max_decrease_live_weight *
                     (state.days_in_milk / duration_minimum_live_weight) *
                     Decimal(math.exp(1 - (state.days_in_milk /
                                           duration_minimum_live_weight))) +
                     Decimal(pow(pregnancy_parameter, 3)) * Decimal(pow(dpc, 3))
                     ).quantize(precision)
    return bw


def set_milkbot_variables(lactation_number: int,
                          lactation_number_limit: int) -> tuple:
    """
    Returns MilkBot variables for a DigitalCow, based on its lactation number.

    :param lactation_number: The number of lactation cycles the cow has completed.
    :type lactation_number: int
    :param lactation_number_limit: The maximum number of lactation cycles the cow
        can complete before culling.
    :type lactation_number_limit: int
    :return: milkbot_variables: A tuple of parameters for the MilkBot function.
        1: scale
        2: ramp
        3: offset
        4: decay
    :rtype: tuple[Decimal, Decimal, Decimal, Decimal]
    :raises ValueError: If the lactation number is larger than the lactation
        number limit.
    """
    # TODO Source
    match lactation_number:
        case 0:
            milkbot_variables = (
                Decimal("0"), Decimal("1"), Decimal("1"), Decimal("1"))
        case 1:
            decay = Decimal("0.693") / Decimal("358")
            decay = Decimal(f"{np.random.normal(float(decay), 0)}")
            milkbot_variables = (
                Decimal(f"{np.random.normal(34.8, 0)}"),
                Decimal(f"{np.random.normal(29.6, 0)}"),
                Decimal(f"{np.random.normal(0, 0)}"),
                decay)
        case ln if 1 < ln < lactation_number_limit + 2:
            # +2 ensures that if the cow calves in its last lactation cycle,
            # it won't cause a ValueError.
            decay = Decimal("0.693") / Decimal("240")
            decay = Decimal(f"{np.random.normal(float(decay), 0)}")
            milkbot_variables = (
                Decimal(f"{np.random.normal(47.7, 0)}"),
                Decimal(f"{np.random.normal(22.1, 0)}"),
                Decimal(f"{np.random.normal(0, 0)}"), decay)
        case _:
            raise ValueError
    return milkbot_variables


def milk_production(milkbot_variables: tuple, state: State, dp_limit: int,
                    duration_dry: int, precision: Decimal) -> Decimal:
    """
    Calculates milk production for a given state using the MilkBot algorithm.

    :param milkbot_variables: A tuple containing parameters for the MilkBot algorithm.
    :type: tuple
    :param state: A state object for which milk production must be calculated.
    :type state: State
    :param dp_limit: The maximum number of days a cow can be pregnant.
    :type dp_limit: int
    :param duration_dry: The number of days before calving, when a cow is not
        being milked, otherwise known as the Dry period.
    :type duration_dry: int
    :param precision: A Decimal number that determines the number of decimal places
        to be used.
    :type: Decimal
    :returns: The milk production for the given days in milk in kg.
    :rtype: Decimal
    """
    # Source (Hostens M., et al., 2012)
    if state.lactation_number == 0 or state.state == 'Exit' \
            or state.days_pregnant >= dp_limit - duration_dry:
        return Decimal("0")
    scale = milkbot_variables[0]
    ramp = milkbot_variables[1]
    offset = milkbot_variables[2]
    decay = milkbot_variables[3]
    return Decimal(scale * Decimal(Decimal("1") - (pow(Decimal(math.e), (
            (offset - Decimal(state.days_in_milk)) / ramp)) / Decimal(
        "2"))) * pow(Decimal(math.e),
                     -decay * Decimal(state.days_in_milk))).quantize(precision)


def calculate_dmi(state: State, body_weight: Decimal, precision: Decimal):
    """
    Calculates the dry matter intake of a cow for a specific state.

    :param state: The State object that represents the specific day for which the
        dry matter intake must be calculated.
    :type state: State
    :param body_weight: The body weight of the cow in kg on the specific day for which
        the dry matter intake must be calculated.
    :param precision: A decimal number that determines the number of decimal places
        to be used.
    :type precision: Decimal
    :return: The dry matter intake in kg for the specific state that is given.
    :rtype: Decimal
    """
    # Source: (Giordano J.O., et al., 2012) (Cabrera)
    # doi: http://dx.doi.org/10.3168/jds.2011-4972
    fcm_dim = Decimal(state.milk_output * Decimal(
        "0.04"))  # kg (fat corrected milk) 4% FCM production
    dmi = Decimal((Decimal("0.372") * fcm_dim + Decimal("0.0968") *
                   pow(body_weight, Decimal("0.75"))) *
                  (1 - pow(Decimal(math.e),
                           (Decimal("-0.192") * ((Decimal(state.days_in_milk / 7)
                                                  ) + Decimal("3.67")))))).quantize(
        precision)
    return dmi


def manure_nitrogen_output(dmi: Decimal, diet_cp: Decimal, milk_yield: Decimal,
                           milk_cp: Decimal, precision: Decimal):
    """
    Returns results from a mass balance equation that estimates nitrogen in manure 
    for lactating cows when dry-matter intake, dietary crude protein concentration, 
    milk yield and milk crude protein concentration are known.
    
    :param dmi: The dry-matter intake of the cow in kg.
    :type dmi: Decimal
    :param diet_cp: The dietary crude protein concentration in %.
    :type diet_cp: Decimal
    :param milk_yield: The milk output of the cow in kg.
    :type milk_yield: Decimal
    :param milk_cp: The crude protein concentration in the milk of the cow in %.
    :type milk_cp: Decimal
    :param precision: A decimal number that determines the number of decimal places
        to be used.
    :type precision: Decimal
    :return: Manure nitrogen output in g.
    :rtype: Decimal
    """""
    # TODO: SOURCE
    manure_n_output = Decimal((dmi * diet_cp) / Decimal("0.625") -
                              (milk_yield * milk_cp) / Decimal("0.638") -
                              Decimal("5")).quantize(precision)
    return manure_n_output


def urine_nitrogen_output(lactation_number: int, nitrogen_intake: Decimal,
                          precision: Decimal):
    """
    Returns the estimated nitrogen output for a cow's urine based on its
    nitrogen intake.

    :param lactation_number: The lactation number of the cow on the day of the
        calculation.
    :type lactation_number: int
    :param nitrogen_intake: The amount of nitrogen consumed by the cow in g per day.
    :type nitrogen_intake: Decimal
    :param precision: A decimal number that determines the number of decimal places
        to be used.
    :type precision: Decimal
    :return:
        - mu_n_output: The mean nitrogen output in g.
        - min_n_output: The minimum nitrogen output in g.
        - max_n_output: The maximum nitrogen output in g.
    :rtype:
        - mu_n_output: Decimal
        - min_n_output: Decimal
        - max_n_output: Decimal
    """
    # TODO: CHECK NOT LACTATING!
    # Johnson et al. (2016) -> Reed et al. (2015)
    if lactation_number < 0:
        # root-mean-square prediction error: 25%
        mu_n_output = (Decimal("12.0") + (Decimal("0.333") *
                                          nitrogen_intake)).quantize(precision)
        min_n_output = (Decimal("6.2") + (Decimal("0.322") *
                                          nitrogen_intake)).quantize(precision)
        max_n_output = (Decimal("17.8") + (Decimal("0.344") *
                                           nitrogen_intake)).quantize(precision)
    else:
        # root-mean-square prediction error: 36%
        mu_n_output = (Decimal("14.3") + (Decimal("0.51") *
                                          nitrogen_intake)).quantize(precision)
        min_n_output = (Decimal("11.12") + (Decimal("0.39") *
                                            nitrogen_intake)).quantize(precision)
        max_n_output = (Decimal("17.48") + (Decimal("0.63") *
                                            nitrogen_intake)).quantize(precision)
    return mu_n_output, min_n_output, max_n_output


def fecal_nitrogen_output(lactation_number, dmi, nitrogen_intake, precision):
    """
    Returns the estimated nitrogen output for a cow's feces based on its nitrogen
    intake or dmi.

    :param lactation_number: The lactation number of the cow on the day of the
        calculation.
    :type lactation_number: int
    :param dmi: The dry matter intake of the cow in kg per day.
    :type dmi: Decimal
    :param nitrogen_intake: The amount of nitrogen consumed by the cow in g per day.
    :type nitrogen_intake: Decimal
    :param precision: A decimal number that determines the number of decimal places
        to be used.
    :type precision: Decimal
    :return:
        - mu_n_output: The mean nitrogen output in g.
        - min_n_output: The minimum nitrogen output in g.
        - max_n_output: The maximum nitrogen output in g.
    :rtype:
        - mu_n_output: Decimal
        - min_n_output: Decimal
        - max_n_output: Decimal
    """
    # TODO: CHECK NOT LACTATING!
    # Johnson et al. (2016)
    if lactation_number < 0:
        # Reed et al. (2015)
        # root-mean-square prediction error: 16%
        mu_n_output = (Decimal("-18.5") + (Decimal("10.1") * dmi)).quantize(
            precision)
        min_n_output = (Decimal("-22.09") + (Decimal("9.931") * dmi)).quantize(
            precision)
        max_n_output = (Decimal("-14.91") + (Decimal("10.269") * dmi)).quantize(
            precision)
    else:
        # TODO: SOURCE
        # root-mean-square prediction error: 17%
        mu_n_output = (Decimal("0.35") + (Decimal("0.32") *
                                          nitrogen_intake)).quantize(precision)
        min_n_output = (Decimal("-1.38") + (Decimal("0.3136") *
                                            nitrogen_intake)).quantize(precision)
        max_n_output = (Decimal("2.08") + (Decimal("0.3264") *
                                           nitrogen_intake)).quantize(precision)
    return mu_n_output, min_n_output, max_n_output


def total_manure_nitrogen_output(lactation_number, nitrogen_intake, precision):
    """
    Returns estimated nitrogen output of a cow's manure (urine and feces) based on its
    nitrogen intake.

    :param lactation_number: The lactation number of the cow on the day of the
        calculation.
    :type lactation_number: int
    :param nitrogen_intake: The amount of nitrogen consumed by the cow in g per day.
    :type nitrogen_intake: Decimal
    :param precision: A decimal number that determines the number of decimal places
        to be used.
    :type precision: Decimal
    :return:
        - mu_n_output: The mean nitrogen output in g.
        - min_n_output: The minimum nitrogen output in g.
        - max_n_output: The maximum nitrogen output in g.
    :rtype:
        - mu_n_output: Decimal
        - min_n_output: Decimal
        - max_n_output: Decimal
    """
    # TODO: CHECK NOT LACTATING!
    # Johnson et al. 2016 -> Reed et al. (2015)
    if lactation_number < 0:
        # root-mean-square prediction error: 11%
        mu_n_output = (Decimal("20.3") + (Decimal("0.654") *
                                          nitrogen_intake)).quantize(precision)
        min_n_output = (Decimal("15.58") + (Decimal("0.645") *
                                            nitrogen_intake)).quantize(precision)
        max_n_output = (Decimal("25.02") + (Decimal("0.663") *
                                            nitrogen_intake)).quantize(precision)
    else:
        # root-mean-square prediction error: 13%
        mu_n_output = (Decimal("15.1") + (Decimal("0.83") *
                                          nitrogen_intake)).quantize(precision)
        min_n_output = (Decimal("12.6") + (Decimal("0.812") *
                                           nitrogen_intake)).quantize(precision)
        max_n_output = (Decimal("17.6") + (Decimal("0.848") *
                                           nitrogen_intake)).quantize(precision)
    return mu_n_output, min_n_output, max_n_output


def milk_nitrogen_output(dmi, precision):
    """
    Calculates the nitrogen output in a cow's milk based on its dry matter intake.

    :param dmi: The dry matter intake of the cow in kg per day.
    :type dmi: Decimal
    :param precision: A decimal number that determines the number of decimal places
        to be used.
    :type precision: Decimal
    :return:
        - mu_n_output: The mean nitrogen output in g.
        - min_n_output: The minimum nitrogen output in g.
        - max_n_output: The maximum nitrogen output in g.
    :rtype:
        - mu_n_output: Decimal
        - min_n_output: Decimal
        - max_n_output: Decimal
    """
    # Johnson et al. (2016) -> Reed et al. (2015)
    # root-mean-square prediction error: 14%
    mu_n_output = (Decimal("-19.0") + (Decimal("8.13") * dmi)).quantize(precision)
    min_n_output = (Decimal("-22.21") + (Decimal("7.885") * dmi)).quantize(precision)
    max_n_output = (Decimal("-15.79") + (Decimal("8.375") * dmi)).quantize(precision)
    return mu_n_output, min_n_output, max_n_output


def fecal_phosphor_output(phosphor_intake, milk_yield, precision):
    """
    Calculates the phosphor output of a cow's feces based on the cow's
    phosphor intake and milk production.

    :param phosphor_intake: The amount of phosphor consumed by the cow in g per day.
    :type phosphor_intake: Decimal
    :param milk_yield: The milk production of the cow in kg per day.
    :type milk_yield: Decimal
    :param precision: A decimal number that determines the number of decimal places
        to be used.
    :type precision: Decimal
    :return:
        - mu_p_output: The mean phosphor output in g.
        - min_p_output: The minimum phosphor output in g.
        - max_p_output: The maximum phosphor output in g.
    :rtype:
        - mu_p_output: Decimal
        - min_p_output: Decimal
        - max_p_output: Decimal
    """
    # Alvarez-Fuentes et al. (2016)
    mu_p_output = (Decimal("0.73") * phosphor_intake - Decimal("0.37") *
                   milk_yield).quantize(precision)
    min_p_output = (Decimal("0.7") * phosphor_intake - Decimal("0.29") *
                    milk_yield).quantize(precision)
    max_p_output = (Decimal("0.76") * phosphor_intake - Decimal("0.45") *
                    milk_yield).quantize(precision)
    return mu_p_output, min_p_output, max_p_output
