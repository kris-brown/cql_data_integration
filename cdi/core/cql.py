# External modules
from typing import List as L, Dict as D, Tuple as T, Union as U, Optional as O
from abc    import ABCMeta,abstractmethod
from re     import split,sub,findall

# Internal modules
from cdi.core.utils      import Base, Conn, flatten, merge_dicts
from cdi.core.expr       import Expr as SQLExpr,Fn, Literal as Lit

from cdi.core.exposed    import (Overlap as UserOverlap, Schema as UserSchema,
                                      JavaFunc as UserJavaFunc,Land as UserLand,
                                      Entity as UserEntity,Instance as UserInstance)
from cdi.core.classes    import (Land,LandObj,Schema,Overlap,Path,PathEQ,FK,
                                      Attr,Rewrite)
from cdi.core.primitives import (CQLSection,Expr,Gen as CQLGen,JLit,JavaFunc,
                                      Schema as CQLSchema,Type,FK as CQLFK,Eq,
                                      PathEQ as CQLPEQ,Typeside,LandInstance,
                                      Entity as CQLEntity,Attr as CQLAttr,
                                      Title,Options,sql,MapLit,MapObj,IdMap,
                                      Path as CQLPath, Query, Constraints,
                                      Constraint,ChaseInstance,MapInstance,
                                      DelInstance,EvalInstance,MapInstance,
                                      CoProdInstance,Exec,Export,GetMapping,
                                      ExprFunc,QueryObj,Java,JavaConst,JavaType,
                                      SchemaColimitQuotient,
                                      GetSchema,Instance,Include)
'''
Defines the high-level operations (Merge/Migrate) that this interface exposes
to a user --- these are not primitives in CQL - rather, these operations
construct an CQL file
'''
Input = U[UserInstance,Conn] # an input schema is either a DB cxn or a literal instance
##########################################################################

