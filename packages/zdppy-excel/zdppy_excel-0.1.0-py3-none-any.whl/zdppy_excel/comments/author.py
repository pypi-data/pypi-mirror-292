# Copyright (c) 2010-2023 zdppy_excel


from zdppy_excel.descriptors.serialisable import Serialisable
from zdppy_excel.descriptors import (
    Sequence,
    Alias
)


class AuthorList(Serialisable):

    tagname = "authors"

    author = Sequence(expected_type=str)
    authors = Alias("author")

    def __init__(self,
                 author=(),
                ):
        self.author = author
