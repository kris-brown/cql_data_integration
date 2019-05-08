# External
from typing import (Any,
                    List     as L,
                    Set      as S,
                    Dict     as D,
                    Union    as U,
                    Tuple    as T,
                    Iterable as I,
                    Callable as C)
from abc         import ABCMeta,abstractmethod
from collections import defaultdict
from itertools   import chain
# Internal
from cdi.core.utils import Base,Conn, Showable, Fn, merge_dicts

'''
Primitive datatypes which appear in an CQL file

These classes should really just be containers that know how to print themselves
to a file. Business logic should be kept in classes.py
'''
##############################################################################
eq  = '{} = {}'
arr = '{} -> {}'
nn  = '\n\n'.join
nt  = '\n\t'.join
ntt = '\n\t\t'.join
nnt = '\n\n\t'.join
nttt = '\n\t\t\t'.join
nntt = '\n\n\t\t'.join

class CQLSection(Base, metaclass = ABCMeta):
    '''Class for things that appear in the CQL file outline'''
    @abstractmethod
    def show(self) -> str:
        raise NotImplementedError

class Title(CQLSection):
    def __init__(self,num:int,subsection: int = None, name:str = '')->None:
        self.num = num
        self.sub = subsection
        self.name = name

    @property
    def sect(self)->str:
        return str(self.num) + ('' if not self.sub else '.%d'%self.sub)

    def __str__(self)->str:
        return 'Title<%s: %s>'%(self.sect,self.name)
    def show(self)->str:
        s = '//Section %s: '%self.sect + self.name
        x = '//'+'-'*(len(s)-2)
        return '\n'.join([x,s,x])

class Options(CQLSection):
    def __init__(self, **kwargs : Any) -> None:
        self.kwargs = kwargs
    def __str__(self) -> str:
        return 'Options<%s>'%self.kwargs
    def show(self) -> str:
        return 'options\n\t'+nt(eq.format(k,self.escape(v))
                for k,v in self.kwargs.items())
    @staticmethod
    def escape(x:Any)->str:
        if isinstance(x,str):   return '"%s"'%x
        else:                   return str(x)

class Type(Base):
    def __init__(self, name : str) -> None:
        self.name = name
    def __str__(self) -> str:
        return self.name

class Java(Base):
    '''Java-related things'''

class JavaFunc(Java):
    def __init__(self, name:str,itypes : L[str], otype: str, src:str)->None:
        self.name   = name
        self.itypes = itypes
        self.otype  = otype
        self.src    = src

    def __str__(self)->str:
        i = ','.join(map(str,self.itypes))
        args = [self.name,i,self.otype,self.src]
        return '{} : {} -> {}\n\t\t\t = "{}"'.format(*args)

    def __call__(self, *args : 'Expr') -> 'ExprFunc':
        return ExprFunc(func=self,args=list(args))

class JavaType(Java):
    '''Declare a java type, such as Long'''
    def __init__(self,name:str,expr:str)->None:
        self.name = name
        self.expr = expr
    def __str__(self)->str: return '{} = "{}"'.format(self.name,self.expr)

class JavaConst(Java):
    '''Unsure why this is needed....'''
    def __init__(self,name:str,expr:str)->None:
        self.name = name
        self.expr = expr
    def __str__(self)->str: return '{} = "{}"'.format(self.name,self.expr)

class Typeside(CQLSection):
    def __init__(self,
                 name    : str,
                 imports : L['Typeside'] = None,
                 funcs   : L[JavaFunc]   = None,
                 types   : L[JavaType]   = None,
                 consts  : L[JavaConst]  = None
                ) -> None:
        self.name    = name
        self.imports = set(imports or [])
        self.types   = set(types   or [])
        self.consts  = set(consts  or [])
        self.funcs   = set(funcs   or [])

    def __str__(self) -> str:
        args = [self.name,len(self.imports),len(self.funcs)]
        return 'Typeside<{},{} imports, {} funcs>'.format(*args)

    def show(self) -> str:
        i = ('\n\timports\n\t\t' + ntt([t.name for t in self.imports])) \
                if self.imports else ''
        t = ('\n\tjava_types\n\t\t'+nntt(map(str,self.types))) \
                if self.types else ''
        c = ('\n\tjava_constants\n\t\t'+nntt(map(str,self.consts))) \
                if self.consts else ''
        f = ('\n\tjava_functions\n\t\t'+nntt(map(str,self.funcs))) if self.funcs else ''
        body = '\n'.join([i,t,c,f])
        return 'typeside {} = literal {{ {} }}'.format(self.name,body)