class CQL(Base, metaclass = ABCMeta):
    '''
    Class of high-level CQL operations which produce an CQL file from Python input

    Currently there are only two (merge/migrate), and they require the same input
    - filt1/2 correspond to src/tar respectively. They map entities in the schema
      to SQL expressions which are used in the WHERE clause of the query which
      lands data from an external DB.
    - overlap specifies the semantic overlap between the two schemas
    - funcs are used to declare any java types/functions/constants that are used
      elsewhere in the input
    '''
    default = Options(gui_max_graph_size    = 100000000,
                      gui_max_table_size    = 100000000,
                      timeout               = 3600,
                      jdbc_quote_char       = "`",
                      allow_java_eqs_unsafe = True )

    def __init__(self,
                 src     : 'UserSchema',
                 tar     : 'UserSchema',
                 filt1   : D[UserEntity,SQLExpr]     = None,
                 filt2   : D[UserEntity,SQLExpr]     = None,
                 overlap : UserOverlap               = None,
                 funcs   : U[L[Java],L[UserJavaFunc]]= None,
                ) -> None:

        self.src    = src.schema()
        self.tar    = tar.schema()
        self.overlap= overlap.overlap() if overlap else Overlap(self.src,self.tar)

        self.filt1  = filt1 or {}
        self.filt2  = filt2 or {}

        self.funcs  = [f.javafunc() for f in (funcs or []) if isinstance(f,UserJavaFunc)]
        self.jtype  = [t            for t in (funcs or []) if isinstance(t,JavaType)]
        self.jconst = [c            for c in (funcs or []) if isinstance(c,JavaConst)]

    ######################
    # main public method #
    ######################
    def file(self, src    : Input, tar : Input, merged : Conn = None) -> str:
        '''A file is just concatenation of sections'''
        fi = '\n\n\n'.join([s.show() for s in self.sections(src,tar,merged)])
        return self._align(fi) # attempt to prettify

    #############
    # interface #
    #############
    @abstractmethod
    def sections(self, src : Input, tar : Input, merged : Conn ) -> L[CQLSection]:
        raise NotImplementedError # this is how Merge and Migrate differ

    ###################
    # private methods #
    ###################
    def _lands(self)->T[Land,Land]:
        '''
        Given one's overlap and the src/tar filters, construct a Land instance
        which contains info needed to write the import_jdbc section of an CQL file
        '''
        items = [(self.src,self.overlap.sa1,{k.name:v for k,v in self.filt1.items()}),
                 (self.tar,self.overlap.sa2,{k.name:v for k,v in self.filt2.items()})]

        l1,l2 =  [Land(schema,
                       [LandObj(src   = e,
                               consts = {a.attr:a.expr for a in sa if a.ent==en},
                               where  = filt.get(en,Lit(1)))
                        for en,e in schema.entities.items()])
                    for schema,sa,filt in items]
        return l1,l2

    def _from_db(self,
                 num  : int,
                 name : str,
                 s    : Schema,
                 ss   : CQLSchema,
                 land : Land,
                 conn : Conn
                 ) -> T[Instance, L[CQLSection]]:
        '''
        Assuming we have a DB connection for src or tar, create a series of CQL
        sections that result in an instance of the desired schema WITHOUT failing.

        In order to do this safely, we make no assumptions about the data adhering
        to FK constraints or data integrity constraints. We land the data in a
        pseudo-schema that has attributes instead of FKs and use the chase to
        produce an instance with valid FKs (if there is a NULL or dangling FK
        reference, a new record (with labeled NULLs) will be generated, which
        may in turn trigger other null records to also be generated). We then use
        a delete_cascade to remove records which do not meet data integrity constraints.
        '''
        s_core = s.schema('s_%s_core'%name,self._ty,uid=True,fks=False,pe=False)
        s_raw  = s.schema('s_%s_raw'%name,self._ty,uid=True,fks='attr',pe=False)
        s_fk   = s.schema(name+'_fk',self._ty,uid=True,pe=False)
        c_fk   = s.fk_constraints('con_fk_'+name,s_raw)

        idm = IdMap('id_core_'+name,s_core)
        m   = self._land_migrate('M_fks_'+name,s_raw,s_fk,idm)

        i_raw = land.inst('i_%s_raw'%name,s_raw,conn)
        ich   = ChaseInstance('i_chased_'+name,c_fk,i_raw)
        ifk   = MapInstance('i_fk_'+name,'sigma',m,ich)
        i     = DelInstance('i_'+name,ifk,ss)

        return i,[s_core,s_raw,s_fk,
                Title(num,1,'Mappings'), idm,  m,
                Title(num,2,'Constraints'), c_fk,
                Title(num,3,'Land data'), i_raw,
                Title(num,4,'Move "unconstrained" instance data into real schema'),
                ich,ifk,i,]

    def _inst(self,
              sect : int,
              name : str,
              conn : Input,
              s    : Schema,
              ss   : CQLSchema,
              land : Land,
              ) -> T[Instance,L[CQLSection]]:
        '''
        Get the instance of src/tar + CQL sections required to construct it.
        Treat instances literally provided by user different from those with a
        DB connection.
        '''
        if isinstance(conn,Conn):
            return self._from_db(sect,name,s,ss,land,conn)
        else:
            i = conn.inst('i'+name,ss)
            return i,[i]

    def _export(self,sect:int,conn:O[Conn],ifinal:Instance) -> L[CQLSection]:
        '''Export an instance to a DB connection'''
        if not conn: return []
        drop   = Exec('cmd_drop',conn,'DROP DATABASE IF EXISTS `%s`'%conn.db,db=False)
        create = Exec('cmd_create',conn,"CREATE SCHEMA `%s`"%conn.db,db=False)
        merge  = Export('cmd_merged',conn,ifinal)
        return  [Title(4, name='Export to database'), drop, create, merge]


    @staticmethod
    def _align(fi : str) -> str:
        '''
        Aligns colons / arrows / equals on contiguous lines - works kind of poorly
        '''
        pats = [r' [:=(AS)]',r'->',r'//']
        def process(chunk:str,pat:str)->str:
            splits,outs = [],[] # type: ignore
            lines  = chunk.replace('\t','    ').split('\n')
            splits = [split(pat,line) for line in lines]
            l      = max([len(s[0]) if len(s)==2 else 0 for s in splits])

            return '\n'.join([line if len(s)!=2 else sub(pat,' '*(l-len(s[0]))+findall(pat,line)[0],line)
                                for s,line in zip(splits,lines)])

        for pat in pats:
            chunks = fi.split('\n\n')
            fi = '\n\n'.join([process(c,pat) for c in chunks])
        return fi

    @staticmethod
    def _land_migrate(name : str,
                      src  : 'CQLSchema',
                      tar  : 'CQLSchema',
                      id   : 'IdMap'
                     ) -> MapLit:
        '''Generate the mapping needed to convert FK references to FKs'''
        mo = []
        for en,e in src.entities.items():
            t = tar.entities[en]
            attrs = {e.attrs[fkn] : CQLPath([fk,tar.entities[fk.tar].attrs['uid']])
                        for fkn,fk in t.fks.items()}
            mo.append(MapObj(e,t,attrs))

        return MapLit(name,src,tar,[id],mo)

    @property
    def _ty(self)->Typeside:
        return Typeside('ty',[sql],types=self.jtype,consts=self.jconst,funcs=self.funcs)


