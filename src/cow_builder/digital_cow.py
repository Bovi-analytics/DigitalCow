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
Import the classes from the modules ``digital_cow`` and ``digital_herd``.
::

    from cow_builder.digital_cow import DigitalCow
    from cow_builder.digital_herd import DigitalHerd

************************************************************

2. Create a DigitalCow and DigitalHerd object:
**********************************************
A DigitalCow object can be made without a DigitalHerd object,
however it won't have full functionality until a DigitalHerd is added as its herd.

a) Without a DigitalHerd object:
    1) Without parameters::

        cow = DigitalCow()

    2) With parameters::

        cow = DigitalCow(days_in_milk=245, lactation_number=3,
        days_pregnant=165, diet_cp_cu=160, diet_cp_fo=140, age=2079, state='Pregnant')

    *These parameters may not be all available parameters. Look at each class'
    documentation for details.*

b) With a DigitalHerd object:
    1) Without parameters:

        a_herd = DigitalHerd()
        cow = DigitalCow(herd=a_herd)

    2) With parameters::

        a_herd = DigitalHerd(vwp=(365, 90, 70), insemination_window=(110, 100, 90),
        milk_threshold=12, duration_dry=(70, 50))
        cow = DigitalCow(days_in_milk=67, lactation_number=1,
        days_pregnant=0, diet_cp_cu=160, diet_cp_fo=140, age=767, herd=a_herd, state='Open')

    *These parameters may not be all available parameters. Look at each class'
    documentation for details.*

c) Set the herd of the DigitalCow:
    1) Sets the DigitalHerd as the herd of the DigitalCow::

        a_herd = DigitalHerd()
        cow = DigitalCow(herd=a_herd)

    2) Overwrites the DigitalHerd as the herd of the DigitalCow::

        a_herd = DigitalHerd()
        another_herd = DigitalHerd()
        cow = DigitalCow(herd=a_herd)
        cow.herd = another_herd

    *There are other methods that alter the herd of the cow using functions from the
    ``DigitalHerd`` class. These are described in the ``digital_herd`` module.*

************************************************************

3. Retrieving and altering instance variables:
**********************************************
There are many variables in the ``DigitalCow`` class, all of which can be called.

1) Retrieving ``property`` variables:

all instance variables are ``properties``. They can be called like this::

    a_cow = DigitalCow()
    dim = a_cow.current_days_in_milk

2) Altering ``property`` variables:

all instance variables can be altered like this::

    a_cow = DigitalCow()
    dim = 200
    a_cow.current_days_in_milk = dim

************************************************************

4. Generate states for the DigitalCow object:
*********************************************
Generate states for the cow with using the ``generate_total_states()`` function.
If you use these to make a transition matrix, this will determine the size of the matrix and
thus how far you can simulate.

The ``days_in_milk_limit`` parameter determines the maximum number of days within one lactation
(The actual number can be less depending on the milk threshold). The ``lactation_number_limit`` is the maximum
number of lactations that can be completed before culling.


a) without parameters::

    cow.generate_total_state()

Here the ``days_in_milk_limit`` and ``lactation_number_limit`` variables from the
herd are used.

b) with parameters::

    cow.generate_total_states(dim_limit=750, ln_limit=9)

************************************************************

5. Using the ``state_probability_generator``:
*********************************************
The ``state_probability_generator()`` function takes a DigitalCow as a parameter.
It goes through the states that have been generated and returns the probability of the cow moving from one state
to another together with the indices of these states. This can be used together with the ``array_assembler`` function
from the ``chain_simulator`` package to create a transition matrix.

::
    from chain_simulator.assembly import array_assembler
    from cow_builder.digital_cow import state_probability_generator

    tm = array_assembler(state_count=cow.node_count, probability_calculator=state_probability_generator(cow))

************************************************************

6. Using the vector phenotype functions:
****************************************
The vector phenotype functions are used to calculate phenotype values from a given vector of state probabilities.
These functions can be passed to the ``simulation_accumulator`` function of the ``chain_simulator`` package in
a dictionary. Parameters should be partially filled to allow the ``simulation_accumulator`` to access specific
instance variables and functions.

::

    from cow_builder.digital_cow import vector_milk_production, vector_nitrogen_emission
    from functools import partial

    callbacks = {
        "milk": partial(vector_milk_production, digital_cow=cow),
        "nitrogen": partial(vector_nitrogen_emission, digital_cow=cow)
    }

