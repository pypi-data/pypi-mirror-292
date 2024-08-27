# Copyright (c) 2010-2023 zdppy_excel

from zdppy_excel.xml.constants import CHART_NS

from zdppy_excel.descriptors.serialisable import Serialisable
from zdppy_excel.descriptors.excel import Relation


class ChartRelation(Serialisable):

    tagname = "chart"
    namespace = CHART_NS

    id = Relation()

    def __init__(self, id):
        self.id = id
