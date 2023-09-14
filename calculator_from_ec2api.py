# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import csv
import core
import boto3
import sys

# csv output file
file_output = open('output.csv', 'w', newline='')

#output writer
writer = csv.writer(file_output)
header = ["AWS Region","Operating System","Instance Type","Tenancy","Number of Instances","Savings Plan Type","Term","Purchasing Option","Savings Plan Rate ($)","Total Hourly Savings Plan Cost ($)"]
writer.writerow(header)

#summary savings plan to purchase
summary_sp = {}

ec2_client = boto3.client('ec2')

#input parameters
tag_name = sys.argv[1]
tag_value = sys.argv[2]
sp_type = sys.argv[3]
term = sys.argv[4]
purchasing_option = sys.argv[5]

def main_handler():
    response_ec2 = ec2_client.describe_instances(
        Filters=[
            {
                'Name': 'tag:' + tag_name,
                'Values': [
                    tag_value
                ]
            }
        ],
    )

    #elaborate instances from EC2 API response
    reservations = response_ec2['Reservations']
    for reservation in reservations:
        instances = reservation['Instances']
        for instance in instances:
            # filter only running instances
            if (instance['State']['Code'] == 16):
                elaborate_item(instance)

    #write summary savings plan to purchase
    write_summary()


def elaborate_item(instance):
    #last char removed to get the region
    region_code = instance['Placement']['AvailabilityZone'][:-1]
    usage_operation = instance['UsageOperation']
    os = instance['PlatformDetails']
    instance_type = instance['InstanceType']
    tenancy = core.tenancy_dict[instance['Placement']['Tenancy']]
    n_instances = 1 #fixed to 1
    instance_family = instance_type.split('.')[0]

    #check parameters
    core.check_input_parameters(usage_operation, tenancy, sp_type, term, purchasing_option)
    
    csv_row = [region_code, os, instance_type, tenancy, n_instances, sp_type, term, purchasing_option]
    
    sp_rate = core.get_savings_plan_rate(region_code, usage_operation, instance_family, instance_type, tenancy, sp_type, term, purchasing_option)
    csv_row.append(sp_rate)

    total_hourly_rate = sp_rate * n_instances
    csv_row.append(total_hourly_rate)
    
    writer.writerow(csv_row)

    # savings plan description for summary
    if (sp_type == "ComputeSavingsPlans"):
        sp_description = sp_type + " (" + term + " - " + purchasing_option + ")"
    else: # EC2 Instance Savings plan case
        sp_description = sp_type + " (" + term + " - " + purchasing_option + "); family: " + instance_family + "; region: " + region_code

    # register commitment for the summary
    if (sp_description not in summary_sp):
        summary_sp[sp_description] = total_hourly_rate
    else:
        summary_sp[sp_description] += total_hourly_rate

def write_summary():
    writer.writerow([]) #empty row as separator
    writer.writerow(["Summary Savings Plans to purchase:", "Hourly Commitment ($)"])
    for sp_description in summary_sp:
        writer.writerow([sp_description, summary_sp[sp_description]])

main_handler()

print("COMPLETED SUCCESSFULLY")

file_output.close()
