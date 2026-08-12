"""
S3 raw zone: land the untouched Treasury API response before any cleaning.
 
The raw zone is a durable, private copy of exactly what the source returned,
stored write-once. Everything downstream reads from here, not from the live API anymore.
"""

import json
from datetime import datetime, timezone
import boto3
from typing import Optional

SOURCE = 'us_treasury'
DATASET = 'debt_to_penny'    
RAW_BUCKET = 'treasury-raw-an-2026'

def build_raw_key(pulled_at: datetime) -> str:
    """
    A full HH:MM:SS timestamp on the filename makes each pull unique, so a second
    pull on the same day will land beside the first pull, instead of overwriting it.
    """
    date_prefix = pulled_at.strftime("year=%Y/month=%m/day=%d")   # today's date
    stamp = pulled_at.strftime("%Y%m%dT%H%M%SZ")                  # HH:MM:SS
    return f"raw/{SOURCE}/{DATASET}/{date_prefix}/pull_{stamp}.json"


def land_raw(raw_response, pulled_at: Optional[datetime] = None) -> str:
    """
    Write the response to S3 exactly as received.
    """
    pulled_at = pulled_at or datetime.now(timezone.utc)

    key = build_raw_key(pulled_at)
    body = json.dumps(raw_response).encode("utf-8")
 
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=RAW_BUCKET,
        Key=key,
        Body=body,
        ContentType="application/json",
    )
    return key

if __name__ == "__main__":
    raw = {"example": "the untouched API response goes here"}

    key = land_raw(raw)
    print(f"landed raw pull at s3://{RAW_BUCKET}/{key}")
    
    # path = f's3a://{RAW_BUCKET}/{key}'