sql = Typeside('sql') # builtin typeside

class Attr(Base):
    def __init__(self, name : str, ent : str, dtype : str) -> None:
        self.name  = name
        self.ent   = ent
        self.dtype = dtype

    def __str__(self) -> str: return self.name

    def show(self, desc : str = None) -> str:
        '''Render attr in an CQL schema. Function caller should know desc if any'''
        des  = ('//'+desc) if desc else ''
        args = [self.name,self.ent,self.dtype,des]
        return '{} : {} -> {} {}'.format(*args)

class FK(Base):
    def __init__(self, name : str, src : str, tar : str) -> None:
        self.name = name
        self.src  = src
        self.tar  = tar

    def __str__(self)->str: return self.name

    def show(self,desc:str = None) -> str:
        '''Render FK in an CQL schema'''
        des = ('//'+desc) if desc else ''
        args = [self.name,self.src,self.tar,des]
        return '{} : {} -> {} {}'.format(*args)

class Entity(Base):
    def __init__(self,
                 name   : str,
                 attrs  : I[Attr] = None,
                 fks    : I[FK]   = None
                ) -> None:
        self.name  = name
        self.attrs = {a.name  : a  for a  in attrs or []}
        self.fks   = {f.name  : f  for f  in fks   or []}

    def __str__(self) -> str:
        return self.name

    def show(self,desc : str = None) -> str:
        '''Render entity in the entities section of an CQL schema'''
        return self.name + (' // ' + desc if desc else '').replace('\n',' ')

################################################################################
class Expr(Showable, metaclass = ABCMeta):

    def __str__(self)->str:
        return 'CQLExpr<%s>'%self.show(str)

    @property
    @abstractmethod
    def dtype(self) -> str: raise NotImplementedError

class Eq(Expr):
    '''A WHERE constraint for an uber-flower query'''
    def __init__(self, e1 : Expr, e2 : Expr) -> None:
        self.e1 = e1
        self.e2 = e2

    def __str__(self) -> str:
        return '%s = %s'%(self.e1,self.e2)

    def show(self,f : Fn) -> str:
        return self.e1.show(f) + '=' + self.e2.show(f)

    def dtype(self)->str:
        return 'Boolean'

class JLit(Expr):
    '''
    A literal used in a Java expression (must be typed)
    '''

    def __init__(self, lit : str, dtype:str)->None:
        self.lit   = lit
        self._dtype = dtype

    def __str__(self) -> str:
        return self.show(str)

    def __eq__(self,other:object)->bool:
        return vars(self)==vars(other)

    @property
    def dtype(self)->str: return self._dtype

    def show(self, _ : Fn) -> str:
        return '"%s"@%s'%(self.lit,self._dtype)

class Path(Expr):
    def __init__(self, xs : L[U[Attr,FK,JLit,'GenAttr']]) -> None:
        assert xs
        assert all([isinstance(x,(Attr,FK,JLit,GenAttr)) for x in xs])
        self.xs = xs or []

    def __str__(self) -> str:
        return self.show(str)

    @property
    def start(self)->str:
        x = self.xs[0]
        if   isinstance(x,Attr):    return x.ent + '.'
        elif isinstance(x,FK):      return x.src + '.'
        elif isinstance(x,GenAttr): return x.name + '.'
        elif isinstance(x,JLit):    return ''
        else:                       raise TypeError

    @property
    def dtype(self)->str: return '???'

    def show(self, f : Fn) -> str:
        return  self.start + ' . '.join([f(x) for x in self.xs])

    @classmethod # OBSOLETE IF NORMAL 'SHOW' METHOD HAS START IN IT
    def noStart(cls,x:Any)->str:
        if isinstance(x,Path):
            return  ' . '.join([str(xx) for xx in x.xs])
        elif isinstance(x,Expr):    return x.show(cls.noStart)
        else: raise TypeError

