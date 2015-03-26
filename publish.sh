rm -rf public/ &&
hugo &&
s3cmd -c ~/.s3cmd/personal sync -MP public/ s3://jamesturk.net &&
s3cmd -c ~/.s3cmd/personal put -P --mime-type=text/css public/css/main.css s3://jamesturk.net/css/main.css &&
./cf.py
