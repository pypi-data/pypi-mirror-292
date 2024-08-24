# Copyright 2024 Khiat Mohammed Abderrezzak
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Khiat Mohammed Abderrezzak <khiat.dev@gmail.com>


"""Sophisticate Court Queue"""


from typing import List, NoReturn, Any, Self
from tabulate import tabulate


__all__: List = [
    "courtQueue",
    "QueueOverflowError",
    "QueueUnderflowError",
]


def _red(text: str) -> str:
    """Red Coloring Function"""
    return f"\033[91;1m{text}\033[00m"


def _green(text: str) -> str:
    """Green Coloring Function"""
    return f"\033[92;1m{text}\033[00m"


def _blue(text: str) -> str:
    """Blue Coloring Function"""
    return f"\033[94;1m{text}\033[00m"


class QueueOverflowError(Exception):
    pass


class QueueUnderflowError(Exception):
    pass


class courtQueue:
    def __init__(
        self: "courtQueue",
        data: List[List[Any]] | None = None,
        *,
        detail: bool = False,
        rows: int = 1,
        columns: int = 1,
    ) -> None:
        if data is None:
            self.rows: int = rows
            self.columns: int = columns
        self.row: int = 0
        self.col: int = 0
        self.len: int = 0
        self.court_queue: List[List[Any]] = data
        self.detail: bool = detail

    @property
    def rows(self: "courtQueue") -> int:
        return self._rows

    @rows.setter
    def rows(self: "courtQueue", rows: int) -> None | NoReturn:
        if not isinstance(rows, int):
            raise ValueError("The number of rows must be an integer !")
        if rows == 0:
            raise ValueError("The number of rows must be greater than zero !")
        if rows < 0:
            raise ValueError("The number of rows must be a positive number !")
        self._rows: int = rows

    @property
    def columns(self: "courtQueue") -> int:
        return self._columns

    @columns.setter
    def columns(self: "courtQueue", columns: int) -> None | NoReturn:
        if not isinstance(columns, int):
            raise ValueError("The number of columns must be an integer !")
        if columns == 0:
            raise ValueError("The number of columns must be greater than zero !")
        if columns < 0:
            raise ValueError("The number of columns must be a positive number !")
        self._columns: int = columns

    @property
    def court_queue(self: "courtQueue") -> Self:
        return self

    @court_queue.setter
    def court_queue(
        self: "courtQueue", data: List[List[Any]] | None
    ) -> None | NoReturn:
        if not isinstance(data, list):
            if data is None:
                data: List = []
                for i in range(self.rows):
                    data.append([])
                    for j in range(self.columns):
                        data[i].append(None)
            else:
                raise TypeError("Only the list data type is accepted.")
        else:
            none_values: int = 0
            for i in range(len(data)):
                if not isinstance(data[i], list):
                    raise TypeError("Rows must be of list data type.")
                else:
                    if len(data[0]) is not len(data[i]):
                        raise ValueError(
                            "The number of columns in each row is not the same !"
                        )
                    if i % 2 == 0:
                        for j in range(len(data[i])):
                            if data[i][j] is None:
                                try:
                                    if data[i][j + 1] is not None:
                                        raise ValueError(
                                            "A value after an empty value is not accepted."
                                        )
                                    else:
                                        none_values += 1
                                except IndexError as e0:
                                    try:
                                        if data[i + 1][-1] is not None:
                                            raise ValueError(
                                                "A value after an empty value is not accepted."
                                            ) from None
                                        else:
                                            none_values += 1
                                    except IndexError as e1:
                                        none_values += 1
                    else:
                        for j in range(-1, -len(data[i]) - 1, -1):
                            if data[i][j] is None:
                                try:
                                    if data[i][j - 1] is not None:
                                        raise ValueError(
                                            "A value after an empty value is not accepted."
                                        )
                                    else:
                                        none_values += 1
                                except IndexError as e2:
                                    try:
                                        if data[i + 1][0] is not None:
                                            raise ValueError(
                                                "A value after an empty value is not accepted."
                                            ) from None
                                        else:
                                            none_values += 1
                                    except IndexError as e3:
                                        none_values += 1
            if not none_values:
                self.row: int = len(data)
                self.col: int = (
                    len(data[-1]) if (self.row - 1) % 2 == 0 else -len(data[-1]) - 1
                )
                self.len: int = self.row * len(data[0])
            else:
                self.row: int = (
                    (
                        len(data) - 1 - (none_values // len(data[0]))
                        if none_values // (none_values // len(data[0])) > len(data[0])
                        else (len(data) - (none_values // len(data[0])))
                    )
                    if none_values // len(data[0]) != 0
                    else len(data) - 1
                )
                self.col: int = (
                    (
                        len(data[0]) - (none_values % len(data[0]))
                        if none_values % len(data[0]) != 0
                        else 0
                    )
                    if self.row % 2 == 0
                    else (
                        (none_values % len(data[0]) - len(data[0]) - 1)
                        if none_values % len(data[0]) != 0
                        else -1
                    )
                )
                self.len: int = (len(data) * len(data[0])) - none_values
        self._court_queue: List[List[Any]] = data

    def enqueue(self: "courtQueue", value: Any) -> None | NoReturn:
        try:
            if (
                self.col != len(self._court_queue[self.row])
                and self.col != -len(self._court_queue[self.row]) - 1
            ):
                self._court_queue[self.row][self.col] = value
                self.len += 1
                if self.row % 2 == 0:
                    self.col += 1
                else:
                    self.col -= 1
            else:
                if self.row % 2 == 0:
                    self.col = -1
                else:
                    self.col = 0
                self.row += 1
                self.enqueue(value)
        except IndexError as e4:
            raise QueueOverflowError("The queue is full !") from None

    def dequeue(self: "courtQueue") -> None | NoReturn:
        if self._court_queue[0][0] is not None:
            self._court_queue[0].pop(0)
            self.len -= 1
            for i in range(len(self._court_queue)):
                if i % 2 == 0:
                    try:
                        if self._court_queue[i + 1][-1] is not None:
                            self._court_queue[i].append(self._court_queue[i + 1].pop())
                        else:
                            self._court_queue[i].append(None)
                            break
                    except IndexError as e5:
                        self._court_queue[i].append(None)
                else:
                    try:
                        if self._court_queue[i + 1][0] is not None:
                            self._court_queue[i].insert(
                                0, self._court_queue[i + 1].pop(0)
                            )
                        else:
                            self._court_queue[i].insert(0, None)
                            break
                    except IndexError as e6:
                        self._court_queue[i].insert(0, None)
            if self.row == len(self._court_queue):
                self.row -= 1
                if self.row % 2 == 0:
                    self.col -= 1
                else:
                    self.col += 1
            else:
                if self.col != 0 and self.col != -1:
                    if self.row % 2 == 0:
                        self.col -= 1
                    else:
                        self.col += 1
                else:
                    self.row -= 1
                    if self.row % 2 == 0:
                        self.col: int = (
                            len(self._court_queue[0]) if self.row != 0 else 0
                        )
                    else:
                        self.col: int = -len(self._court_queue[0]) - 1
        else:
            raise QueueUnderflowError("The queue is empty !")

    def isEmpty(self: "courtQueue") -> bool:
        return not self._court_queue[0][0]

    def isFull(self: "courtQueue") -> bool:
        if (len(self._court_queue) - 1) % 2 == 0:
            return not not self._court_queue[-1][-1]
        else:
            return not not self._court_queue[-1][0]

    def peek(self: "courtQueue") -> Any | NoReturn:
        if self._court_queue[0][0] is not None:
            return self._court_queue[0][0]
        raise QueueUnderflowError("The queue is empty!")

    def top(self: "courtQueue") -> Any | NoReturn:
        return self.peek()

    def clear(self: "courtQueue") -> None:
        if self.len > 0:
            for _ in range(self.len):
                self.dequeue()

    def __len__(self: "courtQueue") -> int:
        return self.len

    def __str__(self: "courtQueue") -> str:
        if not self.detail:
            return f"{self._court_queue}"
        else:
            output: List = []
            for i in range(len(self._court_queue)):
                if i % 2 == 0:
                    (
                        output.append([_red("^ EXIT")])
                        if i != 0
                        else output.append([_red("<- EXIT")])
                    )
                    for j in range(len(self._court_queue[i])):
                        if self._court_queue[i][j] is not None:
                            if not isinstance(self._court_queue[i][j], str):
                                output[i].append(_blue(self._court_queue[i][j]))
                            else:
                                if len(self._court_queue[i][j]) == 0:
                                    output[i].append(self._court_queue[i][j])
                                elif len(self._court_queue[i][j]) == 1:
                                    output[i].append(
                                        _blue(f"'{self._court_queue[i][j]}'")
                                    )
                                else:
                                    output[i].append(
                                        _blue(f'"{self._court_queue[i][j]}"')
                                    )
                        else:
                            output[i].append("")
                    output[i].append(_green("<- ENTER"))
                else:
                    output.append([_green("ENTER ->")])
                    for j in range(len(self._court_queue[i])):
                        if self._court_queue[i][j] is not None:
                            if not isinstance(self._court_queue[i][j], str):
                                output[i].append(_blue(self._court_queue[i][j]))
                            else:
                                if len(self._court_queue[i][j]) == 0:
                                    output[i].append(self._court_queue[i][j])
                                elif len(self._court_queue[i][j]) == 1:
                                    output[i].append(
                                        _blue(f"'{self._court_queue[i][j]}'")
                                    )
                                else:
                                    output[i].append(
                                        _blue(f'"{self._court_queue[i][j]}"')
                                    )
                        else:
                            output[i].append("")
                    output[i].append(_red("EXIT ^"))
            return f"{tabulate(output, tablefmt='fancy_grid')}"


def _main() -> None:
    print("court-queue")


if __name__ == "__main__":
    _main()
