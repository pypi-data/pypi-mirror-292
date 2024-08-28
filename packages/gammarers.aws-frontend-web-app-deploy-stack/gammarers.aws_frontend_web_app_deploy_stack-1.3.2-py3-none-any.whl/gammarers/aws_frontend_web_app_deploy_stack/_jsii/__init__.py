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

import aws_cdk._jsii
import constructs._jsii
import gammarers.aws_secure_bucket._jsii
import gammarers.aws_secure_cloudfront_origin_bucket._jsii
import gammarers.aws_secure_frontend_web_app_cloudfront_distribution._jsii

__jsii_assembly__ = jsii.JSIIAssembly.load(
    "@gammarers/aws-frontend-web-app-deploy-stack",
    "1.3.2",
    __name__[0:-6],
    "aws-frontend-web-app-deploy-stack@1.3.2.jsii.tgz",
)

__all__ = [
    "__jsii_assembly__",
]

publication.publish()
