# External
from typing import (Any, TYPE_CHECKING,
                    Set      as S,
                    List     as L,
                    Dict     as D,
                    Tuple    as T,
                    Union    as U,
                    Optional as O,
                    Iterator as I,
                    Callable as C)
from abc import ABCMeta,abstractmethod
from itertools import chain

# Internal
if TYPE_CHECKING:
    from cdi.core.exposed import JavaFunc

from cdi.core.utils      import Base, Conn, flatten
from cdi.core.expr       import Expr as SQLExpr,Fn,Literal # FK as ExprFK, Attr as ExprAttr,
from cdi.core.primitives import (Type,Attr as CQLAttr, FK as CQLFK,
    Entity as CQLEntity, Gen as CQLGen,
    Constraint,Expr as CQLExpr,
    LandInstance,QueryObj,
    Schema as CQLSchema,Typeside,
    PathEQ as CQLPEQ,EQ as CQLEQ, Path as CQLPath, ObsEQ as CQLOEQ,
    Constraints,
    JavaFunc as CQLFunc,ExprFunc as CQLExprFunc,
    GenAttr as CQLGenAttr,
    JLit as CQLJLit, Quotient, Instance,
    SchemaColimitQuotient,SchemaColimitModify)
'''
"2nd" level of representation, in between user-exposed constructors and low-level
CQL primitives. Classes in this file should contain most of the 'business logic'.
'''
################################################################################
class Rewrite(Base):
    '''Data structure for determining whether an attribute/FK should be renamed
    after a schema colimit'''
    def __init__(self,ents:D[str,T[str,S[str]]]=None)->None:
        self.ents  = ents  or {}

    def __str__(self) -> str: return 'Rewrite(%d ents)'%len(self.ents)

    def __call__(self,ent:str,attr:str=None)->str:
        '''Prefix attr/fk name with modelname only if there is a collision'''
        # Case 1: renaming an entity
        if not attr:
            return self.ents[ent][0] if ent in self.ents else ent
        # Case 2: renaming an attribute
        elif ((ent not in self.ents)
            or (attr not in self.ents[ent][1])):
            return attr
        else:
            return ent + '_' + attr

class Attr(Base):
    '''Internal representation of an entity's attribute'''
    def __init__(self,
                 name   : str,
                 obj    : str,
                 dtype  : Type,
                 id     : bool
                ) -> None:
        self.name  = name
        self.obj   = obj
        self.dtype = dtype
        self.id    = id

    def __str__(self) -> str: return self.name

    def attr(self,rewrite:Rewrite=None) -> CQLAttr:
        r = rewrite or Rewrite()
        return CQLAttr(r(self.obj,self.name),r(self.obj),self.dtype.name)

    def genattr(self) -> 'CQLGenAttr':
        g = CQLGen(self.obj,self.obj)
        return CQLGenAttr(self.name,self.dtype.name,g)

    def path(self) -> 'Path':
        '''A length-1 path of the attribute'''
        return Path(self.obj,[self])

class FK(Base):
    ''' Foreign key which knows src and target'''
    def __init__(self,
                 name : str,
                 src  : str,
                 tar  : str,
                 id   : bool
                ) -> None:
        self.name = name
        self.src  = src
        self.tar  = tar
        self.id   = id

    def __str__(self) -> str:
        return 'FK<%s>'%self.name

    def fk(self, rewrite:Rewrite=None) -> CQLFK:
        r = rewrite or Rewrite()
        return CQLFK(r(self.src,self.name),r(self.src),self.tar)

    def path(self) -> 'Path':
        return Path(self.src,[self])

