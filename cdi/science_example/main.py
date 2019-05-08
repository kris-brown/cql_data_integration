# Internal imports
from cdi import (Migrate, Merge, Instance, Conn)

from .inputs.catalysis     import rich
from .inputs.oqmd          import oqmd, fOQMD
from .inputs.javafuncs     import funcs
from .inputs.overlap       import overlap
################################################################################

oqmd = oqmd.remove_obj('species') # this one poses some problems for merging


def main()->None:
    '''
    Specify overlap between two materials databases, produce CQL files which
    can merge and migrate data
    '''
    ###########################
    # DBs used in the process #
    ###########################
    merged_db = Conn(db   = 'integrated')
    oqmd_db   = Conn(host = 'mysql.categoricaldata.net',
                     db   = 'qchem',
                     user = 'qchem_public',
                     pw   = 'quantumchemistry')


    root = 'cdi/science_example/outputs/'

    args = dict(src     = oqmd,
                tar     = rich,
                overlap = overlap,
                filt1   = fOQMD,
                funcs   = funcs) # type: dict

    fi1  = Migrate(**args).file(src = oqmd_db, tar = Instance(), merged = merged_db)

    fi2  = Merge(**args).file(src = oqmd_db, tar = Instance(), merged = merged_db)


    with open(root+'migrate.cql','w') as f: f.write(fi1)
    with open(root+'merge.cql',  'w') as f: f.write(fi2)

################################################################################
if __name__=='__main__':
    main()
