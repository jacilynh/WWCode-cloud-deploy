import boto3, botocore
import argparse


def create_ec2_catalog_middleware(aws_cf_client, stack_name, db_hostname, db_user, db_password, db_name, cft_file):
    """
    Creates the ec2 instance that hosts our middleware application
    AMI:
    Keyname:
    """

    cf_parameters = [
        {"ParameterKey": "DBHostName", "ParameterValue": db_hostname},
        {"ParameterKey": "DBUser", "ParameterValue": db_user},
        {"ParameterKey": "DBPassword", "ParameterValue": db_password},
        {"ParameterKey": "DBName", "ParameterValue": db_name},
        {"ParameterKey": "ImageId", "ParameterValue": "ami-e689729e" },
        {"ParameterKey": "KeyName", "ParameterValue": "wwcode"}
    ]
    print(cf_parameters)

    try:
        if _stack_exists(stack_name, aws_cf_client):
            print('Updating {}'.format(stack_name))
            with open(cft_file, 'r') as template:
                response = aws_cf_client.update_stack(
                    StackName=stack_name,
                    TemplateBody=template.read(),
                    Parameters=cf_parameters            
                )
                waiter = aws_cf_client.get_waiter('stack_create_complete')

            waiter = aws_cf_client.get_waiter('stack_update_complete')
        else:
            print('Creating {}'.format(stack_name))
            with open(cft_file, 'r') as template:
                response = aws_cf_client.create_stack(
                    StackName=stack_name,
                    TemplateBody=template.read(),
                    Parameters=cf_parameters,
                    DisableRollback=True
                )
                waiter = aws_cf_client.get_waiter('stack_create_complete')

        print("...waiting for stack to be ready...")
        waiter.wait(StackName=stack_name)
    except botocore.exceptions.ClientError as ex:
        error_message = ex.response['Error']['Message']
        if error_message == 'No updates are to be performed.':
            print("No changes")
        else:
            raise

def _stack_exists(stack_name, aws_cf_client):
    stacks = aws_cf_client.list_stacks()['StackSummaries']
    for stack in stacks:
        if stack['StackStatus'] == 'DELETE_COMPLETE':
            continue
        if stack_name == stack['StackName']:
            return True
    return False

def get_stack_output(aws_cf_client, stack_name):
    describe_stack = aws_cf_client.describe_stacks(StackName=stack_name)
    print(describe_stack)

    stacks = describe_stack["Stacks"]

    out_dict = {}
    for stack in stacks:
        for outputs in stack["Outputs"]:
            out_dict[outputs["OutputKey"]] = outputs["OutputValue"]
    
    return out_dict

def main():    
    parser = argparse.ArgumentParser(description='Deployment Arguments')
    parser.add_argument("--stack_name", help="The Cloud Formation stack name to be created", required=True)
    # parser.add_argument("--db_hostname", help="the mysql host name", required=True)
    parser.add_argument("--db_stack_name", help="The Database stack name. Used for the db hostname.", required=True)
    parser.add_argument("--db_user", help="the mysql user", required=True)
    parser.add_argument("--db_password", help="the mysql password", required=True)
    parser.add_argument("--db_name", help="the mysql db name", required=True)
    args = parser.parse_args()

    stack_name = args.stack_name
    # db_hostname = args.db_hostname
    db_stack_name = args.db_stack_name
    db_user = args.db_user
    db_password = args.db_password
    db_name = args.db_name
 
    parser = argparse.ArgumentParser(description='Deployment Arguments')
    parser.add_argument("--stack_name", help="The Cloud Formation stack name to be created", required=True)
    # parser.add_argument("--db_hostname", help="the mysql host name", required=True)
    parser.add_argument("--db_stack_name", help="The Database stack name. Used for the db hostname.", required=True)
    parser.add_argument("--db_user", help="the mysql user", required=True)
    parser.add_argument("--db_password", help="the mysql password", required=True)
    parser.add_argument("--db_name", help="the mysql db name", required=True)
    args = parser.parse_args()

    stack_name = args.stack_name
    # db_hostname = args.db_hostname
    db_stack_name = args.db_stack_name
    db_user = args.db_user
    db_password = args.db_password
    db_name = args.db_name

    session = boto3.Session(profile_name='workshop', region_name='us-west-2')

    aws_cf_client = session.client('cloudformation')


    # Get the DB Hostname from DB Cloud Formation Stack
    db_stack_output = get_stack_output(aws_cf_client=aws_cf_client, stack_name=db_stack_name)
    
    print(db_stack_output)

    # Get the database hostname created by cloudformation
    db_hostname = db_stack_output.get("RDSEndpoint")

    create_ec2_catalog_middleware(aws_cf_client=aws_cf_client, 
        stack_name=stack_name, 
        db_hostname=db_hostname,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
        cft_file="catalog-middleware.yaml")

if __name__ == '__main__':
    main()
