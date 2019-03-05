//-----------------
//Section 0: Set-up
//-----------------


options
    gui_max_graph_size    = 100000000
    gui_max_table_size    = 100000000
    timeout               = 3600
    jdbc_quote_char       = "`"
    allow_java_eqs_unsafe = True


typeside ty = literal { 
    imports
        sql



    java_functions
        cat : String,String -> String
             = "return input[0] + input[1]"

        makeStructJSON : String,String,String,String,Double,Double,Double,Double,Double,Double,Double,Double,Double -> Text
             = "var MS = Java.type(\"str_utils.makeStructJSON\"); return MS.run(input[0],input[1],input[2],input[3],input[4],input[5],input[6],input[7],input[8],input[9],input[10],input[11],input[12]); "

        matches : String,String -> Boolean
             = "return input[0].matches(input[1])"

        bigint_to_int : Bigint -> Integer
                      = "return  input[0].intValue();"

        makeCompositionDict : String -> String
             = "var CD = Java.type(\"str_utils.makeCompositionDict\"); return CD.run(input[0]);"

        decimal_to_float : Double -> Float
                         = "return input[0].floatValue()"

        gt   : Integer,Integer -> Boolean
             = "return input[0] > input[1]"

        countsubstr : String,String -> Integer
             = "return input[0].split(input[1], -1).length-1"

        gteq : Double,Double -> Boolean
             = "return input[0] >= input[1]" }


//--------------------------
//Section 1: Declare schemas
//--------------------------


schema src = literal : ty { 

    entities
    //------

        journals
        authors
        elements
        hubbards
        meta_data
        spacegroups
        compositions
        compositions_element_set
        publications
        publications_author_set
        entries
        entries_element_set
        entries_meta_data
        structures
        calculations
        calculations_meta_data
        calculations_element_set
        sites
        prototypes
        atoms
        structures_element_set
        structures_meta_data
        fits
        fits_dft
        reference_energies
        hubbard_corrections

    foreign_keys
    //------

        metadata_id    : calculations_meta_data   -> meta_data 
        site_id        : atoms                    -> sites 
        element_id     : atoms                    -> elements 
        entry_id       : entries_meta_data        -> entries 
        calculation_id : fits_dft                 -> calculations 
        input_id       : calculations             -> structures 
        element_id     : hubbards                 -> elements 
        composition_id : compositions_element_set -> compositions 
        Element_id     : compositions_element_set -> elements 
        ligand_id      : hubbards                 -> elements 
        author_id      : publications_author_set  -> authors 
        structure_id   : structures_element_set   -> structures 
        element_id     : reference_energies       -> elements 
        reference_id   : entries                  -> publications 
        structure_id   : structures_meta_data     -> structures 
        metadata_id    : structures_meta_data     -> meta_data 
        reference_id   : publications_author_set  -> publications 
        entry_id       : structures               -> entries 
        element_id     : calculations_element_set -> elements 
        spacegroup_id  : structures               -> spacegroups 
        journal_id     : publications             -> journals 
        composition_id : calculations             -> compositions 
        composition_id : prototypes               -> compositions 
        fit_id         : hubbard_corrections      -> fits 
        element_id     : hubbard_corrections      -> elements 
        entry_id       : entries_element_set      -> entries 
        calculation_id : calculations_element_set -> calculations 
        element_id     : entries_element_set      -> elements 
        fit_id         : fits_dft                 -> fits 
        hubbard_id     : hubbard_corrections      -> hubbards 
        fit_id         : reference_energies       -> fits 
        output_id      : calculations             -> structures 
        structure_id   : prototypes               -> structures 
        calculation_id : calculations_meta_data   -> calculations 
        metadata_id    : entries_meta_data        -> meta_data 
        entry_id       : calculations             -> entries 
        structure_id   : atoms                    -> structures 
        element_id     : structures_element_set   -> elements 
        structure_id   : sites                    -> structures 



    attributes
    //------

        magmom_pa       : structures          -> Double 
        name : fits                           -> String 
        f_elec          : elements            -> Integer 
        natoms          : calculations        -> Integer 
        z3              : structures          -> Double 
        group           : elements            -> Integer 
        d_elec          : elements            -> Integer 
        page_last       : publications        -> Integer 
        stability       : entries             -> Double 
        natoms          : structures          -> Integer 
        path : entries                        -> String 
        generic : compositions                -> String 
        year            : publications        -> Integer 
        settings        : calculations        -> Text 
        period          : elements            -> Integer 
        nsteps          : calculations        -> Integer 
        b               : structures          -> Double 
        value           : hubbard_corrections -> Double 
        z2              : structures          -> Double 
        comp : structures                     -> String 
        user : calculations                   -> String 
        nsites          : structures          -> Integer 
        energy_pa       : structures          -> Double 
        attempt         : calculations        -> Integer 
        number          : spacegroups         -> Integer 
        convention : hubbards                 -> String 
        ntypes          : compositions        -> Integer 
        path : calculations                   -> String 
        schoenflies : spacegroups             -> String 
        z               : sites               -> Double 
        x               : atoms               -> Double 
        duplicate_of_id : entries             -> Integer 
        x2              : structures          -> Double 
        meidema         : compositions        -> Double 
        label : entries                       -> String 
        y3              : structures          -> Double 
        pearson : spacegroups                 -> String 
        xs : structures                       -> String 
        magmom          : atoms               -> Double 
        y1              : structures          -> Double 
        x               : sites               -> Double 
        energy          : calculations        -> Double 
        band_gap        : calculations        -> Double 
        label : structures                    -> String 
        converged       : calculations        -> Boolean 
        type : meta_data                      -> String 
        measured        : structures          -> Boolean 
        z               : elements            -> Integer 
        volume          : publications        -> Integer 
        lattice_system : spacegroups          -> String 
        ntypes          : structures          -> Integer 
        formula : compositions                -> String 
        y               : atoms               -> Double 
        magmom          : structures          -> Double 
        mass            : elements            -> Double 
        first : authors                       -> String 
        specific_heat   : elements            -> Double 
        a               : structures          -> Double 
        xc : calculations                     -> String 
        s_elec          : elements            -> Integer 
        hm : spacegroups                      -> String 
        delta_e         : structures          -> Double 
        job_name : calculations               -> String 
        volume          : structures          -> Double 
        dftcode : calculations                -> String 
        y2              : structures          -> Double 
        runtime         : calculations        -> Double 
        x3              : structures          -> Double 
        label : calculations                  -> String 
        system_type : structures              -> String 
        symbol : elements                     -> String 
        configuration : calculations          -> String 
        title           : publications        -> Text 
        z1              : structures          -> Double 
        pw              : calculations        -> Double 
        charge          : atoms               -> Double 
        psp : calculations                    -> String 
        hall : spacegroups                    -> String 
        ys : structures                       -> String 
        u               : hubbards            -> Double 
        ox              : hubbards            -> Double 
        magmom          : calculations        -> Double 
        bigind          : atoms               -> Bigint 
        z               : atoms               -> Double 
        natoms          : entries             -> Integer 
        meta_stability  : structures          -> Double 
        value           : meta_data           -> Text 
        last : authors                        -> String 
        page_first      : publications        -> Integer 
        c               : structures          -> Double 
        l               : hubbards            -> Integer 
        centrosymmetric : spacegroups         -> Boolean 
        x1              : structures          -> Double 
        name            : journals            -> Text 
        energy          : structures          -> Double 
        fx              : atoms               -> Double 
        code : journals                       -> String 
        delta_e         : entries             -> Double 
        zs : structures                       -> String 
        value           : reference_energies  -> Double 
        y               : sites               -> Double 
        volume_pa       : structures          -> Double 
        p_elec          : elements            -> Integer 
        name : elements                       -> String 
        fz              : atoms               -> Double 
        fy              : atoms               -> Double 

 
}


schema tar = literal : ty { 

    entities
    //------

        job
        element
        species
        struct
        cell
        atom
        calc
        struct_composition
        bulk
        molecule
        surface

    foreign_keys
    //------

        element : atom               -> element 
        cell    : struct             -> cell 
        struct  : struct_composition -> struct 
        struct  : molecule           -> struct 
        struct  : job                -> struct 
        struct  : atom               -> struct 
        calc    : job                -> calc 
        species : struct             -> species 
        struct  : surface            -> struct 
        struct  : bulk               -> struct 
        element : struct_composition -> element 

    path_equations
    //------

        atom.number = atom.element . atomic_number

    attributes
    //------

        xc : calc                          -> String 
        stordir : job                      -> String 
        c1            : cell               -> Double 
        raw           : struct             -> Text 
        system_type : struct               -> String 
        b3            : cell               -> Double 
        a2            : cell               -> Double 
        name : element                     -> String 
        symmetry : species                 -> String 
        b             : cell               -> Double 
        psp : calc                         -> String 
        x             : atom               -> Double 
        c3            : cell               -> Double 
        phase : species                    -> String 
        y             : atom               -> Double 
        energy        : job                -> Double 
        pointgroup : molecule              -> String 
        a             : cell               -> Double 
        atomic_number : element            -> Integer 
        a3            : cell               -> Double 
        z             : atom               -> Double 
        number        : atom               -> Integer 
        pw            : calc               -> Double 
        num           : struct_composition -> Integer 
        composition : struct               -> String 
        vacuum        : surface            -> Double 
        formula : species                  -> String 
        ind           : atom               -> Integer 
        b2            : cell               -> Double 
        dftcode : calc                     -> String 
        symbol : element                   -> String 
        n_atoms       : struct             -> Integer 
        c             : cell               -> Double 
        a1            : cell               -> Double 
        job_name : job                     -> String 
        facet : surface                    -> String 
        c2            : cell               -> Double 
        volume        : cell               -> Double 
        user : job                         -> String 
        b1            : cell               -> Double 

    observation_equations
    //------

        forall s0 : surface . system_type(s0.struct) = "bulk"@String
        forall b0 : bulk . system_type(b0.struct) = "bulk"@String
        forall st0 : struct . phase(st0.species) = st0.system_type
        forall m0 : molecule . system_type(m0.struct) = "molecule"@String
        forall a0 : atom . gteq(a0.x,"0.000"@Double) = "true"@Boolean 
}


schema src2 = literal : ty {     imports
    //------

        src

    entities
    //------

        bulk
        struct_composition

    foreign_keys
    //------

        struct  : struct_composition -> structures 
        element : struct_composition -> elements 
        struct  : bulk               -> structures 



    attributes
    //------

        num : struct_composition -> Integer 
        raw : structures         -> Text 
        composition : structures -> String 
        ind : atoms              -> Integer 

 
}


