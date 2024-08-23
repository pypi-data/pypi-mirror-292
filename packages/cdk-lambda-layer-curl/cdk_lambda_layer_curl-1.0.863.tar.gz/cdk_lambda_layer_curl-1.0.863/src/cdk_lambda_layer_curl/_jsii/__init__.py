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

import aws_cdk.aws_lambda._jsii
import aws_cdk.core._jsii
import constructs._jsii

__jsii_assembly__ = jsii.JSIIAssembly.load(
    "cdk-lambda-layer-curl",
    "1.0.863",
    __name__[0:-6],
    "cdk-lambda-layer-curl@1.0.863.jsii.tgz",
)

__all__ = [
    "__jsii_assembly__",
]

publication.publish()
