import os.path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


# gebe damit nur den Pfad von diesem File an, den absoluten Pfad -J
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# engine ist verantwortlich für Interaktion mit Datenbank(SQLite) -J
engine = create_engine(f"sqlite:///{BASE_DIR}/db", echo=True)

# sorgt dafür, dass immer die selbe session verwendet wird und nicht immer eine neue Verbindung aufgebaut werden muss -J
session = scoped_session(
    sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=engine,
    )
)

Base = declarative_base()
