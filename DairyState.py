class State:

    def __init__(self, state, days_in_milk, lactation_number,
                 days_pregnant=0):
        self._state = state

        # raise exception if variables are not of the correct type
        self._days_in_milk = days_in_milk
        self._lactation_number = lactation_number
        self._days_pregnant = days_pregnant

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def days_in_milk(self):
        return self._days_in_milk

    @days_in_milk.setter
    def days_in_milk(self, dim):
        self._days_in_milk = dim

    @property
    def lactation_number(self):
        return self._lactation_number

    @lactation_number.setter
    def lactation_number(self, ln):
        self._lactation_number = ln

    @property
    def days_pregnant(self):
        return self._days_pregnant

    @days_pregnant.setter
    def days_pregnant(self, dp):
        self._days_pregnant = dp
