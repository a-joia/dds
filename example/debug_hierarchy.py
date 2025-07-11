#!/usr/bin/env python3
"""
Debug script to test hierarchy printing with minimal data.
"""

import sys
import os

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.client import DBDescClient, print_hierarchy_by_path

def main():
    print("🔍 Debugging hierarchy printing...")
    
    # Initialize client
    client = DBDescClient("http://localhost:8000")
    
    try:
        # Create minimal test data
        print("\n📦 Creating minimal test data...")
        
        # Create cluster
        cluster = client.create_cluster("debug_cluster")
        print(f"✅ Created cluster: {cluster['name']}")
        
        # Create database
        db = client.create_database_by_path("debug_cluster/debug_db")
        print(f"✅ Created database: {db['name']}")
        
        # Create table
        table = client.create_table_by_path("debug_cluster/debug_db/debug_table")
        print(f"✅ Created table: {table['name']}")
        
        # Create root field
        root_field = client.create_field_by_path("debug_cluster/debug_db/debug_table/root_field")
        print(f"✅ Created root field: {root_field['name']}")
        
        print("🔍 About to create subfield...")
        # Create subfield
        try:
            # Try creating subfield directly first
            print("🔍 Creating subfield directly...")
            sub_field = client.create_field(table['id'], "sub_field", parent_id=root_field['id'])
            print(f"✅ Created subfield directly: {sub_field['name']}")
        except Exception as e:
            print(f"❌ Failed to create subfield directly: {e}")
            import traceback
            traceback.print_exc()
            
        try:
            # Now try the path method
            print("🔍 Creating subfield by path...")
            sub_field2 = client.create_field_by_path("debug_cluster/debug_db/debug_table/root_field/sub_field2")
            print(f"✅ Created subfield by path: {sub_field2['name']}")
        except Exception as e:
            print(f"❌ Failed to create subfield by path: {e}")
            import traceback
            traceback.print_exc()
        
        # Debug: Let's check what fields we actually have
        print("\n🔍 Debug: Checking all fields in table...")
        all_fields = client.get_fields(table['id'])
        print(f"Total fields in table: {len(all_fields)}")
        for field in all_fields:
            print(f"  Field: {field['name']}, ID: {field['id']}, Parent ID: {field.get('parent_id')}")
        
        # Let's also check the raw API response
        print("\n🔍 Debug: Raw API response for fields...")
        import requests
        response = requests.get(f"http://localhost:8000/tables/{table['id']}/fields/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Test hierarchy printing
        print("\n" + "="*50)
        print("📋 TESTING HIERARCHY PRINTING")
        print("="*50)
        print_hierarchy_by_path("debug_cluster/debug_db/debug_table")
        
        print("\n🎉 Debug completed!")
        
    except Exception as e:
        print(f"❌ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 