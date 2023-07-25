.. DigitalCow documentation master file, created by sphinx-quickstart on Thu Apr  6 11:45:32 2023. You can adapt this file completely to your liking, but it should at least contain the root `toctree` directive.

Cow-builder documentation
=========================

This is the documentation of the cow_builder package. Use the indices at the bottom of this page.

Required packages to use this package are :py:mod:`chain_simulator` and :py:mod:`numpy`.
Additionally, :py:mod:`scipy` can be used to save and load created transition matrices.
These packages are automatically installed when installing the ``cow_builder`` package.

Installing the visualisation version will also include :py:mod:`matplotlib`, which can be used to visualise results
from a simulation. How this can be installed is described in the ReadMe of the cow-builder Github repository.

=======================
How To Use This Package
=======================
(See the individual classes, methods, and attributes for details.)

*Values in this HowTo are examples, see documentation of each class or function
for details on the default values.*

1. Import the classes DigitalCow and DigitalHerd:
*************************************************
1) Import the ``DigitalCow`` class from the ``digital_cow`` module and
the ``DigitalHerd`` class from the ``digital_herd`` module::

    from cow_builder.digital_cow import DigitalCow
    from cow_builder.digital_herd import DigitalHerd

************************************************************

2. Create a DigitalCow and DigitalHerd object:
**********************************************
A ``DigitalCow`` object can be made without a ``DigitalHerd`` object,
however it won't have full functionality until a ``DigitalHerd`` is added as its herd.

a) Without a ``DigitalHerd`` object:
    1) Without parameters::

        cow = DigitalCow()

    2) With parameters::

        cow = DigitalCow(days_in_milk=245, lactation_number=3,
        days_pregnant=165, diet_cp_cu=160, diet_cp_fo=140, age=2079, state='Pregnant')

    *These parameters may not be all available parameters. Look at each class'
    documentation for details.*

b) With a ``DigitalHerd`` object:
    1) Without parameters::

        a_herd = DigitalHerd()
        cow = DigitalCow(herd=a_herd)

    2) With parameters::

        a_herd = DigitalHerd(vwp=[365, 90, 70], insemination_window=[110, 100, 90],
        milk_threshold=12, duration_dry=[70, 50])
        cow = DigitalCow(days_in_milk=67, lactation_number=1,
        days_pregnant=0, diet_cp_cu=160, diet_cp_fo=140, age=767, herd=a_herd, state='Open')

    *These parameters may not be all available parameters. Look at each class'
    documentation for details.*

c) Set the herd of the ``DigitalCow``:
    1) Sets the ``DigitalHerd`` as the herd of the ``DigitalCow``::

        a_herd = DigitalHerd()
        cow = DigitalCow(herd=a_herd)

    2) Overwrites the ``DigitalHerd`` as the herd of the ``DigitalCow``::

        a_herd = DigitalHerd()
        another_herd = DigitalHerd()
        cow = DigitalCow(herd=a_herd)
        cow.herd = another_herd

    *There are other methods that alter the herd of the cow using functions from the
    DigitalHerd class. These are described in the digital_herd module.*

************************************************************

3. Generate states for the DigitalCow object:
*********************************************
Generate states for the cow using the ``generate_total_states()`` function:

a) without parameters::

    cow.generate_total_state()

Here the ``days_in_milk_limit`` and ``lactation_number_limit`` variables from
the ``DigitalHerd`` object are used.

b) with parameters::

    cow.generate_total_states(dim_limit=750, ln_limit=9)

************************************************************

4. Create a transition matrix using the ``chain_simulator`` package:
********************************************************************
To create a transition matrix from the states of the ``DigitalCow`` object, the
:py:mod:`chain_simulator` package must be used.

a) Create a new transition matrix:
    1) Import ``array_assembler`` from the ``chain_simulator`` package
    and the ``state_probability_generator`` function from the ``digital_cow`` module::

        from chain_simulator.assembly import array_assembler
        from cow_builder.digital_cow import state_probability_generator

    2) Use ``array_assembler`` to create a transition matrix::

        tm = array_assembler(state_count=cow.node_count, probability_calculator=state_probability_generator(cow))

    3) *Optional:* Save the transition matrix to a file using :py:mod:`scipy`::

        from scipy.sparse import save_npz

        save_npz('transition_matrix.npz', tm, True)