class Entity(Base):
    '''Internal representation of an entity'''
    def __init__(self,
                 name   : str,
                 attrs  : D[str,Attr],
                 fks    : D[str,FK],
                 id     : Attr = None
                 ) -> None:
        self.name  = name
        self.id    = id
        self.attrs = attrs
        self.fks   = fks

    def __str__(self)->str:
        return 'Entity<%s>'%self.name

    @property
    def ids(self) -> L[str]:
        '''Names of all identifying attributes / relations'''
        return [an for an,a in self.attrs.items() if a.id] \
              + [fn for fn,f in self.fks.items() if f.id]

    def ent(self,
            uid     : bool        = False,
            fks     : U[bool,str] = True
            ) -> CQLEntity:
        '''
        Create an Entity from primitives.py

        - Optionally add an extra attribute "uid :: String"
        - Optionally include all FKs as pseudo-attributes (type String)
        - Optionally do not represent the FKs at all.
        '''
        s = "String"
        a = [CQLAttr(a.name,self.name,a.dtype.name) for a in self.attrs.values()] \
            + ([CQLAttr(f,self.name,s) for f in self.fks] if fks is 'attr' else [])\
            + ([CQLAttr('uid',self.name,s)] if uid else[])
        f = [CQLFK(f.name,self.name,f.tar) for f in self.fks.values()]
        return CQLEntity(self.name,a,f if fks is True else [])

    def fk_constraints(self) -> L[Constraint]:
        '''Constraints that enforce the FK relations, to be used in an CQL chase'''
        g1,g2 = [CQLGen(x,self.name) for x in ['x0','x1']]
        s    = 'where x0.uid=x1.uid -> where x0=x1'
        out  = Constraint([g1,g2],s.format(self.name))
        s2   = '-> exists unique y0:{1} where x0.{2}=y0.uid'
        out2 = [Constraint([g1],s2.format(self.name,fk.tar,fk.name))
                    for fkn,fk in self.fks.items()]
        return [out] + out2

class Gen(Base):
    '''
    A generator for some entity, to be used in CQL expressions
    '''
    def __init__(self, name : str, ent : Entity) -> None:
        self.name  = name
        self.ent   = ent

    def __str__(self)->str:
        return 'Gen<%s:%s>'%(self.name,self.ent.name)

    def gen(self)->CQLGen:
        return CQLGen(self.name,self.ent.name)


class UserExposedCQLExpr(Base, metaclass = ABCMeta):
    '''
    Class of expressions which can occur in CQL
    (combination of paths and java function applications)

    For unclear and complicated reasons, this user-exposed level class needs to
    be in this file....
    '''
    @abstractmethod
    def mk_expr(self)->'Expr':
        raise NotImplementedError

class Expr(UserExposedCQLExpr,metaclass=ABCMeta):
    ''''CQL Expression'''
    @abstractmethod
    def gens(self)->L[Gen]: raise NotImplementedError

    @abstractmethod
    def expr(self,schema:'Schema')->CQLExpr: raise NotImplementedError

    def mk_expr(self)->'Expr': return self


class Ref(Expr,SQLExpr):
    '''Refer to an attribute/fk but do not yet check if it actually exists
        Useful when working with attributes that will exist later '''
    def __init__(self,objname:str,attrname:str)->None:
        self.obj  = objname
        self.attr = attrname

    def __str__(self)->str:
        return 'Ref<%s.%s>'%(self.obj,self.attr)

    def fields(self)->list: return []

    def show(self, _ : Fn) -> str: return self.attr

    def realize(self,schema:'Schema') -> U['Attr','FK']:
        '''Turn reference into a real Attr/FK '''
        o = schema[self.obj]
        if   self.attr in o.attrs: return o.attrs[self.attr]
        elif self.attr in o.fks: return o.fks[self.attr]
        else: raise ValueError(o,self,' not in ',set(o.attrs)|set(o.fks))

    def gens(self)->L[Gen]: return []

    def expr(self, s : 'Schema')->CQLExpr:
        a = self.realize(s)
        if   isinstance(a,Attr):  dtype = a.dtype.name
        elif isinstance(a,FK):    dtype = a.tar
        else:                     raise TypeError
        g = CQLGen(self.obj,self.obj)
        return CQLGenAttr(self.attr,dtype,g)

    def func(self,arg : Expr)->'ExprFunc':
        from cdi.core.exposed import JavaFunc,DType # need to make analogous classes in this file...
        f = JavaFunc(self.attr,[],DType('?'),'')
        return ExprFunc(f,[arg])

