from dataclasses import dataclass
from decimal import Decimal


@dataclass(repr=True, eq=True)
class State:

    def __init__(self, state, days_in_milk, lactation_number, days_pregnant=0,
                 milk_output=Decimal("0")):
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
