#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2018, Anaconda, Inc., and Bokeh Contributors.
# All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------
''' Generate and publish badges bokeh related statistics.

'''

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
import os
import json
from subprocess import check_output

# External imports
from google.cloud import bigquery as bq
from google.oauth2 import service_account

import boto3
import requests

# Bokeh imports

#-----------------------------------------------------------------------------
# Globals and constants
#-----------------------------------------------------------------------------

AWS_BUCKET_NAME = "badges.bokeh.org"

AWS_HEADERS = {
    'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0',
}

BADGE_URL = "https://img.shields.io/badge/downloads-%0.2fk%%2Fmonth-brightgreen.svg"

PIP_BADGE_FILE_NAME = "pip-downloads-30-day.svg"

PIP_QUERY = """
SELECT COUNT(*) as total_downloads
FROM TABLE_DATE_RANGE(
    [the-psf:pypi.downloads],
    DATE_ADD(CURRENT_TIMESTAMP(), -31, 'DAY'),
    CURRENT_TIMESTAMP()
)
WHERE file.project = 'bokeh'
LIMIT 100
"""

#-----------------------------------------------------------------------------
# Public API
#-----------------------------------------------------------------------------

def badge(event, context):

    # -- credentials -=----------------

    ssm = boto3.client('ssm')
    result = ssm.get_parameter(Name='bokeh-docs-google-cloud-credentials', WithDecryption=True)
    creds = result['Parameter']['Value']
    google_credentials = service_account.Credentials.from_service_account_info(json.loads(creds))

    # -- query ------------------------

    client = bq.Client(credentials=google_credentials, project='bokeh-docs')
    config = bq.QueryJobConfig(use_legacy_sql=True)
    query = client.query(PIP_QUERY, job_config=config)
    results = list(query.result())
    downloads = int(results[0]['total_downloads'])

    # -- badge ------------------------

    badge_url = BADGE_URL % (downloads / 1000.0)
    badge_request = requests.get(badge_url, stream=True)
    badge_data = badge_request.raw.read(decode_content=True).decode('utf-8')

    # -- publish  ---------------------

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(AWS_BUCKET_NAME)

    result = bucket.put_object(
        ContentType='image/svg+xml',
        Key=PIP_BADGE_FILE_NAME,
        Body=badge_data,
        Metadata=AWS_HEADERS,
    )

    # -- return -----------------------

    body = {
        "uploaded": "true",
        "bucket": AWS_BUCKET_NAME,
        "pip": PIP_BADGE_FILE_NAME
    }

    return {
        "statusCode": 200,
        "body": json.dumps(body)
    }
