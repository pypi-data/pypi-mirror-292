#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
from .applicationexecutetype import ApplicationExecuteType


#--------------------------------------------------------------------------------
# 매니페스트 데이터. (준비된 데이터)
#--------------------------------------------------------------------------------
class ManifestData:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	Name : str
	Version : str
	Type : ApplicationExecuteType
	Symbols : list[str] # 실제로는 set이 맞지만 yaml에서 set을 표현할 수 없어 list로 대체.
	Arguments : list[str]


	#--------------------------------------------------------------------------------
	# 생성됨.
	#--------------------------------------------------------------------------------
	def __init__(self) -> None:
		self.Name = str()
		self.Version = "1.0.0"
		self.Type = ApplicationExecuteType.UNKNOWN
		self.Symbols = list()
		self.Arguments = list()