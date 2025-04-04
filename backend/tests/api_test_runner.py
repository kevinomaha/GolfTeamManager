#!/usr/bin/env python
"""
API Test Runner for Golf League Manager

This script tests all API endpoints for the Golf League Manager application.
It sets up the necessary environment and runs tests for each API endpoint.
"""

import os
import sys
import json
import boto3
import pytest
from moto import mock_dynamodb
from datetime import datetime, timedelta
import uuid

# Add the lambda directory to the path so we can import the resolvers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda', 'resolvers'))

# Import the resolvers
import playerResolvers
import scheduleResolvers
import swapRequestResolvers
import scoreResolvers

# Constants for test data
TEST_REGION = 'us-east-1'
PLAYER_TABLE = 'GolfLeague-Players-Test'
SCHEDULE_TABLE = 'GolfLeague-Schedules-Test'
SWAP_REQUEST_TABLE = 'GolfLeague-SwapRequests-Test'
SCORE_TABLE = 'GolfLeague-Scores-Test'

def setup_dynamodb():
    """Set up DynamoDB tables for testing."""
    print("Setting up DynamoDB tables...")
    
    # Set environment variables for tests
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = TEST_REGION
    
    os.environ['PLAYER_TABLE'] = PLAYER_TABLE
    os.environ['SCHEDULE_TABLE'] = SCHEDULE_TABLE
    os.environ['SWAP_REQUEST_TABLE'] = SWAP_REQUEST_TABLE
    os.environ['SCORE_TABLE'] = SCORE_TABLE
    
    # Create DynamoDB client
    dynamodb = boto3.resource('dynamodb', region_name=TEST_REGION)
    
    # Create Player table
    try:
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
        print(f"Created table: {PLAYER_TABLE}")
    except Exception as e:
        print(f"Error creating {PLAYER_TABLE}: {e}")

    # Create Schedule table
    try:
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
        print(f"Created table: {SCHEDULE_TABLE}")
    except Exception as e:
        print(f"Error creating {SCHEDULE_TABLE}: {e}")

    # Create SwapRequest table
    try:
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
        print(f"Created table: {SWAP_REQUEST_TABLE}")
    except Exception as e:
        print(f"Error creating {SWAP_REQUEST_TABLE}: {e}")

    # Create Score table
    try:
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
        print(f"Created table: {SCORE_TABLE}")
    except Exception as e:
        print(f"Error creating {SCORE_TABLE}: {e}")
    
    return dynamodb

def populate_sample_data(dynamodb):
    """Populate tables with sample data."""
    print("Populating tables with sample data...")
    
    # Sample players
    players = [
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
            'email': 'jordan.hansen@mutualofomaha.com',
            'name': 'Jordan Hansen',
            'phone': '555-456-7890',
            'weeksScheduled': 0,
            'isAdmin': False,
            'totalWins': 0,
            'totalLosses': 0
        }
    ]
    
    # Sample schedules
    schedules = [
        {
            'id': 'schedule1',
            'date': '2025-04-28',
            'time': '17:30',
            'course': 'Eagle Run',
            'players': ['player1', 'player2', 'player3', 'player4'],
            'notes': 'First game of the season',
            'isCompleted': False
        },
        {
            'id': 'schedule2',
            'date': '2025-05-05',
            'time': '17:30',
            'course': 'Tiburon',
            'players': ['player1', 'player2', 'player3', 'player4'],
            'notes': 'Week 2',
            'isCompleted': False
        }
    ]
    
    # Insert players
    player_table = dynamodb.Table(PLAYER_TABLE)
    for player in players:
        player_table.put_item(Item=player)
    
    # Insert schedules
    schedule_table = dynamodb.Table(SCHEDULE_TABLE)
    for schedule in schedules:
        schedule_table.put_item(Item=schedule)
    
    print("Sample data populated successfully")

