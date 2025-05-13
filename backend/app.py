import os
import uuid
import boto3
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/upload": {"origins": "*"},
    r"/view/*": {"origins": "*"}
})

# Config from environment
S3_BUCKET = os.environ["SNAPS_BUCKET"]
DB_ENDPOINT = os.environ["DB_ENDPOINT"]
DB_USER = os.environ["DB_USERNAME"]
DB_PASS = os.environ["DB_PASSWORD"]
DB_NAME = os.environ.get("DB_NAME", "postgres")
REGION = os.environ.get("AWS_REGION", "us-east-1")

# Clients / DB engine
s3 = boto3.client("s3", region_name=REGION)
engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASS}@{DB_ENDPOINT}:5432/{DB_NAME}")


@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "filename required"}), 400

    # Generate IDs & keys
    snap_id = str(uuid.uuid4())
    key = f"raw/{snap_id}-{filename}"

    # Pre-signed URLs
    put_url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=300
    )
    get_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=300
    )

    # Insert metadata into RDS
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO snaps (id, s3_key) VALUES (:id, :key)"),
            {"id": snap_id, "key": key}
        )

    return jsonify({"id": snap_id, "put_url": put_url, "get_url": get_url})


@app.route("/view/<snap_id>", methods=["GET"])
def view_snap(snap_id):
    # Lookup key in DB
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT s3_key FROM snaps WHERE id = :id"),
            {"id": snap_id}
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        key = row[0]

    # Generate a fresh pre-signed GET URL
    get_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=300
    )
    return jsonify({"get_url": get_url})


@app.route("/", methods=["GET"])
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
