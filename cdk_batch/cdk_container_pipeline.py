from aws_cdk import (
    core as cdk,
    aws_ecr as ecr,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_secretsmanager as secretsmanager,
)

class EcrPipelineStack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 1. Create an ECR repository
        ecr_repository = ecr.Repository(self, 'MyEcrRepo',
                                        repository_name='my-ecr-repo')

        # 2. Create a CodeBuild project for building the Docker image
        codebuild_project = codebuild.PipelineProject(self, 'DockerBuildProject',
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
                            'docker build -t my-ecr-repo .',
                            f'docker tag my-ecr-repo:latest {ecr_repository.repository_uri}:latest'
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
        github_token = secretsmanager.Secret.from_secret_name_v2(self, "GitHubToken", "github-token")

        source_action = codepipeline_actions.GitHubSourceAction(
            action_name="GitHub_Source",
            owner="<GITHUB_OWNER>",  # Replace with your GitHub username
            repo="<GITHUB_REPO>",    # Replace with your repository name
            branch="main",           # Replace with your repository branch
            oauth_token=cdk.SecretValue.secrets_manager("github-token"),  # OAuth token from Secrets Manager
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

