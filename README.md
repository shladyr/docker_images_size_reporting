# Docker Image Size Reporter

## Overview

This Python script provides functionality to authenticate with AWS Elastic Container Registry (ECR), <br/>
check Read permissions, find all docker image repositories with tag "latest" and <br/>
report the sizes of Docker images in specified repositories.

## Requirements, Prerequisites

- Python 3
- AWS Access Key and Secret Key with necessary permissions for ECR
- boto3 library
- tabulate library

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/shladyr/docker_images_size_reporting.git
    ```

## Execution, Usage

To run the script, execute the following command in the terminal:
```commandline
python3 get_docker_images_size.py ${AWS_ACCESS_KEY_ID} ${AWS_SECRET_ACCESS_KEY}
```

## Command-line Arguments

- `aws_access_key`: AWS Access Key for authentication.
- `aws_secret_key`: AWS Secret Key for authentication.

## Example of OUTPUT

![ecr_docker_size.png](doc%2Fecr_docker_size.png)

## References

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr/client/describe_images.html
- https://boto3.amazonaws.com/v1/documentation/api/1.26.83/reference/services/ecr/client/describe_repositories.html
- https://pypi.org/project/tabulate/

## Important Note

Beginning with Docker version 1.9, the Docker client compresses image layers <br/> 
before pushing them to a V2 Docker registry. The output of the docker images command <br/>
shows the uncompressed image size, so it may return a larger image size than <br/> 
the image sizes returned by DescribeImages. <br/>
See https://docs.aws.amazon.com/cli/latest/reference/ecr/describe-images.html

## Diagram by pyfactor

![Image_pyfactor.svg](doc%2FImage_pyfactor.svg)

## Diagram by code2flow

![Image_code2flow.png](doc%2FImage_code2flow.png)