class Migrate(CQL):
    '''
    Given i1 : src and i2 : tar, add the data from i1 to i2 to create a new
    instance of tar
    '''
    def __str__(self)->str:
        return 'Migrate<%s->%s>'%(self.src.name,self.tar.name)

    def sections(self, src_conn : Input, tar_conn : Input, merged_conn : Conn)-> L[CQLSection]:

        s_inter  = self._inter() # intermediate schema
        starnc   = self.tar.copy()
        starnc.pes = set(); starnc.oes = set()
        s1       = self.overlap.add_sql_attr(self.src) # only source has 'extra' attrs from landing, possibly

        src      = s1.schema('src',self._ty) # this is an CQL schema, lower level than the CQL interface schema
        tar      = self.tar.schema('tar',self._ty)
        tarnc    = starnc.schema('tar_nc',self._ty)
        inter    = s_inter.schema('inter',self._ty)
        l1,l2    = self._lands()
        isrc,src_sects = self._inst(1,'src',src_conn,s1,src,l1)
        itar,tar_sects = self._inst(2,'tar',tar_conn,self.tar,tar,l2)

        Q  = Query('Q',src,inter,self.qobjs(s_inter))

        maps=[MapObj(src=e.ent(),
                     tar=(self.tar[self.overlap.entities[en]]
                        if en in self.overlap.entities else self.tar[en]).ent(),
                    attrs = {a.attr():self.overlap.patheqs_simple[a].path()
                                for an,a in e.attrs.items()
                                if a in self.overlap.patheqs_simple},
                    fks = {f.fk():self.overlap.patheqs_simple[f].path()
                                for fn,f in e.fks.items()
                                if f in self.overlap.patheqs_simple})

            for en,e in s_inter.entities.items()]

        M      = MapLit('M',inter,tarnc,maps=maps)
        ialt   = EvalInstance('i_altered',Q,isrc)
        imap   = MapInstance('i_mapped','sigma',M,ialt)
        icon   = DelInstance('i_constrained',imap,tar)
        imrg   = CoProdInstance('i_merged',icon,itar,tar)
        final  = self.tar.quotient('i_final',imrg)

        return [Title(0, 1, 'Set-up'), self.default,  self._ty,
                Title(0, 2, 'Declare schemas'), src, tar, tarnc, inter,
                Title(1, name = 'Create source instance')] + src_sects + [
                Title(2, name = 'Create target instance')] + tar_sects + [
                Title(3, name = "Data migration"),
                Title(3, 1, "Query which adds extra information when eval'd"),  Q,
                Title(3, 2, 'Mapping'),  M,
                Title(3, 3, 'Move instance data from src to target'), ialt, imap, icon, imrg,
                Title(3, 4, 'Record linkages'), final,
                ] + self._export(4,merged_conn,final)

    def _inter(self) -> "Schema":
        '''
        Intermediate model with both added and removed entities/attributes/Fks

        Result schema after Query
        (has only entities/attrs that map somewhere in target schema)
        '''
        copy = self.src.copy() # so that we don't modify the Entities in src

        # Get all objects from src which are mapped into the target schema
        objs = [copy[objname] for objname in self.overlap.entities]

        # Remove any attributes which are not mapped somewhere in the target
        for o in objs:
            o.attrs = {an:a for an,a in o.attrs.items()
                            if a.path() in self.overlap.patheqs}
            o.fks   = {fkn:fk for fkn,fk in o.fks.items()
                            if fk.path() in self.overlap.patheqs}

        inter = Schema('inter',objs,[])

        assert not self.overlap.new2(), 'Cannot add "new" things to the target schema of a migration'

        for new in self.overlap.new1(): new.add(inter);

        return inter

    def qobjs(self,inter:Schema)->L[QueryObj]:
        '''
        Fill out the content for a query (src -> inter), depending on Overlap
        and intermediate schema.
        '''
        qobjs = {en:QueryObj(en,
                          [g.gen() for g in self.overlap.all_gens(en)],
                          where = self.overlap.conds(e.name),
                          attrs = {an:a.genattr()
                                    for an,a in e.attrs.items()
                                    if a in self.overlap.patheqs_simple},
                          fks = {fkn:{fk.tar:en+'.'+fkn}
                                    for fkn,fk in e.fks.items()
                                    if fk in self.overlap.patheqs_simple})

                 for en,e in inter.entities.items()}

        # Default FKs incorrect for New Entities. make a fix
        for q in qobjs.values():
            if q.ent in self.overlap.ne1:
                for fk in q.fks.keys():
                    real_fk = self.overlap.ne1[q.ent].ent.fks[fk]
                    q.fks[fk] = {real_fk.tar : self.overlap.ne1[q.ent].fks[real_fk].name}
                for attr in q.attrs.keys():
                    q.attrs[attr] = self.overlap.ne1[q.ent].attrs[attr].expr(self.overlap.s1)
        for na in self.overlap.na1:
            qo = qobjs[na.ent.name]
            qo.attrs[na.attr.name] = na.expr.expr(self.overlap.s1)

        for nf in self.overlap.nf1:
            qo = qobjs[nf.ent.name]
            qo.fks[nf.fk.name] = {nf.gen.ent.name:nf.gen.name}
            # ????  nf.gen.ent.name feels like it should be nf.fk.tar...
            # ...but that doesn't work in library example

        return list(qobjs.values())

