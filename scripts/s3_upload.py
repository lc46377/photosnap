import boto3
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Create an S3 bucket and upload a file"
    )
    parser.add_argument("bucket", help="Name of the S3 bucket")
    parser.add_argument("file", help="Path to the local file to upload")
    parser.add_argument(
        "--key",
        help="S3 object key (defaults to filename)",
        default=None,
    )
    args = parser.parse_args()

    s3 = boto3.client("s3")
    try:
        s3.create_bucket(Bucket=args.bucket)
        print(f"Bucket '{args.bucket}' created")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket '{args.bucket}' already owned by you")
    except Exception as e:
        print(f"Error creating bucket: {e}")
        return

    key = args.key or args.file.split("/")[-1]
    try:
        s3.upload_file(args.file, args.bucket, key)
        print(f"Uploaded {args.file} to s3://{args.bucket}/{key}")
    except Exception as e:
        print(f"Upload error: {e}")

if __name__ == "__main__":
    main()