class ExprFunc(Expr):
    def __init__(self, func : 'JavaFunc', args : L[Expr]) -> None:
        self.func = func
        self.args = args

    def show(self, f : Fn) -> str:
        args = '(%s)'%(','.join([a.show(f) for a in self.args]))
        return self.func.name + args
    @property
    def dtype(self) -> str: return self.func.otype

################################################################################
class PathEQ(Expr):
    def __init__(self, p1 : Path, p2 : Path) -> None:
        self.p1 = p1
        self.p2 = p2

    def __str__(self) -> str:
        return self.show(str)

    def show(self, f: Fn)->str:
        return '%s = %s'%(self.p1.show(f), self.p2.show(f))

    @property
    def dtype(self) -> str: return 'Boolean'

class ObsEQ(Expr):
    def __init__(self, e1 : Expr, e2 : Expr, gens : L['Gen']) -> None:
        self.e1,self.e2,self.gens = e1,e2,gens

    def __str__(self) -> str:
        return self.show(str)

    def show(self, f: Fn)->str:
        gens = ' '.join([str(g) for g in self.gens])
        args = [gens, self.e1.show(f),self.e2.show(f)]
        out  = 'forall {} . {} = {}'.format(*args)
        return out

    @property
    def dtype(self) -> str: return 'Boolean'


    @classmethod
    def renderObs(cls, x : Expr) -> str:
        if isinstance(x, Path):
            return 'x.' + x.show(cls.renderObs)
        elif isinstance(x,Expr):    return x.show(cls.renderObs)
        else:                       return str(x)

class EQ(Expr):
    def __init__(self, e1 : Expr, e2 : Expr) -> None:
        self.e1 = e1
        self.e2 = e2

    def __str__(self) -> str:
        return self.show(str)

    def show(self, f: Fn)->str:
        return '%s = %s'%(self.e1.show(f),self.e2.show(f))

    @property
    def dtype(self) -> str: return 'Boolean'

class Schema(CQLSection):
    def __init__(self,
                 name     : str,
                 typeside : str,
                 imports  : I['Schema'] = None,
                 entities : I[Entity]   = None,
                 attrs    : I[Attr]     = None,
                 fks      : I[FK]       = None,
                 pes      : I[PathEQ]   = None,
                 oes      : I[ObsEQ]    = None,
                 ent_desc : D[str,str]  = None,
                 col_desc : D[str,D[str,str]] = None
                ) -> None:

        self.name     = name
        self.typeside = typeside
        self.imports  = set(imports or [])
        self.entities = {e.name:e for e in entities or []}
        self.attrs    = {a for e in (entities or [])
                                for a in e.attrs.values()} | set(attrs or [])

        self.fks      = {f for e in (entities or [])
                                for f in e.fks.values()} | set(fks or [])
        self.pes      = pes or set()
        self.oes      = oes or set()
        self.ent_desc = ent_desc or {}
        self.col_desc = col_desc or defaultdict(dict)

    def __str__(self) -> str:
        args = [self.name,self.typeside,len(self.entities),len(self.imports)]
        return 'Schema<{} ({}),{} entities,{} imports'.format(*args)

    def show(self) -> str:
        sect = '\t%s\n\t//------\n\n\t\t'
        i  = (sect % 'imports'  + ntt([s.name for s in self.imports])) \
                if self.imports else ''
        e  = (sect % 'entities' + ntt([x.show(self.ent_desc.get(x.name)) for x in self.entities.values()])) \
                if self.entities else ''
        f  = (sect % 'foreign_keys') + ntt([fk.show(self.col_desc[fk.src].get(fk.name)) for fk in self.fks])\
                if self.fks else ''

        pe = (sect % 'path_equations' + ntt([str(pe) for pe in self.pes])) \
                if self.pes else ''
        at = (sect % 'attributes' + ntt([a.show(self.col_desc[a.ent].get(a.name)) for a in self.attrs])) \
                if self.attrs else ''

        oe = sect % 'observation_equations' + ntt([oe.show(ObsEQ.renderObs) for oe in self.oes]) \
                if self.oes else ''
        body = nn([i,e,f,pe,at,oe])
        args = [self.name,self.typeside,body]
        return 'schema {} = literal : {} {{ {} \n}}'.format(*args)

    def all_entities(self) -> D[str, Entity]:
        return merge_dicts([self.entities] + [i.all_entities() for i in self.imports])

    def rewrite_dict(self, overlap:D[str,str], left : 'Schema') -> D[str,T[str,S[str]]]:
        '''
        Data structure needed for re-writing path equations after a schema
        colimit. Considering the RHS schema (given a left-biased merge), we need
        to firstly check what entity a given entity has been equated with (first
        element of the tuple) and what attributes are held in common (these will
        need to be prefixed)
        '''
        es,les = self.all_entities(),left.all_entities()
        out = {k:(v,{a for a in chain(es[k].attrs,es[k].fks)
                    if a in chain(les[v].attrs,les[v].fks)})
            for k,v in overlap.items()}
        return out

