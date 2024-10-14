#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_batch.cdk_batch_stack import BatchStack
from cdk_batch.cdk_container_pipeline import EcrPipelineStack
from cdk_batch.cdk_secret_manager import SecretManagerStack

properties = { "stack": "cdk-batch-"}

app = cdk.App()

SecretManagerStack(app, "SecretManagerStack", properties)

EcrPipelineStack(app, "EcrPipelineStack", properties)

#BatchStack(app, "CdkBatchStack")

app.synth()
