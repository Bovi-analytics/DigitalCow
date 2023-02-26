import numpy as np
from DigitalHerd import DigitalHerd


class DigitalCow(DigitalHerd):

    def __init__(self, days_in_milk=0, lactation_number=0, current_days_pregnant=0,
                 age_at_first_heat=None, condition=None, state='Open'):
        super().__init__()
        self.__current_days_in_milk = days_in_milk
        self.__current_lactation_number = lactation_number
        self.__current_days_pregnant = current_days_pregnant
        self.__age_at_first_heat = age_at_first_heat
        self.__condition = condition
        self.__herd = []
        self.__current_state = f"{state}_{self.__current_days_in_milk}_{self.__current_lactation_number}"
        self.__life_states = ['Open', 'Pregnant', 'DoNotBreed', 'Exit']
        self.__total_states = {}

    def age(self, days=1):
        new_days_in_milk = self.__current_days_in_milk
        new_days_pregnant = self.__current_days_pregnant
        new_lactation_number = self.__current_lactation_number
        for day in range(days):
            for state in self.__life_states:
                new_current_state = f"{state}_{new_days_in_milk}_{new_lactation_number}"

                # Make a list with all new states new_current_state can transition to.
                match state:
                    case 'Open':
                        new_states = {
                            f"Open_{new_days_in_milk + 1}_{new_lactation_number}": 0,
                            f"Pregnant_{new_days_in_milk + 1}_{new_lactation_number}": 0,
                            f"DoNotBreed_{new_days_in_milk + 1}_{new_lactation_number}": 0,
                            f"Exit_{new_days_in_milk + 1}_{new_lactation_number}": 0
                        }
                    case 'Pregnant':
                        new_states = {
                            f"Open_{new_days_in_milk + 1}_{new_lactation_number}": 0,
                            f"Pregnant_{new_days_in_milk + 1}_{new_lactation_number}": 0,
                            f"DoNotBreed_{new_days_in_milk + 1}_{new_lactation_number}": 0,
                            f"Exit_{new_days_in_milk + 1}_{new_lactation_number}": 0,
                            f"Open_0_{new_lactation_number + 1}": 0,
                            f"DoNotBreed_0_{new_lactation_number + 1}": 0  # maybe, have to check
                        }
                    case 'DoNotBreed':
                        new_states = {
                            f"DoNotBreed_{new_days_in_milk + 1}_{new_lactation_number}": 0,
                            f"Exit_{new_days_in_milk + 1}_{new_lactation_number}": 0
                        }
                    case 'Exit':
                        new_states = {
                            f"Exit_{new_days_in_milk + 1}_{new_lactation_number}": 0
                        }
                    case _:
                        new_states = {}
                        print('Error')

                for new_state in new_states:
                    # probabilities that the object transitions from new_current_state to new_state
                    new_states[new_state] = self.probability_state_change(new_current_state, new_state,
                                                                          dim=new_days_in_milk, ln=new_lactation_number,
                                                                          dp=new_days_pregnant)
                new_current_state = {
                    new_current_state: new_states
                    # new_current_state: {
                    #                   new_state: probability
                    #                   new_state: probability
                    #                   }
                }
                self.__total_states.update(new_current_state)
                new_days_in_milk += 1
                if new_days_pregnant > 0:
                    new_days_pregnant += 1

    def probability_state_change(self, current_state, new_state, dim=None, ln=None, dp=None):
        if new_state.split('_')[0] not in self.__life_states:
            print('Error')
        if dim is None:
            dim = self.__current_days_in_milk
        if ln is None:
            ln = self.__current_lactation_number
        if dp is None:
            dp = self.__current_days_pregnant

        if new_state.split('_')[1] != dim + 1 and new_state.split('_')[2] == ln:
            return 0.0
        match current_state.split('_')[0], new_state.split('_')[0]:
            case 'Exit', 'Exit':
                # Exit always goes to the next exit state
                return 1.0
            case 'Exit', ('Open' | 'Pregnant' | 'DoNotBreed'):
                return 0.0

        if ln == 0:
            return self.__probability_state_change_heifer(current_state, new_state, dim, dp)
        # elif ln == 1:
        #     return self.__probability_state_change_first_lactation(new_state, dim, dp)
        # elif ln >= 2:
        #     return self.__probability_state_change_new_lactation(new_state, dim, dp)
        # else:
        #     #
        #     return

    def __probability_state_change_heifer(self, current_state, new_state, days_in_milk, days_pregnant):
        age_at_first_heat = self.generate_age_at_first_heat()

        def __probability_heat():
            if days_in_milk < age_at_first_heat or days_pregnant > 0:
                return 0.0
            else:
                return 0.8

        def __probability_pregnancy():
            ##
            return 0.5

        def __probability_birth():
            return 0.4

        def __probability_abortion():
            if days_pregnant > 0:
                return 0.2
            else:
                return 0.0

        def __probability_exit():
            return 0.01

        def __probability_dnb():
            return 0.0

        match new_state.split('_')[0]:
            case 'Exit':
                return __probability_exit()
            case 'DoNotBreed':
                return __probability_dnb()
            case 'Pregnant':
                return __probability_heat() * __probability_pregnancy() * __probability_exit()
            case 'Open':
                if days_pregnant > 279:
                    return __probability_birth() * __probability_abortion() * __probability_dnb() * __probability_exit()
                elif days_pregnant > 0:
                    return __probability_abortion() * __probability_dnb() * __probability_exit()



























    def __probability_state_change_first_lactation(self, new_state, days_in_milk, days_pregnant):

        def __probability_heat():
            if days_in_milk < self.voluntary_waiting_period or days_pregnant > 0:
                return 0.0
            else:
                return 0.8

        def __probability_pregnancy():
            ##
            return 0.5

        def __probability_abortion():
            if days_pregnant > 0:
                return 0.2
            else:
                return 0.0

        def __probability_exit():
            return 0.01

        def __probability_dnb():
            return 0.0

        return __probability_heat() * __probability_pregnancy()

    def __probability_state_change_new_lactation(self, new_state, days_in_milk, days_pregnant):

        def __probability_heat():
            if days_in_milk < self.voluntary_waiting_period or days_pregnant > 0:
                return 0.0
            else:
                return 0.8

        def __probability_pregnancy():
            ##
            return 0.5

        def __probability_abortion():
            if days_pregnant > 0:
                return 0.2
            else:
                return 0.0

        def __probability_exit():
            return 0.01

        def __probability_dnb():
            return 0.0

        return __probability_heat() * __probability_pregnancy()

    def __str__(self):
        return f"DIM: {self.__current_days_in_milk}\n" \
               f"Lactation number: {self.__current_lactation_number}\n" \
               f"Days pregnant: {self.__current_days_pregnant}\n" \
               f"Current state: {self.__current_state}\n" \
               f"Condition: {self.__condition}"

    # def __repr__(self):
    #     return 'Digital twin of a dairy cow'

    @property
    def current_days_in_milk(self):
        return self.__current_days_in_milk

    @current_days_in_milk.setter
    def current_days_in_milk(self, dim):
        self.__current_days_in_milk = dim

    @property
    def current_days_pregnant(self):
        return self.__current_days_pregnant

    @current_days_pregnant.setter
    def current_days_pregnant(self, dp):
        self.__current_days_pregnant = dp

    @property
    def current_lactation_number(self):
        return self.__current_lactation_number

    @current_lactation_number.setter
    def current_lactation_number(self, ln):
        self.__current_lactation_number = ln

    @property
    def age_at_first_heat(self):
        return self.__age_at_first_heat

    @age_at_first_heat.setter
    def age_at_first_heat(self, age_at_first_heat):
        self.__age_at_first_heat = age_at_first_heat

    @property
    def current_state(self):
        return self.__current_state

    @current_state.setter
    def current_state(self, state):
        # must be state_dim_ln
        self.__current_state = state

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, condition):
        self.__condition = condition

    @property
    def total_states(self):
        return self.__total_states

    # @total_states.setter
    # def total_states(self, states):
    #     self.__total_states = states
