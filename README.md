# Savings Plan Commitment Calculator

This package contains a script to find the usage commitment (measured in $/hour) required to purchase one or more [Savings Plans](https://aws.amazon.com/savingsplans/) given a list of EC2 instances. Those instances should be part of your overall **steady-state usage** as per the Savings Plan's main purpose. Please note, this script doesn’t account for AWS Lambda and AWS Fargate usage. Keep this in mind when calculating your Compute Savings Plan commitment if you use these services.

Note that the script is meant to help finding the proper usage commitment only. It shouldn't be used as a baseline for purchasing new savings plan. Learn more about Compute Savings Plans and EC2 Instance Savings Plans in the [AWS Documentation](https://docs.aws.amazon.com/savingsplans/latest/userguide/what-is-savings-plans.html) and check the recommendations provided in [AWS Cost Explorer](https://console.aws.amazon.com/cost-reports/home?region=us-east-1#/dashboard).

## Usage
There are two ways you can choose to provide the list of EC2 instances. Either 1) automatically using the EC2 APIs from your AWS account or 2) manually filling a csv input file. 

### Option 1: Using the EC2 APIs from your AWS account
The script *calculator_from_ec2api.py* automatically collects the EC2 instances **running** on your AWS Account in the **current Region** using the [describe_instances](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html#) API. You need the required IAM permissions to view all resources in the Amazon EC2 console, you can use the same policy as this [Example: Read-only access](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-policies-ec2-console.html#ex-read-only).
Then, you can just run the script with the following parameters required to the calculator:
- **Tag Key** used to filter your EC2 instances to consider (e.g. *environment*)
- **Tag Value** used to filter your EC2 instances to consider (e.g. *prod*)
- **Savings Plan Type** (possible values: *EC2InstanceSavingsPlans, ComputeSavingsPlans*)
- **Term** (possible values: *1yr, 3yr*)
- **Purchasing Option** (possible values: *No Upfront, Partial Upfront, All Upfront*)

This is an example to find the usage commitment (measured in $/hour) for one or more EC2 Instance Saving Plans (1yr, All Upfront) for your EC2 instances running in the current region with tag key *environment* and tag value *prod* :
 ```bash
    python3 calculator_from_ec2api.py 'environment' 'prod' 'EC2InstanceSavingsPlans' '1yr' 'All Upfront'
```

These are the full steps to execute the script in your AWS Account.

1. Log into your AWS account and select the AWS Region in which your EC2 instances are running

2. Launch [AWS CloudShell](https://console.aws.amazon.com/cloudshell/home) or your local shell (Python 3.10 or newer is required)

3. Clone this source code project using [git](https://git-scm.com/) or download & upload it manually

4. Make sure you have latest pip package installed
    ```bash
    python3 -m ensurepip --upgrade
    ```
5. Install Python [boto3](https://pypi.org/project/boto3/) package
    ```bash
    python3 -m pip install boto3
    ```
6. Run the *calculator_from_ec2api.py* as described above.
    ```bash
    python3 calculator_from_ec2api.py '<Tag Key>' '<Tag Value>' '<Savings Plan Type>' '<Term>' '<Purchasing Option>'
    ```
7. Check the *output.csv* that has been created

### Option 2: Manually filling a csv input file

Fill the *input.csv* file with your instances and place it into the same folder of the *calculator_from_csv.py* script. Each csv row must contain the following data:
- **AWS Region** (e.g. *eu-west-1*)
- **Operating System** (e.g. *SUSE Linux*), for the full list see the column "Platform details" in [this table of the documentation page](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/billing-info-fields.html). Note: the name must match exactly the one in the documentation.
- **Instance Type** (e.g. *m6g.xlarge*)
- **Tenancy** (possible values: *Shared, Dedicated Host, Dedicated Instance*)
- **Number of Instances** (e.g. *7*)
- **Savings Plan Type** (possible values: *EC2InstanceSavingsPlans, ComputeSavingsPlans*)
- **Term** (possible values: *1yr, 3yr*)
- **Purchasing Option** (possible values: *No Upfront, Partial Upfront, All Upfront*)

Run the *calculator_from_csv.py* as described below and check the *output.csv* that has been created.

```bash
python calculator_from_csv.py
```

## Understand the results

Open the *output.csv* file that has been created. For each row of your *input.csv* file you will find two new columns:
- **Savings Plan Rate** based on the configuration provided and according to the [pricing page](https://aws.amazon.com/savingsplans/compute-pricing/)
- **Total Hourly Savings Plans Cost** that is simply **Savings Plan Rate** per **Number of Instances**

Then, you will find a **summary of each Savings Plan to purchase and the Hourly Commitment calculated (measured in $/hour)**.

This is an example of how an *output.csv* looks like:

AWS Region | Operating System | Instance Type | Tenancy | Number of Instances | Savings Plan Type | Term | Purchasing Option | Savings Plan Rate ($) | Total Hourly Savings Plan Cost ($)
| ------------- | ------------- | ----------- | ----------- | ----------- | ----------- | ----- | ----------- | ----------- | ----------- |
eu-south-1 | Red Hat Enterprise Linux | m5.xlarge | Shared | 2 | EC2InstanceSavingsPlans | 3yr | No Upfront | 0.157 | 0.314
eu-central-1 | Red Hat Enterprise Linux | r6i.xlarge | Shared | 2 | ComputeSavingsPlans | 1yr | No Upfront | 0.28025 | 0.5605
eu-central-1 | Red Hat Enterprise Linux | r6i.2xlarge | Shared | 4 | ComputeSavingsPlans | 1yr | No Upfront | 0.5705 | 2.282
eu-central-1 | Red Hat Enterprise Linux | m6i.2xlarge | Shared | 1 | ComputeSavingsPlans | 1yr | No Upfront | 0.48074 | 0.48074
eu-central-1 | Linux/UNIX | m6i.2xlarge | Dedicated Instance | 1 | ComputeSavingsPlans | 3yr | No Upfront | 0.26318 | 0.26318
eu-central-1 | Linux/UNIX | m6idn | Dedicated Host | 1 | ComputeSavingsPlans | 1yr | No Upfront | 10.83 | 10.83
|  |  |  |  |  |  |  |  |  |  |
Summary Savings Plans to purchase: | Hourly Commitment ($) |  |  |  |  |  |  |  |  |  |
EC2InstanceSavingsPlans (3yr - No Upfront); family: m5; region: eu-south-1 | 0.314 |  |  |  |  |  |  |  |  |  |
ComputeSavingsPlans (1yr - No Upfront) | 14.15324 |  |  |  |  |  |  |  |  |  |
ComputeSavingsPlans (3yr - No Upfront) | 0.26318 |  |  |  |  |  |  |  |  |  |


## Requirements
- Python 3.10 or newer
