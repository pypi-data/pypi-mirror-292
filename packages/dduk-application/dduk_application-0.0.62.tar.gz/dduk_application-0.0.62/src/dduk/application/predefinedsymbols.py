#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
from enum import Enum


#--------------------------------------------------------------------------------
# 미리 선언된 내장 심볼 목록.
#--------------------------------------------------------------------------------
class PredefinedSymbols(Enum):
	SYMBOL_LOG = "LOG"
	SYMBOL_SERVICE = "SERVICE"
	SYMBOL_SUBPROCESS = "SUBPROCESS"