class GenAttr(Expr):
    '''
    Internal representation of an entity's attribute
    '''
    def __init__(self,
                 name   : str,
                 gen    : Gen,
                ) -> None:
        self.name  = name
        self.gen   = gen

    def __str__(self)->str: return self.name
    def gens(self)->L[Gen]: return [self.gen]
    def expr(self,schema:'Schema')->CQLExpr:
        en = self.gen.ent.name
        assert en in schema, 'Cannot find entity %s in %s'%(en,schema.entities)
        ent = schema[en]
        assert self.name in ent.attrs or self.name in ent.fks, '%s cannot find attribute %s in %s /// %s'%(self.gen,self.name,ent.attrs,ent.fks)
        if self.name in ent.attrs:
            dt  = ent.attrs[self.name].dtype.name
        else:
            dt = ent.fks[self.name].tar
        return CQLGenAttr(self.name,dt,self.gen.gen())
    def mk_expr(self)->Expr: return self

class JLit(Expr):
    ''' A java literal '''
    def __init__(self, val : Any, dtype : Type) -> None:
        self.val    = val
        self._dtype = dtype

    def __str__(self) -> str:
        return str(self.val)

    def expr(self,_:'Schema') -> CQLExpr:
        return self.jlit()

    def gens(self) -> L[Gen]: return []

    def jlit(self) -> CQLJLit:
        return CQLJLit(str(self.val),self._dtype.name)

    def mk_expr(self)->Expr: return self

class Path(Expr):
    '''
    A sequence of FKs followed by an attr, or a java literal
    (maybe this could be more elegantly achieved by making JLit a subclass)
    '''
    def __init__(self,start:str, xs : L[U[FK,Attr,JLit]]) -> None:
        assert xs, 'No such thing as empty path'
        self.xs = xs
        self.start = start
        if isinstance(xs[0],JLit): assert len(xs)==1

    def __str__(self) -> str:
        return ' . '.join(map(str,self.xs))#self.show(str)

    def dtype(self) -> str:
        raise NotImplementedError

    def show(self, f : Fn) -> str:
        return ' . '.join(map(f,self.xs))

    def gens(self)->L[Gen]: return []

    def expr(self, schema:'Schema') -> CQLExpr: return self.path()

    def mk_expr(self)->Expr: return self

    def path(self,rewrite:Rewrite=None)->CQLPath:
        xs = [] # type: L[U[CQLAttr,CQLFK,CQLJLit,CQLGenAttr]]
        for x in self.xs:
            if   isinstance(x,FK):      xs.append(x.fk(rewrite=rewrite))
            elif isinstance(x,Attr):    xs.append(x.attr(rewrite=rewrite))
            elif isinstance(x,JLit):    xs.append(x.jlit())
            elif isinstance(x,GenAttr): xs.append(x.genattr())
        return CQLPath(xs)

    def exists_in(self,schema:'Schema')->bool:
        '''Determine if the path can exist within a schema'''
        for x in self.xs:
            if isinstance(x,FK):
                if x not in schema[x.src].fks.values(): return False
            elif isinstance(x,Attr):
                if x not in schema[x.obj].attrs.values(): return False
        return True

class PathEQ(Base):
    '''Container of two paths, expressing their equality'''
    def __init__(self, p1 : Path, p2 : Path) -> None:
        self.p1, self.p2 = p1, p2

    def __str__(self) -> str:
        return 'PathEQ<%s|%s>'%(self.p1,self.p2)

    def __iter__(self)->I[Path]:
        return iter([self.p1,self.p2])

    def patheq(self,rewrite:Rewrite=None) -> CQLPEQ:
        return CQLPEQ(self.p1.path(rewrite),self.p2.path())

    def exists_in(self,schema:'Schema')->bool:
        return all([p.exists_in(schema) for p in self])

