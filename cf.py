#!/usr/bin/env python3

import pathlib
import boto.cloudfront

# Credentials in ~/.aws/credentials
DISTRIBUTION_ID = 'E22K2SQ1U6924J'

if __name__ == '__main__':
    # every file under public
    paths = ['/'+str(p.relative_to('public')) for p in pathlib.Path('public').rglob('*') if p.is_file()]

    cf = boto.cloudfront.CloudFrontConnection()
    cf.create_invalidation_request(DISTRIBUTION_ID, paths)
    print('created invalidation request for {} files'.format(len(paths)))
