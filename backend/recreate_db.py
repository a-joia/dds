#!/usr/bin/env python3
"""
Script to recreate the database with new indexes and optimizations.
Run this to apply the performance improvements.
"""

print('Starting recreate_db.py')
import os
import sys
print('Before imports')
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from backend.database import engine, init_db
from backend.models import Base

print('Imports successful')

def recreate_database():
    """Recreate the database with new schema and optimizations."""
    # Remove existing database file
    db_file = os.path.join(os.path.dirname(__file__), "dbdesc.db")
    if os.path.exists(db_file):
        print(f"Removing existing database: {db_file}")
        os.remove(db_file)
    
    # Remove WAL files if they exist
    wal_file = db_file + "-wal"
    if os.path.exists(wal_file):
        print(f"Removing WAL file: {wal_file}")
        os.remove(wal_file)
    
    shm_file = db_file + "-shm"
    if os.path.exists(shm_file):
        print(f"Removing SHM file: {shm_file}")
        os.remove(shm_file)
    
    # Create new database with optimizations
    print("Creating new database with indexes and optimizations...")
    init_db()
    print("Database recreated successfully!")
    print("Note: You'll need to re-import your data.")

if __name__ == "__main__":
    recreate_database() 