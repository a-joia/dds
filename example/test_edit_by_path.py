#!/usr/bin/env python3
"""
Test script to demonstrate the edit_by_path and rename_by_path functions.
Tests editing field metadata and renaming resources by path.
"""

import sys
import os

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.client import DBDescClient, edit_by_path, rename_by_path

def main():
    print("🚀 Testing edit_by_path and rename_by_path functions...")
    
    # Initialize client
    client = DBDescClient("http://localhost:8000")
    
    try:
        # Create test resources first
        print("\n📦 Creating test resources...")
        cluster = client.create_cluster("test_edit_cluster")
        db = client.create_database_by_path("test_edit_cluster/test_edit_db")
        table = client.create_table_by_path("test_edit_cluster/test_edit_db/test_edit_table")
        field = client.create_field_by_path("test_edit_cluster/test_edit_db/test_edit_table/test_field")
        subfield = client.create_field_by_path("test_edit_cluster/test_edit_db/test_edit_table/test_field/test_subfield")
        
        print(f"✅ Created test resources:")
        print(f"   Cluster: {cluster['name']}")
        print(f"   Database: {db['name']}")
        print(f"   Table: {table['name']}")
        print(f"   Field: {field['name']}")
        print(f"   Subfield: {subfield['name']}")
        
        # Test 1: Edit field metadata
        print("\n✏️ Testing edit_by_path - field metadata update...")
        try:
            updated_field = edit_by_path("test_edit_cluster/test_edit_db/test_edit_table/test_field", {
                "description": "This is an updated field description",
                "type": "string",
                "nullable": False,
                "max_length": 255
            })
            print(f"✅ Updated field metadata: {updated_field.get('meta', {})}")
        except Exception as e:
            print(f"❌ Error updating field metadata: {e}")
        
        # Test 2: Edit subfield metadata
        print("\n✏️ Testing edit_by_path - subfield metadata update...")
        try:
            updated_subfield = edit_by_path("test_edit_cluster/test_edit_db/test_edit_table/test_field/test_subfield", {
                "description": "This is an updated subfield description",
                "type": "integer",
                "default": 0,
                "min_value": 0,
                "max_value": 100
            })
            print(f"✅ Updated subfield metadata: {updated_subfield.get('meta', {})}")
        except Exception as e:
            print(f"❌ Error updating subfield metadata: {e}")
        
        # Test 3: Rename cluster
        print("\n✏️ Testing rename_by_path - cluster rename...")
        try:
            updated_cluster = rename_by_path("test_edit_cluster", "test_edit_cluster_renamed")
            print(f"✅ Renamed cluster: {updated_cluster['name']}")
        except Exception as e:
            print(f"❌ Error renaming cluster: {e}")
        
        # Test 4: Rename database
        print("\n✏️ Testing rename_by_path - database rename...")
        try:
            updated_db = rename_by_path("test_edit_cluster_renamed/test_edit_db", "test_edit_db_renamed")
            print(f"✅ Renamed database: {updated_db['name']}")
        except Exception as e:
            print(f"❌ Error renaming database: {e}")
        
        # Test 5: Rename table
        print("\n✏️ Testing rename_by_path - table rename...")
        try:
            updated_table = rename_by_path("test_edit_cluster_renamed/test_edit_db_renamed/test_edit_table", "test_edit_table_renamed")
            print(f"✅ Renamed table: {updated_table['name']}")
        except Exception as e:
            print(f"❌ Error renaming table: {e}")
        
        # Test 6: Edit field metadata after rename (using new paths)
        print("\n✏️ Testing edit_by_path - field metadata after rename...")
        try:
            updated_field_after_rename = edit_by_path("test_edit_cluster_renamed/test_edit_db_renamed/test_edit_table_renamed/test_field", {
                "description": "Field description after rename",
                "type": "varchar",
                "is_primary_key": True
            })
            print(f"✅ Updated field metadata after rename: {updated_field_after_rename.get('meta', {})}")
        except Exception as e:
            print(f"❌ Error updating field metadata after rename: {e}")
        
        # Test 7: Test error cases for edit_by_path
        print("\n❌ Testing error cases for edit_by_path...")
        
        # Test invalid field path format
        print("\nTesting invalid field path format:")
        try:
            edit_by_path("cluster/database", {"description": "test"})
        except ValueError as e:
            print(f"✅ Expected ValueError: {e}")
        
        # Test non-existent field
        print("\nTesting non-existent field:")
        try:
            edit_by_path("test_edit_cluster_renamed/test_edit_db_renamed/test_edit_table_renamed/non_existent_field", {"description": "test"})
        except Exception as e:
            print(f"✅ Expected error: {e}")
        
        # Test 8: Test error cases for rename_by_path
        print("\n❌ Testing error cases for rename_by_path...")
        
        # Test invalid rename path format
        print("\nTesting invalid rename path format:")
        try:
            rename_by_path("cluster/database/table/field", "new_name")
        except ValueError as e:
            print(f"✅ Expected ValueError: {e}")
        
        # Test non-existent resource
        print("\nTesting non-existent resource:")
        try:
            rename_by_path("non_existent_cluster", "new_name")
        except Exception as e:
            print(f"✅ Expected error: {e}")
        
        print("\n🎉 All edit_by_path and rename_by_path tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 