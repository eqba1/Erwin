from sqlalchemy import create_engine, MetaData, Table, Integer, String, \
    Column, select

metadata = MetaData()

engine = create_engine(
    'sqlite:///messenger.db',
    connect_args={'check_same_thread': False}
)

conn = engine.connect()

user = Table('users', metadata,
    Column('id', Integer(), primary_key=True),
    Column('name', String(100), nullable=False),
    Column('password', String(100), nullable=False),
)

metadata.create_all(engine)

def find(query):
    s = select([user]).where(
        user.c.name == query
    )

    r = conn.execute(s).fetchall()
    return r 

def add(name, password):
    ins = user.insert().values(
        name = name,
        password = password
    )
    r = conn.execute(ins)
    return r 

