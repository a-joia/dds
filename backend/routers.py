from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from . import crud, schemas, deps
from typing import List, Optional, Dict, Any
from .crud import get_field_id_by_path, get_field_path_by_id, get_cluster_id_by_path, get_database_id_by_path, get_table_id_by_path

router = APIRouter()

# Cluster endpoints
@router.post("/clusters/", response_model=schemas.ClusterRead)
def create_cluster(cluster: schemas.ClusterCreate, db: Session = Depends(deps.get_db)):
    return crud.create_cluster(db, cluster)

@router.get("/clusters/", response_model=List[schemas.ClusterRead])
def read_clusters(db: Session = Depends(deps.get_db)):
    return crud.get_clusters(db)

# Database endpoints
@router.post("/clusters/{cluster_id}/databases/", response_model=schemas.DatabaseRead)
def create_database(cluster_id: int, database: schemas.DatabaseCreate, db: Session = Depends(deps.get_db)):
    return crud.create_database(db, cluster_id, database)

@router.get("/clusters/{cluster_id}/databases/", response_model=List[schemas.DatabaseRead])
def read_databases(cluster_id: int, db: Session = Depends(deps.get_db)):
    return crud.get_databases(db, cluster_id)

# Table endpoints
@router.post("/databases/{database_id}/tables/", response_model=schemas.TableRead)
def create_table(database_id: int, table: schemas.TableCreate, db: Session = Depends(deps.get_db)):
    return crud.create_table(db, database_id, table)

@router.get("/databases/{database_id}/tables/", response_model=List[schemas.TableRead])
def read_tables(database_id: int, db: Session = Depends(deps.get_db)):
    return crud.get_tables(db, database_id)

# Field endpoints
@router.post("/tables/{table_id}/fields/", response_model=schemas.FieldRead)
def create_field(table_id: int, field: schemas.FieldCreate, db: Session = Depends(deps.get_db)):
    return crud.create_field(db, table_id, field)

@router.get("/tables/{table_id}/fields/", response_model=List[schemas.FieldRead])
def read_fields(table_id: int, db: Session = Depends(deps.get_db)):
    return crud.get_fields(db, table_id)

# Edge endpoints
@router.post("/edges/", response_model=schemas.EdgeRead)
def create_edge(edge: schemas.EdgeCreate, db: Session = Depends(deps.get_db)):
    return crud.create_edge(db, edge)

@router.get("/fields/{field_id}/edges/", response_model=List[schemas.EdgeRead])
def read_edges(field_id: int, db: Session = Depends(deps.get_db)):
    return crud.get_edges(db, field_id)

@router.delete("/edges/{edge_id}")
def delete_edge(edge_id: int, db: Session = Depends(deps.get_db)):
    success = crud.delete_edge(db, edge_id)
    if not success:
        raise HTTPException(status_code=404, detail="Edge not found")
    return {"success": True}

from fastapi import Body

