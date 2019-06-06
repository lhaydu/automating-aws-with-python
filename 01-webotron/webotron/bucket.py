# -*- coding: utf-8 -*-

"""Classes for S3 buckets."""

import mimetypes
import pathlib
from botocore.exceptions import ClientError
import util

class BucketManager:
    """Manage an S3 Bucket."""

    def __init__(self, session):
        """Create a BucketManager object."""
        self.session = session
        self.s3 = session.resource('s3')
        pass

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
                s3_bucket = self.s3.create_bucket(
                    Bucket='bucket',
                    CreateBucketConfiguration={'Location_Constraint': self.session.region_name})

        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise error

        return s3_bucket

    def set_policy(self, bucket):
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

    def configure_website(self, bucket):
        """Configure bucket to be a website."""
        bucket.Website().put(WebsiteConfiguration={
            'ErrorDocument': {
                'Key': 'error.html'
            },
            'IndexDocument': {
                'Suffix': 'index.html'
            }
        })

    @staticmethod
    def upload_file(bucket, path, key):
        """Upload file to S3 bucket given a path and key."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'
        return bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            }
        )

    def sync(self, pathname, bucket_name):
        """Sync files in local directory to bucket."""
        bucket = self.s3.Bucket(bucket_name)
        root = pathlib.Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for path in target.iterdir():
                if path.is_dir():
                    handle_directory(path)
                if path.is_file():
                    key = pathlib.PurePosixPath(path.relative_to(root))
                    self.upload_file(bucket, str(path), str(key))

        handle_directory(root)
