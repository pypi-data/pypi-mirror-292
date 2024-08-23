#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
import yaml
from .applicationexecutetype import ApplicationExecuteType


#--------------------------------------------------------------------------------
# 전역 상수 목록.
#--------------------------------------------------------------------------------


#--------------------------------------------------------------------------------
# 준비된 데이터.
#--------------------------------------------------------------------------------
class PreparedData:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	Name : str
	Type : ApplicationExecuteType
	Symbols : set[str]
	Arguments : list[str]
	StartModuleName : str
	StartFunctionName : str


	#--------------------------------------------------------------------------------
	# 생성됨.
	#--------------------------------------------------------------------------------
	def __init__(self) -> None:
		self.Name = str()
		self.Type = ApplicationExecuteType.UNKNOWN
		self.Symbols = set()
		self.Arguments = list()
		self.StartModuleName = str()
		self.StartFunctionName = str()

	#--------------------------------------------------------------------------------
	# YAML을 역직렬화하여 인스턴스 생성.
	#--------------------------------------------------------------------------------
	@staticmethod
	def YAMLConstructor(loader : yaml.Loader, node : yaml.Node) -> PreparedData:
		mappings : dict = loader.construct_mapping(node, deep = True)
		preparedData = PreparedData()
		preparedData.Name = mappings.get("Name", str())
		preparedData.Type = mappings.get("Type", ApplicationExecuteType.UNKNOWN)
		preparedData.Symbols = mappings.get("Symbols", set())
		preparedData.Arguments = mappings.get("Arguments", list())
		preparedData.StartModuleName = mappings.get("StartModuleName", str())
		preparedData.StartFunctionName = mappings.get("StartFunctionName", str())
		return preparedData