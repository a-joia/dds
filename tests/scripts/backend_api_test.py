import requests
import time

BASE_URL = 'http://localhost:8000'

# Utility functions
def wait_for_server(url=BASE_URL, timeout=10):
    for _ in range(timeout * 2):
        try:
            requests.get(url + '/clusters/')
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError('Backend server not available')

wait_for_server()

# --- CLUSTER TESTS ---
def test_create_and_list_cluster():
    cname = 'testcluster'
    # Clean up if exists
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    # Create
    resp = requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    assert resp.status_code == 200, resp.text
    # Read
    get_resp = requests.get(f'{BASE_URL}/clusters/by-path/{cname}')
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()['name'] == cname
    # List
    clusters = requests.get(f'{BASE_URL}/clusters/').json()
    assert any(c['name'] == cname for c in clusters)
    # Clean up
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    clusters = requests.get(f'{BASE_URL}/clusters/').json()
    assert not any(c['name'] == cname for c in clusters)
    get_resp = requests.get(f'{BASE_URL}/clusters/by-path/{cname}')
    assert get_resp.status_code == 404

def test_update_cluster():
    cname = 'testcluster2'
    new_name = 'testcluster2_renamed'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{new_name}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    resp = requests.patch(f'{BASE_URL}/clusters/by-path/{cname}', json={'name': new_name})
    assert resp.status_code == 200, resp.text
    # Read updated
    get_resp = requests.get(f'{BASE_URL}/clusters/by-path/{new_name}')
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()['name'] == new_name
    # Old name should not exist
    get_old = requests.get(f'{BASE_URL}/clusters/by-path/{cname}')
    assert get_old.status_code == 404
    requests.delete(f'{BASE_URL}/clusters/by-path/{new_name}')

