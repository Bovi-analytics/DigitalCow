import math
import numpy as np
import matplotlib.pyplot as plt


def bw(days_in_milk: int, days_pregnant: int, age: int, ln: int):

    dpc = (days_pregnant - 50)  # d after conception - 50
    if dpc < 0:
        dpc = 0

    birth_weight = np.random.normal(42, 0)
    mature_live_weight = None
    growth_rate = None
    pregnancy_parameter = None
    max_decrease_live_weight = None
    duration_minimum_live_weight = None
    match ln:
        case 1:
            birth_weight = np.random.normal(42, 0)
            mature_live_weight = np.random.normal(660, 0)
            growth_rate = np.random.normal(0.0038, 0)
            pregnancy_parameter = np.random.normal(0.012, 0)
            max_decrease_live_weight = np.random.normal(-80, 0)
            duration_minimum_live_weight = np.random.normal(50, 0)
        case 2:
            birth_weight = np.random.normal(42, 0)
            mature_live_weight = np.random.normal(695, 0)
            growth_rate = np.random.normal(0.0037, 0)
            pregnancy_parameter = np.random.normal(0.0075, 0)
            max_decrease_live_weight = np.random.normal(-70, 0)
            duration_minimum_live_weight = np.random.normal(50, 0)
        case ln if ln > 2:
            birth_weight = np.random.normal(42, 0)
            mature_live_weight = np.random.normal(700, 0)
            growth_rate = np.random.normal(0.0037, 0)
            pregnancy_parameter = np.random.normal(0.004, 0)
            max_decrease_live_weight = np.random.normal(-60, 0)
            duration_minimum_live_weight = np.random.normal(50, 0)

    body_weight = (mature_live_weight * math.pow((1 - (1 - math.pow((birth_weight / mature_live_weight), (1 / 3))) *
                                                  math.exp(-growth_rate * age)), 3) +
                   (max_decrease_live_weight * (days_in_milk / duration_minimum_live_weight) *
                    math.exp(1 - (days_in_milk / duration_minimum_live_weight))) +
                   (math.pow(pregnancy_parameter, 3) * math.pow(dpc, 3)))
    return body_weight


def bw2(days_in_milk: int):

    birth_weight = np.random.normal(42, 0)
    max_weight = 580
    growth_rate = 0.79
    body_weight = min(max(birth_weight, 27.2 + (growth_rate * days_in_milk)), max_weight)

    return body_weight


def dmi(days_in_milk: int, body_weight: float, milk: float):
    fcm_dim = milk * 1  # kg (fat corrected milk) 4% FCM production
    dmi = ((0.372 * fcm_dim + (0.0968 * pow(body_weight, 0.75))) *
           (1 - math.exp((-0.192 * ((days_in_milk / 7) + 3.67)))))
    return dmi


def milk_production(days_in_milk: int, lactation: int, days_pregnant: int, dp_limit: int, duration_dry: int) -> float:
    match lactation:
        case 0:
            scale = 0
            ramp = 1
            offset = 0
            decay = 1
        case 1:
            scale = np.random.normal(41.66, 0)
            ramp = np.random.normal(29.07, 0)
            offset = np.random.normal(0, 0)
            decay = np.random.normal(0.001383, 0)
        case 2:
            scale = np.random.normal(56.70, 0)
            ramp = np.random.normal(21.41, 0)
            offset = np.random.normal(0, 0)
            decay = np.random.normal(0.002874, 0)
        case ln if ln > 2:
            scale = np.random.normal(59.69, 0)
            ramp = np.random.normal(19.71, 0)
            offset = np.random.normal(0, 0)
            decay = np.random.normal(0.003262, 0)
        case _:
            raise ValueError
    if lactation == 0 or days_pregnant >= dp_limit - duration_dry:
        return 0.0
    milk = scale * (1 - (pow(math.e, ((offset - dim) / ramp)) / 2)) * pow(math.e, -decay * days_in_milk)
    return milk


