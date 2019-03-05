from cdi import (
    JavaFunc, JavaType,JavaConst,Decimal,Float,String,Boolean,Integer,Double,
    Text,Varchar,Long,Bigint)
################################################################################

# Other java data types possible, though not needed in this demo
# longtype  = JavaType('Long','java.lang.Long')
# longconst = JavaConst('Long','return input[0]')

#######################################
# Custom Functions for use within CQL #
#######################################
bigint_to_int = JavaFunc('bigint_to_int',
                        [Bigint],Integer,
                        'return  input[0].intValue();')

dec_to_float = JavaFunc('decimal_to_float',
                        [Decimal],
                        Float,
                        'return input[0].floatValue()')

matches     = JavaFunc('matches',
                       [String,String],
                       Boolean,
                       "return input[0].matches(input[1])")

cat         = JavaFunc('cat',
                       [String,String],
                       String,
                       "return input[0] + input[1]")

countsubstr = JavaFunc('countsubstr',
                       [String,String],
                       Integer,
                       "return input[0].split(input[1], -1).length-1")

gt          = JavaFunc('gt',
                       [Integer,Integer],
                       Boolean,
                       "return input[0] > input[1]")

gteq        = JavaFunc('gteq',
                       [Double,Double],
                       Boolean,
                       "return input[0] >= input[1]")

mcd         = JavaFunc('makeCompositionDict',[String],String,
                        """var CD = Java.type(\\"str_utils.makeCompositionDict\\"); return CD.run(input[0]);""")

msj         = JavaFunc('makeStructJSON',
                       [String]*4+[Double]*9,
                       Text,
                        """var MS = Java.type(\\"str_utils.makeStructJSON\\"); return MS.run(%s); """%(','.join(['input[%d]'%i for i in range(13)])))

funcs = [bigint_to_int,dec_to_float, matches, cat, countsubstr, gt, mcd, msj,gteq]
