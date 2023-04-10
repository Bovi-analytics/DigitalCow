"""
:module: digitalcow
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
    a_herd = DigitalHerd(vwp=50, insemination_cutoff=300,
    milk_threshold=Decimal("30"))\n
    cow = DigitalCow(days_in_milk=67, lactation_number=1,
    current_days_pregnant=0, herd=a_herd, state='Open')\n

c) `Set the herd of the DigitalCow`:
    1) Overwrites the DigitalHerd as the herd of the DigitalCow\n

    ``a_herd = DigitalHerd()``\n
    ``cow = DigitalCow()``\n
    ``cow.herd = a_herd``\n

    2) Adds the DigitalCow objects to the DigitalHerd and sets the DigitalHerd as
    the herd of each DigitalCow

    ``a_herd = DigitalHerd()``\n
    ``cow = DigitalCow()``\n
    ``cow2 = DigitalCow()``\n
    ``a_herd.add_to_herd(cows=[cow, cow2])``\n

    3) Overwrites the list of DigitalCow objects as the herd of the DigitalHerd

    ``a_herd = DigitalHerd()``\n
    ``cow = DigitalCow()``\n
    ``cow2 = DigitalCow()``\n
    ``a_herd.herd = [cow, cow2]``\n

3.

"""


from decimal import Decimal, getcontext
import DigitalHerd
import DairyState
import math


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
                 age_at_first_heat=None, herd=None, state='Open'):
        """
        Initializes a new instance of a DigitalCow object.

        :param days_in_milk: The amount of days since the cow's last calving,
        or it's birth if it has not calved yet. Defaults to 0.
        :type days_in_milk: int
        :param lactation_number: The amount of lactation cycles the cow has
        completed. Defaults to 0.
        :type lactation_number: int
        :param current_days_pregnant: The amount of days that the cow is pregnant.
        Defaults to 0.
        :type current_days_pregnant: int
        :param age_at_first_heat: The age in days, at which the cow had her first
        heat. Defaults to None if it has not happened yet.
        :type age_at_first_heat: int or None
        :param herd: The herd to which the cow belongs. Contains variables that
        apply to all cows in the herd.
        :type herd: DigitalHerd.DigitalHerd
        :param state: The life state of the cow. This state should be one of the
        states defined in self.__life_states.
        :type state: str
        """
        self._herd = herd
        self._current_state = DairyState.State(state, days_in_milk,
                                               lactation_number,
                                               current_days_pregnant)
        self._age_at_first_heat = age_at_first_heat
        self.__life_states = ['Open', 'Pregnant', 'DoNotBreed', 'Exit']
        self._total_states = None
        self._milkbot_variables = None
        self.__set_milkbot_variables(lactation_number)

    def generate_total_states(self, dim_limit=None, ln_limit=None) -> None:
        """
        Generates a tuple of DairyState objects that represent all possible states
        of the DigtalCow instance.

        :param dim_limit: The limit of days in milk for which states should be
            generated.
        :type dim_limit: int or None
        :param ln_limit: The limit of lactation numbers for which states should be
            generated.
        :type ln_limit: int or None
        :returns:
        """
        if dim_limit is None:
            dim_limit = self.herd.days_in_milk_limit
        if ln_limit is None:
            ln_limit = self.herd.lactation_number_limit
        total_states = []
        new_days_in_milk = self.current_days_in_milk
        new_lactation_number = self.current_lactation_number
        days_pregnant_limit = self.current_days_pregnant + 1
        if self.current_days_pregnant == 0:
            new_days_pregnant = 1
            start_as_pregnant = False
        else:
            new_days_pregnant = self.current_days_pregnant
            start_as_pregnant = True

        while new_lactation_number < ln_limit:
            self.__set_milkbot_variables(new_lactation_number)
            for state in self.__life_states:
                milk_output = self.milk_production(new_days_in_milk)
                if state == 'Pregnant':
                    if start_as_pregnant:
                        while new_days_pregnant < days_pregnant_limit:
                            new_current_state = DairyState.State(state, new_days_in_milk, new_lactation_number,
                                                                 new_days_pregnant, milk_output)
                            total_states.append(new_current_state)
                            new_days_pregnant += 1
                        days_pregnant_limit += 1
                    else:
                        while new_days_pregnant <= days_pregnant_limit:
                            new_current_state = DairyState.State(state, new_days_in_milk, new_lactation_number,
                                                                 new_days_pregnant, milk_output)
                            total_states.append(new_current_state)
                            new_days_pregnant += 1
                        new_days_pregnant = 1
                        days_pregnant_limit += 1
                else:
                    new_current_state = DairyState.State(state, new_days_in_milk, new_lactation_number, 0, milk_output)
                    total_states.append(new_current_state)
            if new_days_in_milk == dim_limit:
                new_days_in_milk = 0
                new_lactation_number += 1
            else:
                new_days_in_milk += 1
        self.total_states = tuple(total_states)

    def milk_production(self, days_in_milk=None) -> Decimal:
        """
        Calculates milk production for a given number of days in milk using the
        milkbot algorithm.

        :param days_in_milk:
        :type days_in_milk: int or None
        :returns: The milk production for the given days in milk.
            :rtype decimal.Decimal
        """
        getcontext().prec = 5

        if days_in_milk is None:
            days_in_milk = self.current_days_in_milk
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

    def probability_state_change(self, current_state: DairyState.State,
                                 new_state: DairyState.State) -> Decimal:
        """
        Calculates the probability of transitioning from current_state to new_state.

        :param current_state: The state from which to transition.
        :type current_state: DairyState.State
        :param new_state: The state to transition into.
        :type new_state: DairyState.State
        :returns: The probability of transitioning from current_state to new_state.
            :rtype: decimal.Decimal
        :raises ValueError: If the state is not defined in self.__life_states.
        """
        getcontext().prec = 7

        if new_state.state not in self.__life_states or current_state.state not in \
                self.__life_states:
            raise ValueError("State variables of a State object must be defined in "
                             "self.__life_states")

        if new_state not in self.possible_new_states(current_state):
            return Decimal("0")
        vwp = self.voluntary_waiting_period
        if new_state.days_in_milk < vwp and new_state.state == 'Pregnant':
            return Decimal("0")
        # !!!!!!!
        if (new_state.days_in_milk != current_state.days_in_milk + 1 and
                new_state.lactation_number != current_state.lactation_number + 1
                and new_state.state != 'Open'):
            return Decimal("0")

        def __probability_insemination():
            """Returns the probability for getting inseminated."""
            if current_state.days_in_milk < vwp:
                return Decimal("0")
            else:
                match current_state.lactation_number:
                    case 0:
                        return Decimal("0.7")
                    case ln if 0 < ln < self.herd.lactation_number_limit:
                        return Decimal("0.5")

        def __probability_pregnancy():
            """Returns the probability of becoming pregnant from an insemination."""
            match current_state.lactation_number:
                case 0:
                    return Decimal("0.45")
                case ln if 0 < ln < self.herd.lactation_number_limit:
                    return Decimal("0.35")

        def __probability_birth():
            """Returns the probability of calving."""
            # !!!!!!
            if current_state.days_pregnant > 282:
                return Decimal("1")
            else:
                return Decimal("0")

        def __probability_abortion():
            """Returns the probability of aborting a pregnancy."""
            # dp 30-45 12.5%
            # dp 46-180 9.9%
            # dp 181-282 2%
            if 29 < current_state.days_pregnant < 46:
                return Decimal("12.5") / Decimal("15")
            elif 45 < current_state.days_pregnant < 181:
                return Decimal("9.9") / Decimal("135")
            elif 180 < current_state.days_pregnant < 283:
                return Decimal("2") / Decimal("102")
            else:
                # !!!!!!!!!!!
                return Decimal("0")

        def __probability_above_insemination_cutoff():
            """Returns 1 if the days in milk is above the cutoff for insemination."""
            if current_state.state == 'Open' and current_state.days_in_milk > self.herd.insemination_dim_cutoff:
                return Decimal("1")
            else:
                return Decimal("0")

        def __probability_milk_below_threshold():
            """Returns 1 if the milk production falls below the milk threshold for
            staying in the herd."""
            if current_state.milk_output < self.herd.milk_threshold and not current_state.lactation_number == 0:
                return Decimal("1")
            else:
                return Decimal("0")

        def __probability_death():
            """Returns the probability of involuntary death."""
            # 0.05 / 1 y = 365 d for perinatal cows
            return Decimal("0.05") / Decimal("365")

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
                        if __probability_milk_below_threshold() == Decimal("1"):
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
                        if __probability_milk_below_threshold() == Decimal("1"):
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
                        if __probability_milk_below_threshold() == Decimal("1"):
                            return Decimal("1")
                        else:
                            return __probability_death()
                            # chance mortality or culling

            case 'Exit':
                # !!!!!!!
                match new_state.state:
                    case 'Open':
                        return Decimal("1")
                    case ('Exit' | 'Pregnant' | 'DoNotBreed'):
                        return Decimal("0")

    def __set_milkbot_variables(self, lactation_number: int) -> None:
        """
        Sets the milkbot variables for the cow, based on its lactation number.

        :param lactation_number: The number of lactation cycles the cow has completed.
        :returns:
        :raises ValueError: If the lactation number is larger than the lactation
            number limit.
        """
        getcontext().prec = 7
        match lactation_number:
            case 0:
                self.milkbot_variables = (
                    Decimal("0"), Decimal("1"), Decimal("1"), Decimal("1"))
            case 1:
                decay = Decimal("0.693") / Decimal("358")
                self.milkbot_variables = (
                    Decimal("34.8"), Decimal("29.6"), Decimal("0"), decay)
            case ln if 1 < ln < self.herd.lactation_number_limit:
                decay = Decimal("0.693") / Decimal("240")
                self.milkbot_variables = (
                    Decimal("47.7"), Decimal("22.1"), Decimal("0"), decay)
            case _:
                raise ValueError

    def possible_new_states(self, current_state: DairyState.State) -> tuple:
        """
        Returns a tuple with all states current_state can transition into.

        :param current_state: The state from which to transition.
        :type current_state: DairyState.State
        :returns: (tuple) A tuple containing all states that current_state can
            transition into.
        :raises ValueError: If the state of current_state is not valid.
        """
        if current_state is None:
            current_state = self.current_state
        self.__set_milkbot_variables(current_state.lactation_number)
        milk_output = self.milk_production(current_state.days_in_milk + 1)
        match current_state.state:
            case 'Open':
                return (
                    DairyState.State('Open', current_state.days_in_milk + 1,
                                     current_state.lactation_number, 0, milk_output),
                    DairyState.State('Pregnant', current_state.days_in_milk + 1,
                                     current_state.lactation_number, 1, milk_output),
                    DairyState.State('DoNotBreed', current_state.days_in_milk + 1,
                                     current_state.lactation_number, 0, milk_output),
                    DairyState.State('Exit', current_state.days_in_milk + 1,
                                     current_state.lactation_number, 0, Decimal("0"))
                )
            case 'Pregnant':
                return (
                    DairyState.State('Open', current_state.days_in_milk + 1,
                                     current_state.lactation_number, 0, milk_output),
                    DairyState.State('Pregnant', current_state.days_in_milk + 1,
                                     current_state.lactation_number,
                                     current_state.days_pregnant + 1, milk_output),
                    DairyState.State('DoNotBreed', current_state.days_in_milk + 1,
                                     current_state.lactation_number, 0, milk_output),
                    DairyState.State('Exit', current_state.days_in_milk + 1,
                                     current_state.lactation_number, 0, Decimal("0")),
                    DairyState.State('Open', 0, current_state.lactation_number + 1,
                                     0, Decimal("0")),
                    DairyState.State('DoNotBreed', 0,
                                     current_state.lactation_number + 1, 0,
                                     Decimal("0"))
                )
            case 'DoNotBreed':
                return (
                    DairyState.State('DoNotBreed', current_state.days_in_milk + 1,
                                     current_state.lactation_number, 0, milk_output),
                    DairyState.State('Exit', current_state.days_in_milk + 1,
                                     current_state.lactation_number, 0, Decimal("0"))
                )
            case 'Exit':
                # !!!!!!!
                return (
                    DairyState.State('Open', 0, 0, 0, Decimal("0")),
                )
            case _:
                raise ValueError('The current state given is invalid.')

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
    def milkbot_variables(self) -> tuple:
        return self._milkbot_variables

    @milkbot_variables.setter
    def milkbot_variables(self, var):
        if type(var) == tuple and len(var) == 4:
            self._milkbot_variables = var

    @property
    def voluntary_waiting_period(self) -> int:
        if self.current_state.lactation_number == 0:
            if self._age_at_first_heat is None:
                self._age_at_first_heat = self.herd.generate_age_at_first_heat()
            return self.age_at_first_heat
        else:
            return self.herd.voluntary_waiting_period

    @property
    def edge_count(self) -> int:
        # Maybe since the amount of transitions for O P DNB and E are set,
        # we can add the length for 1 day and multiply with amount of days.
        edge_count = 0
        for state in self.total_states:
            edge_count += len(self.possible_new_states(state))
        return edge_count

    @property
    def node_count(self) -> int:
        return len(self.total_states)

    @property
    def initial_state_vector(self):
        index = self.total_states.index(self.current_state)
        vector = len(self.total_states) * [0]
        vector[index] = 1
        return tuple(vector)

