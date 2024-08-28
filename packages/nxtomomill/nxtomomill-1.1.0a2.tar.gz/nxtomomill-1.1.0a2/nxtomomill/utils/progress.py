# coding: utf-8

from __future__ import annotations
import sys


class Progress:
    """Simple interface for defining advancement on a 100 percentage base"""

    def __init__(self, name: str):
        self._name = name
        self._progress = 0
        self.set_name(name)

    def set_name(self, name):
        self._name = name
        self.reset()

    def reset(self, max_: int | None = None) -> None:
        r"""
        reset the advancement to n and max advancement to max\_
        :param max\_: max progress value
        """
        self._n_processed = 0
        self._max_processed = max_

    def start_process(self) -> None:
        self.set_advancement(0)

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, progress):
        progress = max(0, progress)
        progress = min(100, progress)
        self._progress = progress
        length = 20  # modify this to change the length
        block = int(round(length * progress / 100))
        blocks_str = "#" * block + "-" * (length - block)
        msg = f"\r{self._name}: [{blocks_str}] {round(progress, 2)}%"
        if progress >= 100:
            msg += " DONE\r\n"
        sys.stdout.write(msg)
        sys.stdout.flush()

    def set_advancement(self, value: int) -> None:
        """

        :param value: set advancement to value
        """
        self.progress = value

    def end_process(self) -> None:
        """Set advancement to 100 %"""
        self.set_advancement(100)

    def set_max_advancement(self, n: int) -> None:
        """

        :param n: number of steps contained by the advancement. When
            advancement reach this value, advancement will be 100 %
        """
        self._max_processed = n

    def increase_advancement(self, i: int = 1) -> None:
        """

        :param i: increase the advancement of n step
        """
        self._n_processed += i
        advancement = int(float(self._n_processed / self._max_processed) * 100)
        self.set_advancement(advancement)
