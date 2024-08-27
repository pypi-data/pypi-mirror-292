#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
from enum import Enum, auto


#--------------------------------------------------------------------------------
# 애플리케이션 실행 방식.
#--------------------------------------------------------------------------------
class ApplicationExecuteType(Enum):
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	UNKNOWN = auto() # 1. 정체불명.
	SOURCE = auto() # 2. 소스.
	BUILD = auto() # 3. 빌드.
	SERVICE = auto() # 4. 서비스.


	#--------------------------------------------------------------------------------
	# 열거체의 요소 값을 요소 이름으로 변경.
	#--------------------------------------------------------------------------------
	@staticmethod
	def ToName(applicationExecuteType : ApplicationExecuteType) -> str:
		return applicationExecuteType.name.upper()


	#--------------------------------------------------------------------------------
	# 요소 이름을 열거체의 요소 값으로 변경.
	#--------------------------------------------------------------------------------
	@staticmethod
	def ToValue(applicationExecuteTypeName : str) -> ApplicationExecuteType:
		try:
			applicationExecuteTypeNameUpper = applicationExecuteTypeName.upper()
			return ApplicationExecuteType[applicationExecuteTypeNameUpper]
		except Exception as exception:
			raise ValueError(applicationExecuteTypeNameUpper)