"""
    CLI tool written in Python 3 used to systemically rename files in a directory while adhering to a variety of criteria.
    Copyright (C) 2022  Kevin Tyrrell

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Dict, List
from re import findall, compile, fullmatch
from math import log, ceil
from random import Random

from core.directory import *
from util.util import require_non_none


class RandomizeDecorator(Directory):
    def __init__(self, decorated: Directory, seed: int = None):
        """
        Decorator which randomly shuffles all numerical values in the directory

        :param decorated: Decorated Directory
        :param seed: Seed to be used ('None' for system's clock)
        """
        self.__decorated = require_non_none(decorated)
        self.__seed = seed

    def get_files(self) -> Dict[str, FileMetadata]:
        return self.__decorated.get_files()

    def operate(self) -> None:
        self.__decorated.operate()
        flist = list(self.get_files().values())
        gen = Random(self.__seed)
        for i in range(len(flist) - 1):
            i: int
            j: int = gen.randrange(i, len(flist))
            if i != j:
                i: FileMetadata = flist[i]
                j: FileMetadata = flist[j]
                temp = i.num
                i.num = j.num
                j.num = temp


class ExtensionDecorator(Directory):
    def __init__(self, decorated: Directory, ext: str):
        """
        Decorator which modifies the file extension of all files in the directory

        :param decorated: Decorated directory
        :param ext: Extension to be set
        """
        self.__decorated = require_non_none(decorated)
        self.__ext = require_non_none(ext)

    def get_files(self) -> Dict[str, FileMetadata]:
        return self.__decorated.get_files()

    def operate(self) -> None:
        self.__decorated.operate()
        files, ext = self.get_files(), self.__ext
        for k, v in files.items():
            v.ext = ext


class FormatDecorator(Directory):
    __format_specifier = "${}"  # Substitution constant for optional input regex

    def __init__(self, decorated: Directory, fmt: list[str]):
        """
        Decorator which modifies the output filename into a specified format

        The format string must contain a '$d' specifier, designated for the numerical pattern.
        e.g. [4.doc, 5.doc] -> FormatDecorator("Homework ($d)") -> [Homework (4).doc, Homework (5).doc]

        :param decorated: Decorated directory
        :param fmt: Format to be applied to the output file
        """
        self.__decorated = require_non_none(decorated)
        self.__fmt = require_non_none(fmt)

    def get_files(self) -> Dict[str, FileMetadata]:
        return self.__decorated.get_files()

    def operate(self) -> None:
        self.__decorated.operate()
        files, fmt = self.get_files(), self.__fmt

        """
        Index 1: Output Format
        * Must contain '$d' format specifier for numerical pattern
        * May contain '$1', '$2', etc format specifiers for regex substitution
        
        Index 2: [Optional] Input Capture
        * Regex string which should include capture groups
        * Any captured group will be substituted into the output format
        * Captured groups correspond to their format specifiers, in order of capture
        * e.g. (Apple) Pear (Banana), '$1' corresponds to 'Apple', '$2' -> 'Banana'
        """
        if len(fmt) > 1:  # User wants to capture input
            pattern = compile(fmt[1])
            for k, v in files.items():
                fmt = fmt[0]
                matcher = fullmatch(pattern, k)
                if matcher is None:
                    raise Exception("--format optional capture regex does not match file: {}".format(k))
                groups = matcher.groups()
                for i in range(len(groups)):
                    target = FormatDecorator.__format_specifier.format(i + 1)
                    fmt = fmt.replace(target, groups[i])
                v.fmt = fmt
        else:  # No regex capture provided, no need for substitution
            for k, v in files.items():
                v.fmt = fmt[0]


class ZeroesDecorator(Directory):
    def __init__(self, decorated: Directory, digits: int = 0):
        """
        Decorator which inserts leading zeroes preceding the numerical value

        e.g. [7.png, 300.png] -> ZeroesDecorator(3) -> [007.png, 300.png]

        :param decorated: Decorated directory
        :param digits: Number of desired digits for the numerical value (0 for automatic)
        """
        self.__decorated = require_non_none(decorated)
        self.__digits = require_non_none(digits)

    def get_files(self) -> Dict[str, FileMetadata]:
        return self.__decorated.get_files()

    def operate(self) -> None:
        self.__decorated.operate()
        files = self.get_files()
        large = max(map(lambda x: x.num, files.values()))
        digits = max(self.__digits, self.__count_digits(large))
        for k, v in files.items():
            v.fnum = (digits - self.__count_digits(v.num)) * "0" + str(v.num)

    @staticmethod
    def __count_digits(num: int):
        """
        :param num: Number to count digits of
        :return: Number of digits present
        """
        return int(ceil(log(abs(num) + 1, 10)))


class ShifterDecorator(Directory):
    def __init__(self, decorated: Directory, shift: int):
        """
        Decorator which shifts all numerical values in filenames by a specified offset

        e.g. [50.mkv] -> ShifterDecorator(-5) -> [45.mkv]

        :param decorated: Decorated directory
        :param shift: int Offset to shift by
        """
        self.__decorated = require_non_none(decorated)
        self.__shift = require_non_none(shift)
        if shift == 0:
            raise ValueError("File number shift is invalid: " + shift)

    def get_files(self) -> Dict[str, FileMetadata]:
        return self.__decorated.get_files()

    def operate(self) -> None:
        self.__decorated.operate()
        files, shift = self.get_files(), self.__shift
        for k, v in files.items():
            v.num = v.num + shift


class FlattenDecorator(Directory):
    def __init__(self, decorated: Directory):
        """
        Decorator which flattens the numerical pattern, ensuring all files are consecutive

        e.g. [ "15.avi", "24.avi", "101.avi" ] -> [ "15.avi", "16.avi", "17.avi" ]

        :param decorated: Decorated directory
        """
        self.__decorated = require_non_none(decorated)

    def get_files(self) -> Dict[str, FileMetadata]:
        return self.__decorated.get_files()

    def operate(self) -> None:
        self.__decorated.operate()
        files = self.get_files()
        if len(files) <= 1:
            return  # A directory of zero or one files is already flattened

        sort = sorted(files.items(), key=lambda t: t[1].num)
        first: FileMetadata = sort[0][1]
        small = int(first.num)  # Redundant cast
        for i in range(1, len(files)):  # Skip first (smallest) element
            v: FileMetadata = sort[i][1]
            v.num = small + i


class NumeratedDecorator(Directory):
    def __init__(self, decorated: Directory):
        """
        Decorator which initializes the numerical pattern according to the filenames in the directory.
        This decorator is an initialization operation and must be called before other decorators.

        e.g. [ "MyPhoto34HighRes.png", "MyPhoto36HighRes.png" ] ->
                { "MyPhoto34HighRes.png": 34, "MyPhoto36HighRes.png": 36 }

        :param decorated: Decorated directory
        """
        self.__decorated = require_non_none(decorated)

    def get_files(self) -> Dict[str, FileMetadata]:
        return self.__decorated.get_files()

    def operate(self) -> None:
        self.__decorated.operate()
        files = self.get_files()

        regexp = "([0-9]+)"  # Captures all 'runs' of integers in the filename
        runs_by_file = {f: [int(e) for e in findall(regexp, f)] for f in files}
        # Count of numerical 'runs' in which the filenames all share
        num_runs = min(map(lambda x: len(x), runs_by_file.values()))
        unique_runs = list(filter(
            lambda x: NumeratedDecorator.__is_unique_run_set(runs_by_file, x), list(range(0, num_runs))))

        if len(unique_runs) > 1:
            for t in runs_by_file.items():
                print("{}\n\tAmbiguous numbering: {}".format(t[0], ", ".join(map(lambda x: str(t[1][x]), unique_runs))))
            raise Exception("A numerated pattern could not be differentiated")
        if len(unique_runs) <= 0:
            raise Exception("A numerated pattern is not present in the directory")
        unique_runs = unique_runs[0]
        for k, v in files.items():
            v.num = runs_by_file[k][unique_runs]  # Pattern can now be determined

    @staticmethod  # Returns true if all runs at an index are unique
    def __is_unique_run_set(runs: Dict[str, List[int]], index: int):
        s = set()
        for nums in runs.values():
            e = nums[index]
            if e in s:
                return False
            s.add(e)
        return True
