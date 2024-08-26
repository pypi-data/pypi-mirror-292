from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

import aws_cdk.aws_events._jsii
import aws_cdk.aws_events_targets._jsii
import aws_cdk.aws_iam._jsii
import aws_cdk.aws_lambda._jsii
import aws_cdk.aws_logs._jsii
import aws_cdk.aws_route53._jsii
import aws_cdk.aws_s3._jsii
import aws_cdk.core._jsii
import constructs._jsii

__jsii_assembly__ = jsii.JSIIAssembly.load(
    "cdk-certbot-dns-route53",
    "1.2.236",
    __name__[0:-6],
    "cdk-certbot-dns-route53@1.2.236.jsii.tgz",
)

__all__ = [
    "__jsii_assembly__",
]

publication.publish()
