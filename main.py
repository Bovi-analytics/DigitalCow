# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import DairyState
from DigitalCow import DigitalCow
from DigitalHerd import DigitalHerd
from DigitalCowFacade import DigitalCowFacade
import chain_simulator
from chain_simulator.utilities import validate_matrix_sum, validate_matrix_positive
import time
from decimal import Decimal
import logging


def make_herd():
    new_herd = DigitalHerd(360, 2, 30)
    print(new_herd.herd)
    cow1 = DigitalCow()
    cow1.age_at_first_heat = 370
    cow2 = DigitalCow(71, 1, 15)
    new_herd.add_to_herd(cows=[cow1, cow2])
    print(new_herd.herd)
    another_herd = DigitalHerd(360, 1, 32)
    cow3 = DigitalCow(41, 0, 0)
    cow4 = DigitalCow(39, 0, 0)
    cow5 = DigitalCow(200, 3, 74)
    another_herd.add_to_herd(cows=[cow4, cow5])
    cow3.generate_total_states(dim_limit=600)
    print(cow3.total_states)
    print(new_herd.herd)
    print(another_herd.herd)
    facade = DigitalCowFacade(cow3, cow3.total_states)
    # matrix = facade.probability()
    # vector = calculation(matrix)
    # amount_of_milk = cow3.get_milk(vector)


def new_herd_example():
    just_another_herd = DigitalHerd(240, 0, 50)
    a_cow = DigitalCow(15, 2, 0)
    another_cow = DigitalCow(269, 1, 144)
    just_another_herd.herd = [a_cow, another_cow]
    print('test')
    print(a_cow.total_states)
    a_cow.generate_total_states(1)
    print(a_cow.total_states)


def test():
    a_cow = DigitalCow(100, 2, 30, state='Pregnant')
    print(a_cow._total_states)
    a_herd = DigitalHerd()
    a_cow.herd = a_herd
    a_cow.generate_total_states(dim_limit=450, ln_limit=3)
    print(a_cow._total_states)
    facade = DigitalCowFacade(a_cow, a_cow.total_states)
    probability_exit = a_cow.probability_state_change(
        DairyState.State('Open', 100, 2, 0, Decimal("35")),
        DairyState.State('Exit', 101, 2, 0, Decimal("0")))
    print(probability_exit)
    for state in a_cow.total_states:
        new_states = a_cow.possible_new_states(state)
        for new_state in new_states:
            probability = facade.probability(state, new_state)
            print(probability)


def test2():
    new_herd = DigitalHerd()
    cow = DigitalCow(100, 1, 40, 365, state='Pregnant', herd=new_herd)
    # cow = DigitalCow(herd=new_herd)
    # new_herd.add_to_herd([cow])
    start = time.perf_counter()
    cow.generate_total_states(950, 2)
    end = time.perf_counter()
    print(end - start)

    start = time.perf_counter()
    print(cow.node_count)
    end = time.perf_counter()
    print(end - start)

    start = time.perf_counter()
    print(cow.edge_count)
    end = time.perf_counter()
    print(end - start)

    start = time.perf_counter()
    v = cow.initial_state_vector
    end = time.perf_counter()
    print(end - start)


def chain_simulator_test():
    logging.basicConfig()
    just_another_herd = DigitalHerd()
    just_another_cow = DigitalCow()
    just_another_cow.herd = just_another_herd
    start = time.perf_counter()
    just_another_cow.generate_total_states(dim_limit=45, ln_limit=9)
    end = time.perf_counter()
    print(just_another_cow.node_count)
    print(just_another_cow.edge_count)
    print(f"duration for generating states: {end - start}")
    start = time.perf_counter()
    facade = DigitalCowFacade(just_another_cow, just_another_cow.total_states)
    end = time.perf_counter()
    print(f"duration making facade: {end - start}")
    start = time.perf_counter()
    assembler = chain_simulator.ScipyCSRAssembler(facade)
    end = time.perf_counter()
    print(f"duration making assembler: {end - start}")
    start = time.perf_counter()
    tm = assembler.assemble()
    end = time.perf_counter()
    print(f"duration making TM: {end - start}")
    print(validate_matrix_sum(tm))
    print(validate_matrix_positive(tm))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # make_herd()
    # new_herd_example()
    # test()
    # test2()
    chain_simulator_test()