def total_manure_nitrogen_output(lactating: bool, nitrogen_intake: float):
    # NRC 8th revised edition (2021)
    if lactating:
        # root-mean-square prediction error: 11%
        mu_n_output = (20.3 + (0.654 * nitrogen_intake))
        min_n_output = (15.58 + (0.645 * nitrogen_intake))
        max_n_output = (25.02 + (0.663 * nitrogen_intake))
    else:
        # root-mean-square prediction error: 13%
        mu_n_output = (15.1 + (0.83 * nitrogen_intake))
        min_n_output = (12.6 + (0.812 * nitrogen_intake))
        max_n_output = (17.6 + (0.848 * nitrogen_intake))
    return mu_n_output, min_n_output, max_n_output


def manure_nitrogen_output(dry_matter_intake_: float, diet_cp: float, milk_yield: float,
                           milk_cp: float):
    # NRC 8th revised edition (2021)
    manure_n_output = ((dry_matter_intake_ * diet_cp) / 0.625) - ((milk_yield * milk_cp) / 0.638) - 5
    return manure_n_output


if __name__ == '__main__':
    x_values = []
    y_values = []
    dp = 0
    age = 0
    plt.figure()
    milk_cp = 3.4
    for dim in range(700):
        if dim > 700 - 279:
            dp += 1
        diet_cp = None
        intake = None
        weight = bw2(dim)
        milk = milk_production(dim, 0, dp, 279, 60)
        dry_matter_intake = dmi(dim, weight, milk)
        if dp >= 279 - 30 or dim < 365 / 2:
            diet_cp = 0.16
            intake = dry_matter_intake * diet_cp / 0.625
        elif 279 - 60 <= dp < 279 - 30 or dim >= 365 / 2:
            diet_cp = 0.14
            intake = dry_matter_intake * diet_cp / 0.625
        nitrogen = total_manure_nitrogen_output(False, intake)[0]
        x_values.append(age)
        y_values.append(nitrogen)
        age += 1
    dp = 0

    for dim in range(410):
        lactating = True
        if dim > 410 - 280:
            dp += 1
        if dp >= 280 - 60:
            lactating = False
        diet_cp = None
        intake = None
        weight = bw(dim, dp, age, 1)
        milk = milk_production(dim, 1, dp, 280, 60)
        dry_matter_intake = dmi(dim, weight, milk)
        if dp >= 280 - 30 or dim < 100:
            diet_cp = 0.16
            intake = dry_matter_intake * diet_cp / 0.625
        elif 280 - 60 <= dp < 280 - 30:
            diet_cp = 0.14
            intake = dry_matter_intake * diet_cp / 0.625
        elif dim >= 100:
            diet_cp = 0.15
            intake = dry_matter_intake * diet_cp / 0.625
        if lactating:
            nitrogen = manure_nitrogen_output(dry_matter_intake, diet_cp * 100, milk, milk_cp)
        else:
            nitrogen = total_manure_nitrogen_output(lactating, intake)[0]
        x_values.append(age)
        y_values.append(nitrogen)
        age += 1
    dp = 0

    for dim in range(390):
        lactating = True
        if dim > 390 - 282:
            dp += 1
        if dp >= 282 - 60:
            lactating = False
        diet_cp = None
        intake = None
        weight = bw(dim, dp, age, 2)
        milk = milk_production(dim, 2, dp, 282, 60)
        dry_matter_intake = dmi(dim, weight, milk)
        if dp >= 282 - 30 or dim < 100:
            diet_cp = 0.16
            intake = dry_matter_intake * diet_cp / 0.625
        elif 282 - 60 <= dp < 282 - 30:
            diet_cp = 0.14
            intake = dry_matter_intake * diet_cp / 0.625
        elif dim >= 100:
            diet_cp = 0.15
            intake = dry_matter_intake * diet_cp / 0.625
        if lactating:
            nitrogen = manure_nitrogen_output(dry_matter_intake, diet_cp * 100, milk, milk_cp)
        else:
            nitrogen = total_manure_nitrogen_output(lactating, intake)[0]
        x_values.append(age)
        y_values.append(nitrogen)
        age += 1
    dp = 0

    for dim in range(390):
        lactating = True
        if dim > 390 - 282:
            dp += 1
        if dp >= 282 - 60:
            lactating = False
        diet_cp = None
        intake = None
        weight = bw(dim, dp, age, 3)
        milk = milk_production(dim, 3, dp, 282, 60)
        dry_matter_intake = dmi(dim, weight, milk)
        if dp >= 282 - 30 or dim < 100:
            diet_cp = 0.16
            intake = dry_matter_intake * diet_cp / 0.625
        elif 282 - 60 <= dp < 282 - 30:
            diet_cp = 0.14
            intake = dry_matter_intake * diet_cp / 0.625
        elif dim >= 100:
            diet_cp = 0.15
            intake = dry_matter_intake * diet_cp / 0.625
        if lactating:
            nitrogen = manure_nitrogen_output(dry_matter_intake, diet_cp * 100, milk, milk_cp)
        else:
            nitrogen = total_manure_nitrogen_output(lactating, intake)[0]
        x_values.append(age)
        y_values.append(nitrogen)
        age += 1
    dp = 0

    for dim in range(390):
        lactating = True
        if dim > 390 - 282:
            dp += 1
        if dp >= 282 - 60:
            lactating = False
        diet_cp = None
        intake = None
        weight = bw(dim, dp, age, 4)
        milk = milk_production(dim, 4, dp, 282, 60)
        dry_matter_intake = dmi(dim, weight, milk)
        if dp >= 282 - 30 or dim < 100:
            diet_cp = 0.16
            intake = dry_matter_intake * diet_cp / 0.625
        elif 282 - 60 <= dp < 282 - 30:
            diet_cp = 0.14
            intake = dry_matter_intake * diet_cp / 0.625
        elif dim >= 100:
            diet_cp = 0.15
            intake = dry_matter_intake * diet_cp / 0.625
        if lactating:
            nitrogen = manure_nitrogen_output(dry_matter_intake, diet_cp * 100, milk, milk_cp)
        else:
            nitrogen = total_manure_nitrogen_output(lactating, intake)[0]
        x_values.append(age)
        y_values.append(nitrogen)
        age += 1

    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='cow nitrogen')
    plt.xlabel('Age (days)')
    plt.ylabel('N (g)')
    plt.title(f'Nitrogen emission for the first 4 lactations')
    plt.plot([700, 700], [30, 0], label='calving1')
    plt.plot([1110, 1110], [30, 0], label='calving2')
    plt.plot([1500, 1500], [30, 0], label='calving3')
    plt.plot([1890, 1890], [30, 0], label='calving4')
    plt.legend()
    plt.savefig('../img/nitrogen_lactations_0-4_age')
    plt.close()

    # ------------------------------------------------------------------------------------------------------------------
    x_values = []
    y_values = []
    dp = 0
    age = 0
    plt.figure()
    milk_cp = 3.4
    for dim in range(700):
        if dim > 700 - 279:
            dp += 1
        diet_cp = None
        intake = None
        weight = bw2(dim)
        milk = milk_production(dim, 0, dp, 279, 60)
        dry_matter_intake = dmi(dim, weight, milk)
        if dp >= 279 - 30 or dim < 365 / 2:
            diet_cp = 0.16
            intake = dry_matter_intake * diet_cp / 0.625
        elif 279 - 60 <= dp < 279 - 30 or dim >= 365 / 2:
            diet_cp = 0.14
            intake = dry_matter_intake * diet_cp / 0.625
        nitrogen = total_manure_nitrogen_output(False, intake)[0]
        x_values.append(dim)
        y_values.append(nitrogen)
        age += 1
    dp = 0
    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='lactation 0')
    x_values = []
    y_values = []
    for dim in range(410):
        lactating = True
        if dim > 410 - 280:
            dp += 1
        diet_cp = None
        intake = None
        weight = bw(dim, dp, age, 1)
        milk = milk_production(dim, 1, dp, 280, 60)
        dry_matter_intake = dmi(dim, weight, milk)
        if dp >= 280 - 30 or dim < 100:
            diet_cp = 0.16
            intake = dry_matter_intake * diet_cp / 0.625
        elif 280 - 60 <= dp < 280 - 30:
            diet_cp = 0.14
            intake = dry_matter_intake * diet_cp / 0.625
        elif dim >= 100:
            diet_cp = 0.15
            intake = dry_matter_intake * diet_cp / 0.625
        if lactating:
            nitrogen = manure_nitrogen_output(dry_matter_intake, diet_cp * 100, milk, milk_cp)
        else:
            nitrogen = total_manure_nitrogen_output(lactating, intake)[0]
        x_values.append(dim)
        y_values.append(nitrogen)
        age += 1
    dp = 0
    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='lactation 1')
    x_values = []
    y_values = []
    for dim in range(390):
        lactating = True
        if dim > 390 - 282:
            dp += 1
        diet_cp = None
        intake = None
        weight = bw(dim, dp, age, 2)
        milk = milk_production(dim, 2, dp, 282, 60)
        dry_matter_intake = dmi(dim, weight, milk)
        if dp >= 282 - 30 or dim < 100:
            diet_cp = 0.16
            intake = dry_matter_intake * diet_cp / 0.625
        elif 282 - 60 <= dp < 282 - 30:
            diet_cp = 0.14
            intake = dry_matter_intake * diet_cp / 0.625
        elif dim >= 100:
            diet_cp = 0.15
            intake = dry_matter_intake * diet_cp / 0.625
        if lactating:
            nitrogen = manure_nitrogen_output(dry_matter_intake, diet_cp * 100, milk, milk_cp)
        else:
            nitrogen = total_manure_nitrogen_output(lactating, intake)[0]
        x_values.append(dim)
        y_values.append(nitrogen)
        age += 1
    dp = 0
    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='lactation 2')
    x_values = []
    y_values = []
    for dim in range(390):
        lactating = True
        if dim > 390 - 282:
            dp += 1
        diet_cp = None
        intake = None
        weight = bw(dim, dp, age, 3)
        milk = milk_production(dim, 3, dp, 282, 60)
        dry_matter_intake = dmi(dim, weight, milk)
        if dp >= 282 - 30 or dim < 100:
            diet_cp = 0.16
            intake = dry_matter_intake * diet_cp / 0.625
        elif 282 - 60 <= dp < 282 - 30:
            diet_cp = 0.14
            intake = dry_matter_intake * diet_cp / 0.625
        elif dim >= 100:
            diet_cp = 0.15
            intake = dry_matter_intake * diet_cp / 0.625
        if lactating:
            nitrogen = manure_nitrogen_output(dry_matter_intake, diet_cp * 100, milk, milk_cp)
        else:
            nitrogen = total_manure_nitrogen_output(lactating, intake)[0]
        x_values.append(dim)
        y_values.append(nitrogen)
        age += 1
    dp = 0
    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='lactation 3')
    x_values = []
    y_values = []
    for dim in range(390):
        lactating = True
        if dim > 390 - 282:
            dp += 1
        diet_cp = None
        intake = None
        weight = bw(dim, dp, age, 4)
        milk = milk_production(dim, 4, dp, 282, 60)
        dry_matter_intake = dmi(dim, weight, milk)
        if dp >= 282 - 30 or dim < 100:
            diet_cp = 0.16
            intake = dry_matter_intake * diet_cp / 0.625
        elif 282 - 60 <= dp < 282 - 30:
            diet_cp = 0.14
            intake = dry_matter_intake * diet_cp / 0.625
        elif dim >= 100:
            diet_cp = 0.15
            intake = dry_matter_intake * diet_cp / 0.625
        if lactating:
            nitrogen = manure_nitrogen_output(dry_matter_intake, diet_cp * 100, milk, milk_cp)
        else:
            nitrogen = total_manure_nitrogen_output(lactating, intake)[0]
        x_values.append(dim)
        y_values.append(nitrogen)
        age += 1

    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='lactation 4')
    x_values = []
    y_values = []
    plt.xlabel('DIM (days)')
    plt.ylabel('N (g)')
    plt.title(f'Nitrogen emission for the first 4 lactations')
    plt.legend()
    plt.savefig('../img/nitrogen_lactations_0-4_dim')
    plt.close()
