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
        
        print("\n🧪 Testing list_field_paths_by_table_path()...")
        try:
            paths = client.list_field_paths_by_table_path("test_cluster_path", "test_db_path", "test_table_path")
            print(f"✅ Field paths under test_cluster_path/test_db_path/test_table_path:")
            for p in paths:
                print(f"   - {p}")
        except Exception as e:
            print(f"❌ Error listing field paths: {e}")
        
        print("\n🧪 Testing list_field_paths_with_empty_description_by_table_path()...")
        try:
            empty_desc_paths = client.list_field_paths_with_empty_description_by_table_path("test_cluster_path", "test_db_path", "test_table_path")
            print(f"✅ Field paths with empty description under test_cluster_path/test_db_path/test_table_path:")
            for p in empty_desc_paths:
                print(f"   - {p}")
        except Exception as e:
            print(f"❌ Error listing field paths with empty description: {e}")
        
        print("\n🧪 Testing get_field_info_by_path()...")
        try:
            info = client.get_field_info_by_path("test_cluster_path/test_db_path/test_table_path/test_field_path")
            print(f"✅ Info for test_field_path:")
            print(info)
        except Exception as e:
            print(f"❌ Error getting field info by path: {e}")
        
        print("\n🧪 Testing create_field_by_path() with metadata and get_field_info_by_path()...")
        try:
            meta = {"description": "A field with metadata", "type": "string"}
            field_with_meta = client.create_field_by_path(
                "test_cluster_path/test_db_path/test_table_path/field_with_meta2",
                meta=meta
            )
            info = client.get_field_info_by_path("test_cluster_path/test_db_path/test_table_path/field_with_meta2")
            print(f"✅ Info for field_with_meta2:")
            print(info)
            assert info["meta"].get("description") == "A field with metadata"
            assert info["meta"].get("type") == "string"
        except Exception as e:
            print(f"❌ Error with metadata test: {e}")
        
        print("\n🧪 Testing list_field_paths_without_type_by_table_path()...")
        try:
            missing_type_paths = client.list_field_paths_without_type_by_table_path("test_cluster_path", "test_db_path", "test_table_path")
            print(f"✅ Field paths with missing type under test_cluster_path/test_db_path/test_table_path:")
            for p in missing_type_paths:
                print(f"   - {p}")
        except Exception as e:
            print(f"❌ Error listing field paths with missing type: {e}")
        
        print("\n🔍 Debug test for nested subfields...")
        try:
            # Create a simple field structure step by step
            print("Creating root field 'debug_field'...")
            root_field = client.create_field_by_path("test_cluster_path/test_db_path/test_table_path/debug_field")
            print(f"✅ Root field created: {root_field['name']}, id: {root_field['id']}")
            
            print("Creating subfield 'debug_subfield'...")
            subfield = client.create_field_by_path("test_cluster_path/test_db_path/test_table_path/debug_field/debug_subfield")
            print(f"✅ Subfield created: {subfield['name']}, id: {subfield['id']}, parent_id: {subfield.get('parent_id')}")
            
            print("Creating nested subfield 'debug_nested'...")
            nested = client.create_field_by_path("test_cluster_path/test_db_path/test_table_path/debug_field/debug_subfield/debug_nested")
            print(f"✅ Nested subfield created: {nested['name']}, id: {nested['id']}, parent_id: {nested.get('parent_id')}")

            
            print("Creating nested subfield 'debug_nested'...")
            nested = client.create_field_by_path("test_cluster_path/test_db_path/test_table_path/debug_field/debug_subfield/debug_nested/debugnest2")
            print(f"✅ Nested subfield created: {nested['name']}, id: {nested['id']}, parent_id: {nested.get('parent_id')}")
            
            # List all fields to see the structure
            print("Listing all fields in table...")
            all_paths = client.list_field_paths_by_table_path("test_cluster_path", "test_db_path", "test_table_path")
            for p in all_paths:
                if "debug" in p:
                    print(f"   - {p}")
                    
        except Exception as e:
            print(f"❌ Debug test failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 