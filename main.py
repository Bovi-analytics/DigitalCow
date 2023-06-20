# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np
from _decimal import Decimal

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
    # just_another_cow = DigitalCow(
    #     days_in_milk=650, lactation_number=0, days_pregnant=275,
    #     age=650, herd=just_another_herd, state='Pregnant')
    just_another_cow = DigitalCow(
        days_in_milk=0, lactation_number=1, days_pregnant=0,
        age=660, herd=just_another_herd, state='Open')
    # just_another_cow = DigitalCow(
    #     days_in_milk=0, lactation_number=0, days_pregnant=0,
    #     age=0, herd=just_another_herd, state='Open')
    start = time.perf_counter()
    just_another_cow.generate_total_states(dim_limit=1000, ln_limit=9)
    end = time.perf_counter()
    print(f"duration for generating states: {end - start} seconds.")

    # start = time.perf_counter()
    # tm = array_assembler(just_another_cow.node_count,
    #                      state_probability_generator(just_another_cow))
    # scipy.sparse.save_npz('transition_matrices/transition_matrix_2_lactations.npz', tm, True)
    # end = time.perf_counter()
    # print(f"duration making TM: {end - start} seconds.")

    tm = scipy.sparse.load_npz('transition_matrices/transition_matrix_9_lactations.npz')

    print(
        f"validation of the sum of rows being equal to 1: {validate_matrix_sum(tm)}")
    print(
        f"validation of the probabilities in the matrix being positive: {validate_matrix_negative(tm)}")

    simulated_days = 560
    # simulated_days = 6185
    steps = 1
    simulation = state_vector_processor(just_another_cow.initial_state_vector, tm,
                                        simulated_days, steps)
    start = time.perf_counter()
    milk_accumulator = {}
    nitrogen_accumulator = {}
    callbacks = {
        "milk": partial(vector_milk_production, digital_cow=just_another_cow,
                        intermediate_accumulator=milk_accumulator),
        "nitrogen": partial(vector_nitrogen_emission, digital_cow=just_another_cow,
                            intermediate_accumulator=nitrogen_accumulator)
    }
    accumulated = simulation_accumulator(simulation, **callbacks)
    end = time.perf_counter()
    print(f"The time needed to iterate over the simulation "
          f"and calculate phenotype output: {end - start} seconds.")
    print(f"accumulated: {accumulated}")

    # plt.figure()
    # xpoints = np.asarray([key for key in milk_accumulator.keys()])
    # ypoints = np.asarray([value for value in milk_accumulator.values()])
    # plt.plot(xpoints, ypoints)
    # plt.title('Average milk production per day in simulation.')
    # plt.ylabel('Milk production (kg)')
    # plt.xlabel('Days in simulation')
    # plt.show()
    # plt.close()

    plt.figure()
    xpoints = np.asarray([key for key in nitrogen_accumulator.keys()])
    ypoints = np.asarray([value for value in nitrogen_accumulator.values()])
    plt.plot(xpoints, ypoints)
    plt.title('Average nitrogen emission per day in simulation.')
    plt.ylabel('Nitrogen emission (g)')
    plt.xlabel('Days in simulation')
    plt.show()
    plt.close()

    print("simulation successful.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    chain_simulator_test()