class Mapping(CQLSection, metaclass = ABCMeta):
    name = '???'

    def show(self) -> str:
        return 'mapping {} = {}'.format(self.name,self.print())

    def __str__(self)->str:
        return self.show()

    @abstractmethod
    def print(self) -> str: raise NotImplementedError

    @property
    @abstractmethod
    def tar(self) -> 'Schema':
        raise NotImplementedError

    @property
    @abstractmethod
    def src(self) -> 'Schema':
        raise NotImplementedError

class IdMap(Mapping):
    def __init__(self, name : str, schema : Schema) -> None:
        self.name   = name
        self.schema = schema

    def print(self) -> str:
        return 'identity {}'.format(self.schema.name)
    @property
    def src(self) -> 'Schema': return self.schema
    @property
    def tar(self) -> 'Schema': return self.schema

class MapObj(Base):
    '''
    Building block of a Mapping literal
    '''
    def __init__(self,
                 src   : Entity,
                 tar   : Entity,
                 attrs : D[Attr,Path] = None,
                 fks   : D[FK,Path]   = None
                ) -> None:
        self.src   = src
        self.tar   = tar
        self.attrs = attrs or {}
        self.fks   = fks   or {}

    def __str__(self) -> str:
        a = ('attributes\n\t\t'+ntt(arr.format(k,Path.noStart(v)) for k,v in self.attrs.items()))\
                if self.attrs else ''
        f = ('foreign_keys\n\t\t'+ntt(arr.format(k,Path.noStart(v)) for k,v in self.fks.items()))\
                if self.fks else ''
        args = [self.src.name,self.tar.name,f,a]
        return 'entity\n\t\t{} -> {}\n\t{}\n\t{}'.format(*args)

class MapLit(Mapping):
    def __init__(self,
                 name    : str,
                 src     : Schema,
                 tar     : Schema,
                 imports : L[Mapping] = None,
                 maps    : L[MapObj]  = None,
                ) -> None:

        self.name    = name
        self._src    = src
        self._tar    = tar
        self.imports = set(imports or [])
        self.maps    = {m.src.name : m for m in (maps    or [])}

        # Validate: make sure everything in source schema has a mapping
        for e in self._src.entities:
            assert e in self.maps, 'MapLit %s missing %s'%(self,e)

    def __str__(self) -> str:
        return 'MapLit<%s -> %s>'%(self.src.name,self.tar.name)

    def print(self) -> str:
        i    = ('\n\timports\n\t\t'+ntt([i.name for i in self.imports])) if self.imports else ''
        m    = nnt(map(str,self.maps.values()))
        args = [self.src.name,self.tar.name,i,m]
        return 'literal : {} -> {} {{\n\t {}\n\n\t{} }}'.format(*args)

    @property
    def src(self) -> 'Schema': return self._src

    @property
    def tar(self) -> 'Schema': return self._tar

class GetMapping(Mapping):
    def __init__(self,name:str,sc:'SchemaColimit',schema:'Schema')->None:
        self.name = name
        self.sc   = sc
        self.schema = schema

    def print(self)->str:
        return 'getMapping %s %s'%(self.sc.name,self.schema.name,)

    @property
    def src(self) -> 'Schema': return self.schema

    @property
    def tar(self) -> 'Schema': return self.sc.schema('???')

class Include(Mapping):
    def __init__(self,name:str,src:'Schema',tar:'Schema')->None:
        self.name = name
        self._src = src
        self._tar = tar

    def print(self)->str:
        return 'include %s %s'%(self.src.name,self.tar.name)

    @property
    def src(self) -> 'Schema': return self._src

    @property
    def tar(self) -> 'Schema': return self._tar