def test_player_apis():
    """Test Player API operations."""
    print("\n=== Testing Player APIs ===")
    
    # Test getPlayer
    print("\nTesting getPlayer...")
    player_id = 'player1'
    event = {
        'arguments': {'id': player_id},
        'info': {
            'fieldName': 'getPlayer',
            'parentTypeName': 'Query'
        }
    }
    
    result = playerResolvers.getPlayer(event)
    if result and result['id'] == player_id and result['name'] == 'Kevin Cory':
        print("✅ getPlayer test passed")
    else:
        print("❌ getPlayer test failed")
        print(f"Expected player with ID {player_id}, got: {result}")
    
    # Test listPlayers
    print("\nTesting listPlayers...")
    event = {
        'info': {
            'fieldName': 'listPlayers',
            'parentTypeName': 'Query'
        }
    }
    
    result = playerResolvers.listPlayers(event)
    if result and len(result) == 4:
        print("✅ listPlayers test passed")
    else:
        print("❌ listPlayers test failed")
        print(f"Expected 4 players, got: {len(result) if result else 0}")
    
    # Test createPlayer
    print("\nTesting createPlayer...")
    new_player = {
        'email': 'ryan.wand@mutualofomaha.com',
        'name': 'Ryan Wand',
        'phone': '555-987-6543',
        'isAdmin': False
    }
    
    event = {
        'arguments': {'input': new_player},
        'info': {
            'fieldName': 'createPlayer',
            'parentTypeName': 'Mutation'
        }
    }
    
    result = playerResolvers.createPlayer(event)
    if (result and result['email'] == new_player['email'] and 
        result['name'] == new_player['name'] and 'id' in result):
        print("✅ createPlayer test passed")
        created_player_id = result['id']
    else:
        print("❌ createPlayer test failed")
        print(f"Expected new player with email {new_player['email']}, got: {result}")
        created_player_id = None
    
    # Test updatePlayer
    if created_player_id:
        print("\nTesting updatePlayer...")
        update_data = {
            'name': 'Ryan Wand Jr.',
            'phone': '555-111-2222',
            'totalWins': 5
        }
        
        event = {
            'arguments': {
                'id': created_player_id,
                'input': update_data
            },
            'info': {
                'fieldName': 'updatePlayer',
                'parentTypeName': 'Mutation'
            }
        }
        
        result = playerResolvers.updatePlayer(event)
        if (result and result['id'] == created_player_id and 
            result['name'] == update_data['name'] and 
            result['totalWins'] == update_data['totalWins']):
            print("✅ updatePlayer test passed")
        else:
            print("❌ updatePlayer test failed")
            print(f"Expected updated player with name {update_data['name']}, got: {result}")

def test_schedule_apis():
    """Test Schedule API operations."""
    print("\n=== Testing Schedule APIs ===")
    
    # Test getSchedule
    print("\nTesting getSchedule...")
    schedule_id = 'schedule1'
    event = {
        'arguments': {'id': schedule_id},
        'info': {
            'fieldName': 'getSchedule',
            'parentTypeName': 'Query'
        }
    }
    
    result = scheduleResolvers.getSchedule(event)
    if result and result['id'] == schedule_id and result['course'] == 'Eagle Run':
        print("✅ getSchedule test passed")
    else:
        print("❌ getSchedule test failed")
        print(f"Expected schedule with ID {schedule_id}, got: {result}")
    
    # Test listSchedules
    print("\nTesting listSchedules...")
    event = {
        'info': {
            'fieldName': 'listSchedules',
            'parentTypeName': 'Query'
        }
    }
    
    result = scheduleResolvers.listSchedules(event)
    if result and len(result) == 2:
        print("✅ listSchedules test passed")
    else:
        print("❌ listSchedules test failed")
        print(f"Expected 2 schedules, got: {len(result) if result else 0}")
    
    # Test createSchedule
    print("\nTesting createSchedule...")
    new_schedule = {
        'date': '2025-05-12',
        'time': '17:30',
        'course': 'Shoreline',
        'players': ['player1', 'player2', 'player3', 'player4'],
        'notes': 'Week 3',
        'isCompleted': False
    }
    
    event = {
        'arguments': {'input': new_schedule},
        'info': {
            'fieldName': 'createSchedule',
            'parentTypeName': 'Mutation'
        }
    }
    
    result = scheduleResolvers.createSchedule(event)
    if (result and result['date'] == new_schedule['date'] and 
        result['course'] == new_schedule['course'] and 'id' in result):
        print("✅ createSchedule test passed")
        created_schedule_id = result['id']
    else:
        print("❌ createSchedule test failed")
        print(f"Expected new schedule with date {new_schedule['date']}, got: {result}")
        created_schedule_id = None
    
    # Test updateSchedule
    if created_schedule_id:
        print("\nTesting updateSchedule...")
        update_data = {
            'time': '18:00',
            'notes': 'Updated Week 3 - Later tee time',
            'isCompleted': True
        }
        
        event = {
            'arguments': {
                'id': created_schedule_id,
                'input': update_data
            },
            'info': {
                'fieldName': 'updateSchedule',
                'parentTypeName': 'Mutation'
            }
        }
        
        result = scheduleResolvers.updateSchedule(event)
        if (result and result['id'] == created_schedule_id and 
            result['time'] == update_data['time'] and 
            result['isCompleted'] == update_data['isCompleted']):
            print("✅ updateSchedule test passed")
        else:
            print("❌ updateSchedule test failed")
            print(f"Expected updated schedule with time {update_data['time']}, got: {result}")

