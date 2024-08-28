#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
from logging import Handler, LogRecord
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
# 로그 화면 출력 핸들러.
#--------------------------------------------------------------------------------
class PrintHandler(Handler):
	#--------------------------------------------------------------------------------
	# 멤버 변수 목록.
	#--------------------------------------------------------------------------------


	#--------------------------------------------------------------------------------
	# 생성됨.
	#--------------------------------------------------------------------------------
	def __init__(self, logType : LogType = LogType.NONE) -> None:
		base = super()
		base.__init__(logType.value)


	#--------------------------------------------------------------------------------
	# 로그 출력.
	#--------------------------------------------------------------------------------
	def emit(self, record : LogRecord):
		message = self.format(record)
		builtins.print(message)
		# if record.levelno == FATAL or record.levelno == CRITICAL: Print(f"<bg_red><white><b>{message}</b></white></bg_red>")
		# elif record.levelno == ERROR: Print(f"<red>{message}</red>")
		# elif record.levelno == WARN or record.levelno == WARNING: Print(f"<yellow>{message}</yellow>")
		# elif record.levelno == INFO: Print(f"{message}")
		# elif record.levelno == DEBUG: Print(f"<magenta>{message}</magenta>")
		# PrintLog(message, record.levelno)