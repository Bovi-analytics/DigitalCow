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

    # !!!!!!!
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
                case range(1, 9):
                    return Decimal("0.5")

    def __probability_pregnancy():
        match current_state.lactation_number:
            case 0:
                return Decimal("0.45")
            case range(1, 9):
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
        if 29 < current_state.days_pregnant < 45:
            return Decimal("0.0083333")
        elif 45 < current_state.days_pregnant < 180:
            return Decimal("0.0007333")
        elif 180 < current_state.days_pregnant < 283:
            return Decimal("0.0001961")
        else:
            return Decimal("0")

    def __probability_above_dim_cutoff():
        # !!!!!
        if current_state.state == 'Open' and current_state.days_in_milk > self.herd.insemination_dim_cutoff:
            return Decimal("1")
        else:
            return Decimal("0")

    def __probability_milk_below_threshold():
        if current_state.milk_output < self.herd.milk_threshold:
            return Decimal("1")
        else:
            return Decimal("0")

    def __probability_death():
        # 5% / y
        # !!!!!!!!!!!!!!
        match current_state.lactation_number:
            case 0:
                return Decimal("0.0001369")
            case range(1, 9):
                return Decimal("0")

    match current_state.state:
        case 'Open':
            match new_state.state:
                case 'Open':
                    if current_state.days_in_milk < vwp:
                        return (Decimal("1") - __probability_death()) * (Decimal("1") - __probability_milk_below_threshold())
                    else:
                        return (Decimal("1") - __probability_death()) * (Decimal("1") - (__probability_insemination() * __probability_pregnancy())) * (Decimal("1") - __probability_milk_below_threshold()) * (Decimal("1") - __probability_above_dim_cutoff())
                    # chance staying open
                case 'Pregnant':
                    return (__probability_insemination() * __probability_pregnancy()) * (Decimal("1") - __probability_death()) * (Decimal("1") - __probability_milk_below_threshold()) * (Decimal("1") - __probability_above_dim_cutoff())
                    # chance becoming pregnant
                case 'DoNotBreed':
                    return __probability_above_dim_cutoff() * (Decimal("1") - __probability_death()) * (Decimal("1") - __probability_milk_below_threshold())
                    # chance becoming dnb
                case 'Exit':
                    # !!!!!!!
                    if current_state.milk_output < self.herd.milk_threshold and not current_state.days_in_milk < vwp:
                        return Decimal("1")
                    else:
                        return __probability_death()
                    # chance mortality or culling

        case 'Pregnant':
            match new_state.state:
                case 'Open':
                    if new_state.lactation_number == current_state.lactation_number + 1:
                        return __probability_birth() * (Decimal("1") - __probability_death())
                    else:
                        return __probability_abortion() * (Decimal("1") - __probability_death())
                case 'Pregnant':
                    return (Decimal("1") - __probability_death()) * (Decimal("1") - __probability_abortion())
                    # chance staying pregnant
                case 'DoNotBreed':
                    # !!!!!!!
                    return Decimal("0")
                case 'Exit':
                    # !!!!!!!
                    if current_state.milk_output < self.herd.milk_threshold and not current_state.days_in_milk < vwp:
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
                    # !!!!!!!
                    if current_state.milk_output < self.herd.milk_threshold and not current_state.days_in_milk < vwp:
                        return Decimal("1")
                    else:
                        return __probability_death()
                    # chance mortality or culling

        case 'Exit':
            # !!!!!!!
            match new_state.state:
                case 'Exit':
                    return Decimal("1")
                case ('Open' | 'Pregnant' | 'DoNotBreed'):
                    return Decimal("0")
