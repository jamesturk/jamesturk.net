#!/bin/sh

# set AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESSPKEY
../letsencrypt/letsencrypt-auto --agree-tos -a letsencrypt-s3front:auth \
    --letsencrypt-s3front:auth-s3-bucket jamesturk.net \
    -i letsencrypt-s3front:installer \
    --letsencrypt-s3front:installer-cf-distribution-id E22K2SQ1U6924J \
    -d jamesturk.net -d www.jamesturk.net --debug
