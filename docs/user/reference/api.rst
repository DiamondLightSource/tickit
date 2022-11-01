API
===

.. automodule:: examples

``examples``
------------

.. automodule:: examples.devices

    ``examples.devices``
    --------------------

    .. automodule:: examples.devices.remote_controlled
        :members:

        ``examples.devices.remote_controlled``
        --------------------------------------

    .. automodule:: examples.devices.shutter
        :members:
        :exclude-members: random

        ``examples.devices.shutter``
        ----------------------------

    .. automodule:: examples.devices.trampoline
        :members:
        :exclude-members: RandomTrampolineDevice
        
        ..
            RandomTrampolineDevice excluded such that Inputs & Outputs TypedDicts may be
            :noindex:ed to prevent namespace collision with Trampoline Inputs & Outputs
            as TypedDict lacks proper __qualname__

        ``examples.devices.trampoline``
        -------------------------------

        .. autoclass:: examples.devices.trampoline.RandomTrampolineDevice
            :members:
            :exclude-members: Inputs, Outputs

            .. autoclass:: examples.devices.trampoline.RandomTrampolineDevice.Inputs
                :noindex:

            .. autoclass:: examples.devices.trampoline.RandomTrampolineDevice.Outputs
                :noindex:

.. automodule:: tickit

``tickit``
----------

.. data:: tickit.__version__
    :type: str

    Version number as calculated by https://github.com/dls-controls/versiongit

.. automodule:: tickit.adapters

    ``tickit.adapters``
    -------------------

    .. automodule:: tickit.adapters.interpreters

        ``tickit.adapters.interpreters``
        --------------------------------

        .. automodule:: tickit.adapters.interpreters.command

            ``tickit.adapters.interpreters.command``
            ----------------------------------------------

            .. automodule:: tickit.adapters.interpreters.command.command_interpreter
                :members:

                ``tickit.adapters.interpreters.command.command_interpreter``
                ------------------------------------------------------------

            .. automodule:: tickit.adapters.interpreters.command.regex_command
                :members:

                ``tickit.adapters.interpreters.command.regex_command``
                ------------------------------------------------------

    .. automodule:: tickit.adapters.servers

        ``tickit.adapters.servers``
        ---------------------------

        .. automodule:: tickit.adapters.servers.tcp
            :members:

            ``tickit.adapters.servers.tcp``
            -------------------------------

    .. automodule:: tickit.adapters.composed
        :members:
        
        ``tickit.adapters.composed``
        ----------------------------
    
    .. automodule:: tickit.adapters.epicsadapter
        :members:

        ``tickit.adapters.epicsadapter``
        --------------------------------

.. automodule:: tickit.core

    ``tickit.core``
    ---------------

    .. automodule:: tickit.core.components

        ``tickit.core.components``
        --------------------------

        .. automodule:: tickit.core.components.component
            :members:

            ``tickit.core.components.component``
            ------------------------------------

        .. automodule:: tickit.core.components.device_simulation
            :members:

            ``tickit.core.components.device_simulation``
            --------------------------------------------

        .. automodule:: tickit.core.components.system_simulation
            :members:

            ``tickit.core.components.system_simulation``
            --------------------------------------------

    .. automodule:: tickit.core.management

        ``tickit.core.management``
        --------------------------

        .. automodule:: tickit.core.management.schedulers

            ``tickit.core.management.schedulers``
            -------------------------------------

            .. automodule:: tickit.core.management.schedulers.base
                :members:

                ``tickit.core.management.schedulers.base``
                ------------------------------------------

            .. automodule:: tickit.core.management.schedulers.master
                :members:

                ``tickit.core.management.schedulers.master``
                --------------------------------------------

            .. automodule:: tickit.core.management.schedulers.slave
                :members:

                ``tickit.core.management.schedulers.slave``
                -------------------------------------------


        .. automodule:: tickit.core.management.event_router
            :members:

            ``tickit.core.management.event_router``
            ---------------------------------------

        .. automodule:: tickit.core.management.ticker
            :members:
            :exclude-members: Ticker

            ``tickit.core.management.ticker``
            ---------------------------------

            .. autoclass:: tickit.core.management.ticker.Ticker
                :members:
                
                .. seealso:: `How component updates are ordered`

    .. automodule:: tickit.core.state_interfaces

        ``tickit.core.state_interfaces``
        --------------------------------

        .. automodule:: tickit.core.state_interfaces.internal
            :members:

            ``tickit.core.state_interfaces.internal``
            -----------------------------------------

        .. automodule:: tickit.core.state_interfaces.kafka
            :members:

            ``tickit.core.state_interfaces.kafka``
            --------------------------------------

        .. automodule:: tickit.core.state_interfaces.state_interface
            :members:

            ``tickit.core.state_interfaces.state_interface``
            ------------------------------------------------

    .. automodule:: tickit.core.device
        :members:

        ``tickit.core.device``
        ----------------------
    
    .. automodule:: tickit.core.adapter
        :members:

        ``tickit.core.adapter``
        -----------------------

    .. automodule:: tickit.core.runner
        :members:

        ``tickit.core.runner``
        ---------------------------------

    .. automodule:: tickit.core.typedefs
        :members:

        ``tickit.core.typedefs``
        ------------------------

.. automodule:: tickit.devices

    ``tickit.devices``
    ------------------

    .. automodule:: tickit.devices.sink
        :members:

        ``tickit.devices.sink``
        ---------------------------

    .. automodule:: tickit.devices.source
        :members:

        ``tickit.devices.source``
        -----------------------------

    .. automodule:: tickit.devices.cryostream

    ``tickit.devices.cryostream``
    -----------------------------

        .. automodule:: tickit.devices.cryostream.base
            :members:
            
            ``tickit.devices.cryostream.base``
            ----------------------------------
        
        .. automodule:: tickit.devices.cryostream.cryostream
            :members:

            ``tickit.devices.cryostream.cryostream``
            ----------------------------------------
        
        .. automodule:: tickit.devices.cryostream.status
            :members:

            ``tickit.devices.cryostream.status``
            ------------------------------------

        .. automodule:: tickit.devices.cryostream.states   
            :members:

            ``tickit.device.cryostream.states``
            -----------------------------------
        
    .. automodule:: tickit.devices.femto

    ``tickit.devices.femto``
    ------------------------

        .. automodule:: tickit.devices.femto.femto
            :members:
        
            ``tickit.devices.femto.femto``
            ------------------------------

    .. automodule:: tickit.devices.pneumatic
    
    ``tickit.devices.pneumatic``
    ----------------------------

        .. automodule:: tickit.devices.pneumatic.pneumatic
            :members:
        
            ``tickit.devices.pneumatic.pneumatic``
            --------------------------------------

.. automodule:: tickit.utils

    ``tickit.utils``
    ----------------

    .. automodule:: tickit.utils.byte_format
        :members:

        ``tickit.utils.byte_format``
        ----------------------------

    .. automodule:: tickit.utils.configuration

        ``tickit.utils.configuration``
        ------------------------------

        .. automodule:: tickit.utils.configuration.configurable
            :members:

            ``tickit.utils.configuration.configurable``
            -------------------------------------------

        .. automodule:: tickit.utils.configuration.loading
            :members:

            ``tickit.utils.configuration.loading``
            --------------------------------------

    .. automodule:: tickit.utils.singleton
        :members:
        :special-members: __call__

        ``tickit.utils.singleton``
        --------------------------

    .. automodule:: tickit.utils.topic_naming
        :members:

        ``tickit.utils.topic_naming``
        -----------------------------