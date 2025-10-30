from typing import TypeAlias
from dataclasses import dataclass


__all__ = [
    'RawVariableName',
    'ConvertedVariableName',
    'RawExpressionStr',
    'ConvertedExpressionStr',
    'VariableName',
    'ExpressionStr'
]


RawExpressionStr: TypeAlias = str
ConvertedExpressionStr: TypeAlias = str
RawVariableName: TypeAlias = RawExpressionStr
ConvertedVariableName: TypeAlias = ConvertedExpressionStr


@dataclass(frozen=True)
class VariableName:
    raw: RawVariableName
    converted: ConvertedVariableName


@dataclass(frozen=True)
class ExpressionStr:
    raw: RawExpressionStr
    converted: ConvertedExpressionStr