************************************************************
"""
from numpy import ndarray
from cow_builder.digital_herd import DigitalHerd
from cow_builder.state import State
import math
from typing import Generator
import numpy as np
from functools import cache


class DigitalCow:
    """
    A digital twin representing a dairy cow.

    :Attributes:
        :var _herd: The ``DigitalHerd`` instance representing the herd that the cow
            belongs to.
        :type _herd: DigitalHerd
        :var _current_state: The ``State`` instance representing the current state of
            the cow.
        :type _current_state: State
        :var _age_at_first_heat: The age in days, at which the cow had her first
            estrus. Defaults to None if it has not happened yet.
        :type _age_at_first_heat: int | None
        :var __life_states: A list of all possible life states the cow can be in.
        :type __life_states: list[str]
        :var _total_states: A tuple of ``State`` objects containing all possible
            states this cow can be in or transition to. Filled by
            ``self.generate_total_states()``.
        :type _total_states: tuple[State] | None
        :var _milkbot_variables: A tuple of 4 floats used for the
            ``self.milk_production`` function.

            * index = 0: scale
            * index = 1: ramp
            * index = 2: offset
            * index = 3: decay

            Filled by ``self.__set_milkbot_variables()``.
        :type _milkbot_variables: tuple[float]

    :Methods:
        __init__(days_in_milk, lactation_number, days_pregnant, age_at_first_heat,
        herd, state, precision)\n
        generate_total_states(dim_limit, ln_limit)\n
        probability_state_change(state_from, state_to)\n
        possible_new_states(state_from)\n

    ************************************************************
    """

    def __init__(self, days_in_milk=0, lactation_number=0, days_pregnant=0,
                 diet_cp_cu=160, diet_cp_fo=140,
                 milk_cp=3.4, age=0, herd=None,
                 state='Open', age_at_first_heat=None):
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
        :type herd: DigitalHerd | None
        :param state: The life state of the cow.
            This state should be one of the states defined in ``self.__life_states``.
            Defaults to 'Open'.
        :type state: str
        """
        self._herd = herd
        self.__life_states = ['Open', 'DoNotBreed', 'Pregnant', 'Exit']
        self._age_at_first_heat = age_at_first_heat
        self._total_states = None
        self._generated_days_in_milk = None
        self._generated_lactation_numbers = None
        self._age = age
        self._diet_cp_cu = diet_cp_cu
        self._diet_cp_fo = diet_cp_fo
        self._milk_cp = milk_cp
        temp_state = State(state, days_in_milk, lactation_number,
                           days_pregnant, 0.0)

        if herd is not None:
            self.milkbot_variables = set_milkbot_variables(lactation_number)
            milk_output = milk_production(self.milkbot_variables,
                                          temp_state,
                                          self.herd.get_days_pregnant_limit(
                                              temp_state.lactation_number),
                                          self.herd.get_duration_dry(
                                              temp_state.lactation_number))

            self._current_state = State(state, days_in_milk,
                                        lactation_number,
                                        days_pregnant, milk_output)
            self.herd = herd
        else:
            self._current_state = temp_state

    def generate_total_states(self, dim_limit=None, ln_limit=None) -> None:
        """
        Generates a tuple of ``State`` objects that represent all possible
        states of the ``DigitalCow`` instance.

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
                self.milkbot_variables = set_milkbot_variables(lactation_number)
                if life_state == 'Pregnant':
                    milk_output = None
                else:
                    temp_state = State(life_state, days_in_milk,
                                       lactation_number, 0, 0.0)
                    milk_output = milk_production(self.milkbot_variables,
                                                  temp_state,
                                                  self.herd.get_days_pregnant_limit(
                                                      temp_state.lactation_number),
                                                  self.herd.get_duration_dry(
                                                      temp_state.lactation_number))
                # Calculates the milk output for the cow at every state.

                match life_state:
                    case 'Open':
                        if days_in_milk <= vwp + insemination_window:
                            if milk_output >= self.herd.milk_threshold or \
                                    lactation_number == 0:
                                new_state = State(life_state, days_in_milk,
                                                  lactation_number, 0,
                                                  milk_output)
                                total_states.append(new_state)

                    case 'DoNotBreed':
                        if days_in_milk > vwp + insemination_window and \
                                lactation_number != 0:
                            if milk_output >= self.herd.milk_threshold or \
                                    lactation_number == 0:
                                new_state = State(life_state, days_in_milk,
                                                  lactation_number, 0,
                                                  milk_output)
                                total_states.append(new_state)

                            if last_pregnancy:
                                self.milkbot_variables = set_milkbot_variables(
                                    lactation_number + 1)
                                temp_state = State(life_state,
                                                   days_in_milk,
                                                   lactation_number + 1, 0,
                                                   0.0)
                                milk_output = milk_production(
                                    self.milkbot_variables,
                                    temp_state,
                                    self.herd.get_days_pregnant_limit(
                                        temp_state.lactation_number),
                                    self.herd.get_duration_dry(
                                        temp_state.lactation_number))
                                if milk_output >= self.herd.milk_threshold or \
                                        lactation_number == 0:
                                    new_state = State(life_state,
                                                      days_in_milk,
                                                      lactation_number + 1,
                                                      0,
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
                                                       0.0)
                                    milk_output = milk_production(
                                        self.milkbot_variables,
                                        temp_state,
                                        self.herd.get_days_pregnant_limit(
                                            temp_state.lactation_number),
                                        self.herd.get_duration_dry(
                                            temp_state.lactation_number))

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
                                    elif days_in_milk == vwp + dp_limit:
                                        last_pregnancy = True

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
                                  lactation_number, 0, 0.0)
                total_states.append(new_state)
                if lactation_number == ln_limit:
                    new_state = State('Exit', dim_limit,
                                      lactation_number + 1, 0, 0.0)
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
                               lactation_number, 0, 0.0)
            milk_output = milk_production(self.milkbot_variables,
                                          temp_state,
                                          self.herd.get_days_pregnant_limit(
                                              temp_state.lactation_number),
                                          self.herd.get_duration_dry(
                                              temp_state.lactation_number))

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

    def probability_state_change(self, state_from: State, state_to: State) -> float:
        """
        Calculates the probability of transitioning from ``state_from`` to
        ``state_to``.

        :param state_from: The state from which to transition.
        :type state_from: State
        :param state_to: The state to transition into.
        :type state_to: State
        :returns: The probability of transitioning from ``state_from`` to
            ``state_to``.
        :rtype: float
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
            return 0

        if state_from.days_in_milk == self._generated_days_in_milk or \
                (state_from.days_in_milk == vwp + insemination_window +
                 dp_limit and state_from.lactation_number == 0) and \
                state_to == State('Exit', state_from.days_in_milk,
                                  state_from.lactation_number, 0, 0.0):
            return 1

        def __probability_ovulation():
            """Returns the probability for ovulating."""
            match state_from.lactation_number:
                case 0:
                    return 1 / 19
                case ln if ln > 0:
                    return 1 / 21

        def __probability_insemination():
            """Returns the probability for getting inseminated."""
            if state_from.days_in_milk < vwp:
                return 0
            else:
                match state_from.lactation_number:
                    case 0:
                        return 0.85
                    case ln if 0 < ln:
                        return 0.65

        def __probability_pregnancy():
            """Returns the probability of becoming pregnant from an insemination."""
            match state_from.lactation_number:
                case 0:
                    return 0.5
                case 1:
                    return 0.45
                case ln if 1 < ln:
                    return 0.35

        def __probability_birth():
            """Returns 1 if the cow has reached the day of calving."""
            if state_from.days_pregnant == dp_limit:
                return 1
            else:
                return 0

        def __probability_abortion():
            """Returns the probability of aborting a pregnancy."""
            if state_from.days_pregnant < 30:
                return 0
            elif 29 < state_from.days_pregnant < 46:
                return 0.125 / 15
            elif 45 < state_from.days_pregnant < 181:
                return 0.099 / 135
            elif 180 < state_from.days_pregnant < dp_limit + 1:
                return 0.02 / (dp_limit - 180)

        def __probability_above_insemination_cutoff():
            """Returns 1 if the days in milk is above the cutoff for insemination."""
            if state_from.days_in_milk > vwp + insemination_window:
                return 1
            else:
                return 0

        def __probability_milk_below_threshold():
            """Returns 1 if the milk production falls below the milk threshold for
            staying in the herd."""
            if state_from.milk_output < self.herd.milk_threshold and \
                    state_from.lactation_number != 0 and \
                    state_from.days_pregnant < dp_limit - duration_dry:
                return 1
            else:
                return 0

        def __probability_death():
            """Returns the probability of involuntary death."""
            # 5% per 1 y = 365 d for perinatal cows
            return 0.05 / 365

        not_death_ = (1 - __probability_death())
        pregnant_ = (__probability_ovulation() * __probability_insemination() *
                     __probability_pregnancy())
        not_pregnant_ = (1 - pregnant_)
        not_aborting_ = (1 - __probability_abortion())
        not_below_milk_threshold_ = (
                1 - __probability_milk_below_threshold())
        not_above_insemination_cutoff_ = (
                1 - __probability_above_insemination_cutoff())

        match state_from.state:
            case 'Open':
                match state_to.state:
                    case 'Open':
                        if state_from.days_in_milk < vwp:
                            return (not_below_milk_threshold_ *
                                    not_death_)
                        else:
                            return (not_pregnant_ * not_below_milk_threshold_ *
                                    not_above_insemination_cutoff_ *
                                    not_death_)
                            # chance staying open

                    case 'Pregnant':
                        return (pregnant_ *
                                not_below_milk_threshold_ *
                                not_above_insemination_cutoff_ *
                                not_death_)
                        # chance becoming pregnant

                    case 'DoNotBreed':
                        if state_from.days_in_milk == vwp + insemination_window \
                                and state_from.lactation_number != 0:
                            return (not_pregnant_ *
                                    not_below_milk_threshold_ *
                                    not_death_)
                        else:
                            return (__probability_above_insemination_cutoff() *
                                    not_below_milk_threshold_ *
                                    not_death_)
                        # chance becoming dnb

                    case 'Exit':
                        if __probability_milk_below_threshold() == 1:
                            return 1
                            # culling
                        elif state_from.days_in_milk == vwp + insemination_window \
                                and state_from.lactation_number == 0:
                            return ((not_pregnant_ * not_death_)
                                    + __probability_death())
                        else:
                            return __probability_death()
                            # chance mortality

            case 'Pregnant':
                match state_to.state:
                    case 'Open':
                        if state_to.lactation_number == \
                                state_from.lactation_number + 1:
                            return (__probability_birth() *
                                    not_below_milk_threshold_ *
                                    not_death_)
                            # chance calving
                        else:
                            return (__probability_abortion() *
                                    not_below_milk_threshold_ *
                                    not_death_)
                            # chance aborting the pregnancy

                    case 'Pregnant':
                        return (not_aborting_ *
                                not_below_milk_threshold_ *
                                not_death_)
                        # chance staying pregnant

                    case 'DoNotBreed':
                        if state_to.lactation_number == \
                                state_from.lactation_number + 1:
                            return (__probability_birth() *
                                    not_below_milk_threshold_ *
                                    not_death_)
                            # chance calving and becoming DNB
                        else:
                            return (__probability_abortion() *
                                    not_below_milk_threshold_ *
                                    not_death_)
                            # chance aborting and becoming DNB

                    case 'Exit':
                        if __probability_milk_below_threshold() == 1:
                            return 1
                            # culling
                        elif state_from.days_pregnant == dp_limit \
                                and state_from.lactation_number == 0:
                            return __probability_death()
                        elif state_from.days_in_milk >= vwp + insemination_window \
                                and state_from.lactation_number == 0:
                            return ((__probability_abortion() * not_death_)
                                    + __probability_death())
                        else:
                            return __probability_death()
                            # chance mortality

            case 'DoNotBreed':
                match state_to.state:
                    case 'Open':
                        return 0
                    case 'Pregnant':
                        return 0
                    case 'DoNotBreed':
                        return not_below_milk_threshold_ * not_death_
                        # chance staying DoNotBreed
                    case 'Exit':
                        if __probability_milk_below_threshold() == 1:
                            return 1
                            # culling
                        else:
                            return __probability_death()
                            # chance mortality

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
                           state_from.lactation_number, 0, 0.0)]
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
                            state_from.lactation_number)
                        temp_state = State('Pregnant',
                                           state_from.days_in_milk + 1,
                                           state_from.lactation_number,
                                           1, 0.0)
                        milk_output = milk_production(
                            self.milkbot_variables,
                            temp_state,
                            self.herd.get_days_pregnant_limit(
                                temp_state.lactation_number),
                            self.herd.get_duration_dry(
                                temp_state.lactation_number))

                        #
                        states_to.append(State(
                            'Pregnant',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number, 1, milk_output))

                    if state_from.days_in_milk >= vwp + insemination_window and \
                            state_from.lactation_number != 0:
                        self.milkbot_variables = set_milkbot_variables(
                            state_from.lactation_number)
                        temp_state = State('DoNotBreed',
                                           state_from.days_in_milk + 1,
                                           state_from.lactation_number,
                                           0, 0.0)
                        milk_output = milk_production(
                            self.milkbot_variables,
                            temp_state,
                            self.herd.get_days_pregnant_limit(
                                temp_state.lactation_number),
                            self.herd.get_duration_dry(
                                temp_state.lactation_number))

                        states_to.append(State(
                            'DoNotBreed',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number, 0, milk_output))

                    elif state_from.days_in_milk < vwp + insemination_window:
                        self.milkbot_variables = set_milkbot_variables(
                            state_from.lactation_number)
                        temp_state = State('Open',
                                           state_from.days_in_milk + 1,
                                           state_from.lactation_number,
                                           0, 0.0)
                        milk_output = milk_production(
                            self.milkbot_variables,
                            temp_state,
                            self.herd.get_days_pregnant_limit(
                                temp_state.lactation_number),
                            self.herd.get_duration_dry(
                                temp_state.lactation_number))
                        states_to.append(State(
                            'Open',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number, 0, milk_output))

            case 'DoNotBreed':
                if state_from.milk_output > self.herd.milk_threshold:
                    self.milkbot_variables = set_milkbot_variables(
                        state_from.lactation_number)
                    temp_state = State('DoNotBreed',
                                       state_from.days_in_milk + 1,
                                       state_from.lactation_number,
                                       0,
                                       0.0)
                    milk_output = milk_production(
                        self.milkbot_variables,
                        temp_state,
                        self.herd.get_days_pregnant_limit(
                            temp_state.lactation_number),
                        self.herd.get_duration_dry(
                            temp_state.lactation_number))
                    if milk_output >= self.herd.milk_threshold:
                        states_to.append(State(
                            'DoNotBreed',
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
                            state_from.lactation_number + 1)
                        if state_from.lactation_number == \
                                self._generated_lactation_numbers:
                            temp_state = State(
                                'DoNotBreed', state_from.days_in_milk + 1,
                                state_from.lactation_number + 1, 0, 0.0)
                            milk_output = milk_production(
                                self.milkbot_variables,
                                temp_state,
                                self.herd.get_days_pregnant_limit(
                                    temp_state.lactation_number),
                                self.herd.get_duration_dry(
                                    temp_state.lactation_number))
                            states_to.append(State(
                                'DoNotBreed', state_from.days_in_milk + 1,
                                state_from.lactation_number + 1, 0,
                                milk_output))

                        else:
                            temp_state = State(
                                'Open', 0,
                                state_from.lactation_number + 1, 0, 0.0)
                            milk_output = milk_production(
                                self.milkbot_variables,
                                temp_state,
                                self.herd.get_days_pregnant_limit(
                                    temp_state.lactation_number),
                                self.herd.get_duration_dry(
                                    temp_state.lactation_number))
                            states_to.append(State(
                                'Open',
                                0, state_from.lactation_number + 1,
                                0, milk_output))

                    elif state_from.days_pregnant < dp_limit:
                        self.milkbot_variables = set_milkbot_variables(
                            state_from.lactation_number)
                        temp_state = State('Pregnant',
                                           state_from.days_in_milk + 1,
                                           state_from.lactation_number,
                                           state_from.days_pregnant + 1, 0.0)
                        milk_output = milk_production(
                            self.milkbot_variables,
                            temp_state,
                            self.herd.get_days_pregnant_limit(
                                temp_state.lactation_number),
                            self.herd.get_duration_dry(
                                temp_state.lactation_number))
                        states_to.append(State(
                            'Pregnant',
                            state_from.days_in_milk + 1,
                            state_from.lactation_number,
                            state_from.days_pregnant + 1, milk_output))
                        if state_from.days_in_milk < vwp + insemination_window:
                            self.milkbot_variables = set_milkbot_variables(state_from.lactation_number)
                            temp_state = State('Open',
                                               state_from.days_in_milk + 1,
                                               state_from.lactation_number,
                                               0, 0.0)
                            milk_output = milk_production(
                                self.milkbot_variables,
                                temp_state,
                                self.herd.get_days_pregnant_limit(
                                    temp_state.lactation_number),
                                self.herd.get_duration_dry(
                                    temp_state.lactation_number))
                            states_to.append(State(
                                'Open',
                                state_from.days_in_milk + 1,
                                state_from.lactation_number, 0, milk_output))

                        elif state_from.days_in_milk >= vwp + insemination_window \
                                and state_from.lactation_number != 0:
                            self.milkbot_variables = set_milkbot_variables(
                                state_from.lactation_number)
                            temp_state = State('DoNotBreed',
                                               state_from.days_in_milk + 1,
                                               state_from.lactation_number,
                                               0, 0.0)
                            milk_output = milk_production(
                                self.milkbot_variables,
                                temp_state,
                                self.herd.get_days_pregnant_limit(
                                    temp_state.lactation_number),
                                self.herd.get_duration_dry(
                                    temp_state.lactation_number))
                            states_to.append(State(
                                'DoNotBreed',
                                state_from.days_in_milk + 1,
                                state_from.lactation_number, 0, milk_output))

            case 'Exit':
                states_to = []

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
               f"diet_cp_cu={self._diet_cp_cu}" \
               f"diet_cp_fo={self._diet_cp_fo}" \
               f"milk_cp={self._milk_cp}" \
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
                self.current_lactation_number)
            milk_output = milk_production(
                self.milkbot_variables,
                self.current_state,
                self.herd.get_days_pregnant_limit(
                    self.current_state.lactation_number),
                self.herd.get_duration_dry(
                    self.current_state.lactation_number))
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
                                          self.current_state.lactation_number))
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
    def current_milk_output(self) -> float:
        """The current milk output of the cow."""
        return self._current_state.milk_output

    @current_milk_output.setter
    def current_milk_output(self, mo):
        self._current_state = self._current_state.mutate(milk_output=mo)

    @property
    def current_state(self) -> State:
        """The current state of the cow, as a ``State`` object."""
        return self._current_state

    @property
    def total_states(self) -> tuple:
        """A generated tuple of ``State`` objects that the cow can be in."""
        return self._total_states

    @total_states.setter
    def total_states(self, states):
        self._total_states = states

    @property
    def milkbot_variables(self) -> tuple:
        """A tuple containing 4 parameters used to calculate milk output."""
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
        """The total number of ``State`` objects in ``total_states``."""
        return len(self.total_states)

    @property
    def initial_state_vector(self) -> ndarray:
        """A numpy array indicating which state of all states in ``total_states``
        the cow is in."""
        index = self.total_states.index(self.current_state)
        vector = len(self.total_states) * [0]
        vector[index] = 1
        return np.asarray(vector)

    @property
    def age(self) -> int:
        """The age of the cow in days."""
        return self._age

    @age.setter
    def age(self, age):
        self._age = age

    @property
    def diet_cp_cu(self) -> float:
        """The concentration of crude proteins in the diet of the cow in g."""
        return self._diet_cp_cu

    @diet_cp_cu.setter
    def diet_cp_cu(self, cp):
        self._diet_cp_cu = cp

    @property
    def diet_cp_fo(self) -> float:
        """The concentration of crude proteins in the diet of the cow in g."""
        return self._diet_cp_fo

    @diet_cp_fo.setter
    def diet_cp_fo(self, cp):
        self._diet_cp_fo = cp

    @property
    def milk_cp(self) -> float:
        """The concentration of crude proteins in the milk produced by the cow in
        g."""
        return self._milk_cp

    @milk_cp.setter
    def milk_cp(self, cp):
        self._milk_cp = cp


