# cql_data_integration
An interface for generating Categorical Query Language files to merge/migrate data between databases. This repository can only create input files for CQL, not execute them directly, though instructions for doing that can be found below.

The interface exposes only a tiny fraction of the expressivity of CQL. However, it has abstracted two very specific types of data pipelines (**merge** and **migrate**) such that certain types of very large, intricate, and repetitive CQL files can be concisely specified.

The underlying interface for CQL (`/cdi/core`) is very preliminary and for demonstration purposes only.

## Setup

This setup has only been tested on Mac OSX.

### Setup virtual environment

```bash
cd INSTALL_DIR/cql_data_integration
python3 -m venv .env
echo "export PYTHONPATH=$(pwd):PYTHONPATH" >> .env/bin/activate
source .env/bin/activate
pip install -r requirements.txt
```

Before running any Python scripts, first execute `source .env/bin/activate` in the main directory.

### Setup MySQL
MySQL can be installed with `brew install mysql@5.7`

Download [Java MySQL connector](https://dev.mysql.com/downloads/connector/j/) (Platform independent, TAR archive). Make sure to note the path to the .jar file, which will be used in the next step. Note that MySQL is not necessary to use CQL or this interface, but it is needed to connect to external data sources (such as OQMD) or to export results.

### Setup CQL
[CQL](https://www.categoricaldata.net/fql.html) can be downloaded if the version in the main directory is out of date.

This alias will be helpful for opening the CQL IDE such that MySQL database connections can be made and that CQL has access to user-defined scripts.
```bash
alias runcql='java -Xmx4096m -cp "/path/to/mysql-connector-java-X.X.XX.jar:INSTALL_DIR/cql_data_integration/cql.jar:INSTALL_DIR/cql_data_integration/scripts/bin" catdata.ide.IDE'
```

You will need Java and the JDK to run that command.


## Example

For maximum clarity, we walk through the some of the features of this interface using a  nonscientific example. CQL is being used here as a tool to relate information that is represented in two different structures. We'll focus first on that of **migration**: we have a concrete instance of data in a database **Src** and want to represent that information in a database **Tar**.

### Declare source and target schemas
Imagine a source of data that represents Novels, which have titles, years, and author names associated with them. To make this idea concrete, we need to import some constructors.

```python
from cdi import Schema, Entity, Attr, Varchar, Integer

Nov = Entity(
    name  = 'Nov',
    desc  = 'A book',
    id    = 'id',
    attrs = [ Attr('title', Varchar, id = True, desc = 'Book title '),
              Attr('aname', Varchar,            desc = 'Author name'),
              Attr('year',  Integer,            desc = 'Book publish date')])
```

We get a Python object that we'll see can be used in many interesting ways. There are some important things to note here: if we were constructing a CQL file to connect to an external database, then it is important that we correctly identify the PK by specifying `id`.<sup>[1](#myfootnote1)</sup>
  Another nuance is that each `Entity` has the option to have _identifying_ information (data for which, if two instantiations of the entity agree on, then they should be considered the same entity). By making _title_ the sole piece of identifying data for **Nov**, we are making a modeling assumption that no two distinct books share the same title. This is important to do if we care about the situation where two databases are referring to the same novel, despite representing it very differently; we need to know what counts as identifying information in order to make this connection.

Now, let's add to our model model two more entities: Chapters (of a novel, which have an index and some text associated with them) and Readers (who have names, a favorite novel, and a list of books they've checked out from a library). These entities are related to other entities, so we use the notion of a foreign key to relate them. Just like with attributes, a `FK` can be _identifying_ or not - it's important to realize why **Chap** needs its FK to **Nov** in order to be identified whereas this is not the case for a reader's favorite book.

```python
from cdi import FK

Chap = Entity(
    name  = 'Chap',
    desc  = "A chapter within a book",
    id    = 'id',
    attrs = [Attr('num',            id = True,   desc = 'Chapter #'), # default datatype: Integer
             Attr('text', Varchar,               desc = 'Full text of a chapter')],
    fks   = [FK(name = 'novel_id', tar = 'Nov', id = True, desc = 'What novel this chapter belongs to')])

Readr = Entity(
    name  = 'Readr',
    id    = 'id',
    attrs = [Attr('rname',    Varchar, id = True, desc = 'Reader name'),
             Attr('borrowed', Varchar,            desc = 'Comma separated list of books reader has checked out of library')],
    fks   = [FK(name = 'fav',tar = 'Nov', desc = "A reader's favorite novel")])
```

Our demonstration target schema will specify a mixture of information that can be directly found in the source, some derivable from the source, and some information not even in principle derivable from the source. It clearly represents similar information to **Src** (the meanings of **Novel**, **Chapter**, and **Reader** are clear, although there is not one-to-one overlap in their attributes). It also introduces **Library** and **Author** entities, as well as a **Borrow** entity (which represents **Reader**+**Novel**+**Library** triples, with useful information such as what date the novel was checked out by the reader, as well as less useful information like the sum of the lengths of the reader's name + the novel's title).

```python
Novel = Entity(
    name  = 'Novel',
    attrs = [Attr('title',Varchar,id = True,desc = 'Book title')],
    fks   = [FK('wrote','Author')])

Chapter = Entity(
    name  = 'Chapter',
    attrs = [Attr('num',       id=True, desc = 'Chapter #'),
             Attr('n_words',            desc = 'Full text of a chapter'),
             Attr('page_start',         desc = 'Staring page of chapter')],
    fks  = [FK('novel','Novel', id = True)])

Reader = Entity(
    name  = 'Reader',
    attrs = [Attr('readername',Varchar,desc = 'Reader name')],
    fks   = [FK('favorite','Novel')])

Author = Entity(
    name  = 'Author',
    desc  = 'Authors, considered as an entity of their own',
    attrs = [Attr('authorname', Varchar, id = True, desc = 'Name of author'),
             Attr('born',                           desc = 'Author birth year')])

Library = Entity(
    name  = 'Library',
    attrs = [Attr('libname', Varchar, id = True, desc = 'Name of library')],
    fks   = [FK('most_popular','Novel')])

Borrow = Entity(
    name  = 'Borrow',
    desc  = 'A triple, (Novel,Reader,Library), meaning that this novel was borrowed from this library by this reader',
    attrs = [Attr('date',     Date,  desc = 'Date novel was checked out by reader from the library'),
             Attr('total_len',       desc = "Sum of letters in reader's name + book title (example derived property)")],
    fks   = [FK('r', 'Reader',  id = True),
             FK('n', 'Novel',   id = True),
             FK('l', 'Library', id = True)])
```

Lastly, we assemble the entities into a `Schema` object.

```python
from cdi import Schema

src = Schema('src',[Chap,Nov,Readr])
tar = Schema('tar',[Chapter,Novel,Reader,Borrow,Author,Library])
```

Everything above can be found in `library_example/models.py`

### Declare source and target instances

The bulk of our work will be to define a procedure that translates instances of **Src** into instances of **Tar**. The overall procedure will be to combine instance data of the transformed **Src** with some pre-existing instance **Tar**. For this demonstration, **Tar** will be empty, and we can specify this easily:
```python
from cdi import Instance

i_target = Instance()
```

We want our **Src** instance to have real data to work with, though. One way to do this is to give a database connection:

```python    
from cdi import Conn

oqmd_db   = Conn(host = 'mysql.categoricaldata.net',
                 db   = 'qchem',
                 user = 'qchem_public',
                 pw   = 'quantumchemistry')
```

For small toy examples, we can enter the data manually. An `Instance` maps attributes/relations to a map of generators (distinct records of some entity) which gives a generator's values for that attribute/relation.

```python
from cdi import Gen, JLit

r1,r2               = [Gen('r%d'%i,Readr) for i in range(1,3)]
n1,n2,n3            = [Gen('n%d'%i,Nov) for i in range(1,4)]
n1c1,n1c2,n2c1,n3c1 = [Gen('n%dc%d'%(x,y),Chap) for x,y in [(1,1),(1,2),(2,1),(3,1)]]
one,two,y1,y2,y3    = [JLit(x,Integer) for x in [1,2,1924,1915,1926]]

# Wrap Python string as a typed Java string
s = lambda x: JLit(x,Varchar)

i_src = Instance({Readr['fav']      : {r1   : n1,  r2   : n2},
                  Chap['novel_id']  : {n1c1 : n1,  n1c2 : n1,  n2c1 : n2,  n3c1 : n3},
                  Chap['num']       : {n1c1 : one, n1c2 : two, n2c1 : one, n3c1 : one},
                  Nov['year']       : {n1   : y1,  n2   : y2,  n3   : y3},
                  Readr['rname']    : {r1   : s('KSB'),  r2 : s("BR")},
                  Nov['aname']      : {n1   : s('Mann'), n2 : s('Kakfa'),n3 : s('Kafka')},
                  Nov['title']      : {n1   : s('Magic'),n2 : s('Meta'), n3 : s('Castle')},
                  Readr['borrowed'] : {r1   : s('Magic, Meta'),r2 : s("Meta")},
                  Chap['text']      : {n1c1 : s("An unassuming young man was travelling..."),
                                       n1c2 : s("Hans Castorp retained only pale..."),
                                       n2c1 : s("One morning, as Gregor..."),
                                       n3c1 : s("It was late in the evening when K...")}})

```

For instance, the first row in the `Instance` declaration below says that the favorite novel of "reader 1" is "novel 1". "reader 1" is in itself meaningless, but it has meaning through the values it is given in other parts of the `Instance` declaration.

### Define Overlap

The first thing to do is to provide the source and target schemas.
```python
from cdi import Overlap

overlap = Overlap(
    s1 = src,
    s2 = tar,
    ...
)
```
The heart of an overlap specification is the path equalities. These are expressed as a list of `PathEQ` objects, where the first path is in **Src** and the second in **Tar**. A path equality conveys the fact that the meaning of taking a path in one schema has the same _meaning_ as taking that path in the other. The simplest case is below:

```python
from cdi import PathEQ, Path

overlap = Overlap(
    ...
    paths = [PathEQ(Path(Nov['title']),
                    Path(Novel['title'])),

             PathEQ(Path(Readr['fav']),
                    Path(Reader['favorite']))

            ...
            ]
)
```

The meaning of this is the following: the **Nov** object of **Src** has the same meaning as the **Novel** object of **Tar**, and furthermore to take the path _title_ from **Nov** to **String** within **Src** has the same meaning has taking the path _title_ from **Novel** to **String** in **Tar**. Likewise, to take the path _fav_ from **Readr** to **Nov** in **Src** has the same meaning as taking _favorite_ from **Reader** to **Novel** (this `PathEQ` in itself is sufficient to conclude the **Readr** ≋ **Reader** _and_ **Nov** ≋ **Novel**).  The next most complicated thing we can do is this:

```python
overlap = Overlap(
    ...
    paths = [
            ...

            PathEQ(Path(Nov['aname']),
                   Path(Novel['wrote'],Author['authorname'])),
            ...
            ]
)
```

The meaning of the phrase "the novel's author" is encoded as an attribute to the **Nov** object in **Src**, yet **Tar** represents authors as an entity of their own such that we need a path of length two to convey the same meaning. There are many kinds of helper functions and Python tricks one can use to make the overlap specification more concise (as is done in the _science example_).

#### "New" attributes, FKs, entities
As mentioned, there need not be a one-to-one match of information between the two schemas; **Src** has some extra and some missing information. For a migration from **Src** to **Tar**, we are concerned with the fragment of **Tar** that is not explicitly in **Src** (for that could be described by a `PathEQ`) yet is derivable from other parts of **Src**. Again we use `Gen` to create generators of an entity, which act as variables (e.g. "for all `x` of type **Chap**...").

```python
from cdi import NewAttr, JavaFunc

chap = Gen('Chap',Chap)

count_words = JavaFunc('count_words', [String], Integer, "return 1 + input[0].length() - input[0].replaceAll(' ', '').length()")

overlap = Overlap(
    ...
    new_attr1 = [NewAttr(Chap, 'n_words', Integer, count_words(chap['text'])),
                ...
                ],
   ...
)
```

Giving **Chap** a 'new attribute' *n_words* works because the corresponding entity **Tar.Chapter** has an attribute _n_words_. Something similar can be done with a list of `NewFK` instances passed to `new_fk1`.<sup>[2](#myfootnote2)</sup> We've patched up one hole, but there are still many remaining elements of **Tar** that **Src** does not have. We do not need to patch them all, though our data migration becomes much more rich if we put in the effort to do as much as possible. Sometimes it is possible to generate new _entities_ from old ones. Consider the **Author** entity, which has _name_ and _born_ as attributes. We certainly do not have information to populate _born_, but we have author names as an attribute of **Nov**.

```python
from cdi import NewEntity

overlap = Overlap(
    ...
    new_ent1  = [
                  NewEntity(name = 'Author', gens = [nov]),
                 ...
                ]
)
```

This says that we have possibly a different author for every instance of **Nov**, and, in conjunction with our earlier path equality (`Nov.aname` ≋ `Novel.wrote.authorname`), is sufficient to specify what we want.<sup>[3](#myfootnote3)</sup> A more complicated instance of entity creation is below:

```python
from cdi import CQLExpr, Lit, EQ

matches = JavaFunc('matches', [String,String],   Boolean, "return input[0].matches(input[1])")
plus    = JavaFunc('plus',    [Integer,Integer], Integer, "return input[0] + input[1]")
cat     = JavaFunc('cat',     [String,String],   String,  "return input[0] + input[1]")
Len     = JavaFunc('len',     [String],          Integer, "return input[0].length()")

wild = Lit(".*",String) # regex wildcard

def concat(*args : CQLExpr) -> CQLExpr:
    '''Concatenate multiple strings within CQL: folds n arguments into a series of binary applications of 'cat' '''
    return reduce(cat,args)


NewEntity(
    name  = 'Borrow',
    gens  = [nov,readr],
    where = [EQ(matches(readr['borrowed'],
                        concat(wild, nov['title'], wild)),
                Lit('true',Boolean))],
    attrs = {Attr('total_len',Integer): plus(Len(readr['rname']),
                                             Len(nov['title']))},
    fks   = {FK('r','Readr') : readr,
             FK('n','Nov')  : nov})]
)
```

We want one **Borrow** instance for every (**Readr**,**Nov**) pair in **Src**. But we don't want to create these pairs indiscriminately (the _meaning_ of **Borrow** in **Tar** is that some person borrowed the book). Luckily we do have sufficient information to determine this: the _borrow_ attribute has a string concatenated list of novels that have borrowed, so we can use a regex match in the _where_ clause as a first attempt to generate the correct pairs. We can populate one of the attributes that is a function attributes that we do have (we still do not know what **Library** they were borrowed at or what date, but we have done as much as possible).



### Putting it all together

With an `Overlap` specified and passing a list of all the `JavaFunc`s that were used, we can construct a `Migrate` object with a `file` method which formats the CQL input file to draw data from the correct inputs. A `merged` parameter can also be specified with a MySQL database connection in order to have the results exported.

```python
from cdi import Migrate

m  = Migrate(src = src, tar = tar, overlap = overlap, funcs = [count_words,Len,plus,matches,cat])
fi = m.file(src = isrc, tar = itar)
with open('cdi/library_example/lib.cql','w') as f:
    f.write(fi)
```

To generate the file from the command line, execute the following script:

```bash
python -m cdi.library_example.main
```

In the CQL GUI, we can open this file and run it. The result will look like this:

![Demo](http://web.stanford.edu/~ksb/images/Demo_Result.png)

There are many things we can check to see that the data was migrated properly (such as counting the number of letters in Reader's names + Novel titles and comparing to **Borrow**.*total_len*), and that attributes that could not have been populated were not (e.g. **Author**.*born*, **Chapter**.*page_start*).<sup>[4](#myfootnote4)</sup>


### To do
A tutorial example with merge, data-integrity constraints, generating SQL with Python, and connecting to arbitrary scripts for user-defined functions. For now the input files for the *science example* are the only help for doing these things.

## Further reading

You can read the associated paper which discusses the *science example* in more depth and application of this technology to addressing data-sharing challenges in computational science [here](https://doi.org/10.1016/j.commatsci.2019.04.002) or on [arXiv](https://arxiv.org/abs/1903.10579).

## Footnotes

<a name="myfootnote1">1</a>: This ID is only for internal bookkeeping and should not be part of the model (all IDs should be interchangeable with any other unique identifier).

<a name="myfootnote2">2</a>: Note that the names _new_attr1_, _new_fk1_, and _new_ent1_ come from providing something to **Src** found in **Tar**, whereas _new_attr2_ would provide something to **Tar** not found in **Src**. This is always meaningless for `Migrate`, but not for `Merge`; the same `Overlap` constructor is used for both `Merge` and `Migrate` because is a lot of overlapping information needed to do these operations.

<a name="myfootnote3">3</a>: Specifying identifying information for **Author** is what prevents us from having duplicates in the end.

<a name="myfootnote4">4</a>: However, certain things may be confusing at first, like the three mystery authors with no information and three instances of **Library** which could not possibly have had corresponding data in **Src**. The key to understanding this behavior is understanding how CQL handles the enforcement of foreign key constraints. A cascade of events was begun by creating three **Borrow** instances without providing information about which **Library** the books were borrowed at. We don't know anything about those libraries, but we do know they must exist, so three records in **Library** are automatically generated (we don't have any reason to conclude they are the same library - all we know is that we know nothing about their details). Likewise, each of those libraries has a most popular novel (although we know nothing about it), so three records of **Novel** are automatically generated, which in turn generate the three authors that have no information. It is possible to write CQL input files that handle these nuances differently, but the strategy above could be seen as a strategy for dealing with unknowns with the fewest assumptions.
