# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from DigitalCow import DigitalCow
from DigitalHerd import DigitalHerd


def make_herd():
    new_herd = DigitalHerd(360, 2, 30)
    print(new_herd.herd)
    cow1 = DigitalCow()
    cow1.age_at_first_heat = 370
    cow2 = DigitalCow(71, 1, 15)
    new_herd.add_to_herd(cows=[cow1, cow2])
    print(new_herd.herd)
    another_herd = DigitalHerd(360, 1, 32)
    DigitalHerd.add_to_herd(another_herd, 3, dim_cows=[82, 15, 157], lns_cows=[2, 3, 1], dp_cows=[31, 0, 120])
    cow3 = another_herd.herd[0]
    cow4 = DigitalCow(39, 0, 0)
    cow5 = DigitalCow(200, 3, 74)
    another_herd.add_to_herd(cows=[cow4, cow5])
    cow3.age(7)
    print(cow3.current_days_in_milk, cow3.current_lactation_number, cow3.current_days_pregnant)
    print(new_herd.herd)
    print(another_herd.herd)


def new_herd_example():
    just_another_herd = DigitalHerd(240, 0, 50)
    a_cow = DigitalCow(15, 2, 0)
    just_another_herd.herd = [a_cow]
    print('test')


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    # See PyCharm help at https://www.jetbrains.com/help/pycharm/


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # print_hi('PyCharm')
    # make_herd()
    new_herd_example()
