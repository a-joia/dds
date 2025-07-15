import pytest
from api.path_client import PathClient
import uuid
import threading
import time

def unique_name(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

client = PathClient()

# --- Cluster/Database/Table/Field Creation & Deletion ---
def test_create_and_delete_hierarchy():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    fname = unique_name('field')
    # Create
    c = client.create_cluster(cname)
    assert c['name'] == cname
    db = client.create_database(f"{cname}/{dname}")
    assert db['name'] == dname
    table = client.create_table(f"{cname}/{dname}/{tname}")
    assert table['name'] == tname
    field = client.create_field(f"{cname}/{dname}/{tname}/{fname}", meta={"type": "int"})
    assert field['name'] == fname
    # Delete field
    client.delete_field(f"{cname}/{dname}/{tname}/{fname}")
    # Delete table
    client.delete_table(f"{cname}/{dname}/{tname}")
    # Delete database
    client.delete_database(f"{cname}/{dname}")
    # Delete cluster
    client.delete_cluster(cname)

# --- Metadata Editing ---
def test_metadata_editing():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    fname = unique_name('field')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    client.create_field(f"{cname}/{dname}/{tname}/{fname}", meta={"type": "int"})
    # Edit description
    client.edit_field_description(f"{cname}/{dname}/{tname}/{fname}", "desc1")
    meta = client.get_field_metadata(f"{cname}/{dname}/{tname}/{fname}")
    assert meta is not None and meta['description'] == "desc1"
    # Add metadata
    client.add_field_metadata(f"{cname}/{dname}/{tname}/{fname}", {"unit": "kg"})
    meta = client.get_field_metadata(f"{cname}/{dname}/{tname}/{fname}")
    assert meta is not None and meta['unit'] == "kg"
    # Overwrite only one key
    client.edit_field_metadata(f"{cname}/{dname}/{tname}/{fname}", {"unit": "g"})
    meta = client.get_field_metadata(f"{cname}/{dname}/{tname}/{fname}")
    assert meta is not None and meta['unit'] == "g" and meta['description'] == "desc1"
    # Clean up
    client.delete_field(f"{cname}/{dname}/{tname}/{fname}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Edge Management ---
def test_edge_management():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    f1 = unique_name('f1')
    f2 = unique_name('f2')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    client.create_field(f"{cname}/{dname}/{tname}/{f1}", meta={"type": "int"})
    client.create_field(f"{cname}/{dname}/{tname}/{f2}", meta={"type": "int"})
    # Add edge
    client.add_edge(f"{cname}/{dname}/{tname}/{f1}", f"{cname}/{dname}/{tname}/{f2}")
    edges = client.get_edges(f"{cname}/{dname}/{tname}/{f1}")
    assert any(f2 in e['path'] for e in edges)
    # Remove edge
    client.remove_edge(f"{cname}/{dname}/{tname}/{f1}", f"{cname}/{dname}/{tname}/{f2}")
    edges = client.get_edges(f"{cname}/{dname}/{tname}/{f1}")
    assert not any(f2 in e['path'] for e in edges)
    # Clean up
    client.delete_field(f"{cname}/{dname}/{tname}/{f1}")
    client.delete_field(f"{cname}/{dname}/{tname}/{f2}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Hierarchy and Listing ---
def test_hierarchy_and_listing():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    f1 = unique_name('f1')
    f2 = unique_name('f2')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    client.create_field(f"{cname}/{dname}/{tname}/{f1}", meta={"type": "int", "unit": "kg"})
    client.create_field(f"{cname}/{dname}/{tname}/{f2}", meta={"type": "float", "unit": "g"})
    # List clusters
    clusters = client.list_clusters()
    assert cname in clusters
    # List databases
    dbs = client.list_database(cname)
    assert f"{cname}/{dname}" in dbs
    # List fields
    fields = client.list_fields(f"{cname}/{dname}/{tname}")
    assert any(f1 in f for f in fields) and any(f2 in f for f in fields)
    # Hierarchy filter
    filtered = client.get_hierarchy(f"{cname}/{dname}/{tname}", filter=[("unit", "kg")])
    assert any(f1 in f for f in filtered) and not any(f2 in f for f in filtered)
    # Clean up
    client.delete_field(f"{cname}/{dname}/{tname}/{f1}")
    client.delete_field(f"{cname}/{dname}/{tname}/{f2}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Corner Cases ---
def test_corner_cases():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    f1 = unique_name('f1')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    # Try to create duplicate field
    client.create_field(f"{cname}/{dname}/{tname}/{f1}", meta={"type": "int"})
    try:
        client.create_field(f"{cname}/{dname}/{tname}/{f1}", meta={"type": "int"})
        assert False, "Should not allow duplicate field creation"
    except Exception:
        pass
    # Try to delete non-existent field
    try:
        client.delete_field(f"{cname}/{dname}/{tname}/notexist")
    except Exception:
        pass
    # Try to get metadata for non-existent field
    try:
        client.get_field_metadata(f"{cname}/{dname}/{tname}/notexist")
    except Exception:
        pass
    # Clean up
    client.delete_field(f"{cname}/{dname}/{tname}/{f1}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Connected Databases ---
def test_connected_databases():
    cname = unique_name('cluster')
    d1 = unique_name('db1')
    d2 = unique_name('db2')
    t1 = unique_name('table1')
    t2 = unique_name('table2')
    f1 = unique_name('f1')
    f2 = unique_name('f2')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{d1}")
    client.create_database(f"{cname}/{d2}")
    client.create_table(f"{cname}/{d1}/{t1}")
    client.create_table(f"{cname}/{d2}/{t2}")
    client.create_field(f"{cname}/{d1}/{t1}/{f1}", meta={"type": "int"})
    client.create_field(f"{cname}/{d2}/{t2}/{f2}", meta={"type": "int"})
    # Add edge between fields in different databases
    client.add_edge(f"{cname}/{d1}/{t1}/{f1}", f"{cname}/{d2}/{t2}/{f2}")
    connected = client.get_connected_databases(f"{cname}/{d1}")
    assert f"{cname}/{d2}" in connected
    # Clean up
    client.delete_field(f"{cname}/{d1}/{t1}/{f1}")
    client.delete_field(f"{cname}/{d2}/{t2}/{f2}")
    client.delete_table(f"{cname}/{d1}/{t1}")
    client.delete_table(f"{cname}/{d2}/{t2}")
    client.delete_database(f"{cname}/{d1}")
    client.delete_database(f"{cname}/{d2}")
    client.delete_cluster(cname)

# --- Advanced/Edge Scenarios ---
def test_deeply_nested_fields():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    # Create hierarchy step by step
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    base = f"{cname}/{dname}/{tname}"
    client.create_field(f"{base}/f1", meta={"type": "int"})
    client.create_field(f"{base}/f1/sf1", meta={"type": "int"})
    client.create_field(f"{base}/f1/sf1/sf2", meta={"type": "int"})
    path = f"{base}/f1/sf1/sf2/sf3"
    client.create_field(path, meta={"type": "int", "deep": True})
    # Edit deep field
    client.edit_field_description(path, "deepdesc")
    meta = client.get_field_metadata(path)
    assert meta is not None and meta['description'] == "deepdesc"
    # Delete deep field
    client.delete_field(path)
    # Clean up
    client.delete_field(f"{base}/f1/sf1/sf2")
    client.delete_field(f"{base}/f1/sf1")
    client.delete_field(f"{base}/f1")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

def test_complex_metadata():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    fname = unique_name('field')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    complex_meta = {"type": "object", "props": {"a": 1, "b": [1,2,3]}, "desc": "complex"}
    client.create_field(f"{cname}/{dname}/{tname}/{fname}", meta=complex_meta)
    meta = client.get_field_metadata(f"{cname}/{dname}/{tname}/{fname}")
    assert meta is not None and meta['props']['a'] == 1
    # Overwrite with partial keys
    client.edit_field_metadata(f"{cname}/{dname}/{tname}/{fname}", {"props": {"a": 2}})
    meta = client.get_field_metadata(f"{cname}/{dname}/{tname}/{fname}")
    assert meta is not None and meta['props']['a'] == 2
    # Clean up
    client.delete_field(f"{cname}/{dname}/{tname}/{fname}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

def test_edge_cases_for_edges():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    f1 = unique_name('f1')
    f2 = unique_name('f2')
    fdeep = f"{f1}/sf1/sf2"
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    # Create parent fields step by step for fdeep
    base = f"{cname}/{dname}/{tname}"
    client.create_field(f"{base}/{f1}", meta={"type": "int"})
    client.create_field(f"{base}/{f1}/sf1", meta={"type": "int"})
    client.create_field(f"{base}/{f1}/sf1/sf2", meta={"type": "int"})
    client.create_field(f"{cname}/{dname}/{tname}/{f2}", meta={"type": "int"})
    # Add edge between deep subfield and f2
    client.add_edge(f"{base}/{fdeep}", f"{cname}/{dname}/{tname}/{f2}")
    edges = client.get_edges(f"{base}/{fdeep}")
    assert any(f2 in e['path'] for e in edges)
    # Add same edge again (should not duplicate or error)
    try:
        client.add_edge(f"{base}/{fdeep}", f"{cname}/{dname}/{tname}/{f2}")
    except Exception:
        pass
    # Remove non-existent edge
    try:
        client.remove_edge(f"{cname}/{dname}/{tname}/{f1}", f"{cname}/{dname}/{tname}/{f2}")
    except Exception:
        pass
    # Clean up
    for p in [f"{base}/{fdeep}", f"{base}/{f1}/sf1/sf2", f"{base}/{f1}/sf1", f"{base}/{f1}", f"{cname}/{dname}/{tname}/{f2}"]:
        try:
            client.delete_field(p)
        except Exception:
            pass
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

def test_bulk_deletion():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    f1 = unique_name('f1')
    f2 = unique_name('f2')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    client.create_field(f"{cname}/{dname}/{tname}/{f1}", meta={"type": "int"})
    client.create_field(f"{cname}/{dname}/{tname}/{f2}", meta={"type": "int"})
    # Delete database
    client.delete_database(f"{cname}/{dname}")
    # Ensure fields and table are gone
    try:
        client.get_field_metadata(f"{cname}/{dname}/{tname}/{f1}")
        assert False, "Field should not exist after database deletion"
    except Exception:
        pass
    # Clean up
    client.delete_cluster(cname)

def test_invalid_paths():
    client = PathClient()
    # Too short
    try:
        client.create_database("onlycluster")
        assert False, "Should fail on invalid path"
    except Exception:
        pass
    # Too long
    try:
        client.create_table("a/b/c/d")
        assert False, "Should fail on invalid path"
    except Exception:
        pass
    # Special characters
    cname = unique_name('clu!@#')
    try:
        client.create_cluster(cname)
        client.delete_cluster(cname)
    except Exception:
        pass

def test_edge_directionality():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    f1 = unique_name('f1')
    f2 = unique_name('f2')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    client.create_field(f"{cname}/{dname}/{tname}/{f1}", meta={"type": "int"})
    client.create_field(f"{cname}/{dname}/{tname}/{f2}", meta={"type": "int"})
    client.add_edge(f"{cname}/{dname}/{tname}/{f1}", f"{cname}/{dname}/{tname}/{f2}")
    # Remove edge in reverse order
    client.remove_edge(f"{cname}/{dname}/{tname}/{f2}", f"{cname}/{dname}/{tname}/{f1}")
    edges = client.get_edges(f"{cname}/{dname}/{tname}/{f1}")
    assert not any(f2 in e['path'] for e in edges)
    # Clean up
    client.delete_field(f"{cname}/{dname}/{tname}/{f1}")
    client.delete_field(f"{cname}/{dname}/{tname}/{f2}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

def test_advanced_filtering():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    f1 = unique_name('f1')
    f2 = unique_name('f2')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    client.create_field(f"{cname}/{dname}/{tname}/{f1}", meta={"type": "int", "unit": "kg", "color": "red"})
    client.create_field(f"{cname}/{dname}/{tname}/{f2}", meta={"type": "float", "unit": "g", "color": "blue"})
    # Filter by multiple keys
    filtered = client.get_hierarchy(f"{cname}/{dname}/{tname}", filter=[("unit", "kg"), ("color", "red")])
    assert any(f1 in f for f in filtered) and not any(f2 in f for f in filtered)
    # Filter by non-existent key
    filtered = client.get_hierarchy(f"{cname}/{dname}/{tname}", filter=[("nonexistent", "value")])
    assert filtered == []
    # Clean up
    client.delete_field(f"{cname}/{dname}/{tname}/{f1}")
    client.delete_field(f"{cname}/{dname}/{tname}/{f2}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Concurrency Test ---
def test_concurrent_creation_and_deletion():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    base = f"{cname}/{dname}/{tname}"
    field_names = [f"f{i}" for i in range(10)]
    def create_field(fname):
        client.create_field(f"{base}/{fname}", meta={"type": "int"})
    def delete_field(fname):
        try:
            client.delete_field(f"{base}/{fname}")
        except Exception:
            pass
    threads = []
    # Concurrent creation
    for fname in field_names:
        t = threading.Thread(target=create_field, args=(fname,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    # Concurrent deletion
    threads = []
    for fname in field_names:
        t = threading.Thread(target=delete_field, args=(fname,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Rapid Edits Test ---
def test_rapid_edits():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    fname = unique_name('field')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    client.create_field(f"{cname}/{dname}/{tname}/{fname}", meta={"type": "int"})
    # Rapidly update metadata
    for i in range(20):
        client.edit_field_metadata(f"{cname}/{dname}/{tname}/{fname}", {"version": i})
        meta = client.get_field_metadata(f"{cname}/{dname}/{tname}/{fname}")
        assert meta is not None and meta['version'] == i
    client.delete_field(f"{cname}/{dname}/{tname}/{fname}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Load Test (Basic) ---
def test_basic_load():
    cname = unique_name('cluster')
    dname = unique_name('db')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    num_tables = 10
    num_fields = 20
    tnames = [f"t{i}" for i in range(num_tables)]
    start = time.time()
    for tname in tnames:
        client.create_table(f"{cname}/{dname}/{tname}")
        for j in range(num_fields):
            client.create_field(f"{cname}/{dname}/{tname}/f{j}", meta={"type": "int"})
    elapsed = time.time() - start
    print(f"Created {num_tables} tables x {num_fields} fields in {elapsed:.2f} seconds")
    # Clean up
    for tname in tnames:
        for j in range(num_fields):
            try:
                client.delete_field(f"{cname}/{dname}/{tname}/f{j}")
            except Exception:
                pass
        client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Simultaneous Creation of the Same Resource ---
def test_simultaneous_creation():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    fname = unique_name('field')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    base = f"{cname}/{dname}/{tname}/{fname}"
    results = []
    def create_field():
        try:
            client.create_field(base, meta={"type": "int"})
            results.append("success")
        except Exception as e:
            results.append(str(e))
    threads = [threading.Thread(target=create_field) for _ in range(2)]
    for t in threads: t.start()
    for t in threads: t.join()
    print("Results:", results)
    assert results.count("success") == 2
    client.delete_field(base)
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Simultaneous Deletion and Access ---
def test_deletion_and_access_race():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    fname = unique_name('field')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    client.create_field(f"{cname}/{dname}/{tname}/{fname}", meta={"type": "int"})
    def delete_field():
        try:
            client.delete_field(f"{cname}/{dname}/{tname}/{fname}")
        except Exception:
            pass
    def access_field():
        try:
            client.get_field_metadata(f"{cname}/{dname}/{tname}/{fname}")
        except Exception:
            pass
    t1 = threading.Thread(target=delete_field)
    t2 = threading.Thread(target=access_field)
    t1.start(); t2.start(); t1.join(); t2.join()
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Rapid Add/Remove Edge ---
def test_rapid_add_remove_edge():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    f1 = unique_name('f1')
    f2 = unique_name('f2')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    client.create_field(f"{cname}/{dname}/{tname}/{f1}", meta={"type": "int"})
    client.create_field(f"{cname}/{dname}/{tname}/{f2}", meta={"type": "int"})
    for _ in range(10):
        client.add_edge(f"{cname}/{dname}/{tname}/{f1}", f"{cname}/{dname}/{tname}/{f2}")
        client.remove_edge(f"{cname}/{dname}/{tname}/{f1}", f"{cname}/{dname}/{tname}/{f2}")
    edges = client.get_edges(f"{cname}/{dname}/{tname}/{f1}")
    assert not any(f2 in e['path'] for e in edges)
    client.delete_field(f"{cname}/{dname}/{tname}/{f1}")
    client.delete_field(f"{cname}/{dname}/{tname}/{f2}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Large Metadata Payload ---
def test_large_metadata():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    fname = unique_name('field')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    large_meta = {"type": "object", "data": {str(i): i for i in range(1000)}}
    client.create_field(f"{cname}/{dname}/{tname}/{fname}", meta=large_meta)
    meta = client.get_field_metadata(f"{cname}/{dname}/{tname}/{fname}")
    assert meta is not None and len(meta['data']) == 1000
    client.delete_field(f"{cname}/{dname}/{tname}/{fname}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Invalid JSON/Corrupt Data ---
def test_invalid_json():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    fname = unique_name('field')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    # Try to create field with unserializable object
    try:
        import datetime
        client.create_field(f"{cname}/{dname}/{tname}/{fname}", meta={"type": "int", "dt": datetime.datetime.now()})
        assert False, "Should not allow unserializable meta"
    except Exception:
        pass
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Unicode and Special Characters in Names ---
def test_unicode_names():
    cname = unique_name('clu😀')
    dname = unique_name('db💾')
    tname = unique_name('tabℹ️')
    fname = unique_name('fiełd_测试')
    try:
        client.create_cluster(cname)
        client.create_database(f"{cname}/{dname}")
        client.create_table(f"{cname}/{dname}/{tname}")
        client.create_field(f"{cname}/{dname}/{tname}/{fname}", meta={"type": "int"})
        meta = client.get_field_metadata(f"{cname}/{dname}/{tname}/{fname}")
        assert meta is not None and meta['type'] == "int"
    finally:
        try: client.delete_field(f"{cname}/{dname}/{tname}/{fname}")
        except: pass
        try: client.delete_table(f"{cname}/{dname}/{tname}")
        except: pass
        try: client.delete_database(f"{cname}/{dname}")
        except: pass
        try: client.delete_cluster(cname)
        except: pass

# --- Edge to Nonexistent Node ---
def test_edge_to_nonexistent():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    f1 = unique_name('f1')
    f2 = unique_name('f2')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    client.create_field(f"{cname}/{dname}/{tname}/{f1}", meta={"type": "int"})
    try:
        client.add_edge(f"{cname}/{dname}/{tname}/{f1}", f"{cname}/{dname}/{tname}/{f2}")
        assert False, "Should not allow edge to nonexistent node"
    except Exception:
        pass
    client.delete_field(f"{cname}/{dname}/{tname}/{f1}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Delete Parent with Active Edges ---
def test_delete_parent_with_edges():
    cname = unique_name('cluster')
    d1 = unique_name('db1')
    d2 = unique_name('db2')
    t1 = unique_name('table1')
    t2 = unique_name('table2')
    f1 = unique_name('f1')
    f2 = unique_name('f2')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{d1}")
    client.create_database(f"{cname}/{d2}")
    client.create_table(f"{cname}/{d1}/{t1}")
    client.create_table(f"{cname}/{d2}/{t2}")
    client.create_field(f"{cname}/{d1}/{t1}/{f1}", meta={"type": "int"})
    client.create_field(f"{cname}/{d2}/{t2}/{f2}", meta={"type": "int"})
    client.add_edge(f"{cname}/{d1}/{t1}/{f1}", f"{cname}/{d2}/{t2}/{f2}")
    client.delete_table(f"{cname}/{d2}/{t2}")
    # Edge should be gone
    edges = client.get_edges(f"{cname}/{d1}/{t1}/{f1}")
    assert not any(f2 in e['path'] for e in edges)
    client.delete_field(f"{cname}/{d1}/{t1}/{f1}")
    client.delete_table(f"{cname}/{d1}/{t1}")
    client.delete_database(f"{cname}/{d1}")
    client.delete_database(f"{cname}/{d2}")
    client.delete_cluster(cname)

# --- Circular Edge Creation ---
def test_circular_edge():
    cname = unique_name('cluster')
    dname = unique_name('db')
    tname = unique_name('table')
    f1 = unique_name('f1')
    f2 = unique_name('f2')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    client.create_table(f"{cname}/{dname}/{tname}")
    client.create_field(f"{cname}/{dname}/{tname}/{f1}", meta={"type": "int"})
    client.create_field(f"{cname}/{dname}/{tname}/{f2}", meta={"type": "int"})
    client.add_edge(f"{cname}/{dname}/{tname}/{f1}", f"{cname}/{dname}/{tname}/{f2}")
    client.add_edge(f"{cname}/{dname}/{tname}/{f2}", f"{cname}/{dname}/{tname}/{f1}")
    # Both should be in each other's edge list
    edges1 = client.get_edges(f"{cname}/{dname}/{tname}/{f1}")
    edges2 = client.get_edges(f"{cname}/{dname}/{tname}/{f2}")
    assert any(f2 in e['path'] for e in edges1)
    assert any(f1 in e['path'] for e in edges2)
    client.remove_edge(f"{cname}/{dname}/{tname}/{f1}", f"{cname}/{dname}/{tname}/{f2}")
    client.remove_edge(f"{cname}/{dname}/{tname}/{f2}", f"{cname}/{dname}/{tname}/{f1}")
    client.delete_field(f"{cname}/{dname}/{tname}/{f1}")
    client.delete_field(f"{cname}/{dname}/{tname}/{f2}")
    client.delete_table(f"{cname}/{dname}/{tname}")
    client.delete_database(f"{cname}/{dname}")
    client.delete_cluster(cname)

# --- Bulk Deletion Under Load ---
def test_bulk_deletion_under_load():
    cname = unique_name('cluster')
    dname = unique_name('db')
    client.create_cluster(cname)
    client.create_database(f"{cname}/{dname}")
    num_tables = 5
    num_fields = 10
    tnames = [f"t{i}" for i in range(num_tables)]
    for tname in tnames:
        client.create_table(f"{cname}/{dname}/{tname}")
        for j in range(num_fields):
            client.create_field(f"{cname}/{dname}/{tname}/f{j}", meta={"type": "int"})
    # Delete cluster while fields/tables exist
    client.delete_cluster(cname)
    # Ensure all is gone
    try:
        client.list_database(cname)
        assert False, "Databases should not exist after cluster deletion"
    except Exception:
        pass

if __name__ == "__main__":
    test_create_and_delete_hierarchy()
    test_metadata_editing()
    test_edge_management()
    test_hierarchy_and_listing()
    test_corner_cases()
    test_connected_databases()
    test_deeply_nested_fields()
    test_complex_metadata()
    test_edge_cases_for_edges()
    test_bulk_deletion()
    test_invalid_paths()
    test_edge_directionality()
    test_advanced_filtering()
    test_concurrent_creation_and_deletion()
    test_rapid_edits()
    test_basic_load()
    test_simultaneous_creation()
    test_deletion_and_access_race()
    test_rapid_add_remove_edge()
    test_large_metadata()
    test_invalid_json()
    test_unicode_names()
    test_edge_to_nonexistent()
    test_delete_parent_with_edges()
    test_circular_edge()
    test_bulk_deletion_under_load()
    print("All PathClient tests passed.") 