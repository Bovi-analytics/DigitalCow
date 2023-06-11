# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from typing import Callable

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
    # scipy.sparse.save_npz('transition_matrix_large.npz', tm, True)
    # end = time.perf_counter()
    # print(f"duration making TM: {end - start} seconds.")

    tm = scipy.sparse.load_npz('transition_matrix_large.npz')

    print(
        f"validation of the sum of rows being equal to 1: {validate_matrix_sum(tm)}")
    print(
        f"validation of the probabilities in the matrix being positive: {validate_matrix_negative(tm)}")

    simulated_days = 5740
    steps = 14
    simulation = state_vector_processor(just_another_cow.initial_state_vector, tm,
                                        simulated_days, steps)
    start = time.perf_counter()
    callbacks = {
        "milk": partial(vector_milk_production, digital_cow=just_another_cow),
        "nitrogen": partial(vector_nitrogen_emission, digital_cow=just_another_cow)
    }
    accumulated = simulation_accumulator(simulation, **callbacks)
    end = time.perf_counter()
    print(f"The time needed to iterate over the simulation "
          f"and calculate phenotype output: {end - start} seconds.")
    print(f"accumulated: {accumulated}")

    # print(f"The weighted average milk production for this simulation is: "
    #       f"{weighted_avg} kg")
    # print(f"The weighted average nitrogen emission of manure for this simulation is: "
    #       f"{weighted_avg} g")

    print("simulation successful.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    chain_simulator_test()