class ObsEQ(Base):
    '''Container for two expressions, expressing their equality'''
    def __init__(self, s : 'Schema', e1 : Expr, e2 : Expr) -> None:
        self.e1,self.e2,self.s = e1,e2,s

    def __str__(self)->str:
        return 'ObsEQ<%s|%s>'%(self.e1,self.e2)

    def obseq(self) -> CQLOEQ:
        gs = [g.gen() for g in set(self.e1.gens() + self.e2.gens())]

        return CQLOEQ(self.e1.expr(self.s),self.e2.expr(self.s),gs)

class Schema(Base):
    '''Internal representation a schema'''
    def __init__(self,
                 name     : str,
                 entities : L[Entity]   = None,
                 pes      : L[PathEQ]   = None,
                 oes      : L[ObsEQ]    = None
                 ) -> None:
        self.name     = name
        self.entities = {e.name:e for e in entities or []}
        self.pes      = set(pes or [])
        self.oes      = set(oes or [])

    def __str__(self)->str:
        return 'Schema<%s,%d entities, %d pathEQs>'%(self.name,len(self.entities),len(self.pes))

    def __getitem__(self, key : str) -> Entity:
        return self.entities[key]

    def __contains__(self,key : str) -> bool:
        return key in self.entities

    def get(self, objname : str) -> Entity:
        '''Get an object by name'''
        return self[objname]

    @property
    def cql_entities(self)->D[str,CQLEntity]:
        return {k:v.ent() for k,v in self.entities.items()}

    def schema(self,
               name : str,
               ty   : Typeside,
               imp  : L[CQLSchema] = None,
               uid  : bool         = False,
               fks  : U[bool,str]  = True,
               pe   : bool         = True
               ) -> CQLSchema:
        e   = [e.ent(uid,fks) for e in self.entities.values()]
        pes = [peq.patheq() for peq in self.pes if pe]
        oes = [peq.obseq() for peq in self.oes if pe]
        return CQLSchema(name=name,typeside=ty.name,imports=imp,entities=e,pes=pes,oes=oes)

    def fk_constraints(self,name:str,schema:'CQLSchema')->Constraints:
        cons = flatten([e.fk_constraints() for e in self.entities.values()])

        return Constraints(name=name,schema=schema,cons=cons)

    def quotient(self,name:str,inst:Instance)->Quotient:
        ents = {en:e.ids for en,e in self.entities.items()}
        return Quotient(name,inst,ents)


class ExprFunc(Expr):
    '''Representing a function called on some arguments'''
    def __init__(self,func:'JavaFunc',args:L[Expr])->None:
        self.func = func
        self.args = args
    def __str__(self)->str:
        return '%s(%s)'%(self.func.name,','.join(map(str,self.args)))

    def gens(self)->L[Gen]:
        return flatten([a.gens() for a in self.args])
    def expr(self,schema:Schema)->CQLExpr:
        return CQLExprFunc(self.func.javafunc(),[e.expr(schema) for e in self.args])
    def mk_expr(self)->Expr: return self

class LandObj(Base):
    '''
    High-level specification of how a particular entity should be landed
    src    - entity being landed
    consts - attributes to be created upon landing
    where  - constraint on which records are landed
    #id     - specify what to use ID column (IMPORTANT that this is what other
    #         tables are referring to in the FKs to this entity)
    '''
    def __init__(self,
                 src    : Entity,
                 consts : D[Attr,SQLExpr] = None,
                 where  : SQLExpr = None,
                ) -> None:
        self.src    = src
        self.consts = consts
        self.where  = where

    def __str__(self)->str:
        return 'LandObj<%s>'%self.src.name

