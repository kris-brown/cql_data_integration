# External
from typing import List as L, Dict as D
# Internal
from cdi.science_example.inputs.oqmd      import oqmd,calc as calcs,structs,atoms,elems
from cdi.science_example.inputs.catalysis import rich,job,elem,calc,struct,cell,atom
from cdi.science_example.inputs.javafuncs import cat,countsubstr,gt,mcd,msj,bigint_to_int
from cdi import (
    Overlap,Entity,PathEQ,Path,Gen,SQLAttr,NewAttr,NewEntity, Attr,FK,EQ,Long,
    toDecimal,Int,Text,String,Bigint,Varchar,Boolean,Double,Decimal,Sum,Literal,
    CONCAT,SUBSELECT,GROUP_CONCAT,JLit,SQLExpr,REPLACE,JSON_EXTRACT,MIN)


################################################################################
# Helpers for Path equalities
#---------------------------

def Rename_attrs(obj1 : Entity, obj2 : Entity, attrs : D[str, str]) -> L[PathEQ]:
    '''Shorthand function for identifying columns/FKs of two entities'''
    return [PathEQ(Path(obj1[col1]), Path(obj2[col2]))
                for col1,col2 in attrs.items()]

def ID_attrs(obj1 : Entity, obj2 : Entity, attrs : L[str]) -> L[PathEQ]:
    '''Rename_attrs in the case when the attribute/FK has the same name'''
    return Rename_attrs(obj1,obj2,{col:col for col in attrs})


# E.g. a1 -> x1, b2 -> y2, c -> c, volume -> volume
cell_dict = {**{a+i:b+i for a,b in zip('xyz','abc') for i in '123'},
             **{x:x for x in ['volume','a','b','c']}}


# Helpers for SQL statements
#---------------------------
compexpr = SUBSELECT(GROUP_CONCAT(atoms['element_id']),
                                  tab   = 'atoms A',
                                  where = 'A.structure_id = atoms.structures.id')

#(SELECT MIN(`id`) FROM atoms A WHERE A.structure_id=atoms.structure_id )

def readJSON(key : str) -> SQLExpr:
    '''
    Read a OQMD json file, which has some peculiarities (strings have single
    rather than double quotes, 'True' and 'False' are upper case)
    '''
    e : SQLExpr    = calcs['settings']
    replacedict = {'True':'true', 'False':'false', "'":'"'}

    for a,b in replacedict.items():
        e = REPLACE(e, Literal(a), Literal(b))

    return JSON_EXTRACT(e, Literal('$.%s'%key))

compexpr = SUBSELECT(GROUP_CONCAT(atoms['element_id']),
                     tab='atoms',where='structure_id = structures.id')

atoms_ind = atoms['id'] - SUBSELECT(MIN(atoms['id']),tab='atoms A',where='A.structure_id=atoms.structure_id')

xs,ys,zs = [SUBSELECT(GROUP_CONCAT(atoms[x]),
                     tab='atoms',where='structure_id = structures.id')
            for x in 'xyz']

calc_constants = dict(dftcode='vasp',xc='PBE',user='OQMD')

# Generators for CQL expressions
#-------------------------------
s0 = Gen('s0',structs)
l0 = Gen('e0',elems)


# Helpers for CQL expressions
#---------------------------
zero = JLit('0',Int) # java literal

elemcount = countsubstr(s0['comp'], cat(l0['symbol'], JLit(',',String)))

msj_kwargs = ['comp','xs','ys','zs'] + [a+b for a in 'xyz' for b in '123']
msj_args   = [structs[x] for x in msj_kwargs]

# Specification of overlap
#------------------------

overlap = Overlap(s1=oqmd, s2=rich,

    paths=[
            # Path equalities specified one at a time
            #----------------------------------------
            PathEQ(Path(elems['z']),Path(elem['atomic_number'])),

            # Path Equalities defined with some sort of loop
            #-----------------------------------------------
        ] + ID_attrs(calcs,job, ['energy','user','job_name'])                   \
          + ID_attrs(atoms,atom,['x','y','z','ind'])                            \
          + ID_attrs(elems,elem,['symbol','name'])                              \
          + Rename_attrs(calcs,job,{'path':'stordir','output_id':'struct'})     \
          + Rename_attrs(structs,struct,{'natoms'       : 'n_atoms',
                                         'system_type'  : 'system_type'})       \
          + Rename_attrs(atoms,atom,{'structure_id' : 'struct',
                                         'element_id'   : 'element'})           \
         + [PathEQ(Path(calcs[col]),
                    Path(job['calc'],calc[col]))
              for col in ['dftcode','xc','pw','psp']
        ]
          + [PathEQ(Path(structs[struct_col]),
                    Path(struct['cell'], cell[cell_col]))
              for struct_col,cell_col in cell_dict.items()
        ],

    sql_attr1 = [
        # Attributes computed in SQL upon landing
        #----------------------------------------
        SQLAttr(calcs, 'psp',     Varchar, readJSON('potentials')),
        SQLAttr(calcs, 'pw',      Decimal, toDecimal(readJSON('encut'))),
        SQLAttr(calcs, 'job_name',Varchar, CONCAT(Literal('oqmd - '),
                                                  calcs['label'])),

        SQLAttr(structs,'comp',        String, CONCAT(compexpr,Literal(','))),
        SQLAttr(structs,'system_type', Varchar, Literal('bulk')),

        SQLAttr(atoms,  'bigind',    Bigint,   atoms_ind),
        SQLAttr(structs,'xs',     String, xs),
        SQLAttr(structs,'ys',     String, ys),
        SQLAttr(structs,'zs',     String, zs)

        # More SQL attributes, defined with loops
        #----------------------------------

            # Compute the L² Norm of three 3D vectors
       ] + [SQLAttr(structs,abc,Double,
                    Sum([structs['%s%d'%(xyz,i)] ** Literal(2)
                          for i in range(1,4)]) ** Literal(0.5))
            for abc,xyz in zip('abc','xyz')

       ] + [SQLAttr(calcs,attr,Varchar,Literal(constval))
            for attr,constval in calc_constants.items()],

    # Attrs computed in CQL (can use Java functions + info from multiple tables)
    #---------------------------------------------------------------------------
    new_attr1 = [NewAttr(structs,'composition',  String, mcd(structs['comp'])),
                 NewAttr(structs,'raw',          Text,   msj(*msj_args)),
                 NewAttr(atoms,'ind',Int,bigint_to_int(atoms['bigind']))],

    # New Entities computed in CQL
    #-----------------------------
    new_ent1  = [NewEntity(name  = 'struct_composition',
                           gens  = [s0, l0],
                           where = [EQ(gt(elemcount, zero) , JLit('true',Boolean))],
                           attrs = {Attr('num',Int) : elemcount},
                           fks   = {FK('struct','structures') : s0,
                                    FK('element','elements')  : l0}),

                NewEntity(name = 'bulk',
                          gens = [s0],
                          fks  = {FK('struct','structures') : s0})]

)
