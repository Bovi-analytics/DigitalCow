# $Id:
# Author: Gabe van den Hoeven
# Copyright:
"""


"""


from dataclasses import dataclass
from decimal import Decimal


@dataclass(repr=True, eq=True)
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
    def __init__(self, state, days_in_milk, lactation_number, days_pregnant=0,
                 milk_output=Decimal("0")):
        """Initializes an instance of a State object.

        :param state: The life state of the dairy cow
        :type state: str
        :param days_in_milk: The amount of days since the cow's last calving, or it's birth if it has not calved yet.
        :type days_in_milk: int
        :param lactation_number: The amount of lactation cycles the cow has completed.
        :type lactation_number: int
        :param days_pregnant: The amount of days that the cow is pregnant.
        :type days_pregnant: int
        :param milk_output: The amount of milk the cow produces in this state.
        :type milk_output: Decimal
        :raises ValueError: If days_pregnant is not equal to 0 and the state is not equal to 'Pregnant'.
        :raises TypeError: If the type of any variable is wrong.
        """
        if days_pregnant != 0 and state != 'Pregnant':
            raise ValueError
        self._state = state
        if not type(self._state) == str:
            raise TypeError
        self._days_in_milk = days_in_milk
        if not type(self._days_in_milk) == int:
            raise TypeError
        self._lactation_number = lactation_number
        if not type(self._lactation_number) == int:
            raise TypeError
        self._days_pregnant = days_pregnant
        if not type(self._days_pregnant) == int:
            raise TypeError
        self._milk_output = milk_output
        if not type(self._milk_output) == Decimal:
            raise TypeError

    def __str__(self):
        return f"state: {self._state}\n" \
               f"days_in_milk: {self._days_in_milk}\n" \
               f"lactation_number: {self._lactation_number}\n" \
               f"days_pregnant: {self._days_pregnant}"

    @property
    def state(self) -> str:
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def days_in_milk(self) -> int:
        return self._days_in_milk

    @days_in_milk.setter
    def days_in_milk(self, dim):
        self._days_in_milk = dim

    @property
    def lactation_number(self) -> int:
        return self._lactation_number

    @lactation_number.setter
    def lactation_number(self, ln):
        self._lactation_number = ln

    @property
    def days_pregnant(self) -> int:
        return self._days_pregnant

    @days_pregnant.setter
    def days_pregnant(self, dp):
        self._days_pregnant = dp

    @property
    def milk_output(self) -> Decimal:
        return self._milk_output

    @milk_output.setter
    def milk_output(self, mo):
        if type(mo) == Decimal:
            self._milk_output = mo
