import matplotlib.pyplot as plt
import numpy as np
from cow_builder.digital_cow import DigitalCow, state_probability_generator, \
    vector_milk_production, vector_nitrogen_emission
from cow_builder.digital_herd import DigitalHerd
from chain_simulator.simulation import state_vector_processor
from chain_simulator.utilities import simulation_accumulator
from chain_simulator.assembly import array_assembler
from functools import partial
import time

just_another_herd = DigitalHerd()
just_another_cow = DigitalCow(
    days_in_milk=0, lactation_number=1, days_pregnant=0,
    age=660, herd=just_another_herd, state='Open')

just_another_cow.generate_total_states(dim_limit=1000, ln_limit=9)

tm = array_assembler(just_another_cow.node_count,
                     state_probability_generator(just_another_cow))

simulated_days = 2800
steps = 14
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
print(
    f"The milk production is: {accumulated['milk']} kg\n"
    f"The nitrogen emission is: {accumulated['nitrogen']} g"
)

plt.figure()
xpoints = np.asarray([key for key in milk_accumulator.keys()])
ypoints = np.asarray([value for value in milk_accumulator.values()])
plt.plot(xpoints, ypoints, label='just another cow')
plt.title('Average milk production per day in simulation')
plt.ylabel('Milk production (kg)')
plt.xlabel('Days in simulation')
plt.legend()
plt.show()
plt.close()
plt.figure()
xpoints = np.asarray([key for key in nitrogen_accumulator.keys()])
ypoints = np.asarray([value for value in nitrogen_accumulator.values()])
plt.plot(xpoints, ypoints, label='just another cow')
plt.title('Average nitrogen emission per day in simulation')
plt.ylabel('Nitrogen emission (g)')
plt.xlabel('Days in simulation')
plt.legend()
plt.show()
plt.close()
