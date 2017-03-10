AWS_DEFAULT_PROFILE=james
rm -rf public/ &&
hugo &&
s3cmd -c ~/.s3cfg sync -MP public/ s3://jamesturk.net &&
s3cmd -c ~/.s3cfg put -P --mime-type=text/css public/css/main.css s3://jamesturk.net/css/main.css &&
./cf.py