class Land(Base):
    '''Higher level of abstraction than the primitive jdbc_instance - exposed to user'''
    def __init__(self, schema : Schema, ents : L[LandObj] = None) -> None:
        self.schema = schema
        self.ents   = {e.src : e for e in ents or []}

    def __str__(self)->str:
        return 'Land<%s>'%self.schema.name

    def inst(self, name : str, schema : CQLSchema, conn : Conn) -> LandInstance:
        ents = {e.ent():self.makeSQL(e,self.ents.get(e,LandObj(e))) for e in self.schema.entities.values()}
        return LandInstance(name,conn,schema,ents)

    @staticmethod
    def makeSQL(e : Entity, lo : LandObj) -> str:
        '''Construct a SQL statement which lands data for an entity into CQL'''

        # General template
        land = '\n\t\t"SELECT {id} AS `id`, CONVERT({id},CHAR(50)) AS `uid`'\
               '{cols} \n\n\t\t'\
               'FROM {name} \n\t\t'\
               'WHERE {cons}"'


        def showFunc(x : Any) -> str:
            '''Custom representation of attributes AND custom escape rules, given
            that this is appearing within CQL's double quotes'''

            if   isinstance(x,Ref): return '`%s`'%x.attr
            elif isinstance(x,Literal):
                s = x.x
                if isinstance(s,str):
                    s = s.replace('%','%%')
                    sing,doub = "'" in s, '"' in s
                    assert not (sing and doub), "Don't know how to handle a string w/ both single and double quotes: "+s
                    if sing: return '(\\"%s\\")'%s#%s.replace("'","\\'")
                    else:    return "('%s')"%s.replace('"','\\"')
                else:                   return '(%s)' % str(s)
            elif isinstance(x,SQLExpr): return x.show(showFunc)
            else:
                raise TypeError(x,type(x))

        idcol  = e.id
        consts = lo.consts or {}

        # String constants
        com      = ',\n\t\t\t'
        astr     = com+'`{0}`{1} AS `{0}`'
        addstr   = com+'{0}{1} AS `{2}`'

        ''' Note about the odd business of landing foreign key values:

        We just want the FK value as a raw string

        If it is NULL, construct value that will (almost certainly)
        NOT refer to record in target table NOR will be the same
        as the value from any other record in this table which also
        has a NULL FK here. CQL will create a unique NULL record for
        the target of this FK, which is our desired semantics (we
        know something exists, but nothing about it)
        '''

        fstr     = com+"COALESCE(CONVERT(`{name}`,CHAR(250))"+com+\
                   "         CONCAT('{obj}.{name}$',CONVERT({id},CHAR(250))))"\
                   "\n\t\t\t    AS `{name}`"

        # Main component of landing an obje ct
        ats      = [astr.format(n,'+0E0' if a.dtype.name in ['Decimal','Double'] else '')
                        for n,a in e.attrs.items() ] # if a not in add_]

        fknames  = [fk for fk in e.fks]
        fks      = [fstr.format(name=fk,obj=e.name,id=idcol) for fk in fknames]

        addcols  = [addstr.format(e.show(showFunc),'+0E0' if a.dtype.name == 'Double' else '',a.name)
                       for a,e in consts.items()]

        cols     = ''.join(ats+  addcols + fks)


        cons     = lo.where.show(showFunc) if lo.where else '1'

        return land.format(name=e.name,id=idcol,cols=cols,cons=cons)

class EQ(Base):
    '''Expression equality, found in the WHERE clause of CQL uber flower queries'''
    def __init__(self, e1 : Expr, e2 : Expr) -> None:
        self.e1 = e1
        self.e2 = e2
    def __str__(self) -> str:
        return 'ExprEQ<%s = %s>'%(self.e1,self.e2)

    def eq(self,schema:Schema) -> CQLEQ:
        return CQLEQ(self.e1.expr(schema),self.e2.expr(schema))

class New(Base,metaclass=ABCMeta):
    @abstractmethod
    def add(self,s:'Schema') -> None:
        '''Modifies a schema by adding itself'''
        raise NotImplementedError