def state_probability_generator(digital_cow: DigitalCow) -> \
        Generator[tuple[int, int, float], None, None]:
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
        - state_index[state_from]: The index of the ``state_from`` state in the
            tuple of states.
        - state_index[state_to]: The index of the ``state_to`` state in the tuple of
            states.
        - probability: The probability of moving from ``state_from`` to ``state_to``.
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
        if not new_states:
            new_states = (state_from,)
        for state_to in new_states:
            probability = digital_cow.probability_state_change(state_from, state_to)
            if len(new_states) == 1:
                probability = 1
            yield state_index[state_from], \
                state_index[state_to], \
                probability


def vector_milk_production(vector: np.ndarray, step_in_time: int, step_size: int, digital_cow: DigitalCow,
                           intermediate_accumulator: dict[int, float] | None):
    """
    A function that calculates the milk production of a cow ``digital_cow``,
    on a given day in simulation ``step_in_time``, using a vector of state probabilities.
    The milk production is multiplied with ``step_size`` to extrapolate the milk production until the
    next ``step_in_time``. If an intermediate_accumulator is given, milk production is also saved in that dictionary.

    :param vector: A vector of state probabilities that represents the probability of the cow being in each state at
        the current time in the simulation.
    :type vector: np.ndarray
    :param step_in_time: The current day in the simulation.
    :type step_in_time: int
    :param step_size: The interval in days for which phenotype values are calculated during the simulation.
    :type step_size: int
    :param digital_cow: The representation of the cow that is being simulated.
    :type digital_cow: DigitalCow
    :param intermediate_accumulator: A dictionary that stores the milk production of each day in the simulation for
        which phenotype values are calculated.
    :type intermediate_accumulator: dict[int, float] | None

    :return The milk production of the current day in simulation extrapolated until the next step_in_time.
    :rtype: float
    """
    non_exit_states = 0
    vector_phenotype = 0
    index_state = {
        index: state for index, state in enumerate(digital_cow.total_states)
    }
    nonzero_indices = np.where(vector > 0)[0]

    for index in nonzero_indices:
        state = index_state[index]
        if state.state != 'Exit':
            non_exit_states += 1
            vector_phenotype += state.milk_output
    try:
        vector_phenotype = vector_phenotype / non_exit_states
    except ZeroDivisionError:
        vector_phenotype = 0
    if intermediate_accumulator is not None:
        intermediate_accumulator[step_in_time] = vector_phenotype
    return vector_phenotype * step_size


