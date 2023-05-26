# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import numpy as np

from cow_builder.digital_cow import DigitalCow, state_probability_generator, \
    create_paths, path_probability, path_milk_production, phenotype_simulation
from cow_builder.digital_herd import DigitalHerd
from chain_simulator.simulation import state_vector_processor
from chain_simulator.utilities import validate_matrix_sum, \
    validate_matrix_positive
from chain_simulator.assembly import array_assembler
import time
import logging


def chain_simulator_test():
    logging.basicConfig()
    just_another_herd = DigitalHerd()
    just_another_cow = DigitalCow(days_in_milk=650, lactation_number=0,
                                  days_pregnant=275, age=650, herd=just_another_herd,
                                  state='Pregnant')
    start = time.perf_counter()
    just_another_cow.generate_total_states(dim_limit=1000, ln_limit=2)
    end = time.perf_counter()
    print(f"duration for generating states: {end - start} seconds.")
    # start = time.perf_counter()
    # print(just_another_cow.node_count)
    # end = time.perf_counter()
    # print(f"duration node count: {end -start}")
    # start = time.perf_counter()
    # print(just_another_cow.edge_count)
    # end = time.perf_counter()
    # print(f"duration edge count: {end - start}")

    # with open('states_3.txt', 'w') as file:
    #     for state in just_another_cow.total_states:
    #         file.write(f"{state}\n")
    start = time.perf_counter()
    tm = array_assembler(just_another_cow.node_count,
                         state_probability_generator(just_another_cow))
    end = time.perf_counter()
    print(f"duration making TM: {end - start} seconds.")
    print(
        f"validation of the sum of rows being equal to 1: {validate_matrix_sum(tm)}")
    print(
        f"validation of the probabilities in the matrix being positive: {validate_matrix_positive(tm)}")
    simulated_days = 7
    steps = 1
    simulation = state_vector_processor(just_another_cow.initial_state_vector, tm,
                                        simulated_days, steps)
    start = time.perf_counter()
    all_paths, all_simulations = create_paths(simulation, just_another_cow,
                                              simulated_days)

    path_milk_totals = path_milk_production(just_another_cow, all_paths)
    path_probabilities = path_probability(all_paths, all_simulations)
    path_milk_probabilities, weighted_avg = phenotype_simulation(path_milk_totals,
                                                                 path_probabilities)
    end = time.perf_counter()
    print(f"The time needed to iterate over the simulation, build paths, "
          f"and calculate phenotype output: {end - start} seconds.")
    print(f"The weighted average milk production for this simulation is: "
          f"{weighted_avg} kg")
    print("simulation successful.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    chain_simulator_test()