class SQLAttr(New):
    '''Create a new attribute during landing data from SQL using a SQL expression'''
    def __init__(self,ent:str,attr:Attr,expr:SQLExpr) -> None:
        self.ent  = ent
        self.attr = attr
        self.expr = expr

    def __str__(self)->str:
        return 'SQLAttr<%s.%s>'%(self.ent,self.attr.name)

    def add(self,s:'Schema') -> None:
        assert self.ent in s
        s[self.ent].attrs[self.attr.name] = self.attr

class NewAttr(New):
    '''Create a new attribute during an CQL query'''
    def __init__(self, ent:Entity, attr:str,dtype:Type,expr:Expr)->None:
        self.ent  = ent
        self.attr = Attr(attr,ent.name,dtype,id=False)
        self.expr = expr

    def __str__(self)->str:
        return 'NewAttr<%s.%s>'%(self.ent.name,self.attr)

    @property
    def gens(self)->L[Gen]:
        return self.expr.gens()

    def add(self,s:'Schema')->None:
        assert self.ent.name in s, '%s not in %s'%(self.ent,s.entities.keys())
        s[self.ent.name].attrs[self.attr.name] = self.attr

class NewFK(New):
    '''Create a new FK during an CQL query for an existing object...might be buggy'''
    def __init__(self, ent : Entity, fk : FK, gen : Gen) -> None:
        self.ent  = ent
        self.fk   = fk
        self.gen  = gen

    def __str__(self)->str:
        return 'NewFK<%s.%s>'%(self.ent.name,self.fk)

    def add(self,s:'Schema')->None:
        assert self.ent.name in s, '%s not in %s'%(self.ent,s.entities.keys())
        s[self.ent.name].fks[self.fk.name] = self.fk

class NewEntity(New):
    '''Construct an entirely new object from an CQL query'''
    def __init__(self,
                 ent    : Entity,
                 gens   : L[Gen],
                 attrs  : D[str,Expr] = None,
                 fks    : D[FK,Gen]   = None,
                 where  : L[EQ]       = None,
                 ) -> None:

        self.ent   = ent
        self.gens  = gens
        self.where = where or []
        self.attrs = attrs or {}
        self.fks   = fks   or {}

    def __str__(self)->str:
        return 'NewEntity<%s>'%self.ent.name

    def add(self,s:'Schema')->None:
        assert self.ent.name not in s
        s.entities[self.ent.name] = self.ent

    def qobj(self,fullschema : Schema)->QueryObj:
        return QueryObj(ent  = self.ent.name,
                        gens = [g.gen() for g in self.gens],
                        where = [e.eq(fullschema) for e in self.where],
                        attrs = {a:e.expr(fullschema) for a,e in self.attrs.items()},
                        fks   = {k.name:{k.tar:v.name} for k,v in self.fks.items()})
