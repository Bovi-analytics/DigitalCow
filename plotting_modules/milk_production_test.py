import math
import numpy as np
import matplotlib.pyplot as plt


def milk_production(dim: int, ln: int, dp: int, dp_limit: int, duration_dry: int) -> float:
    # match ln:
    #     case 0:
    #         scale = 0
    #         ramp = 1
    #         offset = 1
    #         decay = 1
    #     case 1:
    #         decay = 0.693 / 358
    #         scale = np.random.normal(34.8, 0)
    #         ramp = np.random.normal(29.6, 0)
    #         offset = np.random.normal(0, 0)
    #         decay = np.random.normal(decay, 0)
    #     case ln if ln > 1:
    #         decay = 0.693 / 240
    #         scale = np.random.normal(47.7, 0)
    #         ramp = np.random.normal(22.1, 0)
    #         offset = np.random.normal(0, 0)
    #         decay = np.random.normal(decay, 0)
    #     case _:
    #         raise ValueError

    match ln:
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
    if ln == 0 or dp >= dp_limit - duration_dry:
        return 0.0
    milk = scale * (1 - (pow(math.e, ((offset - dim) / ramp)) / 2)) * pow(math.e, -decay * dim)
    return milk


if __name__ == '__main__':
    x_values = []
    y_values = []
    age = 0
    dp = 0
    plt.figure()
    for dim in range(700):
        if dim > 700 - 279:
            dp += 1
        milk = milk_production(dim, 0, dp, 279, 60)
        x_values.append(age)
        y_values.append(milk)
        age += 1
    dp = 0
    for dim in range(410):
        if dim > 410 - 280:
            dp += 1
        milk = milk_production(dim, 1, dp, 280, 60)
        x_values.append(age)
        y_values.append(milk)
        age += 1
    dp = 0
    for dim in range(390):
        if dim > 390 - 282:
            dp += 1
        milk = milk_production(dim, 2, dp, 282, 60)
        x_values.append(age)
        y_values.append(milk)
        age += 1
    dp = 0
    for dim in range(390):
        if dim > 390 - 282:
            dp += 1
        milk = milk_production(dim, 3, dp, 282, 60)
        x_values.append(age)
        y_values.append(milk)
        age += 1
    dp = 0
    for dim in range(390):
        if dim > 390 - 282:
            dp += 1
        milk = milk_production(dim, 4, dp, 282, 60)
        x_values.append(age)
        y_values.append(milk)
        age += 1

    xmarkers = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xmarkers, ypoints, label='cow milk production')
    plt.xlabel('Age (days)')
    plt.ylabel('Milk (kg)')
    plt.title(f'Cow Milk Production')
    # plt.plot([700, 700], [50, 0], label='calving1')
    # plt.plot([1110, 1110], [50, 0], label='calving2')
    # plt.plot([1500, 1500], [50, 0], label='calving3')
    # plt.plot([1890, 1890], [50, 0], label='calving4')
    plt.legend()
    plt.savefig('../img/milk_lactations_0-4_age')
    plt.close()

# ----------------------------------------------------------------------------------------------------------------------

    x_values = []
    y_values = []
    age = 0
    dp = 0
    plt.figure()
    # for dim in range(700):
    #     if dim > 700 - 279:
    #         dp += 1
    #     milk = milk_production(dim, 0, dp, 279, 60)
    #     x_values.append(dim)
    #     y_values.append(milk)
    #     age += 1
    # dp = 0
    # xmarkers = np.asarray(x_values)
    # ypoints = np.asarray(y_values)
    # plt.plot(xmarkers, ypoints, label='lactation 0')
    # x_values = []
    # y_values = []

    for dim in range(410):
        if dim > 410 - 280:
            dp += 1
        milk = milk_production(dim, 1, dp, 280, 60)
        x_values.append(dim)
        y_values.append(milk)
        age += 1
    dp = 0
    xmarkers = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xmarkers, ypoints, label='lactation 1')
    x_values = []
    y_values = []

    for dim in range(390):
        if dim > 390 - 282:
            dp += 1
        milk = milk_production(dim, 2, dp, 282, 60)
        x_values.append(dim)
        y_values.append(milk)
        age += 1
    dp = 0
    xmarkers = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xmarkers, ypoints, label='lactation 2')
    x_values = []
    y_values = []

    for dim in range(390):
        if dim > 390 - 282:
            dp += 1
        milk = milk_production(dim, 3, dp, 282, 60)
        x_values.append(dim)
        y_values.append(milk)
        age += 1
    dp = 0
    xmarkers = np.asarray(x_values)
    ypoints = np.asarray(y_values)
    plt.plot(xmarkers, ypoints, label='lactation 3')
    x_values = []
    y_values = []

    # for dim in range(390):
    #     if dim > 390 - 282:
    #         dp += 1
    #     milk = milk_production(dim, 4, dp, 282, 60)
    #     x_values.append(dim)
    #     y_values.append(milk)
    #     age += 1
    # xmarkers = np.asarray(x_values)
    # ypoints = np.asarray(y_values)
    # plt.plot(xmarkers, ypoints, label='lactation 4')
    # x_values = []
    # y_values = []

    plt.xlabel('DIM (days)')
    plt.ylabel('Milk (kg)')
    plt.title(f'Cow lactation curves')
    plt.legend()
    plt.savefig('../img/milk_lactations_1-3_dim')
    plt.close()
