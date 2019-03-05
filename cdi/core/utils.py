from typing  import (Any, TypeVar,
                     List     as L,
                     Dict     as D,
                     Callable as C)
from abc       import ABCMeta,abstractmethod
from os        import environ
from copy      import deepcopy

################################################################################
T = TypeVar('T')
Fn = C[[Any],str] # type shortcut

class Base(object):
    @abstractmethod
    def __str__(self)->str:
        raise NotImplementedError
    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other : Any) -> bool:
        '''
        Maybe the below should be preferred? Try it out, sometime!
        return type(self) == type(other) and vars(self) == vars(other)
        '''
        if type(other) == type(self):
            return vars(self) == vars(other)
        else:
            args = [self,type(self),other,type(other)]
            raise ValueError('Equality type error \n{} \n({}) \n\n{} \n({})'.format(*args))

    def __lt__(self,other:object) -> bool:
        return str(self) < str(other)

    def __hash__(self) -> int:
        return hash(str(vars(self)))

    def copy(self : T) -> T:
        return deepcopy(self)

class Showable(Base,metaclass=ABCMeta):
    @abstractmethod
    def show(self,f:Fn)->str:
        """ Apply function recursively to fields """
        raise NotImplementedError

##############################################################
class Conn(Base):
    def __init__(self,host:str='127.0.0.1',port:int=3306,db:str='cql',user:str=None,pw:str=None)->None:
        self.host = host
        self.port = port
        self.db   = db
        self.user = user or environ['USER']
        self.pw   = pw   or environ['USER']

    def __str__(self)->str:
        return 'Conn<%s>'%(self.db)

    def jdbc(self, db : bool = True) -> str:
        dbstr = self.db if db else ''
        args = [self.host,self.port,dbstr,self.user,self.pw]
        return 'jdbc:mysql://{}:{}/{}?user={}&password={}'.format(*args)

##############################################################################
A = TypeVar('A'); B = TypeVar('B')

def flatten(lol: L[L[A]])->L[A]:
    """Convert list of lists to a single list via concatenation"""
    return [item for sublist in lol for item in sublist]

##############################################################
def merge_dicts(dicts: L[D[A, B]]) -> D[A, B]:
    return {k: v for d in dicts for k, v in d.items()}

def concat_map(f: C[[A], L[B]], args: L[A]) -> L[B]:
    """
    Maps a function over an input.
    We apply the function to every element in the list and concatenate result.
    """
    return flatten([f(arg) for arg in args])

##############################################################
