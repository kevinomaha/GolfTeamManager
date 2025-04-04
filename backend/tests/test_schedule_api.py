import os
import sys
import json
import pytest
import boto3
from unittest.mock import patch, MagicMock

# Add the lambda directory to the path so we can import the resolvers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda', 'resolvers'))

# Import the resolvers
import scheduleResolvers

class TestScheduleAPI:
    """Test cases for Schedule API operations."""

    def test_get_schedule(self, setup_dynamodb_tables, populate_tables):
        """Test getting a schedule by ID."""
        # Arrange
        schedule_id = 'schedule1'
        event = {
            'arguments': {'id': schedule_id},
            'info': {
                'fieldName': 'getSchedule',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = scheduleResolvers.getSchedule(event)
        
        # Assert
        assert result is not None
        assert result['id'] == schedule_id
        assert result['date'] == '2025-04-28'
        assert result['course'] == 'Eagle Run'
        assert 'playerIds' in result
        assert len(result['playerIds']) == 4
        assert 'players' in result
        assert len(result['players']) == 4

    def test_list_schedules(self, setup_dynamodb_tables, populate_tables):
        """Test listing all schedules."""
        # Arrange
        event = {
            'info': {
                'fieldName': 'listSchedules',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = scheduleResolvers.listSchedules(event)
        
        # Assert
        assert result is not None
        assert len(result) == 2
        assert any(schedule['course'] == 'Eagle Run' for schedule in result)
        assert any(schedule['course'] == 'Tiburon' for schedule in result)
        
        # Check that players are populated
        for schedule in result:
            assert 'players' in schedule
            assert len(schedule['players']) == 4

    def test_get_schedules_by_date(self, setup_dynamodb_tables, populate_tables):
        """Test getting schedules by date."""
        # Arrange
        date = '2025-04-28'
        event = {
            'arguments': {'date': date},
            'info': {
                'fieldName': 'getSchedulesByDate',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = scheduleResolvers.getSchedulesByDate(event)
        
        # Assert
        assert result is not None
        assert len(result) == 1
        assert result[0]['date'] == date
        assert result[0]['course'] == 'Eagle Run'
        assert 'players' in result[0]
        assert len(result[0]['players']) == 4

    def test_get_player_schedules(self, setup_dynamodb_tables, populate_tables):
        """Test getting schedules for a player."""
        # Arrange
        player_id = 'player1'
        event = {
            'arguments': {'playerId': player_id},
            'info': {
                'fieldName': 'getPlayerSchedules',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = scheduleResolvers.getPlayerSchedules(event)
        
        # Assert
        assert result is not None
        assert len(result) == 2
        for schedule in result:
            assert player_id in schedule['playerIds']
            assert 'players' in schedule
            assert len(schedule['players']) == 4
            assert any(player['id'] == player_id for player in schedule['players'])

    def test_create_schedule(self, setup_dynamodb_tables, populate_tables):
        """Test creating a new schedule."""
        # Arrange
        new_schedule = {
            'date': '2025-05-12',
            'time': '16:00',
            'course': 'Shoreline',
            'playerIds': ['player1', 'player2', 'player3', 'player4'],
            'notes': 'Third game',
            'isCompleted': False
        }
        
        event = {
            'arguments': {'input': new_schedule},
            'info': {
                'fieldName': 'createSchedule',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Act
        result = scheduleResolvers.createSchedule(event)
        
        # Assert
        assert result is not None
        assert result['date'] == new_schedule['date']
        assert result['time'] == new_schedule['time']
        assert result['course'] == new_schedule['course']
        assert result['playerIds'] == new_schedule['playerIds']
        assert result['notes'] == new_schedule['notes']
        assert result['isCompleted'] == new_schedule['isCompleted']
        assert 'id' in result
        assert 'players' in result
        assert len(result['players']) == 4
        
        # Verify the schedule was actually created in the database
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(os.environ['SCHEDULE_TABLE'])
        db_result = table.get_item(Key={'id': result['id']})
        assert 'Item' in db_result
        assert db_result['Item']['date'] == new_schedule['date']
        
        # Verify player weeksScheduled was incremented
        player_table = dynamodb.Table(os.environ['PLAYER_TABLE'])
        for player_id in new_schedule['playerIds']:
            player = player_table.get_item(Key={'id': player_id})['Item']
            assert int(player['weeksScheduled']) == 1  # Incremented from 0 to 1

    def test_update_schedule(self, setup_dynamodb_tables, populate_tables):
        """Test updating an existing schedule."""
        # Arrange
        schedule_id = 'schedule2'
        update_data = {
            'time': '17:00',
            'course': 'Tiburon West',
            'notes': 'Updated notes',
            'playerIds': ['player1', 'player2', 'player3']  # Removing player4
        }
        
        # Mock the current schedule
        current_schedule = {
            'id': schedule_id,
            'date': '2025-05-05',
            'time': '15:00',
            'course': 'Tiburon',
            'playerIds': ['player1', 'player2', 'player3', 'player4'],
            'notes': 'Second game',
            'isCompleted': False
        }
        
        event = {
            'arguments': {
                'id': schedule_id,
                'input': update_data
            },
            'info': {
                'fieldName': 'updateSchedule',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Act
        # First get the current schedule from DynamoDB to avoid mocking
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(os.environ['SCHEDULE_TABLE'])
        current_db_schedule = table.get_item(Key={'id': schedule_id})['Item']
        
        result = scheduleResolvers.updateSchedule(event)
        
        # Assert
        assert result is not None
        assert result['id'] == schedule_id
        assert result['time'] == update_data['time']
        assert result['course'] == update_data['course']
        assert result['notes'] == update_data['notes']
        assert set(result['playerIds']) == set(update_data['playerIds'])
        assert 'players' in result
        assert len(result['players']) == 3
        
        # Verify the schedule was actually updated in the database
        updated_db_schedule = table.get_item(Key={'id': schedule_id})['Item']
        assert updated_db_schedule['time'] == update_data['time']
        assert updated_db_schedule['course'] == update_data['course']
        assert updated_db_schedule['notes'] == update_data['notes']
        
        # Verify player weeksScheduled was decremented for removed player
        player_table = dynamodb.Table(os.environ['PLAYER_TABLE'])
        player4 = player_table.get_item(Key={'id': 'player4'})['Item']
        assert int(player4['weeksScheduled']) == 0  # Decremented back to 0

    def test_update_schedule_not_found(self, setup_dynamodb_tables):
        """Test updating a non-existent schedule."""
        # Arrange
        schedule_id = 'non-existent-schedule'
        update_data = {
            'time': '17:00',
            'course': 'Non-existent Course'
        }
        
        event = {
            'arguments': {
                'id': schedule_id,
                'input': update_data
            },
            'info': {
                'fieldName': 'updateSchedule',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Act & Assert
        with pytest.raises(Exception) as excinfo:
            scheduleResolvers.updateSchedule(event)
        
        assert f"Schedule with ID {schedule_id} not found" in str(excinfo.value)