def vector_nitrogen_emission(vector: np.ndarray, step_in_time: int, step_size: int, digital_cow: DigitalCow,
                             intermediate_accumulator: dict[int, float] | None):
    """
    A function that calculates the nitrogen emission of a cow ``digital_cow``,
    on a given day in simulation ``step_in_time``, using a vector of state probabilities.
    The nitrogen emission is multiplied with ``step_size`` to extrapolate the nitrogen emission until the
    next ``step_in_time``. If an intermediate_accumulator is given, nitrogen emission is also saved in that dictionary.

    :param vector: A vector of state probabilities that represents the probability of the cow being in each state at
        the current time in the simulation.
    :type vector: np.ndarray
    :param step_in_time: The current day in the simulation.
    :type step_in_time: int
    :param step_size: The interval in days for which phenotype values are calculated during the simulation.
    :type step_size: int
    :param digital_cow: The representation of the cow that is being simulated.
    :type digital_cow: DigitalCow
    :param intermediate_accumulator: A dictionary that stores the nitrogen emission of each day in the simulation for
        which phenotype values are calculated.
    :type intermediate_accumulator: dict[int, float] | None

    :return: The nitrogen emission of the current day in simulation extrapolated until the next step_in_time.
    :rtype: float
    """
    non_exit_states = 0
    vector_phenotype = 0
    index_state = {
        index: state for index, state in enumerate(digital_cow.total_states)
    }
    nonzero_indices = np.where(vector > 0)[0]
    diet_cp = None
    intake = None

    for index in nonzero_indices:
        state = index_state[index]
        age = digital_cow.age + step_in_time
        if state.state != 'Exit':
            dp_limit = digital_cow.herd.get_days_pregnant_limit(
                state.lactation_number)
            vwp = digital_cow.herd.get_voluntary_waiting_period(
                state.lactation_number)
            dry_period = digital_cow.herd.get_duration_dry(
                state.lactation_number)
            close_up = dry_period / 2
            milk = state.milk_output
            bw = calculate_body_weight(state, age)
            dmi = calculate_dmi(state, bw)
            lactating = True
            if state.lactation_number == 0:
                lactating = False

            if (state.lactation_number != 0 and state.days_pregnant >=
                dp_limit - close_up) or (state.lactation_number == 0
                                         and state.days_in_milk < (
                    vwp / 2)) or (state.lactation_number != 0 and
                                  state.days_in_milk < 100):
                diet_cp = digital_cow.diet_cp_cu / 1000
                intake = dmi * diet_cp / 0.625

            elif (state.lactation_number != 0 and (dp_limit - dry_period)
                  <= state.days_pregnant < (dp_limit - close_up)) or (
                    state.lactation_number == 0 and
                    state.days_in_milk >= vwp / 2):
                diet_cp = digital_cow.diet_cp_fo / 1000
                intake = dmi * diet_cp / 0.625

            elif state.lactation_number != 0 \
                    and 100 <= state.days_in_milk:
                diet_cp = ((digital_cow.diet_cp_fo +
                            digital_cow.diet_cp_cu) / 2) / 1000
                intake = dmi * diet_cp / 0.625

            if lactating:
                nitrogen = manure_nitrogen_output(
                    dmi, diet_cp * 100,
                    milk, digital_cow.milk_cp)

            else:
                nitrogen = total_manure_nitrogen_output(
                    lactating, intake)[0]

            non_exit_states += 1
            vector_phenotype += nitrogen

    try:
        vector_phenotype = vector_phenotype / non_exit_states
    except ZeroDivisionError:
        vector_phenotype = 0
    if intermediate_accumulator is not None:
        intermediate_accumulator[step_in_time] = vector_phenotype
    return vector_phenotype * step_size


