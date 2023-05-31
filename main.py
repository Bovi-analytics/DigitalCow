# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


from cow_builder.digital_cow import DigitalCow, state_probability_generator, \
    create_graph, create_paths, path_probability, path_milk_production, \
    phenotype_simulation, path_nitrogen_emission, find_probabilities
from cow_builder.digital_herd import DigitalHerd
from chain_simulator.simulation import state_vector_processor
from chain_simulator.utilities import validate_matrix_sum, \
    validate_matrix_negative
from chain_simulator.assembly import array_assembler
import time
import logging
import scipy


def chain_simulator_test():
    logging.basicConfig()
    just_another_herd = DigitalHerd()
    just_another_cow = DigitalCow(days_in_milk=650, lactation_number=0,
                                  days_pregnant=275, age=650, herd=just_another_herd,
                                  state='Pregnant')
    # just_another_cow = DigitalCow(days_in_milk=0, lactation_number=0,
    #                               days_pregnant=0, age=0, herd=just_another_herd,
    #                               state='Open')
    start = time.perf_counter()
    just_another_cow.generate_total_states(dim_limit=1000, ln_limit=2)
    end = time.perf_counter()
    print(f"duration for generating states: {end - start} seconds.")

    # start = time.perf_counter()
    # tm = array_assembler(just_another_cow.node_count,
    #                      state_probability_generator(just_another_cow))
    # end = time.perf_counter()
    # print(f"duration making TM: {end - start} seconds.")
    tm = scipy.sparse.load_npz('transition_matrix_small.npz')

    print(
        f"validation of the sum of rows being equal to 1: {validate_matrix_sum(tm)}")
    print(
        f"validation of the probabilities in the matrix being positive: {validate_matrix_negative(tm)}")
    simulated_days = 28
    steps = 1
    simulation = state_vector_processor(just_another_cow.initial_state_vector, tm,
                                        simulated_days, steps)
    start = time.perf_counter()
    graph_filename = 'Graph.graphml.gz'
    path_file = 'paths.txt'
    # create_graph(just_another_cow, graph_filename)
    # create_paths(just_another_cow, simulated_days, graph_filename, path_file)
    all_simulations = find_probabilities(simulation, just_another_cow)

    # start2 = time.perf_counter()
    # path_milk_totals = path_milk_production(just_another_cow, path_file)
    # path_probabilities = path_probability(path_file, all_simulations)
    # path_milk_probabilities, weighted_avg = phenotype_simulation(path_milk_totals,
    #                                                              path_probabilities)
    # end2 = time.perf_counter()
    # print(f"duration of calculating milk production: {end2 - start2} seconds")

    start2 = time.perf_counter()
    path_nitrogen_totals = path_nitrogen_emission(just_another_cow, path_file,
                                                  simulated_days)
    end2 = time.perf_counter()
    print(f"duration of calculating nitrogen emission: {end2 - start2} seconds")
    path_probabilities = path_probability(path_file, all_simulations)
    path_nitrogen_probabilities, weighted_avg = phenotype_simulation(
        path_nitrogen_totals, path_probabilities)

    end = time.perf_counter()
    print(f"The time needed to iterate over the simulation, build paths, "
          f"and calculate phenotype output: {end - start} seconds.")

    # print(f"The weighted average milk production for this simulation is: "
    #       f"{weighted_avg} kg")
    print(f"The weighted average nitrogen emission of manure for this simulation is: "
          f"{weighted_avg} g")

    print("simulation successful.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    chain_simulator_test()