b) Load an existing transition matrix with :py:mod:`scipy`:
    1) Load the transition matrix::

        from scipy.sparse import load_npz

        tm = load_npz('transition_matrix.npz')

*For details on the parameters of functions from the chain_simulator package,
see the corresponding documentation of the chain_simulator package here:*
:py:mod:`chain_simulator`

************************************************************

5. Use the ``chain_simulator`` package to get a simulation iterator:
**************************************************************************
An iterator made with the ``chain_simulator`` package is used to perform the simulation.

*Note:* You are only setting up the simulation in this step.

1) Import ``state_vector_processor`` from the ``chain_simulator`` package::

    from chain_simulator.simulation import state_vector_processor

2) Use the transition matrix and the cow's initial state vector to create an iterator that can simulate the cow over a
given number of days::

    simulation = state_vector_processor(state_vector=cow.initial_state_vector, transition_matrix=tm, steps=2800, interval=1)

*For details on the parameters of functions from the chain_simulator package,
see the corresponding documentation of the chain_simulator package here:*
:py:mod:`chain_simulator`


************************************************************

6. Create a dictionary with phenotypes and the respective phenotype function from the ``digital_cow`` module:
*************************************************************************************************************
A dictionary with phenotype functions is needed for the chain_simulator package to calculate the desired phenotypes.

1) Import the functions ``vector_milk_production`` and ``vector_nitrogen_emission`` from the ``digital_cow`` module
and the ``partial`` function from ``functools``::

    from cow_builder.digital_cow import vector_milk_production, vector_nitrogen_emission
    from functools import partial

2) *Optional:* Create a dictionary to store intermediate results for every phenotype::

    milk_accumulator = {}
    nitrogen_accumulator = {}

3) Fill in the ``digital_cow`` and ``intermediate_accumulator`` parameters using ``partial`` and add the functions to a dictionary::

    callbacks = {
        "milk": partial(vector_milk_production, digital_cow=cow,
                        intermediate_accumulator=milk_accumulator),
        "nitrogen": partial(vector_nitrogen_emission, digital_cow=cow,
                            intermediate_accumulator=nitrogen_accumulator)
    }

*Filling in these parameters here allows the code to refer to these objects and use them without having to give them as parameters to the simulation_accumulator function nor having it return them.*
*If the intermediate_accumulator is skipped in step 2, it does not need to be filled in.*

************************************************************

7. Run the simulation:
**********************
Run the simulation using the ``simulation_accumulator`` function from the ``chain_simulator`` package.

1) Import the ``simulation_accumulator`` function from the ``chain_simulator`` package::

    from chain_simulator.utilities import simulation_accumulator

2) Run the simulation to get a dictionary with the accumulated phenotype values at the end of the simulation::

    accumulated = simulation_accumulator(simulation, **callbacks)

*For details on the parameters of functions from the chain_simulator package,
see the corresponding documentation of the chain_simulator package here:*
:py:mod:`chain_simulator`

************************************************************

8. *Optional:* Print the results and use Matplotlib to plot the simulation:
***************************************************************************
Extract the results from the dictionary or plot the simulation using the intermediate results and :py:mod:`matplotlib`.

1) Print the results from the simulation::

    print(
        f"The milk production is: {accumulated['milk']} kg\n" \
        f"The nitrogen emission is: {accumulated['nitrogen']} g"
    )

2) Plot the simulation using the intermediate results::

    import matplotlib.pyplot as plt
    import numpy as np

    plt.figure()
    x_points = np.asarray([key for key in milk_accumulator.keys()])
    y_points = np.asarray([value for value in milk_accumulator.values()])
    plt.plot(x_points, y_points, label='milk production')
    plt.legend()
    plt.show()
    plt.close()
    plt.figure()
    x_points = np.asarray([key for key in nitrogen_accumulator.keys()])
    y_points = np.asarray([value for value in nitrogen_accumulator.values()])
    plt.plot(x_points, y_points, label='nitrogen emission')
    plt.legend()
    plt.show()
    plt.close()

*Plotting the simulation requires the user to track the intermediate results.*

************************************************************

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
