import os
import sys
import json
import pytest
import boto3
from unittest.mock import patch, MagicMock

# Add the lambda directory to the path so we can import the resolvers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lambda', 'resolvers'))

# Import the resolvers
import playerResolvers

class TestPlayerAPI:
    """Test cases for Player API operations."""

    def test_get_player(self, setup_dynamodb_tables, populate_tables):
        """Test getting a player by ID."""
        # Arrange
        player_id = 'player1'
        event = {
            'arguments': {'id': player_id},
            'info': {
                'fieldName': 'getPlayer',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = playerResolvers.getPlayer(event)
        
        # Assert
        assert result is not None
        assert result['id'] == player_id
        assert result['name'] == 'Kevin Cory'
        assert result['email'] == 'kevin.cory@mutualofomaha.com'
        assert result['isAdmin'] is True

    def test_list_players(self, setup_dynamodb_tables, populate_tables):
        """Test listing all players."""
        # Arrange
        event = {
            'info': {
                'fieldName': 'listPlayers',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = playerResolvers.listPlayers(event)
        
        # Assert
        assert result is not None
        assert len(result) == 4
        assert any(player['name'] == 'Kevin Cory' for player in result)
        assert any(player['name'] == 'Bruce Barstow' for player in result)
        assert any(player['name'] == 'Russell Avalon' for player in result)
        assert any(player['name'] == 'Jordan Hansen' for player in result)

    def test_get_player_by_email(self, setup_dynamodb_tables, populate_tables):
        """Test getting a player by email."""
        # Arrange
        email = 'bbarstow68@gmail.com'
        event = {
            'arguments': {'email': email},
            'info': {
                'fieldName': 'getPlayerByEmail',
                'parentTypeName': 'Query'
            }
        }
        
        # Act
        result = playerResolvers.getPlayerByEmail(event)
        
        # Assert
        assert result is not None
        assert result['email'] == email
        assert result['name'] == 'Bruce Barstow'
        assert result['id'] == 'player2'

    def test_create_player(self, setup_dynamodb_tables):
        """Test creating a new player."""
        # Arrange
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
        
        # Act
        result = playerResolvers.createPlayer(event)
        
        # Assert
        assert result is not None
        assert result['email'] == new_player['email']
        assert result['name'] == new_player['name']
        assert result['phone'] == new_player['phone']
        assert result['isAdmin'] == new_player['isAdmin']
        assert result['weeksScheduled'] == 0
        assert result['totalWins'] == 0
        assert result['totalLosses'] == 0
        assert 'id' in result
        
        # Verify the player was actually created in the database
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(os.environ['PLAYER_TABLE'])
        db_result = table.get_item(Key={'id': result['id']})
        assert 'Item' in db_result
        assert db_result['Item']['email'] == new_player['email']

    def test_update_player(self, setup_dynamodb_tables, populate_tables):
        """Test updating an existing player."""
        # Arrange
        player_id = 'player3'
        update_data = {
            'name': 'Russell Avalon Jr.',
            'phone': '555-111-2222',
            'totalWins': 5
        }
        
        event = {
            'arguments': {
                'id': player_id,
                'input': update_data
            },
            'info': {
                'fieldName': 'updatePlayer',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Mock the getPlayer function to return a valid player
        with patch('playerResolvers.getPlayer', return_value={
            'id': player_id,
            'email': 'russellavalon@gmail.com',
            'name': 'Russell Avalon',
            'phone': '555-345-6789',
            'weeksScheduled': 0,
            'isAdmin': False,
            'totalWins': 0,
            'totalLosses': 0
        }):
            # Act
            result = playerResolvers.updatePlayer(event)
        
        # Assert
        assert result is not None
        assert result['id'] == player_id
        assert result['name'] == update_data['name']
        assert result['phone'] == update_data['phone']
        assert result['totalWins'] == update_data['totalWins']
        
        # Verify the player was actually updated in the database
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table(os.environ['PLAYER_TABLE'])
        db_result = table.get_item(Key={'id': player_id})
        assert 'Item' in db_result
        assert db_result['Item']['name'] == update_data['name']
        assert db_result['Item']['phone'] == update_data['phone']
        assert int(db_result['Item']['totalWins']) == update_data['totalWins']

    def test_update_player_not_found(self, setup_dynamodb_tables):
        """Test updating a non-existent player."""
        # Arrange
        player_id = 'non-existent-player'
        update_data = {
            'name': 'Non Existent',
            'phone': '555-000-0000'
        }
        
        event = {
            'arguments': {
                'id': player_id,
                'input': update_data
            },
            'info': {
                'fieldName': 'updatePlayer',
                'parentTypeName': 'Mutation'
            }
        }
        
        # Mock the getPlayer function to return None (player not found)
        with patch('playerResolvers.getPlayer', return_value=None):
            # Act & Assert
            with pytest.raises(Exception) as excinfo:
                playerResolvers.updatePlayer(event)
            
            assert f"Player with ID {player_id} not found" in str(excinfo.value)