def set_korver_function_variables(lactation_number: int):
    """
    Returns a set of variables used for a heifer body weight function
    and the Korver function based on a given lactation number.

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
        - birth_weight: float
        - mature_live_weight: float | None
        - growth_rate: float
        - pregnancy_parameter: float | None
        - max_decrease_live_weight: float | None
        - duration_minimum_live_weight: float | None
    """

    # Source: (A. De Vries, 2006)
    # fitted on data: (Poncheki et al., 2015)
    match lactation_number:
        case 0:
            birth_weight = np.random.normal(42, 0)
            mature_live_weight = None
            growth_rate = 0.79
            pregnancy_parameter = None
            max_decrease_live_weight = None
            duration_minimum_live_weight = None
        case 1:
            birth_weight = np.random.normal(42, 0)
            mature_live_weight = np.random.normal(660, 0)
            growth_rate = np.random.normal(0.0038, 0)
            pregnancy_parameter = np.random.normal(0.012, 0)
            max_decrease_live_weight = np.random.normal(-80, 0)
            duration_minimum_live_weight = np.random.normal(50, 0)
        case 2:
            birth_weight = np.random.normal(42, 0)
            mature_live_weight = np.random.normal(695, 0)
            growth_rate = np.random.normal(0.0037, 0)
            pregnancy_parameter = np.random.normal(0.0075, 0)
            max_decrease_live_weight = np.random.normal(-70, 0)
            duration_minimum_live_weight = np.random.normal(50, 0)
        case ln if ln > 2:
            birth_weight = np.random.normal(42, 0)
            mature_live_weight = np.random.normal(700, 0)
            growth_rate = np.random.normal(0.0037, 0)
            pregnancy_parameter = np.random.normal(0.004, 0)
            max_decrease_live_weight = np.random.normal(-60, 0)
            duration_minimum_live_weight = np.random.normal(50, 0)
        case _:
            raise ValueError

    return birth_weight, mature_live_weight, growth_rate, pregnancy_parameter, \
        max_decrease_live_weight, duration_minimum_live_weight


