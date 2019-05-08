//-------------------
//Section 0.1: Set-up
//-------------------


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
        count_words : String -> Integer
             = "return 1 + input[0].length() - input[0].replaceAll(' ', '').length()"

        matches : String,String -> Boolean
             = "return input[0].matches(input[1])"

        len : String -> Integer
             = "return input[0].length()"

        cat : String,String -> String
             = "return input[0] + input[1]"

        plus : Integer,Integer -> Integer
             = "return input[0] + input[1]" }


//----------------------------
//Section 0.2: Declare schemas
//----------------------------


schema src = literal : ty { 

    entities
    //------

        Chap
        Nov
        Readr

    foreign_keys
    //------

        fav      : Readr -> Nov 
        novel_id : Chap  -> Nov 



    attributes
    //------

        aname : Nov      -> String 
        title : Nov      -> String 
        year : Nov       -> Integer 
        num  : Chap      -> Integer 
        rname : Readr    -> String 
        borrowed : Readr -> String 
        text : Chap      -> String 

 
}


schema tar = literal : ty { 

    entities
    //------

        Chapter
        Novel
        Reader
        Borrow
        Author
        Library

    foreign_keys
    //------

        novel        : Chapter -> Novel 
        favorite     : Reader  -> Novel 
        l            : Borrow  -> Library 
        n            : Borrow  -> Novel 
        wrote : Novel          -> Author 
        r            : Borrow  -> Reader 
        most_popular : Library -> Novel 



    attributes
    //------

        born : Author        -> Integer 
        page_start : Chapter -> Integer 
        n_words    : Chapter -> Integer 
        num        : Chapter -> Integer 
        authorname : Author  -> String 
        date       : Borrow  -> Date 
        total_len  : Borrow  -> Integer 
        libname : Library    -> String 
        readername : Reader  -> String 
        title : Novel        -> String 

 
}


schema tar_nc = literal : ty { 

    entities
    //------

        Chapter
        Novel
        Reader
        Borrow
        Author
        Library

    foreign_keys
    //------

        novel        : Chapter -> Novel 
        favorite     : Reader  -> Novel 
        l            : Borrow  -> Library 
        n            : Borrow  -> Novel 
        wrote : Novel          -> Author 
        r            : Borrow  -> Reader 
        most_popular : Library -> Novel 



    attributes
    //------

        born : Author        -> Integer 
        page_start : Chapter -> Integer 
        n_words    : Chapter -> Integer 
        num        : Chapter -> Integer 
        authorname : Author  -> String 
        date       : Borrow  -> Date 
        total_len  : Borrow  -> Integer 
        libname : Library    -> String 
        readername : Reader  -> String 
        title : Novel        -> String 

 
}


schema inter = literal : ty { 

    entities
    //------

        Nov
        Chap
        Readr
        Author
        Borrow

    foreign_keys
    //------

        fav      : Readr  -> Nov 
        n        : Borrow -> Nov 
        wrote : Nov       -> Author 
        novel_id : Chap   -> Nov 
        r        : Borrow -> Readr 



    attributes
    //------

        aname : Nov        -> String 
        title : Nov        -> String 
        total_len : Borrow -> Integer 
        num       : Chap   -> Integer 
        rname : Readr      -> String 
        n_words   : Chap   -> Integer 

 
}


//---------------------------------
//Section 1: Create source instance
//---------------------------------


