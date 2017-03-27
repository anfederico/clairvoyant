.. Clairvoyant documentation master file, created by
   sphinx-quickstart on Sun Mar 26 11:38:09 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Clairvoyant's documentation!
=======================================

Clairvoyant is a machine learning library designed to identify and monitor
social/historical cues for short term stock movement.

Many users will be most interested in :class:`~clairvoyant.Clair`-- the primary
machine learning class. The library provides additional classes that aid in
training, backtesting, and data munging.

The :class:`~clairvoyant.Backtest` class is useful for rapidly testing and
calibrating parameters for maximum signal accuracy. The
:class:`~clairvoyant.Portfolio` class adds trading logic, which helps users
ascertain the impact of various trading decisions in response to model
predictions. Clair needs to understand your data, so we provide a specific class
called :class:`~clairvoyant.History` whose primary purpose is to map whatever
columns you may have defined into common column names that Clair can identify.

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
