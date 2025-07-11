from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from sqlalchemy import and_, or_

def create_cluster(db: Session, cluster: schemas.ClusterCreate) -> models.Cluster:
    existing = db.query(models.Cluster).filter(models.Cluster.name == cluster.name).first()
    if existing is not None:
        return existing
    db_cluster = models.Cluster(name=cluster.name)
    db.add(db_cluster)
    db.commit()
    db.refresh(db_cluster)
    return db_cluster

def get_clusters(db: Session) -> List[models.Cluster]:
    from sqlalchemy.orm import joinedload
    return db.query(models.Cluster).options(
        joinedload(models.Cluster.databases).joinedload(models.Database.tables)
    ).all()

def create_database(db: Session, cluster_id: int, database: schemas.DatabaseCreate) -> models.Database:
    existing = db.query(models.Database).filter(models.Database.name == database.name, models.Database.cluster_id == cluster_id).first()
    if existing is not None:
        return existing
    db_database = models.Database(name=database.name, cluster_id=cluster_id)
    db.add(db_database)
    db.commit()
    db.refresh(db_database)
    return db_database

def get_databases(db: Session, cluster_id: int) -> List[models.Database]:
    from sqlalchemy.orm import joinedload
    return db.query(models.Database).options(
        joinedload(models.Database.tables)
    ).filter(models.Database.cluster_id == cluster_id).all()

def create_table(db: Session, database_id: int, table: schemas.TableCreate) -> models.Table:
    existing = db.query(models.Table).filter(models.Table.name == table.name, models.Table.database_id == database_id).first()
    if existing is not None:
        return existing
    db_table = models.Table(name=table.name, database_id=database_id)
    db.add(db_table)
    db.commit()
    db.refresh(db_table)
    return db_table

def get_tables(db: Session, database_id: int) -> List[models.Table]:
    from sqlalchemy.orm import joinedload
    return db.query(models.Table).options(
        joinedload(models.Table.fields)
    ).filter(models.Table.database_id == database_id).all()

def create_field(db: Session, table_id: int, field: schemas.FieldCreate) -> models.Field:
    existing = db.query(models.Field).filter(
        models.Field.name == field.name,
        models.Field.table_id == table_id,
        models.Field.parent_id == field.parent_id
    ).first()
    if existing is not None:
        return existing
    db_field = models.Field(name=field.name, table_id=table_id, parent_id=field.parent_id, meta=field.meta)
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    return db_field

def get_fields(db: Session, table_id: int, parent_id: Optional[int] = None) -> List[models.Field]:
    from sqlalchemy.orm import joinedload
    return db.query(models.Field).options(joinedload(models.Field.subfields)).filter(models.Field.table_id == table_id, models.Field.parent_id == parent_id).all()

def create_edge(db: Session, edge: schemas.EdgeCreate) -> models.Edge:
    db_edge = models.Edge(from_field_id=edge.from_field_id, to_field_id=edge.to_field_id, type=edge.type)
    db.add(db_edge)
    db.commit()
    db.refresh(db_edge)
    return db_edge

def get_edges(db: Session, field_id: int) -> List[models.Edge]:
    return db.query(models.Edge).filter((models.Edge.from_field_id == field_id) | (models.Edge.to_field_id == field_id)).all()

def delete_edge(db: Session, edge_id: int) -> bool:
    edge = db.query(models.Edge).filter(models.Edge.id == edge_id).first()
    if edge is None:
        return False
    db.delete(edge)
    db.commit()
    return True

def create_equivalence_edge(db: Session, from_field_id: int, to_field_id: int) -> models.Edge:
    # Prevent duplicate equivalence edges (bidirectional)
    existing = db.query(models.Edge).filter(
        or_(
            and_(models.Edge.from_field_id == from_field_id, models.Edge.to_field_id == to_field_id),
            and_(models.Edge.from_field_id == to_field_id, models.Edge.to_field_id == from_field_id)
        ),
        models.Edge.type == "equivalence"
    ).first()
    if existing is not None:
        return existing
    db_edge = models.Edge(from_field_id=from_field_id, to_field_id=to_field_id, type="equivalence")
    db.add(db_edge)
    db.commit()
    db.refresh(db_edge)
    return db_edge


