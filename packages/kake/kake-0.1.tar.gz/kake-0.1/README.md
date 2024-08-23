# kake - Klinoff Application Konstruction Engine

## Description

Kake is a simple build system for C/C++ projects. It is designed to be better than cmake and at least better than gradle.

## Features

- No need to write a lot of complicated scripts and other stuff
- not gradle

## Usage

1. Create a `kakefile.py` in the root of your project
2. Run `python kakefile.py`
3. Profit

## Docs

empty...

## Examples

```python
# File structure
# .
# ├── include/
# │   ├── calc/
# │   │   └── calc.hpp
# │   └── magic/
# │   │   └── magic.hpp
# │   ├── dont_include/
# │   │   └── dont_include.hpp
# ├── src/
# │   └── main.cpp
# │   └── cups.cpp
# │   └── cups.hpp
# ├── lib/
# │   ├── calc/
# │   │   └── calc.cpp
# │   └── magic/
# │   │   └── magic.dll
# │   │   └── magic.lib
# │   │   └── magic.so
# │   ├── dont_include/
# │   │   └── dont_include.cpp
# ├── build/
# └── kakefile.py


from kake import *

project = Project(
    "MyEpicProject", 
    "1.0.0", 
    Executable
)

project.add_include(
    [
        "include/calc",
        "include/magic"
    ]
) # or to include all files in a directory: project.add_include("include")

project.add_lib(
    [
        "lib/calc",
        "lib/magic"
    ]
) # or to include all files in a directory: project.add_lib("lib")

project.add_src(
    [
        "src/main.cpp",
        "src/cups.cpp"
    ]
) # or to include all files in a directory: project.add_src("src/") or project.add_src("src/*.cpp")

project.add_flags(
    [
        "-Wall",
        "-Wextra",
        "-Werror"
    ]
)

project.build()
# kake will generate gcc commands and run them:
# gcc -Wall -Wextra -Werror -Iinclude/calc -Iinclude/magic -Llib/calc -Llib/magic -o build/MyEpicProject src/main.cpp src/cups.cpp -lcalc -lmagic

```

## CLI

### Build project

```bash
kake
```

### New project

```bash
kake new <project_name>
```

## Installation

```bash
pip install kake
```
