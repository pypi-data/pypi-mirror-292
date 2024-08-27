# Copyright (c) 2010-2023 zdppy_excel

from zdppy_excel.descriptors.serialisable import Serialisable
from zdppy_excel.descriptors.excel import Relation


class Drawing(Serialisable):

    tagname = "drawing"

    id = Relation()

    def __init__(self, id=None):
        self.id = id
