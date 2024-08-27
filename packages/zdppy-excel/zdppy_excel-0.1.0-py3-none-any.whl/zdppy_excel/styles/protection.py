# Copyright (c) 2010-2023 zdppy_excel

from zdppy_excel.descriptors import Bool
from zdppy_excel.descriptors.serialisable import Serialisable


class Protection(Serialisable):
    """Protection options for use in styles."""

    tagname = "protection"

    locked = Bool()
    hidden = Bool()

    def __init__(self, locked=True, hidden=False):
        self.locked = locked
        self.hidden = hidden
