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

import aws_cdk.aws_ec2._jsii
import aws_cdk.aws_ecs._jsii
import aws_cdk.aws_ecs_patterns._jsii
import aws_cdk.aws_efs._jsii
import aws_cdk.aws_rds._jsii
import aws_cdk.core._jsii
import constructs._jsii

__jsii_assembly__ = jsii.JSIIAssembly.load(
    "cdk-wordpress", "0.0.994", __name__[0:-6], "cdk-wordpress@0.0.994.jsii.tgz"
)

__all__ = [
    "__jsii_assembly__",
]

publication.publish()
