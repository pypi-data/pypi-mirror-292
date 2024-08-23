"""Start of kake"""
import sys
import os


def main_function():
    """Main function of the project."""
    print("Hello from kake")

class Project:
    """Project class for the project."""

    def __init__(
        self,
        name,
        include=[],
        lib=[],
        src=[],
        flags=[],
        build_dir="build"
    ):
        self.name = name
        self.include = include
        self.lib = lib
        self.src = src
        self.flags = flags
        self.build_dir = build_dir

    def get_name(self):
        """Get the name of the project."""
        return self.name

    def set_name(self, name):
        """Set the name of the project."""
        self.name = name

    def add_include(self, include):
        """Add include to the project."""
        self.include = include

    def add_lib(self, lib):
        """Add lib to the project."""
        self.lib = lib

    def add_src(self, src: list) -> None:
        """Add src to the project."""
        self.src = src

    def add_flags(self, flags):
        """Add flags to the project."""
        self.flags = flags

    def build(self):
        """Build the project."""

        print(f"Building '{self.name}' {os.getcwd()}")

        include_list = [f"-I{inc}" for inc in self.include]
        include = " ".join(include_list) + " "

        lib_list = [f"-l{lib}" for lib in self.lib]
        lib = " ".join(lib_list) + " "

        src = " ".join(self.src) + " "

        flags = " ".join(self.flags) + " "

        command = f"g++ -o {self.build_dir}/{self.name} {include} {lib} {src} {flags}"

        # print(f"{command}")

        cm = os.system(command)

        if cm == 0:
            print("Build successful")
        else:
            print("Build failed")
