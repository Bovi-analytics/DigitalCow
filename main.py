# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from DigitalCow import DigitalCow, possible_new_states
from DigitalHerd import DigitalHerd
from DigitalCowFacade import DigitalCowFacade


def make_herd():
    new_herd = DigitalHerd(360, 2, 30)
    print(new_herd.herd)
    cow1 = DigitalCow()
    cow1.age_at_first_heat = 370
    cow2 = DigitalCow(71, 1, 15)
    new_herd.add_to_herd(cows=[cow1, cow2])
    print(new_herd.herd)
    another_herd = DigitalHerd(360, 1, 32)
    DigitalHerd.add_to_herd(another_herd, dim_cows=[82, 15, 157],
                            lns_cows=[2, 3, 1], dp_cows=[31, 0, 120])
    cow3 = another_herd.herd[0]
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
    a_cow = DigitalCow(0, 0, 0)
    print(a_cow._total_states)
    a_cow.generate_total_states(dim_limit=600, ln_limit=6)
    print(a_cow._total_states)
    a_herd = DigitalHerd()
    a_herd.add_to_herd([a_cow])
    facade = DigitalCowFacade(a_cow, a_cow.total_states)
    for state in a_cow.total_states:
        new_states = possible_new_states(state)
        for new_state in new_states:
            probability = facade.probability(state, new_state)
            print(probability)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # make_herd()
    # new_herd_example()
    test()
