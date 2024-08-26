from abc import ABC
from typing import Optional
from dependency_needle.dependency_strategy.\
    dependency_strategy_interface import IDependencyStrategyInterface


class ScopedDependencyStrategy(IDependencyStrategyInterface):
    """Scoped strategy for dependency building."""

    def _custom_post_build_strategy(self, interface: ABC,
                                    concrete_class: object,
                                    key_lookup: object) -> None:
        """Scoped post build strategy"""

        if (key_lookup not
                in self._interface_lifetime_registery_lookup):
            self._interface_lifetime_registery_lookup[key_lookup] = {
                interface: concrete_class
            }
        elif (interface not
              in self._interface_lifetime_registery_lookup[key_lookup]):
            self._interface_lifetime_registery_lookup[key_lookup].update({
                interface: concrete_class
            })

    def _custom_pre_build_strategy(self,
                                   interface: ABC,
                                   key_lookup: object) -> Optional[object]:
        """Scoped pre build strategy"""
        if (key_lookup in self._interface_lifetime_registery_lookup and
            interface in self._interface_lifetime_registery_lookup
                [key_lookup]):
            return (self._interface_lifetime_registery_lookup[key_lookup]
                    [interface])
        return None
