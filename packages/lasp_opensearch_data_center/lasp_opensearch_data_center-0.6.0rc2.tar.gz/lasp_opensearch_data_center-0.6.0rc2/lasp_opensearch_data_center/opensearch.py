"""Open Search Stack"""
# Standard
from pathlib import Path
# Installed
from constructs import Construct
from aws_cdk import (
    CfnResource,
    Environment,
    Duration,
    aws_opensearchservice as opensearch,
    aws_ec2 as ec2,
    aws_route53 as route53,
    RemovalPolicy,
    aws_certificatemanager as acm,
    aws_iam as iam,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_events as events,
    aws_events_targets as targets,
    aws_ecr_assets as ecr_assets
)


class OpenSearchConstruct(Construct):
    """OpenSearch cnostruct to create the Open Search Domain

    NOTE: This construct takes ~20-40 minutes to deploy/destroy the OpenSearch service.
    Access to the website GUI is available via https://search.{account_type}.{domain_name}/_dashboards/app/home#/

    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        environment: Environment,
        hosted_zone: route53.HostedZone,
        certificate: acm.Certificate,
        vpc: ec2.Vpc,
        opensearch_snapshot_bucket: s3.Bucket,
        opensearch_instance_type: str,
        opensearch_version: str,
        opensearch_zone_awareness: opensearch.ZoneAwarenessConfig,
        opensearch_node_count: str,
        opensearch_domain_name: str,
        opensearch_ip_access_range: str,
        snapshot_repo_name="snapshot-repo-1",
        docker_context_path=str((Path(__file__).parent / "lambda").absolute())
    ) -> None:
        """Construct init

        :param scope:
        :param construct_id:
        :param environment: Environment
            AWS environment
        :param hosted_zone: route53.HostedZone
            Hosted zone to host the OpenSearch instance
        :param certificate: acm.Certificate
            Cert for OpenSearch
        :param vpc:
            VPC in which to put the OpenSearch instance
        :param opensearch_snapshot_bucket: s3.Bucket
            S3 bucket in which to store periodic snapshots
        :param opensearch_instance_type:
            EC2 instance type on which to run OpenSearch (needs pretty significant resources)
        :param opensearch_version:
            Version of OS to deploy
        :param opensearch_zone_awareness:
        :param opensearch_node_count:
        :param opensearch_domain_name:
            Name of opensearch domain
        :param opensearch_ip_access_range:
            IP block on which to allow OpenSearch access (for security purposes)
        :param snapshot_repo_name: str
            Nome of the snapshot repository (used by OpenSearch to write the snapshot)
        :param docker_context_path: str, Optional
            Custom location in which to find a Dockerfile defining a target called `snapshot-lambda`. This construct
            provides a sensible default that takes a snapshot without doing anything fancy.
        """
        super().__init__(scope, construct_id)

        sg_opensearch_cluster = ec2.SecurityGroup(
            self,
            "OpenSearchSG",
            vpc=vpc,
            allow_all_outbound=True,
            description="security group for the opensearch cluster",
            security_group_name="opensearch-cluster-sg",
        )

        sg_opensearch_cluster.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            connection=ec2.Port.all_tcp(),
            description="Open all IPs for testing",
        )

        service_linked_role = CfnResource(
            self,
            "opensearch-service-linked-role",
            type="AWS::IAM::ServiceLinkedRole",
            properties={
                "AWSServiceName": "es.amazonaws.com",
                "Description": "Role for OpenSearch to access resources in the VPC",
            },
        )

        self.domain = opensearch.Domain(
            self,
            "OpenSearchDomain",
            domain_name=opensearch_domain_name,
            # AWS supports 2.3 as of 11/16/22
            # TODO: We may want this to be different in DEV vs PROD
            # Also there are upgrade paths that need to be followed
            # that may be different in DEV vs PROD
            version=opensearch.EngineVersion.open_search(opensearch_version),
            # Define the EC2 instances/nodes
            # Supported EC2 instance types:
            # https://docs.aws.amazon.com/opensearch-service/latest/developerguide/supported-instance-types.html
            capacity=opensearch.CapacityConfig(
                # Num of nodes/instances, for prod should be 1:1 with number of shards created for the indexes
                data_nodes=int(opensearch_node_count),
                # m6g is 2vCPU and 8GB RAM - $100/month per data node
                data_node_instance_type=opensearch_instance_type,
            ),
            # 10GB is the minimum size
            ebs=opensearch.EbsOptions(
                volume_size=50,
                volume_type=ec2.EbsDeviceVolumeType.GP3,
            ),
            # Enable logging
            logging=opensearch.LoggingOptions(
                slow_search_log_enabled=True,
                app_log_enabled=True,
                slow_index_log_enabled=True,
            ),
            # Enable encryption
            node_to_node_encryption=True,
            encryption_at_rest=opensearch.EncryptionAtRestOptions(enabled=True),
            # Require https connections
            enforce_https=True,
            # Use our custom domain name in the endpoint
            # This will autogenerate our CNAME record
            custom_endpoint=opensearch.CustomEndpointOptions(
                domain_name=f"search.{hosted_zone.zone_name}",
                hosted_zone=hosted_zone,
                certificate=certificate,
            ),
            # Destroy OS with cdk destroy
            removal_policy=RemovalPolicy.DESTROY,
            # Option to put the domain within an account VPC, restrictions listed in header
            # vpc=vpc,
            # # If running a single node need to specify a single subnet
            # vpc_subnets=[
            #     ec2.SubnetSelection(
            #         subnets=[vpc.public_subnets[0]],
            #     ),
            # ],
            # Provide end user access to the service
            security_groups=[sg_opensearch_cluster],
            # Amazon ES will distribute the nodes and shards across multiple Availability Zones
            # in the region to increase availability.
            zone_awareness=opensearch_zone_awareness,
        )

        # Add the service linked role as a dependency to the domain (i.e. role must exist first)
        self.domain.node.add_dependency(service_linked_role)

        # Define access policies and restrict to specified IPs
        self.domain.add_access_policies(
            iam.PolicyStatement(
                principals=[iam.AnyPrincipal()],
                actions=["es:*"],
                resources=[f"{self.domain.domain_arn}/*"],
                conditions={"IpAddress": {"aws:SourceIp": opensearch_ip_access_range}},
            )
        )

        #################### Create resources for manual snapshots ####################

        # S3 bucket to store the snapshot data
        # The data is stored in native Lucene format
        # TODO: Determine lifecycle policy, retention on snapshots, for now indefinite
        self.opensearch_snapshot_bucket = opensearch_snapshot_bucket

        # OS principal that allows the service to assume roles
        opensearch_principal = iam.PrincipalWithConditions(
            principal=iam.ServicePrincipal(
                "es.amazonaws.com",
            ),
            conditions={
                "StringEquals": {"aws:SourceAccount": environment.account},
                "ArnLike": {"aws:SourceArn": self.domain.domain_arn},
            },
        )

        # IAM role/policy for the OS domain service to assume
        self.opensearch_snapshot_role = iam.Role(
            self,
            "Role",
            role_name="opensearch_snapshot_role",
            assumed_by=opensearch_principal,
            description="Role OpenSearch assumes to write snapshots to S3 buckets",
        )

        # Policy to allow S3 access to put the new snapshots
        opensearch_snapshot_policy = iam.ManagedPolicy(
            self,
            "opensearch_snapshot_policy",
            description="CI CD automated data policy",
            managed_policy_name="opensearch_snapshot_policy",
            roles=[
                self.opensearch_snapshot_role,
            ],
            statements=[
                iam.PolicyStatement(
                    # Permission to list all S3 buckets
                    effect=iam.Effect.ALLOW,
                    actions=["s3:ListBucket"],
                    resources=[
                        f"{self.opensearch_snapshot_bucket.bucket_arn}",
                    ],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                    resources=[
                        f"{self.opensearch_snapshot_bucket.bucket_arn}/*",
                    ],
                ),
            ],
        )

        docker_image_code = lambda_.DockerImageCode.from_image_asset(
            directory=docker_context_path,
            target="snapshot-lambda",
            platform=ecr_assets.Platform.LINUX_AMD64
        )

        snapshot_lambda = lambda_.DockerImageFunction(
            self,
            "SnapshotLambda",
            code=docker_image_code,
            environment={
                # The snapshot process requires the full API HTTP endpoint
                "OPEN_SEARCH_ENDPOINT": f"https://{self.domain.domain_endpoint}/",
                "SNAPSHOT_S3_BUCKET": self.opensearch_snapshot_bucket.bucket_name,
                "SNAPSHOT_ROLE_ARN": self.opensearch_snapshot_role.role_arn,
                "SNAPSHOT_REPO_NAME": snapshot_repo_name,
            },
            timeout=Duration.seconds(60 * 15),
            memory_size=512,
            retry_attempts=0,
        )

        # Add permissions for Lambda to access OpenSearch
        snapshot_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["es:*"],
                resources=[f"{self.domain.domain_arn}/*"],
            )
        )

        # PassRole allows services to assign AWS roles to resources and services in this account
        # The OS snapshot role is invoked within the Lambda to interact with OS, it is provided to
        # lambda via an Environmental variable in the lambda definition
        snapshot_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["iam:PassRole"],
                resources=[self.opensearch_snapshot_role.role_arn],
            )
        )

        # An Event to trigger the lambda 1X daily, runs every day at 9AM UTC
        # See https://docs.aws.amazon.com/lambda/latest/dg/tutorial-scheduled-events-schedule-expressions.html
        snapshot_lambda_event_rule = events.Rule(
            self,
            "Rule",
            rule_name="SnapshotLambdaScheduler",
            description="Scheduler to trigger the OpenSearch Lambda snapshot function",
            schedule=events.Schedule.cron(
                minute="0", hour="9", month="*", week_day="*", year="*"
            ),
        )
        snapshot_lambda_event_rule.add_target(targets.LambdaFunction(snapshot_lambda))
