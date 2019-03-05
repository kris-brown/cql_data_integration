# Internal imports
from cdi import (Migrate, Merge, Instance, Conn)

from cdi.science_example.inputs.catalysis     import rich
from cdi.science_example.inputs.oqmd          import oqmd, fOQMD
from cdi.science_example.inputs.javafuncs     import funcs
from cdi.science_example.inputs.overlap       import overlap
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
    merged_db, oqmd_db = [Conn(db=db) for db in ['cql_merged','oqmd']]


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