def delete_equivalence_edge(db: Session, from_field_id: int, to_field_id: int) -> bool:
    edge = db.query(models.Edge).filter(
        or_(
            and_(models.Edge.from_field_id == from_field_id, models.Edge.to_field_id == to_field_id),
            and_(models.Edge.from_field_id == to_field_id, models.Edge.to_field_id == from_field_id)
        ),
        models.Edge.type == "equivalence"
    ).first()
    if edge is None:
        return False
    db.delete(edge)
    db.commit()
    return True


def get_equivalent_fields(db: Session, field_id: int) -> list:
    # Find all fields equivalent to the given field_id
    edges = db.query(models.Edge).filter(
        or_(models.Edge.from_field_id == field_id, models.Edge.to_field_id == field_id),
        models.Edge.type == "equivalence"
    ).all()
    equivalents = []
    for edge in edges:
        if edge.from_field_id == field_id:
            equivalents.append(edge.to_field_id)
        else:
            equivalents.append(edge.from_field_id)
    return equivalents

def create_possibly_equivalence_edge(db: Session, from_field_id: int, to_field_id: int) -> models.Edge:
    # Prevent duplicate possibly equivalence edges (bidirectional)
    existing = db.query(models.Edge).filter(
        or_(
            and_(models.Edge.from_field_id == from_field_id, models.Edge.to_field_id == to_field_id),
            and_(models.Edge.from_field_id == to_field_id, models.Edge.to_field_id == from_field_id)
        ),
        models.Edge.type == "possibly_equivalence"
    ).first()
    if existing is not None:
        return existing
    db_edge = models.Edge(from_field_id=from_field_id, to_field_id=to_field_id, type="possibly_equivalence")
    db.add(db_edge)
    db.commit()
    db.refresh(db_edge)
    return db_edge

def delete_possibly_equivalence_edge(db: Session, from_field_id: int, to_field_id: int) -> bool:
    edge = db.query(models.Edge).filter(
        or_(
            and_(models.Edge.from_field_id == from_field_id, models.Edge.to_field_id == to_field_id),
            and_(models.Edge.from_field_id == to_field_id, models.Edge.to_field_id == from_field_id)
        ),
        models.Edge.type == "possibly_equivalence"
    ).first()
    if edge is None:
        return False
    db.delete(edge)
    db.commit()
    return True

def get_possibly_equivalent_fields(db: Session, field_id: int) -> list:
    # Find all fields possibly equivalent to the given field_id
    edges = db.query(models.Edge).filter(
        or_(models.Edge.from_field_id == field_id, models.Edge.to_field_id == field_id),
        models.Edge.type == "possibly_equivalence"
    ).all()
    equivalents = []
    for edge in edges:
        if edge.from_field_id == field_id:
            equivalents.append(edge.to_field_id)
        else:
            equivalents.append(edge.from_field_id)
    return equivalents

def get_field_id_by_path(db: Session, cluster: str, database: str, table: str, *field_path: str) -> Optional[int]:
    # Use a single query with joins to resolve cluster, database, and table
    table_obj = db.query(models.Table).join(
        models.Database, models.Table.database_id == models.Database.id
    ).join(
        models.Cluster, models.Database.cluster_id == models.Cluster.id
    ).filter(
        models.Cluster.name == cluster,
        models.Database.name == database,
        models.Table.name == table
    ).first()
    
    if table_obj is None:
        return None
    
    # Walk through field/subfield path
    parent_id = None
    last_field_obj = None
    for name in field_path:
        field_obj = db.query(models.Field).filter(
            models.Field.name == name, 
            models.Field.table_id == table_obj.id, 
            models.Field.parent_id == parent_id
        ).first()
        if not field_obj:
            return None
        parent_id = field_obj.id
        last_field_obj = field_obj
    
    return last_field_obj.id if last_field_obj else None

