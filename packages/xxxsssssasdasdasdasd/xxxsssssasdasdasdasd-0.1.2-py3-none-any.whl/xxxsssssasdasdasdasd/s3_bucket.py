from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    aws_s3 as s3,
    RemovalPolicy,
    Duration,
    aws_iam as iam,
    App
)
from constructs import Construct

def validate_bucket_props(**kwargs):
        # List of properties that cannot be overridden
        prohibited_keys = ["versioned", "block_public_access", "encryption", "enforce_ssl"]

        # Check if any prohibited keys are in kwargs
        for key in prohibited_keys:
            if key in kwargs:
                raise ValueError(f"The property '{key}' cannot be overridden in CompliantS3Bucket.")
        
        # Ensure bucket_name follows naming conventions
        if "bucket_name" not in kwargs:
            raise ValueError("Must specify a bucket name")
        
        bucket_name = kwargs["bucket_name"]
        if "dino" not in bucket_name:
            raise ValueError("Invalid bucket name")

class BucketCompliant(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)

        validate_bucket_props(**kwargs)

        # Define the S3 bucket with security best practices
        self.bucket = s3.Bucket(self, "CompliantBucket",
            versioned=True, # Enforce versioning
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,  # Block all public access
            encryption=s3.BucketEncryption.S3_MANAGED,  # Enable S3 managed encryption
            enforce_ssl=True,  # Enforce SSL
            removal_policy=RemovalPolicy.DESTROY,  # Keep the bucket when stack is deleted
            **kwargs
        )

    def grant_read_write(self, grantee: iam.IGrantable):
        """Grant read/write permissions to the bucket."""
        self.bucket.grant_read_write(grantee)

    def grant_read(self, grantee: iam.IGrantable):
        """Grant read-only permissions to the bucket."""
        self.bucket.grant_read(grantee)

    def grant_write(self, grantee: iam.IGrantable):
        """Grant write-only permissions to the bucket."""
        self.bucket.grant_write(grantee)

# class CdkPyStack(Stack):

#     def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)

#         # The code that defines your stack goes here
#         bucket = BucketCompliant(
#             self, 
#             "Bucket",
#             bucket_name="dino-my-first-cdk-bucket",
#             lifecycle_rules=[
#                 s3.LifecycleRule(
#                     id="ExpirationRule",
#                     expiration=Duration.days(2),
#                     abort_incomplete_multipart_upload_after=Duration.days(7),
#                 )
#             ],
#         )

#         bucket.grant_read_write(iam.AccountRootPrincipal())


# # Create an instance of the CDK app
# app = App()

# # Instantiate the stack
# stack = CdkPyStack(app, "CdkPyStack")

# # Synthesize the stack to CloudFormation template
# synth_output = app.synth()

# # If you want to access the synthesized CloudFormation template
# # print(synth_output.get_stack(stack.stack_name).template)

# print(synth_output.get_stack_by_name(stack.stack_name).template)