from decimal import Decimal, getcontext


def probability_state_change(self, current_state, new_state) -> Decimal:
    """

    :param current_state:
    :param new_state:
    :return:
    """
    getcontext().prec = 4

    if new_state.state not in self.__life_states:
        raise ValueError("new_state must be defined in self.__life_states")

    # if (new_state.days_in_milk != current_state.days_in_milk + 1 and
    #     new_state.lactation_number != current_state.lactation_number + 1
    #     and current_state.state != 'Exit') or new_state not in possible_new_states(current_state):
    #     return Decimal("0")

    if current_state.lactation_number == 0:
        if self.age_at_first_heat is None:
            self.age_at_first_heat = self.herd.generate_age_at_first_heat()
        vwp = self.age_at_first_heat
    else:
        vwp = self.herd.voluntary_waiting_period

    def __probability_insemination():
        if current_state.days_in_milk < vwp:
            return Decimal("0")
        else:
            match current_state.lactation_number:
                case 0:
                    return Decimal("0.7")
                case (1 | 2 | 3):
                    return Decimal("0.5")

    def __probability_pregnancy():
        match current_state.lactation_number:
            case 0:
                return Decimal("0.45")
            case (1 | 2 | 3):
                return Decimal("0.35")

    def __probability_birth():
        # !!!!!!
        if current_state.days_pregnant > 282:
            return Decimal("1")
        else:
            return Decimal("0")

    def __probability_abortion():
        # dp 30-45 12.5%
        # dp 46-180 9.9%
        # dp 181-282 2%
        if current_state.days_pregnant > 0:
            return Decimal("0.2")
        # !!!!!!
        else:
            return Decimal("0")

    def __probability_dnb():
        if current_state.days_in_milk > 300:
            return Decimal("1")
        else:
            return Decimal("0")

    def __probability_stay_dnb():
        if current_state.milk_output > self.herd.milk_threshold:
            return Decimal("1")
        else:
            return Decimal("0")

    def __probability_exit():
        # 5% / y
        return Decimal("0.01")

    match current_state.state:
        case 'Open':
            match new_state.state:
                case 'Open':
                    if current_state.days_in_milk < vwp:
                        return Decimal("1")
                    else:
                        return (Decimal("1") - __probability_exit()) * (Decimal("1") -
                                                                        (__probability_insemination() *
                                                                         __probability_pregnancy()))
                    # chance staying open
                case 'Pregnant':
                    return __probability_insemination() * __probability_pregnancy()
                    # chance becoming pregnant
                case 'DoNotBreed':
                    return __probability_dnb()
                    # chance becoming dnb
                case 'Exit':
                    return __probability_exit()
                    # mortality

        case 'Pregnant':
            match new_state.state:
                case 'Open':
                    return Decimal("0")

                case 'Pregnant':
                    return (Decimal("1") - __probability_exit()) * (Decimal("1") - __probability_abortion())
                    # chance staying pregnant
                case 'DoNotBreed':
                    if current_state.days_pregnant > 279:
                        return Decimal(
                            __probability_birth() * __probability_dnb())
                        # chance calving and dnb or aborting dnb
                    else:
                        return Decimal(
                            __probability_abortion() * __probability_dnb())
                case 'Exit':
                    return __probability_exit()
                    # mortality
        case 'DoNotBreed':
            match new_state.state:
                case 'Open':
                    return Decimal("0")
                case 'Pregnant':
                    return Decimal("0")
                case 'DoNotBreed':
                    return __probability_stay_dnb()
                    # chance staying DoNotBreed
                case 'Exit':
                    return __probability_exit()
                    # chance mortality or culling
        case 'Exit':
            match new_state.state:
                case 'Exit':
                    return Decimal("1")
                case ('Open' | 'Pregnant' | 'DoNotBreed'):
                    return Decimal("0")

    # elif current_state.lactation_number == 1:
    #     return self.__probability_state_change_first_lactation(current_state,
    #                                                            new_state)
    # elif current_state.lactation_number >= 2:
    #     return self.__probability_state_change_new_lactation(current_state,
    #                                                          new_state)
    # else:
    #     raise ValueError("Lactation number should be equal to or greater than 0")


