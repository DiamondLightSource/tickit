Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.


Unreleased_
-----------

Added:

- HTTP REST Adapter & example device
- Example Counter device
- Basic Eiger device without major logic
- Unit tests covering:

  - EPICS Adapter
  - Cryostream Device & Adapter
  - Femto Device & Adapter
  - Pneumatic Device & Adapter
  - Command Line Interface (CLI)
- Dockerfile specifying a multi-stage build process for a tickit container.

Changed:

- Reworked config (de)serialization

  - User may now reference the :code:`ComponentConfig`, which encapsulate a device and adapters
  - Device & Adapter config classes are no longer automatically generated, configuration should be performed via the :code:`ComponentConfig`

- Made :code:`Device` a typed :code:`Generic` of :code:`InMap` and :code:`OutMap`

Deprecated:

Removed:

Fixed:

- Cryostream flow rate threshold (from 900K > 90K)
- Added dependency on Click to :code:`setup.cfg`
- Added missing :code:`__init__.py` to :code:`tickit.utils.compat`

Security:

0.1_ - 2021-09-23
-----------------

Initial release, with:

- Core functionality
- Built-in Adapters:
  - TCP
  - EPICS
- Example Devices:
  - Remote Controlled (properties set via an adapter)
  - Shutter (I/O interaction and continuous motion)
  - Trampoline & RandomTrampoline (recurring call-backs)
- Real Devices:
  - Cryostream (sample cryo-cooler)
  - Femto (signal amplifier)
  - Pneumatic (pneumatic actuator)

.. _Unreleased: ../../compare/0.2...HEAD
.. _0.2: ../../compare/0.1...0.2
.. _0.1: ../../releases/tag/0.1
