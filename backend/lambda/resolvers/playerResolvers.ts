import { AppSyncResolverEvent } from 'aws-lambda';
import { DynamoDB } from 'aws-sdk';
import { v4 as uuidv4 } from 'uuid';

const dynamoDB = new DynamoDB.DocumentClient();
const PLAYER_TABLE = process.env.PLAYER_TABLE || 'GolfLeague-Players';

// Get a player by ID
export const getPlayer = async (event: AppSyncResolverEvent<{ id: string }, any>) => {
  const { id } = event.arguments;
  
  try {
    const result = await dynamoDB.get({
      TableName: PLAYER_TABLE,
      Key: { id }
    }).promise();
    
    return result.Item;
  } catch (error) {
    console.error('Error getting player:', error);
    throw error;
  }
};

// List all players
export const listPlayers = async () => {
  try {
    const result = await dynamoDB.scan({
      TableName: PLAYER_TABLE
    }).promise();
    
    return result.Items;
  } catch (error) {
    console.error('Error listing players:', error);
    throw error;
  }
};

// Get a player by email
export const getPlayerByEmail = async (event: AppSyncResolverEvent<{ email: string }, any>) => {
  const { email } = event.arguments;
  
  try {
    const result = await dynamoDB.query({
      TableName: PLAYER_TABLE,
      IndexName: 'EmailIndex',
      KeyConditionExpression: 'email = :email',
      ExpressionAttributeValues: {
        ':email': email
      }
    }).promise();
    
    return result.Items && result.Items.length > 0 ? result.Items[0] : null;
  } catch (error) {
    console.error('Error getting player by email:', error);
    throw error;
  }
};

// Create a new player
export const createPlayer = async (event: AppSyncResolverEvent<{ input: any }, any>) => {
  const { input } = event.arguments;
  const id = uuidv4();
  
  const player = {
    id,
    email: input.email,
    name: input.name,
    phone: input.phone || null,
    weeksScheduled: 0,
    isAdmin: input.isAdmin || false,
    totalWins: 0,
    totalLosses: 0
  };
  
  try {
    await dynamoDB.put({
      TableName: PLAYER_TABLE,
      Item: player,
      ConditionExpression: 'attribute_not_exists(id)'
    }).promise();
    
    return player;
  } catch (error) {
    console.error('Error creating player:', error);
    throw error;
  }
};

// Update an existing player
export const updatePlayer = async (event: AppSyncResolverEvent<{ id: string, input: any }, any>) => {
  const { id, input } = event.arguments;
  
  // Build update expression
  let updateExpression = 'set';
  const expressionAttributeNames: Record<string, string> = {};
  const expressionAttributeValues: Record<string, any> = {};
  
  Object.entries(input).forEach(([key, value], index) => {
    const prefix = index === 0 ? ' ' : ', ';
    const attributeName = `#${key}`;
    const attributeValue = `:${key}`;
    
    updateExpression += `${prefix}${attributeName} = ${attributeValue}`;
    expressionAttributeNames[attributeName] = key;
    expressionAttributeValues[attributeValue] = value;
  });
  
  try {
    // Get the current player first
    const currentPlayer = await getPlayer({ arguments: { id } } as any);
    
    if (!currentPlayer) {
      throw new Error(`Player with ID ${id} not found`);
    }
    
    // Update the player
    const result = await dynamoDB.update({
      TableName: PLAYER_TABLE,
      Key: { id },
      UpdateExpression: updateExpression,
      ExpressionAttributeNames: expressionAttributeNames,
      ExpressionAttributeValues: expressionAttributeValues,
      ReturnValues: 'ALL_NEW'
    }).promise();
    
    return result.Attributes;
  } catch (error) {
    console.error('Error updating player:', error);
    throw error;
  }
};
