from sqlalchemy import Column, Integer, String, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Cluster(Base):
    __tablename__ = 'clusters'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    databases = relationship('Database', back_populates='cluster', cascade="all, delete-orphan")

class Database(Base):
    __tablename__ = 'databases'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    cluster_id = Column(Integer, ForeignKey('clusters.id'))
    cluster = relationship('Cluster', back_populates='databases')
    tables = relationship('Table', back_populates='database', cascade="all, delete-orphan")
    
    # Index for faster lookups by cluster_id
    __table_args__ = (Index('idx_database_cluster_id', 'cluster_id'),)

class Table(Base):
    __tablename__ = 'tables'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    database_id = Column(Integer, ForeignKey('databases.id'))
    database = relationship('Database', back_populates='tables')
    fields = relationship('Field', back_populates='table', cascade="all, delete-orphan")
    
    # Index for faster lookups by database_id
    __table_args__ = (Index('idx_table_database_id', 'database_id'),)

class Field(Base):
    __tablename__ = 'fields'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    table_id = Column(Integer, ForeignKey('tables.id'))
    parent_id = Column(Integer, ForeignKey('fields.id'), nullable=True)
    table = relationship('Table', back_populates='fields')
    parent = relationship('Field', remote_side=[id], back_populates='subfields')
    subfields = relationship('Field', back_populates='parent', cascade="all, delete-orphan")
    meta = Column(JSON, default={})
    
    # Indexes for faster lookups
    __table_args__ = (
        Index('idx_field_table_id', 'table_id'),
        Index('idx_field_parent_id', 'parent_id'),
        Index('idx_field_table_parent_name', 'table_id', 'parent_id', 'name'),
    )

class Edge(Base):
    __tablename__ = 'edges'
    id = Column(Integer, primary_key=True)
    from_field_id = Column(Integer, ForeignKey('fields.id'))
    to_field_id = Column(Integer, ForeignKey('fields.id'))
    type = Column(String, nullable=False)  # e.g., 'parent', 'similarity', 'custom'
    from_field = relationship('Field', foreign_keys=[from_field_id])
    to_field = relationship('Field', foreign_keys=[to_field_id])
    
    # Indexes for faster edge lookups
    __table_args__ = (
        Index('idx_edge_from_field_id', 'from_field_id'),
        Index('idx_edge_to_field_id', 'to_field_id'),
        Index('idx_edge_type', 'type'),
        Index('idx_edge_from_to_type', 'from_field_id', 'to_field_id', 'type'),
    ) 