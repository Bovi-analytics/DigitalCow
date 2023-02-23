# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from DigitalCow import DigitalCow
from DigitalHerd import DigitalHerd


def make_herd():
    new_herd = DigitalHerd(360, 2, 30)
    print(new_herd.get_herd())
    cow1 = DigitalCow(new_herd)
    cow2 = DigitalCow(71, 1, 15)
    new_herd.add_to_herd(cows=[cow1, cow2])
    print(new_herd.get_herd())
    another_herd = DigitalHerd(360, 1, 32)
    DigitalHerd.add_to_herd(another_herd, 1, dim_cows=[82], lns_cows=[2], dp_cows=[31])
    cow3 = another_herd.get_herd()[0]
    cow4 = DigitalCow(39, 0, 0)
    cow5 = DigitalCow(200, 3, 74)
    another_herd.add_to_herd(cows=[cow4, cow5])

    print(another_herd.get_herd())


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    # See PyCharm help at https://www.jetbrains.com/help/pycharm/


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # print_hi('PyCharm')
    make_herd()
