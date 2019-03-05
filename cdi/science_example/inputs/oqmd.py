# External
from typing import Dict as D

# Internal
from cdi import (
    Schema, Entity, Attr, FK, Int,Tinyint,Double,Varchar,Text,Date,
    PathEQ,Path,flatten, Zero, IN, Literal as Lit,LT,SQLExpr)

################################################################################

journals = Entity(
    name  = 'journals',
    id    = 'id',
    attrs = [Attr('code', Varchar, id = True),
             Attr('name', Text)]
)

authors = Entity(
    name  = 'authors',
    id    = 'id',
    attrs = [Attr('last', Varchar,id = True),
             Attr('first',Varchar,id = True)]
)

rots = Entity(
    name  = 'rotations',
    id    = 'id',
    attrs = [Attr('a%d%d'%(i,j),Double,id=True)
              for i in range(3) for j in range(3)]
)

trans = Entity(
    name  = 'translations',
    id    = 'id',
    attrs = [Attr(x, Double, id=True) for x in 'xyz']
)

operations = Entity(
    name  = 'operations',
    id    = 'id',
    fks   = [FK('rotation_id',    'rotations',    id = True),
             FK('translation_id', 'translations', id = True)])

elems = Entity(
    name  = 'elements',
    id    ='z',
    attrs = [Attr('z',      Int,      desc = 'atomic number', id = True),
             Attr('name',   Varchar,  desc = 'full atomic name'),
             Attr('symbol', Varchar,  desc = 'atomic symbol'),
             Attr('group',),
             Attr('period',),
             Attr('mass',         Double),
             Attr('specific_heat',Double),
             Attr('s_elec',),
             Attr('p_elec',),
             Attr('d_elec',),
             Attr('f_elec',)]
)

hubbards = Entity(
    name  = 'hubbards',
    id    = 'id',
    attrs = [Attr('convention',Varchar),
             Attr('ox',        Double, desc = 'Oxidation state'),
             Attr('u',         Double),
             Attr('l')],
    fks   = [FK('element_id','elements', id = True),
             FK('ligand_id','elements')]
)

species = Entity(
    name  = 'species',
    id    = 'name',
    desc  = 'An atomic species (Element + charge state).',
    attrs = [Attr('name',Varchar,id = True),
             Attr('ox',  Double, id = True)],
    fks   = [FK('element_id','elements',id = True, desc = 'Oxidation state')]
)

md = Entity(
    name  = 'meta_data',
    id    ='id',
    attrs = [Attr('type', Varchar,id = True),
             Attr('value',Text,   id = True)]
)
####################################################################
sgcols = ['hm','hall','pearson','schoenflies']

sg = Entity(
    name  = 'spacegroups',
    id    = 'number',
    attrs = [Attr('number',id = True),
             Attr('centrosymmetric',   Tinyint),
             Attr('lattice_system',    Varchar)] +
            [Attr(x,Varchar) for x in sgcols]
)

####################################################################
comp = Entity(
    name  = 'compositions',
    id    = 'formula',
    attrs = [Attr('formula',Varchar,  desc = 'Electronegativity sorted and normalized composition string: e.g. Fe2O3, LiFeO2' , id = True),
             Attr('generic', Varchar, desc = 'Genericized composition string. e.g. A2B3, ABC2', id = True),
             Attr('ntypes',  Int,     desc = 'Number of elements'),
             Attr('meidema', Double,  desc = 'Meidema model energy for the composition')]
)

ces = Entity(
    name = 'compositions_element_set',
    id   ='id',
    fks  = [FK('composition_id','compositions',id = True),
            FK('Element_id',    'elements',    id = True)]
)

####################################################################
pubcols = ['page_first','page_last','year','volume']
pubs = Entity(
    name  = 'publications',
    id    = 'id',
    attrs = [Attr('title',Text, id = True)]+[Attr(x) for x in pubcols],
    fks   = [FK('journal_id','journals')]
)
####################################################################
pas = Entity(
    name = 'publications_author_set',
    id   ='id',
    fks  = [FK('reference_id','publications',id = True),
            FK('author_id',      'authors',  id = True)]
)

