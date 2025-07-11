from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.models import Base

DATABASE_URL = "sqlite:///./data/dbdesc.db"

# Create engine with performance optimizations
engine = create_engine(
    DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 30,  # Increase timeout for better concurrency
    },
    pool_size=20,  # Connection pool size
    max_overflow=30,  # Maximum overflow connections
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Enable WAL mode and other SQLite optimizations
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA synchronous=NORMAL"))
        conn.execute(text("PRAGMA cache_size=10000"))
        conn.execute(text("PRAGMA temp_store=MEMORY"))
        conn.execute(text("PRAGMA mmap_size=268435456"))  # 256MB
        conn.execute(text("PRAGMA optimize"))
        conn.commit() 