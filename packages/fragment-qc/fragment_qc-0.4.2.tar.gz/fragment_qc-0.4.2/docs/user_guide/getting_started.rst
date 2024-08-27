===============
Getting Started
===============

Installation
============

If you just want to try Fragme∩t out, use this brief script to install
the latest version from PyPi. Note that xTB is most reliably installed using `conda-forge <https://conda-forge.org>`_.

See the documentation for more details for installing Fragme∩t or for developer instructions see the documentation.

.. code-block:: bash

    # Make sure conda-forge is available
    # this only needs to be run once
    conda config --add channels conda-forge

    # Create a conda env and install depenencies!
    conda create -n fragment "python=3.11" xtb xtb-python 
    conda activate fragment

    # Install the latest version of Fragment
    pip install fragment-qc

    # Test that fragment is installed 
    fragment --help
  
First Steps in Fragmentation
============================

Suppose we have a cluster comprised of 6 water molecules and we'd like to calculate the system energy `ab initio` quantum chemical software. Instead of running the entire cluster at once, we can approximate the cluster energy using fragmentation and the many-body expansion (MBE)

.. math:: 
  :name: eq:mbe

  E_{system} \approx \sum^{m}_{I=1} 
        E_I + \sum^{m}_{I=1}\sum^{m-1}_{J>I} 
            \Delta E_{IJ} + \sum^{m}_{I=1}\sum^{(m-1)}_{J>I}\sum^{(m-2)}_{K>J} \Delta E_{IJK} + \cdots

where :math:`E_I` is the energy of monomer I (in this case a single water molecule) and

.. math::

  \Delta E_{IJ} = E_{IJ} - E_I - E_J

is the two-body interaction energy between monomers I and J and

.. math::

  \Delta E_{IJK} = (E_{IJK}  - E_I - E_J -E_K) - \Delta E_{IJ} - \Delta E_{JK} - \Delta E_{IK}

is the three-body interaction energy, less contributions from the pairwise terms, for monomers I, J, and K. Higher order terms are defined analogously.

In this paper we'll walk through the steps needed to run an MBE calculation up to order 4 (MBE(4)) using the `GFN2-xTB <https://github.com/grimme-lab/xtb>`_ semi-emperical model.

Create a project directory
--------------------------

.. code-block:: bash

  mkdir water6
  cd water6
  fragment init

You should now have an (empty) `fragment.db` database. This is where all drivers, systems, and calculations will be stored.

Get the ``.xyz`` structure file
-------------------------------

This tutorial will explore fragmenting a water 6 cluster. Save the following XYZ file as `water6.xyz`.

.. code-block:: text
  :caption: ``water6.xyz``

  18
  A water 6 cluster in the book configure.
  O   -2.294815470802032    -0.35340370829457846   -1.4570963322795638
  H   -2.881960438102032    0.12296588740542158   -2.049739388579564
  H   -1.4102172378020317    0.0745683714054215   -1.5604491547795636
  O   0.09080023389796821    0.8777598392054216   -1.3863453437795636
  H   0.9061376199979683    0.35842413990542155   -1.5279466229795637
  H   0.12531031699796824    1.1077412038054215   -0.4452916094795637
  O   2.4281271808979685    -0.6521726431945785   -1.3760463098795637
  H   3.2654530112979683    -0.28879311869457847   -1.6763763469795636
  H   2.4976507488979682    -0.6843279777945785   -0.4011477284795637
  O   2.2817380552979682    -0.5383498417945785   1.3854233763204364
  H   1.4467584053979683    -0.05854153339457846   1.550018357920436
  H   2.238419010497968    -1.3234545270945783   1.9375358894204364
  O   -2.4377266432020317    -0.26947301679457847   1.2235689994204364
  H   -2.507481045702032    -0.3329421837945785   0.24094004432043636
  H   -2.6210014391020318    -1.1546355394945784   1.5493709378204361
  O   -0.06454193420203169    0.9356625749054215   1.5322085106204364
  H   -0.17310714100203173    1.6967814865054214   2.1094337979204365
  H   -0.9428015757020318    0.48184552640542144   1.5161249055204364

Now create a strategy file, ``strategy.yaml``, so we can tell Fragment where to find the structure.

.. note::
  
  Fragment uses `YAML <https://learnxinyminutes.com/docs/yaml/>`_ files. These files can be named anything you'd like so use a file structure that makes sense to you!

Past the following block into your yaml file. ``name`` is a label which lets you reference this structure when setting up calculations, ``note`` is an optional note for future reference, and ``source`` is the file path to your structure file.

.. code-block:: yaml
  :caption: ``strategy.yaml``

  systems: # Import our systems
    -
      name: w6
      note: water 6 # A note with more information (optional)
      source: water6.xyz # Path to the .xyz file you just made 

Now run ``fragment strategy strategy.yaml`` which will read in any *new* data from ``strategy.yaml``. You should now see the system when you run ``fragment system list`` and you can get more information about the system by running ``fragment system info w6``.

Creating a driver and running a calculation
-------------------------------------------

