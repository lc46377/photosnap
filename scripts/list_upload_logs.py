import boto3
import sys


def main():
    log_group = sys.argv[1] if len(
        sys.argv) > 1 else "/aws/lambda/photoSnapS3Logger"

    logs = boto3.client("logs", region_name="us-east-1")

    resp = logs.describe_log_streams(
        logGroupName=log_group,
        orderBy="LastEventTime",
        descending=True,
        limit=1
    )
    streams = resp.get("logStreams", [])
    if not streams:
        print(f"No log streams found in {log_group!r}")
        return

    stream_name = streams[0]["logStreamName"]

    # Fetch up to 10 of the latest events
    events = logs.get_log_events(
        logGroupName=log_group,
        logStreamName=stream_name,
        limit=10,
        startFromHead=False
    )["events"]

    if not events:
        print("No log events found.")
        return

    # Print each message
    for evt in events:
        print(evt["message"])


if __name__ == "__main__":
    main()
