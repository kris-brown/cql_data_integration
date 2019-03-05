# External
from typing import (Any,
                    List     as L,
                    Dict     as D,
                    Union    as U,
                    Tuple    as T,
                    Iterable as I,
                    Callable as C)

from abc         import ABCMeta,abstractmethod
from collections import defaultdict

# Internal
from cdi.core.utils       import Base, flatten, Fn
from cdi.core.expr        import Expr as SQLExpr,Literal
from cdi.core.primitives  import Type

from cdi.core.classes import (
    Attr as Attr_, FK as FK_,Entity as Entity_,Overlap as Overlap_,
    Schema as Schema_,PathEQ as PathEQ_,Path as Path_,JLit as JLit_, Gen as Gen_,
    EQ as EQ_,NewEntity as NewEntity_,NewFK as NewFK_,SQLAttr as SQLAttr_,
    NewAttr as NewAttr_,Expr as CQLExpr_,ExprFunc as ExprFunc_,GenAttr as GenAttr_,
    Land as Land_,LandObj,Ref,UserExposedCQLExpr as CQLExpr,ObsEQ as ObsEQ_)

from cdi.core.primitives import (
    Java,JavaFunc as JavaFunc_, LitInstance, EmptyInstance, Schema as CQLSchema,
    JLit as CQLJLit, Gen as CQLGen)

'''
Public interface for CQL - merely meant to collect data from users in a friendly
way and ultimately be converted to classes in classes.py which contain main logic
'''

################################################################################
class DType(Base):
    '''A datatype, possibly SQL or Java'''
    def __init__(self, name : str) -> None:
        self.name = name
    def __str__(self) -> str:
        return 'Type<%s>'%(self.name)
    def type(self)->Type:
        return Type(self.name)

# Specific datatypes exposed for users
Int,Integer,Tinyint,Varchar,Decimal,Text,Date,Double,\
String,Boolean,Float,Long,Bigint = \
    map(DType,['Integer','Integer','Boolean','String','Double','Text','Date',
               'Double','String','Boolean','Float','Long','Bigint'])


class JLit(CQLExpr):
    def __init__(self,val:Any,dtype:DType)->None:
        self.val = val
        self._dtype = dtype

    def __str__(self) -> str:
        return 'JLit<%s,%s>'%(self.val,self._dtype)
    def jlit(self)->JLit_:
        return JLit_(self.val,self._dtype.type())
    def mk_expr(self)->CQLExpr_:
        return self.jlit()

class Attr(Base):
    '''
    User-exposed constructor for attributes
    Doesn't know which object it is from
    '''
    def __init__(self,
                 name   : str,
                 dtype  : DType = None,
                 desc   : str  = '',
                 id     : bool = False
                ) -> None:
        self.name  = name
        self.dtype = dtype or DType('Integer')
        self.desc  = desc
        self.id    = id

    def __str__(self) -> str:
        return 'Attr<%s>'%self.name

    def attr(self,objname:str)->Attr_:
        return Attr_(self.name,objname,self.dtype.type(),self.id)

class FK(Base):
    '''
    User-exposed foreign key...declared within an entity
    (so src object need not be defined)
    '''
    def __init__(self,
                 name : str,
                 tar  : str  = None,
                 id   : bool = False, # whether this is IDENTIFYING
                 desc : str  = ''
                 ) -> None:
        self.name = name
        self.tar  = tar or name # default: FK name = target table
        self.id   = id
        self.desc = desc

    def __str__(self) -> str:
        return 'FK<%s>'%self.name

    def fk(self, objname : str)->FK_:
        return FK_(self.name,objname,self.tar,self.id)


class Entity(Base):
    '''User-exposed object for constructing an entity'''
    def __init__(self,
                 name   : str,
                 desc   : str     = '',
                 attrs  : L[Attr] = None,
                 fks    : L[FK]   = None,
                 id     : str     = '' # which attribute is the PK column (default: "<name>_id")
                 ) -> None:
        self.name  = name
        self.desc  = desc
        self.attrs = {a.name  : a  for a  in attrs or []}
        self.fks   = {fk.name : fk for fk in fks or []}

        self.idname = id or (name + '_id')
        self.idtype = self.attrs[self.idname].dtype \
                            if self.idname in self.attrs else Integer

    def __str__(self)->str:
        return 'Entity<%s>'%self.name

    def __getitem__(self, key : str) -> Ref:
        return Ref(self.name,key)

    @property
    def id(self)->SQLExpr:
        return Ref(self.name,self.idname)

    def ent(self)->Entity_:
        a = {an:at.attr(self.name) for an,at in self.attrs.items()}
        f = {fn:fk.fk(self.name)   for fn,fk in self.fks.items()}
        i = Attr_(self.idname,self.name,self.idtype.type(),id=False)
        return Entity_(self.name,a,f,i)