@cache
def calculate_body_weight(state: State, age: int) -> float:
    """
    Calculates the body weight of a cow for a specific state.
    
    :param state: The ``State`` object that represents the specific day for which the
        body weight must be calculated.
    :type state: State
    :param age: The age of the cow in days.
    :type age: int
    :return: The body weight of the cow in kg in the state that is given.
    :rtype: float
    """
    # Source: (Giordano J.O., et al., 2012) (Cabrera)
    # Source: (De Vries A., 2006)
    birth_weight, mature_live_weight, growth_rate, pregnancy_parameter, \
        max_decrease_live_weight, duration_minimum_live_weight = \
        set_korver_function_variables(state.lactation_number)
    if state.lactation_number == 0:
        max_weight = 580
        start_weight = 27.2
        bw = min(max(birth_weight, start_weight + (growth_rate * state.days_in_milk)), max_weight)
    else:
        dpc = (state.days_pregnant - 50)  # d after conception - 50
        if dpc < 0:
            dpc = 0
        bw = (mature_live_weight *
              pow((1 - (1 - pow((birth_weight / mature_live_weight), (1 / 3))) *
                   math.exp(-growth_rate * age)), 3) +
              (max_decrease_live_weight * (state.days_in_milk / duration_minimum_live_weight) *
               math.exp(1 - (state.days_in_milk / duration_minimum_live_weight))) +
              (pow(pregnancy_parameter, 3) * pow(dpc, 3)))
    return bw


