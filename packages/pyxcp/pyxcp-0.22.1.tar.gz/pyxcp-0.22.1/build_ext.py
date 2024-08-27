#!/usr/bin/env python

import multiprocessing as mp
import os
import platform
import re
import subprocess  # nosec
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


TOP_DIR = Path(__file__).parent

print("Platform", platform.system())
uname = platform.uname()
if uname.system == "Darwin":
    os.environ["MACOSX_DEPLOYMENT_TARGET"] = "11.0"


def banner(msg: str) -> None:
    print("=" * 80)
    print(str.center(msg, 80))
    print("=" * 80)


def build_extension(debug: bool = False, use_temp_dir: bool = False) -> None:
    print("CMakeBuild::build_extension()")

    debug = bool(os.environ.get("DEBUG", 0)) or debug
    cfg = "Debug" if debug else "Release"
    print(f" BUILD-TYPE: {cfg!r}")
    cmake_args = [
        f"-DPYTHON_EXECUTABLE={sys.executable}",
        f"-DCMAKE_BUILD_TYPE={cfg}",  # not used on MSVC, but no harm
    ]
    build_args = ["--config Release", "--verbose"]
    # cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=1 /path/to/src

    if sys.platform.startswith("darwin"):
        # Cross-compile support for macOS - respect ARCHFLAGS if set
        archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
        if archs:
            cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]

    if use_temp_dir:
        build_temp = Path(TemporaryDirectory(suffix=".build-temp").name) / "extension_it_in"
    else:
        build_temp = Path(".")
    # print("cwd:", os.getcwd(), "build-dir:", build_temp, "top:", str(TOP_DIR))
    if not build_temp.exists():
        build_temp.mkdir(parents=True)

    banner("Step #1: Configure")
    # cmake_args += ["--debug-output"]
    subprocess.run(["cmake", str(TOP_DIR), *cmake_args], cwd=build_temp, check=True)  # nosec

    cmake_args += [f"--parallel {mp.cpu_count()}"]

    banner("Step #2: Build")
    # build_args += ["-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]
    subprocess.run(["cmake", "--build", build_temp, *build_args], cwd=TOP_DIR, check=True)  # nosec

    banner("Step #3: Install")
    # subprocess.run(["cmake", "--install", "."], cwd=build_temp, check=True)  # nosec
    subprocess.run(["cmake", "--install", build_temp], cwd=TOP_DIR, check=True)  # nosec


if __name__ == "__main__":
    includes = subprocess.getoutput("pybind11-config --cmakedir")  # nosec
    os.environ["pybind11_DIR"] = includes
    build_extension(False)
