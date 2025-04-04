import { AppSyncResolverEvent } from 'aws-lambda';
import { DynamoDB } from 'aws-sdk';
import { v4 as uuidv4 } from 'uuid';

const dynamoDB = new DynamoDB.DocumentClient();
const SCORE_TABLE = process.env.SCORE_TABLE || 'GolfLeague-Scores';
const PLAYER_TABLE = process.env.PLAYER_TABLE || 'GolfLeague-Players';
const SCHEDULE_TABLE = process.env.SCHEDULE_TABLE || 'GolfLeague-Schedules';

// Helper function to get player details
const getPlayerDetails = async (playerId: string) => {
  try {
    const result = await dynamoDB.get({
      TableName: PLAYER_TABLE,
      Key: { id: playerId }
    }).promise();
    
    return result.Item;
  } catch (error) {
    console.error(`Error getting player ${playerId}:`, error);
    throw error;
  }
};

// Helper function to get schedule details
const getScheduleDetails = async (scheduleId: string) => {
  try {
    const result = await dynamoDB.get({
      TableName: SCHEDULE_TABLE,
      Key: { id: scheduleId }
    }).promise();
    
    return result.Item;
  } catch (error) {
    console.error(`Error getting schedule ${scheduleId}:`, error);
    throw error;
  }
};

// Helper function to populate score with related entities
const populateScore = async (score: any) => {
  if (!score) return null;
  
  // Get player details
  score.player = await getPlayerDetails(score.playerId);
  
  // Get schedule details
  score.schedule = await getScheduleDetails(score.scheduleId);
  
  return score;
};

// Get a score by ID
export const getScore = async (event: AppSyncResolverEvent<{ id: string }, any>) => {
  const { id } = event.arguments;
  
  try {
    const result = await dynamoDB.get({
      TableName: SCORE_TABLE,
      Key: { id }
    }).promise();
    
    return await populateScore(result.Item);
  } catch (error) {
    console.error('Error getting score:', error);
    throw error;
  }
};

// List all scores
export const listScores = async () => {
  try {
    const result = await dynamoDB.scan({
      TableName: SCORE_TABLE
    }).promise();
    
    const scores = result.Items || [];
    
    // Populate each score with related entities
    const populatedScores = await Promise.all(
      scores.map(score => populateScore(score))
    );
    
    return populatedScores;
  } catch (error) {
    console.error('Error listing scores:', error);
    throw error;
  }
};

// Get scores by player
export const getScoresByPlayer = async (event: AppSyncResolverEvent<{ playerId: string }, any>) => {
  const { playerId } = event.arguments;
  
  try {
    const result = await dynamoDB.query({
      TableName: SCORE_TABLE,
      IndexName: 'PlayerIdIndex',
      KeyConditionExpression: 'playerId = :playerId',
      ExpressionAttributeValues: {
        ':playerId': playerId
      }
    }).promise();
    
    const scores = result.Items || [];
    
    // Populate each score with related entities
    const populatedScores = await Promise.all(
      scores.map(score => populateScore(score))
    );
    
    return populatedScores;
  } catch (error) {
    console.error('Error getting scores by player:', error);
    throw error;
  }
};

// Get scores by schedule
export const getScoresBySchedule = async (event: AppSyncResolverEvent<{ scheduleId: string }, any>) => {
  const { scheduleId } = event.arguments;
  
  try {
    const result = await dynamoDB.query({
      TableName: SCORE_TABLE,
      IndexName: 'ScheduleIdIndex',
      KeyConditionExpression: 'scheduleId = :scheduleId',
      ExpressionAttributeValues: {
        ':scheduleId': scheduleId
      }
    }).promise();
    
    const scores = result.Items || [];
    
    // Populate each score with related entities
    const populatedScores = await Promise.all(
      scores.map(score => populateScore(score))
    );
    
    return populatedScores;
  } catch (error) {
    console.error('Error getting scores by schedule:', error);
    throw error;
  }
};

