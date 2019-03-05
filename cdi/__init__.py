from cdi.core.primitives  import JavaType,JavaConst
from cdi.core.cql         import (Migrate, Merge)

from cdi.core.expr import (Expr as SQLExpr, AND, IF, ELSE, Literal, MAX, One,
                                 COUNT, LEN, IN, GROUP_CONCAT, CONCAT, Literal, LT,
                                 ABS, SUM, NOT,REGEXP, BINARY, Sum, toDecimal, GT,
                                 NULL, MIN,COALESCE, LIKE, OR, EQUALS, NE, Zero,
                                 JSON_EXTRACT, REPLACE, CONVERT, R2, STD, AVG,
                                 SUBSELECT)

from cdi.core.utils      import Conn,merge_dicts, flatten


from cdi.core.exposed import (
    Schema, Entity, Attr, FK,PathEQ,Path,CQLExpr,
    JLit,EQ,Instance,
    JavaFunc, Land,NewEntity,NewAttr,NewFK,SQLAttr,Overlap,Gen,
    Int,Integer,Tinyint,Float,Varchar,Decimal,Text,Date,Double,String,Boolean,
    Long,Bigint)
