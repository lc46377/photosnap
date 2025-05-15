import os
import uuid
import boto3
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, text

# —————————————————————————————————————————————
# App & Configuration
# —————————————————————————————————————————————

app = Flask(__name__)

# Global CORS (we'll also inject via after_request)
CORS(app, resources={r"/*": {"origins": "*"}})

# Inject CORS headers on every response (including errors)
@app.after_request
def add_cors_headers(response):
    response.headers.setdefault("Access-Control-Allow-Origin", "*")
    response.headers.setdefault("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    response.headers.setdefault("Access-Control-Allow-Headers", "Content-Type,Authorization")
    return response

# JWT config
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET", "super-secret-key")
jwt = JWTManager(app)

# AWS & DB config from environment
S3_BUCKET = os.environ["SNAPS_BUCKET"]
DB_ENDPOINT = os.environ["DB_ENDPOINT"]
DB_USER    = os.environ["DB_USERNAME"]
DB_PASS    = os.environ["DB_PASSWORD"]
DB_NAME    = os.environ.get("DB_NAME", "postgres")
REGION     = os.environ.get("AWS_REGION", "us-east-1")

# Clients / DB engine
s3 = boto3.client("s3", region_name=REGION)
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_ENDPOINT}:5432/{DB_NAME}")

# —————————————————————————————————————————————
# Authentication Endpoints
# —————————————————————————————————————————————

@app.route("/signup", methods=["OPTIONS", "POST"])
def signup():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return {"msg": "username & password required"}, 400

    pw_hash = generate_password_hash(password, method="pbkdf2:sha256")
    try:
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO users (username, password_hash) VALUES (:u, :p)"),
                {"u": username, "p": pw_hash}
            )
    except Exception as e:
        return {"msg": f"error: {str(e)}"}, 400

    return {"msg": "user created"}, 201

@app.route("/login", methods=["OPTIONS", "POST"])
def login():
    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return {"msg": "username & password required"}, 400

    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, password_hash FROM users WHERE username = :u"),
            {"u": username}
        )
        row = result.mappings().first()

    if not row or not check_password_hash(row["password_hash"], password):
        return {"msg": "bad credentials"}, 401

    access_token = create_access_token(identity=str(row["id"]))
    return {"access_token": access_token}, 200

# —————————————————————————————————————————————
# Friend Request Endpoints
# —————————————————————————————————————————————

@app.route("/friends/pending", methods=["GET"])
@jwt_required()
def list_pending():
    me = get_jwt_identity()
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT id, from_user FROM friend_requests "
                "WHERE to_user = :me AND status = 'pending'"
            ),
            {"me": me}
        )
        rows = result.mappings().all()

    return jsonify([
        {"req_id": str(r["id"]), "from_user": str(r["from_user"])}
        for r in rows
    ])

@app.route("/friends/list", methods=["OPTIONS", "GET"])
@jwt_required()
def list_friends():
    if request.method == "OPTIONS":
        return "", 200

    me = get_jwt_identity()
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT id, username FROM users WHERE id != :me"),
            {"me": me}
        )
        rows = result.mappings().all()

    return jsonify([
        {"id": str(r["id"]), "username": r["username"]}
        for r in rows
    ])

@app.route("/friends/request", methods=["OPTIONS", "POST"])
@jwt_required()
def send_request():
    if request.method == "OPTIONS":
        return "", 200

    me = get_jwt_identity()
    data = request.get_json() or {}
    to_user = data.get("to_user")
    if not to_user:
        return {"msg": "to_user required"}, 400

    with engine.begin() as conn:
        conn.execute(text(
            "INSERT INTO friend_requests (from_user, to_user) VALUES (:f, :t)"
        ), {"f": me, "t": to_user})

    return {"msg": "request sent"}, 201

