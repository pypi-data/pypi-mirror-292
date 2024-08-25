#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
import logging
import os
from queue import Queue
from logging import Logger as InternalLogger
from logging import handlers, StreamHandler, FileHandler, Formatter
from logging.handlers import QueueHandler, QueueListener
from ..ansicode import ANSICODE
from ..strutility import GetTimestampString
from .logtype import LogType


#--------------------------------------------------------------------------------
# 전역 상수 목록.
#--------------------------------------------------------------------------------
EMPTY : str = ""
NONE : str = "NONE"
COLON : str = ":"
SPACE : str = " "
SLASH : str = "/"
HYPHEN : str = "-"
COMMA : str = ","
UTF8 : str = "utf-8"


#--------------------------------------------------------------------------------
# 로거.
#--------------------------------------------------------------------------------
class Logger:
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------
	__ansicode : ANSICODE
	__internalLoggerName : str
	__internalLogger : InternalLogger


	#--------------------------------------------------------------------------------
	# 내부 로거 반환.
	#--------------------------------------------------------------------------------
	@property
	def InternalLogger(self) -> InternalLogger:
		return self.__internalLogger


	#--------------------------------------------------------------------------------
	# 생성됨.
	#--------------------------------------------------------------------------------
	def __init__(self, name : str) -> None:
		self.__ansicode = ANSICODE()
		self.__internalLoggerName = name
		self.__internalLogger = logging.getLogger(self.__internalLoggerName)


	#--------------------------------------------------------------------------------
	# 기록 시작.
	# - 로그 파일 사용 설정을 비활성화 하면 로그는 CLI상에서만 출력된다.
	#--------------------------------------------------------------------------------
	def Start(self, logType : LogType = LogType.DEBUG, logPath : str = EMPTY) -> None:

		useLogFile : bool = logPath is not EMPTY
		timestamp : str = GetTimestampString(EMPTY, EMPTY, EMPTY, True, EMPTY)
		logFilePath : str = f"{logPath}/{self.__internalLoggerName}-{timestamp}.log"

		# # EXE 파일 실행.
		# if Application.IsBuild():
		# 	useLogFile = False
		# 	logLevel = logging.WARNING
		# # VSCode에서 디버깅 실행.
		# elif Application.IsDebug():
		# 	useLogFile = True
		# 	logLevel = logging.DEBUG
		# 	logFilePath = Application.GetRootPathWithRelativePath(f"logs/pyappcore-debug-{timestamp}.log")
		# # Blender.exe로 소스코드 실행.
		# elif Application.HasSymbol(SYMBOL_SERVICE):
		# 	useLogFile = True
		# 	logLevel = logging.INFO
		# 	logFilePath = Application.GetRootPathWithRelativePath(f"logs/pyappcore-service-{timestamp}.log")
		# # VSCode에서 디버깅 없이 실행.
		# else:
		# 	useLogFile = True
		# 	logLevel = logging.INFO
		# 	logFilePath = Application.GetRootPathWithRelativePath(f"logs/pyappcore-nodebug-{timestamp}.log")

		# 로그 수준 설정.
		self.__internalLogger.setLevel(logType.value)

		# 로깅 큐 추가.
		# 로그 파일 기록이 자꾸 씹히는 이슈 있어서 사용. (하지만 개선 효과 없음)
		logQueue = Queue()
		ququeHandler = QueueHandler(logQueue)
		self.__internalLogger.addHandler(ququeHandler)

		# 로그 출력 양식 설정.
		# formatter : Formatter = Formatter("[%(asctime)s][%(name)s][%(levelname)s] %(message)s")
		formatter : Formatter = Formatter("[%(asctime)s][%(levelname)s] %(message)s")

		# 프린트 핸들러.
		# printHandler : PrintHandler = PrintHandler(logLevel)
		# printHandler.setLevel(logLevel)
		# printHandler.setFormatter(formatter)
		# applicationLogger.addHandler(printHandler)

		# 로그파일 설정.
		if useLogFile:
			if not os.path.isdir(logPath):
				os.makedirs(logPath)
			
			fileHandler : StreamHandler = FileHandler(logFilePath, encoding = UTF8)
			internalName = LogType.GetInternalName(logType)
			fileHandler.setLevel(internalName)
			fileHandler.setFormatter(formatter)
			# applicationLogger.addHandler(fileHandler)
			# queueListener = QueueListener(logQueue, printHandler, fileHandler)

			# 큐 시작.
			queueListener = QueueListener(logQueue, fileHandler)
			queueListener.start()


	#--------------------------------------------------------------------------------
	# 로그 출력.
	#--------------------------------------------------------------------------------
	def Print(self, text : str, logLevel : int) -> None:
		if logLevel == logging.FATAL or logLevel == logging.CRITICAL: self.__ansicode.Print(f"<bg_red><white><b>{text}</b></white></bg_red>")
		elif logLevel == logging.ERROR: self.__ansicode.Print(f"<red>{text}</red>")
		elif logLevel == logging.WARN or logLevel == logging.WARNING: self.__ansicode.Print(f"<yellow>{text}</yellow>")
		elif logLevel == logging.INFO: self.__ansicode.Print(f"{text}")
		elif logLevel == logging.DEBUG: self.__ansicode.Print(f"<magenta>{text}</magenta>")
		else: self.__ansicode.Print(text)