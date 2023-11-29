#!/usr/local/bin/python3

import argparse
import boto3
import logging
import sys
from tabulate import tabulate

class AwsEcrAuthenticator:
    def __init__(self, aws_access_key=None, aws_secret_key=None):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.ecr_client = None

    def configure_logging(self):
        logging.basicConfig(
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    def read_aws_credentials(self):
        try:
            parser = argparse.ArgumentParser(description='AWS ECR Authenticator')
            parser.add_argument('aws_access_key', help='AWS Access Key')
            parser.add_argument('aws_secret_key', help='AWS Secret Key')
            args = parser.parse_args()
            return args.aws_access_key, args.aws_secret_key
        except Exception as e:
            logging.error(f'Error reading AWS credentials: {e}')
            sys.exit(1)

    def authenticate_to_aws_ecr(self):
        try:
            self.configure_logging()
            logging.info('Authenticating to AWS ECR...')
            ecr_client = boto3.client(
                'ecr',
                region_name="us-west-2",
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )
            logging.info('Successfully authenticated to AWS ECR')
            return ecr_client
        except Exception as e:
            logging.error(f'Error authenticating to AWS ECR: {e}')
            sys.exit(1)

    def check_read_permissions_to_aws_ecr(self, repository_name='project/application', tag='latest'):
        try:
            logging.info(f'Checking Read permissions to AWS ECR by pulling "{repository_name}:{tag}" image...')

            # Pulling the image to check permissions
            self.ecr_client.batch_check_layer_availability(
                repositoryName=repository_name,
                layerDigests=[f'sha256:{tag}']
            )

            logging.info('Read permissions to AWS ECR verified')
        except Exception as e:
            logging.error(f'Error checking Read permissions to AWS ECR: {e}')
            sys.exit(1)


class DockerImageSizeReporter:
    def __init__(self, ecr_client):
        self.ecr_client = ecr_client
        self.image_sizes = {}  # Dictionary to store image sizes

    def get_list_of_all_repositories(self):
        try:
            logging.info('Getting list of all Aws ECR repositories...')
            repositories = self.ecr_client.describe_repositories()['repositories']
            repository_names = [repository['repositoryName'] for repository in repositories]
            logging.info(f'List of Aws ECR repositories: {repository_names}')
            return repository_names
        except Exception as e:
            logging.error(f'Error getting list of Aws ECR repositories: {e}')
            sys.exit(1)

    def get_size_of_docker_image(self, repository_name):
        try:
            logging.info(f'Getting size of Docker image in repository: {repository_name}...')
            images = self.ecr_client.describe_images(repositoryName=repository_name)['imageDetails']

            for image in images:
                # Check if the image has the tag "latest"
                if 'latest' in image.get('imageTags', []):
                    image_size_bytes = image.get('imageSizeInBytes', 0)
                    image_size_gb = image_size_bytes / (1024 ** 3)  # Convert bytes to gigabytes (Gb)
                    image_name = f"{repository_name}:{image['imageTags'][0]}"

                    # Store image name and size in the dictionary
                    self.image_sizes[image_name] = image_size_gb

        except Exception as e:
            logging.error(f'Error getting size of Docker images: {e}')
            sys.exit(1)

    def build_table_top_size_report(self):
        try:
            logging.info('Building table of top Docker image sizes...')
            # Sort rows by size from higher to lower
            sorted_table_data = sorted(self.image_sizes.items(), key=lambda x: x[1], reverse=True)

            # Display the table
            table_headers = ["Docker Image Name", "Docker Image Size (GB)"]
            logging.info(tabulate(sorted_table_data, headers=table_headers, tablefmt="grid"))

        except Exception as e:
            logging.error(f'Error building table of Docker image sizes: {e}')
            sys.exit(1)


def main():
    # Read AWS credentials
    aws_access_key, aws_secret_key = AwsEcrAuthenticator().read_aws_credentials()

    # Authenticate to AWS ECR
    aws_ecr_authenticator = AwsEcrAuthenticator(aws_access_key, aws_secret_key)
    aws_ecr_authenticator.ecr_client = aws_ecr_authenticator.authenticate_to_aws_ecr()

    # Check Read permissions to AWS ECR
    aws_ecr_authenticator.check_read_permissions_to_aws_ecr()

    # Instantiate DockerImageSizeReporter
    docker_image_size_reporter = DockerImageSizeReporter(aws_ecr_authenticator.ecr_client)

    # Get list of all repositories
    repositories = docker_image_size_reporter.get_list_of_all_repositories()

    # Get size of all Docker images in each repository
    for repository in repositories:
        docker_image_size_reporter.get_size_of_docker_image(repository)

    # Build and display the table of top Docker image sizes
    docker_image_size_reporter.build_table_top_size_report()

if __name__ == "__main__":
    main()