@app.route("/friends/respond", methods=["OPTIONS", "POST"])
@jwt_required()
def respond_request():
    if request.method == "OPTIONS":
        return "", 200

    me = get_jwt_identity()
    data = request.get_json() or {}
    req_id = data.get("req_id")
    action = data.get("action")  # "accepted" or "rejected"
    if action not in ("accepted", "rejected"):
        return {"msg": "invalid action"}, 400

    with engine.begin() as conn:
        conn.execute(text(
            "UPDATE friend_requests SET status = :s "
            "WHERE id = :i AND to_user = :me"
        ), {"s": action, "i": req_id, "me": me})

    return {"msg": "done"}, 200

# —————————————————————————————————————————————
# Snap Upload & View Endpoints
# —————————————————————————————————————————————

@app.route("/upload", methods=["OPTIONS", "POST"])
@jwt_required()
def upload():
    if request.method == "OPTIONS":
        return "", 200

    me = get_jwt_identity()
    data = request.get_json() or {}
    filename   = data.get("filename")
    recipients = data.get("recipients", [])

    if not filename or not recipients:
        return {"msg": "filename  recipients required"}, 400

    snap_id = str(uuid.uuid4())
    key     = f"raw/{snap_id}-{filename}"

    put_url = s3.generate_presigned_url(
        "put_object", Params={"Bucket": S3_BUCKET, "Key": key}, ExpiresIn=300
    )
    get_url = s3.generate_presigned_url(
        "get_object", Params={"Bucket": S3_BUCKET, "Key": key}, ExpiresIn=300
    )

    with engine.begin() as conn:
        conn.execute(text(
            "INSERT INTO snaps (id, s3_key, owner) VALUES (:id, :key, :owner)"
        ), {"id": snap_id, "key": key, "owner": me})

        for uid in recipients:
            conn.execute(text(
                "INSERT INTO snap_recipients (snap_id, user_id) VALUES (:s, :u)"
            ), {"s": snap_id, "u": uid})

    return jsonify({"id": snap_id, "put_url": put_url, "get_url": get_url})

@app.route("/view/<snap_id>", methods=["OPTIONS", "GET"])
@jwt_required()
def view_snap(snap_id):
    if request.method == "OPTIONS":
        return "", 200

    me = get_jwt_identity()
    with engine.begin() as conn:
        row = conn.execute(text(
            "SELECT viewed FROM snap_recipients "
            "WHERE snap_id = :s AND user_id = :me"
        ), {"s": snap_id, "me": me}).fetchone()

        if not row:
            return {"msg": "not allowed"}, 403
        if row["viewed"]:
            return {"msg": "already viewed"}, 410

        conn.execute(text(
            "UPDATE snap_recipients SET viewed = true "
            "WHERE snap_id = :s AND user_id = :me"
        ), {"s": snap_id, "me": me})

        snap = conn.execute(text(
            "SELECT s3_key FROM snaps WHERE id = :s"
        ), {"s": snap_id}).fetchone()

        get_url = s3.generate_presigned_url(
            "get_object", Params={"Bucket": S3_BUCKET, "Key": snap["s3_key"]}, ExpiresIn=300
        )

    return jsonify({"get_url": get_url})

@app.route("/snaps/list", methods=["OPTIONS", "GET"])
@jwt_required()
def list_snaps():
    if request.method == "OPTIONS":
        return "", 200

    me = get_jwt_identity()
    sql = text("""
      SELECT sr.snap_id, u.username
      FROM snap_recipients AS sr
      JOIN snaps           AS s  ON sr.snap_id = s.id
      JOIN users           AS u  ON s.owner    = u.id
      WHERE sr.user_id = :me
    """)
    rows = engine.connect().execute(sql, {"me": me}).fetchall()
    
    return jsonify([{"id": str(r[0]), "owner": r[1]} for r in rows])

# —————————————————————————————————————————————
# Health Check
# —————————————————————————————————————————————

@app.route("/", methods=["GET"])
def health():
    return "OK", 200

# —————————————————————————————————————————————

if __name__ == "__main__":
    # in dev
    app.run(host="0.0.0.0", port=5000)
    # in prod, you’ll use: gunicorn app:app --bind 0.0.0.0:5000