// Create a new score
export const createScore = async (event: AppSyncResolverEvent<{ input: any }, any>) => {
  const { input } = event.arguments;
  const id = uuidv4();
  
  const score = {
    id,
    scheduleId: input.scheduleId,
    playerId: input.playerId,
    score: input.score,
    result: input.result,
    notes: input.notes || null
  };
  
  try {
    // Verify that the player is part of the schedule
    const schedule = await getScheduleDetails(input.scheduleId);
    if (!schedule.playerIds.includes(input.playerId)) {
      throw new Error('Player is not part of the specified schedule');
    }
    
    // Create the score
    await dynamoDB.put({
      TableName: SCORE_TABLE,
      Item: score,
      ConditionExpression: 'attribute_not_exists(id)'
    }).promise();
    
    // Update player win/loss record
    if (input.result) {
      const updateExpression = input.result === 'WIN' 
        ? 'ADD totalWins :inc' 
        : input.result === 'LOSS' 
          ? 'ADD totalLosses :inc' 
          : null;
      
      if (updateExpression) {
        await dynamoDB.update({
          TableName: PLAYER_TABLE,
          Key: { id: input.playerId },
          UpdateExpression: updateExpression,
          ExpressionAttributeValues: {
            ':inc': 1
          }
        }).promise();
      }
    }
    
    // Mark schedule as completed if all players have scores
    const existingScores = await getScoresBySchedule({ arguments: { scheduleId: input.scheduleId } } as any);
    const allPlayersHaveScores = schedule.playerIds.every(playerId => 
      existingScores.some(score => score.playerId === playerId)
    );
    
    if (allPlayersHaveScores) {
      await dynamoDB.update({
        TableName: SCHEDULE_TABLE,
        Key: { id: input.scheduleId },
        UpdateExpression: 'set isCompleted = :isCompleted',
        ExpressionAttributeValues: {
          ':isCompleted': true
        }
      }).promise();
    }
    
    // Populate the score with related entities for the response
    return await populateScore(score);
  } catch (error) {
    console.error('Error creating score:', error);
    throw error;
  }
};

// Update an existing score
export const updateScore = async (event: AppSyncResolverEvent<{ id: string, input: any }, any>) => {
  const { id, input } = event.arguments;
  
  try {
    // Get the current score
    const currentScore = await getScore({ arguments: { id } } as any);
    
    if (!currentScore) {
      throw new Error(`Score with ID ${id} not found`);
    }
    
    // If result is changing, update player win/loss record
    if (input.result && input.result !== currentScore.result) {
      // Revert old result
      if (currentScore.result === 'WIN') {
        await dynamoDB.update({
          TableName: PLAYER_TABLE,
          Key: { id: currentScore.playerId },
          UpdateExpression: 'ADD totalWins :dec',
          ExpressionAttributeValues: {
            ':dec': -1
          }
        }).promise();
      } else if (currentScore.result === 'LOSS') {
        await dynamoDB.update({
          TableName: PLAYER_TABLE,
          Key: { id: currentScore.playerId },
          UpdateExpression: 'ADD totalLosses :dec',
          ExpressionAttributeValues: {
            ':dec': -1
          }
        }).promise();
      }
      
      // Apply new result
      if (input.result === 'WIN') {
        await dynamoDB.update({
          TableName: PLAYER_TABLE,
          Key: { id: currentScore.playerId },
          UpdateExpression: 'ADD totalWins :inc',
          ExpressionAttributeValues: {
            ':inc': 1
          }
        }).promise();
      } else if (input.result === 'LOSS') {
        await dynamoDB.update({
          TableName: PLAYER_TABLE,
          Key: { id: currentScore.playerId },
          UpdateExpression: 'ADD totalLosses :inc',
          ExpressionAttributeValues: {
            ':inc': 1
          }
        }).promise();
      }
    }
    
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
    
    // Update the score
    const result = await dynamoDB.update({
      TableName: SCORE_TABLE,
      Key: { id },
      UpdateExpression: updateExpression,
      ExpressionAttributeNames: expressionAttributeNames,
      ExpressionAttributeValues: expressionAttributeValues,
      ReturnValues: 'ALL_NEW'
    }).promise();
    
    // Populate the updated score with related entities
    return await populateScore(result.Attributes);
  } catch (error) {
    console.error('Error updating score:', error);
    throw error;
  }
};
