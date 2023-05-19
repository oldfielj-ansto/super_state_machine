"""State machine core."""

from enum import Enum
from functools import partial

import six

from . import utils

NotSet = object()


class DefaultMeta(object):

    """Default configuration values."""

    states_enum_name = "States"


class AttributeDict(dict):
    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        return self[key]


class StateMachineMetaclass(type):

    """Metaclass for state machine, to build all its logic."""

    def __new__(metacls, name, bases, attrs):
        """Create state machine and add all logic and methods to it."""
        metacls._set_up_context()
        new_class = super(metacls, metacls).__new__(metacls, name, bases, attrs)
        metacls.context.new_class = new_class

        parents = [b for b in bases if isinstance(b, metacls)]
        if not parents:
            return metacls.context.new_class

        metacls._set_up_config_getter()
        metacls._check_states_enum()
        metacls._check_if_states_are_strings()
        metacls._set_up_translator()
        metacls._calculate_state_name()
        metacls._check_state_value()
        metacls._add_standard_attributes()
        metacls._generate_standard_transitions()
        metacls._generate_standard_methods()
        metacls._generate_named_checkers()
        metacls._generate_named_transitions()
        metacls._add_new_methods()
        metacls._set_complete_option()
        metacls._complete_meta_for_new_class()

        new_class = metacls.context.new_class
        del metacls.context
        return new_class

    @classmethod
    def _set_up_context(metacls):
        """Create context to keep all needed variables in."""
        metacls.context = AttributeDict()
        metacls.context.new_meta = {}
        metacls.context.new_transitions = {}
        metacls.context.new_methods = {}

    @classmethod
    def _check_states_enum(metacls):
        """Check if states enum exists and is proper one."""
        states_enum_name = metacls.context.get_config("states_enum_name")
        try:
            metacls.context["states_enum"] = getattr(
                metacls.context.new_class, states_enum_name
            )
        except AttributeError:
            raise ValueError("No states enum given!")  # noqa: B904

        proper = True
        try:
            if not issubclass(metacls.context.states_enum, Enum):
                proper = False
        except TypeError:
            proper = False

        if not proper:
            raise ValueError("Please provide enum instance to define available states.")

    @classmethod
    def _check_if_states_are_strings(metacls):
        """Check if all states are strings."""
        for item in list(metacls.context.states_enum):
            if not isinstance(item.value, six.string_types):
                raise ValueError(
                    "Item {name} is not string. Only strings are allowed.".format(
                        name=item.name
                    )
                )

    @classmethod
    def _check_state_value(metacls):
        """Check initial state value - if is proper and translate it.

        Initial state is required.
        """
        state_value = metacls.context.get_config("initial_state", None)
        state_value = state_value or getattr(
            metacls.context.new_class, metacls.context.state_name, None
        )

        if not state_value:
            raise ValueError(
                "Empty state is disallowed, yet no initial state is given!"
            )
        state_value = metacls.context.new_meta["translator"].translate(state_value)
        metacls.context.state_value = state_value

    @classmethod
    def _add_standard_attributes(metacls):
        """Add attributes common to all state machines.

        These are methods for setting and checking state etc.

        """
        setattr(  # noqa: B010
            metacls.context.new_class,
            metacls.context.new_meta["state_attribute_name"],
            metacls.context.state_value,
        )
        setattr(  # noqa: B010
            metacls.context.new_class, metacls.context.state_name, utils.state_property
        )

        setattr(metacls.context.new_class, "is_", utils.is_)  # noqa: B010
        setattr(metacls.context.new_class, "can_be_", utils.can_be_)  # noqa: B010
        setattr(metacls.context.new_class, "set_", utils.set_)  # noqa: B010

    @classmethod
    def _generate_standard_transitions(metacls):
        """Generate methods used for transitions."""
        allowed_transitions = metacls.context.get_config("transitions", {})
        for key, transitions in allowed_transitions.items():
            key = metacls.context.new_meta["translator"].translate(key)

            new_transitions = set()
            for trans in transitions:
                if not isinstance(trans, Enum):
                    trans = metacls.context.new_meta["translator"].translate(trans)
                new_transitions.add(trans)

            metacls.context.new_transitions[key] = new_transitions

        for state in metacls.context.states_enum:
            if state not in metacls.context.new_transitions:
                metacls.context.new_transitions[state] = set()

    @classmethod
    def _generate_standard_methods(metacls):
        """Generate standard setters, getters and checkers."""
        for state in metacls.context.states_enum:
            getter_name = "is_{name}".format(name=state.value)
            metacls.context.new_methods[getter_name] = utils.generate_getter(state)

            setter_name = "set_{name}".format(name=state.value)
            metacls.context.new_methods[setter_name] = utils.generate_setter(state)

            checker_name = "can_be_{name}".format(name=state.value)
            checker = utils.generate_checker(state)
            metacls.context.new_methods[checker_name] = checker

        metacls.context.new_methods["actual_state"] = utils.actual_state
        metacls.context.new_methods["as_enum"] = utils.as_enum
        metacls.context.new_methods["force_set"] = utils.force_set

    @classmethod
    def _generate_named_checkers(metacls):
        named_checkers = metacls.context.get_config("named_checkers", None) or []
        for method, key in named_checkers:
            if method in metacls.context.new_methods:
                raise ValueError(
                    "Name collision for named checker '{checker}' - this "
                    "name is reserved for other auto generated method.".format(
                        checker=method
                    )
                )

            key = metacls.context.new_meta["translator"].translate(key)
            metacls.context.new_methods[method] = utils.generate_checker(key.value)

    @classmethod
    def _generate_named_transitions(metacls):
        named_transitions = metacls.context.get_config("named_transitions", None) or []

        translator = metacls.context.new_meta["translator"]
        for item in named_transitions:
            method, key, from_values = metacls._unpack_named_transition_tuple(item)

            if method in metacls.context.new_methods:
                raise ValueError(
                    "Name collision for transition '{transition}' - this name "
                    "is reserved for other auto generated method.".format(
                        transition=method
                    )
                )

            key = translator.translate(key)
            metacls.context.new_methods[method] = utils.generate_setter(key)

            if from_values:
                from_values = [translator.translate(k) for k in from_values]
                for s in metacls.context.states_enum:
                    if s in from_values:
                        metacls.context.new_transitions[s].add(key)

    @classmethod
    def _unpack_named_transition_tuple(metacls, item):
        try:
            method, key = item
            from_values = metacls.context["states_enum"]
        except ValueError:
            method, key, from_values = item
            if from_values is None:
                from_values = []
            if not isinstance(from_values, list):
                from_values = list((from_values,))

        return method, key, from_values

    @classmethod
    def _add_new_methods(metacls):
        """Add all generated methods to result class."""
        for name, method in metacls.context.new_methods.items():
            if hasattr(metacls.context.new_class, name):
                raise ValueError(f"Name collision in state machine class - {name}.")

            setattr(metacls.context.new_class, name, method)

    @classmethod
    def _set_complete_option(metacls):
        """Check and set complete option."""
        get_config = metacls.context.get_config
        complete = get_config("complete", None)
        if complete is None:
            conditions = [
                get_config("transitions", False),
                get_config("named_transitions", False),
            ]
            complete = not any(conditions)

        metacls.context.new_meta["complete"] = complete

    @classmethod
    def _set_up_config_getter(metacls):
        meta = getattr(metacls.context.new_class, "Meta", DefaultMeta)
        metacls.context.get_config = partial(get_config, meta)

    @classmethod
    def _set_up_translator(metacls):
        translator = utils.EnumValueTranslator(metacls.context["states_enum"])
        metacls.context.new_meta["translator"] = translator

    @classmethod
    def _calculate_state_name(metacls):
        metacls.context.state_name = "state"
        new_state_name = "_" + metacls.context.state_name
        metacls.context.new_meta["state_attribute_name"] = new_state_name

    @classmethod
    def _complete_meta_for_new_class(metacls):
        metacls.context.new_meta["transitions"] = metacls.context.new_transitions
        metacls.context.new_meta["config_getter"] = metacls.context["get_config"]
        setattr(  # noqa: B010
            metacls.context.new_class, "_meta", metacls.context["new_meta"]
        )


class StateMachine(six.with_metaclass(StateMachineMetaclass)):

    """State machine."""


def get_config(original_meta, attribute, default=NotSet):
    for meta in [original_meta, DefaultMeta]:
        try:
            return getattr(meta, attribute)
        except AttributeError:
            pass

    if default is NotSet:
        raise

    return default
