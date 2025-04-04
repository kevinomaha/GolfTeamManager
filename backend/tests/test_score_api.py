import os
import sys
import json
import pytest
import boto3
from unittest.mock import patch, MagicMock

# Add the lambda directory to the path so we can import the resolvers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda', 'resolvers'))

# Import the resolvers
import scoreResolvers

class TestScoreAPI:
    """Test cases for Score API operations."""

    @pytest.fixture
    def sample_score(self, setup_dynamodb_tables, populate_tables):
        """Create a sample score for testing."""
        score = {
            'id': 'score1',
            'scheduleId': 'schedule1',
            'playerId': 'player1',
            'score': 85,
            'result': 'WIN',
            'notes': 'Great game'
        }
        
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(os.environ['SCORE_TABLE'])
        table.put_item(Item=score)
        
        return score

    def test_get_score(self, setup_dynamodb_tables, sample_score):
        """Test getting a score by ID."""
        # Arrange
        score_id = sample_score['id']
        event = {
            'arguments': {'id': score_id},
            'info': {
                'fieldName': 'getScore',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = scoreResolvers.getScore(event)
        
        # Assert
        assert result is not None
        assert result['id'] == score_id
        assert result['scheduleId'] == sample_score['scheduleId']
        assert result['playerId'] == sample_score['playerId']
        assert result['score'] == sample_score['score']
        assert result['result'] == sample_score['result']
        assert 'player' in result
        assert 'schedule' in result

    def test_list_scores(self, setup_dynamodb_tables, sample_score):
        """Test listing all scores."""
        # Arrange
        event = {
            'info': {
                'fieldName': 'listScores',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = scoreResolvers.listScores(event)
        
        # Assert
        assert result is not None
        assert len(result) == 1
        assert result[0]['id'] == sample_score['id']
        assert 'player' in result[0]
        assert 'schedule' in result[0]

    def test_get_scores_by_player(self, setup_dynamodb_tables, sample_score):
        """Test getting scores by player."""
        # Arrange
        player_id = sample_score['playerId']
        event = {
            'arguments': {'playerId': player_id},
            'info': {
                'fieldName': 'getScoresByPlayer',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = scoreResolvers.getScoresByPlayer(event)
        
        # Assert
        assert result is not None
        assert len(result) == 1
        assert result[0]['playerId'] == player_id
        assert 'player' in result[0]
        assert 'schedule' in result[0]

    def test_get_scores_by_schedule(self, setup_dynamodb_tables, sample_score):
        """Test getting scores by schedule."""
        # Arrange
        schedule_id = sample_score['scheduleId']
        event = {
            'arguments': {'scheduleId': schedule_id},
            'info': {
                'fieldName': 'getScoresBySchedule',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = scoreResolvers.getScoresBySchedule(event)
        
        # Assert
        assert result is not None
        assert len(result) == 1
        assert result[0]['scheduleId'] == schedule_id
        assert 'player' in result[0]
        assert 'schedule' in result[0]

    def test_create_score(self, setup_dynamodb_tables, populate_tables):
        """Test creating a new score."""
        # Arrange
        new_score = {
            'scheduleId': 'schedule1',
            'playerId': 'player2',
            'score': 90,
            'result': 'LOSS',
            'notes': 'Tough day'
        }
        
        event = {
            'arguments': {'input': new_score},
            'info': {
                'fieldName': 'createScore',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Patch the necessary functions to avoid actual DynamoDB operations
        with patch('scoreResolvers.getScheduleDetails') as mock_get_schedule, \
             patch('scoreResolvers.getScoresBySchedule') as mock_get_scores:
            
            # Mock schedule details
            mock_get_schedule.return_value = {
                'id': 'schedule1',
                'playerIds': ['player1', 'player2', 'player3', 'player4']
            }
            
            # Mock existing scores
            mock_get_scores.return_value = []
            
            # Act
            result = scoreResolvers.createScore(event)
        
        # Assert
        assert result is not None
        assert result['scheduleId'] == new_score['scheduleId']
        assert result['playerId'] == new_score['playerId']
        assert result['score'] == new_score['score']
        assert result['result'] == new_score['result']
        assert result['notes'] == new_score['notes']
        assert 'id' in result
        assert 'player' in result
        assert 'schedule' in result
        
        # Verify the score was actually created in the database
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(os.environ['SCORE_TABLE'])
        db_result = table.get_item(Key={'id': result['id']})
        assert 'Item' in db_result
        assert db_result['Item']['score'] == new_score['score']
        
        # Verify player totalLosses was incremented
        player_table = dynamodb.Table(os.environ['PLAYER_TABLE'])
        player = player_table.get_item(Key={'id': new_score['playerId']})['Item']
        assert int(player['totalLosses']) == 1  # Incremented from 0 to 1

    def test_create_score_player_not_in_schedule(self, setup_dynamodb_tables, populate_tables):
        """Test creating a score for a player not in the schedule."""
        # Arrange
        new_score = {
            'scheduleId': 'schedule1',
            'playerId': 'non-existent-player',
            'score': 90,
            'result': 'LOSS',
            'notes': 'Tough day'
        }
        
        event = {
            'arguments': {'input': new_score},
            'info': {
                'fieldName': 'createScore',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Patch the getScheduleDetails function to return a schedule without the player
        with patch('scoreResolvers.getScheduleDetails') as mock_get_schedule:
            mock_get_schedule.return_value = {
                'id': 'schedule1',
                'playerIds': ['player1', 'player2', 'player3', 'player4']
            }
            
            # Act & Assert
            with pytest.raises(Exception) as excinfo:
                scoreResolvers.createScore(event)
            
            assert "Player is not part of the specified schedule" in str(excinfo.value)

    def test_update_score(self, setup_dynamodb_tables, sample_score):
        """Test updating an existing score."""
        # Arrange
        score_id = sample_score['id']
        update_data = {
            'score': 82,
            'result': 'TIE',
            'notes': 'Updated notes'
        }
        
        event = {
            'arguments': {
                'id': score_id,
                'input': update_data
            },
            'info': {
                'fieldName': 'updateScore',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Patch the necessary functions to avoid actual DynamoDB operations
        with patch('scoreResolvers.getScore') as mock_get_score:
            # Mock current score
            mock_get_score.return_value = {
                **sample_score,
                'player': {'id': sample_score['playerId']},
                'schedule': {'id': sample_score['scheduleId']}
            }
            
            # Act
            result = scoreResolvers.updateScore(event)
        
        # Assert
        assert result is not None
        assert result['id'] == score_id
        assert result['score'] == update_data['score']
        assert result['result'] == update_data['result']
        assert result['notes'] == update_data['notes']
        
        # Verify the score was actually updated in the database
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(os.environ['SCORE_TABLE'])
        db_result = table.get_item(Key={'id': score_id})
        assert 'Item' in db_result
        assert db_result['Item']['score'] == update_data['score']
        assert db_result['Item']['result'] == update_data['result']
        
        # Verify player win/loss record was updated
        player_table = dynamodb.Table(os.environ['PLAYER_TABLE'])
        player = player_table.get_item(Key={'id': sample_score['playerId']})['Item']
        assert int(player['totalWins']) == 0  # Decremented from 1 to 0

    def test_update_score_not_found(self, setup_dynamodb_tables):
        """Test updating a non-existent score."""
        # Arrange
        score_id = 'non-existent-score'
        update_data = {
            'score': 82,
            'result': 'TIE'
        }
        
        event = {
            'arguments': {
                'id': score_id,
                'input': update_data
            },
            'info': {
                'fieldName': 'updateScore',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Patch the getScore function to return None (score not found)
        with patch('scoreResolvers.getScore', return_value=None):
            # Act & Assert
            with pytest.raises(Exception) as excinfo:
                scoreResolvers.updateScore(event)
            
            assert f"Score with ID {score_id} not found" in str(excinfo.value)
