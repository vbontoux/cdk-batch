#!/usr/bin/env python3

import aws_cdk as cdk

from cdk_batch.cdk_batch_stack import CdkBatchStack
from cdk_batch.cdk_container_pipeline import EcrPipelineStack


app = cdk.App()
EcrPipelineStack(app, "EcrPipelineStack")

#CdkBatchStack(app, "CdkBatchStack")
app.synth()
