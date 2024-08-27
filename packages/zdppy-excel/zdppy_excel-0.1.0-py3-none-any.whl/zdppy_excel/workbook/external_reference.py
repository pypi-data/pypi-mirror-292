# Copyright (c) 2010-2023 zdppy_excel

from zdppy_excel.descriptors.serialisable import Serialisable
from zdppy_excel.descriptors import (
    Sequence
)
from zdppy_excel.descriptors.excel import (
    Relation,
)

class ExternalReference(Serialisable):

    tagname = "externalReference"

    id = Relation()

    def __init__(self, id):
        self.id = id
