from aws_cdk import (
    Stack,
    Duration,
    aws_batch as batch,
    aws_ec2 as ec2,
    aws_ecr as ecr,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    Size
)
from constructs import Construct
import aws_cdk as cdk

class BatchStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, properties, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

       # VPC for Fargate Environment
        
        # create a vpc without any Natgateway
        vpc = ec2.Vpc(self, "BatchFargateVPC")


        # Retrieve the ECR repository and image tag
        #ecr_repo = ecr.Repository.from_repository_name(self, "MyECRRepo", "your-ecr-repo-name")
        ecr_repo = properties["ECR_REPO"]
        container_image = ecs.ContainerImage.from_ecr_repository(ecr_repo, "latest")

        # Define IAM Role for Batch Job
        job_role = iam.Role(self, "cdk-batch-vince-JobRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        
        # Create a job policy to access ECR to pull the batch-job image
        job_policy = iam.PolicyStatement(
            actions=["ecr:GetAuthorizationToken", "ecr:BatchCheckLayerAvailability", "ecr:GetDownloadUrlForLayer", "ecr:BatchGetImage", "logs:CreateLogStream", "logs:PutLogEvents"],
            resources=["*"]  # Replace with your ECR repository ARN
        )

        # Grant necessary permissions to the job role
        job_role.add_to_policy(job_policy)

        # Define Fargate Compute Environment
        compute_environment = batch.FargateComputeEnvironment(self, "cdk-batch-vince-FargateComputeEnv",
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            vpc=vpc
        )

        # Define Job Queue
        job_queue = batch.CfnJobQueue(self, "cdk-batch-vince-FargateJobQueue",
            compute_environment_order=[{
                "order": 1,
                "computeEnvironment": compute_environment.compute_environment_name
            }],
            priority=1
        )

        # Define Job Definition 
        job_definition = batch.EcsJobDefinition(self, "MyJobDef",
            container=batch.EcsFargateContainerDefinition(self, "cdk-batch-vince-FargateJobDef",
                image=container_image,
                memory=Size.mebibytes(512),
                cpu=0.25,
                execution_role=job_role
            )
        )

        # Add job queu and definition to the properties for later use
        properties["JobQueue"] = job_queue
        properties["JobDefinition"] = job_definition
        properties["BatchStack"] = self
    

        # Output the Job Queue and definition
        cdk.CfnOutput(self, 'JobQueueArn', value=job_queue.attr_job_queue_arn)
        cdk.CfnOutput(self, 'JobDefinitionArn', value=job_definition.job_definition_arn)

