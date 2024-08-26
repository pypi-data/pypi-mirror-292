"""Pybind11 Bindings for SCINE ReaDuct"""
import scine_readuct
import typing
from typing import Union
import scine_utilities
import scine_utilities.core

__all__ = [
    "load_yaml",
    "run_afir_task",
    "run_bond_order_task",
    "run_bspline_task",
    "run_freq_task",
    "run_hessian_task",
    "run_integral_task",
    "run_irc_task",
    "run_nt2_task",
    "run_nt_task",
    "run_opt_task",
    "run_optimization_task",
    "run_single_point_task",
    "run_sp_task",
    "run_transition_state_optimization_task",
    "run_tsopt_task"
]


def load_yaml(arg0: str) -> typing.Tuple[typing.Dict[str, typing.Tuple[str, str, scine_utilities.core.Calculator]], typing.List[typing.Tuple[str, typing.List[str], typing.List[str]]], typing.List[scine_utilities.ValueCollection]]:
    """
    Load the system map, the task, input, and output names and the task settings from a ReaDuct yaml input file
    """
def run_afir_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_bond_order_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_bspline_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_freq_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_hessian_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_integral_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_irc_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_nt2_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_nt_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_opt_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_optimization_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_single_point_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_sp_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_transition_state_optimization_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
def run_tsopt_task(systems: dict, names_of_used_systems: typing.List[str], test_run_only: bool = False, observers: typing.List[typing.Callable[[int, scine_utilities.AtomCollection, scine_utilities.Results, str], None]] = [], **kwargs) -> typing.Tuple[typing.Dict[str, scine_utilities.core.Calculator], bool]:
    pass
