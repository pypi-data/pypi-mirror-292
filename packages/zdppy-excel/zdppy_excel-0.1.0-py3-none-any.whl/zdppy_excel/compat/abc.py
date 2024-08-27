# Copyright (c) 2010-2023 zdppy_excel


try:
    from abc import ABC
except ImportError:
    from abc import ABCMeta
    ABC = ABCMeta('ABC', (object, ), {})
