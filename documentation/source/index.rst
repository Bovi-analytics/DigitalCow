.. DigitalCow documentation master file, created by
   sphinx-quickstart on Thu Apr  6 11:45:32 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Cow builder documentation
=========================

This is the documentation of the cow_builder package. Use the indices

======================
How To Use This Module
======================
(See the individual classes, methods, and attributes for details.)\n
*Values in this HowTo are examples, see documentation of each class or function
for details on the default values.*

1. Import the classes DigitalCow and DigitalHerd:
*************************************************
First import the DigitalCow class:

    ``from cow_builder.digital_cow import DigitalCow``

You will also need to import the DigitalHerd class from the digital_herd module:

    ``from cow_builder.digital_herd import DigitalHerd``

************************************************************

2. Create a DigitalCow and DigitalHerd object:
**********************************************
A DigitalCow object can be made without a DigitalHerd object,
however it won't have full functionality until a DigitalHerd is added as its herd.

a) Without a DigitalHerd object:
    1) Without parameters:

        ``cow = DigitalCow()``\n

    2) With parameters:

        ``cow = DigitalCow(days_in_milk=245, lactation_number=3,
        days_pregnant=165, age_at_first_heat=371, age=2079, state='Pregnant')``\n

    *These parameters may not be all available parameters. Look at each class'
    documentation for details.*

b) With a DigitalHerd object:
    1) Without parameters:

        ``a_herd = DigitalHerd()``\n
        ``cow = DigitalCow(herd=a_herd)``\n

    2) With parameters:

        ``a_herd = DigitalHerd(vwp=[365, 90, 70], insemination_window=[110, 100, 90],
        milk_threshold=Decimal("12"), duration_dry=[70, 50])``\n
        ``cow = DigitalCow(days_in_milk=67, lactation_number=1,
        days_pregnant=0, age=767, herd=a_herd, state='Open')``\n

    *These parameters may not be all available parameters. Look at each class'
    documentation for details.*

c) Set the herd of the DigitalCow:
    1) Sets the DigitalHerd as the herd of the DigitalCow:

        ``a_herd = DigitalHerd()``\n
        ``cow = DigitalCow(herd=a_herd)``\n

    2) Overwrites the DigitalHerd as the herd of the DigitalCow:

        ``a_herd = DigitalHerd()``\n
        ``another_herd = DigitalHerd()``\n
        ``cow = DigitalCow(herd=a_herd)``\n
        ``cow.herd = another_herd``\n

    *There are other methods that alter the herd of the cow using functions from the
    DigitalHerd class. These are described in the digital_herd module.*

************************************************************

3. Generate states for the DigitalCow object:
*********************************************
Generate states for the cow with using the ``generate_total_states()`` function:

a) without parameters:

    ``cow.generate_total_state()``

Here the ``days_in_milk_limit`` and ``lactation_number_limit`` variables from the
herd are used.\n

b) with parameters:

    ``cow.generate_total_states(dim_limit=750, ln_limit=9)``

************************************************************

4. Create a transition matrix using the :py:mod:`chain_simulator` package:
**************************************************************************
To create a transition matrix from the states of the DigitalCow object the
:py:mod:`chain_simulator` package must be used.\n
1) Import ``array_assembler`` from the ``chain_simulator`` package:

    ``from chain_simulator.assembly import array_assembler``

2) Import the ``state_probability_generator`` function from this module:

    ``from cow_builder.digital_cow import state_probability_generator``

3) Use ``array_assembler`` to create a transition matrix:

    ``tm = array_assembler(cow.node_count, state_probability_generator(cow))``

*For details on the parameters of functions from the* :py:mod:`chain_simulator`
*package, see the corresponding documentation of the* :py:mod:`chain_simulator`
*package here:* :py:mod:`chain_simulator`
:py:mod:`matplotlib`

************************************************************

5. Perform a simulation using the ``chain_simulator`` package to get the ``simulation`` Iterator:
*************************************************************************************************
1) Import ``state_vector_processor`` from the ``chain_simulator`` package:

    ``from chain_simulator.simulation import state_vector_processor``

2) Use the transition matrix and the cow's initial state vector to simulate the cow over a given number of days:

    ``simulation = state_vector_processor(cow.initial_state_vector, tm, 140, 7)``

*For details on the parameters of functions from the chain_simulator package,
see the corresponding documentation of the chain_simulator package here:*
:py:mod:`chain_simulator`


************************************************************

6. Create the graph, all possible paths, path phenotype totals, and path probabilities for the simulation:
**********************************************************************************************************
1) Import the functions ``create_graph``, ``create_paths``, ``find_probabilities``, ``path_probability``, and ``path_milk_production``:

    ``from cow_builder.digital_cow import create_graph, create_paths, find_probabilities, path_probability, path_milk_production``

2) Create a directed graph using the ``create_graph()`` function:


    ``graph_filename = 'Mygraph.graphml.gz'``\n
    ``create_graph(cow, graph_filename)``\n

3) Create the paths that the cow could take during the simulation using the ``create_paths()`` function:

    ``path_file = 'paths.txt'``\n
    ``create_paths(cow, simulated_days, graph_filename, path_file)``\n

4) Find the path phenotype totals and the path probabilities:

    ``all_simulations = find_probabilities(simulation, cow)``\n
    ``path_milk_totals = path_milk_production(cow, path_file)``\n
    ``path_probabilities = path_probability(path_file, all_simulations)``\n

************************************************************

7. Get phenotypes for the simulation period:
********************************************
1) Import the ``phenotype_simulation`` function:

    ``from cow_builder.digital_cow import phenotype_simulation``

2) Get the weighted phenotypes for all paths and the weighted average using the ``phenotype_simulation()`` function:

    ``weighted_path_milk_totals, weighted_avg = phenotype_simulation(path_milk_totals, path_probabilities)``

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
