import boto3

def main():
    ec2 = boto3.client("ec2")
    resp = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )
    for reservation in resp.get("Reservations", []):
        for inst in reservation.get("Instances", []):
            iid = inst.get("InstanceId")
            state = inst.get("State", {}).get("Name")
            typ = inst.get("InstanceType")
            print(f"{iid}\t{state}\t{typ}")

if __name__ == "__main__":
    main()