def set_milkbot_variables(lactation_number: int) -> tuple:
    """
    Returns MilkBot variables for a DigitalCow, based on its lactation number.

    :param lactation_number: The number of lactation cycles the cow has completed.
    :type lactation_number: int
    :returns: A tuple of parameters for the MilkBot function.

        * index = 1: scale
        * index = 2: ramp
        * index = 3: offset
        * index= 4: decay
    :rtype: tuple[float]
    :raises ValueError: If the lactation number is larger than the lactation
        number limit.
    """
    # (Hostens, M., et al, 2012)
    match lactation_number:
        case 0:
            milkbot_variables = (0, 1, 0, 1)
        case 1:
            milkbot_variables = (
                np.random.normal(41.66, 0),
                np.random.normal(29.07, 0),
                np.random.normal(0, 0),
                np.random.normal(0.001383, 0))
        case 2:
            milkbot_variables = (
                np.random.normal(56.70, 0),
                np.random.normal(21.41, 0),
                np.random.normal(0, 0),
                np.random.normal(0.002874, 0))
        case ln if ln > 2:
            milkbot_variables = (
                np.random.normal(59.69, 0),
                np.random.normal(19.71, 0),
                np.random.normal(0, 0),
                np.random.normal(0.003262, 0))
        case _:
            raise ValueError
    return milkbot_variables


@cache
def milk_production(milkbot_variables: tuple, state: State, dp_limit: int,
                    duration_dry: int) -> float:
    """
    Calculates milk production for a given state using the MilkBot algorithm.

    :param milkbot_variables: A tuple containing parameters for the MilkBot algorithm.
    :type milkbot_variables: tuple
    :param state: A ``State`` object for which milk production must be calculated.
    :type state: State
    :param dp_limit: The maximum number of days a cow can be pregnant.
    :type dp_limit: int
    :param duration_dry: The number of days before calving when a cow is not
        being milked, otherwise known as the Dry period.
    :type duration_dry: int
    :returns: The milk production for the given days in milk in kg.
    :rtype: float
    """
    # Source (Erlich, et al., 2011)
    if state.lactation_number == 0 or state.state == 'Exit' \
            or state.days_pregnant >= dp_limit - duration_dry:
        return 0.0
    scale = milkbot_variables[0]
    ramp = milkbot_variables[1]
    offset = milkbot_variables[2]
    decay = milkbot_variables[3]
    return scale * (1 - (math.exp(((offset - state.days_in_milk) / ramp)) / 2)) * math.exp(-decay * state.days_in_milk)


@cache
def calculate_dmi(state: State, body_weight: float):
    """
    Calculates the dry matter intake of a cow for a specific state.

    :param state: The ``State`` object that represents the specific day for which the
        dry matter intake must be calculated.
    :type state: State
    :param body_weight: The body weight of the cow in kg on the specific day for which
        the dry matter intake must be calculated.
    :return: The dry matter intake in kg for the specific state that is given.
    :rtype: float
    """
    # Source: (Giordano J.O., et al., 2012)
    # doi: http://dx.doi.org/10.3168/jds.2011-4972
    fcm_dim = state.milk_output * 1  # kg (fat corrected milk) multiplier when working with variable fat content.
    dmi = ((0.372 * fcm_dim + (0.0968 * pow(body_weight, 0.75))) *
           (1 - math.exp((-0.192 * ((state.days_in_milk / 7) + 3.67)))))
    return dmi


@cache
def manure_nitrogen_output(dmi: float, diet_cp: float, milk_yield: float,
                           milk_cp: float):
    """
    Returns the estimated daily nitrogen emission in manure for lactating cows 
    when dry-matter intake, dietary crude protein concentration, 
    milk yield and milk crude protein concentration are known.
    
    :param dmi: The dry-matter intake of the cow in kg.
    :type dmi: float
    :param diet_cp: The dietary crude protein concentration in %.
    :type diet_cp: float
    :param milk_yield: The milk output of the cow in kg.
    :type milk_yield: float
    :param milk_cp: The crude protein concentration in the milk of the cow in %.
    :type milk_cp: float
    :return: Manure nitrogen output in g.
    :rtype: float
    """
    # NRC 8th revised edition (2021)
    manure_n_output = ((dmi * diet_cp) / 0.625) - ((milk_yield * milk_cp) / 0.638) - 5
    return manure_n_output