class GetSchema(Schema):
    def __init__(self, name : str, sc : 'SchemaColimit') -> None:
        self.name = name
        self.sc   = sc
    def __str__(self) -> str: return self.show()
    def show(self) -> str:
        return 'schema {} = getSchema {}'.format(self.name,self.sc.name)

class SchemaColimit(CQLSection):

    @abstractmethod
    def name(self) -> str: raise NotImplementedError

    def schema(self,name:str) -> Schema:
        return GetSchema(name,self)

class SchemaColimitModify(SchemaColimit):
    def __init__(self,
                 name     : str,
                 sc       : SchemaColimit,
                 ents     : D[str,str],
                 fks      : D[str,str],
                 attrs    : D[str,str],
                 rm_attrs : L[str],
                 rm_fks   : L[str]
                ) -> None:
        self._name    = name
        self.sc       = sc
        self.ents     = ents
        self.fkmap    = fks
        self.attrmap  = attrs
        self.rm_attrs = rm_attrs
        self.rm_fks   = rm_fks
        assert not rm_attrs
        assert not rm_fks

    def __str__(self)->str:
        return 'SchemaColimitModify<%s>'%(self.sc.name)

    def show(self)->str:
        def pat(sect : str, items : L[str]) -> str:
            return (sect+''.join(['\n\t\t'+x for x in items])) if items else ''

        rne  = pat('rename entities',[arr.format(k,v) for k,v in self.ents.items()])
        rnfk = pat('rename foreign_keys',[arr.format(k,v) for k,v in self.fkmap.items()])
        rna  = pat('rename attributes',[arr.format(k,v) for k,v in self.attrmap.items()])
        body = nn([rne,rnfk,rna])
        args = [self.name,self.sc.name,body ]
        return 'schema_colimit {} = modify {} {{\n\t{} }}'.format(*args)
    @property
    def name(self) -> str: return self._name

class SchemaColimitQuotient(SchemaColimit):
    def __init__(self,
                 name     : str,
                 s1       : 'Schema',
                 s2       : 'Schema',
                 ent_eqs  : D[str,str],
                 path_eqs : L[PathEQ]
                ) -> None:
        self._name     = name
        self.s1       = s1
        self.s2       = s2
        self.ent_eqs  = ent_eqs
        self.path_eqs = path_eqs
    def __str__(self)->str:
        return 'SchemaColimitQuotient<%s|%s>'%(self.s1.name,self.s2.name)
    def show(self) -> str:
        n1,n2 = self.s1.name,self.s2.name
        dot  = '%s.%s'
        ee   = ntt([eq.format(dot%(n1,k),dot%(n2,v)) for k,v in self.ent_eqs.items()])
        pe   = ntt([str(p) for p in self.path_eqs])
        body = '\n\n\tentity_equations\n\t\t{}\n\n\tpath_equations\n\t\t{}'.format(ee,pe)

        opt  = '\n\toptions\n\t\tsimplify_names = false\n\t\tleft_bias = true\n'
        args = [self.name,n1,n2,self.s1.typeside,body, opt]
        return 'schema_colimit {} = quotient {} + {} : {} {{ {} {} }}'.format(*args)

    @property
    def name(self)->str: return self._name


class GenAttr(Expr):
    def __init__(self,
                 name   : str,
                 dtype  : str,
                 gen    : 'Gen',
                ) -> None:
        self.name  = name
        self.gen   = gen
        self._dtype = dtype

    def __str__(self)->str:
        return self.show(str)

    def show(self, _ : Fn) -> str:
        return self.gen.name+'.'+self.name

    @property
    def dtype(self) -> str: return self._dtype


class Gen(Base):
    def __init__(self, name : str, ent : str) -> None:
        self.name = name
        self.ent  = ent

    def __str__(self)->str:
        return self.name + ' : ' + self.ent


