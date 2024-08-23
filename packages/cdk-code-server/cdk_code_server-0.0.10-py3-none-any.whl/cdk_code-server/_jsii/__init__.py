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
import cdk_preinstalled_amazon_linux_ec2._jsii
import constructs._jsii
import open_constructs_aws_cdk._jsii

__jsii_assembly__ = jsii.JSIIAssembly.load(
    "cdk-code-server", "0.0.10", __name__[0:-6], "cdk-code-server@0.0.10.jsii.tgz"
)

__all__ = [
    "__jsii_assembly__",
]

publication.publish()