schema tar2 = literal : ty {     imports
    //------

        tar









 
}


schema src_no_cons = literal : ty { 

    entities
    //------

        journals
        authors
        elements
        hubbards
        meta_data
        spacegroups
        compositions
        compositions_element_set
        publications
        publications_author_set
        entries
        entries_element_set
        entries_meta_data
        structures
        calculations
        calculations_meta_data
        calculations_element_set
        sites
        prototypes
        atoms
        structures_element_set
        structures_meta_data
        fits
        fits_dft
        reference_energies
        hubbard_corrections

    foreign_keys
    //------

        metadata_id    : calculations_meta_data   -> meta_data 
        site_id        : atoms                    -> sites 
        element_id     : atoms                    -> elements 
        entry_id       : entries_meta_data        -> entries 
        calculation_id : fits_dft                 -> calculations 
        input_id       : calculations             -> structures 
        element_id     : hubbards                 -> elements 
        composition_id : compositions_element_set -> compositions 
        Element_id     : compositions_element_set -> elements 
        ligand_id      : hubbards                 -> elements 
        author_id      : publications_author_set  -> authors 
        structure_id   : structures_element_set   -> structures 
        element_id     : reference_energies       -> elements 
        reference_id   : entries                  -> publications 
        structure_id   : structures_meta_data     -> structures 
        metadata_id    : structures_meta_data     -> meta_data 
        reference_id   : publications_author_set  -> publications 
        entry_id       : structures               -> entries 
        element_id     : calculations_element_set -> elements 
        spacegroup_id  : structures               -> spacegroups 
        journal_id     : publications             -> journals 
        composition_id : calculations             -> compositions 
        composition_id : prototypes               -> compositions 
        fit_id         : hubbard_corrections      -> fits 
        element_id     : hubbard_corrections      -> elements 
        entry_id       : entries_element_set      -> entries 
        calculation_id : calculations_element_set -> calculations 
        element_id     : entries_element_set      -> elements 
        fit_id         : fits_dft                 -> fits 
        hubbard_id     : hubbard_corrections      -> hubbards 
        fit_id         : reference_energies       -> fits 
        output_id      : calculations             -> structures 
        structure_id   : prototypes               -> structures 
        calculation_id : calculations_meta_data   -> calculations 
        metadata_id    : entries_meta_data        -> meta_data 
        entry_id       : calculations             -> entries 
        structure_id   : atoms                    -> structures 
        element_id     : structures_element_set   -> elements 
        structure_id   : sites                    -> structures 



    attributes
    //------

        magmom_pa       : structures          -> Double 
        name : fits                           -> String 
        f_elec          : elements            -> Integer 
        natoms          : calculations        -> Integer 
        z3              : structures          -> Double 
        group           : elements            -> Integer 
        d_elec          : elements            -> Integer 
        page_last       : publications        -> Integer 
        stability       : entries             -> Double 
        natoms          : structures          -> Integer 
        path : entries                        -> String 
        generic : compositions                -> String 
        year            : publications        -> Integer 
        settings        : calculations        -> Text 
        period          : elements            -> Integer 
        nsteps          : calculations        -> Integer 
        b               : structures          -> Double 
        value           : hubbard_corrections -> Double 
        z2              : structures          -> Double 
        comp : structures                     -> String 
        user : calculations                   -> String 
        nsites          : structures          -> Integer 
        energy_pa       : structures          -> Double 
        attempt         : calculations        -> Integer 
        number          : spacegroups         -> Integer 
        convention : hubbards                 -> String 
        ntypes          : compositions        -> Integer 
        path : calculations                   -> String 
        schoenflies : spacegroups             -> String 
        z               : sites               -> Double 
        x               : atoms               -> Double 
        duplicate_of_id : entries             -> Integer 
        x2              : structures          -> Double 
        meidema         : compositions        -> Double 
        label : entries                       -> String 
        y3              : structures          -> Double 
        pearson : spacegroups                 -> String 
        xs : structures                       -> String 
        magmom          : atoms               -> Double 
        y1              : structures          -> Double 
        x               : sites               -> Double 
        energy          : calculations        -> Double 
        band_gap        : calculations        -> Double 
        label : structures                    -> String 
        converged       : calculations        -> Boolean 
        type : meta_data                      -> String 
        measured        : structures          -> Boolean 
        z               : elements            -> Integer 
        volume          : publications        -> Integer 
        lattice_system : spacegroups          -> String 
        ntypes          : structures          -> Integer 
        formula : compositions                -> String 
        y               : atoms               -> Double 
        magmom          : structures          -> Double 
        mass            : elements            -> Double 
        first : authors                       -> String 
        specific_heat   : elements            -> Double 
        a               : structures          -> Double 
        xc : calculations                     -> String 
        s_elec          : elements            -> Integer 
        hm : spacegroups                      -> String 
        delta_e         : structures          -> Double 
        job_name : calculations               -> String 
        volume          : structures          -> Double 
        dftcode : calculations                -> String 
        y2              : structures          -> Double 
        runtime         : calculations        -> Double 
        x3              : structures          -> Double 
        label : calculations                  -> String 
        system_type : structures              -> String 
        symbol : elements                     -> String 
        configuration : calculations          -> String 
        title           : publications        -> Text 
        z1              : structures          -> Double 
        pw              : calculations        -> Double 
        charge          : atoms               -> Double 
        psp : calculations                    -> String 
        hall : spacegroups                    -> String 
        ys : structures                       -> String 
        u               : hubbards            -> Double 
        ox              : hubbards            -> Double 
        magmom          : calculations        -> Double 
        bigind          : atoms               -> Bigint 
        z               : atoms               -> Double 
        natoms          : entries             -> Integer 
        meta_stability  : structures          -> Double 
        value           : meta_data           -> Text 
        last : authors                        -> String 
        page_first      : publications        -> Integer 
        c               : structures          -> Double 
        l               : hubbards            -> Integer 
        centrosymmetric : spacegroups         -> Boolean 
        x1              : structures          -> Double 
        name            : journals            -> Text 
        energy          : structures          -> Double 
        fx              : atoms               -> Double 
        code : journals                       -> String 
        delta_e         : entries             -> Double 
        zs : structures                       -> String 
        value           : reference_energies  -> Double 
        y               : sites               -> Double 
        volume_pa       : structures          -> Double 
        p_elec          : elements            -> Integer 
        name : elements                       -> String 
        fz              : atoms               -> Double 
        fy              : atoms               -> Double 

 
}


schema src2_no_cons = literal : ty {     imports
    //------

        src_no_cons

    entities
    //------

        bulk
        struct_composition

    foreign_keys
    //------

        struct  : struct_composition -> structures 
        element : struct_composition -> elements 
        struct  : bulk               -> structures 



    attributes
    //------

        num : struct_composition -> Integer 
        raw : structures         -> Text 
        composition : structures -> String 
        ind : atoms              -> Integer 

 
}


schema tar_no_cons = literal : ty { 

    entities
    //------

        job
        element
        species
        struct
        cell
        atom
        calc
        struct_composition
        bulk
        molecule
        surface

    foreign_keys
    //------

        element : atom               -> element 
        cell    : struct             -> cell 
        struct  : struct_composition -> struct 
        struct  : molecule           -> struct 
        struct  : job                -> struct 
        struct  : atom               -> struct 
        calc    : job                -> calc 
        species : struct             -> species 
        struct  : surface            -> struct 
        struct  : bulk               -> struct 
        element : struct_composition -> element 



    attributes
    //------

        xc : calc                          -> String 
        stordir : job                      -> String 
        c1            : cell               -> Double 
        raw           : struct             -> Text 
        system_type : struct               -> String 
        b3            : cell               -> Double 
        a2            : cell               -> Double 
        name : element                     -> String 
        symmetry : species                 -> String 
        b             : cell               -> Double 
        psp : calc                         -> String 
        x             : atom               -> Double 
        c3            : cell               -> Double 
        phase : species                    -> String 
        y             : atom               -> Double 
        energy        : job                -> Double 
        pointgroup : molecule              -> String 
        a             : cell               -> Double 
        atomic_number : element            -> Integer 
        a3            : cell               -> Double 
        z             : atom               -> Double 
        number        : atom               -> Integer 
        pw            : calc               -> Double 
        num           : struct_composition -> Integer 
        composition : struct               -> String 
        vacuum        : surface            -> Double 
        formula : species                  -> String 
        ind           : atom               -> Integer 
        b2            : cell               -> Double 
        dftcode : calc                     -> String 
        symbol : element                   -> String 
        n_atoms       : struct             -> Integer 
        c             : cell               -> Double 
        a1            : cell               -> Double 
        job_name : job                     -> String 
        facet : surface                    -> String 
        c2            : cell               -> Double 
        volume        : cell               -> Double 
        user : job                         -> String 
        b1            : cell               -> Double 

 
}


schema tar2_no_cons = literal : ty {     imports
    //------

        tar_no_cons









 
}


//---------------------------------
//Section 1: Create source instance
//---------------------------------


