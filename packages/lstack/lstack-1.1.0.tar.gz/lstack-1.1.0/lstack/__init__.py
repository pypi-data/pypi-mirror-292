# Copyright (c) 2024 Khiat Mohammed Abderrezzak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: Khiat Mohammed Abderrezzak <khiat.dev@gmail.com>


"""Sophisticate Linked Stack"""


__all__: list = [
    "singlyLinkedStack",
    "doublyLinkedStack",
    "CapacityError",
    "StackOverflowError",
    "StackUnderflowError",
]


from linkedit import (
    tabulate,
    singlyLinkedList,
    doublyLinkedList,
    _red,
    _green,
    _blue,
)


class CapacityError(Exception):
    pass


class StackOverflowError(Exception):
    pass


class StackUnderflowError(Exception):
    pass


class _stack:
    def __init__(
        self: "_stack",
        data: object = None,
        *,
        capacity: int,
        detail: bool = False,
    ) -> None:
        self.capacity: int = capacity
        self.size: int = 0
        self.detail: bool = detail
        self.stack: list = data

    @property
    def capacity(self: "_stack") -> int:
        return self._capacity

    @capacity.setter
    def capacity(self: "_stack", capacity: int) -> None:
        if not isinstance(capacity, int):
            raise CapacityError("Capacity must be an integer !")
        elif capacity < 0:
            raise CapacityError("Capacity must be positif integer !")
        elif capacity == 0:
            raise CapacityError("Capacity must be greater than zero !")
        else:
            self._capacity: int = capacity

    def __str__(self: "_stack") -> str:
        stack: list = []
        if self.detail:
            stack.append(
                [
                    _green("ENTER")
                    + _red("  ^")
                    + "\n"
                    + " " * len("En")
                    + _green("|")
                    + " " * len("er  ")
                    + _red("|")
                    + "\n"
                    + " " * len("En")
                    + _green("v")
                    + " " * len("er ")
                    + _red("EXIT")
                ]
            )
            for _ in range(self._capacity - self.size):
                stack.append([""])
            try:
                tracker: object = self.pop_index
            except AttributeError as e0:
                tracker: object = self._stack._head
        else:
            tracker: object = self._stack._head
        for _ in range(self.size):
            if self.detail:
                if not isinstance(tracker.data, str):
                    stack.append([_blue(f"{tracker.data}")])
                else:
                    if len(tracker.data) == 0:
                        stack.append([tracker.data])
                    elif len(tracker.data) == 1:
                        stack.append([_blue(f"'{tracker.data}'")])
                    else:
                        stack.append([_blue(f'"{tracker.data}"')])
                try:
                    tracker: object | None = tracker.prev
                except AttributeError as e1:
                    tracker: object | None = tracker.next
            else:
                stack.append(tracker.data)
                tracker: object | None = tracker.next
        if self.detail:
            return tabulate(stack, tablefmt="fancy_grid")
        else:
            return f"{stack}"

    def __len__(self: "_stack") -> int:
        return self.size

    def isEmpty(self: "_stack") -> bool:
        return not self.size

    def isFull(self: "_stack") -> bool:
        return self.size == self._capacity

    def top(
        self: "_stack",
    ) -> object:
        return self.peek()


class singlyLinkedStack(_stack):
    """Stack Using Static Non Circular Singly Linked List"""

    @property
    def stack(self: "singlyLinkedStack") -> singlyLinkedList:
        return self._stack

    @stack.setter
    def stack(
        self: "singlyLinkedStack",
        data: object,
    ) -> None:
        try:
            if len(data) > self._capacity:
                raise CapacityError(
                    "Capacity must be greater than or equal the len of data"
                )
            else:
                self._stack: singlyLinkedList = singlyLinkedList(detail=self.detail)
                for i in data:
                    if i is not None:
                        self._stack.prepend(i)
                self.size: int = len(self._stack)
        except TypeError as e2:
            if data is not None:
                self.stack: list = [data]
            else:
                self.stack: list = []

    def push(
        self: "singlyLinkedStack",
        data: object,
    ) -> None:
        if self.size != self._capacity:
            if data is not None:
                self._stack.prepend(data)
                self.size += 1
        else:
            raise StackOverflowError("Stack is full !")

    def pop(self: "singlyLinkedStack") -> None:
        if not self.size:
            raise StackUnderflowError("Stack is empty !")
        else:
            self.size -= 1
            return self._stack.pop(0)

    def peek(
        self: "singlyLinkedStack",
    ) -> object:
        if self.size:
            return self._stack._head.data
        else:
            raise StackUnderflowError("Stack is empty !")

    def clear(self: "singlyLinkedStack") -> None:
        if self.size:
            self._stack.clear()
            self.size: int = 0


class doublyLinkedStack(_stack):
    """Stack Using Static Non Circular Doubly Linked List"""

    @property
    def stack(self: "doublyLinkedStack") -> doublyLinkedList:
        return self._stack

    @stack.setter
    def stack(
        self: "doublyLinkedStack",
        data: object,
    ) -> None:
        try:
            if len(data) > self._capacity:
                raise CapacityError(
                    "Capacity must be greater than or equal the len of data"
                )
            else:
                self._stack: doublyLinkedList = doublyLinkedList(detail=self.detail)
                for i in data:
                    if i is not None:
                        self._stack.append(i)
                        self.size += 1
                for _ in range(self._capacity - self.size):
                    self._stack.append(None)
                self.push_index: object = self._stack._head
                for _ in range(self.size):
                    self.push_index: object | None = self.push_index.next
                self.pop_index: None | object = self.push_index.prev
        except TypeError as e3:
            if data is not None:
                self.stack: list = [data]
            else:
                self.stack: list = []
        except AttributeError as e4:
            self.pop_index: object = self._stack._tail

    def push(
        self: "doublyLinkedStack",
        data: object,
    ) -> None:
        if self.size != self._capacity:
            if data is not None:
                self.push_index.data = data
                self.size += 1
                self.push_index: object | None = self.push_index.next
                if self.pop_index is not None:
                    self.pop_index: object = self.pop_index.next
                else:
                    self.pop_index: object = self._stack._head
        else:
            raise StackOverflowError("Stack is full !")

    def pop(self: "doublyLinkedStack") -> None:
        if not self.size:
            raise StackUnderflowError("Stack is empty !")
        else:
            returned_value: object = self.pop_index.data
            self.pop_index.data = None
            self.size -= 1
            self.pop_index: object | None = self.pop_index.prev
            if self.push_index is None:
                self.push_index: object = self._stack._tail
            else:
                self.push_index: object = self.push_index.prev
            return returned_value

    def peek(
        self: "doublyLinkedStack",
    ) -> object:
        if self.pop_index is not None:
            return self.pop_index.data
        else:
            raise StackUnderflowError("Stack is empty !")

    def clear(self: "doublyLinkedStack") -> None:
        if self.size:
            self._stack.clear()
            self._stack *= self._capacity
            self.push_index: object = self._stack._head
            self.pop_index: None = None
            self.size: int = 0


def _main() -> None:
    print("lstack")


if __name__ == "__main__":
    _main()