def urine_nitrogen_output(lactating: bool, nitrogen_intake: float):
    """
    Returns the estimated daily nitrogen emission for a cow's urine
    based on its nitrogen intake.

    :param lactating: A boolean deciding which formulas to use based on
        whether the cow is lactating or not.
    :type lactating: bool
    :param nitrogen_intake: The amount of nitrogen consumed by the cow in g per day.
    :type nitrogen_intake: float
    :return:
        - mu_n_output: The mean nitrogen output in g.
        - min_n_output: The minimum nitrogen output in g.
        - max_n_output: The maximum nitrogen output in g.
    :rtype:
        - mu_n_output: float
        - min_n_output: float
        - max_n_output: float
    """
    # NRC 8th revised edition (2021)
    if lactating:
        # root-mean-square prediction error: 25%
        mu_n_output = (12.0 + (0.333 * nitrogen_intake))
        min_n_output = (6.2 + (0.322 * nitrogen_intake))
        max_n_output = (17.8 + (0.344 * nitrogen_intake))
    else:
        # root-mean-square prediction error: 36%
        mu_n_output = (14.3 + (0.51 * nitrogen_intake))
        min_n_output = (11.12 + (0.39 * nitrogen_intake))
        max_n_output = (17.48 + (0.63 * nitrogen_intake))
    return mu_n_output, min_n_output, max_n_output


def fecal_nitrogen_output(lactating: bool, dmi: float, nitrogen_intake: float):
    """
    Returns the estimated daily nitrogen emission for a cow's feces
    based on its nitrogen intake or dmi.

    :param lactating: A boolean deciding which formulas to use based on
        whether the cow is lactating or not.
    :type lactating: bool
    :param dmi: The dry matter intake of the cow in kg per day.
    :type dmi: float
    :param nitrogen_intake: The amount of nitrogen consumed by the cow in g per day.
    :type nitrogen_intake: float
    :return:
        - mu_n_output: The mean nitrogen output in g.
        - min_n_output: The minimum nitrogen output in g.
        - max_n_output: The maximum nitrogen output in g.
    :rtype:
        - mu_n_output: float
        - min_n_output: float
        - max_n_output: float
    """
    # NRC 8th revised edition (2021)
    if lactating:
        # root-mean-square prediction error: 16%
        mu_n_output = (-18.5 + (10.1 * dmi))
        min_n_output = (-22.09 + (9.931 * dmi))
        max_n_output = (-14.91 + (10.269 * dmi))
    else:
        # root-mean-square prediction error: 17%
        mu_n_output = (0.35 + (0.32 * nitrogen_intake))
        min_n_output = (-1.38 + (0.3136 * nitrogen_intake))
        max_n_output = (2.08 + (0.3264 * nitrogen_intake))
    return mu_n_output, min_n_output, max_n_output


@cache
def total_manure_nitrogen_output(lactating: bool, nitrogen_intake: float):
    """
    Returns estimated daily nitrogen emission of a cow's manure
    (urine and feces) based on its nitrogen intake.

    :param lactating: A boolean deciding which formulas to use based on
        whether the cow is lactating or not.
    :type lactating: bool
    :param nitrogen_intake: The amount of nitrogen consumed by the cow in g per day.
    :type nitrogen_intake: float
    :return:
        - mu_n_output: The mean nitrogen output in g.
        - min_n_output: The minimum nitrogen output in g.
        - max_n_output: The maximum nitrogen output in g.
    :rtype:
        - mu_n_output: float
        - min_n_output: float
        - max_n_output: float
    """

    # NRC 8th revised edition (2021)
    if lactating:
        # root-mean-square prediction error: 11%
        mu_n_output = (20.3 + (0.654 * nitrogen_intake))
        min_n_output = (15.58 + (0.645 * nitrogen_intake))
        max_n_output = (25.02 + (0.663 * nitrogen_intake))
    else:
        # root-mean-square prediction error: 13%
        mu_n_output = (15.1 + (0.83 * nitrogen_intake))
        min_n_output = (12.6 + (0.812 * nitrogen_intake))
        max_n_output = (17.6 + (0.848 * nitrogen_intake))
    return mu_n_output, min_n_output, max_n_output


def milk_nitrogen_output(dmi: float):
    """
    Returns the estimated daily nitrogen output in a cow's milk based on its dry
    matter intake.

    :param dmi: The dry matter intake of the cow in kg per day.
    :type dmi: float
    :return:
        - mu_n_output: The mean nitrogen output in g.
        - min_n_output: The minimum nitrogen output in g.
        - max_n_output: The maximum nitrogen output in g.
    :rtype:
        - mu_n_output: float
        - min_n_output: float
        - max_n_output: float
    """
    # NRC 8th revised edition (2021)
    # root-mean-square prediction error: 14%
    mu_n_output = (-19.0 + (8.13 * dmi))
    min_n_output = (-22.21 + (7.885 * dmi))
    max_n_output = (-15.79 + (8.375 * dmi))
    return mu_n_output, min_n_output, max_n_output


def fecal_phosphor_output(phosphor_intake: float, milk_yield: float):
    """
    Calculates the daily phosphor emission of a cow's feces based on the cow's
    phosphor intake and milk production.

    :param phosphor_intake: The amount of phosphor consumed by the cow in g per day.
    :type phosphor_intake: float
    :param milk_yield: The milk production of the cow in kg per day.
    :type milk_yield: float
    :return:
        - mu_p_output: The mean phosphor output in g.
        - min_p_output: The minimum phosphor output in g.
        - max_p_output: The maximum phosphor output in g.
    :rtype:
        - mu_p_output: float
        - min_p_output: float
        - max_p_output: float
    """
    # NRC 8th revised edition (2021)
    mu_p_output = (0.73 * phosphor_intake) - (0.37 * milk_yield)
    min_p_output = (0.7 * phosphor_intake) - (0.29 * milk_yield)
    max_p_output = (0.76 * phosphor_intake) - (0.45 * milk_yield)
    return mu_p_output, min_p_output, max_p_output