class Merge(CQL):
    '''
    Combine information from i1 : src and i2 : tar such that a new instance
    of a third schema contains "full" information from both databases. For name
    collisions, we preserve the naming conventions of the src schema.
    '''
    def __str__(self)->str:
        return 'Merge<%s->%s>'%(self.src.name,self.tar.name)


    def sections(self, src_conn : Input, tar_conn : Input, merged_conn : Conn = None)-> L[CQLSection]:

        s1       = self.overlap.add_sql_attr(self.src)           # extra attributes added during landing, potentially
        t1       = self.overlap.add_sql_attr(self.tar,src=False) # extra attributes added during landing, potentially
        src      = s1.schema('src',self._ty,)
        tar      = t1.schema('tar',self._ty)

        srcneq      = s1.schema('src_no_cons',self._ty,pe=False)
        tarneq      = t1.schema('tar_no_cons',self._ty,pe=False)

        # Schemas which have extra info in them due to CQL queries
        schema_args1 = dict(typeside = 'ty',
                            entities = [e.ent.ent() for e in self.overlap.ne1.values()],
                            attrs    = [a.attr.attr() for a in self.overlap.na1],
                            fks      = [f.fk.fk() for f in self.overlap.nf1]) # type: dict
        schema_args2 = dict(typeside = 'ty',
                            entities = [e.ent.ent() for e in self.overlap.ne2.values()],
                            attrs    = [a.attr.attr() for a in self.overlap.na2],
                            fks      = [f.fk.fk() for f in self.overlap.nf2])# type: dict

        src2     = CQLSchema('src2',imports = [src], **schema_args1)
        tar2     = CQLSchema('tar2', imports = [tar],**schema_args2)

        src2neq = CQLSchema('src2_no_cons', imports = [srcneq],**schema_args1)
        tar2neq = CQLSchema('tar2_no_cons', imports = [tarneq],**schema_args2)

        l1,l2          = self._lands()
        isrc,src_sects = self._inst(1,'src',src_conn,s1,src,l1)
        itar,tar_sects = self._inst(2,'tar',tar_conn,self.tar,tar,l2,)

        Q1  = Query('Q1',src,src2,self.add_query_objs(s1))
        Q2  = Query('Q2',tar,tar2,self.add_query_objs(t1,src=False))
        ent_eqs = {**{e.ent.name:e.ent.name for e in
                         set(self.overlap.ne1.values()) | set(self.overlap.ne2.values())},
                   **self.overlap.entity_eqs()}

        rd = Rewrite(src2.rewrite_dict(self.overlap.entities,tar2))

        path_eqs = [PathEQ(a,b).patheq(rewrite=rd) for a,b in self.overlap.patheqs.items()]

        mrgargs  = dict(ent_eqs = {v:k for k,v in ent_eqs.items()},
                        path_eqs = path_eqs) # type: dict

        mrg_      = SchemaColimitQuotient(name='merged_',s1=tar2,s2=src2,
                                         **mrgargs)

        mrgneq   = SchemaColimitQuotient(name='merged_no_cons_',
                                          s1=tar2neq,s2=src2neq,**mrgargs)


        mrg    = self.overlap.modify(name  = 'merged_no_cons',sc = mrgneq)

        ssc      = GetSchema('s_merged',mrg_)
        sscneq   = GetSchema('s_merged_no_cons',mrg)

        isrc2  = EvalInstance('i_src2',Q1,isrc)
        itar2  = EvalInstance('i_tar2',Q2,itar)


        P1    = Include('P1',src2neq,src2)
        P2    = Include('P2',tar2neq,tar2)
        M1    = GetMapping('M1',mrg,src2neq)
        M2    = GetMapping('M2',mrg,tar2neq)

        isrc2neq = MapInstance('i_src_no_cons','delta',P1,isrc2)
        itar2neq = MapInstance('i_tar_no_cons','delta',P2,itar2)
        tmp1     = MapInstance('srctmp','sigma',M1,isrc2neq)
        tmp2     = MapInstance('tartmp','sigma',M2,itar2neq)
        imrgneq  = CoProdInstance('i_merged_no_con',tmp1,tmp2,sscneq)
        imrg     = DelInstance('i_merged',imrgneq,ssc)
        final    = self.tar.quotient('i_final',imrg)

        return [Title(0,0,'Set-up'),self.default, self._ty,
                Title(1,0,'Declare schemas'), src,tar,src2,tar2,srcneq,src2neq,tarneq,tar2neq,
                Title(1, name = 'Create source instance')] + src_sects + [
                Title(2, name = 'Create target instance')] + tar_sects + [
                Title(3, name = "Data integration"),
                Title(3,1,"Queries which add extra information when eval'd"), Q1, Q2, isrc2,itar2,
                Title(3,2,'Merging of schemas'), mrg_,mrgneq,mrg,ssc,sscneq,P1,P2,M1,M2,
                Title(3,3,'Merge instance data'),isrc2neq,itar2neq,tmp1,tmp2,imrgneq,imrg,
                Title(3, 4, 'Record linkages'), final,
                ] + self._export(4,merged_conn,final)

    def add_query_objs(self, querysrc : Schema, src : bool = True) -> L[QueryObj]:
        '''Simple construction of query by just injecting information in source
            and adding new information from overlap'''

        nes = self.overlap.ne1 if src else self.overlap.ne2
        nas = self.overlap.na1 if src else self.overlap.na2
        nfs = self.overlap.nf1 if src else self.overlap.nf2

        return [QueryObj(ent   = en,
                         gens  = [g.gen() for g in self.overlap.all_gens(en,src=src)],
                         attrs = {**{an:a.genattr() for an,a in e.attrs.items()},
                                  **{a.attr.name:a.expr.expr(querysrc) for a in nas
                                    if a.ent.name == en}},
                         fks   = {**{fkn:{fk.tar:en+'.'+fkn}
                                     for fkn,fk in e.fks.items()},
                                  **{nf.fk.name : {nf.fk.tar:nf.fk.name} for nf in nfs
                                        if nf.fk.src == en}}
                        )

                for en,e in querysrc.entities.items()] \
              + [ne.qobj(querysrc) for ne in nes.values()]
