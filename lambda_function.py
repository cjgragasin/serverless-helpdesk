import boto3
import json
import uuid
from datetime import datetime

# Configuration
REGION = 'ap-southeast-1'
TABLE_NAME = 'helpdesk-tickets'
SNS_TOPIC_ARN = 'arn:aws:sns:ap-southeast-1:339712921454:helpdesk-notifications'  # We'll fill this later

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', region_name=REGION)
    sns = boto3.client('sns', region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)
    
    # Parse the incoming request body
    body = json.loads(event['body'])
    
    # Generate unique ticket ID
    ticket_id = str(uuid.uuid4())[:8].upper()
    timestamp = datetime.now().isoformat()
    
    # Save ticket to DynamoDB
    ticket = {
        'ticket_id': ticket_id,
        'name': body['name'],
        'email': body['email'],
        'issue_type': body['issue_type'],
        'description': body['description'],
        'status': 'OPEN',
        'created_at': timestamp
    }
    
    table.put_item(Item=ticket)
    print(f"✅ Ticket {ticket_id} saved to DynamoDB")
    
    # Send email notification via SNS
    message = f"""
    New IT Helpdesk Ticket Created!
    
    Ticket ID: {ticket_id}
    Name: {body['name']}
    Email: {body['email']}
    Issue Type: {body['issue_type']}
    Description: {body['description']}
    Status: OPEN
    Created At: {timestamp}
    """
    
    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"New Helpdesk Ticket #{ticket_id}",
        Message=message
    )
    print(f"✅ Email notification sent for ticket {ticket_id}")
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'Ticket created successfully!',
            'ticket_id': ticket_id
        })
    }