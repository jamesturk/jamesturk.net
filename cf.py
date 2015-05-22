#!/usr/bin/env python3

import pathlib
import boto.cloudfront

# Credentials in ~/.aws/credentials
DISTRIBUTION_ID = 'E22K2SQ1U6924J'

if __name__ == '__main__':
    cf = boto.cloudfront.CloudFrontConnection()
    # counts as just one request out of the 1000 free requests
    cf.create_invalidation_request(DISTRIBUTION_ID, '/*')
    print('created invalidation request for /*')