def test_swap_request_apis():
    """Test SwapRequest API operations."""
    print("\n=== Testing SwapRequest APIs ===")
    
    # Test createSwapRequest
    print("\nTesting createSwapRequest...")
    new_swap_request = {
        'requestorId': 'player1',
        'requestorWeekId': 'schedule1',
        'targetId': 'player2',
        'targetWeekId': 'schedule2',
        'proposedDate': '2025-05-05',
        'reason': 'Family event',
        'status': 'PENDING'
    }
    
    event = {
        'arguments': {'input': new_swap_request},
        'info': {
            'fieldName': 'createSwapRequest',
            'parentTypeName': 'Mutation'
        }
    }
    
    result = swapRequestResolvers.createSwapRequest(event)
    if (result and result['requestorId'] == new_swap_request['requestorId'] and 
        result['targetId'] == new_swap_request['targetId'] and 'id' in result):
        print("✅ createSwapRequest test passed")
        created_swap_id = result['id']
    else:
        print("❌ createSwapRequest test failed")
        print(f"Expected new swap request, got: {result}")
        created_swap_id = None
    
    # Test getSwapRequest
    if created_swap_id:
        print("\nTesting getSwapRequest...")
        event = {
            'arguments': {'id': created_swap_id},
            'info': {
                'fieldName': 'getSwapRequest',
                'parentTypeName': 'Query'
            }
        }
        
        result = swapRequestResolvers.getSwapRequest(event)
        if result and result['id'] == created_swap_id:
            print("✅ getSwapRequest test passed")
        else:
            print("❌ getSwapRequest test failed")
            print(f"Expected swap request with ID {created_swap_id}, got: {result}")
    
    # Test listSwapRequests
    print("\nTesting listSwapRequests...")
    event = {
        'info': {
            'fieldName': 'listSwapRequests',
            'parentTypeName': 'Query'
        }
    }
    
    result = swapRequestResolvers.listSwapRequests(event)
    if result and len(result) >= 1:
        print("✅ listSwapRequests test passed")
    else:
        print("❌ listSwapRequests test failed")
        print(f"Expected at least 1 swap request, got: {len(result) if result else 0}")
    
    # Test acceptSwapRequest
    if created_swap_id:
        print("\nTesting acceptSwapRequest...")
        event = {
            'arguments': {'id': created_swap_id},
            'info': {
                'fieldName': 'acceptSwapRequest',
                'parentTypeName': 'Mutation'
            }
        }
        
        result = swapRequestResolvers.acceptSwapRequest(event)
        if result and result['id'] == created_swap_id and result['status'] == 'ACCEPTED':
            print("✅ acceptSwapRequest test passed")
        else:
            print("❌ acceptSwapRequest test failed")
            print(f"Expected accepted swap request, got: {result}")

def test_score_apis():
    """Test Score API operations."""
    print("\n=== Testing Score APIs ===")
    
    # Test createScore
    print("\nTesting createScore...")
    new_score = {
        'scheduleId': 'schedule1',
        'playerId': 'player1',
        'score': 85,
        'result': 'WIN',
        'notes': 'Great round'
    }
    
    event = {
        'arguments': {'input': new_score},
        'info': {
            'fieldName': 'createScore',
            'parentTypeName': 'Mutation'
        }
    }
    
    result = scoreResolvers.createScore(event)
    if (result and result['scheduleId'] == new_score['scheduleId'] and 
        result['playerId'] == new_score['playerId'] and 'id' in result):
        print("✅ createScore test passed")
        created_score_id = result['id']
    else:
        print("❌ createScore test failed")
        print(f"Expected new score, got: {result}")
        created_score_id = None
    
    # Test getScore
    if created_score_id:
        print("\nTesting getScore...")
        event = {
            'arguments': {'id': created_score_id},
            'info': {
                'fieldName': 'getScore',
                'parentTypeName': 'Query'
            }
        }
        
        result = scoreResolvers.getScore(event)
        if result and result['id'] == created_score_id:
            print("✅ getScore test passed")
        else:
            print("❌ getScore test failed")
            print(f"Expected score with ID {created_score_id}, got: {result}")
    
    # Test listScores
    print("\nTesting listScores...")
    event = {
        'info': {
            'fieldName': 'listScores',
            'parentTypeName': 'Query'
        }
    }
    
    result = scoreResolvers.listScores(event)
    if result and len(result) >= 1:
        print("✅ listScores test passed")
    else:
        print("❌ listScores test failed")
        print(f"Expected at least 1 score, got: {len(result) if result else 0}")
    
    # Test updateScore
    if created_score_id:
        print("\nTesting updateScore...")
        update_data = {
            'score': 82,
            'notes': 'Updated score after review'
        }
        
        event = {
            'arguments': {
                'id': created_score_id,
                'input': update_data
            },
            'info': {
                'fieldName': 'updateScore',
                'parentTypeName': 'Mutation'
            }
        }
        
        result = scoreResolvers.updateScore(event)
        if (result and result['id'] == created_score_id and 
            result['score'] == update_data['score']):
            print("✅ updateScore test passed")
        else:
            print("❌ updateScore test failed")
            print(f"Expected updated score, got: {result}")

def main():
    """Run all API tests."""
    print("Starting Golf League Manager API Tests...")
    
    # Set up mock DynamoDB
    with mock_dynamodb():
        # Set up tables
        dynamodb = setup_dynamodb()
        
        # Populate sample data
        populate_sample_data(dynamodb)
        
        # Run tests
        test_player_apis()
        test_schedule_apis()
        test_swap_request_apis()
        test_score_apis()
    
    print("\nAPI Tests completed!")

if __name__ == '__main__':
    main()