schema s_src_core = literal : ty { 

    entities
    //------

        journals
        authors
        elements
        hubbards
        meta_data
        spacegroups
        compositions
        compositions_element_set
        publications
        publications_author_set
        entries
        entries_element_set
        entries_meta_data
        structures
        calculations
        calculations_meta_data
        calculations_element_set
        sites
        prototypes
        atoms
        structures_element_set
        structures_meta_data
        fits
        fits_dft
        reference_energies
        hubbard_corrections





    attributes
    //------

        uid : spacegroups                     -> String 
        f_elec          : elements            -> Integer 
        natoms          : calculations        -> Integer 
        z3              : structures          -> Double 
        page_last       : publications        -> Integer 
        uid : entries_meta_data               -> String 
        stability       : entries             -> Double 
        path : entries                        -> String 
        generic : compositions                -> String 
        period          : elements            -> Integer 
        nsteps          : calculations        -> Integer 
        b               : structures          -> Double 
        value           : hubbard_corrections -> Double 
        energy_pa       : structures          -> Double 
        number          : spacegroups         -> Integer 
        convention : hubbards                 -> String 
        ntypes          : compositions        -> Integer 
        schoenflies : spacegroups             -> String 
        z               : sites               -> Double 
        meidema         : compositions        -> Double 
        label : entries                       -> String 
        uid : reference_energies              -> String 
        xs : structures                       -> String 
        uid : fits                            -> String 
        y1              : structures          -> Double 
        x               : sites               -> Double 
        converged       : calculations        -> Boolean 
        uid : calculations_meta_data          -> String 
        measured        : structures          -> Boolean 
        z               : elements            -> Integer 
        y               : atoms               -> Double 
        mass            : elements            -> Double 
        first : authors                       -> String 
        specific_heat   : elements            -> Double 
        a               : structures          -> Double 
        xc : calculations                     -> String 
        s_elec          : elements            -> Integer 
        uid : fits_dft                        -> String 
        y2              : structures          -> Double 
        uid : calculations_element_set        -> String 
        system_type : structures              -> String 
        symbol : elements                     -> String 
        configuration : calculations          -> String 
        pw              : calculations        -> Double 
        charge          : atoms               -> Double 
        hall : spacegroups                    -> String 
        ys : structures                       -> String 
        uid : atoms                           -> String 
        ox              : hubbards            -> Double 
        z               : atoms               -> Double 
        uid : structures_element_set          -> String 
        meta_stability  : structures          -> Double 
        value           : meta_data           -> Text 
        last : authors                        -> String 
        page_first      : publications        -> Integer 
        delta_e         : entries             -> Double 
        zs : structures                       -> String 
        p_elec          : elements            -> Integer 
        uid : elements                        -> String 
        fy              : atoms               -> Double 
        magmom_pa       : structures          -> Double 
        uid : authors                         -> String 
        name : fits                           -> String 
        uid : sites                           -> String 
        uid : compositions_element_set        -> String 
        group           : elements            -> Integer 
        d_elec          : elements            -> Integer 
        uid : structures_meta_data            -> String 
        natoms          : structures          -> Integer 
        uid : prototypes                      -> String 
        settings        : calculations        -> Text 
        z2              : structures          -> Double 
        comp : structures                     -> String 
        name : elements                       -> String 
        user : calculations                   -> String 
        uid : journals                        -> String 
        nsites          : structures          -> Integer 
        uid : structures                      -> String 
        attempt         : calculations        -> Integer 
        uid : hubbard_corrections             -> String 
        uid : publications_author_set         -> String 
        uid : calculations                    -> String 
        uid : meta_data                       -> String 
        path : calculations                   -> String 
        x               : atoms               -> Double 
        duplicate_of_id : entries             -> Integer 
        x2              : structures          -> Double 
        y3              : structures          -> Double 
        pearson : spacegroups                 -> String 
        magmom          : atoms               -> Double 
        energy          : calculations        -> Double 
        band_gap        : calculations        -> Double 
        label : structures                    -> String 
        type : meta_data                      -> String 
        volume          : publications        -> Integer 
        lattice_system : spacegroups          -> String 
        ntypes          : structures          -> Integer 
        formula : compositions                -> String 
        magmom          : structures          -> Double 
        hm : spacegroups                      -> String 
        delta_e         : structures          -> Double 
        job_name : calculations               -> String 
        volume          : structures          -> Double 
        dftcode : calculations                -> String 
        x3              : structures          -> Double 
        uid : hubbards                        -> String 
        label : calculations                  -> String 
        title           : publications        -> Text 
        z1              : structures          -> Double 
        uid : publications                    -> String 
        psp : calculations                    -> String 
        uid : entries_element_set             -> String 
        u               : hubbards            -> Double 
        uid : compositions                    -> String 
        uid : entries                         -> String 
        magmom          : calculations        -> Double 
        bigind          : atoms               -> Bigint 
        natoms          : entries             -> Integer 
        c               : structures          -> Double 
        l               : hubbards            -> Integer 
        centrosymmetric : spacegroups         -> Boolean 
        x1              : structures          -> Double 
        name            : journals            -> Text 
        energy          : structures          -> Double 
        fx              : atoms               -> Double 
        code : journals                       -> String 
        value           : reference_energies  -> Double 
        y               : sites               -> Double 
        volume_pa       : structures          -> Double 
        year            : publications        -> Integer 
        fz              : atoms               -> Double 
        runtime         : calculations        -> Double 

 
}


schema s_src_raw = literal : ty { 

    entities
    //------

        journals
        authors
        elements
        hubbards
        meta_data
        spacegroups
        compositions
        compositions_element_set
        publications
        publications_author_set
        entries
        entries_element_set
        entries_meta_data
        structures
        calculations
        calculations_meta_data
        calculations_element_set
        sites
        prototypes
        atoms
        structures_element_set
        structures_meta_data
        fits
        fits_dft
        reference_energies
        hubbard_corrections





    attributes
    //------

        uid : spacegroups                         -> String 
        f_elec          : elements                -> Integer 
        natoms          : calculations            -> Integer 
        z3              : structures              -> Double 
        page_last       : publications            -> Integer 
        uid : entries_meta_data                   -> String 
        stability       : entries                 -> Double 
        journal_id : publications                 -> String 
        path : entries                            -> String 
        generic : compositions                    -> String 
        element_id : entries_element_set          -> String 
        reference_id : publications_author_set    -> String 
        period          : elements                -> Integer 
        nsteps          : calculations            -> Integer 
        b               : structures              -> Double 
        value           : hubbard_corrections     -> Double 
        energy_pa       : structures              -> Double 
        number          : spacegroups             -> Integer 
        convention : hubbards                     -> String 
        ntypes          : compositions            -> Integer 
        schoenflies : spacegroups                 -> String 
        z               : sites                   -> Double 
        meidema         : compositions            -> Double 
        label : entries                           -> String 
        uid : reference_energies                  -> String 
        xs : structures                           -> String 
        uid : fits                                -> String 
        y1              : structures              -> Double 
        author_id : publications_author_set       -> String 
        x               : sites                   -> Double 
        converged       : calculations            -> Boolean 
        uid : calculations_meta_data              -> String 
        measured        : structures              -> Boolean 
        z               : elements                -> Integer 
        element_id : reference_energies           -> String 
        metadata_id : calculations_meta_data      -> String 
        y               : atoms                   -> Double 
        reference_id : entries                    -> String 
        mass            : elements                -> Double 
        first : authors                           -> String 
        specific_heat   : elements                -> Double 
        a               : structures              -> Double 
        xc : calculations                         -> String 
        s_elec          : elements                -> Integer 
        element_id : hubbards                     -> String 
        uid : fits_dft                            -> String 
        element_id : atoms                        -> String 
        y2              : structures              -> Double 
        element_id : calculations_element_set     -> String 
        uid : calculations_element_set            -> String 
        structure_id : atoms                      -> String 
        system_type : structures                  -> String 
        symbol : elements                         -> String 
        configuration : calculations              -> String 
        pw              : calculations            -> Double 
        charge          : atoms                   -> Double 
        calculation_id : calculations_meta_data   -> String 
        hall : spacegroups                        -> String 
        metadata_id : structures_meta_data        -> String 
        ys : structures                           -> String 
        uid : atoms                               -> String 
        ox              : hubbards                -> Double 
        entry_id : entries_element_set            -> String 
        z               : atoms                   -> Double 
        uid : structures_element_set              -> String 
        meta_stability  : structures              -> Double 
        value           : meta_data               -> Text 
        last : authors                            -> String 
        page_first      : publications            -> Integer 
        element_id : hubbard_corrections          -> String 
        calculation_id : calculations_element_set -> String 
        delta_e         : entries                 -> Double 
        zs : structures                           -> String 
        composition_id : prototypes               -> String 
        p_elec          : elements                -> Integer 
        uid : elements                            -> String 
        fy              : atoms                   -> Double 
        magmom_pa       : structures              -> Double 
        element_id : structures_element_set       -> String 
        uid : authors                             -> String 
        name : fits                               -> String 
        uid : sites                               -> String 
        uid : compositions_element_set            -> String 
        group           : elements                -> Integer 
        d_elec          : elements                -> Integer 
        uid : structures_meta_data                -> String 
        natoms          : structures              -> Integer 
        uid : prototypes                          -> String 
        structure_id : prototypes                 -> String 
        spacegroup_id : structures                -> String 
        settings        : calculations            -> Text 
        z2              : structures              -> Double 
        comp : structures                         -> String 
        name : elements                           -> String 
        user : calculations                       -> String 
        uid : journals                            -> String 
        nsites          : structures              -> Integer 
        uid : structures                          -> String 
        attempt         : calculations            -> Integer 
        entry_id : structures                     -> String 
        uid : publications_author_set             -> String 
        uid : calculations                        -> String 
        uid : hubbard_corrections                 -> String 
        input_id : calculations                   -> String 
        uid : meta_data                           -> String 
        structure_id : structures_meta_data       -> String 
        path : calculations                       -> String 
        structure_id : sites                      -> String 
        x               : atoms                   -> Double 
        duplicate_of_id : entries                 -> Integer 
        x2              : structures              -> Double 
        y3              : structures              -> Double 
        pearson : spacegroups                     -> String 
        magmom          : atoms                   -> Double 
        output_id : calculations                  -> String 
        energy          : calculations            -> Double 
        band_gap        : calculations            -> Double 
        label : structures                        -> String 
        calculation_id : fits_dft                 -> String 
        type : meta_data                          -> String 
        volume          : publications            -> Integer 
        lattice_system : spacegroups              -> String 
        ntypes          : structures              -> Integer 
        formula : compositions                    -> String 
        metadata_id : entries_meta_data           -> String 
        magmom          : structures              -> Double 
        composition_id : calculations             -> String 
        entry_id : entries_meta_data              -> String 
        hm : spacegroups                          -> String 
        delta_e         : structures              -> Double 
        job_name : calculations                   -> String 
        volume          : structures              -> Double 
        dftcode : calculations                    -> String 
        Element_id : compositions_element_set     -> String 
        x3              : structures              -> Double 
        site_id : atoms                           -> String 
        fit_id : fits_dft                         -> String 
        uid : hubbards                            -> String 
        label : calculations                      -> String 
        composition_id : compositions_element_set -> String 
        title           : publications            -> Text 
        z1              : structures              -> Double 
        uid : publications                        -> String 
        psp : calculations                        -> String 
        fit_id : reference_energies               -> String 
        uid : entries_element_set                 -> String 
        entry_id : calculations                   -> String 
        u               : hubbards                -> Double 
        uid : compositions                        -> String 
        uid : entries                             -> String 
        magmom          : calculations            -> Double 
        bigind          : atoms                   -> Bigint 
        natoms          : entries                 -> Integer 
        c               : structures              -> Double 
        l               : hubbards                -> Integer 
        centrosymmetric : spacegroups             -> Boolean 
        x1              : structures              -> Double 
        name            : journals                -> Text 
        energy          : structures              -> Double 
        fx              : atoms                   -> Double 
        code : journals                           -> String 
        structure_id : structures_element_set     -> String 
        value           : reference_energies      -> Double 
        y               : sites                   -> Double 
        volume_pa       : structures              -> Double 
        hubbard_id : hubbard_corrections          -> String 
        year            : publications            -> Integer 
        ligand_id : hubbards                      -> String 
        fz              : atoms                   -> Double 
        runtime         : calculations            -> Double 
        fit_id : hubbard_corrections              -> String 

 
}


