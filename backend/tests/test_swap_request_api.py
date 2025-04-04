import os
import sys
import json
import pytest
import boto3
from unittest.mock import patch, MagicMock

# Add the lambda directory to the path so we can import the resolvers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda', 'resolvers'))

# Import the resolvers
import swapRequestResolvers

class TestSwapRequestAPI:
    """Test cases for SwapRequest API operations."""

    @pytest.fixture
    def sample_swap_request(self, setup_dynamodb_tables, populate_tables):
        """Create a sample swap request for testing."""
        swap_request = {
            'id': 'swap1',
            'requestorId': 'player1',
            'requestorWeekId': 'schedule1',
            'targetId': 'player2',
            'targetWeekId': 'schedule2',
            'proposedDate': '2025-05-15',
            'reason': 'Vacation conflict',
            'status': 'PENDING',
            'createdAt': '2025-04-20T10:00:00Z'
        }
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(os.environ['SWAP_REQUEST_TABLE'])
        table.put_item(Item=swap_request)
        
        return swap_request

    def test_get_swap_request(self, setup_dynamodb_tables, sample_swap_request):
        """Test getting a swap request by ID."""
        # Arrange
        swap_id = sample_swap_request['id']
        event = {
            'arguments': {'id': swap_id},
            'info': {
                'fieldName': 'getSwapRequest',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = swapRequestResolvers.getSwapRequest(event)
        
        # Assert
        assert result is not None
        assert result['id'] == swap_id
        assert result['requestorId'] == sample_swap_request['requestorId']
        assert result['targetId'] == sample_swap_request['targetId']
        assert result['status'] == 'PENDING'
        assert 'requestor' in result
        assert 'target' in result
        assert 'requestorWeek' in result
        assert 'targetWeek' in result

    def test_list_swap_requests(self, setup_dynamodb_tables, sample_swap_request):
        """Test listing all swap requests."""
        # Arrange
        event = {
            'info': {
                'fieldName': 'listSwapRequests',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = swapRequestResolvers.listSwapRequests(event)
        
        # Assert
        assert result is not None
        assert len(result) == 1
        assert result[0]['id'] == sample_swap_request['id']
        assert 'requestor' in result[0]
        assert 'target' in result[0]
        assert 'requestorWeek' in result[0]
        assert 'targetWeek' in result[0]

    def test_get_swap_requests_by_requestor(self, setup_dynamodb_tables, sample_swap_request):
        """Test getting swap requests by requestor."""
        # Arrange
        requestor_id = sample_swap_request['requestorId']
        event = {
            'arguments': {'requestorId': requestor_id},
            'info': {
                'fieldName': 'getSwapRequestsByRequestor',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = swapRequestResolvers.getSwapRequestsByRequestor(event)
        
        # Assert
        assert result is not None
        assert len(result) == 1
        assert result[0]['requestorId'] == requestor_id
        assert 'requestor' in result[0]
        assert 'target' in result[0]
        assert 'requestorWeek' in result[0]
        assert 'targetWeek' in result[0]

    def test_get_swap_requests_by_target(self, setup_dynamodb_tables, sample_swap_request):
        """Test getting swap requests by target."""
        # Arrange
        target_id = sample_swap_request['targetId']
        event = {
            'arguments': {'targetId': target_id},
            'info': {
                'fieldName': 'getSwapRequestsByTarget',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = swapRequestResolvers.getSwapRequestsByTarget(event)
        
        # Assert
        assert result is not None
        assert len(result) == 1
        assert result[0]['targetId'] == target_id
        assert 'requestor' in result[0]
        assert 'target' in result[0]
        assert 'requestorWeek' in result[0]
        assert 'targetWeek' in result[0]

    def test_get_swap_requests_by_status(self, setup_dynamodb_tables, sample_swap_request):
        """Test getting swap requests by status."""
        # Arrange
        status = sample_swap_request['status']
        event = {
            'arguments': {'status': status},
            'info': {
                'fieldName': 'getSwapRequestsByStatus',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = swapRequestResolvers.getSwapRequestsByStatus(event)
        
        # Assert
        assert result is not None
        assert len(result) == 1
        assert result[0]['status'] == status
        assert 'requestor' in result[0]
        assert 'target' in result[0]
        assert 'requestorWeek' in result[0]
        assert 'targetWeek' in result[0]

    def test_create_swap_request(self, setup_dynamodb_tables, populate_tables):
        """Test creating a new swap request."""
        # Arrange
        new_swap_request = {
            'requestorId': 'player3',
            'requestorWeekId': 'schedule1',
            'targetId': 'player4',
            'targetWeekId': 'schedule2',
            'proposedDate': '2025-05-20',
            'reason': 'Work conflict'
        }
        
        event = {
            'arguments': {'input': new_swap_request},
            'info': {
                'fieldName': 'createSwapRequest',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Patch the getScheduleDetails function to return valid schedules
        with patch('swapRequestResolvers.getScheduleDetails') as mock_get_schedule:
            mock_get_schedule.side_effect = lambda id: {
                'schedule1': {
                    'id': 'schedule1',
                    'playerIds': ['player1', 'player2', 'player3', 'player4']
                },
                'schedule2': {
                    'id': 'schedule2',
                    'playerIds': ['player1', 'player2', 'player3', 'player4']
                }
            }[id]
            
            # Act
            result = swapRequestResolvers.createSwapRequest(event)
        
        # Assert
        assert result is not None
        assert result['requestorId'] == new_swap_request['requestorId']
        assert result['targetId'] == new_swap_request['targetId']
        assert result['proposedDate'] == new_swap_request['proposedDate']
        assert result['reason'] == new_swap_request['reason']
        assert result['status'] == 'PENDING'
        assert 'id' in result
        assert 'createdAt' in result
        assert 'requestor' in result
        assert 'target' in result
        assert 'requestorWeek' in result
        assert 'targetWeek' in result
        
        # Verify the swap request was actually created in the database
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(os.environ['SWAP_REQUEST_TABLE'])
        db_result = table.get_item(Key={'id': result['id']})
        assert 'Item' in db_result
        assert db_result['Item']['requestorId'] == new_swap_request['requestorId']

    def test_update_swap_request(self, setup_dynamodb_tables, sample_swap_request):
        """Test updating an existing swap request."""
        # Arrange
        swap_id = sample_swap_request['id']
        update_data = {
            'reason': 'Updated reason',
            'status': 'REJECTED'
        }
        
        event = {
            'arguments': {
                'id': swap_id,
                'input': update_data
            },
            'info': {
                'fieldName': 'updateSwapRequest',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Patch the getSwapRequest function to return the sample swap request
        with patch('swapRequestResolvers.getSwapRequest', return_value=sample_swap_request):
            # Act
            result = swapRequestResolvers.updateSwapRequest(event)
        
        # Assert
        assert result is not None
        assert result['id'] == swap_id
        assert result['reason'] == update_data['reason']
        assert result['status'] == update_data['status']
        
        # Verify the swap request was actually updated in the database
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(os.environ['SWAP_REQUEST_TABLE'])
        db_result = table.get_item(Key={'id': swap_id})
        assert 'Item' in db_result
        assert db_result['Item']['reason'] == update_data['reason']
        assert db_result['Item']['status'] == update_data['status']

    def test_accept_swap_request(self, setup_dynamodb_tables, sample_swap_request):
        """Test accepting a swap request."""
        # Arrange
        swap_id = sample_swap_request['id']
        event = {
            'arguments': {'id': swap_id},
            'info': {
                'fieldName': 'acceptSwapRequest',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Patch the necessary functions to avoid actual DynamoDB operations
        with patch('swapRequestResolvers.getSwapRequest', return_value=sample_swap_request), \
             patch('swapRequestResolvers.getScheduleDetails') as mock_get_schedule, \
             patch('boto3.resource') as mock_resource:
            
            # Mock schedule details
            mock_get_schedule.side_effect = lambda id: {
                'schedule1': {
                    'id': 'schedule1',
                    'playerIds': ['player1', 'player2', 'player3', 'player4']
                },
                'schedule2': {
                    'id': 'schedule2',
                    'playerIds': ['player1', 'player2', 'player3', 'player4']
                }
            }[id]
            
            # Mock DynamoDB update operations
            mock_table = MagicMock()
            mock_table.update.return_value = {'Attributes': {**sample_swap_request, 'status': 'ACCEPTED'}}
            mock_resource.return_value.Table.return_value = mock_table
            
            # Act
            result = swapRequestResolvers.acceptSwapRequest(event)
        
        # Assert
        assert result is not None
        assert result['id'] == swap_id
        assert result['status'] == 'ACCEPTED'

    def test_reject_swap_request(self, setup_dynamodb_tables, sample_swap_request):
        """Test rejecting a swap request."""
        # Arrange
        swap_id = sample_swap_request['id']
        event = {
            'arguments': {'id': swap_id},
            'info': {
                'fieldName': 'rejectSwapRequest',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Patch the necessary functions to avoid actual DynamoDB operations
        with patch('swapRequestResolvers.getSwapRequest', return_value=sample_swap_request), \
             patch('boto3.resource') as mock_resource:
            
            # Mock DynamoDB update operations
            mock_table = MagicMock()
            mock_table.update.return_value = {'Attributes': {**sample_swap_request, 'status': 'REJECTED'}}
            mock_resource.return_value.Table.return_value = mock_table
            
            # Act
            result = swapRequestResolvers.rejectSwapRequest(event)
        
        # Assert
        assert result is not None
        assert result['id'] == swap_id
        assert result['status'] == 'REJECTED'

    def test_admin_override_swap_request(self, setup_dynamodb_tables, sample_swap_request):
        """Test admin override of a swap request."""
        # Arrange
        swap_id = sample_swap_request['id']
        event = {
            'arguments': {
                'id': swap_id,
                'approved': True
            },
            'info': {
                'fieldName': 'adminOverrideSwapRequest',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Patch the necessary functions to avoid actual DynamoDB operations
        with patch('swapRequestResolvers.getSwapRequest', return_value=sample_swap_request), \
             patch('swapRequestResolvers.getScheduleDetails') as mock_get_schedule, \
             patch('boto3.resource') as mock_resource:
            
            # Mock schedule details
            mock_get_schedule.side_effect = lambda id: {
                'schedule1': {
                    'id': 'schedule1',
                    'playerIds': ['player1', 'player2', 'player3', 'player4']
                },
                'schedule2': {
                    'id': 'schedule2',
                    'playerIds': ['player1', 'player2', 'player3', 'player4']
                }
            }[id]
            
            # Mock DynamoDB update operations
            mock_table = MagicMock()
            mock_table.update.return_value = {'Attributes': {**sample_swap_request, 'status': 'ACCEPTED'}}
            mock_resource.return_value.Table.return_value = mock_table
            
            # Act
            result = swapRequestResolvers.adminOverrideSwapRequest(event)
        
        # Assert
        assert result is not None
        assert result['id'] == swap_id
        assert result['status'] == 'ACCEPTED'