entries = Entity(
    name  = 'entries',
    id    = 'id',
    desc  ='''An Entry model represents an input structure to the database, and
              can be created from any input file. The Entry also ties together all
              of the associated qmpy.structure, qmpy.Calculation, qmpy.Reference,
              qmpy.FormationEnergies, and other associated database entries.''',
    attrs = [Attr('path',        Varchar, id=True),
             Attr('delta_e',     Double),
             Attr('stability',   Double),
             Attr('label',       Varchar),
             Attr('duplicate_of_id'),
             Attr('natoms', desc='Number of atoms in the primitive input cell')],
    fks   = [FK('reference_id','publications',)]
)

ees = Entity(
    name = 'entries_element_set',
    id   ='id',
    fks  = [FK('entry_id','entries',   id = True),
            FK('element_id','elements',id = True)]
)

ess = Entity(
    name = 'entries_species_set',
    id   = 'id',
    fks  = [FK('species_id','species', id = True),
            FK('entry_id',  'entries', id = True)]
)

emd = Entity(
    name = 'entries_meta_data',
    id   = 'id',
    fks  = [FK('entry_id',   'entries',  id = True),
            FK('metadata_id','meta_data',id = True)]
)

####################################################################
s_doubles = ['volume','volume_pa','energy','energy_pa','magmom','magmom_pa','delta_e','meta_stability',
            ]+[x+str(y) for x in 'xyz' for y in range(1,4)]            #'sxx','syy','szz','sxy','syz','szx']


s_ints = ['natoms','nsites','ntypes']

structs = Entity(
    name  = 'structures',
    id    = 'id',
    desc  = 'Structure model. Principal attributes are a lattice and basis set',
    attrs = [Attr('label',    Varchar, desc='key in the Entry.structures dictionary', id=True),
             Attr('measured', Tinyint)] +
            [Attr(x) for x in s_ints] + [Attr(x,Double) for x in s_doubles],

    fks   = [FK('entry_id',     'entries',id=True),
             FK('spacegroup_id','spacegroups')]
)
####################################################################
calc = Entity(
    name  = 'calculations',
    id    = 'id',
    desc  = 'A VASP calculation',
    attrs = [Attr('natoms',  Int),
             Attr('energy',  Double),
             Attr('magmom',  Double),
             Attr('path',    Varchar, id=True),
             Attr('band_gap',Double),
             Attr('nsteps',  Int,       desc = '# of ionic steps'),
             Attr('attempt',            desc = '# of this attempt at a calculation.'),
             Attr('converged',Tinyint,  desc = 'Did the calculation converge electronically and ionically.'),
             Attr('runtime',  Double,   desc = 'Runtime in seconds'),
             Attr('label',    Varchar,  desc = 'key for entry.calculations dict.'),
             Attr('settings', Text,     desc = 'dictionary of VASP settings'),
             Attr('configuration',Varchar, desc='Type of calculation (module).')],

    fks   = [FK('composition_id','compositions'),
             FK('entry_id',      'entries',),
             FK('input_id',      'structures'),
             FK('output_id',     'structures')]
)

cmd = Entity(
    name = 'calculations_meta_data',
    id   = 'id',
    fks  = [FK('calculation_id','calculations',id=True),
            FK('metadata_id',   'meta_data',   id=True)]
)

caes = Entity(
    name = 'calculations_element_set',
    id   = 'id',
    fks  = [FK('calculation_id','calculations',id=True),
            FK('element_id',    'elements',    id=True)]
)

sites = Entity(
    name  = 'sites',
    id    = 'id',
    desc  = 'A lattice site, occupied by one Atom, many Atoms or no Atoms',
    attrs = [Attr(x, Double, id=True) for x in 'xyz'],
    fks   = [FK('structure_id','structures',)]
)

proto = Entity(
    name = 'prototypes',
    id   = 'name',
    fks  = [FK('structure_id',  'structures',  id=True),
            FK('composition_id','compositions',id=True)]
)

