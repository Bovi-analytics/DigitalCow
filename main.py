# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from cow_builder.digital_cow import DigitalCow, state_probability_generator, \
    vector_milk_production, vector_nitrogen_emission
from cow_builder.digital_herd import DigitalHerd
from chain_simulator.simulation import state_vector_processor
from chain_simulator.utilities import validate_matrix_sum, \
    validate_matrix_negative, simulation_accumulator
from chain_simulator.assembly import array_assembler
from functools import partial
import time
import logging
import scipy


def chain_simulator_test():
    logging.basicConfig()
    just_another_herd = DigitalHerd()

    cow = DigitalCow(
        days_in_milk=0, lactation_number=0, days_pregnant=0,
        age=0, herd=just_another_herd, state='Open')
    cow.generate_total_states(dim_limit=1000, ln_limit=9)

    just_another_cow = DigitalCow(
        days_in_milk=0, lactation_number=1, days_pregnant=0,
        age=660, herd=just_another_herd, state='Open')
    just_another_cow.generate_total_states(dim_limit=1000, ln_limit=9)

    a_cow = DigitalCow(
        days_in_milk=0, lactation_number=2, days_pregnant=0,
        age=1070, herd=just_another_herd, state='Open')
    a_cow.generate_total_states(dim_limit=1000, ln_limit=9)

    a_fourth_cow = DigitalCow(
        days_in_milk=0, lactation_number=3, days_pregnant=0,
        age=1490, herd=just_another_herd, state='Open')
    a_fourth_cow.generate_total_states(dim_limit=1000, ln_limit=9)

    a_fifth_cow = DigitalCow(
        days_in_milk=0, lactation_number=4, days_pregnant=0,
        age=1890, herd=just_another_herd, state='Open')
    a_fifth_cow.generate_total_states(dim_limit=1000, ln_limit=9)

    a_sixth_cow = DigitalCow(
        days_in_milk=0, lactation_number=5, days_pregnant=0,
        age=2290, herd=just_another_herd, state='Open')
    a_sixth_cow.generate_total_states(dim_limit=1000, ln_limit=9)
    # tm = array_assembler(just_another_cow.node_count,
    #                      state_probability_generator(just_another_cow))
    # scipy.sparse.save_npz('transition_matrices/transition_matrix_2_lactations.npz', tm, True)

    tm = scipy.sparse.load_npz('transition_matrices/transition_matrix_9_lactations.npz')

    print(
        f"validation of the sum of rows being equal to 1: {validate_matrix_sum(tm)}")
    print(
        f"validation of the probabilities in the matrix being positive: {validate_matrix_negative(tm)}")
    # print(cow.total_states.index(cow.current_state))
    # print(just_another_cow.total_states.index(just_another_cow.current_state))
    # print(a_cow.total_states.index(a_cow.current_state))
    # print(a_fourth_cow.total_states.index(a_fourth_cow.current_state))
    # print(a_fifth_cow.total_states.index(a_fifth_cow.current_state))
    # print(a_sixth_cow.total_states.index(a_sixth_cow.current_state))
    # print(len(cow.total_states))
    # print('step in time with callback_value:\n')
    simulated_days = 4900
    steps = 14
    simulation1 = state_vector_processor(cow.initial_state_vector, tm,
                                         simulated_days, steps)

    start = time.perf_counter()
    milk_accumulator1 = {}
    nitrogen_accumulator1 = {}
    callbacks1 = {
        "milk": partial(vector_milk_production, digital_cow=cow,
                        intermediate_accumulator=milk_accumulator1),
        "nitrogen": partial(vector_nitrogen_emission, digital_cow=cow,
                            intermediate_accumulator=nitrogen_accumulator1)
    }
    accumulated1 = simulation_accumulator(simulation1, **callbacks1)
    end = time.perf_counter()
    print(f"The time needed to iterate over the simulation "
          f"and calculate phenotype output: {end - start} seconds.")
    print(f"accumulated: {accumulated1}")

    simulation2 = state_vector_processor(just_another_cow.initial_state_vector, tm,
                                         simulated_days, steps)

    start = time.perf_counter()
    milk_accumulator2 = {}
    nitrogen_accumulator2 = {}
    callbacks2 = {
        "milk": partial(vector_milk_production, digital_cow=just_another_cow,
                        intermediate_accumulator=milk_accumulator2),
        "nitrogen": partial(vector_nitrogen_emission, digital_cow=just_another_cow,
                            intermediate_accumulator=nitrogen_accumulator2)
    }
    accumulated2 = simulation_accumulator(simulation2, **callbacks2)
    end = time.perf_counter()
    print(f"The time needed to iterate over the simulation "
          f"and calculate phenotype output: {end - start} seconds.")
    print(f"accumulated: {accumulated2}")

    simulation3 = state_vector_processor(a_cow.initial_state_vector, tm,
                                         simulated_days, steps)

    start = time.perf_counter()
    milk_accumulator3 = {}
    nitrogen_accumulator3 = {}
    callbacks3 = {
        "milk": partial(vector_milk_production, digital_cow=a_cow,
                        intermediate_accumulator=milk_accumulator3),
        "nitrogen": partial(vector_nitrogen_emission, digital_cow=a_cow,
                            intermediate_accumulator=nitrogen_accumulator3)
    }
    accumulated3 = simulation_accumulator(simulation3, **callbacks3)
    end = time.perf_counter()
    print(f"The time needed to iterate over the simulation "
          f"and calculate phenotype output: {end - start} seconds.")
    print(f"accumulated: {accumulated3}")

    simulation4 = state_vector_processor(a_fourth_cow.initial_state_vector, tm,
                                         simulated_days, steps)

    start = time.perf_counter()
    milk_accumulator4 = {}
    nitrogen_accumulator4 = {}
    callbacks4 = {
        "milk": partial(vector_milk_production, digital_cow=a_fourth_cow,
                        intermediate_accumulator=milk_accumulator4),
        "nitrogen": partial(vector_nitrogen_emission, digital_cow=a_fourth_cow,
                            intermediate_accumulator=nitrogen_accumulator4)
    }
    accumulated4 = simulation_accumulator(simulation4, **callbacks4)
    end = time.perf_counter()
    print(f"The time needed to iterate over the simulation "
          f"and calculate phenotype output: {end - start} seconds.")
    print(f"accumulated: {accumulated4}")

    simulation5 = state_vector_processor(a_fifth_cow.initial_state_vector, tm,
                                         simulated_days, steps)

    start = time.perf_counter()
    milk_accumulator5 = {}
    nitrogen_accumulator5 = {}
    callbacks5 = {
        "milk": partial(vector_milk_production, digital_cow=a_fifth_cow,
                        intermediate_accumulator=milk_accumulator5),
        "nitrogen": partial(vector_nitrogen_emission, digital_cow=a_fifth_cow,
                            intermediate_accumulator=nitrogen_accumulator5)
    }
    accumulated5 = simulation_accumulator(simulation5, **callbacks5)
    end = time.perf_counter()
    print(f"The time needed to iterate over the simulation "
          f"and calculate phenotype output: {end - start} seconds.")
    print(f"accumulated: {accumulated5}")

    simulation6 = state_vector_processor(a_sixth_cow.initial_state_vector, tm,
                                         simulated_days, steps)

    start = time.perf_counter()
    milk_accumulator6 = {}
    nitrogen_accumulator6 = {}
    callbacks6 = {
        "milk": partial(vector_milk_production, digital_cow=a_sixth_cow,
                        intermediate_accumulator=milk_accumulator6),
        "nitrogen": partial(vector_nitrogen_emission, digital_cow=a_sixth_cow,
                            intermediate_accumulator=nitrogen_accumulator6)
    }
    accumulated6 = simulation_accumulator(simulation6, **callbacks6)
    end = time.perf_counter()
    print(f"The time needed to iterate over the simulation "
          f"and calculate phenotype output: {end - start} seconds.")
    print(f"accumulated: {accumulated6}")

    # plt.figure()
    # xpoints = np.asarray([key for key in milk_accumulator1.keys()])
    # ypoints = np.asarray([value for value in milk_accumulator1.values()])
    # plt.plot(xpoints, ypoints, label='cow 1')
    #
    # xpoints = np.asarray([key for key in milk_accumulator2.keys()])
    # ypoints = np.asarray([value for value in milk_accumulator2.values()])
    # plt.plot(xpoints, ypoints, label='cow 2')
    #
    # xpoints = np.asarray([key for key in milk_accumulator3.keys()])
    # ypoints = np.asarray([value for value in milk_accumulator3.values()])
    # plt.plot(xpoints, ypoints, label='cow 3')
    #
    # xpoints = np.asarray([key for key in milk_accumulator4.keys()])
    # ypoints = np.asarray([value for value in milk_accumulator4.values()])
    # plt.plot(xpoints, ypoints, label='cow 4')
    #
    # xpoints = np.asarray([key for key in milk_accumulator5.keys()])
    # ypoints = np.asarray([value for value in milk_accumulator5.values()])
    # plt.plot(xpoints, ypoints, label='cow 5')
    #
    # xpoints = np.asarray([key for key in milk_accumulator6.keys()])
    # ypoints = np.asarray([value for value in milk_accumulator6.values()])
    # plt.plot(xpoints, ypoints, label='cow 6')
    # plt.title('Average milk production per day in simulation')
    # plt.ylabel('Milk production (kg)')
    # plt.xlabel('Days in simulation')
    # plt.legend()
    # plt.savefig('img/complete_simulation_2_cows_4900_days_milk_production')
    # plt.close()
    #
    # plt.figure()
    # xpoints = np.asarray([key for key in nitrogen_accumulator1.keys()])
    # ypoints = np.asarray([value for value in nitrogen_accumulator1.values()])
    # plt.plot(xpoints, ypoints, label='cow 1')
    #
    # xpoints = np.asarray([key for key in nitrogen_accumulator2.keys()])
    # ypoints = np.asarray([value for value in nitrogen_accumulator2.values()])
    # plt.plot(xpoints, ypoints, label='cow 2')
    #
    # xpoints = np.asarray([key for key in nitrogen_accumulator3.keys()])
    # ypoints = np.asarray([value for value in nitrogen_accumulator3.values()])
    # plt.plot(xpoints, ypoints, label='cow 3')
    #
    # xpoints = np.asarray([key for key in nitrogen_accumulator4.keys()])
    # ypoints = np.asarray([value for value in nitrogen_accumulator4.values()])
    # plt.plot(xpoints, ypoints, label='cow 4')
    #
    # xpoints = np.asarray([key for key in nitrogen_accumulator5.keys()])
    # ypoints = np.asarray([value for value in nitrogen_accumulator5.values()])
    # plt.plot(xpoints, ypoints, label='cow 5')
    #
    # xpoints = np.asarray([key for key in nitrogen_accumulator6.keys()])
    # ypoints = np.asarray([value for value in nitrogen_accumulator6.values()])
    # plt.plot(xpoints, ypoints, label='cow 6')
    # plt.title('Average nitrogen emission per day in simulation')
    # plt.ylabel('Nitrogen emission (g)')
    # plt.xlabel('Days in simulation')
    # plt.legend()
    # plt.savefig('img/complete_simulation_2_cows_4900_days_nitrogen_emission')
    # plt.close()

    print("simulation successful.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    chain_simulator_test()
