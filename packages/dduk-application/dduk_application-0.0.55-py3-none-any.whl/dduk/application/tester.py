#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
import importlib
import os
import sys
import unittest
import debugpy


#--------------------------------------------------------------------------------
# 테스터 클래스.
#--------------------------------------------------------------------------------
class Tester:
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
	def Test(self, pattern = "test_*.py") -> int:
		#--------------------------------------------------------------------------------
		# 테스트 표시.
		builtins.print("__TESTS__")
	
		# 현재 __main__ 으로 실행되는 코드 대상을 기준으로 한 경로.
		# 따라서 반드시 메인 스크립트는 src 안에 있어야 한다.
		testerFilePath = os.path.abspath(sys.modules["__main__"].__file__)
		testsPath : str = os.path.dirname(testerFilePath)
		rootPath : str = os.path.dirname(testsPath)
		sourcePath : str = os.path.join(rootPath, "src")

		#--------------------------------------------------------------------------------
		# 패키지 임포트.

		# 이상한 코드지만 현재 패키지의 부모를 추가해야 현재 패키지가 등록된다.
		if rootPath not in sys.path:
			sys.path.append(rootPath)

		# 현재 패키지의 부모 디렉터리가 추가되어있지 않으면 현재 패키지를 임포트할 수 없다.
		try:
			importlib.import_module("src")
		except ModuleNotFoundError:
			raise ImportError(f"Failed to import the src package. Make sure that src is a valid package.")
		try:
			importlib.import_module("tests")
		except ModuleNotFoundError:
			raise ImportError(f"Failed to import the tests package. Make sure that src is a valid package.")

		#--------------------------------------------------------------------------------
		# 시작.
		try:
			# 패키지 실행.
			# 실행된 프로젝트 소스 폴더 내의 __main__.py를 찾아서 그 안의 Main()을 호출.
			testsModuleFilePath : str = os.path.join(testsPath, "__main__.py")
			if not os.path.isfile(testsModuleFilePath):
				raise FileNotFoundError(testsModuleFilePath)
			mainModuleSpecification = importlib.util.spec_from_file_location("tests.__main__", testsModuleFilePath)
			mainModule = importlib.util.module_from_spec(mainModuleSpecification)
			mainModule.__package__ = "tests"
			mainModuleSpecification.loader.exec_module(mainModule)

			# 테스트 로더 생성.
			loader = unittest.TestLoader()

			# tests 폴더 내의 test_ 로 시작하는 모든 스크립트 파일을 기준으로 테스트 스위트 생성.
			suite = loader.discover(start_dir = testsPath, pattern = pattern)

			# 테스트 실행기 생성.
			runner = unittest.TextTestRunner()
			runner.run(suite)
			return 0
		
			# # 메인 함수 실행.
			# if not hasattr(mainModule, "Main"):
			# 	raise AttributeError(f"\"Main\" function not found in {testsModuleFilePath}")
			# mainFunction = builtins.getattr(mainModule, "Main")
			# exitcode = mainFunction(sys.argv)
			# return exitcode
		except Exception as exception:
			builtins.print(exception)