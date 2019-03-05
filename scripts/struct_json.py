from json import dumps,loads,dump
from sys  import argv

def oqmd_data_to_json(symbs : str, xs : str, ys : str, zs : str, cell : list) -> str:
    """
    Serialize an Atoms object in a human-readable way
    """
    symlist = ['X', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs', 'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og']

    def roundfloat(xs: str) -> list:
        return [round(float(x), 3) for x in xs.split(',') if x]

    # preprocess data
    nums = [symlist.index(x) for x in symbs.split(',') if x]
    xx,yy,zz, = map(roundfloat,[xs,ys,zs])
    rounded_cell = [round(float(x), 3) for x in cell]
    atomdata = [] # initialize result list
    for i,(num,x,y,z) in enumerate(zip(nums,xx,yy,zz)):
        atomdata.append({'number' : num, 'x' : x, 'y' : y, 'z' : z,
                         'magmom'       : None,
                         'tag'          : None,
                         'constrained'  : 0,
                         'index'        : i})

    # process cell
    out = {'cell': [[rounded_cell[3*i+j] for j in range(3)] for i in range(3)]
          ,'atomdata':atomdata}

    return dumps(out)


if __name__ == '__main__':
    nums,xs,ys,zs = argv[1:5]
    cell = argv[5:]
    print(oqmd_data_to_json(nums,xs,ys,zs,cell))
