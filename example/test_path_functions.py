#!/usr/bin/env python3
"""
Test script to demonstrate the new path-based creation functions.
Tests create_database_by_path(), create_table_by_path(), and create_field_by_path().
"""

import sys
import os

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.client import DBDescClient

def main():
    print("🚀 Testing path-based creation functions...")
    
    # Initialize client
    client = DBDescClient("http://localhost:8000")
    
    try:
        # Test 1: Create a cluster first
        print("\n📦 Creating a test cluster...")
        cluster = client.create_cluster("test_cluster_path")
        print(f"✅ Created cluster: {cluster['name']}")
        
        # Test 2: Create database by path
        print("\n🗄️ Testing create_database_by_path()...")
        try:
            db = client.create_database_by_path("test_cluster_path/test_db_path")
            print(f"✅ Created database by path: {db['name']}")
        except ValueError as e:
            print(f"❌ Error creating database: {e}")
        
        # Test 3: Create table by path
        print("\n📋 Testing create_table_by_path()...")
        try:
            table = client.create_table_by_path("test_cluster_path/test_db_path/test_table_path")
            print(f"✅ Created table by path: {table['name']}")
        except ValueError as e:
            print(f"❌ Error creating table: {e}")
        
        # Test 4: Create field by path
        print("\n🔧 Testing create_field_by_path()...")
        try:
            field = client.create_field_by_path("test_cluster_path/test_db_path/test_table_path/test_field_path")
            print(f"✅ Created field by path: {field['name']}")
        except ValueError as e:
            print(f"❌ Error creating field: {e}")
        
        # Test 5: Create subfield by path
        print("\n🔧 Testing create_field_by_path() with subfield...")
        try:
            subfield = client.create_field_by_path("test_cluster_path/test_db_path/test_table_path/test_field_path/test_subfield_path")
            print(f"✅ Created subfield by path: {subfield['name']}")
        except ValueError as e:
            print(f"❌ Error creating subfield: {e}")
        
        # Test 6: Create nested subfield by path
        print("\n🔧 Testing create_field_by_path() with nested subfield...")
        try:
            nested_subfield = client.create_field_by_path("test_cluster_path/test_db_path/test_table_path/test_field_path/test_subfield_path/test_nested_subfield_path")
            print(f"✅ Created nested subfield by path: {nested_subfield['name']}")
        except ValueError as e:
            print(f"❌ Error creating nested subfield: {e}")
        
        # Test 7: Test error cases
        print("\n❌ Testing error cases...")
        
        # Test non-existent cluster
        print("\nTesting non-existent cluster:")
        try:
            client.create_database_by_path("non_existent_cluster/test_db")
        except ValueError as e:
            print(f"✅ Expected error: {e}")
        
        # Test non-existent database
        print("\nTesting non-existent database:")
        try:
            client.create_table_by_path("test_cluster_path/non_existent_db/test_table")
        except ValueError as e:
            print(f"✅ Expected error: {e}")
        
        # Test non-existent table
        print("\nTesting non-existent table:")
        try:
            client.create_field_by_path("test_cluster_path/test_db_path/non_existent_table/test_field")
        except ValueError as e:
            print(f"✅ Expected error: {e}")
        
        # Test non-existent parent field
        print("\nTesting non-existent parent field:")
        try:
            client.create_field_by_path("test_cluster_path/test_db_path/test_table_path/non_existent_field/test_subfield")
        except ValueError as e:
            print(f"✅ Expected error: {e}")
        
        # Test invalid path formats
        print("\nTesting invalid path formats:")
        try:
            client.create_database_by_path("invalid_path")
        except ValueError as e:
            print(f"✅ Expected error: {e}")
        
        try:
            client.create_table_by_path("cluster_only")
        except ValueError as e:
            print(f"✅ Expected error: {e}")
        
        try:
            client.create_field_by_path("cluster/db")
        except ValueError as e:
            print(f"✅ Expected error: {e}")
        
        # Test with metadata
        print("\n🔧 Testing create_field_by_path() with metadata...")
        try:
            field_with_meta = client.create_field_by_path(
                "test_cluster_path/test_db_path/test_table_path/field_with_meta",
                meta={"type": "string", "description": "A test field with metadata"}
            )
            print(f"✅ Created field with metadata: {field_with_meta['name']}")
            print(f"   Metadata: {field_with_meta.get('meta', {})}")
        except ValueError as e:
            print(f"❌ Error creating field with metadata: {e}")
        
        print("\n🎉 All path-based function tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 