# --- DATABASE TESTS ---
def test_create_and_list_database():
    cname = 'testcluster3'
    dname = 'testdb'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    resp = requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    assert resp.status_code == 200, resp.text
    # Read
    get_resp = requests.get(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()['name'] == dname
    # Clean up
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    get_resp = requests.get(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    assert get_resp.status_code == 404
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

def test_update_database():
    cname = 'testcluster4'
    dname = 'testdb2'
    new_dname = 'testdb2_renamed'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{new_dname}')
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    resp = requests.patch(f'{BASE_URL}/databases/by-path/{cname}/{dname}', json={'name': new_dname})
    assert resp.status_code == 200, resp.text
    # Read updated
    get_resp = requests.get(f'{BASE_URL}/databases/by-path/{cname}/{new_dname}')
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()['name'] == new_dname
    # Old name should not exist
    get_old = requests.get(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    assert get_old.status_code == 404
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{new_dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

# --- TABLE TESTS ---
def test_create_and_list_table():
    cname = 'testcluster5'
    dname = 'testdb3'
    tname = 'testtable'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    resp = requests.post(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    assert resp.status_code == 200, resp.text
    # Read
    get_resp = requests.get(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()['name'] == tname
    # Clean up
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    get_resp = requests.get(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    assert get_resp.status_code == 404
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

def test_update_table():
    cname = 'testcluster6'
    dname = 'testdb4'
    tname = 'testtable2'
    new_tname = 'testtable2_renamed'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{new_tname}')
    requests.post(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    resp = requests.patch(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}', json={'name': new_tname})
    assert resp.status_code == 200, resp.text
    # Read updated
    get_resp = requests.get(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{new_tname}')
    assert get_resp.status_code == 200, get_resp.text
    assert get_resp.json()['name'] == new_tname
    # Old name should not exist
    get_old = requests.get(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    assert get_old.status_code == 404
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{new_tname}')
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

# --- FIELD TESTS ---
def test_create_and_list_field():
    cname = 'testcluster7'
    dname = 'testdb5'
    tname = 'testtable3'
    fname = 'testfield'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.post(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}')
    # Correct meta
    resp = requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}', json={"type": "string"})
    assert resp.status_code == 200, resp.text
    # Read
    get_resp = requests.get(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}')
    assert get_resp.status_code == 200, get_resp.text
    field_data = get_resp.json()
    assert field_data['name'] == fname
    assert field_data['meta']['type'] == 'string'
    # List fields
    fields = requests.get(f'{BASE_URL}/fields/by-table-path/{cname}/{dname}/{tname}').json().get('paths', [])
    assert any(fname in f for f in fields)
    # Clean up
    requests.delete(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}')
    get_resp = requests.get(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}')
    assert get_resp.status_code == 404
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

def test_create_field_missing_meta():
    cname = 'testcluster7b'
    dname = 'testdb5b'
    tname = 'testtable3b'
    fname = 'testfieldb'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.post(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    # No meta
    resp = requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}', json=None)
    assert resp.status_code == 422
    assert 'Field required' in resp.text
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

def test_create_field_meta_not_dict():
    cname = 'testcluster7c'
    dname = 'testdb5c'
    tname = 'testtable3c'
    fname = 'testfieldc'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.post(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    # Meta not a dict
    resp = requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}', json=[1,2,3])
    assert resp.status_code == 422
    assert 'Input should be a valid dictionary' in resp.text
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

def test_create_field_missing_type():
    cname = 'testcluster7d'
    dname = 'testdb5d'
    tname = 'testtable3d'
    fname = 'testfieldd'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.post(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    # Meta missing 'type'
    resp = requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}', json={"description": "desc"})
    assert resp.status_code == 400
    assert "meta must contain a 'type' key" in resp.text
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

def test_create_field_duplicate():
    cname = 'testcluster7e'
    dname = 'testdb5e'
    tname = 'testtable3e'
    fname = 'testfielde'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.post(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    resp1 = requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}', json={"type": "string"})
    assert resp1.status_code == 200
    resp2 = requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}', json={"type": "string"})
    assert resp2.status_code == 400
    assert 'Field already exists at this path' in resp2.text
    requests.delete(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}')
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

def test_update_field_meta():
    import uuid
    cname = 'testcluster8'
    dname = 'testdb6'
    tname = 'testtable4'
    fname = f'testfield2_{uuid.uuid4().hex[:8]}'  # Unique field name
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.post(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}')
    # Create field with required meta
    requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}', json={"type": "string"})
    resp = requests.patch(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}/meta', json={"type": "int", "description": "desc"})
    print('PATCH status:', resp.status_code, 'PATCH response:', resp.text)
    assert resp.status_code == 200, resp.text
    print('PATCH response JSON:', resp.json())  # DEBUG PRINT
    # Verify meta update before cleanup
    get_resp = requests.get(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}/meta')
    print('GET /meta status:', get_resp.status_code, 'GET /meta response:', get_resp.text)
    meta = get_resp.json()
    assert meta['type'] == 'int' and meta['description'] == 'desc'
    # Clean up
    requests.delete(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}')
    get_resp = requests.get(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname}')
    assert get_resp.status_code == 404
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

# --- EQUIVALENCE TESTS ---
def test_equivalence():
    cname = 'testcluster9'
    dname = 'testdb7'
    tname = 'testtable5'
    fname1 = 'field1'
    fname2 = 'field2'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.post(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    # Create both fields with required meta
    requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname1}', json={"type": "string"})
    requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname2}', json={"type": "string"})
    # Add equivalence
    resp = requests.post(f'{BASE_URL}/equivalence/?from_path={cname}/{dname}/{tname}/{fname1}&to_path={cname}/{dname}/{tname}/{fname2}')
    assert resp.status_code == 200, resp.text
    # List equivalents
    equivalents = requests.get(f'{BASE_URL}/fields/{cname}/{dname}/{tname}/{fname1}/equivalence/').json()['equivalents']
    assert any(eq['path'].endswith(fname2) for eq in equivalents)
    # Remove equivalence
    resp = requests.delete(f'{BASE_URL}/equivalence/?from_path={cname}/{dname}/{tname}/{fname1}&to_path={cname}/{dname}/{tname}/{fname2}')
    assert resp.status_code == 200, resp.text
    # Clean up
    requests.delete(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname1}')
    requests.delete(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname2}')
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

# --- POSSIBLY-EQUIVALENCE TESTS ---
def test_possibly_equivalence():
    cname = 'testcluster10'
    dname = 'testdb8'
    tname = 'testtable6'
    fname1 = 'field1'
    fname2 = 'field2'
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.post(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    # Create both fields with required meta
    requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname1}', json={"type": "string"})
    requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname2}', json={"type": "string"})
    # Add possibly-equivalence
    resp = requests.post(f'{BASE_URL}/possibly-equivalence/?from_path={cname}/{dname}/{tname}/{fname1}&to_path={cname}/{dname}/{tname}/{fname2}')
    assert resp.status_code == 200, resp.text
    # List possibly-equivalents
    equivalents = requests.get(f'{BASE_URL}/fields/{cname}/{dname}/{tname}/{fname1}/possibly-equivalence/').json()['equivalents']
    assert any(eq['path'].endswith(fname2) for eq in equivalents)
    # Remove possibly-equivalence
    resp = requests.delete(f'{BASE_URL}/possibly-equivalence/?from_path={cname}/{dname}/{tname}/{fname1}&to_path={cname}/{dname}/{tname}/{fname2}')
    assert resp.status_code == 200, resp.text
    # Clean up
    requests.delete(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname1}')
    requests.delete(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname2}')
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}') 

def test_delete_field_removes_edges():
    import uuid
    cname = 'testcluster_edge'
    dname = 'testdb_edge'
    tname = 'testtable_edge'
    fname1 = f'fieldA_{uuid.uuid4().hex[:8]}'
    fname2 = f'fieldB_{uuid.uuid4().hex[:8]}'
    # Clean up in case of previous runs
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')
    requests.post(f'{BASE_URL}/clusters/', json={'name': cname})
    requests.post(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.post(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    # Create two fields
    resp1 = requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname1}', json={"type": "string"})
    resp2 = requests.post(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname2}', json={"type": "string"})
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    # Get field IDs
    field1 = requests.get(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname1}').json()
    field2 = requests.get(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname2}').json()
    id1 = field1['id']
    id2 = field2['id']
    # Create an edge between them
    edge_resp = requests.post(f'{BASE_URL}/edges/', json={"from_field_id": id1, "to_field_id": id2, "type": "custom"})
    assert edge_resp.status_code == 200, edge_resp.text
    edge_id = edge_resp.json()['id']
    # Check both fields have the edge
    edges1 = requests.get(f'{BASE_URL}/fields/{id1}/edges/').json()
    edges2 = requests.get(f'{BASE_URL}/fields/{id2}/edges/').json()
    assert any(e['id'] == edge_id for e in edges1)
    assert any(e['id'] == edge_id for e in edges2)
    # Delete field1
    del_resp = requests.delete(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname1}')
    assert del_resp.status_code == 200 or del_resp.status_code == 204
    # Edge should be gone from field2's edge list
    edges2_after = requests.get(f'{BASE_URL}/fields/{id2}/edges/').json()
    assert not any(e['id'] == edge_id for e in edges2_after), f"Edge {edge_id} should be deleted when field1 is deleted"
    # Clean up
    requests.delete(f'{BASE_URL}/fields/by-path/{cname}/{dname}/{tname}/{fname2}')
    requests.delete(f'{BASE_URL}/tables/by-path/{cname}/{dname}/{tname}')
    requests.delete(f'{BASE_URL}/databases/by-path/{cname}/{dname}')
    requests.delete(f'{BASE_URL}/clusters/by-path/{cname}')

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name in globals() and callable(globals()[test_name]):
            print(f"Running {test_name}...")
            globals()[test_name]()
        else:
            print(f"Test {test_name} not found.")
    else:
        print("No test name provided. Available tests:")
        for name in globals():
            if name.startswith('test_') and callable(globals()[name]):
                print(name) 