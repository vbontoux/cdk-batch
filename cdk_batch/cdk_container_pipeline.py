from aws_cdk import (
    aws_ecr as ecr,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,

)
from constructs import Construct
import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from aws_cdk import aws_iam as iam


class EcrPipelineStack(cdk.Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
    
        # Get the current region
        region = self.region

        # You can now use `region` in your resources or outputs
        print(f"Deploying in region: {region}")

        # 1. Create an ECR repository
        ecr_repository = ecr.Repository(self, 'MyBatchJobRepo',
                                        repository_name='batch-job',
                                        removal_policy=cdk.RemovalPolicy.DESTROY)

        # 2. Create a CodeBuild project for building the Docker image

        # first create a role for codebuild that allows access to ECR to push images to a repository
        codebuild_role = iam.Role(self, 'CodeBuildRole',
            assumed_by=iam.ServicePrincipal('codebuild.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ContainerRegistryPowerUser')
            ]
        )

        codebuild_project = codebuild.PipelineProject(self, 'DockerBuildProject',
            role=codebuild_role,
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0, # Latest standard image with Docker support
                privileged=True  # Required for Docker builds
            ),
            build_spec=codebuild.BuildSpec.from_object({
                'version': '0.2',
                'phases': {
                    'pre_build': {
                        'commands': [
                            'echo Logging in to Amazon ECR...',
                            f'aws ecr get-login-password --region {self.region} | docker login --username AWS --password-stdin {ecr_repository.repository_uri}'
                        ]
                    },
                    'build': {
                        'commands': [
                            'echo Build started on `date`',
                            'echo Building the Docker image...',
                            'cd batch_job',
                            'docker build -t batch-job .',
                            f'docker tag batch-job:latest {ecr_repository.repository_uri}:latest'
                        ]
                    },
                    'post_build': {
                        'commands': [
                            'echo Pushing the Docker image...',
                            f'docker push {ecr_repository.repository_uri}:latest',
                            'echo Build completed on `date`'
                        ]
                    }
                },
                'artifacts': {
                    'files': '**/*'
                }
            })
        )

        # 3. Source action: GitHub source
        source_output = codepipeline.Artifact()

        # GitHub access token stored in AWS Secrets Manager
        # github_token = secretsmanager.Secret.from_secret_name_v2(self, "GitHubToken", "github-token")
        # secret_value = cdk.SecretValue.unsafe_plain_text("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")
        secret_value = cdk.SecretValue.unsafe_plain_text("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")

        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="vbontoux",  # Replace with your GitHub username
            repo="cdk-batch",    # Replace with your repository name
            branch="main",           # Replace with your repository branch
            #oauth_token=cdk.SecretValue.secrets_manager("github-token"), 
            oauth_token=secret_value,
            output=source_output
        )

        # 4. Build action: CodeBuild project
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Docker_Build",
            project=codebuild_project,
            input=source_output
        )

        # 5. Create the CodePipeline
        pipeline = codepipeline.Pipeline(self, "MyPipeline",
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[source_action]
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[build_action]
                )
            ]
        )

        # Output the ECR repository URI
        cdk.CfnOutput(self, 'EcrRepoUri', value=ecr_repository.repository_uri)