To use an external quantum chemical (QC) software, you need to define a driver. You already installed xTB with fragment, so we are going to use that. Add the following block to your ``strategy.yaml`` file. It has the same ``name`` and optional ``note`` parameters as the system section. This has a ``type`` parameter which tells Fragme∩t which driver we are using and an ``options`` section which allows us to driver-specific configuration options. This structure consistent for defining all drivers, fragments, and modifiers.

.. code-block:: yaml
  :caption: ``strategy.yaml`` continued...

  # systems...

  drivers:
    - # A driver to run GFN2-xTB calculations
      name: GFN2-xTB
      type: LibxTB
      options:
        method: gfn2 # Use the GFN2 method (this is the default)
        calc_charges: True # Calculate partial charges

Now let's set up a calculation for the supersystem (no fragmentation). Add the following section to your ``strategy.yaml`` file. It has the ``name`` and ``note`` fields. The ``systems`` field is a list of all systems (using the ``name`` field from the systems section) you wish to run this calculation on. ``steps`` is a list of actions you wish to take on the system. For now, we are just handing the full system to the ``GFN2-xTB`` driver.

.. note::

  If you don't specify a ``name`` one will be generated automatically using the system name and the steps

.. code-block:: yaml
  :caption: ``strategy.yaml`` continued...

  # systems...
  # drivers...
  calculations:
    -
      name: supersystem
      note: Perform the supersystem calculation
      systems: [w6] 
      steps:
        - GFN2-xTB # Pass the system directly to xTB


Re-run ``fragment strategy add strategy.yaml``. Notice that the water 6 system isn't added again. You can run ``fragment strategy list`` to see drivers and other logic-related ``fragment.db`` entries. Running ``fragment calc list`` gives you information about calculations.

Finally, run ``fragment calc run w6--supersystem`` and wait. It will print out the results! Running ``fragment calc info w6--supersystem`` will let you view these results later.

Creating a primary fragmenter
-----------------------------

Fragme∩t has the water 6 cluster saved to ``fragment.db`` but we haven't separated it into individual water molecules. This can be done using a primary fragmenter. In this case we will use the CovalentComponentsFragmenter which splits a supersystem into non-covalently bonded subsystems using experimental bond radii. We'll use the primary fragmenter when we set up a calculation in a later section.


.. code-block:: yaml
  :caption: ``strategy.yaml`` continued...

  fragmenters:
    - 
      name: cov-comp 
      type: CovalentComponentsFragmenter


Creating an auxiliary fragmenter
--------------------------------

We now have the monomers but we are interested in the interactions `between` monomers using :ref:`the MBE <eq:mbe>`. This can be done using an auxialiary fragmenter which creates combinations of the monomers. Here we will be doing the full MBE(4).

.. code-block:: yaml
  :caption: ``strategy.yaml`` continued...

  fragmenters:
    # cov-comp...
    - 
      name: mbe 
      type: FullFragmenter


Create a MBE(4) calculation
---------------------------

Calculations have multiple steps with the result of each step being handed to the subsiquent step. Here we set up a calculation with the steps:

1. Start with water 6 supersystem pass it to the ``cov-comp`` fragmenter to separate the water monomers

2. Take the water monomers (primary fragments) and pass them to the auxiliary fragmenter (``mbe``) to create all possible 2-, 3-, and 4- monomer combinations

3. Pass the auxiliary fragments to ``GFN2-xTB`` to calculate the energy and sum up those calculations

Put the following block into the ``calculations`` section of ``strategy.yaml``. The steps section references to multiple drivers and fragmenters. Note that stages can accept arguments (`e.g.` ``mbe(4)`` to do the MBE up to order 4)

.. code-block:: yaml
  :caption: ``strategy.yaml`` continued...

  # systems...
  # fragmenters...

  calculations:
    # supersystem calc...
    -
      name: mbe4
      note: Full MBE(4)
      systems: [w6] 
      steps:
        - cov-comp
        - mbe(4)
        - GFN2-xTB


Run the calculations
--------------------

Once more run ``fragment strategy add strategy.yaml`` and then run ``fragment calc run w6--mbe4``.

For reference you should have gotten ~-30.491989 Eh for the supersystem-based energy and ~-30.491931 Eh for the MBE(4)-based energy. Try playing around with different MBE orders.


Appendix: Complete ``strategy.yaml``
====================================

.. code-block:: yaml
  :caption: ``strategy.yaml``

  systems: # Import our systems
    -
      name: w6
      note: water 6 # A note with more information (optional)
      source: water6.xyz # Path to the .xyz file you just made 

  fragmenters:
    - # Splits system into non-covalently bonded components
      name: cov-comp 
      type: CovalentComponentsFragmenter
    - # Creates combinations of monomers
      name: mbe 
      type: FullFragmenter
  
  drivers:
    - # A driver to run GFN2-xTB calculations
      name: GFN2-xTB
      type: LibxTB
      options:
        method: gfn2 # Use the GFN2 method (this is the default)
        calc_charges: True # Calculate partial charges
  
  calculations:
    -
      name: supersystem
      note: Perform the supersystem calculation
      systems: [w6] # You can also put [ALL] to run this calculation for
                    #  every named system in fragment.db
      steps:
        - GFN2-xTB # Pass the system directly to xTB
    -
      name: mbe(4) 
      note: Full MBE(4)
      systems: [w6] 
      steps:
        - cov-comp
        - mbe(4)
        - GFN2-xTB