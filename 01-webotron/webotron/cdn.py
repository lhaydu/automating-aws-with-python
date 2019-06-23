# -*- coding: utf-8 -*-


"""Class for CloudFront Distribution."""


import uuid


class DistributionManager:
    """Class for CDN Distribution."""

    def __init__(self, session):
        """Initialization."""
        self.session = session
        self.client = self.session.client('cloudfront')

    def find_matching_dist(self, domain_name):
        """Determine if the CDN exists for the domain."""
        paginator = self.client.get_paginator('list_distributions')
        dist = None
        for page in paginator.paginate():
            try:
                for dist in page['DistributionList']['Items']:
                    for alias in dist['Aliases']['Items']:
                        if alias == domain_name:
                            return dist
            except:
                pass
            finally:
                print("Distribution does not contain Aliases: %s" % (dist['DomainName']))

        return None

    def create_dist(self, domain_name, cert):
        """Create a CDN for the domain and apply the certificiate."""
        origin_id = 'S3-' + domain_name
        result = self.client.create_distribution(
            DistributionConfig={
                'CallerReference': str(uuid.uuid4()),
                'Aliases': {
                    'Quantity': 1,
                    'Items': [domain_name]
                },
                'DefaultRootObject': 'index.html',
                'Comment': 'Created by webotron',
                'Enabled': True,
                'Origins': {
                    'Quantity': 1,
                    'Items': [{
                        'Id': origin_id,
                        'DomainName': '{}.s3.amazonaws.com'.format(domain_name),
                        'S3OriginConfig': {
                            'OriginAccessIdentity': ''
                        }
                    }]
                },
                'DefaultCacheBehavior': {
                    'TargetOriginId': origin_id,
                    'ViewerProtocolPolicy': 'redirect-to-https',
                    'TrustedSigners': {
                        'Quantity': 0,
                        'Enabled': False
                    },
                    'ForwardedValues': {
                        'Cookies': {'Forward': 'all'},
                        'Headers': {'Quantity': 0},
                        'QueryString': False,
                        'QueryStringCacheKeys': {'Quantity': 0}
                    },
                    'DefaultTTL': 86400,
                    'MinTTL': 3600
                },
                'ViewerCertificate': {
                    'ACMCertificateArn': cert['CertificateArn'],
                    'SSLSupportMethod': 'sni-only',
                    'MinimumProtocolVersion': 'TLSv1.1_2016'
                }
            }
        )
        return result['Distribution']

    def await_deploy(self, dist):
        """Check for the completion of the distribution deployment."""
        waiter = self.client.get_waiter('distribution_deployed')
        waiter.wait(Id=dist['Id'], WaiterConfig={
            'Delay': 30,
            'MaxAttempts': 50
            })