schema src_fk = literal : ty { 

    entities
    //------

        journals
        authors
        elements
        hubbards
        meta_data
        spacegroups
        compositions
        compositions_element_set
        publications
        publications_author_set
        entries
        entries_element_set
        entries_meta_data
        structures
        calculations
        calculations_meta_data
        calculations_element_set
        sites
        prototypes
        atoms
        structures_element_set
        structures_meta_data
        fits
        fits_dft
        reference_energies
        hubbard_corrections

    foreign_keys
    //------

        metadata_id    : calculations_meta_data   -> meta_data 
        site_id        : atoms                    -> sites 
        element_id     : atoms                    -> elements 
        entry_id       : entries_meta_data        -> entries 
        calculation_id : fits_dft                 -> calculations 
        input_id       : calculations             -> structures 
        element_id     : hubbards                 -> elements 
        composition_id : compositions_element_set -> compositions 
        Element_id     : compositions_element_set -> elements 
        ligand_id      : hubbards                 -> elements 
        author_id      : publications_author_set  -> authors 
        structure_id   : structures_element_set   -> structures 
        element_id     : reference_energies       -> elements 
        reference_id   : entries                  -> publications 
        structure_id   : structures_meta_data     -> structures 
        metadata_id    : structures_meta_data     -> meta_data 
        reference_id   : publications_author_set  -> publications 
        entry_id       : structures               -> entries 
        element_id     : calculations_element_set -> elements 
        spacegroup_id  : structures               -> spacegroups 
        journal_id     : publications             -> journals 
        composition_id : calculations             -> compositions 
        composition_id : prototypes               -> compositions 
        fit_id         : hubbard_corrections      -> fits 
        element_id     : hubbard_corrections      -> elements 
        entry_id       : entries_element_set      -> entries 
        calculation_id : calculations_element_set -> calculations 
        element_id     : entries_element_set      -> elements 
        fit_id         : fits_dft                 -> fits 
        hubbard_id     : hubbard_corrections      -> hubbards 
        fit_id         : reference_energies       -> fits 
        output_id      : calculations             -> structures 
        structure_id   : prototypes               -> structures 
        calculation_id : calculations_meta_data   -> calculations 
        metadata_id    : entries_meta_data        -> meta_data 
        entry_id       : calculations             -> entries 
        structure_id   : atoms                    -> structures 
        element_id     : structures_element_set   -> elements 
        structure_id   : sites                    -> structures 



    attributes
    //------

        uid : spacegroups                     -> String 
        f_elec          : elements            -> Integer 
        natoms          : calculations        -> Integer 
        z3              : structures          -> Double 
        page_last       : publications        -> Integer 
        uid : entries_meta_data               -> String 
        stability       : entries             -> Double 
        path : entries                        -> String 
        generic : compositions                -> String 
        period          : elements            -> Integer 
        nsteps          : calculations        -> Integer 
        b               : structures          -> Double 
        value           : hubbard_corrections -> Double 
        energy_pa       : structures          -> Double 
        number          : spacegroups         -> Integer 
        convention : hubbards                 -> String 
        ntypes          : compositions        -> Integer 
        schoenflies : spacegroups             -> String 
        z               : sites               -> Double 
        meidema         : compositions        -> Double 
        label : entries                       -> String 
        uid : reference_energies              -> String 
        xs : structures                       -> String 
        uid : fits                            -> String 
        y1              : structures          -> Double 
        x               : sites               -> Double 
        converged       : calculations        -> Boolean 
        uid : calculations_meta_data          -> String 
        measured        : structures          -> Boolean 
        z               : elements            -> Integer 
        y               : atoms               -> Double 
        mass            : elements            -> Double 
        first : authors                       -> String 
        specific_heat   : elements            -> Double 
        a               : structures          -> Double 
        xc : calculations                     -> String 
        s_elec          : elements            -> Integer 
        uid : fits_dft                        -> String 
        y2              : structures          -> Double 
        uid : calculations_element_set        -> String 
        system_type : structures              -> String 
        symbol : elements                     -> String 
        configuration : calculations          -> String 
        pw              : calculations        -> Double 
        charge          : atoms               -> Double 
        hall : spacegroups                    -> String 
        ys : structures                       -> String 
        uid : atoms                           -> String 
        ox              : hubbards            -> Double 
        z               : atoms               -> Double 
        uid : structures_element_set          -> String 
        meta_stability  : structures          -> Double 
        value           : meta_data           -> Text 
        last : authors                        -> String 
        page_first      : publications        -> Integer 
        delta_e         : entries             -> Double 
        zs : structures                       -> String 
        p_elec          : elements            -> Integer 
        uid : elements                        -> String 
        fy              : atoms               -> Double 
        magmom_pa       : structures          -> Double 
        uid : authors                         -> String 
        name : fits                           -> String 
        uid : sites                           -> String 
        uid : compositions_element_set        -> String 
        group           : elements            -> Integer 
        d_elec          : elements            -> Integer 
        uid : structures_meta_data            -> String 
        natoms          : structures          -> Integer 
        uid : prototypes                      -> String 
        settings        : calculations        -> Text 
        z2              : structures          -> Double 
        comp : structures                     -> String 
        name : elements                       -> String 
        user : calculations                   -> String 
        uid : journals                        -> String 
        nsites          : structures          -> Integer 
        uid : structures                      -> String 
        attempt         : calculations        -> Integer 
        uid : hubbard_corrections             -> String 
        uid : publications_author_set         -> String 
        uid : calculations                    -> String 
        uid : meta_data                       -> String 
        path : calculations                   -> String 
        x               : atoms               -> Double 
        duplicate_of_id : entries             -> Integer 
        x2              : structures          -> Double 
        y3              : structures          -> Double 
        pearson : spacegroups                 -> String 
        magmom          : atoms               -> Double 
        energy          : calculations        -> Double 
        band_gap        : calculations        -> Double 
        label : structures                    -> String 
        type : meta_data                      -> String 
        volume          : publications        -> Integer 
        lattice_system : spacegroups          -> String 
        ntypes          : structures          -> Integer 
        formula : compositions                -> String 
        magmom          : structures          -> Double 
        hm : spacegroups                      -> String 
        delta_e         : structures          -> Double 
        job_name : calculations               -> String 
        volume          : structures          -> Double 
        dftcode : calculations                -> String 
        x3              : structures          -> Double 
        uid : hubbards                        -> String 
        label : calculations                  -> String 
        title           : publications        -> Text 
        z1              : structures          -> Double 
        uid : publications                    -> String 
        psp : calculations                    -> String 
        uid : entries_element_set             -> String 
        u               : hubbards            -> Double 
        uid : compositions                    -> String 
        uid : entries                         -> String 
        magmom          : calculations        -> Double 
        bigind          : atoms               -> Bigint 
        natoms          : entries             -> Integer 
        c               : structures          -> Double 
        l               : hubbards            -> Integer 
        centrosymmetric : spacegroups         -> Boolean 
        x1              : structures          -> Double 
        name            : journals            -> Text 
        energy          : structures          -> Double 
        fx              : atoms               -> Double 
        code : journals                       -> String 
        value           : reference_energies  -> Double 
        y               : sites               -> Double 
        volume_pa       : structures          -> Double 
        year            : publications        -> Integer 
        fz              : atoms               -> Double 
        runtime         : calculations        -> Double 

 
}


//---------------------
//Section 1.1: Mappings
//---------------------


mapping id_core_src = identity s_src_core


mapping M_fks_src = literal : s_src_raw -> src_fk {
     
    imports
        id_core_src

    entity
        journals -> journals
    
    

    entity
        authors -> authors
    
    

    entity
        elements -> elements
    
    

    entity
        hubbards   -> hubbards
    
    attributes
        element_id -> element_id . uid
        ligand_id  -> ligand_id . uid

    entity
        meta_data -> meta_data
    
    

    entity
        spacegroups -> spacegroups
    
    

    entity
        compositions -> compositions
    
    

    entity
        compositions_element_set -> compositions_element_set
    
    attributes
        composition_id           -> composition_id . uid
        Element_id               -> Element_id . uid

    entity
        publications -> publications
    
    attributes
        journal_id   -> journal_id . uid

    entity
        publications_author_set -> publications_author_set
    
    attributes
        reference_id            -> reference_id . uid
        author_id               -> author_id . uid

    entity
        entries      -> entries
    
    attributes
        reference_id -> reference_id . uid

    entity
        entries_element_set -> entries_element_set
    
    attributes
        entry_id            -> entry_id . uid
        element_id          -> element_id . uid

    entity
        entries_meta_data -> entries_meta_data
    
    attributes
        entry_id          -> entry_id . uid
        metadata_id       -> metadata_id . uid

    entity
        structures    -> structures
    
    attributes
        entry_id      -> entry_id . uid
        spacegroup_id -> spacegroup_id . uid

    entity
        calculations   -> calculations
    
    attributes
        composition_id -> composition_id . uid
        entry_id       -> entry_id . uid
        input_id       -> input_id . uid
        output_id      -> output_id . uid

    entity
        calculations_meta_data -> calculations_meta_data
    
    attributes
        calculation_id         -> calculation_id . uid
        metadata_id            -> metadata_id . uid

    entity
        calculations_element_set -> calculations_element_set
    
    attributes
        calculation_id           -> calculation_id . uid
        element_id               -> element_id . uid

    entity
        sites        -> sites
    
    attributes
        structure_id -> structure_id . uid

    entity
        prototypes     -> prototypes
    
    attributes
        structure_id   -> structure_id . uid
        composition_id -> composition_id . uid

    entity
        atoms        -> atoms
    
    attributes
        structure_id -> structure_id . uid
        site_id      -> site_id . uid
        element_id   -> element_id . uid

    entity
        structures_element_set -> structures_element_set
    
    attributes
        structure_id           -> structure_id . uid
        element_id             -> element_id . uid

    entity
        structures_meta_data -> structures_meta_data
    
    attributes
        structure_id         -> structure_id . uid
        metadata_id          -> metadata_id . uid

    entity
        fits -> fits
    
    

    entity
        fits_dft       -> fits_dft
    
    attributes
        fit_id         -> fit_id . uid
        calculation_id -> calculation_id . uid

    entity
        reference_energies -> reference_energies
    
    attributes
        fit_id             -> fit_id . uid
        element_id         -> element_id . uid

    entity
        hubbard_corrections -> hubbard_corrections
    
    attributes
        fit_id              -> fit_id . uid
        element_id          -> element_id . uid
        hubbard_id          -> hubbard_id . uid }


