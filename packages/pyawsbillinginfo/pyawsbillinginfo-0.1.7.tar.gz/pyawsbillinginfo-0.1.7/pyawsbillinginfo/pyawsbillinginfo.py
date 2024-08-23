import os

import boto3
import csv
import configargparse
from datetime import datetime, timedelta
from dateutil.parser import parse

def get_billing_data(client, start_date, end_date, granularity):
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity=granularity,  # DAILY, MONTHLY, or HOURLY
        Metrics=['UnblendedCost'],  # You can add more metrics if needed
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            },
        ]
    )
    return response['ResultsByTime']


def write_to_csv(data, filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['TimePeriod', 'Service', 'Amount', 'Unit'])

        for time_period in data:
            for group in time_period['Groups']:
                writer.writerow([
                    time_period['TimePeriod']['Start'],
                    group['Keys'][0],
                    group['Metrics']['UnblendedCost']['Amount'],
                    group['Metrics']['UnblendedCost']['Unit']
                ])


def get_date_string(date, granularity):
    if granularity == 'HOURLY':
        return date.strftime('%Y-%m-%dT%H:00:00Z')
    else:
        return date.strftime('%Y-%m-%d')


def main(start_date, end_date, filename, region, granularity, profile):
    # Initialize the Cost Explorer client
    session = boto3.Session(profile_name=profile)
    client = session.client('ce', region_name=region)

    # Get billing data
    billing_data = get_billing_data(client, start_date, end_date, granularity)

    # Write to CSV
    write_to_csv(billing_data, filename)

    print(
        f"Billing data from {start_date} to {end_date} with granularity '{granularity}' has been written to {filename}")


def aws_billing_info():

    # Set up argument parsing
    home_dir = os.path.expanduser("~")
    conf_file = 'pyawsbillinginfo.conf'
    parser = configargparse.ArgumentParser(description="Extract AWS billing data into a CSV file.",
                                           default_config_files=[f'{conf_file}',
                                                                 f'{home_dir}/{conf_file}'])

    # Default dates: last month
    default_end_date = datetime.today().date()
    default_start_date = (datetime.today().date() - timedelta(days=30))

    parser.add_argument('--start-date', type=parse, default=default_start_date,
                        help=f'Start date for the billing data (default: {default_start_date})')
    parser.add_argument('--end-date', type=parse, default=default_end_date,
                        help=f'End date for the billing data in(default: {default_end_date})')
    parser.add_argument('--filename', type=str, default='aws_billing_data.csv',
                        help='Output CSV filename (default: aws_billing_data.csv)')
    parser.add_argument('--region', type=str, default='eu-west-1',
                        help='AWS region for Cost Explorer (default: eu-west-1)')
    parser.add_argument('--granularity', type=str, choices=['DAILY', 'MONTHLY', "HOURLY"], default='DAILY',
                        help='Granularity of the billing data: DAILY or MONTHLY (default: MONTHLY)')
    parser.add_argument('--profile', type=str, default='default', help='AWS profile name (default: pybilling)')

    args = parser.parse_args()

    start_date = get_date_string(args.start_date, args.granularity)
    end_date = get_date_string(args.end_date, args.granularity)
    # Run the main function with parsed arguments
    if args.granularity == "HOURLY":
        print("HOURLY granularity must be enabled in the AWS Cost Explorer settings")
        print("and only allows the last 14 days of data to be retrieved")
        if args.end_date - args.start_date > timedelta(days=14):
            print("Please use a start date that is less 14 days before the end date fro HOURLY granularity")
            exit(1)

    print(f"AWS Billing statement:")
    print(f"region      : {args.region}")
    print(f"Granularity : {args.granularity}")
    print(f"start date  : {start_date} ")
    print(f"end date    : {end_date}")
    print(f"Duration    : {args.end_date - args.start_date}")

    start_date = get_date_string(args.start_date, args.granularity)
    end_date = get_date_string(args.end_date, args.granularity)
    main(start_date, end_date, args.filename, args.region, args.granularity, args.profile)


if __name__ == "__main__":
    aws_billing_info()