class QueryObj(Base):
    def __init__(self,
                 ent   : str,
                 gens  : L[Gen],
                 attrs : D[str,Expr] = None,
                 where : L[EQ]       = None,
                 fks   : D[str,D[str,str]]  = None
                ) -> None:
        self.ent   = ent
        self.gens  = gens
        self.attrs = attrs or {}
        self.where = set(where or [])
        self.fks   = fks or {}

        assert all([isinstance(k,str) and isinstance(v,Expr)
                    for k,v in self.attrs.items()])

    def __str__(self) -> str:
        g = nttt(map(str,sorted(self.gens)))
        w = ('\n\n\t\twhere \n\t\t\t'+nttt(map(str,sorted(self.where)))) if self.where else ''
        a = ('\n\n\t\tattributes \n\t\t\t'\
              +nttt([arr.format(k,v.show(str)) for k,v in sorted(self.attrs.items())]))\
                if self.attrs else ''
        f = ('\n\n\t\tforeign_keys \n\t\t\t'\
              +nttt([arr.format(k,'{%s}'%(' '.join([arr.format(vk,vv)
                                                        for vk,vv in sorted(v.items())])))
                     for k,v in self.fks.items()]))\
            if self.fks else ''
        args = [self.ent,g,w,a,f]

        return 'entity {} -> {{\n\t\tfrom\n\t\t\t{} {} {} {}}}'.format(*args)

class Query(CQLSection):
    def __init__(self,
                 name : str,
                 src  : Schema,
                 tar  : Schema,
                 objs : L[QueryObj],
                ) -> None:
        self.name = name
        self.src  = src
        self.tar  = tar
        self.objs = {o.ent:o for o in objs or []}

        for ten,te in tar.entities.items():
            assert ten in self.objs, ten
            tobj = self.objs[ten]
            for a in te.attrs:
                e = '%s missing statement for %s.%s'
                assert a in tobj.attrs, e%(self,ten,a)

    def __str__(self)->str:
        return 'Query<%s: %s -> %s>'%(self.name,self.src.name,self.tar.name)

    def show(self)->str:
        o    = nnt(map(str,sorted(self.objs.values())))
        opt  = '\n\toptions\n\t\tprover=completion'
        args = [self.name,self.src.name,self.tar.name,o,opt]
        return 'query {} = literal : {} -> {} {{\n\t{} {} }}'.format(*args)


class Constraint(Base):
    '''
    Don't really understand how these are constructed enough to truly handle.
    Just uses a raw string for the meat of it.
    '''
    def __init__(self,gens:L[Gen],con : str) -> None:
        self.gens = gens
        self.con  = con

    def __str__(self) -> str:
        g = ' '.join(map(str,self.gens))
        return 'forall {} {}'.format(g,self.con)

class Constraints(CQLSection):
    def __init__(self,name:str,schema:Schema,cons:L[Constraint]=None)->None:
        self.name = name
        self.schema = schema
        self.cons = set(cons or [])

    def __str__(self) -> str:
        args = self.name,self.schema.name,len(self.cons)
        return 'Constraints<{} ({}), {} constriants'.format(*args)

    def show(self) -> str:
        cons = nnt(map(str, sorted(self.cons)))
        args = [self.name, self.schema.name, cons]
        return 'constraints {} = literal : {} {{\n\t {} }}'.format(*args)

class Instance(CQLSection, metaclass = ABCMeta):
    name = '???'
    def __str__(self)->str:
        return self.show()

    @abstractmethod
    def print(self) -> str:
        raise NotImplementedError

    def show(self) -> str:
        return 'instance {} = {}'.format(self.name, self.print())

    @property
    @abstractmethod
    def schema(self)->Schema:
        raise NotImplementedError

class ChaseInstance(Instance):
    def __init__(self, name : str, con : Constraints, inst : Instance) -> None:
        self.name   = name
        self.con    = con
        self.inst   = inst

    def print(self) -> str:
        return 'chase {} {}'.format(self.con.name, self.inst.name)
    @property
    def schema(self)->Schema:
        return self.con.schema
class MapInstance(Instance):
    def __init__(self,name:str,functor:str,mapping:Mapping,inst:Instance) -> None:
        self.name    = name
        self.functor = functor
        self.map     = mapping
        self.inst    = inst
        assert functor in ['sigma','delta','pi']

    def print(self) -> str:
        return '{} {} {}'.format(self.functor, self.map.name, self.inst.name)
    @property
    def schema(self)->Schema:
        return self.map.tar

class EvalInstance(Instance):
    def __init__(self, name:str, q: Query, inst:Instance) -> None:
        self.name   = name
        self.q   = q
        self.inst = inst

    def print(self) -> str:
        return 'eval {} {}'.format(self.q.name,self.inst.name)
    @property
    def schema(self)->Schema:
        return self.q.tar