def get_field_path_by_id(db: Session, field_id: int) -> str:
    # Walk up the parent chain to build the path
    field = db.query(models.Field).filter(models.Field.id == field_id).first()
    if not field:
        return ''
    names = []
    current = field
    while current:
        names.append(current.name)
        if current.parent_id is not None:
            current = db.query(models.Field).filter(models.Field.id == current.parent_id).first()
        else:
            break
    names = list(reversed(names))
    # Get table, database, cluster
    table = db.query(models.Table).filter(models.Table.id == getattr(field, 'table_id', None)).first()
    if table is None:
        return '/'.join(names)
    database = db.query(models.Database).filter(models.Database.id == getattr(table, 'database_id', None)).first() if getattr(table, 'database_id', None) is not None else None
    if database is None:
        return '/'.join([str(getattr(table, 'name', ''))] + names)
    cluster = db.query(models.Cluster).filter(models.Cluster.id == getattr(database, 'cluster_id', None)).first() if getattr(database, 'cluster_id', None) is not None else None
    if cluster is None:
        return '/'.join([str(getattr(database, 'name', '')), str(getattr(table, 'name', ''))] + names)
    return '/'.join([str(getattr(cluster, 'name', '')), str(getattr(database, 'name', '')), str(getattr(table, 'name', ''))] + names)

def get_cluster_id_by_path(db: Session, cluster: str) -> Optional[int]:
    cluster_obj = db.query(models.Cluster).filter(models.Cluster.name == cluster).first()
    return getattr(cluster_obj, 'id', None) if cluster_obj else None

def get_database_id_by_path(db: Session, cluster: str, database: str) -> Optional[int]:
    cluster_obj = db.query(models.Cluster).filter(models.Cluster.name == cluster).first()
    if not cluster_obj:
        return None
    db_obj = db.query(models.Database).filter(models.Database.name == database, models.Database.cluster_id == getattr(cluster_obj, 'id', None)).first()
    return getattr(db_obj, 'id', None) if db_obj else None

def get_table_id_by_path(db: Session, cluster: str, database: str, table: str) -> Optional[int]:
    cluster_obj = db.query(models.Cluster).filter(models.Cluster.name == cluster).first()
    if not cluster_obj:
        return None
    db_obj = db.query(models.Database).filter(models.Database.name == database, models.Database.cluster_id == getattr(cluster_obj, 'id', None)).first()
    if not db_obj:
        return None
    table_obj = db.query(models.Table).filter(models.Table.name == table, models.Table.database_id == getattr(db_obj, 'id', None)).first()
    return getattr(table_obj, 'id', None) if table_obj else None

def delete_field(db: Session, field_id: int):
    # Recursively delete subfields
    subfields = db.query(models.Field).filter(models.Field.parent_id == field_id).all()
    for sub in subfields:
        delete_field(db, sub.id)
    # Delete all edges (equivalence and possibly equivalence) involving this field
    db.query(models.Edge).filter((models.Edge.from_field_id == field_id) | (models.Edge.to_field_id == field_id)).delete(synchronize_session=False)
    # Delete the field itself
    field = db.query(models.Field).filter(models.Field.id == field_id).first()
    if field:
        db.delete(field)
    db.commit()

def delete_table(db: Session, table_id: int):
    # Delete all fields in the table (and their subfields/edges)
    fields = db.query(models.Field).filter(models.Field.table_id == table_id).all()
    for field in fields:
        delete_field(db, field.id)
    # Delete the table itself
    table = db.query(models.Table).filter(models.Table.id == table_id).first()
    if table:
        db.delete(table)
    db.commit()

def delete_database(db: Session, database_id: int):
    # Delete all tables in the database (and their fields/edges)
    tables = db.query(models.Table).filter(models.Table.database_id == database_id).all()
    for table in tables:
        delete_table(db, table.id)
    # Delete the database itself
    database = db.query(models.Database).filter(models.Database.id == database_id).first()
    if database:
        db.delete(database)
    db.commit()

