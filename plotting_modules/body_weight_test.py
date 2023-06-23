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


if __name__ == '__main__':
    x_values = []
    y_values = []
    weights = []
    dp = 0
    age = 0
    plt.figure()
    for dim in range(700):
        weight = bw2(dim)
        weights.append(weight)

        x_values.append(age)
        y_values.append(weight)
        age += 1
    dp = 0

    for dim in range(410):
        if dim > 410 - 280:
            dp += 1
        weight = bw(dim, dp, age, 1)
        weights.append(weight)

        x_values.append(age)
        y_values.append(weight)
        age += 1
    dp = 0

    for dim in range(390):
        if dim > 390 - 282:
            dp += 1
        weight = bw(dim, dp, age, 2)
        weights.append(weight)

        x_values.append(age)
        y_values.append(weight)
        age += 1
    dp = 0

    for dim in range(390):
        if dim > 390 - 282:
            dp += 1
        weight = bw(dim, dp, age, 3)
        weights.append(weight)

        x_values.append(age)
        y_values.append(weight)
        age += 1
    dp = 0

    for dim in range(390):
        if dim > 390 - 282:
            dp += 1
        weight = bw(dim, dp, age, 4)
        weights.append(weight)

        x_values.append(age)
        y_values.append(weight)
        age += 1

    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='cow body weight')
    plt.xlabel('Age (days)')
    plt.yticks([50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700])
    plt.ylabel('Weight (kg)')
    plt.title(f'Body weight for the first 4 lactations')
    plt.plot([700, 700], [700, 0], label='calving1')
    plt.plot([1110, 1110], [700, 0], label='calving2')
    plt.plot([1500, 1500], [700, 0], label='calving3')
    plt.plot([1890, 1890], [700, 0], label='calving4')
    plt.legend()
    plt.savefig('img/body_weight_lactations_0-4_age')
    plt.close()

    # ------------------------------------------------------------------------------------------------------------------
    x_values = []
    y_values = []
    age = 700
    dp = 0
    plt.figure()

    for dim in range(500):
        if dim > 80:
            dp += 1
        weight = bw(dim, dp, age, 1)
        x_values.append(dim)
        y_values.append(weight)
        age += 1
    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='ln=1')

    dp = 0
    x_values = []
    y_values = []
    for dim in range(500):
        if dim > 60:
            dp += 1
        weight = bw(dim, dp, age, 2)
        x_values.append(dim)
        y_values.append(weight)
        age += 1
    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='ln=2')

    dp = 0
    x_values = []
    y_values = []
    for dim in range(500):
        if dim > 60:
            dp += 1
        weight = bw(dim, dp, age, 3)
        x_values.append(dim)
        y_values.append(weight)
        age += 1
    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='ln=3')
    plt.plot([410, 410], [700, 500], label='calving 2')
    plt.plot([0, 500], [700, 700])
    plt.plot([0, 500], [680, 680])
    plt.plot([390, 390], [700, 500], label='calving 3 and 4')
    plt.xlabel("Days in milk")
    plt.ylabel("Weight (kg)")
    plt.title("Body weight per lactation")
    plt.yticks([500, 580, 600, 680, 700])
    plt.legend()
    plt.savefig('img/body_weight_lactations_1-3_dim')
    plt.close()
    # ------------------------------------------------------------------------------------------------------------------
    x_values = []
    y_values = []
    age = 700
    dp = 0
    plt.figure()

    for dim in range(500):
        if dim > 80:
            dp += 1
        if dim <= 100:
            weight = bw(dim, dp, age, 1)
            x_values.append(dim)
            y_values.append(weight)
        age += 1
    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='ln=1')

    dp = 0
    x_values = []
    y_values = []
    for dim in range(500):
        if dim > 60:
            dp += 1
        if dim <= 100:
            weight = bw(dim, dp, age, 2)
            x_values.append(dim)
            y_values.append(weight)
        age += 1
    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='ln=2')

    dp = 0
    x_values = []
    y_values = []
    for dim in range(500):
        if dim > 60:
            dp += 1
        if dim <= 100:
            weight = bw(dim, dp, age, 3)
            x_values.append(dim)
            y_values.append(weight)
        age += 1
    xpoints = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xpoints, ypoints, label='ln=3')
    plt.xlabel("Days in milk")
    plt.ylabel("Weight (kg)")
    plt.title("Body weight in first 100 days per lactation")
    plt.legend()
    plt.savefig('img/body_weight_lactations_1-3_100_dim')
    plt.close()