class DelInstance(Instance):
    def __init__(self, name:str, inst:Instance, schema:Schema) -> None:
        self.name   = name
        self.inst   = inst
        self._schema = schema

    def print(self) -> str:
        return 'cascade_delete {} : {}'.format(self.inst.name, self.schema.name)
    @property
    def schema(self)->Schema:
        return self._schema

class CoProdInstance(Instance):
    def __init__(self,name:str,i1:Instance,i2:Instance,schema:Schema)->None:
        self.name=name
        self.i1 = i1
        self.i2 = i2
        self._schema = schema
    def print(self)->str:
        args = [self.i1.name,self.i2.name,self.schema.name]
        return 'coproduct {} + {} : {}'.format(*args)
    @property
    def schema(self)->Schema:
        return self._schema

class Quotient(Instance):
    def __init__(self,name:str, inst:Instance, ents:D[str,L[str]]=None)->None:
        self.name = name
        self.inst = inst
        self.ents = ents or {}

    def print(self)->str:
        e = nnt([arr.format('entity '+e,
                            '{{from a:{0} b:{0} where {1}}}'.format(e,
                                ' '.join(['a.{0}=b.{0}'.format(x)
                                            for x in xs])))
                for e,xs in self.ents.items()])
        opt = '\n\toptions\n\t\tquotient_use_chase = false'
        return 'quotient_query {} {{\n\n\t{} {}}}'.format(self.inst.name,e,opt)

    @property
    def schema(self)->Schema:
        return self.inst.schema

class LandInstance(Instance):
    def __init__(self,name:str,conn:Conn,schema:Schema,ents:D[Entity,str])->None:
        self.name    = name
        self.conn    = conn
        self._schema = schema
        self.ents    = ents
    @property
    def schema(self)->Schema:
        return self._schema
    def print(self)->str:
        e = nnt([arr.format(ent.name,sql) for ent,sql in self.ents.items()])
        args = [self.conn.jdbc(),self.schema.name,e]
        return 'import_jdbc "{}" : {} {{\n\t{} }}'.format(*args)

class EmptyInstance(Instance):
    def __init__(self,name:str,schema:Schema)->None:
        self.name = name
        self._schema = schema
    @property
    def schema(self)->Schema:
        return self._schema
    def print(self)->str: return 'empty : '+self.schema.name

class LitInstance(Instance):
    def __init__(self,
                 name   : str,
                 schema : Schema,
                 gens   : I[Gen],
                 eqs    : D[str,D[Gen,U[Gen,JLit]]]
                ) -> None:
        self.name    = name
        self._schema = schema
        self.gens    = gens
        self.eqs     = eqs

    @property
    def schema(self) -> Schema:
        return self._schema

    def print(self) -> str:
        g = ntt([str(g) for g in sorted(self.gens)])
        e = ntt([arr.format(k,'{%s}'%(','.join([g.name + ' ' + (eq.name if isinstance(eq,Gen) else str(eq)) for g,eq in v.items()])))
                for k,v in sorted(self.eqs.items())])
        body = 'generators\n\t\t{}\n\n\tmulti_equations\n\t\t{}'.format(g,e)
        return 'literal : {} {{\n\t{}}}'.format(self.schema.name,body)

####################################################

class Command(CQLSection, metaclass = ABCMeta):
    name = '???'
    def __str__(self) -> str:
        return self.show()
    @abstractmethod
    def print(self) -> str: raise NotImplementedError

    def show(self) -> str:
        return 'command {} = {}'.format(self.name,self.print())

class Exec(Command):
    def __init__(self, name : str, conn : Conn, sql : str, db : bool = True) -> None:
        self.name  = name
        self.conn  = conn
        self.sql   = sql
        self.db    = db
    def print(self) -> str:
        args = [self.conn.jdbc(self.db),self.sql]
        return 'exec_jdbc "{}" {{"{}"}}'.format(*args)

class Export(Command):
    def __init__(self, name : str, conn : Conn, inst : Instance) -> None:
        self.name  = name
        self.conn  = conn
        self.inst  = inst
    def print(self) -> str:
        args = [self.inst.name, self.conn.jdbc()]
        return 'export_jdbc_instance {} "{}" ""'.format(*args)