class Path(Base):
    '''Constructor for paths (list path items as args)'''
    def __init__(self,*xs : U[Ref,JLit,'GenAttr',CQLExpr]) -> None:
        assert xs, 'No such thing as empty path'
        self.xs = list(xs)

    def __str__(self)->str:
        return 'Path<%s>'%','.join(map(str,self.xs))

    def path(self,s:Schema_)-> Path_:
        x0 = self.xs[0]
        if   isinstance(x0,Ref):    start = x0.obj
        elif isinstance(x0,JLit):   start = x0._dtype.name
        else: raise ValueError(x0)
        xs = [] # type: L[U[FK_,Attr_,JLit_]]
        for x in self.xs:
            if   isinstance(x,Ref):    xs.append(x.realize(s))
            elif isinstance(x,JLit):   xs.append(x.jlit())
        return Path_(start, xs)

    def obs(self,s:Schema_)-> CQLExpr_:
        x0 = self.xs[0]
        if isinstance(x0,JLit): return x0.jlit()
        elif isinstance(x0,GenAttr):
            out = x0.mk_expr()
            for x in self.xs[1:]:
                assert isinstance(x,Ref), 'Invalid type in obseq %s'%type(x)
                out = x.func(out)
            return out
        elif isinstance(x0,CQLExpr):
            assert len(self.xs)==1
            return x0.mk_expr()
        else: raise TypeError(type(x0))
        
    @property
    def is_path(self)->bool:
        return not any([isinstance(x, (JLit,JavaFunc,GenAttr)) for x in self.xs])

class PathEQ(Base):
    '''Constructor for path equalities'''
    def __init__(self, p1 : Path, p2 : Path) -> None:
        self.p1, self.p2 = p1, p2

    def __str__(self) -> str:
        return 'PathEQ<%s | %s>'%(self.p1,self.p2)

    def peq(self, s1 : Schema_, s2 : Schema_ = None) -> U[PathEQ_,ObsEQ_]:

        s2 = s2 or s1 # one schema provided ==> PEQ WITHIN a single schema
        if self.is_path:
            return PathEQ_(self.p1.path(s1), self.p2.path(s2))
        else:
            return ObsEQ_(s1,self.p1.obs(s1), self.p2.obs(s2))

    @property
    def is_path(self) -> bool:
        return self.p1.is_path and self.p2.is_path

class Schema(Base):
    '''User-exposed object for constructing a schema'''
    def __init__(self,
                 name     : str,
                 entities : L[Entity]   = None,
                 pes      : L[PathEQ]   = None,
                 ) -> None:
        self.name     = name
        self.entities = {e.name:e for e in entities or []}
        self.pes      = set(pes or [])

    def __str__(self)->str:
        args = (self.name,len(self.entities),len(self.pes))
        return 'Schema<{},{} entities, {} pathEQs>'.format(*args)

    def __getitem__(self, key : str) -> Entity:
        return self.entities[key]

    get = __getitem__

    def schema(self)->Schema_:
        '''To do - distinguish path equalities from observation_equations'''
        es    = [e.ent() for e in self.entities.values()]
        dummy = Schema_(self.name, es)
        eqs   = [p.peq(dummy) for p in self.pes]

        return Schema_(name=self.name,
                       entities=es,
                       pes = [eq for eq in eqs if isinstance(eq,PathEQ_)],
                       oes = [eq for eq in eqs if isinstance(eq,ObsEQ_)])

    def remove_obj(self,name:str)->'Schema':
        return Schema(self.name,[e for en,e in self.entities.items()
                        if e.name != name and not any([name == fk.tar for fk in e.fks.values()])])

class ExprFunc(CQLExpr):
    '''A java function that has been called on arguments...this is not exposed
        to user'''
    def __init__(self,func:'JavaFunc',args:I[CQLExpr])->None:
        self.func = func
        self.args = list(args)
    def __str__(self)->str:
        return 'ExprFunc<%s(%s)>'%(self.func.name,self.args)
    def mk_expr(self)->CQLExpr_:
        return ExprFunc_(self.func,[e.mk_expr() for e in self.args])

