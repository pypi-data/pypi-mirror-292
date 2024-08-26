from sqlalchemy.sql.sqltypes import *



class TINYINT(SmallInteger):

    __visit_name__ = 'TINYINT'


class STRUCT(JSON):

    __visit_name__ = 'STRUCT'


class DOUBLE(Float):

    __visit_name__ = 'DOUBLE'

