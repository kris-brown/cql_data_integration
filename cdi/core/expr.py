# External Modules
from abc    import abstractmethod,ABCMeta
from typing import (Any,
                    List     as L,
                    Tuple    as T,
                    Callable as C)

from infix  import or_infix as pipe_infix # type: ignore
from copy   import deepcopy
from functools  import reduce
from operator   import add

# Internal Modules
from cdi.core.utils       import concat_map, Base,Showable,Fn
from cdi.core.primitives  import Type,FK as CQLFK, Attr as CQLAttr
"""
Python-sql interface
"""
###############################################################################

class Expr(Showable,metaclass = ABCMeta):
    '''SQL expression'''

    def __str__(self)->str:
        return self.show(str)
    def __repr__(self)->str:
        return 'Expr<%s>'%(str(self))

    # Abstract methods
    #-----------------
    @abstractmethod
    def fields(self)->list:
        """ List of immediate substructures of the expression (not recursive) """
        raise NotImplementedError

    #--------------------#
    # Overloaded methods #
    #--------------------#
    def __abs__(self)->'ABS':                  return ABS(self)
    def __add__(self, other:'Expr')->'PLUS':  return PLUS(self,other)
    def __mul__(self, other:'Expr')->'MUL':   return MUL(self,other)
    def __pow__(self, other:'Expr')->'POW':   return POW(self,other)
    def __sub__(self, other:'Expr')->'MINUS': return MINUS(self,other)
    def __or__(self,other : Any)->Any: raise NotImplementedError
    del __or__  # tricking the type checker to use |Infix|
    def __truediv__(self, other:'Expr')->'DIV':   return DIV(self,other)

################################################################################

##############
# Subclasses #
##############

class Unary(Expr):
    """
    Expression that depends on just one individual thing
    """
    # Input-indepedent parameters
    #----------------------------
    @property
    @abstractmethod
    def name(self)->str: raise NotImplementedError

    # Implement Expr abstract methods
    #--------------------------------
    def fields(self)->list:
        return [self.x]

    def show(self, f : Fn) -> str:
        x = f(self.x)
        return '%s(%s)' % (self.name, x)

    # Class-specific init
    #-------------------
    def __init__(self, x : Expr) -> None:
        self.x = x

class Binary(Expr):
    """
    Expression that depends on two individual things
    """

    # Input-indepedent parameters
    #----------------------------
    @property
    @abstractmethod
    def name(self) -> str: raise NotImplementedError

    infix = True

    # Implement Expr abstract methods
    #--------------------------------
    def fields(self) -> list:
        return [self.x,self.y]

    def show(self, f : Fn) -> str:
        x,y = f(self.x), f(self.y)
        if self.infix:
            return '(%s %s %s)'%(x,self.name,y)
        else:
            return '%s(%s,%s)'%(self.name,x,y)

    # Class-specific init
    #-------------------
    def __init__(self,x:Expr,y:Expr)->None:
        self.x,self.y = x,y

class Ternary(Expr):
    """
    Expression that depends on three individual things
    """
    # Input-indepedent parameters
    #----------------------------
    @property
    @abstractmethod
    def name(self) -> str: raise NotImplementedError
    # Implement Expr abstract methods
    #--------------------------------
    def fields(self) -> list:
        return [self.x,self.y,self.z]

    def show(self, f : Fn) -> str:
        x,y,z = f(self.x), f(self.y), f(self.z)
        return '%s(%s,%s,%s)'%(self.name,x,y,z)

    # Class-specific init
    #-------------------
    def __init__(self,x:Expr,y:Expr,z:Expr) -> None:
        self.x,self.y,self.z = x,y,z

class Nary(Expr):
    """
    SQL Functions that take multiple arguments, initialized by user with
    multiple inputs (i.e. not a single list input)
    """
    # Input-indepedent parameters
    #----------------------------
    @property
    @abstractmethod
    def name(self) -> str: raise NotImplementedError

    @property
    def delim(self) -> str: return ',' # default delimiter

    def fields(self) -> list:
        return self.xs

    def __init__(self, *xs : Expr) -> None:
        self.xs  = list(xs)

    def show(self, f : Fn) -> str:
        xs = map(f,self.xs)
        d  = ' %s '%self.delim
        return '%s(%s)'%(self.name,d.join(xs))

class Named(Expr):
    """
    Inherit from this to allow any arbitrary class, e.g. XYZ(object),
     to automatically deduce that its 'name' property should be 'XYZ'
    """
    @property
    def name(self)->str:
        return type(self).__name__

class Agg(Unary):
    """
    This class is meant to be inherited by any SQL function we want to flag
    as an aggregation.

    We can optionally specify what objects we want to aggregate over, otherwise
    the intent will be guessed
    """

    def __init__(self, x : Expr, objs : list = None) -> None:
        assert issubclass(type(x),Expr)
        self.x    = x
        self.objs = objs or []



################################################################################
# Specific Expr classes for user interface
###########################################