def delete_cluster(db: Session, cluster_id: int):
    # Delete all databases in the cluster (and their tables/fields/edges)
    databases = db.query(models.Database).filter(models.Database.cluster_id == cluster_id).all()
    for database in databases:
        delete_database(db, database.id)
    # Delete the cluster itself
    cluster = db.query(models.Cluster).filter(models.Cluster.id == cluster_id).first()
    if cluster:
        db.delete(cluster)
    db.commit() 

def get_table_graph_data(db: Session, table_id: int) -> dict:
    """
    Get graph data for a table including all fields and their edges.
    Returns a dictionary with nodes and edges for graph visualization.
    """
    from sqlalchemy.orm import joinedload
    
    # Get the table with all fields and subfields
    table = db.query(models.Table).options(
        joinedload(models.Table.fields).joinedload(models.Field.subfields)
    ).filter(models.Table.id == table_id).first()
    
    if not table:
        return {"nodes": [], "edges": []}
    
    # Get cluster and database info
    database = db.query(models.Database).filter(models.Database.id == table.database_id).first()
    if not database:
        return {"nodes": [], "edges": []}
    
    cluster = db.query(models.Cluster).filter(models.Cluster.id == database.cluster_id).first()
    if not cluster:
        return {"nodes": [], "edges": []}
    
    # Create the cluster.database.table node
    table_node_id = -1  # Use negative ID to distinguish from field IDs
    table_node_name = f"{cluster.name}.{database.name}.{table.name}"
    table_node_path = f"{cluster.name}/{database.name}/{table.name}"
    
    # Get all fields for this table (including subfields)
    all_fields = db.query(models.Field).filter(models.Field.table_id == table_id).all()
    field_ids = [f.id for f in all_fields]
    
    # Get all edges that involve any field in this table
    edges = db.query(models.Edge).options(
        joinedload(models.Edge.from_field),
        joinedload(models.Edge.to_field)
    ).filter(
        or_(
            models.Edge.from_field_id.in_(field_ids),
            models.Edge.to_field_id.in_(field_ids)
        )
    ).all()
    
    # Build nodes list - start with the table node
    nodes = [{
        "id": table_node_id,
        "name": table_node_name,
        "path": table_node_path,
        "parent_id": None,
        "meta": {"type": "table", "description": f"Table {table.name} in database {database.name} of cluster {cluster.name}"}
    }]
    
    # Add field nodes
    for field in all_fields:
        # Get the full path for the field
        path = get_field_path_by_id(db, field.id)
        nodes.append({
            "id": field.id,
            "name": field.name,
            "path": path,
            "parent_id": field.parent_id if field.parent_id else table_node_id,  # Connect root fields to table node
            "meta": field.meta or {}
        })
    
    # Build edges list
    edge_list = []
    
    # Add edges from table node to root fields (fields without parent)
    for field in all_fields:
        if field.parent_id is None:
            edge_list.append({
                "id": f"table_field_{field.id}",
                "from": table_node_id,
                "to": field.id,
                "from_path": table_node_path,
                "to_path": get_field_path_by_id(db, field.id),
                "type": "contains"
            })
    
    # Add edges for field hierarchy (fields to their subfields)
    for field in all_fields:
        if field.parent_id is not None:
            edge_list.append({
                "id": f"field_subfield_{field.id}",
                "from": field.parent_id,
                "to": field.id,
                "from_path": get_field_path_by_id(db, field.parent_id),
                "to_path": get_field_path_by_id(db, field.id),
                "type": "contains"
            })
    
    # Track external table connections
    external_connections = []
    
    # Add existing equivalence and possibly equivalence edges
    for edge in edges:
        # Get the full paths for both fields using the relationship objects
        from_field = edge.from_field
        to_field = edge.to_field
        if from_field and to_field:
            # Only add edges where both fields belong to the current table
            if from_field.table_id == table_id and to_field.table_id == table_id:
                from_path = get_field_path_by_id(db, from_field.id)
                to_path = get_field_path_by_id(db, to_field.id)
                edge_list.append({
                    "id": edge.id,
                    "from": from_field.id,
                    "to": to_field.id,
                    "from_path": from_path,
                    "to_path": to_path,
                    "type": edge.type
                })
            else:
                # Track external connections
                from_table = db.query(models.Table).filter(models.Table.id == from_field.table_id).first()
                to_table = db.query(models.Table).filter(models.Table.id == to_field.table_id).first()
                from_db = db.query(models.Database).filter(models.Database.id == from_table.database_id).first() if from_table else None
                to_db = db.query(models.Database).filter(models.Database.id == to_table.database_id).first() if to_table else None
                from_cluster = db.query(models.Cluster).filter(models.Cluster.id == from_db.cluster_id).first() if from_db else None
                to_cluster = db.query(models.Cluster).filter(models.Cluster.id == to_db.cluster_id).first() if to_db else None
                
                external_connections.append({
                    "edge_id": edge.id,
                    "from_field_id": from_field.id,
                    "to_field_id": to_field.id,
                    "from_table": {
                        "id": from_field.table_id,
                        "name": from_table.name if from_table else "Unknown",
                        "database": from_db.name if from_db else "Unknown",
                        "cluster": from_cluster.name if from_cluster else "Unknown",
                        "path": f"{from_cluster.name}/{from_db.name}/{from_table.name}" if all([from_cluster, from_db, from_table]) else "Unknown"
                    },
                    "to_table": {
                        "id": to_field.table_id,
                        "name": to_table.name if to_table else "Unknown",
                        "database": to_db.name if to_db else "Unknown",
                        "cluster": to_cluster.name if to_cluster else "Unknown",
                        "path": f"{to_cluster.name}/{to_db.name}/{to_table.name}" if all([to_cluster, to_db, to_table]) else "Unknown"
                    },
                    "type": edge.type
                })
    
    return {
        "table": {
            "id": table.id,
            "name": table.name
        },
        "nodes": nodes,
        "edges": edge_list,
        "external_connections": external_connections
    } 

