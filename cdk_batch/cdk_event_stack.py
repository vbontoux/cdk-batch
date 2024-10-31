from aws_cdk import (
    Stack,
    Duration,
    aws_batch as batch,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct
import aws_cdk as cdk

class EventStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, properties, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        job_queue = properties["JobQueue"]
        job_definition = properties["JobDefinition"]
        batch_stack = properties["BatchStack"]

        # Create a rule to trigger the Batch Job defined in the Batch Stack
        rule = events.Rule(
            self, 
            "BatchJobScheduleRule",
            schedule=events.Schedule.rate(Duration.minutes(2))
        )


        rule.add_target(
            targets.BatchJob(
                job_queue_arn=job_queue.attr_job_queue_arn,
                job_definition_arn=job_definition.job_definition_arn,
                job_name="cdk-batch-vince-ScheduledFargateBatchJob",
                job_queue_scope=batch_stack,
                job_definition_scope=batch_stack,

                # batch_job_props=batch.CfnJob.BatchJobPropsProperty(
                #     container_overrides=batch.CfnJob.ContainerOverridesProperty(
                #         environment=[
                #             batch.CfnJob.EnvironmentVariableProperty(name="BATCH_JOB_DURATION", value=60)
                #         ]
                #     )
                # )
                
                # batch_job_props=batch.JobOverrides(
                #     container_overrides=batch.ContainerOverrides(
                #         environment=[
                #             batch.CfnJob.EnvironmentVariableProperty(
                #                 name="BATCH_JOB_DURATION",
                #                 value=60
                #             )
                #         ]
                #     )
                # )
            )
        )