//------------------------
//Section 1.2: Constraints
//------------------------


constraints con_fk_src = literal : s_src_raw {
     forall x0 : atoms -> exists unique y0:elements where x0.element_id=y0.uid

    forall x0 : atoms -> exists unique y0:sites where x0.site_id=y0.uid

    forall x0 : atoms -> exists unique y0:structures where x0.structure_id=y0.uid

    forall x0 : atoms x1 : atoms where x0.uid=x1.uid -> where x0=x1

    forall x0 : authors x1 : authors where x0.uid=x1.uid -> where x0=x1

    forall x0 : calculations -> exists unique y0:compositions where x0.composition_id=y0.uid

    forall x0 : calculations -> exists unique y0:entries where x0.entry_id=y0.uid

    forall x0 : calculations -> exists unique y0:structures where x0.input_id=y0.uid

    forall x0 : calculations -> exists unique y0:structures where x0.output_id=y0.uid

    forall x0 : calculations x1 : calculations where x0.uid=x1.uid -> where x0=x1

    forall x0 : calculations_element_set -> exists unique y0:calculations where x0.calculation_id=y0.uid

    forall x0 : calculations_element_set -> exists unique y0:elements where x0.element_id=y0.uid

    forall x0 : calculations_element_set x1 : calculations_element_set where x0.uid=x1.uid -> where x0=x1

    forall x0 : calculations_meta_data -> exists unique y0:calculations where x0.calculation_id=y0.uid

    forall x0 : calculations_meta_data -> exists unique y0:meta_data where x0.metadata_id=y0.uid

    forall x0 : calculations_meta_data x1 : calculations_meta_data where x0.uid=x1.uid -> where x0=x1

    forall x0 : compositions x1 : compositions where x0.uid=x1.uid -> where x0=x1

    forall x0 : compositions_element_set -> exists unique y0:compositions where x0.composition_id=y0.uid

    forall x0 : compositions_element_set -> exists unique y0:elements where x0.Element_id=y0.uid

    forall x0 : compositions_element_set x1 : compositions_element_set where x0.uid=x1.uid -> where x0=x1

    forall x0 : elements x1 : elements where x0.uid=x1.uid -> where x0=x1

    forall x0 : entries -> exists unique y0:publications where x0.reference_id=y0.uid

    forall x0 : entries x1 : entries where x0.uid=x1.uid -> where x0=x1

    forall x0 : entries_element_set -> exists unique y0:elements where x0.element_id=y0.uid

    forall x0 : entries_element_set -> exists unique y0:entries where x0.entry_id=y0.uid

    forall x0 : entries_element_set x1 : entries_element_set where x0.uid=x1.uid -> where x0=x1

    forall x0 : entries_meta_data -> exists unique y0:entries where x0.entry_id=y0.uid

    forall x0 : entries_meta_data -> exists unique y0:meta_data where x0.metadata_id=y0.uid

    forall x0 : entries_meta_data x1 : entries_meta_data where x0.uid=x1.uid -> where x0=x1

    forall x0 : fits x1 : fits where x0.uid=x1.uid -> where x0=x1

    forall x0 : fits_dft -> exists unique y0:calculations where x0.calculation_id=y0.uid

    forall x0 : fits_dft -> exists unique y0:fits where x0.fit_id=y0.uid

    forall x0 : fits_dft x1 : fits_dft where x0.uid=x1.uid -> where x0=x1

    forall x0 : hubbard_corrections -> exists unique y0:elements where x0.element_id=y0.uid

    forall x0 : hubbard_corrections -> exists unique y0:fits where x0.fit_id=y0.uid

    forall x0 : hubbard_corrections -> exists unique y0:hubbards where x0.hubbard_id=y0.uid

    forall x0 : hubbard_corrections x1 : hubbard_corrections where x0.uid=x1.uid -> where x0=x1

    forall x0 : hubbards -> exists unique y0:elements where x0.element_id=y0.uid

    forall x0 : hubbards -> exists unique y0:elements where x0.ligand_id=y0.uid

    forall x0 : hubbards x1 : hubbards where x0.uid=x1.uid -> where x0=x1

    forall x0 : journals x1 : journals where x0.uid=x1.uid -> where x0=x1

    forall x0 : meta_data x1 : meta_data where x0.uid=x1.uid -> where x0=x1

    forall x0 : prototypes -> exists unique y0:compositions where x0.composition_id=y0.uid

    forall x0 : prototypes -> exists unique y0:structures where x0.structure_id=y0.uid

    forall x0 : prototypes x1 : prototypes where x0.uid=x1.uid -> where x0=x1

    forall x0 : publications -> exists unique y0:journals where x0.journal_id=y0.uid

    forall x0 : publications x1 : publications where x0.uid=x1.uid -> where x0=x1

    forall x0 : publications_author_set -> exists unique y0:authors where x0.author_id=y0.uid

    forall x0 : publications_author_set -> exists unique y0:publications where x0.reference_id=y0.uid

    forall x0 : publications_author_set x1 : publications_author_set where x0.uid=x1.uid -> where x0=x1

    forall x0 : reference_energies -> exists unique y0:elements where x0.element_id=y0.uid

    forall x0 : reference_energies -> exists unique y0:fits where x0.fit_id=y0.uid

    forall x0 : reference_energies x1 : reference_energies where x0.uid=x1.uid -> where x0=x1

    forall x0 : sites -> exists unique y0:structures where x0.structure_id=y0.uid

    forall x0 : sites x1 : sites where x0.uid=x1.uid -> where x0=x1

    forall x0 : spacegroups x1 : spacegroups where x0.uid=x1.uid -> where x0=x1

    forall x0 : structures -> exists unique y0:entries where x0.entry_id=y0.uid

    forall x0 : structures -> exists unique y0:spacegroups where x0.spacegroup_id=y0.uid

    forall x0 : structures x1 : structures where x0.uid=x1.uid -> where x0=x1

    forall x0 : structures_element_set -> exists unique y0:elements where x0.element_id=y0.uid

    forall x0 : structures_element_set -> exists unique y0:structures where x0.structure_id=y0.uid

    forall x0 : structures_element_set x1 : structures_element_set where x0.uid=x1.uid -> where x0=x1

    forall x0 : structures_meta_data -> exists unique y0:meta_data where x0.metadata_id=y0.uid

    forall x0 : structures_meta_data -> exists unique y0:structures where x0.structure_id=y0.uid

    forall x0 : structures_meta_data x1 : structures_meta_data where x0.uid=x1.uid -> where x0=x1 }


//----------------------
//Section 1.3: Land data
//----------------------


