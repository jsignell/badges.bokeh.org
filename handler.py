# ----------------------------------------------------------------------------
# Copyright (c) 2012 - 2018, Anaconda, Inc., and Bokeh Contributors.
# All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
''' Generate and publish badges bokeh related statistics.

'''

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Standard library imports
import json

# External imports
from google.cloud import bigquery as bq
from google.oauth2 import service_account

import boto3
import requests

# Bokeh imports

# Local imports
from pip_badge import pip_badge
from conda_badge import conda_badge

# ----------------------------------------------------------------------------
# Globals and constants
# ----------------------------------------------------------------------------

AWS_BUCKET_NAME = "badges.bokeh.org"

AWS_HEADERS = {
    'Content-Type': 'image/svg+xml',
    'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0',
}

PIP_BADGE_FILE_NAME = "pip-downloads-1-month.svg"
CONDA_BADGE_FILE_NAME = "conda-downloads-1-month.svg"


def badge(event, context):
    conda_downloads = conda_badge()
    pip_downloads = pip_badge()

    # -- publish  ---------------------

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(AWS_BUCKET_NAME)

    result = bucket.put_object(
        ContentType='image/svg+xml',
        CacheControl='no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0',
        Key=PIP_BADGE_FILE_NAME,
        Body=pip_downloads,
    )

    result = bucket.put_object(
        ContentType='image/svg+xml',
        CacheControl='no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0',
        Key=CONDA_BADGE_FILE_NAME,
        Body=conda_downloads,
    )

    # -- return -----------------------

    body = {
        "uploaded": "true",
        "bucket": AWS_BUCKET_NAME,
        "pip": PIP_BADGE_FILE_NAME,
        "conda": CONDA_BADGE_FILE_NAME,
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }
