#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
from enum import Enum
import logging
import sys
import traceback
from dduk.utility.logging.logger import Logger
from dduk.utility.logging.logtype import LogType
from dduk.utility.strutility import GetTimestampString
from .internaldata import InternalData
from .internalrepository import InternalRepository
from .predefinedsymbols import PredefinedSymbols


#--------------------------------------------------------------------------------
# 전역 상수 목록.
#--------------------------------------------------------------------------------
EMPTY : str = ""
NONE : str = "NONE"
HYPHEN : str = "-"
COMMA : str = ","
SLASH : str = "/"
BACKSLASH : str = "\\"
COLON : str = ":"
SPACE : str = " "
DEFAULT_LOGGERNAME : str = "dduk-application"


#--------------------------------------------------------------------------------
# 애플리케이션 클래스.
#--------------------------------------------------------------------------------
class Application:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------


	#--------------------------------------------------------------------------------
	# 생성됨.
	#--------------------------------------------------------------------------------
	def __init__(self) -> None:
		pass


	#--------------------------------------------------------------------------------
	# 로그 출력.
	#--------------------------------------------------------------------------------
	@staticmethod
	def Print(message : str, logType : LogType) -> None:
		# 로거 가져오기.
		logger : Logger = InternalRepository.Get(Logger)

		# 일단 콘솔에 출력.
		timestamp = GetTimestampString(HYPHEN, SPACE, COLON, True, COMMA)
		logLevel = logType.value
		logName = LogType.GetInternalName(logType)
		logger.Print(f"[{timestamp}][{logName}]{message}", logLevel)

		# 로그파일 기록시.
		if Application.HasSymbolWithPredefinedSymbol(PredefinedSymbols.SYMBOL_LOG):
			applicationLogger = logging.getLogger()
			if logType == LogType.NONE: # logging.NOTSET:
				return
			elif logType == LogType.DEBUG: # logging.DEBUG:
				applicationLogger.debug(message)
			elif logType == LogType.INFO: # logging.INFO:
				applicationLogger.info(message)
			elif logType == LogType.WARNING: # logging.WARN or logging.WARNING:
				applicationLogger.warning(message)
			elif logType == LogType.ERROR: # logging.ERROR:
				applicationLogger.error(message)
			elif logType == LogType.CRITICAL: # logging.FATAL or logging.CRITICAL:
				applicationLogger.critical(message)


	#--------------------------------------------------------------------------------
	# 빌드된 상태인지 여부.
	#--------------------------------------------------------------------------------
	@staticmethod
	def IsBuild() -> bool:
		internalData = InternalRepository.Get(InternalData)
		return internalData.IsBuild()


	#--------------------------------------------------------------------------------
	# 로그 디버그 출력.
	#--------------------------------------------------------------------------------
	@staticmethod
	def LogDebug(message : str) -> None:
		Application.Print(message, LogType.DEBUG)

	#--------------------------------------------------------------------------------
	# 로그 인포 출력.
	#--------------------------------------------------------------------------------
	@staticmethod
	def Log(message : str) -> None:
		Application.Print(message, LogType.INFO)


	#--------------------------------------------------------------------------------
	# 로그 워닝 출력.
	#--------------------------------------------------------------------------------
	@staticmethod
	def LogWarning(message : str) -> None:
		Application.Print(message, LogType.WARNING)


	#--------------------------------------------------------------------------------
	# 로그 에러 출력.
	#--------------------------------------------------------------------------------
	@staticmethod
	def LogError(message : str) -> None:
		Application.Print(message, LogType.ERROR)


	#--------------------------------------------------------------------------------
	# 로그 익셉션 출력.
	#--------------------------------------------------------------------------------
	@staticmethod
	def LogException(exception : Exception, useTraceback : bool = True, useExit : bool = True) -> None:
		if useTraceback:
			traceback.print_exc()
			tb = exception.__traceback__
			while tb:
				filename = tb.tb_frame.f_code.co_filename
				lineno = tb.tb_lineno
				funcname = tb.tb_frame.f_code.co_name
				result = traceback.format_exc()
				result = result.strip()
				line = result.splitlines()[-1]
				Application.Print(f"Exception in {filename}, line {lineno}, in {funcname}", LogType.EXCEPTION)
				Application.Print(f"\t{line}", LogType.EXCEPTION)
				tb = tb.tb_next
		else:
			Application.Print(exception, LogType.EXCEPTION)

		if useExit:
			sys.exit(1)
	
	#--------------------------------------------------------------------------------
	# 로그 크리티컬 출력.
	#--------------------------------------------------------------------------------
	@staticmethod
	def LogCritical(message : str) -> None:
		Application.Print(message, LogType.CRITICAL)
	

	#--------------------------------------------------------------------------------
	# 디버깅 상태인지 여부.
	#--------------------------------------------------------------------------------
	@staticmethod
	def IsDebug() -> bool:
		internalData = InternalRepository.Get(InternalData)
		return internalData.IsDebug()


	#--------------------------------------------------------------------------------
	# 실행된 파일 이름 반환.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetExecuteFileName() -> str:
		internalData = InternalRepository.Get(InternalData)
		return internalData.GetExecuteFileName()


	#--------------------------------------------------------------------------------
	# 애플리케이션이 존재하는 경로 / 프로젝트가 존재하는 경로.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetRootPath() -> str:
		internalData = InternalRepository.Get(InternalData)
		return internalData.GetRootPath()

	#--------------------------------------------------------------------------------
	# 메타 파일이 존재하는 경로.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetMetaPath() -> str:
		internalData = InternalRepository.Get(InternalData)
		return internalData.GetMetaPath()
	
	#--------------------------------------------------------------------------------
	# 소스 경로 / 실행 파일 실행시 임시 소스 디렉터리 경로.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetSourcePath() -> str:
		internalData = InternalRepository.Get(InternalData)
		return internalData.GetSourcePath()
	

	#--------------------------------------------------------------------------------
	# 리소스 경로 / 실행 파일 실행시 임시 리소스 디렉터리 경로.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetResourcePath() -> str:
		internalData = InternalRepository.Get(InternalData)
		return internalData.GetResourcePath()


	#--------------------------------------------------------------------------------
	# 작업 디렉터리 경로.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetWorkingspacePath() -> str:
		internalData = InternalRepository.Get(InternalData)
		return internalData.GetWorkingspacePath()
	

	#--------------------------------------------------------------------------------
	# 애플리케이션이 존재하는 경로에 상대 경로를 입력하여 절대 경로를 획득.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetRootPathWithRelativePath(relativePath : str) -> str:
		internalData = InternalRepository.Get(InternalData)
		rootPath = internalData.GetRootPath()
		if not relativePath:
			return rootPath
		relativePath = relativePath.replace(BACKSLASH, SLASH)
		absolutePath = f"{rootPath}/{relativePath}"
		return absolutePath


	#--------------------------------------------------------------------------------
	# 메타파일이 존재하는 경로에 상대 경로를 입력하여 절대 경로를 획득.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetMetaPathWithRelativePath(relativePath : str) -> str:
		internalData = InternalRepository.Get(InternalData)
		metaPath = internalData.GetMetaPath()
		if not relativePath:
			return metaPath
		relativePath = relativePath.replace(BACKSLASH, SLASH)
		absolutePath = f"{metaPath}/{relativePath}"
		return absolutePath


	#--------------------------------------------------------------------------------
	# 소스가 존재하는 경로에 상대 경로를 입력하여 절대 경로를 획득.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetSourcePathWithRelativePath(relativePath : str) -> str:
		internalData = InternalRepository.Get(InternalData)
		sourcePath = internalData.GetSourcePath()
		if not relativePath:
			return sourcePath
		relativePath = relativePath.replace(BACKSLASH, SLASH)
		absolutePath = f"{sourcePath}/{relativePath}"
		return absolutePath
	

	#--------------------------------------------------------------------------------
	# 리소스가 존재하는 경로에 상대 경로를 입력하여 절대 경로를 획득.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetResourcePathWithRelativePath(relativePath : str) -> str:
		internalData = InternalRepository.Get(InternalData)
		resourcePath = internalData.GetResourcePath()
		if not relativePath:
			return resourcePath
		relativePath = relativePath.replace(BACKSLASH, SLASH)
		absolutePath = f"{resourcePath}/{relativePath}"
		return absolutePath
	

	#--------------------------------------------------------------------------------
	# 작업 디렉터리 경로에 상대 경로를 입력하여 절대 경로를 획득.
	# - 작업 디렉터리 경로.
	# - 프로젝트 일 때 : src와 동일 계층의 workingspace 디렉터리 이다.
	# - 실행 파일 일 때 : 실행 파일과 동일 디렉터리 이다.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetWorkingspacePathWithRelativePath(relativePath : str) -> str:
		internalData = InternalRepository.Get(InternalData)
		workingspacePath = internalData.GetWorkingspacePath()
		if not relativePath:
			return workingspacePath
		relativePath = relativePath.replace(BACKSLASH, SLASH)
		absolutePath = f"{workingspacePath}/{relativePath}"
		return absolutePath
	

	#--------------------------------------------------------------------------------
	# 심볼 목록 반환.
	#--------------------------------------------------------------------------------
	@staticmethod
	def GetSymbols() -> list[str]:
		internalData = InternalRepository.Get(InternalData)
		return internalData.GetSymbols()
	

	#--------------------------------------------------------------------------------
	# 심볼을 가지고 있는지 여부 반환.
	#--------------------------------------------------------------------------------
	@staticmethod
	def HasSymbol(symbolString) -> bool:
		internalData = InternalRepository.Get(InternalData)
		return internalData.HasSymbol(symbolString)
	

	#--------------------------------------------------------------------------------
	# 심볼을 가지고 있는지 여부 반환.
	# - 인자로 들어가는 열거체의 값은 반드시 문자열이어야 한다.
	#--------------------------------------------------------------------------------
	@staticmethod
	def HasSymbolWithEnum(symbol : Enum) -> bool:
		if isinstance(symbol.value, str):
			internalData = InternalRepository.Get(InternalData)
			return internalData.HasSymbol(symbol.value)
		else:
			Application.LogError(f"{symbol}.value is not str type.")
			return False
	

	#--------------------------------------------------------------------------------
	# 심볼을 가지고 있는지 여부 반환.
	#--------------------------------------------------------------------------------
	@staticmethod
	def HasSymbolWithPredefinedSymbol(symbol : PredefinedSymbols) -> bool:
		return Application.HasSymbolWithEnum(symbol)