API
===

.. automodule:: tickit
    
``tickit``
----------

This is the internal API reference for tickit

.. data:: tickit.__version__
    :type: str

    Version number as calculated by https://github.com/pypa/setuptools_scm


.. automodule:: tickit.core

    ``tickit.core``
    ---------------
    
    .. automodule:: tickit.core.adapter
        :members:

        ``tickit.core.adapter``
        -----------------------

    .. automodule:: tickit.core.device
        :members:

        ``tickit.core.device``
        ----------------------
    
    .. automodule:: tickit.core.runner
        :members:

        ``tickit.core.runner``
        ----------------------
    
    .. automodule:: tickit.core.typedefs
        :members:

        ``tickit.core.typedefs``
        ------------------------
    

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
                
                .. seealso:: 
                    :doc:`How component updates are ordered<../../developer/explanations/how-component-updates-are-ordered>`
    

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


.. automodule:: tickit.adapters

    ``tickit.adapters``
    -------------------

    .. automodule:: tickit.adapters.interpreters

        ``tickit.adapters.interpreters``
        --------------------------------

        .. automodule:: tickit.adapters.interpreters.command

            ``tickit.adapters.interpreters.command``
            ----------------------------------------

            .. automodule:: tickit.adapters.interpreters.command.command_interpreter
                :members:

                ``tickit.adapters.interpreters.command.command_interpreter``
                ------------------------------------------------------------

            .. automodule:: tickit.adapters.interpreters.command.regex_command
                :members:

                ``tickit.adapters.interpreters.command.regex_command``
                ------------------------------------------------------


        .. automodule:: tickit.adapters.interpreters.endpoints

            ``tickit.adapters.interpreters.endpoints``
            ------------------------------------------

            .. automodule:: tickit.adapters.interpreters.endpoints.http_endpoint
                :members:

                ``tickit.adapters.interpreters.endpoints.http_endpoint``
                --------------------------------------------------------

        
        .. automodule:: tickit.adapters.interpreters.wrappers

            ``tickit.adapters.interpreters.wrappers``
            -----------------------------------------

            .. automodule:: tickit.adapters.interpreters.wrappers.beheading_interpreter
                :members:

                ``tickit.adapters.interpreters.wrappers.beheading_interpreter``
                ---------------------------------------------------------------

            .. automodule:: tickit.adapters.interpreters.wrappers.joining_interpreter
                :members:

                ``tickit.adapters.interpreters.wrappers.joining_interpreter``
                -------------------------------------------------------------
            
            .. automodule:: tickit.adapters.interpreters.wrappers.splitting_interpreter
                :members:

                ``tickit.adapters.interpreters.wrappers.splitting_interpreter``
                ---------------------------------------------------------------


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


    .. automodule:: tickit.adapters.httpadapter
        :members:
        
        ``tickit.adapters.httpadapter``
        -------------------------------


    .. automodule:: tickit.adapters.zmqadapter
        :members:
        
        ``tickit.adapters.zmqadapter``
        ------------------------------


    .. automodule:: tickit.adapters.epicsadapter

        ``tickit.adapters.epicsadapter``
        --------------------------------

        .. automodule:: tickit.adapters.epicsadapter.adapter
            :members:

            ``tickit.adapters.epicsadapter.adapter``
            ----------------------------------------



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
        