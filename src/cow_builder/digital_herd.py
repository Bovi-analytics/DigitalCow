# $Id:
# Copyright:
"""
:module: digital_herd
:module author: Gabe van den Hoeven
:synopsis: This module contains the DigitalHerd class representing a dairy herd.

======================
How To Use This Module
======================
(See the individual classes, methods, and attributes for details.)\n
This module is to be used in conjunction with the ``DigitalCow`` class.
The DigitalHerd contains certain variables used by the ``DigitalCow`` class for
simulation purposes. These variables are the same for all ``DigitalCow`` instances
in the herd.\n
*Values in this HowTo are examples, see documentation of each class or function
for details on the default values.*

1. Import the class DigitalHerd:
********************************
Import the class with:\n

    ``from cow_builder.digital_herd import DigitalHerd``.\n

************************************************************

2. Create a DigitalHerd instance:
*********************************
Since default values are provided for the DigitalHerd class, it can be created as
follows:\n

a) without parameters:

    ``new_herd = DigitalHerd()``

b) with parameters:

    ``new_herd = DigitalHerd(milk_threshold=5)``\n

*For details about the parameters, look at the* \ ``__init__``\  *method.*

************************************************************

3. Alter the herd:
******************
There are a few different methods that can be used to alter the herd list of a
DigitalHerd instance. These alterations will also affect the ``DigitalCow`` objects
that are added or removed from the herd.

1) Adds the ``DigitalCow`` objects to the DigitalHerd and sets the DigitalHerd as the herd of each ``DigitalCow``:

    ``a_herd = DigitalHerd()``\n
    ``cow = DigitalCow()``\n
    ``cow2 = DigitalCow()``\n
    ``a_herd.add_to_herd(cows=[cow, cow2])``\n

2) Removes the ``DigitalCow`` objects from the DigitalHerd and sets the herd of each ``DigitalCow`` to None:

    ``a_herd = DigitalHerd()``\n
    ``cow = DigitalCow(herd=a_herd)``\n
    ``cow2 = DigitalCow(herd=a_herd)``\n
    ``a_herd.remove_from_herd(cows=[cow, cow2])``\n

3) Overwrites the list of ``DigitalCow`` objects as the herd of the DigitalHerd and the DigitalHerd as the herd of each ``DigitalCow``:

    ``a_herd = DigitalHerd()``\n
    ``cow = DigitalCow()``\n
    ``cow2 = DigitalCow()``\n
    ``a_herd.herd = [cow, cow2]``\n

************************************************************

"""


import numpy as np
from cow_builder import digital_cow


