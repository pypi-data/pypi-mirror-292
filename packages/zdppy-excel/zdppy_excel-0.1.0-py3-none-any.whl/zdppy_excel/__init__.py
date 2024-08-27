# Copyright (c) 2010-2023 zdppy_excel

DEBUG = False

from zdppy_excel.compat.numbers import NUMPY
from zdppy_excel.xml import DEFUSEDXML, LXML
from zdppy_excel.workbook import Workbook
from zdppy_excel.reader.excel import load_workbook as open
from zdppy_excel.reader.excel import load_workbook
import zdppy_excel._constants as constants

# Expose constants especially the version number

__author__ = constants.__author__
__author_email__ = constants.__author_email__
__license__ = constants.__license__
__maintainer_email__ = constants.__maintainer_email__
__url__ = constants.__url__
__version__ = constants.__version__
