from abc import ABC
from functools import wraps
from inspect import signature, iscoroutinefunction

from http.client import HTTPConnection as ClientHTTPConnection
from typing import Any, Callable, Dict, Optional, get_origin
from requests import Request
from starlette.requests import HTTPConnection as StarlletteHTTPConnection

from dependency_needle.constants import ANNOTATIONS, RETURN
from dependency_needle.lifetime_enums import LifeTimeEnums
from dependency_needle.dependency_strategy import (
    IDependencyStrategyInterface,
    ScopedDependencyStrategy,
    TransientDependencyStrategy,
    SingeltonDependencyStrategy
)
from dependency_needle.identifier_facade import IdentifierFacade


class Container:
    """Container used to build a class by automating the dependancy injection
    to obtain inversion of control"""

    request_class_types = [
        Request,
        StarlletteHTTPConnection,
        ClientHTTPConnection
    ]

    def __init__(self):
        self.__interface_registery_lookup = {}
        self.__singleton_lookup = {}
        self.__transient_lookup = {}
        self.__lifetime_meta_lookup = {
            LifeTimeEnums.SINGLETON: self.__singleton_lookup,
            LifeTimeEnums.TRANSIENT: self.__transient_lookup,
            # Un-Used dictionary
            LifeTimeEnums.SCOPED: {}
        }
        self.__lifetime_strategy_lookup = {
            LifeTimeEnums.SINGLETON: SingeltonDependencyStrategy,
            LifeTimeEnums.TRANSIENT: TransientDependencyStrategy,
            # Un-Used dictionary
            LifeTimeEnums.SCOPED: ScopedDependencyStrategy
        }

    def __gaurd_build_unregistered_interface(self, interface: ABC):
        """Throw 'KeyError' exception if interface is not registered."""
        if interface not in self.__interface_registery_lookup:
            raise KeyError(f"Interface: {interface} is not registered.")

    def __assert_implementation(self, interface: ABC, concrete_class) -> None:
        """Assert that the concrete class implements the interface
        being registered.

        :param interface: interface needed to be registered.
        :param concrete_class: concrete class implementing the interface.
        :return: None
        """
        if interface not in concrete_class.__bases__:
            raise TypeError(f"Concrete class: {concrete_class}"
                            f" has to implement interface: {interface}.")

    def __is_abstract_class(self, interface: ABC) -> bool:
        """Check if interface sent is an abstract class.

        :param interface: interface needed to be checked.
        :return: bool.
        """

        bases = interface.__bases__

        return True if ABC in bases else any([
            self.__is_abstract_class(base)
            for base in bases
        ])

    def __assert_abstract_class(self, interface: ABC) -> None:
        """Assert that the interface being registered is an abstract class.

        :param interface: interface needed to be registered.
        :return: None
        """
        is_abstract = self.__is_abstract_class(interface)
        if not is_abstract:
            raise TypeError(f"Interface: {interface}"
                            f" has to be an abstract class.")

    def __assert_proper_enum_used(self, enum: LifeTimeEnums) -> None:
        """Assert that the enum being passed is valid.

        :param enum: enum used to register dependency.
        :return: None
        """
        if enum not in LifeTimeEnums.__members__.values():
            raise KeyError(f"Enum: {enum} does not exist in 'LifeTimeEnums'.")

    def register_interface(self, interface: ABC,
                           concrete_class,
                           life_time: LifeTimeEnums) -> None:
        """Register interface with a corresponding concrete class to use.

        :param interface: interface needed to be registered.
        :param concrete_class: concrete class implementing the interface.
        :param life_time: life time enum specifying the lifetime of the class.
        :return: None
        """
        interface_to_assert = (get_origin(interface)
                               if get_origin(interface)
                               else interface)
        concrete_to_assert = (get_origin(concrete_class)
                              if get_origin(concrete_class)
                              else concrete_class)
        self.__assert_abstract_class(interface_to_assert)
        self.__assert_implementation(interface_to_assert, concrete_to_assert)
        self.__assert_proper_enum_used(life_time)
        strategy: IDependencyStrategyInterface = (
            self.__lifetime_strategy_lookup[life_time]
        )

        lookup = self.__lifetime_meta_lookup[life_time]
        self.__interface_registery_lookup[interface] = strategy(
            lookup, interface, concrete_class)

    def build(self, interface: ABC, key_lookup) -> object:
        """Build an interface by utilizing the registery lookup.

        :param interface: interface needed to be built
        :param key_lookup: key_lookup that might be used to lookup\
        registered interfaces.
        :return object: concrete class that implemenets that interface
        """
        self.__gaurd_build_unregistered_interface(interface)
        interface_to_build: IDependencyStrategyInterface = (
            self.__interface_registery_lookup[interface]
        )
        return interface_to_build.build(
            self.__interface_registery_lookup,
            key_lookup
        )

    def clear(self, key_lookup):
        """Clear created dependencies for specific key

        :param key_lookup: immutable key to delete from\
        transient lookup.
        """
        if key_lookup in self.__transient_lookup:
            del self.__transient_lookup[key_lookup]

    def __get_kwargs_dependencies(self, fn, identifier, *args,
                                  **kwargs) -> Dict[str, Any]:
        """Build and return kwargs dependencies and return it to complete
        dependency injection logic for the decorated method.

        :param fn: Function decorated.
        :param identifier: Identifier used as lifetime lookup.
        :return: kwargs dictionary.
        """
        kwargs = kwargs.copy()

        if hasattr(fn, ANNOTATIONS):
            dependencies: dict = getattr(
                fn,
                ANNOTATIONS
            )

            for key, interface in dependencies.items():
                if (interface in self.__interface_registery_lookup
                        and key != RETURN):
                    kwargs[key] = self.build(
                        interface, identifier
                    )

            return kwargs

    def __gaurd_invalid_identifier(self, id_arg: Optional[int] = None,
                                   id_kwarg: Optional[str] = None) -> None:
        if id_arg and not isinstance(id_arg, int):
            raise TypeError(f"Id: {id_arg} is not an integer.")

        if id_kwarg and not isinstance(id_kwarg, str):
            raise TypeError(f"Id: {id_arg} is not a string.")

        if id_arg and id_kwarg:
            raise ValueError("Cant use both id_arg:"
                             f" {id_arg} and id_kwarg: {id_kwarg}")

    def __get_identifier(self,
                         id_arg: Optional[int] = None,
                         id_kwarg: Optional[str] = None,
                         *args, **kwargs) -> Any:
        """Get identifier for dependency building

        :return: Any
        """
        self.__gaurd_invalid_identifier(id_arg, id_kwarg)

        if id_kwarg:
            return IdentifierFacade.get_identifier_within_kwarg(id_kwarg,
                                                                **kwargs)
        if id_arg:
            return IdentifierFacade.get_identifier_within_args(id_arg, *args)
        return IdentifierFacade.get_identifier_within_args(1, args)

    def build_dependencies_decorator(self,
                                     id_arg: Optional[int] = None,
                                     id_kwarg: Optional[str] = None,
                                     ) -> Callable[[Callable[[Any], Any]],
                                                   Callable[[Any], Any]]:
        """Dependency decorator factory

        identifier used is defaulted to id_arg of position 0

        :param id_arg: Position of the identifier in the args passed.
        :param id_kwarg: Name of the identifier in the kwargs passed.

        :return: dependency building decorator.
        """
        def __build_dependencies_decorator(fn):
            """Wrap a given function to build its dependencies\
            if they are registered.

            :param fn: function with request/identifier as its\
            first parameter or an annotated parameter of type "Request".
            :return: wrapped function.
            """

            if iscoroutinefunction(fn):
                @wraps(fn)
                async def wrapper(*args, **kwargs):
                    identifier = self.__get_identifier(
                        id_arg, id_kwarg, *args, **kwargs)
                    built_kwargs = self.__get_kwargs_dependencies(
                        fn, identifier, *args, **kwargs
                    )
                    result = await fn(*args, **built_kwargs)
                    self.clear(identifier)

                    return result
            else:
                @wraps(fn)
                def wrapper(*args, **kwargs):
                    identifier = self.__get_identifier(
                        id_arg, id_kwarg, *args, **kwargs)
                    built_kwargs = self.__get_kwargs_dependencies(
                        fn, identifier, *args, **kwargs
                    )
                    result = fn(*args, **built_kwargs)
                    self.clear(identifier)

                    return result

            func_signature = signature(wrapper)
            wrapper_signature = func_signature.replace(
                parameters=[
                    parameter for parameter
                    in func_signature.parameters.values()
                    if parameter.annotation
                    not in self.__interface_registery_lookup
                ]
            )
            wrapper.__signature__ = wrapper_signature

            return wrapper

        return __build_dependencies_decorator
