===============================
psdaq-control-minimal
===============================

.. image:: https://img.shields.io/pypi/v/psdaq-control-minimal.svg
        :target: https://pypi.python.org/pypi/psdaq-control-minimal

A simple repackaging of the lcls2 daq code at https://github.com/slac-lcls/lcls2 with minimal dependencies needed for controlling the LCLS2 daq from a script, as is done in TMO and RIX's hutch pythons.

This pares down the requirements, unlinks the script entrypoints, and exposes only the ``psdaq.control`` submodule.

Requirements
------------

This works with any version of Python >= 3.6.

It requires only ``pyzmq`` for communicating with the DAQ, and ``ophyd`` and ``bluesky`` for hutch python scanning.

Installation
------------

``conda install psdaq-control-minimal -c pcds-tag``
or
``pip install psdaq-control-minimal``

Maintenance
-----------

- Create a new tag on this repo that matches a tag on https://github.com/slac-lcls/lcls2/releases to trigger a new build.
- To test a build locally, you must first run ``./generate_minimal_package.sh`` to clone and set up the minimal set of files.
  If you've already done this before, you must manually clear the old ``lcls2`` and ``psdaq`` folders.

Directory Structure
-------------------

This repo is based the PCDS python cookiecutter. See the following github page for more info:

- `cookiecutter-pcds-python <https://github.com/pcdshub/cookiecutter-pcds-python>`_
