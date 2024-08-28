#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
import os
import yaml
from .applicationexecutetype import ApplicationExecuteType
from .manifestdata import ManifestData


#--------------------------------------------------------------------------------
# 전역 상수 목록.
#--------------------------------------------------------------------------------
READ : str = "r"
WRITE : str = "w"
UTF8 : str = "utf-8"
DOUBLEEXCLAMATIONMARK : str = "!!"
TAGPREFIX : str = "tag:yaml.org,2002:"


#--------------------------------------------------------------------------------
# YAML 래퍼 클래스.
#--------------------------------------------------------------------------------
class YAMLWrapper:
	#--------------------------------------------------------------------------------
	# 클래스 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	__Constructors : Dict[str, Callable[[yaml.Loader, yaml.Node], Any]] = dict()


	#--------------------------------------------------------------------------------
	# 역직렬화 처리기 설정.
	# - 파일 : !!python/object:dduk.application.manifestdata.ManifestData
	# - 등록 : tag:yaml.org,2002:python/object:dduk.application.manifestdata.ManifestData
	# - 파일 : !!python/object/apply:dduk.application.applicationexecutetype.ApplicationExecuteType
	# - 등록 : tag:yaml.org,2002:python/object/apply:dduk.application.applicationexecutetype.ApplicationExecuteType
	# - 즉, 변환 방식 : "!!" ==> "tag:yaml.org,2002:"
	#--------------------------------------------------------------------------------
	@classmethod
	def SetConstructor(selfClassType, tag : str, constructor : Callable[[yaml.Loader, yaml.Node], Any]) -> bool:
		# 태그와 생성자 중 하나라도 없으면 실패.
		if not tag or not constructor:
			return False

		# 태그가 정상적 표기법과 일치하는지 확인 후 다르면 수정.
		fixedTag = tag
		if tag.startswith(DOUBLEEXCLAMATIONMARK) or not tag.startswith(TAGPREFIX):
			fixedTag = tag.replace(DOUBLEEXCLAMATIONMARK, TAGPREFIX)

		# 태그가 이미 존재하면 실패.
		if fixedTag in selfClassType.__Constructors:
			return False

		# 태그 등록 및 성공 반환.	
		selfClassType.__Constructors[fixedTag] = constructor
		yaml.add_constructor(fixedTag, constructor)
		return True


	#--------------------------------------------------------------------------------
	# YAML 파일 불러오기.
	#--------------------------------------------------------------------------------
	@classmethod
	def LoadYAMLFromFile(selfClassType, filePath : str) -> Any:
		if not filePath:
			return None
		if not os.path.isfile(filePath):
			return None
		try:
			with open(filePath, READ, encoding = UTF8) as file:
				yamlString = file.read()
				value = yaml.load(yamlString, Loader = yaml.FullLoader)
				return value
		except Exception as exception:
			builtins.print(exception)
			return None
		

	#--------------------------------------------------------------------------------
	# YAML 파일 저장하기.
	#--------------------------------------------------------------------------------
	@classmethod
	def SaveYAMLToFile(selfClassType, prepareFilePath : str, value : Any) -> bool:
		if not value:
			return False
		try:
			with open(prepareFilePath, WRITE, encoding = UTF8) as file:
				yamlData = yaml.dump(value, default_flow_style = False, sort_keys = False, width = 80, indent = 4)
				file.write(yamlData)
				return True
		except Exception as exception:
			builtins.print(exception)
			return False


	#--------------------------------------------------------------------------------
	# 실행 준비 데이터 역직렬화 처리기.
	#--------------------------------------------------------------------------------
	@staticmethod
	def ManifestDataConstructor(loader : yaml.Loader, node : yaml.Node) -> ManifestData:
		mappings : dict = loader.construct_mapping(node, deep = True)
		manifestData = ManifestData()
		manifestData.Name = mappings.get("Name", str())
		manifestData.Version = mappings.get("Version", "1.0.0")
		manifestData.Type = mappings.get("Type", ApplicationExecuteType.UNKNOWN)
		manifestData.Symbols = mappings.get("Symbols", set())
		manifestData.Arguments = mappings.get("Arguments", list())
		return manifestData


	#--------------------------------------------------------------------------------
	# 애플리케이션 실행 타입 역직렬화 처리기.
	#--------------------------------------------------------------------------------
	@staticmethod
	def ApplicationExecuteTypeConstructor(loader : yaml.Loader, node : yaml.Node) -> ApplicationExecuteType:
		sequences : list = loader.construct_sequence(node, deep = True)		
		return ApplicationExecuteType(sequences[0])