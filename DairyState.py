# $Id:
# Copyright:
"""
:module: DairyState
:module author: Gabe van den Hoeven
    :synopsis: This module contains the State dataclass representing a state of a cow.
        This class is used by the DigitalCow class.

======================
How To Use This Module
======================
(See the individual classes, methods, and attributes for details.)\n
As a dataclass, the State class is purely used as a collection of variables.\n
An instance, once created, cannot be altered except by using the mutate method,
which returns a new altered instance of the class.\n
If two State instances with the same instance values are compared, they will be
considered equal.

"""

from dataclasses import dataclass, asdict
from decimal import Decimal


@dataclass(repr=True, eq=True, frozen=True)
class State:
    """
    A class representing the state of a dairy cow.

    Attributes:
        state : str
            The life state of the dairy cow.
        days_in_milk : int
            The amount of days since the cow's last calving,
            or it's birth if it has not calved yet.
        lactation_number : int
            The amount of lactation cycles the cow has completed.
        days_pregnant : int
            The amount of days that the cow is pregnant.
        milk_output : decimal.Decimal
            The amount of milk the cow produces in this state.

    Methods:
        __post_init__()
        mutate(**kwargs)
    """

    state: str
    days_in_milk: int
    lactation_number: int
    days_pregnant: int
    milk_output: Decimal

    def __post_init__(self):
        """
        Post-init check for illegal variable types and value-combinations.

        :raises TypeError: If the type of any variable is wrong.
        :raises ValueError: If days_pregnant is not equal to 0 and the state
            is not equal to 'Pregnant' or
            days_pregnant is 0 and the state is 'Pregnant'.
        """
        if self.days_pregnant != 0 and self.state != 'Pregnant':
            raise ValueError
        if self.days_pregnant == 0 and self.state == 'Pregnant':
            raise ValueError
        if not type(self.state) == str:
            raise TypeError
        if not type(self.days_in_milk) == int:
            raise TypeError
        if not type(self.lactation_number) == int:
            raise TypeError
        if not type(self.days_pregnant) == int:
            raise TypeError
        if not type(self.milk_output) == Decimal:
            raise TypeError

    def mutate(self, **kwargs):
        """
        Takes an argument of the state class and returns a new instance with the changed value.
        This function can be used to change values in a state object by having the returned instance overwrite
        the original instance.

        :param kwargs: The keyword and value pairs of the new state that need to be changed.
        :return: The new state with the changed values.
            :rtype: DairyState.State
        """
        var = asdict(self)
        for key, value in kwargs:
            var[key] = value
        return State(**var)
