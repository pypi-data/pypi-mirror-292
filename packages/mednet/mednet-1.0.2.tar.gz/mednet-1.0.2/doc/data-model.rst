.. Copyright © 2023 Idiap Research Institute <contact@idiap.ch>
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _mednet.datamodel:

============
 Data model
============

The data model implemented in this package is summarized in the following
figure:

.. image:: img/data-model-lite.png
   :align: center
   :class: only-light

.. image:: img/data-model-dark.png
   :align: center
   :class: only-dark


Each of the elements is described next.


Database
--------

Data that is downloaded from a data provider, and contains samples in their raw
data format. The database may contain both data and metadata, and is supposed
to exist on disk (or any other storage device) in an arbitrary location that is
user-configurable, in the user environment. For example, databases 1 and 2 for
user A may be under ``/home/user-a/databases/database-1`` and
``/home/user-a/databases/database-2``, while for user B, they may sit in
``/groups/medical-data/DatabaseOne`` and ``/groups/medical-data/DatabaseTwo``.


Sample
------

The in-memory representation of the raw database samples. In this package, it
is specified as a two-tuple with a tensor (or a dictionary with multiple
tensors), and metadata (typically label, name, etc.).


RawDataLoader
-------------

A concrete "functor" that allows one to load the raw data and associated
metadata, to create a in-memory Sample representation. RawDataLoaders are
typically Database-specific due to raw data and metadata encoding varying quite
a lot on different databases. RawDataLoaders may also embed various
pre-processing transformations to render data readily usable such as
pre-cropping of black pixel areas, or 16-bit to 8-bit auto-level conversion.


TransformSequence
-----------------

A sequence of callables that allows one to transform torch.Tensor objects into
other torch.Tensor objects, typically to crop, resize, convert Color-spaces,
and the such on raw-data.


DatabaseSplit
-------------

A dictionary that represents an organization of the available raw data in the
database to perform an evaluation protocol (e.g. train, validation, test)
through datasets (or subsets). It is represented as dictionary mapping dataset
names to lists of "raw-data" sample representations, which vary in format
depending on Database metadata availability. RawDataLoaders receive this raw
representations and can convert these to in-memory Sample's.


ConcatDatabaseSplit
-------------------

An extension of a DatabaseSplit, in which the split can be formed by
cannibalising various other DatabaseSplits to construct a new evaluation
protocol. Examples of this are cross-database tests, or the construction of
multi-Database training and validation subsets.


Dataset
-------

An iterable object over in-memory Samples, inherited from the pytorch Dataset
definition. A dataset in our framework may be completely cached in memory or
have in-memory representation of samples loaded on demand. After data loading,
our datasets can optionally apply a TransformSequence, composed of
pre-processing steps defined on a per-model level before optionally caching
in-memory Sample representations. The "raw" representation of a dataset are the
split dictionary values (ie. not the keys).


DataModule
----------

A DataModule aggregates Splits and RawDataLoaders to provide lightning a
known-interface to the complete evaluation protocol (train, validation,
prediction and testing) required for a full experiment to take place. It
automates control over data loading parallelisation and caching inside our
framework, providing final access to readily-usable pytorch DataLoaders.