instance i_src_raw = import_jdbc "com.mysql.jdbc.Driver" "jdbc:mysql://127.0.0.1:3306/oqmd?user=ksb&password=ksb" : s_src_raw {
    journals -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `code` AS `code`,
            `name` AS `name` 

        FROM journals 
        WHERE (0)"

    authors -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `last`  AS `last`,
            `first` AS `first` 

        FROM authors 
        WHERE (0)"

    elements -> 
        "SELECT z AS `id`, CONVERT(z,CHAR(50)) AS `uid`,
            `z`                 AS `z`,
            `name`              AS `name`,
            `symbol`            AS `symbol`,
            `group`             AS `group`,
            `period`            AS `period`,
            `mass`+0E0          AS `mass`,
            `specific_heat`+0E0 AS `specific_heat`,
            `s_elec`            AS `s_elec`,
            `p_elec`            AS `p_elec`,
            `d_elec`            AS `d_elec`,
            `f_elec`            AS `f_elec` 

        FROM elements 
        WHERE (`z` < (84))"

    hubbards -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `convention` AS `convention`,
            `ox`+0E0     AS `ox`,
            `u`+0E0      AS `u`,
            `l`          AS `l`,
            COALESCE(CONVERT(`element_id`,CHAR(250)),
                     CONCAT('hubbards.element_id$',CONVERT(id,CHAR(250))))
                         AS `element_id`,
            COALESCE(CONVERT(`ligand_id`,CHAR(250)),
                     CONCAT('hubbards.ligand_id$',CONVERT(id,CHAR(250))))
                         AS `ligand_id` 

        FROM hubbards 
        WHERE (0)"

    meta_data -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `type`  AS `type`,
            `value` AS `value` 

        FROM meta_data 
        WHERE (0)"

    spacegroups -> 
        "SELECT number AS `id`, CONVERT(number,CHAR(50)) AS `uid`,
            `number`          AS `number`,
            `centrosymmetric` AS `centrosymmetric`,
            `lattice_system`  AS `lattice_system`,
            `hm`              AS `hm`,
            `hall`            AS `hall`,
            `pearson`         AS `pearson`,
            `schoenflies`     AS `schoenflies` 

        FROM spacegroups 
        WHERE (0)"

    compositions -> 
        "SELECT formula AS `id`, CONVERT(formula,CHAR(50)) AS `uid`,
            `formula`     AS `formula`,
            `generic`     AS `generic`,
            `ntypes`      AS `ntypes`,
            `meidema`+0E0 AS `meidema` 

        FROM compositions 
        WHERE (0)"

    compositions_element_set -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            COALESCE(CONVERT(`composition_id`,CHAR(250)),
                     CONCAT('compositions_element_set.composition_id$',CONVERT(id,CHAR(250))))
                AS `composition_id`,
            COALESCE(CONVERT(`Element_id`,CHAR(250)),
                     CONCAT('compositions_element_set.Element_id$',CONVERT(id,CHAR(250))))
                AS `Element_id` 

        FROM compositions_element_set 
        WHERE (0)"

    publications -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `title`      AS `title`,
            `page_first` AS `page_first`,
            `page_last`  AS `page_last`,
            `year`       AS `year`,
            `volume`     AS `volume`,
            COALESCE(CONVERT(`journal_id`,CHAR(250)),
                     CONCAT('publications.journal_id$',CONVERT(id,CHAR(250))))
                         AS `journal_id` 

        FROM publications 
        WHERE (0)"

    publications_author_set -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            COALESCE(CONVERT(`reference_id`,CHAR(250)),
                     CONCAT('publications_author_set.reference_id$',CONVERT(id,CHAR(250))))
                AS `reference_id`,
            COALESCE(CONVERT(`author_id`,CHAR(250)),
                     CONCAT('publications_author_set.author_id$',CONVERT(id,CHAR(250))))
                AS `author_id` 

        FROM publications_author_set 
        WHERE (0)"

    entries -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `path`            AS `path`,
            `delta_e`+0E0     AS `delta_e`,
            `stability`+0E0   AS `stability`,
            `label`           AS `label`,
            `duplicate_of_id` AS `duplicate_of_id`,
            `natoms`          AS `natoms`,
            COALESCE(CONVERT(`reference_id`,CHAR(250)),
                     CONCAT('entries.reference_id$',CONVERT(id,CHAR(250))))
                              AS `reference_id` 

        FROM entries 
        WHERE (0)"

    entries_element_set -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            COALESCE(CONVERT(`entry_id`,CHAR(250)),
                     CONCAT('entries_element_set.entry_id$',CONVERT(id,CHAR(250))))
                AS `entry_id`,
            COALESCE(CONVERT(`element_id`,CHAR(250)),
                     CONCAT('entries_element_set.element_id$',CONVERT(id,CHAR(250))))
                AS `element_id` 

        FROM entries_element_set 
        WHERE (0)"

    entries_meta_data -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            COALESCE(CONVERT(`entry_id`,CHAR(250)),
                     CONCAT('entries_meta_data.entry_id$',CONVERT(id,CHAR(250))))
                AS `entry_id`,
            COALESCE(CONVERT(`metadata_id`,CHAR(250)),
                     CONCAT('entries_meta_data.metadata_id$',CONVERT(id,CHAR(250))))
                AS `metadata_id` 

        FROM entries_meta_data 
        WHERE (0)"

    structures -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `label`                                                                  AS `label`,
            `measured`                                                               AS `measured`,
            `natoms`                                                                 AS `natoms`,
            `nsites`                                                                 AS `nsites`,
            `ntypes`                                                                 AS `ntypes`,
            `volume`+0E0                                                             AS `volume`,
            `volume_pa`+0E0                                                          AS `volume_pa`,
            `energy`+0E0                                                             AS `energy`,
            `energy_pa`+0E0                                                          AS `energy_pa`,
            `magmom`+0E0                                                             AS `magmom`,
            `magmom_pa`+0E0                                                          AS `magmom_pa`,
            `delta_e`+0E0                                                            AS `delta_e`,
            `meta_stability`+0E0                                                     AS `meta_stability`,
            `x1`+0E0                                                                 AS `x1`,
            `x2`+0E0                                                                 AS `x2`,
            `x3`+0E0                                                                 AS `x3`,
            `y1`+0E0                                                                 AS `y1`,
            `y2`+0E0                                                                 AS `y2`,
            `y3`+0E0                                                                 AS `y3`,
            `z1`+0E0                                                                 AS `z1`,
            `z2`+0E0                                                                 AS `z2`,
            `z3`+0E0                                                                 AS `z3`,
            CONCAT((SELECT GROUP_CONCAT(`element_id`) FROM atoms WHERE structure_id = structures.id ) , (',')) AS `comp`,
            ('bulk') AS `system_type`,
            (SELECT GROUP_CONCAT(`x`) FROM atoms WHERE structure_id = structures.id ) AS `xs`,
            POW(((((0) + POW(`x1`,(2))) + POW(`x2`,(2))) + POW(`x3`,(2))),(0.5))+0E0 AS `a`,
            (SELECT GROUP_CONCAT(`y`) FROM atoms WHERE structure_id = structures.id ) AS `ys`,
            POW(((((0) + POW(`z1`,(2))) + POW(`z2`,(2))) + POW(`z3`,(2))),(0.5))+0E0 AS `c`,
            (SELECT GROUP_CONCAT(`z`) FROM atoms WHERE structure_id = structures.id ) AS `zs`,
            POW(((((0) + POW(`y1`,(2))) + POW(`y2`,(2))) + POW(`y3`,(2))),(0.5))+0E0 AS `b`,
            COALESCE(CONVERT(`entry_id`,CHAR(250)),
                     CONCAT('structures.entry_id$',CONVERT(id,CHAR(250))))
                                                                                     AS `entry_id`,
            COALESCE(CONVERT(`spacegroup_id`,CHAR(250)),
                     CONCAT('structures.spacegroup_id$',CONVERT(id,CHAR(250))))
                                                                                     AS `spacegroup_id` 

        FROM structures 
        WHERE `id` IN ((15133),(1638))"

    calculations -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `natoms`                                                                                                                                  AS `natoms`,
            `energy`+0E0                                                                                                                              AS `energy`,
            `magmom`+0E0                                                                                                                              AS `magmom`,
            `path`                                                                                                                                    AS `path`,
            `band_gap`+0E0                                                                                                                            AS `band_gap`,
            `nsteps`                                                                                                                                  AS `nsteps`,
            `attempt`                                                                                                                                 AS `attempt`,
            `converged`                                                                                                                               AS `converged`,
            `runtime`+0E0                                                                                                                             AS `runtime`,
            `label`                                                                                                                                   AS `label`,
            `settings`                                                                                                                                AS `settings`,
            `configuration`                                                                                                                           AS `configuration`,
            ('OQMD') AS `user`,
            CONCAT(('oqmd - ') , `label`)                                                                                                             AS `job_name`,
            ('PBE') AS `xc`,
            JSON_EXTRACT(REPLACE(REPLACE(REPLACE(`settings`,('True'),('true')),('False'),('false')),(\"'\"),('\"')),('$.potentials'))                 AS `psp`,
            CONVERT(JSON_EXTRACT(REPLACE(REPLACE(REPLACE(`settings`,('True'),('true')),('False'),('false')),(\"'\"),('\"')),('$.encut')),Decimal)+0E0 AS `pw`,
            ('vasp') AS `dftcode`,
            COALESCE(CONVERT(`composition_id`,CHAR(250)),
                     CONCAT('calculations.composition_id$',CONVERT(id,CHAR(250))))
                                                                                                                                                      AS `composition_id`,
            COALESCE(CONVERT(`entry_id`,CHAR(250)),
                     CONCAT('calculations.entry_id$',CONVERT(id,CHAR(250))))
                                                                                                                                                      AS `entry_id`,
            COALESCE(CONVERT(`input_id`,CHAR(250)),
                     CONCAT('calculations.input_id$',CONVERT(id,CHAR(250))))
                                                                                                                                                      AS `input_id`,
            COALESCE(CONVERT(`output_id`,CHAR(250)),
                     CONCAT('calculations.output_id$',CONVERT(id,CHAR(250))))
                                                                                                                                                      AS `output_id` 

        FROM calculations 
        WHERE `id` IN ((3187))"

    calculations_meta_data -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            COALESCE(CONVERT(`calculation_id`,CHAR(250)),
                     CONCAT('calculations_meta_data.calculation_id$',CONVERT(id,CHAR(250))))
                AS `calculation_id`,
            COALESCE(CONVERT(`metadata_id`,CHAR(250)),
                     CONCAT('calculations_meta_data.metadata_id$',CONVERT(id,CHAR(250))))
                AS `metadata_id` 

        FROM calculations_meta_data 
        WHERE (0)"

    calculations_element_set -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            COALESCE(CONVERT(`calculation_id`,CHAR(250)),
                     CONCAT('calculations_element_set.calculation_id$',CONVERT(id,CHAR(250))))
                AS `calculation_id`,
            COALESCE(CONVERT(`element_id`,CHAR(250)),
                     CONCAT('calculations_element_set.element_id$',CONVERT(id,CHAR(250))))
                AS `element_id` 

        FROM calculations_element_set 
        WHERE (0)"

    sites -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `x`+0E0 AS `x`,
            `y`+0E0 AS `y`,
            `z`+0E0 AS `z`,
            COALESCE(CONVERT(`structure_id`,CHAR(250)),
                     CONCAT('sites.structure_id$',CONVERT(id,CHAR(250))))
                    AS `structure_id` 

        FROM sites 
        WHERE (0)"

    prototypes -> 
        "SELECT name AS `id`, CONVERT(name,CHAR(50)) AS `uid`,
            COALESCE(CONVERT(`structure_id`,CHAR(250)),
                     CONCAT('prototypes.structure_id$',CONVERT(name,CHAR(250))))
                AS `structure_id`,
            COALESCE(CONVERT(`composition_id`,CHAR(250)),
                     CONCAT('prototypes.composition_id$',CONVERT(name,CHAR(250))))
                AS `composition_id` 

        FROM prototypes 
        WHERE (0)"

    atoms -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `x`+0E0      AS `x`,
            `y`+0E0      AS `y`,
            `z`+0E0      AS `z`,
            `fx`+0E0     AS `fx`,
            `fy`+0E0     AS `fy`,
            `fz`+0E0     AS `fz`,
            `magmom`+0E0 AS `magmom`,
            `charge`+0E0 AS `charge`,
            (`id` - (SELECT MIN(`id`) FROM atoms A WHERE A.structure_id=atoms.structure_id )) AS `bigind`,
            COALESCE(CONVERT(`structure_id`,CHAR(250)),
                     CONCAT('atoms.structure_id$',CONVERT(id,CHAR(250))))
                         AS `structure_id`,
            COALESCE(CONVERT(`site_id`,CHAR(250)),
                     CONCAT('atoms.site_id$',CONVERT(id,CHAR(250))))
                         AS `site_id`,
            COALESCE(CONVERT(`element_id`,CHAR(250)),
                     CONCAT('atoms.element_id$',CONVERT(id,CHAR(250))))
                         AS `element_id` 

        FROM atoms 
        WHERE `id` IN ((203277))"

    structures_element_set -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            COALESCE(CONVERT(`structure_id`,CHAR(250)),
                     CONCAT('structures_element_set.structure_id$',CONVERT(id,CHAR(250))))
                AS `structure_id`,
            COALESCE(CONVERT(`element_id`,CHAR(250)),
                     CONCAT('structures_element_set.element_id$',CONVERT(id,CHAR(250))))
                AS `element_id` 

        FROM structures_element_set 
        WHERE (0)"

    structures_meta_data -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            COALESCE(CONVERT(`structure_id`,CHAR(250)),
                     CONCAT('structures_meta_data.structure_id$',CONVERT(id,CHAR(250))))
                AS `structure_id`,
            COALESCE(CONVERT(`metadata_id`,CHAR(250)),
                     CONCAT('structures_meta_data.metadata_id$',CONVERT(id,CHAR(250))))
                AS `metadata_id` 

        FROM structures_meta_data 
        WHERE (0)"

    fits -> 
        "SELECT name AS `id`, CONVERT(name,CHAR(50)) AS `uid`,
            `name` AS `name` 

        FROM fits 
        WHERE (0)"

    fits_dft -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            COALESCE(CONVERT(`fit_id`,CHAR(250)),
                     CONCAT('fits_dft.fit_id$',CONVERT(id,CHAR(250))))
                AS `fit_id`,
            COALESCE(CONVERT(`calculation_id`,CHAR(250)),
                     CONCAT('fits_dft.calculation_id$',CONVERT(id,CHAR(250))))
                AS `calculation_id` 

        FROM fits_dft 
        WHERE (0)"

    reference_energies -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `value`+0E0 AS `value`,
            COALESCE(CONVERT(`fit_id`,CHAR(250)),
                     CONCAT('reference_energies.fit_id$',CONVERT(id,CHAR(250))))
                        AS `fit_id`,
            COALESCE(CONVERT(`element_id`,CHAR(250)),
                     CONCAT('reference_energies.element_id$',CONVERT(id,CHAR(250))))
                        AS `element_id` 

        FROM reference_energies 
        WHERE (0)"

    hubbard_corrections -> 
        "SELECT id AS `id`, CONVERT(id,CHAR(50)) AS `uid`,
            `value`+0E0 AS `value`,
            COALESCE(CONVERT(`fit_id`,CHAR(250)),
                     CONCAT('hubbard_corrections.fit_id$',CONVERT(id,CHAR(250))))
                        AS `fit_id`,
            COALESCE(CONVERT(`element_id`,CHAR(250)),
                     CONCAT('hubbard_corrections.element_id$',CONVERT(id,CHAR(250))))
                        AS `element_id`,
            COALESCE(CONVERT(`hubbard_id`,CHAR(250)),
                     CONCAT('hubbard_corrections.hubbard_id$',CONVERT(id,CHAR(250))))
                        AS `hubbard_id` 

        FROM hubbard_corrections 
        WHERE (0)" }


//----------------------------------------------------------------
//Section 1.4: Move "unconstrained" instance data into real schema
//----------------------------------------------------------------


instance i_chased_src = chase con_fk_src i_src_raw


instance i_fk_src = sigma M_fks_src i_chased_src


instance i_src = cascade_delete i_fk_src : src


//---------------------------------
//Section 2: Create target instance
//---------------------------------


instance itar = empty : tar


//---------------------------
//Section 3: Data integration
//---------------------------


//------------------------------------------------------------
//Section 3.1: Queries which add extra information when eval'd
//------------------------------------------------------------


query Q1 = literal : src -> src2 {
    entity atoms         -> {
        from
            atoms : atoms  

        attributes 
            bigind -> atoms.bigind
            charge -> atoms.charge
            fx     -> atoms.fx
            fy     -> atoms.fy
            fz     -> atoms.fz
            ind    -> bigint_to_int(atoms.bigind)
            magmom -> atoms.magmom
            x      -> atoms.x
            y      -> atoms.y
            z      -> atoms.z 

        foreign_keys 
            structure_id -> {structures -> atoms.structure_id}
            site_id -> {sites -> atoms.site_id}
            element_id -> {elements -> atoms.element_id}}

    entity authors -> {
        from
            authors : authors  

        attributes 
            first -> authors.first
            last  -> authors.last }

    entity bulk -> {
        from
            s0 : structures   

        foreign_keys 
            struct -> {structures -> s0}}

    entity calculations -> {
        from
            calculations : calculations  

        attributes 
            attempt       -> calculations.attempt
            band_gap      -> calculations.band_gap
            configuration -> calculations.configuration
            converged     -> calculations.converged
            dftcode       -> calculations.dftcode
            energy        -> calculations.energy
            job_name      -> calculations.job_name
            label         -> calculations.label
            magmom        -> calculations.magmom
            natoms        -> calculations.natoms
            nsteps        -> calculations.nsteps
            path          -> calculations.path
            psp           -> calculations.psp
            pw            -> calculations.pw
            runtime       -> calculations.runtime
            settings      -> calculations.settings
            user          -> calculations.user
            xc            -> calculations.xc 

        foreign_keys 
            composition_id -> {compositions -> calculations.composition_id}
            entry_id -> {entries -> calculations.entry_id}
            input_id -> {structures -> calculations.input_id}
            output_id -> {structures -> calculations.output_id}}

    entity calculations_element_set -> {
        from
            calculations_element_set : calculations_element_set   

        foreign_keys 
            calculation_id -> {calculations -> calculations_element_set.calculation_id}
            element_id -> {elements -> calculations_element_set.element_id}}

    entity calculations_meta_data -> {
        from
            calculations_meta_data : calculations_meta_data   

        foreign_keys 
            calculation_id -> {calculations -> calculations_meta_data.calculation_id}
            metadata_id -> {meta_data -> calculations_meta_data.metadata_id}}

    entity compositions -> {
        from
            compositions : compositions  

        attributes 
            formula -> compositions.formula
            generic -> compositions.generic
            meidema -> compositions.meidema
            ntypes  -> compositions.ntypes }

    entity compositions_element_set -> {
        from
            compositions_element_set : compositions_element_set   

        foreign_keys 
            composition_id -> {compositions -> compositions_element_set.composition_id}
            Element_id -> {elements -> compositions_element_set.Element_id}}

    entity elements -> {
        from
            elements : elements  

        attributes 
            d_elec        -> elements.d_elec
            f_elec        -> elements.f_elec
            group         -> elements.group
            mass          -> elements.mass
            name          -> elements.name
            p_elec        -> elements.p_elec
            period        -> elements.period
            s_elec        -> elements.s_elec
            specific_heat -> elements.specific_heat
            symbol        -> elements.symbol
            z             -> elements.z }

    entity entries -> {
        from
            entries : entries  

        attributes 
            delta_e         -> entries.delta_e
            duplicate_of_id -> entries.duplicate_of_id
            label           -> entries.label
            natoms          -> entries.natoms
            path            -> entries.path
            stability       -> entries.stability 

        foreign_keys 
            reference_id -> {publications -> entries.reference_id}}

    entity entries_element_set -> {
        from
            entries_element_set : entries_element_set   

        foreign_keys 
            entry_id -> {entries -> entries_element_set.entry_id}
            element_id -> {elements -> entries_element_set.element_id}}

    entity entries_meta_data -> {
        from
            entries_meta_data : entries_meta_data   

        foreign_keys 
            entry_id -> {entries -> entries_meta_data.entry_id}
            metadata_id -> {meta_data -> entries_meta_data.metadata_id}}

    entity fits -> {
        from
            fits : fits  

        attributes 
            name -> fits.name }

    entity fits_dft -> {
        from
            fits_dft : fits_dft   

        foreign_keys 
            fit_id -> {fits -> fits_dft.fit_id}
            calculation_id -> {calculations -> fits_dft.calculation_id}}

    entity hubbard_corrections -> {
        from
            hubbard_corrections : hubbard_corrections  

        attributes 
            value -> hubbard_corrections.value 

        foreign_keys 
            fit_id -> {fits -> hubbard_corrections.fit_id}
            element_id -> {elements -> hubbard_corrections.element_id}
            hubbard_id -> {hubbards -> hubbard_corrections.hubbard_id}}

    entity hubbards -> {
        from
            hubbards : hubbards  

        attributes 
            convention -> hubbards.convention
            l          -> hubbards.l
            ox         -> hubbards.ox
            u          -> hubbards.u 

        foreign_keys 
            element_id -> {elements -> hubbards.element_id}
            ligand_id -> {elements -> hubbards.ligand_id}}

    entity journals -> {
        from
            journals : journals  

        attributes 
            code -> journals.code
            name -> journals.name }

    entity meta_data -> {
        from
            meta_data : meta_data  

        attributes 
            type  -> meta_data.type
            value -> meta_data.value }

    entity prototypes -> {
        from
            prototypes : prototypes   

        foreign_keys 
            structure_id -> {structures -> prototypes.structure_id}
            composition_id -> {compositions -> prototypes.composition_id}}

    entity publications -> {
        from
            publications : publications  

        attributes 
            page_first -> publications.page_first
            page_last  -> publications.page_last
            title      -> publications.title
            volume     -> publications.volume
            year       -> publications.year 

        foreign_keys 
            journal_id -> {journals -> publications.journal_id}}

    entity publications_author_set -> {
        from
            publications_author_set : publications_author_set   

        foreign_keys 
            reference_id -> {publications -> publications_author_set.reference_id}
            author_id -> {authors -> publications_author_set.author_id}}

    entity reference_energies -> {
        from
            reference_energies : reference_energies  

        attributes 
            value -> reference_energies.value 

        foreign_keys 
            fit_id -> {fits -> reference_energies.fit_id}
            element_id -> {elements -> reference_energies.element_id}}

    entity sites -> {
        from
            sites : sites  

        attributes 
            x -> sites.x
            y -> sites.y
            z -> sites.z 

        foreign_keys 
            structure_id -> {structures -> sites.structure_id}}

    entity spacegroups -> {
        from
            spacegroups : spacegroups  

        attributes 
            centrosymmetric -> spacegroups.centrosymmetric
            hall            -> spacegroups.hall
            hm              -> spacegroups.hm
            lattice_system  -> spacegroups.lattice_system
            number          -> spacegroups.number
            pearson         -> spacegroups.pearson
            schoenflies     -> spacegroups.schoenflies }

    entity struct_composition -> {
        from
            e0 : elements
            s0 : structures 

        where 
            gt(countsubstr(s0.comp,cat(e0.symbol,","@String)),"0"@Integer) = "true"@Boolean 

        attributes 
            num -> countsubstr(s0.comp,cat(e0.symbol,","@String)) 

        foreign_keys 
            struct -> {structures -> s0}
            element -> {elements -> e0}}

    entity structures -> {
        from
            structures : structures  

        attributes 
            a              -> structures.a
            b              -> structures.b
            c              -> structures.c
            comp           -> structures.comp
            composition    -> makeCompositionDict(structures.comp)
            delta_e        -> structures.delta_e
            energy         -> structures.energy
            energy_pa      -> structures.energy_pa
            label          -> structures.label
            magmom         -> structures.magmom
            magmom_pa      -> structures.magmom_pa
            measured       -> structures.measured
            meta_stability -> structures.meta_stability
            natoms         -> structures.natoms
            nsites         -> structures.nsites
            ntypes         -> structures.ntypes
            raw            -> makeStructJSON(structures.comp,structures.xs,structures.ys,structures.zs,structures.x1,structures.x2,structures.x3,structures.y1,structures.y2,structures.y3,structures.z1,structures.z2,structures.z3)
            system_type    -> structures.system_type
            volume         -> structures.volume
            volume_pa      -> structures.volume_pa
            x1             -> structures.x1
            x2             -> structures.x2
            x3             -> structures.x3
            xs             -> structures.xs
            y1             -> structures.y1
            y2             -> structures.y2
            y3             -> structures.y3
            ys             -> structures.ys
            z1             -> structures.z1
            z2             -> structures.z2
            z3             -> structures.z3
            zs             -> structures.zs 

        foreign_keys 
            entry_id -> {entries -> structures.entry_id}
            spacegroup_id -> {spacegroups -> structures.spacegroup_id}}

    entity structures_element_set -> {
        from
            structures_element_set : structures_element_set   

        foreign_keys 
            structure_id -> {structures -> structures_element_set.structure_id}
            element_id -> {elements -> structures_element_set.element_id}}

    entity structures_meta_data -> {
        from
            structures_meta_data : structures_meta_data   

        foreign_keys 
            structure_id -> {structures -> structures_meta_data.structure_id}
            metadata_id -> {meta_data -> structures_meta_data.metadata_id}} 
    options
        prover=completion }


query Q2 = literal : tar -> tar2 {
    entity atom          -> {
        from
            atom : atom  

        attributes 
            ind    -> atom.ind
            number -> atom.number
            x      -> atom.x
            y      -> atom.y
            z      -> atom.z 

        foreign_keys 
            struct -> {struct -> atom.struct}
            element -> {element -> atom.element}}

    entity bulk -> {
        from
            bulk : bulk   

        foreign_keys 
            struct -> {struct -> bulk.struct}}

    entity calc -> {
        from
            calc : calc  

        attributes 
            dftcode -> calc.dftcode
            psp     -> calc.psp
            pw      -> calc.pw
            xc      -> calc.xc }

    entity cell -> {
        from
            cell : cell  

        attributes 
            a      -> cell.a
            a1     -> cell.a1
            a2     -> cell.a2
            a3     -> cell.a3
            b      -> cell.b
            b1     -> cell.b1
            b2     -> cell.b2
            b3     -> cell.b3
            c      -> cell.c
            c1     -> cell.c1
            c2     -> cell.c2
            c3     -> cell.c3
            volume -> cell.volume }

    entity element -> {
        from
            element : element  

        attributes 
            atomic_number -> element.atomic_number
            name          -> element.name
            symbol        -> element.symbol }

    entity job -> {
        from
            job : job  

        attributes 
            energy   -> job.energy
            job_name -> job.job_name
            stordir  -> job.stordir
            user     -> job.user 

        foreign_keys 
            struct -> {struct -> job.struct}
            calc -> {calc -> job.calc}}

    entity molecule -> {
        from
            molecule : molecule  

        attributes 
            pointgroup -> molecule.pointgroup 

        foreign_keys 
            struct -> {struct -> molecule.struct}}

    entity species -> {
        from
            species : species  

        attributes 
            formula  -> species.formula
            phase    -> species.phase
            symmetry -> species.symmetry }

    entity struct -> {
        from
            struct : struct  

        attributes 
            composition -> struct.composition
            n_atoms     -> struct.n_atoms
            raw         -> struct.raw
            system_type -> struct.system_type 

        foreign_keys 
            cell -> {cell -> struct.cell}
            species -> {species -> struct.species}}

    entity struct_composition -> {
        from
            struct_composition : struct_composition  

        attributes 
            num -> struct_composition.num 

        foreign_keys 
            struct -> {struct -> struct_composition.struct}
            element -> {element -> struct_composition.element}}

    entity surface -> {
        from
            surface : surface  

        attributes 
            facet  -> surface.facet
            vacuum -> surface.vacuum 

        foreign_keys 
            struct -> {struct -> surface.struct}} 
    options
        prover=completion }


instance i_src2 = eval Q1 i_src


instance i_tar2 = eval Q2 itar


//-------------------------------
//Section 3.2: Merging of schemas
//-------------------------------


schema_colimit merged_ = quotient tar2 + src2 : ty { 

    entity_equations
        tar2.bulk               = src2.bulk
        tar2.struct_composition = src2.struct_composition
        tar2.element            = src2.elements
        tar2.job                = src2.calculations
        tar2.atom               = src2.atoms
        tar2.struct             = src2.structures

    path_equations
        element.z                     = element.atomic_number
        job.calculations_energy       = job.energy
        job.calculations_user         = job.user
        job.calculations_job_name     = job.job_name
        atom.atoms_x                  = atom.x
        atom.atoms_y                  = atom.y
        atom.atoms_z                  = atom.z
        atom.ind                      = atom.ind
        element.elements_symbol       = element.symbol
        element.elements_name         = element.name
        job.path                      = job.stordir
        job.output_id                 = job.struct
        struct.natoms                 = struct.n_atoms
        struct.structures_system_type = struct.system_type
        atom.structure_id             = atom.struct
        atom.element_id               = atom.element
        job.dftcode                   = job.calc . dftcode
        job.xc                        = job.calc . xc
        job.pw                        = job.calc . pw
        job.psp                       = job.calc . psp
        struct.x1                     = struct.cell . a1
        struct.x2                     = struct.cell . a2
        struct.x3                     = struct.cell . a3
        struct.y1                     = struct.cell . b1
        struct.y2                     = struct.cell . b2
        struct.y3                     = struct.cell . b3
        struct.z1                     = struct.cell . c1
        struct.z2                     = struct.cell . c2
        struct.z3                     = struct.cell . c3
        struct.volume                 = struct.cell . volume
        struct.a                      = struct.cell . a
        struct.b                      = struct.cell . b
        struct.c                      = struct.cell . c 
    options
        simplify_names                = false
        left_bias                     = true
 }


schema_colimit merged_no_cons_ = quotient tar2_no_cons + src2_no_cons : ty { 

    entity_equations
        tar2_no_cons.bulk               = src2_no_cons.bulk
        tar2_no_cons.struct_composition = src2_no_cons.struct_composition
        tar2_no_cons.element            = src2_no_cons.elements
        tar2_no_cons.job                = src2_no_cons.calculations
        tar2_no_cons.atom               = src2_no_cons.atoms
        tar2_no_cons.struct             = src2_no_cons.structures

    path_equations
        element.z                     = element.atomic_number
        job.calculations_energy       = job.energy
        job.calculations_user         = job.user
        job.calculations_job_name     = job.job_name
        atom.atoms_x                  = atom.x
        atom.atoms_y                  = atom.y
        atom.atoms_z                  = atom.z
        atom.ind                      = atom.ind
        element.elements_symbol       = element.symbol
        element.elements_name         = element.name
        job.path                      = job.stordir
        job.output_id                 = job.struct
        struct.natoms                 = struct.n_atoms
        struct.structures_system_type = struct.system_type
        atom.structure_id             = atom.struct
        atom.element_id               = atom.element
        job.dftcode                   = job.calc . dftcode
        job.xc                        = job.calc . xc
        job.pw                        = job.calc . pw
        job.psp                       = job.calc . psp
        struct.x1                     = struct.cell . a1
        struct.x2                     = struct.cell . a2
        struct.x3                     = struct.cell . a3
        struct.y1                     = struct.cell . b1
        struct.y2                     = struct.cell . b2
        struct.y3                     = struct.cell . b3
        struct.z1                     = struct.cell . c1
        struct.z2                     = struct.cell . c2
        struct.z3                     = struct.cell . c3
        struct.volume                 = struct.cell . volume
        struct.a                      = struct.cell . a
        struct.b                      = struct.cell . b
        struct.c                      = struct.cell . c 
    options
        simplify_names                = false
        left_bias                     = true
 }


schema_colimit merged_no_cons = modify merged_no_cons_ {
    

rename foreign_keys
        bulk.src2_no_cons_bulk_struct                              -> src2_bulk_struct
        struct_composition.src2_no_cons_struct_composition_struct  -> src2_struct_composition_struct
        struct_composition.src2_no_cons_struct_composition_element -> src2_struct_composition_element

rename attributes
        struct_composition.src2_no_cons_struct_composition_num -> src2_struct_composition_num }


schema s_merged = getSchema merged_


schema s_merged_no_cons = getSchema merged_no_cons


mapping P1 = include src2_no_cons src2


mapping P2 = include tar2_no_cons tar2


mapping M1 = getMapping merged_no_cons src2_no_cons


mapping M2 = getMapping merged_no_cons tar2_no_cons


//--------------------------------
//Section 3.3: Merge instance data
//--------------------------------


instance i_src_no_cons = delta P1 i_src2


instance i_tar_no_cons = delta P2 i_tar2


instance srctmp = sigma M1 i_src_no_cons


instance tartmp = sigma M2 i_tar_no_cons


instance i_merged_no_con = coproduct srctmp + tartmp : s_merged_no_cons


instance i_merged = cascade_delete i_merged_no_con : s_merged


//----------------------------
//Section 3.4: Record linkages
//----------------------------


instance i_final = quotient_query i_merged {

    entity job -> {from a:job b:job where a.stordir=b.stordir}

    entity element -> {from a:element b:element where a.atomic_number=b.atomic_number}

    entity species -> {from a:species b:species where a.formula=b.formula a.symmetry=b.symmetry}

    entity struct -> {from a:struct b:struct where a.raw=b.raw}

    entity cell -> {from a:cell b:cell where a.a1=b.a1 a.a2=b.a2 a.a3=b.a3 a.b1=b.b1 a.b2=b.b2 a.b3=b.b3 a.c1=b.c1 a.c2=b.c2 a.c3=b.c3}

    entity atom -> {from a:atom b:atom where a.ind=b.ind a.struct=b.struct}

    entity calc -> {from a:calc b:calc where a.dftcode=b.dftcode a.xc=b.xc a.pw=b.pw a.psp=b.psp}

    entity struct_composition -> {from a:struct_composition b:struct_composition where a.struct=b.struct a.element=b.element}

    entity bulk -> {from a:bulk b:bulk where a.struct=b.struct}

    entity molecule -> {from a:molecule b:molecule where a.struct=b.struct}

    entity surface -> {from a:surface b:surface where a.struct=b.struct} 
    options
        quotient_use_chase = false}


//-----------------------------
//Section 4: Export to database
//-----------------------------


command cmd_drop = exec_jdbc "com.mysql.jdbc.Driver" "jdbc:mysql://127.0.0.1:3306/?user=ksb&password=ksb" {"DROP DATABASE IF EXISTS `cql_merged`"}


command cmd_create = exec_jdbc "com.mysql.jdbc.Driver" "jdbc:mysql://127.0.0.1:3306/?user=ksb&password=ksb" {"CREATE SCHEMA `cql_merged`"}


command cmd_merged = export_jdbc_instance i_final "com.mysql.jdbc.Driver" "jdbc:mysql://127.0.0.1:3306/cql_merged?user=ksb&password=ksb" ""