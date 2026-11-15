import argparse, json, uuid
from datetime import datetime, timezone
from .db import initialize_database, SessionLocal
from .models import MissionRow, AstronautRow, AliasRow, SourceSessionRow

def seed():
    db=SessionLocal()
    try:
        mission_id=str(uuid.uuid4()); db.add(MissionRow(id=mission_id,start_at=datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),synthetic=True)); db.flush()
        created=[]
        for namespace, alias, fmt, label in [("ayoub_raw_v1","AST-001","ayoub_raw_v1","Ayoub fictional source subject"),("amina_simulator_v1","AST-01","amina_simulator_v1","Amina fictional simulator subject"),("demo","demo-crew-01","canonical_v1","Demo crew subject")]:
            aid=str(uuid.uuid4()); sid=str(uuid.uuid4()); db.add(AstronautRow(id=aid,mission_id=mission_id,display_name=label,role="Synthetic demo",synthetic=True)); db.flush(); db.add(AliasRow(mission_id=mission_id,astronaut_id=aid,namespace=namespace,value=alias)); db.add(SourceSessionRow(id=sid,mission_id=mission_id,source_format=fmt,namespace=namespace,allowed_aliases_json=json.dumps([alias]))); created.append({"source_format":fmt,"source_session_id":sid,"astronaut_id":aid,"alias":alias})
        db.commit(); print(json.dumps({"mission_id":mission_id,"sessions":created},indent=2))
    finally: db.close()

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("command",choices=["init-db","seed-demo"]); command=parser.parse_args().command
    initialize_database()
    if command=="seed-demo": seed()
    elif command=="init-db": print("Database initialized")
    else: raise SystemExit("Use init-db or seed-demo")

if __name__=="__main__": main()
