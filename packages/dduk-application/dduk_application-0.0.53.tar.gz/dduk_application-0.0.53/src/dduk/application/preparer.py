#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
import inspect
import json
import os
from dduk.core.project import Project
from dduk.utility import jsonutility
from .applicationexecutetype import ApplicationExecuteType
from .prepareddata import PreparedData
from .yamlwrapper import YAMLWrapper


#--------------------------------------------------------------------------------
# 전역 상수 목록.
#--------------------------------------------------------------------------------
PREPARED_DATANAME : str = "manifest"
PREPARED_DATAFILENAME : str = f"{PREPARED_DATANAME}.yaml"
BACKSLASH : str = "\\"
SLASH : str = "/"
COLON : str = "."
PYEXTENSION : str = ".py"
PACKAGE : str = "PACKAGE"
MODULE : str = "MODULE"
CLASS : str = "CLASS"
FUNCTION : str = "FUNCTION"
CARRIAGERETURN : str = "\r"
LINEFEED : str = "\n"
EMPTY : str = ""
LINEFEED : str = "\n"
READ : str = "r"
WRITE : str = "w"
UTF8 : str = "utf-8"
ASTERISK : str = "*"
DOUBLEQUOTATION : str = "\""
DDUK : str = "dduk"
APPLICATION : str = "application"

SOURCE : str = "source"
BUILD : str = "build"
SERVICE : str = "service"

SYMBOLS : str = "symbols"
ARGUMENTS : str = "Arguments"


#--------------------------------------------------------------------------------
# 준비자 클래스.
# - 데이터를 파이썬 코드로 변형해서 저장하므로 이후 추가 비용 없이 파일 이름만 알고 있으면 불러와 사용 가능.
# - 단, 이미 모듈이 리로드 되었다는 전제.
#--------------------------------------------------------------------------------
class Preparer:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------


	#--------------------------------------------------------------------------------
	# 생성됨.
	#--------------------------------------------------------------------------------
	def __init__(self) -> None:
		pass


	#--------------------------------------------------------------------------------
	# 준비.
	#--------------------------------------------------------------------------------
	def Prepare(self, applicationExecuteType : ApplicationExecuteType) -> None:
		#--------------------------------------------------------------------------------
		# 프리페어 표시.
		builtins.print("__PREPARE__")

		# 호출 스택 조사.
		stack = inspect.stack()
		if len(stack) < 2:
			raise Exception("Inspector Exception.")
		
		# 루트 경로와 루트 이름 생성.
		currrentFrame = inspect.stack()[1]
		startFilePath =  currrentFrame.filename
		rootPath = Project.FindRootPath(startFilePath)
		rootPath = rootPath.replace(BACKSLASH, SLASH)
		rootName = os.path.basename(rootPath)
		rootName = rootName.lower()

		# 임시 디렉터리 설정.
		temporaryPath = Project.FindTemporaryPath()
		cachePath : str = os.path.join(temporaryPath, "dduk", "application", "projects", rootName).replace(BACKSLASH, SLASH)
		metaPath : str = os.path.join(cachePath, "meta").replace(BACKSLASH, SLASH)
		os.makedirs(metaPath, exist_ok = True)

		# 파일 경로 생성.
		prepareFilePath : str = f"{metaPath}/{PREPARED_DATAFILENAME}"

		# 기존 파일 제거.
		if os.path.exists(prepareFilePath):
			os.remove(prepareFilePath)

		# 새로운 데이터 만들기.
		preparedData = PreparedData()
		preparedData.Name = rootName
		preparedData.Type = applicationExecuteType

		# 비주얼 스튜디오 코드로부터 셋팅 가져오기.
		settings : dict = self.GetVisualStudioCodeSettings(rootPath, preparedData.Type)
		if settings:
			# 심볼 목록.
			if SYMBOLS in settings:
				preparedData.Symbols.clear()
				symbols : list[str] = settings[SYMBOLS]
				symbols : list[str] = [symbol.upper() for symbol in symbols]
				preparedData.Symbols.update(symbols)

			# 인자 목록.
			if preparedData.Type == ApplicationExecuteType.SOURCE:
				if ARGUMENTS in settings:
					arguments : list[str] = settings[ARGUMENTS]
					preparedData.Arguments.clear()
					preparedData.Arguments.extend(arguments)
					builtins.print(arguments)

		# 파일 기록.
		YAMLWrapper.SaveYAMLToFile(prepareFilePath, preparedData)


	#--------------------------------------------------------------------------------
	# .vscode/settings.json 파일에서 상황에 맞는 데이터 가져오기.
	#--------------------------------------------------------------------------------
	def GetVisualStudioCodeSettings(self, rootPath : str, applicationExecuteType : ApplicationExecuteType) -> dict:
		try:
			vscodeSettingsFilePath = f"{rootPath}/.vscode/settings.json"
			if not os.path.exists(vscodeSettingsFilePath):
				return dict()
			with builtins.open(vscodeSettingsFilePath, READ, encoding = UTF8) as file:
				string = file.read()
				jsonText = jsonutility.RemoveAllCommentsInString(string)
				vscodeSettings = json.loads(jsonText)
		except Exception as exception:
			builtins.print(exception)
			return dict()
		
		try:
			if not vscodeSettings:
				raise ValueError(f"not found settings.json")
			if DDUK not in vscodeSettings:
				raise ValueError(f"\"{DDUK}\" property not found in settings.json")
			else:
				ddukSettings = vscodeSettings[DDUK]
			if APPLICATION not in ddukSettings:
				raise ValueError(f"\"{APPLICATION}\" property not found in settings.json")
			else:
				applicationSettings = ddukSettings[APPLICATION]

			# 소스 모드 설정.
			if applicationExecuteType == ApplicationExecuteType.SOURCE:
				if SOURCE in applicationSettings:
					return applicationSettings[SOURCE]
				else:
					raise ValueError(f"\"{SOURCE}\" property not found in settings.json")
			# 빌드 모드 설정.
			elif applicationExecuteType == ApplicationExecuteType.BUILD:
				if BUILD in applicationSettings:
					return applicationSettings[BUILD]
				else:
					raise ValueError(f"\"{BUILD}\" property not found in settings.json")
			# 서비스 모드 설정.
			elif applicationExecuteType == ApplicationExecuteType.SERVICE:
				if SERVICE in applicationSettings:
					return applicationSettings[SERVICE]
				else:
					raise ValueError(f"\"{SERVICE}\" property not found in settings.json")
		except Exception as exception:
			builtins.print(exception)
			return dict()		