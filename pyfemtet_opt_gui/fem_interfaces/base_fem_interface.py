from abc import ABC, abstractmethod
from typing import Any
from pyfemtet_opt_gui.common.return_msg import ReturnType
from pyfemtet_opt_gui.common.type_alias import *
from pyfemtet_opt_gui.common.expression_processor import Expression


class AbstractFEMInterface(ABC):
    @classmethod
    @abstractmethod
    def get_fem(cls, progress=None) -> tuple[Any, ReturnType]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_connection_state(cls) -> ReturnType:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_obj_names(cls) -> tuple[list[str], ReturnType]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_variables(cls) -> tuple[
        dict[VariableName, Expression],
        ReturnType
    ]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def apply_variables(
            cls,
            variables: dict[RawVariableName, float],
    ) -> tuple[ReturnType, str | None]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def normalize_expr_str(
            cls,
            expr_str: RawExpressionStr,
            names: list[RawVariableName],
    ) -> ConvertedExpressionStr:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def normalize_var_name(
            cls,
            name: RawVariableName,
    ) -> ConvertedVariableName:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def unnormalize_var_name(
            cls,
            name: ConvertedVariableName,
    ) -> RawVariableName:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def open_sample(cls, progress=None) -> tuple[ReturnType, str]:
        raise NotImplementedError

    # TODO: refactoring
    @classmethod
    @abstractmethod
    def get_name(cls) -> tuple[Any, ReturnType]:
        raise NotImplementedError

    # TODO: refactoring
    @classmethod
    @abstractmethod
    def save_femprj(cls) -> tuple[bool, tuple[ReturnType, str]]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def open_help(cls, partial_url):
        raise NotImplementedError
