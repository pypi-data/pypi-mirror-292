#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
from enum import Enum


#--------------------------------------------------------------------------------
# 미리 정의된 심볼 목록.
#--------------------------------------------------------------------------------
class PredefinedSymbols(Enum):
	SYMBOL_SUBPROCESS : str = "SUBPROCESS"
	SYMBOL_LOG : str = "LOG"