class DigitalHerd:
    """
    A class to represent a digital herd of cows and manage their properties.

    :Attributes:
        :var _mu_age_at_first_heat: The mean age in days at which a cow
            will experience its first estrus.
        :type _mu_age_at_first_heat: int
        :var _sigma_age_at_first_heat: The standard deviation in days of the age
            at which a cow will experience its first estrus.
        :type _sigma_age_at_first_heat: int
        :var _voluntary_waiting_period: The voluntary waiting period in days before a
            cow can be inseminated. Values in the tuple are for lactation 0, 1,
            and 2+.
        :type _voluntary_waiting_period: tuple[int]
        :var _milk_threshold: The minimum milk production in kg
            to be considered as a productive cow.
        :type _milk_threshold: float
        :var _insemination_window: The number of days in milk since the
            voluntary waiting period after which a cow is no longer eligible for
            insemination. Values in the tuple are for lactation 0, 1, and 2+.
        :type _insemination_window: tuple[int]
        :var _herd: A list of ``DigitalCow`` objects representing the cows in
            the herd.
        :type _herd: list[DigitalCow]
        :var _days_in_milk_limit: The maximum number of days since calving or birth a
            cow can have before being culled.
        :type _days_in_milk_limit: int
        :var _lactation_number_limit: The maximum number of lactation cycles
            a cow can have completed before being culled.
        :type _lactation_number_limit: int
        :var _days_pregnant_limit: The maximum number of days a cow can be
            pregnant. Values in the tuple are for lactation 0, 1, and 2+.
        :type _days_pregnant_limit: tuple[int]
        :var _duration_dry: The number of days before calving, when a cow is not
            being milked. Values in the tuple are for lactation 1 and 2+.
        :type _duration_dry: tuple[int]

    :Methods:
        __init__(mu_age_at_first_heat, sigma_age_at_first_heat, vwp,
        insemination_window, milk_threshold, days_in_milk_limit,
        lactation_number_limit, days_pregnant_limit, duration_dry)\n
        add_to_herd(cows)\n
        remove_from_herd(cows)\n
        calculate_mu_age_at_first_heat()\n
        generate_age_at_first_heat()\n
        get_voluntary_waiting_period(lactation_number)\n
        set_voluntary_waiting_period(vwp)\n
        get_insemination_window(lactation_number)\n
        set_insemination_window(dim_window)\n
        get_days_pregnant_limit(lactation_number)\n
        set_days_pregnant_limit(limit)\n
        get_duration_dry(lactation_number)\n
        set_duration_dry(duration_dry)\n

    ************************************************************
    """
    def __init__(self, mu_age_at_first_heat=365, sigma_age_at_first_heat=0,
                 vwp=(365, 80, 60), insemination_window=(100, 100, 100),
                 milk_threshold=10, days_in_milk_limit=1000,
                 lactation_number_limit=9, days_pregnant_limit=(279, 280, 282),
                 duration_dry=(60, 60)):
        """
        Initializes an instance of a DigitalHerd object.

        :param mu_age_at_first_heat: The mean age in days at which a cow
            will experience its first estrus.
        :type mu_age_at_first_heat: int
        :param sigma_age_at_first_heat: The standard deviation of the age
            at which a cow will experience its first estrus.
        :type sigma_age_at_first_heat: int
        :param vwp: The voluntary waiting period in days before a
            cow can be inseminated. Values in the tuple are for lactation 0, 1,
            and 2+.
        :type vwp: tuple[int]
        :param insemination_window: The insemination window in days after
            which a cow is no longer eligible for insemination. Values in the tuple
            are for lactation 0, 1, and 2+.
        :type insemination_window: tuple[int]
        :param milk_threshold: The minimum milk production in kg
            to be considered as a productive cow. Default is 10.
        :type milk_threshold: float
        :param days_in_milk_limit: The maximum number of days a cow can be in milk
            before being culled.
        :type days_in_milk_limit: int
        :param lactation_number_limit: The maximum number of lactation cycles a cow
            can have completed before being culled.
        :type lactation_number_limit: int
        :param days_pregnant_limit: The maximum number of days a cow can be pregnant.
            Values in the tuple are for lactation 0, 1, and 2+.
        :type days_pregnant_limit: tuple[int]
        :param duration_dry: The number of days before calving, when a cow is not
            being milked. Values in the tuple are for lactation 1 and 2+.
        :type duration_dry: tuple[int]
        """
        self._mu_age_at_first_heat = mu_age_at_first_heat
        self._sigma_age_at_first_heat = sigma_age_at_first_heat
        self._voluntary_waiting_period = vwp
        self._milk_threshold = milk_threshold
        self._insemination_window = insemination_window
        self._herd = []
        self._days_in_milk_limit = days_in_milk_limit
        self._lactation_number_limit = lactation_number_limit
        self._days_pregnant_limit = days_pregnant_limit
        self._duration_dry = duration_dry
        # other general properties shared between the entities in the _herd

    def add_to_herd(self, cows: list) -> None:
        """
        Takes a list of ``DigitalCow`` objects and adds each cow to the herd if they
        are not in the herd already.

        :param cows: A list of ``DigitalCow`` objects which are to be added to
            the herd.
        :type cows: list[DigitalCow]
        :raises TypeError: If the list given does not solely consist of ``DigitalCow``
            objects.
        """
        if cows is not None:
            for cow in cows:
                if isinstance(cow, digital_cow.DigitalCow):
                    if cow not in self.herd:
                        self.herd.append(cow)
                        cow._herd = self
                else:
                    raise TypeError("The given list should only contain DigitalCow "
                                    "objects.")

    def remove_from_herd(self, cows: list) -> None:
        """
        Takes a list of ``DigitalCow`` objects and removes each cow from the herd
        if they are present in the herd.

        :param cows: A list of ``DigitalCow`` objects which are to be removed from the
            herd.
        :type cows: list[DigitalCow]
        :raises TypeError: If the list given does not solely consist of ``DigitalCow``
            objects.
        """
        if cows is not None:
            for cow in cows:
                if isinstance(cow, digital_cow.DigitalCow):
                    if cow in self.herd:
                        self.herd.remove(cow)
                        cow._herd = None
                else:
                    raise TypeError("The given list should only contain DigitalCow "
                                    "objects.")

    def calculate_mu_age_at_first_heat(self):
        """Calculates the mean age in days at which a cow in the herd will experience
        its first estrus.
        """
        mu_age_at_first_heat = 0
        for cow in self.herd:
            if cow.age_at_first_heat is not None:
                mu_age_at_first_heat += cow.age_at_first_heat
        mu_age_at_first_heat = mu_age_at_first_heat / len(self.herd)
        if not mu_age_at_first_heat == 0:
            self.mu_age_at_first_heat = round(mu_age_at_first_heat)

    def generate_age_at_first_heat(self) -> int:
        """
        Returns a random age at first heat based on the mean age at first heat
        and its standard deviation.

        :returns: A random age at first heat based on the mean age at first heat and its standard deviation.
        :rtype: int
        """
        self.calculate_mu_age_at_first_heat()
        return np.random.normal(self.mu_age_at_first_heat,
                                self.sigma_age_at_first_heat)

    @property
    def mu_age_at_first_heat(self):
        """The mean age in days at which a cow in the herd will experience
        its first estrus."""
        return self._mu_age_at_first_heat

    @mu_age_at_first_heat.setter
    def mu_age_at_first_heat(self, mu: int):
        self._mu_age_at_first_heat = mu

    @property
    def sigma_age_at_first_heat(self):
        """The standard deviation of the age at which a cow will experience
        its first estrus."""
        return self._sigma_age_at_first_heat

    @sigma_age_at_first_heat.setter
    def sigma_age_at_first_heat(self, sigma: int):
        self._sigma_age_at_first_heat = sigma

    @property
    def herd(self) -> list:
        """A list of ``DigitalCow`` objects that represents all the cows in the herd."""
        return self._herd

    @herd.setter
    def herd(self, herd: list):
        all_instances = True
        if type(herd) == list:
            for cow in herd:
                if not isinstance(cow, digital_cow.DigitalCow):
                    all_instances = False
            if all_instances:
                self._herd = herd
                for cow in self._herd:
                    cow.herd = self
            else:
                raise TypeError(
                    "Herd property must be a list containing only DigitalCow "
                    "objects.")

    def get_voluntary_waiting_period(self, lactation_number: int) -> int:
        """
        Returns the voluntary waiting period of a cow in the herd for a given
        lactation number.

        :param lactation_number: The number of lactation cycles the cow has completed.
        :type lactation_number: int
        :returns: The voluntary waiting period in days.
        :rtype: int
        """
        if lactation_number > 2:
            lactation_number = 2
        return self._voluntary_waiting_period[lactation_number]

    def set_voluntary_waiting_period(self, vwp: tuple[int]):
        """
        Sets the voluntary waiting periods for cows in the herd.

        :param vwp: A tuple with the voluntary waiting periods in days before a
            cow can be inseminated. Values in the tuple are for lactation 0, 1,
            and 2+.
        :type vwp: tuple[int]
        """
        for i in vwp:
            if not type(i) == int:
                raise TypeError
        self._voluntary_waiting_period = vwp

    @property
    def milk_threshold(self) -> float:
        """The milk threshold for all cows in the herd. If the milk production
        falls below this threshold, they will be culled."""
        return self._milk_threshold

    @milk_threshold.setter
    def milk_threshold(self, mt: float):
        if type(mt) == float:
            self._milk_threshold = mt

    def get_insemination_window(self, lactation_number: int) -> int:
        """
        Returns the insemination window of a cow in the herd for a given lactation
        number.

        :param lactation_number: The number of lactation cycles the cow has completed.
        :type lactation_number: int
        :return: The insemination window in days.
        :rtype: int
        """
        if lactation_number > 2:
            lactation_number = 2
        return self._insemination_window[lactation_number]
        # TODO CHECK
        # While creating the states, there would be 1 extra day pregnant state
        # making the insemination window one day longer.
        # The - 1 solves this issue without interfering with other parts of the code.

    def set_insemination_window(self, dim_window: tuple[int]):
        """
        Sets the insemination windows for cows in the herd.

        :param dim_window: A tuple with insemination windows in days when a cow can
            be inseminated. Values in the tuple are for lactation 0, 1, and 2+.
        :type dim_window: tuple[int]
        """
        for i in dim_window:
            if not type(i) == int:
                raise TypeError
        self._insemination_window = dim_window

    @property
    def days_in_milk_limit(self) -> int:
        """The maximum number of days after calving or birth before being culled."""
        return self._days_in_milk_limit

    @days_in_milk_limit.setter
    def days_in_milk_limit(self, limit: int):
        self._days_in_milk_limit = limit

    @property
    def lactation_number_limit(self) -> int:
        """The maximum number of lactation cycles a cow can complete before being
        culled."""
        return self._lactation_number_limit

    @lactation_number_limit.setter
    def lactation_number_limit(self, limit: int):
        self._lactation_number_limit = limit

    def get_days_pregnant_limit(self, lactation_number: int) -> int:
        """
        Returns the number of days a cow can be pregnant for a given lactation
        number.

        :param lactation_number: The number of lactation cycles the cow has completed.
        :type lactation_number: int
        :returns: The number of days a cow can be pregnant for the given lactation
            number.
        :rtype: int
        """
        if lactation_number > 2:
            lactation_number = 2
        return self._days_pregnant_limit[lactation_number]

    def set_days_pregnant_limit(self, limit: tuple[int]):
        """
        Sets the maximum number of days a cow in the herd can be pregnant.

        :param limit: A tuple containing limits for number of days a cow can be
            pregnant. Values in the tuple are for lactation 0, 1, and 2+.
        :type limit: tuple[int]
        """
        for i in limit:
            if not type(i) == int:
                raise TypeError
        self._days_pregnant_limit = limit

    def get_duration_dry(self, lactation_number) -> int:
        """
        Returns the dry period for a cow in the herd based on a given lactation
        number.

        :param lactation_number: The number of lactation cycles the cow has completed.
        :type lactation_number: int
        :return: The dry period in days for a cow in the given lactation cycle.
        :rtype: int
        """
        if lactation_number > 1:
            lactation_number = 1
        return self._duration_dry[lactation_number]

    def set_duration_dry(self, duration_dry: tuple[int]):
        """
        Sets the dry periods for all cows in the herd.

        :param duration_dry: A tuple containing the length of dry periods for cow
            with a specific lactation number. Values in the tuple are for
            lactation 1 and 2+.
        :type duration_dry: tuple[int]
        """
        for i in duration_dry:
            if not type(i) == int:
                raise TypeError
        self._duration_dry = duration_dry
