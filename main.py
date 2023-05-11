# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import DairyState
from DigitalCow import DigitalCow, state_probability_generator
from DigitalHerd import DigitalHerd
import chain_simulator
from chain_simulator.implementations import array_assembler
from chain_simulator.utilities import validate_matrix_sum, \
    validate_matrix_positive
import time
from decimal import Decimal
import logging


def chain_simulator_test():
    logging.basicConfig()
    just_another_herd = DigitalHerd(insemination_window=[100, 100, 100],
                                    milk_threshold=Decimal("0"))
    # just_another_cow = DigitalCow(days_in_milk=364, lactation_number=0,
    #                               days_pregnant=0, state='Open')
    just_another_cow = DigitalCow(days_in_milk=650, lactation_number=0,
                                  days_pregnant=275, herd=just_another_herd,
                                  state='Pregnant')
    start = time.perf_counter()
    just_another_cow.generate_total_states(dim_limit=1000, ln_limit=2)
    end = time.perf_counter()
    print(f"duration for generating states: {end - start}")
    # start = time.perf_counter()
    # print(just_another_cow.node_count)
    # end = time.perf_counter()
    # print(f"duration node count: {end -start}")
    # start = time.perf_counter()
    # print(just_another_cow.edge_count)
    # end = time.perf_counter()
    # print(f"duration edge count: {end - start}")

    with open('states_3.txt', 'w') as file:
        for state in just_another_cow.total_states:
            file.write(f"{state}\n")
    start = time.perf_counter()
    tm = array_assembler(just_another_cow.node_count,
                            state_probability_generator(just_another_cow))
    end = time.perf_counter()
    print(f"duration making TM: {end - start}")
    print(validate_matrix_sum(tm))
    # print(validate_matrix_positive(tm))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    chain_simulator_test()
