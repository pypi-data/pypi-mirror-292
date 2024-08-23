#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
import os
import re
from dduk.utility import strutility


#--------------------------------------------------------------------------------
# 전역 상수 목록.
#--------------------------------------------------------------------------------
EMPTY : str = ""
NONE : str = "NONE"
COMMA : str = ","
SLASH : str = "/"
BACKSLASH : str = "\\"
COLON : str = ":"
SPACE : str = " "
DEBUG : str = "DEBUG"
# SYMBOL_NAMING_PATTERN : str = "^[A-Z_][A-Z0-9_]*$"


#--------------------------------------------------------------------------------
# 내부 애플리케이션 데이터 클래스.
#--------------------------------------------------------------------------------
class InternalData:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	__isBuild : bool
	__isDebug : bool
	__executeFileName : str
	__rootPath : str
	__metaPath : str
	__sourcePath : str
	__resourcePath : str
	__workingspacePath : str
	__symbols : set[str]


	#--------------------------------------------------------------------------------
	# 생성됨.
	#--------------------------------------------------------------------------------
	def __init__(self) -> None:
		self.__isBuild = False
		self.__isDebug = False
		self.__executeFileName = str()
		self.__rootPath = str()
		self.__metaPath = str()
		self.__sourcePath = str()
		self.__resourcePath = str()
		self.__workingspacePath = str()
		self.__symbols = set()


 	#--------------------------------------------------------------------------------
	# 빌드 여부 설정.
	#--------------------------------------------------------------------------------
	def SetBuild(self, isBuild : bool) -> None:
		self.__isBuild = isBuild


	#--------------------------------------------------------------------------------
	# 디버그 모드 여부 설정.
	#--------------------------------------------------------------------------------
	def SetDebug(self, isDebug : bool) -> None:
		self.__isDebug = isDebug


 	#--------------------------------------------------------------------------------
	# 실행 된 파일 이름.
	#--------------------------------------------------------------------------------
	def SetExecuteFileName(self, executeFileName : str) -> None:
		self.__executeFileName = executeFileName


	#--------------------------------------------------------------------------------
	# 루트 경로 설정.
	#--------------------------------------------------------------------------------
	def SetRootPath(self, rootPath : str) -> None:
		if not os.path.isdir(rootPath): os.makedirs(rootPath)
		self.__rootPath = rootPath.replace(BACKSLASH, SLASH)


	#--------------------------------------------------------------------------------
	# 메타 파일 경로 설정.
	#--------------------------------------------------------------------------------
	def SetMetaPath(self, metaPath : str) -> None:
		if not os.path.isdir(metaPath): os.makedirs(metaPath)
		self.__metaPath = metaPath.replace(BACKSLASH, SLASH)


	#--------------------------------------------------------------------------------
	# 소스 경로 설정.
	#--------------------------------------------------------------------------------
	def SetSourcePath(self, sourcePath : str) -> None:
		if not os.path.isdir(sourcePath): os.makedirs(sourcePath)
		self.__sourcePath = sourcePath.replace(BACKSLASH, SLASH)


	#--------------------------------------------------------------------------------
	# 리소스 경로 설정.
	#--------------------------------------------------------------------------------
	def SetResourcePath(self, resourcePath : str) -> None:
		if not os.path.isdir(resourcePath): os.makedirs(resourcePath)
		self.__resourcePath = resourcePath.replace(BACKSLASH, SLASH)


	#--------------------------------------------------------------------------------
	# 작업 디렉터리 경로 설정.
	#--------------------------------------------------------------------------------
	def SetWorkingspacePath(self, workingspacePath : str) -> None:
		if not os.path.isdir(workingspacePath): os.makedirs(workingspacePath)
		self.__workingspacePath = workingspacePath.replace(BACKSLASH, SLASH)


	#--------------------------------------------------------------------------------
	# 기존 심볼을 모두 지우고 새로운 심볼 목록 설정.
	#--------------------------------------------------------------------------------
	def SetSymbols(self, symbols : set[str]) -> None:
		self.__symbols = set()
		if symbols:
			# 입력 받은 문자열 정리.
			symbols = [symbol.upper() for symbol in symbols]
			self.__symbols.update(symbols)

		# NONE, EMPTY, SPACE는 없는 것과 마찬가지이므로 목록에서 제거.
		self.__symbols.discard(NONE)
		self.__symbols.discard(EMPTY)
		self.__symbols.discard(SPACE)


	#--------------------------------------------------------------------------------
	# 빌드된 상태인지 여부.
	#--------------------------------------------------------------------------------
	def IsBuild(self) -> bool:
		return self.__isBuild


	#--------------------------------------------------------------------------------
	# 디버깅 상태인지 여부.
	#--------------------------------------------------------------------------------
	def IsDebug(self) -> bool:
		return self.__isDebug


	#--------------------------------------------------------------------------------
	# 실행된 파일 이름 반환.
	#--------------------------------------------------------------------------------
	def GetExecuteFileName(self) -> str:
		return self.__executeFileName


	#--------------------------------------------------------------------------------
	# 애플리케이션이 존재하는 경로 / 실행파일이 존재하는 경로.
	#--------------------------------------------------------------------------------
	def GetRootPath(self) -> str:
		return self.__rootPath


	#--------------------------------------------------------------------------------
	# 메타 경로 / 실행 파일 실행시 임시 메타 데이터 디렉터리 경로.
	#--------------------------------------------------------------------------------
	def GetMetaPath(self) -> str:
		return self.__metaPath
	

	#--------------------------------------------------------------------------------
	# 소스 경로 / 실행 파일 실행시 임시 소스 디렉터리 경로.
	#--------------------------------------------------------------------------------
	def GetSourcePath(self) -> str:
		return self.__sourcePath
	

	#--------------------------------------------------------------------------------
	# 리소스 경로 / 실행 파일 실행시 임시 리소스 디렉터리 경로.
	#--------------------------------------------------------------------------------
	def GetResourcePath(self) -> str:
		return self.__resourcePath


	#--------------------------------------------------------------------------------
	# 작업 디렉터리 경로.
	#--------------------------------------------------------------------------------
	def GetWorkingspacePath(self) -> str:
		return self.__workingspacePath
	

	#--------------------------------------------------------------------------------
	# 심볼 목록 반환.
	#--------------------------------------------------------------------------------
	def GetSymbols(self) -> list[str]:
		return list(self.__symbols)
	

	#--------------------------------------------------------------------------------
	# 심볼을 가지고 있는지 여부 반환.
	#--------------------------------------------------------------------------------
	def HasSymbol(self, symbolString) -> bool:		
		if symbolString not in self.__symbols:
			return False
		return True