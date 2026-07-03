"""
S3 raw zone: land the untouched Treasury API response before any cleaning.
 
The raw zone is a durable, private copy of exactly what the source returned,
stored write-once. Everything downstream reads from here, not from the live API anymore.
"""

import json
from datetime import datetime, timezone
import boto3

def build_raw_key(pulled_at: datetime) -> str:
    """
    A full HH:MM:SS timestamp on the filename makes each pull unique, so a second
    pull on the same day will land beside the first pull, instead of overwriting it.
    """
    date_prefix = pulled_at.strftime("year=%Y/month=%m/day=%d")   # today's date
    stamp = pulled_at.strftime("%Y%m%dT%H%M%SZ")                  # HH:MM:SS
    return f"raw/{SOURCE}/{DATASET}/{date_prefix}/pull_{stamp}.json"