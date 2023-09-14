# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import csv
import core

# csv input and output files
file_input = open('input.csv')
file_output = open('output.csv', 'w', newline='')

#input reader
csvreader = csv.reader(file_input)
header = next(csvreader)

#output writer
writer = csv.writer(file_output)
header.append("Savings Plan Rate ($)")
header.append("Total Hourly Savings Plan Cost ($)")
writer.writerow(header)

#summary savings plan to purchase
summary_sp = {}

def main_handler():
    #elaborate csv input rows
    for csv_row in csvreader:
        elaborate_item(csv_row)

    #write summary savings plan to purchase
    write_summary()

def elaborate_item(csv_row):
    region_code = csv_row[0]
    usage_operation = core.operation_by_platform_dict[csv_row[1]]
    instance_type = csv_row[2]
    tenancy = csv_row[3]
    n_instances = int(csv_row[4])
    sp_type = csv_row[5]
    term = csv_row[6]
    purchasing_option = csv_row[7]
    instance_family = instance_type.split('.')[0]

    #check parameters
    core.check_input_parameters(usage_operation, tenancy, sp_type, term, purchasing_option)
    
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

file_input.close()
file_output.close()
