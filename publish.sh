#!/bin/sh

AWS_DEFAULT_PROFILE=james
rm -rf public/ &&
hugo &&
aws s3 sync --acl public-read public/ s3://jamesturk.net &&
aws cloudfront create-invalidation --distribution-id E22K2SQ1U6924J --path "/*"
