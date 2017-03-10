#!/usr/bin/env python3

import time
import boto3

# Credentials in ~/.aws/credentials
DISTRIBUTION_ID = 'E22K2SQ1U6924J'

if __name__ == '__main__':
    cf = boto3.client('cloudfront')
    # counts as just one request out of the 1000 free requests
    cf.create_invalidation(DistributionId=DISTRIBUTION_ID,
                           InvalidationBatch={
                               'Paths': {'Quantity': 1, 'Items': ['/*']},
                               'CallerReference': str(time.time())
                           }
                           )
    print('created invalidation request for /*')