# Ones that work out of the box
#------------------------------
class ABS(Named,Unary):     pass
class SQRT(Named,Unary):    pass
class MAX(Named,Agg,Unary): pass
class SUM(Named,Agg,Unary): pass
class MIN(Named,Agg,Unary): pass
class AVG(Named,Agg,Unary): pass
class STD(Named,Agg,Unary): pass
class COUNT(Agg,Named,Unary): pass
class CONCAT(Named,Nary):     pass
class BINARY(Named,Unary):    pass  # haha
class REGEXP(Named,Binary):   pass
class REPLACE(Named,Ternary): pass
class COALESCE(Named,Nary):   pass
class GROUP_CONCAT(Named,Agg,Nary): pass

@pipe_infix
class LIKE(Named,Binary):   pass

# Ones that need a field defined
#-------------------------------
class LEN(Unary):     name = 'CHAR_LENGTH'
class MUL(Binary):    name = '*'
class DIV(Binary):    name = '/'
class PLUS(Binary):   name = '+'
class MINUS(Binary):  name = '-'
class POW(Named,Binary):          infix = False
class JSON_EXTRACT(Named,Binary): infix = False


@pipe_infix
class EQUALS(Binary): name = '='
@pipe_infix
class NE(Binary): name = '!='
@pipe_infix
class LT(Binary):     name = '<'
@pipe_infix
class GT(Binary):     name = '>'
@pipe_infix
class LE(Binary):     name = '<='
@pipe_infix
class GE(Binary):     name = '>='

@pipe_infix
class OR(Nary):
    """ Can be used as a binary operator (|OR|) or as a function OR(a,b,...)"""
    name  = ''
    delim = 'OR'

@pipe_infix
class AND(Nary):
    name  = ''
    delim = 'AND'

class And(Nary):
    name  = ''
    delim = 'AND'

class NOT(Named,Unary):
    wrap = False

class NULL(Named,Unary):
    def show(self, f : Fn) -> str:
        return "%s is NULL"%f(self.x)

# Ones that need to be implemented from scratch
#----------------------------------------------

class Literal(Expr):
    '''Integers/Strings/Decimals etc'''
    def __init__(self,x : Any)->None:
        self.x = x

    def fields(self)-> L[Expr]: return []

    def show(self, _ : Fn) -> str:
        if isinstance(self.x,str):
            return "('%s')"%self.x.replace("'","\\'").replace('%','%%')
        else:
            return '(%s)' % str(self.x)

@pipe_infix
class IN(Named):
    def __init__(self,x:Expr,xs:L[Expr])->None:
        self.x   = x
        self.xs  = xs

    def fields(self)->list:
        return [self.x]+self.xs

    def show(self,f:Fn)->str:
        xs = map(f,self.xs)
        return '%s IN (%s)'%(f(self.x),','.join(xs))

##########
# IF_ELSE is *not* for public use; rather:  <Ex1> |IF| <Ex2> |ELSE| <Ex3>
class IF_ELSE(Expr):
    def __init__(self,cond:Expr,_if:Expr,other:Expr)->None:
        self.cond = cond
        self._if = _if
        self._else = other

    def fields(self)->L[Expr]:
        return [self.cond,self._if,self._else]
    def show(self,f:Fn)->str:
        c,i,e = map(f,self.fields())
        return 'IF(%s,%s,%s)'%(c,i,e)

@pipe_infix
def IF(outcome:Expr,condition:Expr)->T[Expr,Expr]:
    return (outcome,condition)

@pipe_infix
def ELSE(ifpair : T[Expr,Expr], other : Expr) -> IF_ELSE:
    return IF_ELSE(ifpair[1],ifpair[0],other)

class CONVERT(Expr):
    def __init__(self, expr : Expr, dtype : str) -> None:
        self.expr = expr
        self.dtype = dtype

        err = 'Are you SURE that MySQL can convert to this dtype? %s'
        assert dtype.lower() in ['decimal','varchar'], err%dtype

    def fields(self) -> L[Expr]:
        return [self.expr]

    def show(self,f:Fn) -> str:
        e = f(self.expr)
        return 'CONVERT(%s,%s)'%(e,self.dtype)

class SUBSELECT(Expr):
    '''Hacky way of getting in subselect .... will not automatically detect
        dependencies'''
    def __init__(self,expr : Expr, tab : str, where : str = '1') -> None:
        self.expr = expr
        self.tab  = tab
        self.where= where

    def fields(self) -> L[Expr]:
        return [self.expr]

    def show(self,f:Fn) -> str:
        e = f(self.expr)
        return '(SELECT %s FROM %s WHERE %s )'%(e,self.tab,self.where)

############################
# Specific Exprs and Funcs #
############################

Zero = Literal(0)
One  = Literal(1)

def Sum(iterable : L[Expr])-> Expr:
    '''The Python builtin 'sum' function doesn't play with non-integers'''
    return reduce(add, iterable, Zero)

def R2(e1 : Expr, e2 : Expr) -> Expr:
    '''
    Pearson correlation coefficient for two independent vars
    "Goodness of fit" for a model y=x, valued between 0 and 1
    '''
    return (AVG(e1*e2)-(AVG(e1)*AVG(e2))) / (STD(e1) * STD(e2))

def toDecimal(e : Expr) -> Expr:
    return CONVERT(e,'Decimal')
