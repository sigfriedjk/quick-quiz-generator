"""Remove legacy resources not managed by Terraform, after a successful destroy."""
import json
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

BUCKET = "sigfriedjk-quickquiz-generator-bundles"
LOG_GROUP = "/aws/lambda/quiz_lambda"


def main():
    state = json.loads(Path("terraform.tfstate").read_text())
    if state.get("resources") != []:
        raise RuntimeError("Refusing cleanup: Terraform state is not empty.")

    logs = boto3.client("logs", region_name="us-east-1")
    try:
        logs.delete_log_group(logGroupName=LOG_GROUP)
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise

    s3 = boto3.client("s3", region_name="us-east-1")
    # Include old versions and delete markers; `aws s3 rb --force` misses these.
    # Keep the state key until everything else is removed so failures are retryable.
    for state_only in (False, True):
        for page in s3.get_paginator("list_object_versions").paginate(Bucket=BUCKET):
            objects = [
                {"Key": obj["Key"], "VersionId": obj["VersionId"]}
                for kind in ("Versions", "DeleteMarkers")
                for obj in page.get(kind, [])
                if (obj["Key"] == "terraform.tfstate") == state_only
            ]
            for offset in range(0, len(objects), 1000):
                result = s3.delete_objects(
                    Bucket=BUCKET, Delete={"Objects": objects[offset:offset + 1000]}
                )
                if result.get("Errors"):
                    raise RuntimeError(f"S3 deletion failed: {result['Errors']}")
    try:
        s3.delete_bucket(Bucket=BUCKET)
    except ClientError:
        # Preserve the empty state if bucket deletion fails after removing its key.
        s3.put_object(Bucket=BUCKET, Key="terraform.tfstate",
                      Body=Path("terraform.tfstate").read_bytes())
        raise


if __name__ == "__main__":
    main()
