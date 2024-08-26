from abc import ABC
from typing import Optional
from dependency_needle.dependency_strategy.\
    dependency_strategy_interface import IDependencyStrategyInterface


class TransientDependencyStrategy(IDependencyStrategyInterface):
    """Transient strategy for dependency building."""

    def _custom_post_build_strategy(self, interface: ABC,
                                    concrete_class: object,
                                    key_lookup: object) -> None:
        """Transient post build strategy"""
        return None

    def _custom_pre_build_strategy(self,
                                   interface: ABC,
                                   key_lookup: object) -> Optional[object]:
        """Transient pre build strategy"""
        return None