class JavaFunc(Java):
    '''User exposed constructor for custom Java functions'''
    def __init__(self, name:str,itypes : L[DType], otype: DType, src:str)->None:
        self.name   = name
        self.itypes = itypes
        self.otype  = otype
        self.src    = src
    def __str__(self)->str:
        return 'JavaFunc<%s>'%self.name
    def __call__(self, *args : CQLExpr) -> CQLExpr:
        return ExprFunc(func=self,args=args)

    def javafunc(self) -> JavaFunc_:
        return JavaFunc_(self.name,[t.name for t in self.itypes],self.otype.name,self.src)

class Land(Base):
    '''User-exposed constructor for specifying constraints on the data landed
    into CQL from an external database'''
    def __init__(self,schema:Schema,where:D[str,SQLExpr])->None:
        self.schema= schema
        self.where = where

    def __str__(self) -> str:
        return 'Land<%s>'%self.schema.name

    def land(self,overlap:Overlap_)->Land_:
        sa = overlap.sa1 if overlap.s1.name == self.schema.name else overlap.sa2
        lo = [LandObj(src    = e.ent(),
                      consts = {a.attr:a.expr for a in sa if a.ent==en},
                      where  = self.where.get(en)) for en,e in self.schema.entities.items()]
        return Land_(self.schema.schema(),lo)

class Gen(Base):
    '''A generator which can be referred to in CQL expressions'''
    def __init__(self, name : str, ent : Entity) -> None:
        self.name = name
        self.ent  = ent

    def __str__(self) -> str:
        return 'Gen<%s:%s>'%(self.name,self.ent)

    def gen(self) -> Gen_:
        return Gen_(self.name,self.ent.ent())

    def __getitem__(self, key : str) -> 'GenAttr':
        return GenAttr(key,self)

class GenAttr(CQLExpr):
    '''Not directly exposed to user, but a front-facing datatype. We do not
        immediately evaluate for details about the attribute (we have attr name
        and the entity) b/c the entity might be changed (esp adding of attrs)'''

    def __init__(self, name : str, gen : Gen)->None:
        self.name = name
        self.gen  = gen

    def __str__(self)->str:
        return 'GenAttr<%s %s>'%(self.gen, self.name)

    def mk_expr(self)->CQLExpr_:
        return GenAttr_(self.name,self.gen.gen())

class EQ(Base):
    '''Equality of expressions, used in WHERE clause of CQL query.'''
    def __init__(self, e1 : CQLExpr, e2 : CQLExpr)->None:
        self.e1 = e1
        self.e2 = e2
    def __str__(self)->str:
        return 'ExprEQ<%s = %s>'%(self.e1,self.e2)

    def eq(self)->EQ_:
        return EQ_(self.e1.mk_expr(),self.e2.mk_expr())

class NewEntity(Base):
    '''Construct a new entity within CQL'''
    def __init__(self,
                 name   : str,
                 gens   : L[Gen],
                 where  : L[EQ]           = None,
                 attrs  : D[Attr,CQLExpr] = None,
                 fks    : D[FK,Gen]       = None
                 ) -> None:
        self.name  = name
        self.gens  = gens
        self.where = where or []
        self.attrs = attrs or {}
        self.fks   = fks or {}

    def __str__(self)->str:
        return 'NewEntity<%s>'%self.name


class SQLAttr(Base):
    '''User interface for creating a new attribute during landing data from SQL
        using a SQL expression'''
    def __init__(self, ent : Entity, attr : str, dtype : DType, expr : SQLExpr) -> None:
        self.ent   = ent
        self.attr  = attr
        self.dtype = dtype
        self.expr  = expr

    def __str__(self)->str:
        return 'SQLAttr<%s.%s>'%(self.ent.name,self.attr)


class NewAttr(Base):
    '''Create a new attribute during an CQL query for an existing object'''
    def __init__(self, ent : Entity, attr : str, dtype : DType, expr : CQLExpr) -> None:
        self.ent   = ent
        self.attr  = attr
        self.dtype = dtype
        self.expr  = expr

    def __str__(self)->str:
        return 'NewAttr<%s.%s>'%(self.ent.name,self.attr)


class NewFK(Base):
    '''Create a new FK during an CQL query for an existing object'''
    def __init__(self, ent : Entity, fk : FK, gen : Gen) -> None:
        self.ent  = ent
        self.fk   = fk
        self.gen  = gen

    def __str__(self)->str:
        return 'NewFK<%s.%s>'%(self.ent.name,self.fk)

