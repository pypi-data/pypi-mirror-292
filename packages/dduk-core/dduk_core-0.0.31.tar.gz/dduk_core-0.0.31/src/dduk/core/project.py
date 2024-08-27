#--------------------------------------------------------------------------------
# 참조 모듈 목록.
#--------------------------------------------------------------------------------
from __future__ import annotations
from typing import Any, Final, Callable, Iterator, Optional, Type, TypeVar, Union, Tuple, List, Dict, Set, cast
import builtins
import os
from .platform import PlatformType, GetPlatformType


#--------------------------------------------------------------------------------
# 전역 상수 목록.
#--------------------------------------------------------------------------------
SLASH : str = "/"
BACKSLASH : str = "\\"
TILDE : str = "~"
ROOTMARKERS : list[str] = [
	# 저장소.
	".svn",				# Subversion (SVN) version control system folder.
	".p4config",		# Perforce configuration file.
	".p4ignore",		# Perforce ignore patterns file.
	".git",				# Git version control system folder.
	".hg",				# Mercurial version control system folder.

	# 개발환경.
	".vscode",			# Visual Studio Code settings directory.
	".vs",				# Visual Studio settings directory.
	".idea",			# JetBrains IDE (PyCharm, IntelliJ IDEA, etc.) settings directory.

	# 파이썬 루트 파일.
	"setup.py",			# Python project setup script.
	"requirements.txt",	# Python project dependencies file.
	"Pipfile",			# Python project Pipenv dependency management file.
	"pyproject.toml",	# Python project configuration file.
	
	# "package.json",  # Node.js project configuration file.
	# "composer.json", # PHP project Composer configuration file.
	# "CMakeLists.txt",# CMake project configuration file.
	# "Makefile",      # Unix/Linux project build automation script.
	# "Cargo.toml",    # Rust project configuration file.
	# "gradle.build",  # Gradle project build script.
	# "pom.xml",       # Maven project configuration file.
	# ".terraform",    # Terraform configuration directory.
	# "Gemfile",       # Ruby project dependency management file.
	# "Rakefile",      # Ruby project build automation script.
	# "config.yml",    # Common YAML configuration file.
	# "config.yaml",   # Common YAML configuration file.
	# ".circleci",     # CircleCI configuration directory.
	# ".travis.yml",   # Travis CI configuration file.
]



#--------------------------------------------------------------------------------
# 프로젝트.
#--------------------------------------------------------------------------------
class Project:
	#--------------------------------------------------------------------------------
	# 대상 파일을 기준으로 상위 경로로 거슬러 올라가며 프로젝트 루트 경로 찾기.
	# - rootMarkers를 None으로 두면 일반적으로 루트 디렉터리에 반드시 존재하는 저장소 디렉터리나 셋팅 파일 등을 기준으로 검색.
	# - rootMarkers를 커스텀 할 경우 루트 디렉터리에만 존재하는 독자적인 파일 혹은 디렉터리를 마커로 두고 그 이름을 입력.
	# - start의 경우 검색을 시작할 대상 파일로, 해당 파일의 조상 중에는 반드시 루트 폴더를 식별할 수 있는 이름의 마커가 존재해야함.
	#--------------------------------------------------------------------------------
	@staticmethod
	def FindRootPath(start : str, rootMarkers : list[str] = None) -> str:
		current = os.path.abspath(start)
		if os.path.isfile(current):
			current = os.path.dirname(current)
		if not rootMarkers: rootMarkers = ROOTMARKERS
		while True:
			if any(os.path.exists(os.path.join(current, marker)) for marker in rootMarkers):
				return current.replace(BACKSLASH, SLASH)
			parent = os.path.dirname(current)
			if parent == current: break
			current = parent
		raise FileNotFoundError("Project root not found.")
	

	#--------------------------------------------------------------------------------
	# 유저 프로필 경로 찾기.
	# - 윈도우 : C:\Users\<username>
	# - 리눅스/맥 : /home/<username> or /Users/<username>
	#--------------------------------------------------------------------------------
	@staticmethod
	def FindUserProfilePath() -> str:
		profilePath = os.path.expanduser(TILDE)
		return profilePath.replace(BACKSLASH, SLASH)
	

	#--------------------------------------------------------------------------------
	# 운영체제 별 현재 사용자 임시 폴더 경로 찾기.
	#--------------------------------------------------------------------------------
	@staticmethod
	def FindUserTemporaryPath() -> str:
		platformType : PlatformType = GetPlatformType()
		userProfilePath = Project.FindUserProfilePath()
		userTemporaryPath : str = str()
		if platformType == PlatformType.WINDOWS:
			userTemporaryPath = os.path.join(userProfilePath, "AppData", "Local")
		elif platformType == PlatformType.LINUX:
			userTemporaryPath = os.path.join(userProfilePath, ".local", "share")
		elif platformType == PlatformType.MACOS:
			userTemporaryPath = os.path.join(userProfilePath, "Library", "Application Support")
		userTemporaryPath = userTemporaryPath.replace(BACKSLASH, SLASH)
		# os.makedirs(userTemporaryPath, exist_ok = True)
		return userTemporaryPath

	#--------------------------------------------------------------------------------
	# 운영체제 별 공통 사용자 임시 폴더 경로 찾기.
	#--------------------------------------------------------------------------------
	@staticmethod
	def FindAllUsersTemporaryPath() -> str:
		platformType : PlatformType = GetPlatformType()
		alluserTemporaryPath : str = str()
		if platformType == PlatformType.WINDOWS:
			alluserTemporaryPath = "C:\\ProgramData" # C:\\Users\\Public
		elif platformType == PlatformType.LINUX:
			alluserTemporaryPath = "/usr/local/share"
		elif platformType == PlatformType.MACOS:
			alluserTemporaryPath = "/Users/Shared"
		alluserTemporaryPath = alluserTemporaryPath.replace(BACKSLASH, SLASH)
		# os.makedirs(alluserTemporaryPath, exist_ok = True)
		return alluserTemporaryPath


	#--------------------------------------------------------------------------------
	# 운영체제 별 애플리케이션 데이터 임시 폴더 경로 찾기.
	# - 윈도우 : C:\ProgramData
	# - 리눅스/맥 : /var/tmp
	#--------------------------------------------------------------------------------
	@staticmethod
	def FindTemporaryPath() -> str:
		platformType : PlatformType = GetPlatformType()
		temporaryPath : str = str()
		if platformType == PlatformType.WINDOWS:
			temporaryPath = "C:\\ProgramData"
		elif platformType == PlatformType.LINUX or platformType == PlatformType.MACOS:
			temporaryPath = "/var/tmp"
		temporaryPath = temporaryPath.replace(BACKSLASH, SLASH)
		# os.makedirs(temporaryPath, exist_ok = True)
		return temporaryPath