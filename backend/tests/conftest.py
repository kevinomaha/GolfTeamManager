import os
import pytest
import boto3
import json
from moto import mock_dynamodb

# Constants for test data
TEST_REGION = 'us-east-1'
PLAYER_TABLE = 'GolfLeague-Players-Test'
SCHEDULE_TABLE = 'GolfLeague-Schedules-Test'
SWAP_REQUEST_TABLE = 'GolfLeague-SwapRequests-Test'
SCORE_TABLE = 'GolfLeague-Scores-Test'

@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for boto3."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = TEST_REGION

@pytest.fixture(scope='function')
def dynamodb(aws_credentials):
    """DynamoDB mock fixture."""
    with mock_dynamodb():
        yield boto3.resource('dynamodb', region_name=TEST_REGION)

@pytest.fixture(scope='function')
def setup_dynamodb_tables(dynamodb):
    """Set up DynamoDB tables for testing."""
    # Create Player table
    dynamodb.create_table(
        TableName=PLAYER_TABLE,
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'email', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'EmailIndex',
                'KeySchema': [
                    {'AttributeName': 'email', 'KeyType': 'HASH'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Create Schedule table
    dynamodb.create_table(
        TableName=SCHEDULE_TABLE,
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'date', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'DateIndex',
                'KeySchema': [
                    {'AttributeName': 'date', 'KeyType': 'HASH'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Create SwapRequest table
    dynamodb.create_table(
        TableName=SWAP_REQUEST_TABLE,
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'requestorId', 'AttributeType': 'S'},
            {'AttributeName': 'targetId', 'AttributeType': 'S'},
            {'AttributeName': 'status', 'AttributeType': 'S'},
            {'AttributeName': 'createdAt', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'RequestorIdIndex',
                'KeySchema': [
                    {'AttributeName': 'requestorId', 'KeyType': 'HASH'},
                    {'AttributeName': 'createdAt', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            },
            {
                'IndexName': 'TargetIdIndex',
                'KeySchema': [
                    {'AttributeName': 'targetId', 'KeyType': 'HASH'},
                    {'AttributeName': 'createdAt', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            },
            {
                'IndexName': 'StatusIndex',
                'KeySchema': [
                    {'AttributeName': 'status', 'KeyType': 'HASH'},
                    {'AttributeName': 'createdAt', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Create Score table
    dynamodb.create_table(
        TableName=SCORE_TABLE,
        KeySchema=[
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'id', 'AttributeType': 'S'},
            {'AttributeName': 'playerId', 'AttributeType': 'S'},
            {'AttributeName': 'scheduleId', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'PlayerIdIndex',
                'KeySchema': [
                    {'AttributeName': 'playerId', 'KeyType': 'HASH'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            },
            {
                'IndexName': 'ScheduleIdIndex',
                'KeySchema': [
                    {'AttributeName': 'scheduleId', 'KeyType': 'HASH'}
                ],
                'Projection': {'ProjectionType': 'ALL'},
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Set environment variables for tests
    os.environ['PLAYER_TABLE'] = PLAYER_TABLE
    os.environ['SCHEDULE_TABLE'] = SCHEDULE_TABLE
    os.environ['SWAP_REQUEST_TABLE'] = SWAP_REQUEST_TABLE
    os.environ['SCORE_TABLE'] = SCORE_TABLE

    yield {
        'player_table': PLAYER_TABLE,
        'schedule_table': SCHEDULE_TABLE,
        'swap_request_table': SWAP_REQUEST_TABLE,
        'score_table': SCORE_TABLE
    }

@pytest.fixture
def sample_players():
    """Sample player data for tests."""
    return [
        {
            'id': 'player1',
            'email': 'kevin.cory@mutualofomaha.com',
            'name': 'Kevin Cory',
            'phone': '555-123-4567',
            'weeksScheduled': 0,
            'isAdmin': True,
            'totalWins': 0,
            'totalLosses': 0
        },
        {
            'id': 'player2',
            'email': 'bbarstow68@gmail.com',
            'name': 'Bruce Barstow',
            'phone': '555-234-5678',
            'weeksScheduled': 0,
            'isAdmin': False,
            'totalWins': 0,
            'totalLosses': 0
        },
        {
            'id': 'player3',
            'email': 'russellavalon@gmail.com',
            'name': 'Russell Avalon',
            'phone': '555-345-6789',
            'weeksScheduled': 0,
            'isAdmin': False,
            'totalWins': 0,
            'totalLosses': 0
        },
        {
            'id': 'player4',
            'email': 'jordanthansen97@gmail.com',
            'name': 'Jordan Hansen',
            'phone': '555-456-7890',
            'weeksScheduled': 0,
            'isAdmin': False,
            'totalWins': 0,
            'totalLosses': 0
        }
    ]

@pytest.fixture
def sample_schedules():
    """Sample schedule data for tests."""
    return [
        {
            'id': 'schedule1',
            'date': '2025-04-28',
            'time': '15:00',
            'course': 'Eagle Run',
            'playerIds': ['player1', 'player2', 'player3', 'player4'],
            'notes': 'First game of the season',
            'isCompleted': False
        },
        {
            'id': 'schedule2',
            'date': '2025-05-05',
            'time': '15:00',
            'course': 'Tiburon',
            'playerIds': ['player1', 'player2', 'player3', 'player4'],
            'notes': 'Second game',
            'isCompleted': False
        }
    ]

@pytest.fixture
def populate_tables(dynamodb, setup_dynamodb_tables, sample_players, sample_schedules):
    """Populate tables with sample data."""
    dynamodb_client = boto3.client('dynamodb', region_name=TEST_REGION)
    
    # Insert players
    for player in sample_players:
        dynamodb_client.put_item(
            TableName=PLAYER_TABLE,
            Item={k: {'S' if isinstance(v, str) else 'N' if isinstance(v, int) else 'BOOL': str(v) if not isinstance(v, bool) else v} for k, v in player.items()}
        )
    
    # Insert schedules
    for schedule in sample_schedules:
        item = {}
        for k, v in schedule.items():
            if k == 'playerIds':
                item[k] = {'SS': v}
            elif isinstance(v, str):
                item[k] = {'S': v}
            elif isinstance(v, int):
                item[k] = {'N': str(v)}
            elif isinstance(v, bool):
                item[k] = {'BOOL': v}
        
        dynamodb_client.put_item(
            TableName=SCHEDULE_TABLE,
            Item=item
        )
    
    return {
        'players': sample_players,
        'schedules': sample_schedules
    }
