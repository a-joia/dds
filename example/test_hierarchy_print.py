#!/usr/bin/env python3
"""
Test script to demonstrate the print_hierarchy_by_path function.
Shows how to print the complete hierarchy below a given path.
"""

import sys
import os

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.client import DBDescClient, print_hierarchy_by_path

def main():
    print("🚀 Testing print_hierarchy_by_path function...")
    
    # Initialize client
    client = DBDescClient("http://localhost:8000")
    
    try:
        # Create test resources with hierarchy
        print("\n📦 Creating test hierarchy...")
        
        # Create cluster
        cluster = client.create_cluster("test_hierarchy_cluster")
        print(f"✅ Created cluster: {cluster['name']}")
        
        # Create databases
        db1 = client.create_database_by_path("test_hierarchy_cluster/test_db_1")
        db2 = client.create_database_by_path("test_hierarchy_cluster/test_db_2")
        print(f"✅ Created databases: {db1['name']}, {db2['name']}")
        
        # Create tables
        table1 = client.create_table_by_path("test_hierarchy_cluster/test_db_1/test_table_1")
        table2 = client.create_table_by_path("test_hierarchy_cluster/test_db_1/test_table_2")
        table3 = client.create_table_by_path("test_hierarchy_cluster/test_db_2/test_table_3")
        print(f"✅ Created tables: {table1['name']}, {table2['name']}, {table3['name']}")
        
        # Create fields with metadata
        field1 = client.create_field_by_path("test_hierarchy_cluster/test_db_1/test_table_1/user_id")
        field2 = client.create_field_by_path("test_hierarchy_cluster/test_db_1/test_table_1/email")
        field3 = client.create_field_by_path("test_hierarchy_cluster/test_db_1/test_table_1/address")
        
        # Create subfields
        subfield1 = client.create_field_by_path("test_hierarchy_cluster/test_db_1/test_table_1/address/street"
                                               )
        subfield2 = client.create_field_by_path("test_hierarchy_cluster/test_db_1/test_table_1/address/city"
                                               )
        subfield3 = client.create_field_by_path("test_hierarchy_cluster/test_db_1/test_table_1/address/zip_code"
                                              )
        
        # Create some fields in other tables
        field4 = client.create_field_by_path("test_hierarchy_cluster/test_db_1/test_table_2/product_id")
        field5 = client.create_field_by_path("test_hierarchy_cluster/test_db_2/test_table_3/order_id")
        
        print(f"✅ Created fields and subfields")
        
        # Test 1: Print entire cluster hierarchy
        print("\n" + "="*60)
        print("📋 TEST 1: Print entire cluster hierarchy")
        print("="*60)
        print_hierarchy_by_path("test_hierarchy_cluster")
        
        # Test 2: Print database hierarchy
        print("\n" + "="*60)
        print("📋 TEST 2: Print database hierarchy")
        print("="*60)
        print_hierarchy_by_path("test_hierarchy_cluster/test_db_1")
        
        # Test 3: Print table hierarchy
        print("\n" + "="*60)
        print("📋 TEST 3: Print table hierarchy")
        print("="*60)
        print_hierarchy_by_path("test_hierarchy_cluster/test_db_1/test_table_1")
        
        # Test 4: Test error cases
        print("\n" + "="*60)
        print("📋 TEST 4: Error cases")
        print("="*60)
        
        # Test non-existent cluster
        print("\nTesting non-existent cluster:")
        print_hierarchy_by_path("non_existent_cluster")
        
        # Test non-existent database
        print("\nTesting non-existent database:")
        print_hierarchy_by_path("test_hierarchy_cluster/non_existent_db")
        
        # Test non-existent table
        print("\nTesting non-existent table:")
        print_hierarchy_by_path("test_hierarchy_cluster/test_db_1/non_existent_table")
        
        # Test invalid path format
        print("\nTesting invalid path format:")
        print_hierarchy_by_path("cluster/database/table/field")
        
        print("\n🎉 All hierarchy printing tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 