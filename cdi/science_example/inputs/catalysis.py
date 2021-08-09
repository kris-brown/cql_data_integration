# Internal
from cdi import (
    Schema, Entity, Attr, FK, Int,Decimal,Double,Varchar,Text,
    Date, PathEQ, Path, JLit, String, Gen, Boolean, EQ)

from ..inputs.javafuncs import gteq
################################################################################
#############
# Catalysis #
#############

job = Entity(
    name = 'job',
    desc = 'DFT job',
    attrs= [Attr('stordir',  Varchar, desc = 'Directory containing log file', id=True),
            Attr('job_name', Varchar, desc = 'Name of job - arbitrary'),
            Attr('user',     Varchar, desc = 'Owner of job'),
            Attr('energy',   Double,  desc = 'Energy result of job')],
    fks = [FK('struct'), FK('calc')]
)

elem = Entity(
    name  = 'element',
    desc  = 'chemical element',
    attrs = [Attr('atomic_number',            desc = '# of protons', id = True),
             Attr('symbol',          Varchar, desc = 'E.g. He, K, Li'),
             Attr('name',            Varchar)]
)

species = Entity(
    name = 'species',
    desc = """Abstraction of a struct which throws away position info.
             Composition is a python dictionary mapping atomic number
             to NORMALIZED stoich""",
    attrs = [Attr('phase',   Varchar,          desc = 'bulk,molecule,surface,liquid'),
             Attr('formula', Varchar, id=True, desc = 'Stringified python dict (ordered, normalized)'),
             Attr('symmetry',Varchar, id=True, desc = '''For molecules, pointgroup;
                                                        for bulks, Prototype name; for surfaces,
                                                        underlying prototype+facet''')]
)

##################################################################################
cellinit = [Attr(x,Decimal,id=True) for x in [a+b for a in 'abc' for b in '123']]
noninit  = ['a','b','c','volume']

cell = Entity(
    name  = 'cell',
    desc  = 'Periodic cells defined by three vectors (all units Angstrom)',
    attrs = cellinit + [Attr(x,Decimal) for x in noninit]
)
###################################################################################

calc = Entity(
    name  = 'calc',
    desc  = 'DFT calc parameters',
    attrs = [Attr('dftcode',Varchar, id = True, desc = 'VASP/GPAW/QuantumEspresso'),
             Attr('xc',     Varchar, id = True, desc = 'PBE/RPBE/BEEF/etc.'),
             Attr('pw',     Double,  id = True, desc = 'Planewave cutoff, eV'),
             Attr('psp',    Varchar, id = True, desc = 'Pseudopotential name')]
)

struct = Entity(
    name  = 'struct',
    desc  = 'Chemical structure defined in periodic cell',
    attrs = [Attr('raw',        Text,id=True,desc = 'JSON encoding of ASE atoms object'),
             Attr('system_type',Varchar,     desc = 'One of: bulk, molecule, surface'),
             Attr('composition',Varchar,     desc = "Stringified Python dictionary of stoich"),
             Attr('n_atoms',                 desc = 'Number of atoms in structure')],
    fks = [FK('cell'), FK('species')]
)

atom = Entity(
    name  = 'atom',
    desc  = 'An atom, considered within a specific chemical structure',
    attrs = [Attr('ind',id=True,  desc = 'ASE atom index'),
             Attr('number',       desc = 'Atomic number'),
             Attr('x', Decimal,   desc = 'x position'),
             Attr('y', Decimal,   desc = 'y position'),
             Attr('z', Decimal,   desc = 'z position')],
    fks  = [FK('struct', id = True),FK('element')]
)

struct_comp = Entity(
    name  = 'struct_composition',
    desc  = 'Mapping table between struct and element to show composition',
    attrs = [Attr('num',desc='Number of this element')],
    fks   = [FK('struct', id = True), FK('element', id = True)]
)

bulk = Entity(
    name = 'bulk',
    desc = 'Subset of Struct: periodicity in 3 dimensions',
    fks  = [FK('struct', id = True)]
)

mol = Entity(
    name  = 'molecule',
    desc  = 'Subset of struct: periodicity in 0 dimensions',
    attrs = [Attr('pointgroup', Varchar)],
    fks   = [FK('struct', id = True)]
)

surf = Entity(
    name  = 'surface',
    desc  = 'Subset of struct: periodicity in 1 or 2 dimensions',
    attrs = [Attr('facet', Varchar, desc = "Autodetected facet"),
             Attr('vacuum',Decimal, desc = 'Layer separation (Angstrom)')],
    fks   = [FK('struct', id=True)]
)

rich_objs = [job, elem, species, struct, cell, atom, calc, struct_comp, bulk, mol, surf]

################################################################################
# Path Equations
################
b0,m0,s0 = Gen('b0',bulk),Gen('m0',mol),Gen('s0',surf)
st0,a0 = Gen('st0',struct), Gen('a0',atom)

rich_pe = [
    PathEQ(Path(atom['number']),
           Path(atom['element'], elem['atomic_number'])),

    PathEQ(Path(b0['struct'], struct['system_type']),
           Path(JLit('bulk', String))),

    PathEQ(Path(m0['struct'], struct['system_type']),
           Path(JLit('molecule', String))),

    PathEQ(Path(s0['struct'], struct['system_type']),
           Path(JLit('surface', String))),

    PathEQ(Path(st0['species'],species['phase']),
           Path(st0['system_type'])),

    PathEQ(Path(gteq(a0['x'],JLit("0.000",Double))),
           Path(JLit('true',Boolean)))
]

rich = Schema('catalysis', rich_objs, rich_pe)
