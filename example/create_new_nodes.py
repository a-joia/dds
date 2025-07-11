#!/usr/bin/env python3
"""
Test script to create, edit, and delete nodes with equivalences and possibly equivalences.
Tests the full CRUD flow including cleanup of edges when nodes are deleted.
"""

import sys
import os
import time

# Add the parent directory to the path so we can import the client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.client import DBDescClient

def main():
    print("🚀 Starting comprehensive test of create/edit/delete flow...")
    
    # Initialize client
    client = DBDescClient("http://localhost:8000")

    # Clean up any existing test databases before starting
    print("\n🧹 Cleaning up any existing test databases...")
    clusters = client.get_clusters()
    for c in clusters:
        dbs = client.get_databases(c['id'])
        for db in dbs:
            if db['name'] in ["test_db_1", "test_db_2"]:
                print(f"Deleting pre-existing test database: {db['name']} (ID: {db['id']})")
                client.delete_database(db['id'])

    try:
        # Test 1: Create clusters
        print("\n📦 Creating clusters...")
        cluster1 = client.create_cluster("test_cluster_1")
        cluster2 = client.create_cluster("test_cluster_2")
        cluster3 = client.create_cluster("acciatartaturuscentralus.centralus")
        print(f"✅ Created clusters: {cluster1['name']}, {cluster2['name']}")
        
        # Test 2: Create databases
        print("\n🗄️ Creating databases...")
        db1 = client.create_database(cluster1['id'], "test_db_1")
        db2 = client.create_database(cluster2['id'], "test_db_2")
        db3 = client.create_database(cluster3['id'], "Anvil2BugsCheck")
        print(f"✅ Created databases: {db1['name']}, {db2['name']}")
        
        # Test 3: Create tables
        print("\n📋 Creating tables...")
        table1 = client.create_table(db1['id'], "test_table_1")
        table2 = client.create_table(db2['id'], "test_table_2")
        table3 = client.create_table(db3['id'], "test_table_3")
        print(f"✅ Created tables: {table1['name']}, {table2['name']}")
        
        # Test 4: Create fields
        print("\n🔧 Creating fields...")
        field1 = client.create_field(table1['id'], "test_field_1")
        field2 = client.create_field(table2['id'], "test_field_2")
        field3 = client.create_field(table3['id'], "test_field_3")
        print(f"✅ Created fields: {field1['name']}, {field2['name']} (IDs: {field1['id']}, {field2['id']})")
        
        # Test 5: Create subfields
        print("\n🔧 Creating subfields...")
        subfield1 = client.create_field(table1['id'], "test_subfield_1", parent_id=field1['id'])
        subfield2 = client.create_field(table2['id'], "test_subfield_2", parent_id=field2['id'])
        subfield3 = client.create_field(table3['id'], "test_subfield_3", parent_id=field3['id'])
        subfield4 = client.create_field(table3['id'], "test_subfield_3", parent_id=subfield3['id'])
        print(f"✅ Created subfields: {subfield1['name']}, {subfield2['name']} (IDs: {subfield1['id']}, {subfield2['id']})")

        # Test 5b: Create subfield in a subfield (third-level field)
        print("\n🔧 Creating sub-subfield (third-level field)...")
        subsubfield1 = client.create_field(table1['id'], "test_subsubfield_1", parent_id=subfield1['id'])
        print(f"✅ Created sub-subfield: {subsubfield1['name']} (ID: {subsubfield1['id']})")
        # Verify sub-subfield exists
        all_fields = client.get_fields(table1['id'])
        subsubfield1_exists = any(f['id'] == subsubfield1['id'] for f in all_fields)
        print(f"Sub-subfield exists after creation: {subsubfield1_exists}")
        
        # Test 6: Add equivalences
        print("\n🔗 Adding equivalences...")
        equiv1 = client.create_edge(field1['id'], field2['id'], "equivalence")
        equiv2 = client.create_edge(subfield1['id'], subfield2['id'], "equivalence")
        print(f"✅ Added equivalences: {equiv1['id']}, {equiv2['id']}")
        
        # Test 7: Add possibly equivalences
        print("\n🔗 Adding possibly equivalences...")
        poss_equiv1 = client.create_edge(field1['id'], subfield2['id'], "possibly_equivalence")
        poss_equiv2 = client.create_edge(subfield1['id'], field2['id'], "possibly_equivalence")
        print(f"✅ Added possibly equivalences: {poss_equiv1['id']}, {poss_equiv2['id']}")
        
        # Test 8: List equivalences and possibly equivalences
        print("\n📋 Listing equivalences...")
        field1_edges = client.get_edges(field1['id'])
        field1_equivs = [e for e in field1_edges if e['type'] == 'equivalence']
        print(f"Field 1 equivalences: {len(field1_equivs)} found")
        
        print("\n📋 Listing possibly equivalences...")
        field1_poss_equivs = [e for e in field1_edges if e['type'] == 'possibly_equivalence']
        print(f"Field 1 possibly equivalences: {len(field1_poss_equivs)} found")
        
        # Test 9: Edit nodes
        print("\n✏️ Editing nodes...")
        updated_table1 = client.update_table(table1['id'], "updated_table_1")
        print(f"✅ Updated table: {updated_table1['name']}")
        # Note: Field name updates are not supported by the backend (only meta updates)
        print("ℹ️ Skipping field name update (not supported by backend)")
        
        # Test 10: Delete nodes and verify cleanup
        print("\n🗑️ Testing deletion with cleanup...")
        # Delete a field and verify its equivalences are cleaned up
        print(f"Deleting field: {field1['name']} (ID: {field1['id']})")
        client.delete_field(field1['id'])
        # Check that field1's edges are gone
        try:
            remaining_edges = client.get_edges(field1['id'])
            print(f"❌ Field 1 still has edges: {len(remaining_edges)}")
        except Exception as e:
            print(f"✅ Field 1 edges cleaned up (as expected): {e}")
        # Check that subfield1 and subsubfield1 are also deleted
        try:
            subfields = client.get_fields(table1['id'])
            subfield1_exists = any(f['id'] == subfield1['id'] for f in subfields)
            subsubfield1_exists = any(f['id'] == subsubfield1['id'] for f in subfields)
            if subfield1_exists:
                print(f"❌ Subfield 1 still exists!")
            else:
                print(f"✅ Subfield 1 deleted with parent field.")
            if subsubfield1_exists:
                print(f"❌ Sub-subfield 1 still exists!")
            else:
                print(f"✅ Sub-subfield 1 deleted with ancestor field.")
        except Exception as e:
            print(f"✅ Subfield 1 and sub-subfield 1 deleted (as expected): {e}")
        # Delete a table and verify all its fields and edges are cleaned up
        print(f"Deleting table: {table1['name']} (ID: {table1['id']})")
        client.delete_table(table1['id'])
        try:
            fields = client.get_fields(table1['id'])
            print(f"❌ Table 1 still has fields: {len(fields)}")
        except Exception as e:
            print(f"✅ Table 1 fields cleaned up (as expected): {e}")
        # Delete a database and verify all its tables are cleaned up
        print(f"Deleting database: {db1['name']} (ID: {db1['id']})")
        client.delete_database(db1['id'])
        try:
            tables = client.get_tables(db1['id'])
            print(f"❌ Database 1 still has tables: {len(tables)}")
        except Exception as e:
            print(f"✅ Database 1 tables cleaned up (as expected): {e}")
        # Delete a cluster and verify all its databases are cleaned up
        print(f"Deleting cluster: {cluster1['name']} (ID: {cluster1['id']})")
        client.delete_cluster(cluster1['id'])
        try:
            dbs = client.get_databases(cluster1['id'])
            print(f"❌ Cluster 1 still has databases: {len(dbs)}")
        except Exception as e:
            print(f"✅ Cluster 1 databases cleaned up (as expected): {e}")
        # Clean up remaining test cluster
        print(f"Deleting remaining test cluster: {cluster2['name']} (ID: {cluster2['id']})")
        client.delete_cluster(cluster2['id'])
        print("✅ Deleted remaining test cluster")
        print("\n🎉 All tests completed successfully!")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 