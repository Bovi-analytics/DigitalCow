# $Id:
# Author: Gabe van den Hoeven
# Copyright:
"""


"""

from dataclasses import dataclass, asdict
from decimal import Decimal


@dataclass(repr=True, eq=True, frozen=True)
class State:
    """
    A class representing the state of a dairy cow.

    Attributes:
        state: The life state of the dairy cow.
            :type state: str
        days_in_milk: The amount of days since the cow's last calving, or it's birth if it has not calved yet.
            :type days_in_milk: int
        lactation_number: The amount of lactation cycles the cow has completed.
            :type lactation_number: int
        days_pregnant: The amount of days that the cow is pregnant.
            :type days_pregnant: int
        milk_output: The amount of milk the cow produces in this state.
            :type milk_output: Decimal
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
        :raises ValueError: If days_pregnant is not equal to 0 and the state is not equal to 'Pregnant' or
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
