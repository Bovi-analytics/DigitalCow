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

        Attributes
        ----------
        state : str
            The current state of the cow.
        days_in_milk : int
            The number of days the cow has been in milk.
        lactation_number : int
            The number of lactation cycles the cow has undergone.
        days_pregnant : int, optional
            The number of days the cow has been pregnant. Defaults to 0.
        milk_output : Decimal, optional
            The amount of milk the cow produces. Defaults to 0.

        Methods
        -------
        __str__()
            Returns a string representation of the state object.
        """

    # """Initializes an instance of a State object.
    #
    # :param state: The life state of the dairy cow
    # :type state: str
    # :param days_in_milk: The amount of days since the cow's last calving, or it's birth if it has not calved yet.
    # :type days_in_milk: int
    # :param lactation_number: The amount of lactation cycles the cow has completed.
    # :type lactation_number: int
    # :param days_pregnant: The amount of days that the cow is pregnant.
    # :type days_pregnant: int
    # :param milk_output: The amount of milk the cow produces in this state.
    # :type milk_output: Decimal
    # :raises ValueError: If days_pregnant is not equal to 0 and the state is not equal to 'Pregnant' or days_pregnant is 0 and the state is 'Pregnant'.
    # :raises TypeError: If the type of any variable is wrong.
    # """

    state: str
    days_in_milk: int
    lactation_number: int
    days_pregnant: int
    milk_output: Decimal

    def __post_init__(self):
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
        var = asdict(self)
        for key, value in kwargs:
            var[key] = value
        return State(**var)