def list_field_paths_by_table_path(db, cluster: str, database: str, table: str) -> list:
    """
    Return a list of all field and subfield paths under the given table, in the format:
    cluster/database/table/field
    cluster/database/table/field/subfield
    ...
    """
    table_id = get_table_id_by_path(db, cluster, database, table)
    if table_id is None:
        return []
    all_fields = db.query(models.Field).filter(models.Field.table_id == table_id).all()
    paths = []
    for field in all_fields:
        path = get_field_path_by_id(db, field.id)
        paths.append(path)
    return paths 

def list_field_paths_with_empty_description_by_table_path(db, cluster: str, database: str, table: str) -> list:
    """
    Return a list of all field and subfield paths under the given table where the description is empty or missing.
    """
    table_id = get_table_id_by_path(db, cluster, database, table)
    if table_id is None:
        return []
    all_fields = db.query(models.Field).filter(models.Field.table_id == table_id).all()
    paths = []
    for field in all_fields:
        meta = field.meta if isinstance(field.meta, dict) else {}
        desc = meta.get('description', None)
        if desc is None or (isinstance(desc, str) and desc.strip() == ""):
            path = get_field_path_by_id(db, field.id)
            paths.append(path)
    return paths 

def list_field_paths_without_type_by_table_path(db, cluster: str, database: str, table: str) -> list:
    """
    Return a list of all field and subfield paths under the given table where the 'type' in meta is missing or empty.
    """
    table_id = get_table_id_by_path(db, cluster, database, table)
    if table_id is None:
        return []
    all_fields = db.query(models.Field).filter(models.Field.table_id == table_id).all()
    paths = []
    for field in all_fields:
        meta = field.meta if isinstance(field.meta, dict) else {}
        t = meta.get('type', None)
        if t is None or (isinstance(t, str) and t.strip() == ""):
            path = get_field_path_by_id(db, field.id)
            paths.append(path)
    return paths 