instance isrc = literal : src {
    generators
        n1   : Nov
        n1c1 : Chap
        n1c2 : Chap
        n2   : Nov
        n2c1 : Chap
        n3   : Nov
        n3c1 : Chap
        r1   : Readr
        r2   : Readr

    multi_equations
        aname    -> {n1 "Mann"@String,n2 "Kakfa"@String,n3 "Kafka"@String}
        borrowed -> {r1 "Magic, Meta"@String,r2 "Meta"@String}
        fav      -> {r1 n1,r2 n2}
        novel_id -> {n1c1 n1,n1c2 n1,n2c1 n2,n3c1 n3}
        num      -> {n1c1 "1"@Integer,n1c2 "2"@Integer,n2c1 "1"@Integer,n3c1 "1"@Integer}
        rname    -> {r1 "KSB"@String,r2 "BR"@String}
        text     -> {n1c1 "An unassuming young man was travelling..."@String,n1c2 "Hans Castorp retained only pale..."@String,n2c1 "One morning, as Gregor..."@String,n3c1 "It was late in the evening when K..."@String}
        title    -> {n1 "Magic"@String,n2 "Meta"@String,n3 "Castle"@String}
        year     -> {n1 "1924"@Integer,n2 "1915"@Integer,n3 "1926"@Integer}}


//---------------------------------
//Section 2: Create target instance
//---------------------------------


instance itar = empty : tar


//-------------------------
//Section 3: Data migration
//-------------------------


//-----------------------------------------------------------
//Section 3.1: Query which adds extra information when eval'd
//-----------------------------------------------------------


query Q = literal : src -> inter {
    entity      Author  -> {
        from
            Nov : Nov   }

    entity Borrow -> {
        from
            Nov   : Nov
            Readr : Readr 

        where 
            matches(Readr.borrowed,cat(cat(".*"@String,Nov.title),".*"@String)) = "true"@Boolean 

        attributes 
            total_len -> plus(len(Readr.rname),len(Nov.title)) 

        foreign_keys 
            r -> {Readr -> Readr}
            n -> {Nov -> Nov}}

    entity Chap -> {
        from
            Chap : Chap  

        attributes 
            n_words -> count_words(Chap.text)
            num     -> Chap.num 

        foreign_keys 
            novel_id -> {Nov -> Chap.novel_id}}

    entity Nov -> {
        from
            Nov : Nov  

        attributes 
            aname -> Nov.aname
            title -> Nov.title 

        foreign_keys 
            wrote -> {Nov -> Nov}}

    entity Readr -> {
        from
            Readr : Readr  

        attributes 
            rname -> Readr.rname 

        foreign_keys 
            fav -> {Nov -> Readr.fav}} 
    options
        prover=completion }


//--------------------
//Section 3.2: Mapping
//--------------------


mapping M = literal : inter -> tar_nc {
     

    entity
        Nov   -> Novel
    foreign_keys
        wrote -> wrote
    attributes
        aname -> wrote . authorname
        title -> title

    entity
        Chap     -> Chapter
    foreign_keys
        novel_id -> novel
    attributes
        num      -> num
        n_words  -> n_words

    entity
        Readr -> Reader
    foreign_keys
        fav   -> favorite
    attributes
        rname -> readername

    entity
        Author -> Author
    
    

    entity
        Borrow    -> Borrow
    foreign_keys
        r         -> r
        n         -> n
    attributes
        total_len -> total_len }


//--------------------------------------------------
//Section 3.3: Move instance data from src to target
//--------------------------------------------------


instance i_altered = eval Q isrc


instance i_mapped = sigma M i_altered


instance i_constrained = cascade_delete i_mapped : tar


instance i_merged = coproduct i_constrained + itar : tar


//----------------------------
//Section 3.4: Record linkages
//----------------------------


instance i_final = quotient_query i_merged {

    entity Chapter -> {from a:Chapter b:Chapter where a.num=b.num a.novel=b.novel}

    entity Novel -> {from a:Novel b:Novel where a.title=b.title}

    entity Reader -> {from a:Reader b:Reader where a.readername=b.readername}

    entity Borrow -> {from a:Borrow b:Borrow where a.r=b.r a.n=b.n a.l=b.l}

    entity Author -> {from a:Author b:Author where a.authorname=b.authorname}

    entity Library -> {from a:Library b:Library where a.libname=b.libname} 
    options
        quotient_use_chase = false}