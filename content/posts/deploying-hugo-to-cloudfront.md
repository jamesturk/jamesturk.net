+++
Description = ""
date = "2015-03-26T15:23:30-04:00"
title = "Deploying Static Sites to CloudFront"
draft = true

+++

Like most developers, I've written my own blog software half a dozen times.  I've spent a lot more time doing that than writing content but decided this time I'd do something different.  I wanted to keep things as simple as possible but still have an excuse to learn a few new things.  

For generation I wound up settling on [Hugo](http://gohugo.io).
Using Hugo let me explore Go's template syntax and poke around at a pretty well-established Go code base.
I don't intend to get into a full comparison of static site generators but another deciding factor was [Hugo's LiveReload](http://gohugo.io/extras/livereload/) feature, which allows me to write in one window and see the results in a browser window as I save.

While there are a few Hugo-specific things here (e.g. the publish directory and reference to running `hugo` to build the site), everything <abbr title="Amazon Web Services">AWS</abbr>-related would work just as well for Pelican, jekyll, or hand-written HTML.

I also figured I'd try to get the site served over HTTPS.   Given limitations in GitHub pages and S3, [Amazon CloudFront](https://aws.amazon.com/cloudfront/) wound up being the way to go for that.



### Pushing to S3

[Amazon S3's static website hosting](http://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html) is a pretty simple way to host a website for under a dollar a month. ($0.50 for the Route 53 Zone and typically just pennies for the storage and bandwidth.)

Once the bucket is set up, I'm using the handy [s3cmd](http://s3tools.org/s3cmd) tool to upload the files.

I wound up with a short `publish.sh` script that looked something like this:

    # first, run hugo to generate the site
    # upload all files with mimetype detection and marked public
    # explicitly put/set mimetype of CSS (avoid text/plain)

    hugo &&
    s3cmd sync -MP public/ s3://jamesturk.net &&
    s3cmd put -P --mime-type=text/css public/css/main.css

At this point, after following the standard S3 website hosting directions the site was accessible at
jamesturk.net.  S3 does have HTTPS support if you use the full bucket name, but I wanted to get things to https://jamesturk.net.

That's where CloudFront comes in.

### Going from S3 to CloudFront

CloudFront is designed to work very well with S3, acting as an edge cache for faster delivery of assets, it also will allow us to use HTTPS.

Amazon has a [decent guide](http://docs.aws.amazon.com/gettingstarted/latest/swh/getting-started-create-cfdist.html) to doing it.

I did a few things differently, choosing a cheaper set of edge locations, configuring 404 pages, and forcing HTTPS.

* If you haven't already, obtain an SSL certificate.  [Eric Mill](https://konklone.com/post/switch-to-https-now-for-free) has a good guide if you aren't sure how.
* Upload your SSL certificate to AWS, [Amazon explains how](http://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/SecureConnections.html#CNAMEsAndHTTPS) but it boiled down to this:

```
aws iam upload-server-certificate
    --server-certificate-name CertificateName
    --certificate-body file://public_key_certificate_file
    --private-key file://privatekey.pem
    --certificate-chain file://certificate_chain_file
    --path /cloudfront/sitename/
```

* Now follow the instructions under "*Create a CloudFront Distribution*" from [Amazon's guide](http://docs.aws.amazon.com/gettingstarted/latest/swh/getting-started-create-cfdist.html).  There'll be a few minor differences:
    * Set **Viewer Protocol Policy** to HTTPS only
    * If you're like me, consider changing **Price Class** to **Use Only US and Europe** to save a little bit.
    * Set **SSL Certificate** to **Custom SSL Certificate** and select the cert you uploaded earlier.
    * **DO NOT** select **All Clients** under **Custom SSL Client Support**. This will cost $600/month,  [SNI](http://en.wikipedia.org/wiki/Server_Name_Indication) is free and just fine for most purposes.
* Now you'll need to follow the instructions under *Update the Record Sets for Your Domain and Subdomain* the [same Amazon guide](http://docs.aws.amazon.com/gettingstarted/latest/swh/getting-started-create-cfdist.html).  This will update your Route 53 config to point at the CloudFront distribution.

At this point, you'll have a working CloudFront distribution so that when people visit *https://yoursite.biz* they'll hit the nearest CloudFront edge which will return cached content from your S3 bucket.  Updating the site is the same as it has always been, but there will be propagation delays as the content makes its way from S3 to CloudFront.

### Next Steps

Now go ahead and make an update and run the s3cmd publishing steps and you'll notice that the changes **aren't** live on your site.  Eventually (by default in about a day) the CloudFront edge cache will expire and update, but that's often less than desirable.

To speed things up you can manually invalidate pages out of the CloudFront distribution.  (It'll still take 10-15 minutes for the edge nodes to receive the invalidation.)

I've written a small Python script to automatically invalidate all objects in the public directory:

```
#!/usr/bin/env python3
import pathlib
import boto.cloudfront

# Credentials in ~/.aws/credentials
DISTRIBUTION_ID = ''      # needs to be set, looks like E11J4SQ1T6811B

if __name__ == '__main__':
    # every file under public
    paths = ['/'+str(p.relative_to('public'))
             for p in pathlib.Path('public').rglob('*') if p.is_file()]

    cf = boto.cloudfront.CloudFrontConnection()
    cf.create_invalidation_request(DISTRIBUTION_ID, paths)
    print('created invalidation request for {} files'.format(len(paths)))
```

This is overkill as it'll invalidate all objects, it'd be possible to figure out which objects have changed and only invalidate those.

Note that by default you're allowed 1,000 free object invalidations a month, and then you start paying $0.005 per file.  For my purposes this is more than enough, but something to consider if you're constantly republishing.

I save that file as `cf.py` and then update the `publish.sh` to look like:

```
hugo &&
s3cmd sync -MP public/ s3://jamesturk.net &&
s3cmd put -P --mime-type=text/css public/css/main.css &&
./cf.py
```

And now every time you're ready to publish a simple `./publish.sh` does the trick.

## Questions? Suggestions?

<a href="https://twitter.com/intent/tweet?text=@jamesturk%20...&related=jamesturk"> <i class="fa fa-twitter"></i> Tweet at me</a>