class Overlap(Base):
    '''
    Overlap between two schemas, specified in three ways.
        -  Path Equalities (the starts of the paths are identified with each other)
        -  "New" entities/attributes (where the new thing exists in the other schema)
    Not supported: equating entities which have NO path equalities (not necessary?)
    '''
    def __init__(self,
                 s1         : Schema,
                 s2         : Schema,
                 patheqs    : L[PathEQ]   = None,
                 sa1        : L[SQLAttr]  = None,
                 na1        : L[NewAttr]  = None,
                 ne1        : L[NewEntity]= None,
                 nf1        : L[NewFK]    = None,
                 sa2        : L[SQLAttr]  = None,
                 na2        : L[NewAttr]  = None,
                 ne2        : L[NewEntity]= None,
                 nf2        : L[NewFK]    = None,
                )->None:
        self.s1, self.s2 = s1, s2
        self.patheqs  = {p.p1:p.p2 for p in patheqs or []}
        self.na1      = set(na1 or [])
        self.ne1      = {ne.ent.name:ne for ne in ne1 or []}
        self.sa1      = set(sa1 or [])
        self.na2      = set(na2 or [])
        self.ne2      = {ne.ent.name:ne for ne in ne2 or []}
        self.sa2      = set(sa2 or [])
        self.nf1      = set(nf1 or [])
        self.nf2      = set(nf2 or [])

        # Make sure the type of the CQL expr output matches the new attribute
        for nas,schema in [(self.na1,self.s1),(self.na2,self.s2)]:
            for na in nas:
                t1,t2 = na.attr.dtype.name, na.expr.expr(schema).dtype
                assert t1 == t2, (na,'"New Attribute" type error: ',t1,t2)

        self.entities = {} # type: D[str,str]

        for p1,p2 in self.patheqs.items():
            start1,start2 = [p1.start,p2.start]
            if start1:
                assert start2
                self.entities[start1] = start2

        self.patheqs_simple = {p1.xs[0]:p2 for p1,p2 in self.patheqs.items()
                                if len(p1.xs) == 1}

        for n in self.new1():
            if isinstance(n,NewEntity):
                self.ne1[n.ent.name] = n
                for a in n.ent.attrs.values():
                    self.patheqs_simple[a] = a.path()
                for fk in n.ent.fks.values():
                    self.patheqs_simple[fk] = fk.path()
            elif isinstance(n,NewAttr):
                self.patheqs_simple[n.attr] = n.attr.path()
            elif isinstance(n,NewFK):
                self.patheqs_simple[n.fk] = n.fk.path()

    def __str__(self)->str:
        return 'Overlap<%s|%s>'%(self.s1.name,self.s2.name)

    def __contains__(self, objname : str) -> bool:
        return objname in self.entities

    def new1(self) -> S[New]:
        return set(self.ne1.values()) | self.na1 | self.nf1

    def new2(self) -> S[New]:
        return set(self.ne2.values()) | self.na2  | self.nf2

    def add_sql_attr(self,schema:Schema,src:bool=True)->Schema:
        '''Adds the attribute computed upon landing to a model'''
        copy = schema.copy()
        attrs = self.sa1 if src else self.sa2
        for sa in attrs:
            sa.add(copy)
        return copy

    def conds(self,objname:str)->L[CQLEQ]:
        '''Where clause for a query entity'''
        if objname not in self.ne1:
            '''Conditions on foreign keys'''
            return []#[fk.eq().eq() for fk in self.s1[objname].fks.values()]
        else:
            return [w.eq(self.s1) for w in self.ne1[objname].where]

    def all_gens(self, objname:str, src:bool=True) -> L[Gen]:
        '''All generators for an entity in a query'''
        if src       and objname in self.ne1: return self.ne1[objname].gens
        if (not src) and objname in self.ne2: return self.ne2[objname].gens

        s       = self.s1 if src else self.s2
        default = Gen(objname,s[objname])
        gens    = [] # type: L[Gen]
        return gens if gens else [default]

    def entity_eqs(self) -> D[str,str]:
        return {p1.start:p2.start for p1,p2 in self.patheqs.items()}

    def modify(self,name:str,sc:SchemaColimitQuotient)->'SchemaColimitModify':
        '''
        Returns a modify command to sc1 such that names that are dependent on
        the name of sc1 are renamed to be the name of sc2
        '''
        prefix    = 'src2_no_cons_'
        prefix_   = 'src2_'
        np        = len(prefix)

        fks  = {} # type: D[str,str]
        attrs= {} # type: D[str,str]
        for e in chain(self.ne1.values(),self.ne2.values()):
            n = e.ent.name
            p1 = n+'.'+prefix+n+'_'
            p2 = prefix_+n+ '_'
            fks.update({p1+f.name:p2+f.name for f in e.fks})
            attrs.update({p1+a:p2+a for a in e.attrs})


        args = dict(ents  = {},#ents,
                    fks   = fks,
                    attrs = attrs,
                    rm_attrs=[],rm_fks=[]) # type: dict
        return SchemaColimitModify(name  = name,sc = sc,**args)
