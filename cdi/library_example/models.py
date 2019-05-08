# External
from typing import Callable as C
# Internal
from cdi import Schema, Entity, Attr, Varchar,FK, Instance, Gen, JLit, Integer, Date
################################################################################

Nov = Entity(
    name  = 'Nov',
    desc  = 'A book',
    id    = 'id',
    attrs = [Attr('aname',Varchar,          desc = 'Author name'),
             Attr('title',Varchar,id = True,desc = 'Book title '),
             Attr('year',                   desc = 'Book publish date')])

Chap = Entity(
    name  = 'Chap',
    desc  = "A chapter within a book",
    id    = 'id',
    attrs = [Attr('num',id = True,   desc = 'Chapter #'),
             Attr('text',Varchar,    desc = 'Full text of a chapter')],
    fks   = [FK('novel_id','Nov', id = True)])

Readr = Entity(
    name  = 'Readr',
    desc  = 'A reader',
    id    = 'id',
    attrs = [Attr('rname',Varchar,   desc = 'Reader name'),
             Attr('borrowed',Varchar,desc = 'Comma separated list of books reader has checked out of library')],
    fks   = [FK('fav','Nov')])


src = Schema('src',[Chap,Nov,Readr])

r1,r2               = [Gen('r%d'%i,Readr) for i in range(1,3)]
n1,n2,n3            = [Gen('n%d'%i,Nov) for i in range(1,4)]
n1c1,n1c2,n2c1,n3c1 = [Gen('n%dc%d'%(x,y),Chap) for x,y in [(1,1),(1,2),(2,1),(3,1)]]
one,two,y1,y2,y3    = [JLit(x,Integer) for x in [1,2,1924,1915,1926]]

# Wrap Python string as a typed Java string
s = lambda x: JLit(x,Varchar) # type: C[[str],JLit]

isrc = Instance({Readr['fav']      : {r1   : n1,  r2   : n2},
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
                                      n3c1 : s("It was late in the evening when K...")},
             })
################################################################################
# Alternative representation of similar domain
##############################################
Novel = Entity(
    name  = 'Novel',
    attrs = [Attr('title', Varchar, id = True, desc = 'Book title')],
    fks   = [FK('wrote','Author')])

Chapter = Entity(
    name  = 'Chapter',
    attrs = [Attr('num',       id=True, desc = 'Chapter #'),
             Attr('n_words',            desc = 'Full text of a chapter'),
             Attr('page_start',         desc = 'Staring page of chapter')],
    fks  = [FK('novel','Novel', id = True)])

Reader = Entity(
    name  = 'Reader',
    attrs = [Attr('readername', Varchar, id = True, desc = 'Reader name')],
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
    desc  = 'A pair, (Novel,Reader), meaning that this novel was borrowed by this reader',
    attrs = [Attr('date',       Date, desc = 'Date novel was checked out by reader from the library'),
             Attr('total_len',        desc = "Sum of letters in reader's name + book title (example derived property)")],
    fks   = [FK('r', 'Reader',  id = True),
             FK('n', 'Novel',   id = True),
             FK('l', 'Library', id = True)])


tar  = Schema('tar',[Chapter,Novel,Reader,Borrow,Author,Library])
itar = Instance()
