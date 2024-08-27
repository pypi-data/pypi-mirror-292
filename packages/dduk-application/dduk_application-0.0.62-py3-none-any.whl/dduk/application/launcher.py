#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
import importlib
import os
# import signal
import sys
from types import ModuleType
import debugpy
from dduk.core.project import Project
from dduk.utility.logging.logger import Logger
from dduk.utility.logging.logtype import LogType
from .application import Application
from .applicationexecutetype import ApplicationExecuteType
from .internaldata import InternalData
from .internalrepository import InternalRepository
from .manifestdata import ManifestData
from .predefinedsymbols import PredefinedSymbols
from .preparer import MANIFESTFILENAME
from .yamlwrapper import YAMLWrapper


#--------------------------------------------------------------------------------
# 전역 상수 목록.
#--------------------------------------------------------------------------------
EMPTY : str = ""
FROZEN : str = "frozen"
BACKSLASH : str = "\\"
SLASH : str = "/"
UTF8 : str = "utf-8"
READ : str = "r"
WRITE : str = "w"


#--------------------------------------------------------------------------------
# 실행자 클래스.
#--------------------------------------------------------------------------------
class Launcher:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------


	#--------------------------------------------------------------------------------
	# 생성됨.
	#--------------------------------------------------------------------------------
	def __init__(self) -> None:
		pass


	#--------------------------------------------------------------------------------
	# 실행.
	#--------------------------------------------------------------------------------
	def Launch(self) -> int:
		#--------------------------------------------------------------------------------
		# 런치 표시.
		builtins.print("__LAUNCH__")
		
		#--------------------------------------------------------------------------------
		# 애플리케이션 클래스 생성.
		application = InternalRepository.Get(Application)

		#--------------------------------------------------------------------------------
		# 내부 데이터 클래스 생성.
		internalData = InternalRepository.Get(InternalData)

		#--------------------------------------------------------------------------------
		# 빌드 설정.
		isBuild : bool = Launcher.VerifyBuild()
		internalData.SetBuild(isBuild)
		if internalData.IsBuild():
			# 실행파일에서 생성되는 임시 루트 경로.
			# 캐시패스는 리소스를 위한 캐시 디렉터리로 실제 실행 파일의 위치가 아님. 
			# 또한 윈도우에서는 8.3형식에 의해 마음대로 캐시폴더의 경로를 짧은 형태로 수정할 수 있어서 캐시 디렉터리 이름만 가져와 덧붙이는 식으로 방어처리.
			profilePath = os.path.expanduser("~")
			cacheName : str = os.path.basename(sys._MEIPASS)
			cachePath : str = os.path.join(profilePath, "AppData", "Local", "Temp", cacheName).replace(BACKSLASH, SLASH)
			rootPath : str = os.path.dirname(sys.executable).replace(BACKSLASH, SLASH)
			sourcePath : str = os.path.join(cachePath, "src").replace(BACKSLASH, SLASH)
			resourcePath : str = os.path.join(cachePath, "res").replace(BACKSLASH, SLASH)
			workingspacePath : str = rootPath.replace(BACKSLASH, SLASH)
			metaPath : str = os.path.join(cachePath, "meta").replace(BACKSLASH, SLASH)
		else:
			# 현재 __main__ 으로 실행되는 코드 대상을 기준으로 한 경로.
			# 따라서 반드시 메인 스크립트는 src 안에 있어야 한다.
			currentFilePath = os.path.abspath(sys.modules["__main__"].__file__).replace(BACKSLASH, SLASH)
			sourcePath : str = os.path.dirname(currentFilePath).replace(BACKSLASH, SLASH)
			rootPath : str = os.path.dirname(sourcePath).replace(BACKSLASH, SLASH)
			resourcePath : str = os.path.join(rootPath, "res").replace(BACKSLASH, SLASH)
			workingspacePath : str = os.path.join(rootPath, "workingspace").replace(BACKSLASH, SLASH)

			# 빌드가 아닌 상태에서의 추가 경로 설정.
			rootName = os.path.basename(rootPath)
			temporaryPath = Project.FindTemporaryPath()
			cachePath : str = os.path.join(temporaryPath, "dduk-python", "dduk-application", "projects", rootName).replace(BACKSLASH, SLASH)
			metaPath : str = os.path.join(cachePath, "meta").replace(BACKSLASH, SLASH)
		
		#--------------------------------------------------------------------------------
		# 실행을 위한 준비 데이터 불러오기. (YAML 파일 로드)
		manifestFilePath : str = f"{metaPath}/{MANIFESTFILENAME}"
		builtins.print(f"prepareFilePath: {manifestFilePath}")
		YAMLWrapper.SetConstructor("!!python/object:dduk.application.manifestdata.ManifestData", YAMLWrapper.ManifestDataConstructor)
		YAMLWrapper.SetConstructor("!!python/object/apply:dduk.application.applicationexecutetype.ApplicationExecuteType", YAMLWrapper.ApplicationExecuteTypeConstructor)
		manifestData : ManifestData = YAMLWrapper.LoadYAMLFromFile(manifestFilePath)
		InternalRepository.Link(manifestData)

		#--------------------------------------------------------------------------------
		# 로거 생성.
		logger = Logger(manifestData.Name)
		InternalRepository.Link(logger)

		#--------------------------------------------------------------------------------
		# 심볼 설정.
		# 준비 데이터로부터 심볼목록을 불러와 설정.
		builtins.print("__PREPARED__")
		internalData.SetSymbols(manifestData.Symbols)

		#--------------------------------------------------------------------------------
		# 디버깅 설정. (서비스와 빌드는 디버깅 할 수 없다고 간주한다.)
		if manifestData.Type == ApplicationExecuteType.SOURCE:
			isDebug : bool = Launcher.VerifyDebug()
			internalData.SetDebug(isDebug)
		else:
			internalData.SetDebug(False)

		#--------------------------------------------------------------------------------
		# 실행 인수 : 실행된 파일 이름 설정.
		if sys.argv:
			builtins.print("__EXECUTE__")
			executeFileName = sys.argv[0]
			internalData.SetExecuteFileName(executeFileName)

		#--------------------------------------------------------------------------------
		# 실행 인수 : 입력된 데이터 설정.
		# 준비 데이터로부터 심볼목록을 불러와 설정.
		builtins.print("__ARGUMENT__")
		sys.argv.clear()
		sys.argv.append(executeFileName)
		sys.argv.extend(manifestData.Arguments)

		#--------------------------------------------------------------------------------
		# 경로 설정.
		internalData.SetRootPath(rootPath)
		internalData.SetMetaPath(metaPath)
		internalData.SetSourcePath(sourcePath)
		internalData.SetResourcePath(resourcePath)
		internalData.SetWorkingspacePath(workingspacePath)

		#--------------------------------------------------------------------------------
		# 경로 출력.
		builtins.print(f"isBuild: {application.IsBuild()}")
		builtins.print(f"rootPath: {application.GetRootPath()}")
		builtins.print(f"metaPath: {application.GetMetaPath()}")
		builtins.print(f"sourcePath: {application.GetSourcePath()}")
		builtins.print(f"resourcePath: {application.GetResourcePath()}")
		builtins.print(f"workingspacePath: {application.GetWorkingspacePath()}")

		#--------------------------------------------------------------------------------
		# 실행 방식에 따른 설정.
		# 빌드.
		logType : LogType = LogType.NONE
		if manifestData.Type == ApplicationExecuteType.BUILD:
			builtins.print("__BUILD__")
			logType = LogType.ERROR
		# 서비스.
		elif manifestData.Type == ApplicationExecuteType.SERVICE:
			builtins.print("__SERVICE__")
			logType = LogType.INFO
		# 소스.
		elif manifestData.Type == ApplicationExecuteType.SOURCE:
			builtins.print("__SOURCE__")				
			if isDebug:
				builtins.print("__DEBUG__")
				logType = LogType.DEBUG
			else:
				builtins.print("__NODEBUG__")
				logType = LogType.INFO
		else:
			raise Exception("Unknown Execute Type!!")

		#--------------------------------------------------------------------------------
		# 로그 설정.
		# 순서 : DEBUG < INFO < WARNING < ERROR < CRITICAL.
		try:
			useLogFile : bool = Application.HasSymbolWithPredefinedSymbol(PredefinedSymbols.SYMBOL_LOG)
			if useLogFile:
				logPath = application.GetRootPathWithRelativePath("logs")
				logger.Start(logType, logPath)
			else:
				logger.Start(logType, EMPTY)
		except Exception as exception:
			builtins.print(exception)

		#--------------------------------------------------------------------------------
		# 패키지 임포트.

		# 이상한 코드지만 메인 패키지의 부모를 추가해야 메인패키지가 등록된다.
		if isBuild:
			if cachePath not in sys.path:
				sys.path.append(cachePath)
		else:
			if rootPath not in sys.path:
				sys.path.append(rootPath)

		# 메인 패키지의 부모 디렉터리가 추가되어있지 않으면 메인 패키지를 임포트할 수 없다.
		try:
			importlib.import_module("src")
		except ModuleNotFoundError:
			raise ImportError(f"Failed to import the src package. Make sure that src is a valid package.")

		# 메인 패키지 임포트.
		# sourcePathBackSlash = sourcePath.replace(SLASH, BACKSLASH)
		# if sourcePathBackSlash not in sys.path: 
		# 	sys.path.append(sourcePathBackSlash)

		# 서브 패키지 임포트.
		# 루트패스를 시작으로 하여 자식경로로 계속 하향식 이동하며 디렉터리들 등록.
		# # 현재경로, 현재경로의 디렉터리들, 현재경로의 파일들.
		# for path, dirnames, filenames in os.walk(sourcePath):
		# 	path = path.replace(BACKSLASH, SLASH)
		# 	if not os.path.isdir(path):
		# 		continue
		# 	if path not in sys.path:
		# 		sys.path.append(path)

		# # 시그널 등록.
		# signal.signal(signal.SIGINT, lambda sight, frame: sys.exit(0))

		#--------------------------------------------------------------------------------
		# 시작.
		try:
			# 잔여 인자 출력.
			if sys.argv:
				Application.Log("__ARGUMENTS__")
				index = 0
				for arg in sys.argv:
					Application.Log(f" - [{index}] {arg}")
					index += 1

			# 메인 패키지 동적 로드.
			# 실행된 프로젝트 소스 폴더 내의 __main__.py를 찾아서 그 안의 Main()을 호출.
			mainModuleFilePath : str = Application.GetSourcePathWithRelativePath(f"__main__.py")
			if not os.path.isfile(mainModuleFilePath):
				raise FileNotFoundError(mainModuleFilePath)
			mainModuleSpecification = importlib.util.spec_from_file_location("src.__main__", mainModuleFilePath)
			mainModule = importlib.util.module_from_spec(mainModuleSpecification)
			mainModule.__package__ = "src"
			mainModuleSpecification.loader.exec_module(mainModule)

			# 메인 함수 실행.
			if not hasattr(mainModule, "Main"):
				raise AttributeError(f"\"Main\" function not found in {mainModuleFilePath}")
			mainFunction = builtins.getattr(mainModule, "Main")
			exitcode = mainFunction(sys.argv)
			return exitcode				
		# except KeyboardInterrupt as exception:
		# 	# if application.IsBuild():
		# 	# 	return 0
		# 	# else:
		# 	# 	Application.LogException(exception)
		# 	return 0
		except Exception as exception:
			Application.LogException(exception)


	#--------------------------------------------------------------------------------
	# 실행 환경 체크 : 바이너리 파일에서 실행했는지 상태 확인.
	# - pyinstaller : FROZEN
	#--------------------------------------------------------------------------------
	@staticmethod
	def VerifyBuild() -> bool:
		try:
			isVerify = builtins.getattr(sys, FROZEN, False)
			return isVerify
		except Exception as exception:
			builtins.print(exception)
			return False


	#--------------------------------------------------------------------------------
	# 실행 환경 체크 : 디버그 세션에 연결 된 상태 확인.
	# - pydevd : PyCharm, 3dsmax
	# - ptvsd : 3dsmax
	# - debugpy : VSCode
	#--------------------------------------------------------------------------------
	@staticmethod
	def VerifyDebug() -> bool:
		try:
			isVerify = debugpy.is_client_connected()
			return isVerify
		except Exception as exception:
			builtins.print(exception)
			return False