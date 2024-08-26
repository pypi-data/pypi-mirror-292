from abc import ABC, abstractmethod
from typing import Optional

from dependency_needle.constants import ANNOTATIONS, RETURN, INIT


class IDependencyStrategyInterface(ABC):
    """Dependency strategy interface to customize building
    and cleaning implementation."""

    def __init__(self, interface_lifetime_registery_lookup: dict,
                 interface, concrete_class):
        self._interface_lifetime_registery_lookup\
            = interface_lifetime_registery_lookup
        self.__interface = interface
        self.__concrete_class = concrete_class

    def __gaurd_build_unregistered_interface(self, interface: ABC,
                                             registery_lookup: dict):
        """Throw 'KeyError' exception if interface is not registered."""
        if interface not in registery_lookup:
            raise KeyError(f"Interface: {interface} is not registered.")

    @abstractmethod
    def _custom_pre_build_strategy(self, interface: ABC,
                                   key_lookup:
                                   object) -> Optional[object]:
        """Method to override in order to customize pre creation behavior."""
        pass

    @abstractmethod
    def _custom_post_build_strategy(self, interface: ABC,
                                    concrete_class: object,
                                    key_lookup:
                                    object) -> None:
        """Method to override in order to customize post creation behavior."""
        pass

    def __build(self, interface: ABC, interface_registery: dict,
                key_lookup: object) -> object:
        """Actual building method, used recursively.

        :param interface: interface required to be built.
        :param interface_registery: registery containing interface key\
              and DependencyStrategy objects values.
        :param key_lookup: key_lookup that\
            might be used to store in the lookup.
        """
        self.__gaurd_build_unregistered_interface(
            self.__interface, interface_registery)

        concrete_class = self._custom_pre_build_strategy(
            interface, key_lookup)

        if not concrete_class:
            created_dependencies = {}
            class_registered: IDependencyStrategyInterface = (
                interface_registery[interface]
            )
            class_to_build = class_registered.__concrete_class

            if hasattr(getattr(class_to_build, INIT), ANNOTATIONS):
                dependencies: dict = getattr(
                    getattr(class_to_build, INIT), ANNOTATIONS)

                if RETURN in dependencies:
                    dependencies.pop(RETURN)

                for key, value in dependencies.items():
                    dependency_registered: IDependencyStrategyInterface = (
                        interface_registery[value]
                    )
                    created_dependencies[key] = dependency_registered.build(
                        interface_registery, key_lookup)

            concrete_class = class_to_build(**created_dependencies)

        self._custom_post_build_strategy(
            interface, concrete_class, key_lookup)

        return concrete_class

    def build(self, interface_registery: dict, key_lookup: object) -> object:
        """Build an interface by going through the dependency lookup.

        :param interface: interface required to be built.
        :param key_lookup: key_lookup that\
            might be used to store in the lookup.
        """
        return self.__build(self.__interface, interface_registery, key_lookup)