@router.patch("/fields/{field_id}/meta", response_model=schemas.FieldRead)
def update_field_meta(field_id: int, meta: Dict[str, Any] = Body(...), db: Session = Depends(deps.get_db)):
    field = db.query(crud.models.Field).filter(crud.models.Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    if not isinstance(meta, dict):
        raise HTTPException(status_code=400, detail="meta must be a dictionary")
    setattr(field, 'meta', meta)
    db.commit()
    db.refresh(field)
    return field

@router.patch("/clusters/by-path/{cluster_path}", response_model=schemas.ClusterRead)
def update_cluster_by_path(cluster_path: str, data: dict = Body(...), db: Session = Depends(deps.get_db)):
    cluster_id = get_cluster_id_by_path(db, cluster_path)
    if cluster_id is None:
        raise HTTPException(status_code=404, detail="Cluster not found for path")
    cluster = db.query(crud.models.Cluster).filter(crud.models.Cluster.id == cluster_id).first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    if 'name' in data:
        cluster.name = data['name']
    db.commit()
    db.refresh(cluster)
    return cluster

@router.patch("/databases/by-path/{cluster}/{database}", response_model=schemas.DatabaseRead)
def update_database_by_path(cluster: str, database: str, data: dict = Body(...), db: Session = Depends(deps.get_db)):
    db_id = get_database_id_by_path(db, cluster, database)
    if db_id is None:
        raise HTTPException(status_code=404, detail="Database not found for path")
    db_obj = db.query(crud.models.Database).filter(crud.models.Database.id == db_id).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Database not found")
    if 'name' in data:
        db_obj.name = data['name']
    db.commit()
    db.refresh(db_obj)
    return db_obj

@router.patch("/tables/by-path/{cluster}/{database}/{table}", response_model=schemas.TableRead)
def update_table_by_path(cluster: str, database: str, table: str, data: dict = Body(...), db: Session = Depends(deps.get_db)):
    table_id = get_table_id_by_path(db, cluster, database, table)
    if table_id is None:
        raise HTTPException(status_code=404, detail="Table not found for path")
    table_obj = db.query(crud.models.Table).filter(crud.models.Table.id == table_id).first()
    if not table_obj:
        raise HTTPException(status_code=404, detail="Table not found")
    if 'name' in data:
        table_obj.name = data['name']
    db.commit()
    db.refresh(table_obj)
    return table_obj

@router.patch("/fields/by-path/{field_path:path}/meta", response_model=schemas.FieldRead)
def update_field_meta_by_path(field_path: str, meta: dict = Body(...), db: Session = Depends(deps.get_db)):
    parts = field_path.split('/')
    if len(parts) < 4:
        raise HTTPException(status_code=400, detail="Field path must include at least cluster/database/table/field")
    field_id = get_field_id_by_path(db, *parts)
    if field_id is None:
        raise HTTPException(status_code=404, detail="Field not found for path")
    field = db.query(crud.models.Field).filter(crud.models.Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    if not isinstance(meta, dict):
        raise HTTPException(status_code=400, detail="meta must be a dictionary")
    setattr(field, 'meta', meta)
    db.commit()
    db.refresh(field)
    return field

@router.get("/fields/by-path/{field_path:path}/meta")
def get_field_meta_by_path(field_path: str, db: Session = Depends(deps.get_db)):
    parts = field_path.split('/')
    field_id = get_field_id_by_path(db, *parts)
    if field_id is None:
        raise HTTPException(status_code=404, detail="Field not found for path")
    field = db.query(crud.models.Field).filter(crud.models.Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    return {"meta": field.meta}

@router.post("/equivalence/")
def add_equivalence_edge(
    from_path: str = Query(..., description="Path to source field, e.g. cluster/db/table/field[/subfield...]"),
    to_path: str = Query(..., description="Path to target field, e.g. cluster/db/table/field[/subfield...]") ,
    db: Session = Depends(deps.get_db)):
    from_parts = from_path.split('/')
    to_parts = to_path.split('/')
    from_id = get_field_id_by_path(db, *from_parts)
    to_id = get_field_id_by_path(db, *to_parts)
    if from_id is None or to_id is None:
        raise HTTPException(status_code=404, detail="Field not found for one or both paths")
    edge = crud.create_equivalence_edge(db, from_id, to_id)
    return {"success": True, "edge_id": edge.id}

@router.delete("/equivalence/")
def remove_equivalence_edge(
    from_path: str = Query(..., description="Path to source field, e.g. cluster/db/table/field[/subfield...]"),
    to_path: str = Query(..., description="Path to target field, e.g. cluster/db/table/field[/subfield...]") ,
    db: Session = Depends(deps.get_db)):
    from_parts = from_path.split('/')
    to_parts = to_path.split('/')
    from_id = get_field_id_by_path(db, *from_parts)
    to_id = get_field_id_by_path(db, *to_parts)
    if from_id is None or to_id is None:
        raise HTTPException(status_code=404, detail="Field not found for one or both paths")
    success = crud.delete_equivalence_edge(db, from_id, to_id)
    if not success:
        raise HTTPException(status_code=404, detail="Equivalence edge not found")
    return {"success": True}

@router.get("/fields/{field_path:path}/equivalence/")
def get_equivalent_fields(field_path: str, db: Session = Depends(deps.get_db)):
    parts = field_path.split('/')
    if len(parts) < 3:
        raise HTTPException(status_code=400, detail="Field path must include at least cluster/database/table/field")
    field_id = get_field_id_by_path(db, *parts)
    if field_id is None:
        raise HTTPException(status_code=404, detail="Field not found for path")
    equivalents = crud.get_equivalent_fields(db, field_id)
    equivalent_nodes = [
        {"id": eq_id, "path": get_field_path_by_id(db, eq_id)}
        for eq_id in equivalents
    ]
    return {"equivalents": equivalent_nodes}

@router.post("/possibly-equivalence/")
def add_possibly_equivalence_edge(
    from_path: str = Query(..., description="Path to source field, e.g. cluster/db/table/field[/subfield...]") ,
    to_path: str = Query(..., description="Path to target field, e.g. cluster/db/table/field[/subfield...]") ,
    db: Session = Depends(deps.get_db)):
    from_parts = from_path.split('/')
    to_parts = to_path.split('/')
    from_id = get_field_id_by_path(db, *from_parts)
    to_id = get_field_id_by_path(db, *to_parts)
    if from_id is None or to_id is None:
        raise HTTPException(status_code=404, detail="Field not found for one or both paths")
    edge = crud.create_possibly_equivalence_edge(db, from_id, to_id)
    return {"success": True, "edge_id": edge.id}

@router.delete("/possibly-equivalence/")
def remove_possibly_equivalence_edge(
    from_path: str = Query(..., description="Path to source field, e.g. cluster/db/table/field[/subfield...]") ,
    to_path: str = Query(..., description="Path to target field, e.g. cluster/db/table/field[/subfield...]") ,
    db: Session = Depends(deps.get_db)):
    from_parts = from_path.split('/')
    to_parts = to_path.split('/')
    from_id = get_field_id_by_path(db, *from_parts)
    to_id = get_field_id_by_path(db, *to_parts)
    if from_id is None or to_id is None:
        raise HTTPException(status_code=404, detail="Field not found for one or both paths")
    success = crud.delete_possibly_equivalence_edge(db, from_id, to_id)
    if not success:
        raise HTTPException(status_code=404, detail="Possibly equivalence edge not found")
    return {"success": True}

@router.get("/fields/{field_path:path}/possibly-equivalence/")
def get_possibly_equivalent_fields(field_path: str, db: Session = Depends(deps.get_db)):
    parts = field_path.split('/')
    if len(parts) < 3:
        raise HTTPException(status_code=400, detail="Field path must include at least cluster/database/table/field")
    field_id = get_field_id_by_path(db, *parts)
    if field_id is None:
        raise HTTPException(status_code=404, detail="Field not found for path")
    equivalents = crud.get_possibly_equivalent_fields(db, field_id)
    equivalent_nodes = [
        {"id": eq_id, "path": get_field_path_by_id(db, eq_id)}
        for eq_id in equivalents
    ]
    return {"equivalents": equivalent_nodes}

@router.post("/fields/by-path/{field_path:path}")
def create_field_by_path(field_path: str, data: dict = Body(...), db: Session = Depends(deps.get_db)):
    # field_path: cluster/database/table/field1/field2/...
    parts = field_path.split('/')
    if len(parts) < 3:
        raise HTTPException(status_code=400, detail="Path must include at least cluster/database/table/field")
    cluster, database, table, *field_names = parts
    # Get table id
    table_id = get_table_id_by_path(db, cluster, database, table)
    if table_id is None:
        raise HTTPException(status_code=404, detail="Table not found for path")
    parent_id = None
    for name in field_names[:-1]:
        parent_id = get_field_id_by_path(db, cluster, database, table, *(field_names[:field_names.index(name)+1]))
        if parent_id is None:
            raise HTTPException(status_code=404, detail=f"Parent field '{name}' not found")
    # Create the field
    from . import schemas
    field_create = schemas.FieldCreate(name=field_names[-1], parent_id=parent_id, meta=data)
    field = db.query(crud.models.Field).filter(
        crud.models.Field.name == field_names[-1],
        crud.models.Field.table_id == table_id,
        crud.models.Field.parent_id == parent_id
    ).first()
    if field:
        raise HTTPException(status_code=400, detail="Field already exists at this path")
    new_field = crud.create_field(db, table_id, field_create)
    return new_field

@router.delete("/fields/{field_id}")
def delete_field_endpoint(field_id: int, db: Session = Depends(deps.get_db)):
    from .crud import delete_field
    delete_field(db, field_id)
    return {"success": True}

@router.delete("/tables/{table_id}")
def delete_table_endpoint(table_id: int, db: Session = Depends(deps.get_db)):
    from .crud import delete_table
    delete_table(db, table_id)
    return {"success": True}

@router.delete("/databases/{database_id}")
def delete_database_endpoint(database_id: int, db: Session = Depends(deps.get_db)):
    from .crud import delete_database
    delete_database(db, database_id)
    return {"success": True}

@router.delete("/clusters/{cluster_id}")
def delete_cluster_endpoint(cluster_id: int, db: Session = Depends(deps.get_db)):
    from .crud import delete_cluster
    delete_cluster(db, cluster_id)
    return {"success": True}

@router.get("/tables/{table_id}/graph/")
def get_table_graph(table_id: int, db: Session = Depends(deps.get_db)):
    """Get graph data for a table including all fields and their edges."""
    return crud.get_table_graph_data(db, table_id)

@router.get("/fields/by-table-path/{cluster}/{database}/{table}")
def list_fields_by_table_path(cluster: str, database: str, table: str, db: Session = Depends(deps.get_db)):
    """
    List all fields and subfields under the specified table, returning their full paths.
    """
    paths = crud.list_field_paths_by_table_path(db, cluster, database, table)
    if not paths:
        raise HTTPException(status_code=404, detail="Table not found or no fields present")
    return {"paths": paths}

@router.get("/fields/by-table-path/{cluster}/{database}/{table}/empty-description")
def list_fields_with_empty_description_by_table_path(cluster: str, database: str, table: str, db: Session = Depends(deps.get_db)):
    """
    List all fields and subfields under the specified table where the description is empty or missing.
    """
    paths = crud.list_field_paths_with_empty_description_by_table_path(db, cluster, database, table)
    if not paths:
        return {"paths": []}
    return {"paths": paths}

@router.get("/fields/by-table-path/{cluster}/{database}/{table}/missing-type")
def list_fields_without_type_by_table_path(cluster: str, database: str, table: str, db: Session = Depends(deps.get_db)):
    """
    List all fields and subfields under the specified table where the 'type' in meta is missing or empty.
    """
    paths = crud.list_field_paths_without_type_by_table_path(db, cluster, database, table)
    if not paths:
        return {"paths": []}
    return {"paths": paths}

@router.get("/fields/by-path/{field_path:path}/info")
def get_field_info_by_path(field_path: str, db: Session = Depends(deps.get_db)):
    """
    Return all information about the field or subfield node given its path.
    """
    parts = field_path.split('/')
    if len(parts) < 4:
        raise HTTPException(status_code=400, detail="Field path must include at least cluster/database/table/field")
    field_id = get_field_id_by_path(db, *parts)
    if field_id is None:
        raise HTTPException(status_code=404, detail="Field not found for path")
    field = db.query(crud.models.Field).filter(crud.models.Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    # Convert SQLAlchemy model to dict
    info = {
        "id": field.id,
        "name": field.name,
        "meta": field.meta,
        "parent_id": field.parent_id,
        "table_id": field.table_id,
    }
    return info 