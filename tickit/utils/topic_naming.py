from tickit.core.typedefs import ComponentID


def valid_component_id(component: ComponentID) -> None:
    """A function which checks the validity of a ComponentID for generating a topic name

    Args:
        component (ComponentID): The ComponentID to check

    Raises:
        ValueError: The component name is empty
    """
    if not component:
        raise ValueError


def output_topic(component: ComponentID) -> str:
    """A function which returns the output topic name for a given component

    Args:
        component (ComponentID): The component for which an output topic name is
            required

    Returns:
        str: The output topic name of the component
    """
    valid_component_id(component)
    return "tickit-" + component + "-out"


def input_topic(component: ComponentID) -> str:
    """A function which returns the input topic name for a given component

    Args:
        component (ComponentID): The component for which an input topic name is required

    Returns:
        str: The input topic name of the component
    """
    valid_component_id(component)
    return "tickit-" + component + "-in"