def __probability_state_change_first_lactation(self, current_state,
                                               new_state) -> Decimal:
    """

    :param current_state:
    :param new_state:
    :return:
    """

    def __probability_insemination():
        if current_state.days_in_milk < self.herd.voluntary_waiting_period:
            return Decimal("0")
        else:
            return Decimal("0.7")

    def __probability_pregnancy():
        ##
        return Decimal("0.45")

    def __probability_birth():
        return Decimal("0.4")

    def __probability_abortion():
        if current_state.days_pregnant > 0:
            return Decimal("0.25")
        else:
            return Decimal("0")

    def __probability_exit():
        return Decimal("0.015")

    def __probability_dnb():
        return Decimal("0.01")

    def __probability_stay_open():
        return Decimal("0.5")

    def __probability_stay_pregnant():
        return Decimal("0.8")

    def __probability_stay_dnb():
        return Decimal("0.6")

    match current_state.state:
        case 'Open':
            match new_state.state:
                case 'Open':
                    return __probability_stay_open()
                    # chance staying open
                case 'Pregnant':
                    return Decimal(
                        __probability_insemination() * __probability_pregnancy())
                    # chance becoming pregnant
                case 'DoNotBreed':
                    return __probability_dnb()
                    # chance becoming dnb
                case 'Exit':
                    return __probability_exit()
                    # mortality
        case 'Pregnant':
            match new_state.state:
                case 'Open':
                    if current_state.days_pregnant > 279:
                        return __probability_birth()  # * __probability_abortion()
                        # chance aborting or calving
                    else:
                        return __probability_abortion()
                        # chance aborting
                case 'Pregnant':
                    return __probability_stay_pregnant()
                    # chance staying pregnant
                case 'DoNotBreed':
                    if current_state.days_pregnant > 279:
                        return Decimal(
                            __probability_birth() * __probability_dnb())
                        # chance calving and dnb or aborting dnb
                    else:
                        return Decimal(
                            __probability_abortion() * __probability_dnb())
                case 'Exit':
                    return __probability_exit()
                    # mortality
        case 'DoNotBreed':
            match new_state.state:
                case 'Open':
                    return Decimal("0")
                case 'Pregnant':
                    return Decimal("0")
                case 'DoNotBreed':
                    return __probability_stay_dnb()
                    # chance staying DoNotBreed
                case 'Exit':
                    return __probability_exit()
                    # chance mortality or culling
        case 'Exit':
            match new_state.state:
                case 'Exit':
                    return Decimal("1")
                case ('Open' | 'Pregnant' | 'DoNotBreed'):
                    return Decimal("0")


def __probability_state_change_new_lactation(self, current_state,
                                             new_state) -> Decimal:
    """

    :param current_state:
    :param new_state:
    :return:
    """

    def __probability_insemination():
        if current_state.days_in_milk < self.herd.voluntary_waiting_period:
            return Decimal("0")
        else:
            return Decimal("0.5")

    def __probability_pregnancy():
        ##
        return Decimal("0.35")

    def __probability_birth():
        return Decimal("0.4")

    def __probability_abortion():
        if current_state.days_pregnant > 0:
            return Decimal("0.37")
        else:
            return Decimal("0")

    def __probability_exit():
        return Decimal("0.02")

    def __probability_dnb():
        return Decimal("0.001")

    def __probability_stay_open():
        return Decimal("0.5")

    def __probability_stay_pregnant():
        return Decimal("0.8")

    def __probability_stay_dnb():
        return Decimal("0.6")

    match current_state.state:
        case 'Open':
            match new_state.state:
                case 'Open':
                    return __probability_stay_open()
                    # chance staying open
                case 'Pregnant':
                    return Decimal(
                        __probability_insemination() * __probability_pregnancy())
                    # chance becoming pregnant
                case 'DoNotBreed':
                    return __probability_dnb()
                    # chance becoming dnb
                case 'Exit':
                    return __probability_exit()
                    # mortality
        case 'Pregnant':
            match new_state.state:
                case 'Open':
                    if current_state.days_pregnant > 279:
                        return __probability_birth()  # * __probability_abortion()
                        # chance aborting or calving
                    else:
                        return __probability_abortion()
                        # chance aborting
                case 'Pregnant':
                    return __probability_stay_pregnant()
                    # chance staying pregnant
                case 'DoNotBreed':
                    if current_state.days_pregnant > 279:
                        return Decimal(
                            __probability_birth() * __probability_dnb())
                        # chance calving and dnb or aborting dnb
                    else:
                        return Decimal(
                            __probability_abortion() * __probability_dnb())
                case 'Exit':
                    return __probability_exit()
                    # mortality
        case 'DoNotBreed':
            match new_state.state:
                case 'Open':
                    return Decimal("0")
                case 'Pregnant':
                    return Decimal("0")
                case 'DoNotBreed':
                    return __probability_stay_dnb()
                    # chance staying DoNotBreed
                case 'Exit':
                    return __probability_exit()
                    # chance mortality or culling
        case 'Exit':
            match new_state.state:
                case 'Exit':
                    return Decimal("1")
                case ('Open' | 'Pregnant' | 'DoNotBreed'):
                    return Decimal("0")
