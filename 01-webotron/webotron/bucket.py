# -*- coding: utf-8 -*-

"""Classes for S3 buckets."""

from functools import reduce
from hashlib import md5
import mimetypes
import pathlib

from botocore.exceptions import ClientError

import boto3
import util


class BucketManager:
    """Manage an S3 Bucket."""
    
    CHUNK_SIZE = 8388608

    def __init__(self, session):
        """Create a BucketManager object."""
        self.session = session
        self.s3 = session.resource('s3')
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize=self.CHUNK_SIZE,
            multipart_threshold=self.CHUNK_SIZE
        )

        self.manifest = {}

    def get_bucket(self, bucket_name):
        """Get bucket object given bucket name."""
        return self.s3.Bucket(bucket_name)

    def get_region_name(self, bucket):
        """Get the bucket's region name."""
        bucket_location = self.s3.meta.client.get_bucket_location(Bucket=bucket.name)
        return bucket_location["LocationConstraint"] or 'us-east-1'

    def get_bucket_url(self, bucket):
        """Get the website URL for this bucket."""
        return "http://{}.{}".format(
            bucket.name,
            util.get_endpoint(self.get_region_name(bucket)).host)

    def all_buckets(self):
        """Get an interator for all buckets."""
        return self.s3.buckets.all()

    def all_objects(self, bucket):
        """Get an interator all all objects in a bucket."""
        return self.s3.Bucket(bucket).objects.all()

    def init_bucket(self, bucket_name):
        """Create a new bucket or return an existing bucket."""
        s3_bucket = None
        try:
            if self.session.region_name == 'us-east-1':
                s3_bucket = self.s3.create_bucket(Bucket=bucket_name)
            else:
                print("Creating bucket: %s" % (bucket_name))
                s3_bucket = self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.session.region_name})

        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise error

        return s3_bucket

    @staticmethod
    def set_policy(bucket):
        """Set bucket policy to be readable by everyone."""
        policy = """
        {
            "Version":"2012-10-17",
            "Statement":[{
                "Sid":"PublicReadGetObject",
                "Effect":"Allow",
                "Principal": "*",
                "Action":["s3:GetObject"],
                "Resource":["arn:aws:s3:::%s/*"]
            }]
         }
        """ % bucket.name
        policy = policy.strip()

        pol = bucket.Policy()
        pol.put(Policy=policy)

    @staticmethod
    def configure_website(bucket):
        """Configure bucket to be a website."""
        bucket.Website().put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        })

    def load_manifest(self, bucket):
        """Load manifest for caching purposes."""
        paginator = self.s3.meta.client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket.name):
            for obj in page.get('Contents', []):
                self.manifest[obj['Key']] = obj['ETag']
        print(self.manifest)

    @staticmethod
    def hash_data(data):
        """Gnerate md5 hash for data."""
        hash = md5()
        hash.update(data)

        return hash

    def gen_etag(self, path):
        """Generate etag for file."""
        hashes = []

        with open(path, 'rb') as f:
            while True:
                data = f.read(self.CHUNK_SIZE)

                if not data:
                    break

                hashes.append(self.hash_data(data))

        if not hashes:
            return ""
        elif len(hashes) == 1:
            return '"{}"'.format(hashes[0].hexdigest())
        else:
            hash = self.hash_data(reduce(lambda x, y: x + y, (h.digest() for h in hashes)))
            return '"{}-{}"'.format(hash.hexdigest(), len(hashes))

    def upload_file(self, bucket, path, key):
        """Upload file to S3 bucket given a path and key."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'

        etag = self.gen_etag(path)
        # handle zero-byte file
        if etag == "":
            pass
        elif self.manifest.get(key, '') == etag:
            print("Skipping {}, etags match".format(key))
            return

        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            },
            Config=self.transfer_config
        )

    def sync(self, pathname, bucket_name):
        """Sync files in local directory to bucket."""
        bucket = self.s3.Bucket(bucket_name)
        self.load_manifest(bucket)
        root = pathlib.Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for path in target.iterdir():
                if path.is_dir():
                    handle_directory(path)
                if path.is_file():
                    key = pathlib.PurePosixPath(path.relative_to(root))
                    self.upload_file(bucket, str(path), str(key))

        handle_directory(root)