###################################################################
wcols   = ['x','y','z','symbol']
wyckoff = Entity(
    name  = 'Wyckoffsites',
    id    = 'id',
    attrs = [Attr('multiplicity', id=True)]
             +[Attr(x,Varchar, id=True) for x in wcols],
    fks = [FK('spacegroup_id','spacegroups',id=True)]
)

####################################################################
acols = ['x','y','z','fx','fy','fz','magmom','charge']

atoms = Entity('atoms',id='id',desc='An atom in a DFT calculated structure',
            attrs = [Attr(x,Double,id=True) for x in acols],
            fks = [FK('structure_id', 'structures',),
                   FK('site_id',      'sites',),
                   FK('element_id',   'elements',),])

####################################################################
jobs = Entity(
    name  = 'jobs',
    id    = 'id',
    attrs = [Attr('qid', id=True),
             Attr('path',     Varchar),
             Attr('run_path', Varchar),
             Attr('ncpus',),
             Attr('created',  Date),
             Attr('state',),],
    fks   = [FK('entry_id','entries')]
)

ses = Entity(
    name = 'structures_element_set',
    id   = 'id',
    fks = [FK('structure_id','structures',id = True),
           FK('element_id',  'elements',  id = True)]
)

smd = Entity(
    name = 'structures_meta_data',
    id   ='id',
    fks  = [FK('structure_id','structures',id = True),
            FK('metadata_id', 'meta_data', id = True),]
)

sss = Entity(
    name = 'structures_species_set',
    id   = 'id',
    fks  = [FK('structure_id','structures',id = True),
            FK('species_id',  'species',   id = True),]
)

fits = Entity(
    name  = 'fits',
    id    = 'name',
    desc  = 'a reference energy fitting scheme.',
    attrs = [Attr('name', Varchar, id=True)]
)

fd  = Entity(
    name = 'fits_dft',
    id   = 'id',
    fks  = [FK('fit_id',        'fits',         id = True),
            FK('calculation_id','calculations', id = True),]
)

re = Entity(
    name  = 'reference_energies',
    id    = 'id',
    desc  = 'Elemental reference energy for evaluating heats of formation',
    attrs = [Attr('value', Double, desc = 'Reference energy (eV/atom)')],
    fks   = [FK('fit_id',    'fits',    id = True),
             FK('element_id','elements',id = True)]
)

####################################################################
hcs     = ['fits','elements','hubbards']

hc = Entity(
    name  = 'hubbard_corrections',
    id    = 'id',
    desc  = 'Energy correction for DFT+U energies',
    attrs = [Attr('value',Double, desc = 'Correction energy (eV/atom)')],
    fks   = [FK(x[:-1]+'_id', x, id = True) for x in hcs]
)

####################################################################
objs = [journals,authors,elems,hubbards,species,md,sg,comp,
        ces,pubs,pas,entries,ees,emd,structs,calc,cmd,caes,sites,proto,
        atoms,ses,smd,sss,fits,fd,re,hc,ess]

pes = [
    PathEQ(Path(atoms['structure_id']),
           Path(atoms['site_id'], sites['structure_id'])),

    PathEQ(Path(calc['energy']),
           Path(calc['output_id'], structs['energy'])),

    PathEQ(Path(calc['natoms']),
           Path(calc['input_id'],structs['entry_id'],entries['natoms'])),

    PathEQ(Path(calc['output_id'],structs['entry_id']),
           Path(calc['input_id'], structs['entry_id']))]


oqmd = Schema('oqmd',objs,pes)

################################################################################
###############################
# 2: Filter on records landed #
###############################

# don't include any records by default
default = {o:Zero for o in oqmd.entities.values()} # type: D[Entity,SQLExpr]

# Allow in specific records

fOQMD = {**default,
         **{calc    : calc.id    |IN| [Lit(3187)],
            atoms   : atoms.id   |IN| [Lit(203277)],
            elems   : elems['z'] |LT| Lit(84),
            structs : structs.id |IN| [Lit(15133),Lit(1638)]} # 2018503
        }