class Overlap(Base):
    '''User interface for specifying overlap between two schemas
    Also possible to construct  attributes and entities that are found in
        the other schema using SQL/CQL expressions
    Arbitrary path equalities (that may involve the newly-constructed attrs/entities)
    '''
    def __init__(self,
                 s1        : Schema,
                 s2        : Schema,
                 paths     : L[PathEQ]      = None,
                 sql_attr1 : L[SQLAttr]     = None,
                 new_attr1 : L[NewAttr]     = None,
                 new_fk1   : L[NewFK]       = None,
                 new_ent1  : L[NewEntity]   = None,
                 sql_attr2 : L[SQLAttr]     = None,
                 new_attr2 : L[NewAttr]     = None,
                 new_fk2   : L[NewFK]       = None,
                 new_ent2  : L[NewEntity]   = None,
                 ) -> None:

        self.s1,self.s2 = s1,s2
        self.paths = paths or []
        self.sa1   = set(sql_attr1 or [])
        self.sa2   = set(sql_attr2 or [])
        self.na1   = set(new_attr1 or [])
        self.na2   = set(new_attr2 or [])
        self.nf1   = set(new_fk1 or [])
        self.nf2   = set(new_fk2 or [])
        self.ne1   = set(new_ent1  or [])
        self.ne2   = set(new_ent2  or [])

    def __str__(self)->str:
        return 'Overlap<%s | %s>'%(self.s1.name,self.s2.name)

    def overlap(self)->Overlap_:

        sa1,sa2 = [[SQLAttr_(a.ent.name,Attr_(a.attr,a.ent.name,a.dtype.type(),id=False),a.expr)
                    for a in sa] for sa in [self.sa1,self.sa2]]

        s1,s2 = [s.schema() for s in [self.s1,self.s2]]
        for schema,sqlattrs in [(s1,sa1),(s2,sa2)]:
            for sqlattr in sqlattrs: sqlattr.add(schema)

        na1,na2 = [[NewAttr_(s.entities[a.ent.name],a.attr,a.dtype.type(),a.expr.mk_expr())
                    for a in na] for s,na in [(s1,self.na1),(s2,self.na2)]]
                    # Previously it was just "s1.entities[...]" for everything, but that looked wrong

        nf1,nf2 = [[NewFK_(s.entities[f.ent.name],f.fk.fk(f.ent.name),f.gen.gen())
                    for f in nf] for s,nf in [(s1,self.nf1),(s2,self.nf2)]]

        for schema,newattrs,newfks in [(s1,na1,nf1),(s2,na2,nf2)]:
            for newattr in newattrs: newattr.add(schema)
            for newfk   in newfks:   newfk.add(schema)


        ne1,ne2 = [[NewEntity_(ent = Entity_(ne.name,
                                            attrs = {a.name:Attr_(a.name,ne.name,a.dtype.type(),a.id)
                                                        for a,e in ne.attrs.items()},
                                            fks   = {fk.name:fk.fk(ne.name)
                                                        for fk,v in ne.fks.items()}),
                               gens  = [g.gen() for g in ne.gens],
                               attrs = {a.name:e.mk_expr() for a,e in ne.attrs.items()},
                               fks   = {f.fk(ne.name):v.gen() for f,v in ne.fks.items()},
                               where = [e.eq() for e in ne.where])
                   for ne in nes]
                    for nes in [self.ne1,self.ne2]]

        for schema,newents in [(s1,ne1),(s2,ne2)]:
            for newent in newents: newent.add(schema)

        ps  = [peq.peq(s1,s2) for peq in self.paths]
        ps_  = [p for p in ps if isinstance(p,PathEQ_)]
        assert len(ps)==len(ps_), 'Invalid PathEQ in schema overlap (no obs equations allowed)'
        return Overlap_(s1,s2, patheqs = ps_, ne1 = ne1,ne2 = ne2, sa1 = sa1,
                        sa2 = sa2, na1 = na1, na2 = na2, nf1 = nf1, nf2=nf2)

class Instance(Base):
    '''
    Literally specify a database instance: alternative to providing a DB connection
    '''
    def __init__(self, eqs : D[Ref,D[Gen,U[Gen,JLit]]] = None) -> None:
        self.eqs = eqs

    def __str__(self) -> str:
        return 'Instance'

    def inst(self, name : str, schema : CQLSchema) -> U[EmptyInstance,LitInstance]:
        if not self.eqs: return EmptyInstance(name,schema)
        gens = set([g.gen().gen() for eqd in self.eqs.values() for g in eqd.keys()])
        eqs  = {r.attr : {g.gen().gen():(s.gen().gen() if isinstance(s,Gen) else s.jlit().jlit())
                for g,s in e.items()} for r,e in self.eqs.items()} # type: D[str,D[CQLGen,U[CQLGen,CQLJLit]]]
        return LitInstance(name = name, schema = schema, gens = gens, eqs = eqs)
