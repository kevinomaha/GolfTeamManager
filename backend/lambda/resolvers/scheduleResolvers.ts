import { AppSyncResolverEvent } from 'aws-lambda';
import { DynamoDB } from 'aws-sdk';
import { v4 as uuidv4 } from 'uuid';

const dynamoDB = new DynamoDB.DocumentClient();
const SCHEDULE_TABLE = process.env.SCHEDULE_TABLE || 'GolfLeague-Schedules';
const PLAYER_TABLE = process.env.PLAYER_TABLE || 'GolfLeague-Players';

// Get a schedule by ID
export const getSchedule = async (event: AppSyncResolverEvent<{ id: string }, any>) => {
  const { id } = event.arguments;
  
  try {
    const result = await dynamoDB.get({
      TableName: SCHEDULE_TABLE,
      Key: { id }
    }).promise();
    
    if (!result.Item) {
      return null;
    }
    
    // Fetch player details
    const schedule = result.Item;
    if (schedule.playerIds && schedule.playerIds.length > 0) {
      const playerPromises = schedule.playerIds.map((playerId: string) => 
        dynamoDB.get({
          TableName: PLAYER_TABLE,
          Key: { id: playerId }
        }).promise()
      );
      
      const playerResults = await Promise.all(playerPromises);
      schedule.players = playerResults.map(result => result.Item).filter(Boolean);
    } else {
      schedule.players = [];
    }
    
    return schedule;
  } catch (error) {
    console.error('Error getting schedule:', error);
    throw error;
  }
};

// List all schedules
export const listSchedules = async () => {
  try {
    const result = await dynamoDB.scan({
      TableName: SCHEDULE_TABLE
    }).promise();
    
    const schedules = result.Items || [];
    
    // Fetch player details for each schedule
    for (const schedule of schedules) {
      if (schedule.playerIds && schedule.playerIds.length > 0) {
        const playerPromises = schedule.playerIds.map((playerId: string) => 
          dynamoDB.get({
            TableName: PLAYER_TABLE,
            Key: { id: playerId }
          }).promise()
        );
        
        const playerResults = await Promise.all(playerPromises);
        schedule.players = playerResults.map(result => result.Item).filter(Boolean);
      } else {
        schedule.players = [];
      }
    }
    
    return schedules;
  } catch (error) {
    console.error('Error listing schedules:', error);
    throw error;
  }
};

// Get schedules by date
export const getSchedulesByDate = async (event: AppSyncResolverEvent<{ date: string }, any>) => {
  const { date } = event.arguments;
  
  try {
    const result = await dynamoDB.query({
      TableName: SCHEDULE_TABLE,
      IndexName: 'DateIndex',
      KeyConditionExpression: '#date = :date',
      ExpressionAttributeNames: {
        '#date': 'date'
      },
      ExpressionAttributeValues: {
        ':date': date
      }
    }).promise();
    
    const schedules = result.Items || [];
    
    // Fetch player details for each schedule
    for (const schedule of schedules) {
      if (schedule.playerIds && schedule.playerIds.length > 0) {
        const playerPromises = schedule.playerIds.map((playerId: string) => 
          dynamoDB.get({
            TableName: PLAYER_TABLE,
            Key: { id: playerId }
          }).promise()
        );
        
        const playerResults = await Promise.all(playerPromises);
        schedule.players = playerResults.map(result => result.Item).filter(Boolean);
      } else {
        schedule.players = [];
      }
    }
    
    return schedules;
  } catch (error) {
    console.error('Error getting schedules by date:', error);
    throw error;
  }
};

// Get schedules for a player
export const getPlayerSchedules = async (event: AppSyncResolverEvent<{ playerId: string }, any>) => {
  const { playerId } = event.arguments;
  
  try {
    // We need to scan the table since we don't have a GSI for playerIds
    const result = await dynamoDB.scan({
      TableName: SCHEDULE_TABLE,
      FilterExpression: 'contains(playerIds, :playerId)',
      ExpressionAttributeValues: {
        ':playerId': playerId
      }
    }).promise();
    
    const schedules = result.Items || [];
    
    // Fetch player details for each schedule
    for (const schedule of schedules) {
      if (schedule.playerIds && schedule.playerIds.length > 0) {
        const playerPromises = schedule.playerIds.map((id: string) => 
          dynamoDB.get({
            TableName: PLAYER_TABLE,
            Key: { id }
          }).promise()
        );
        
        const playerResults = await Promise.all(playerPromises);
        schedule.players = playerResults.map(result => result.Item).filter(Boolean);
      } else {
        schedule.players = [];
      }
    }
    
    return schedules;
  } catch (error) {
    console.error('Error getting player schedules:', error);
    throw error;
  }
};

// Create a new schedule
export const createSchedule = async (event: AppSyncResolverEvent<{ input: any }, any>) => {
  const { input } = event.arguments;
  const id = uuidv4();
  
  const schedule = {
    id,
    date: input.date,
    time: input.time,
    course: input.course,
    playerIds: input.playerIds || [],
    notes: input.notes || null,
    isCompleted: input.isCompleted || false
  };
  
  try {
    // Update the weeksScheduled count for each player
    if (schedule.playerIds && schedule.playerIds.length > 0) {
      const playerUpdatePromises = schedule.playerIds.map((playerId: string) => 
        dynamoDB.update({
          TableName: PLAYER_TABLE,
          Key: { id: playerId },
          UpdateExpression: 'ADD weeksScheduled :inc',
          ExpressionAttributeValues: {
            ':inc': 1
          }
        }).promise()
      );
      
      await Promise.all(playerUpdatePromises);
    }
    
    // Create the schedule
    await dynamoDB.put({
      TableName: SCHEDULE_TABLE,
      Item: schedule,
      ConditionExpression: 'attribute_not_exists(id)'
    }).promise();
    
    // Fetch player details for the response
    if (schedule.playerIds && schedule.playerIds.length > 0) {
      const playerPromises = schedule.playerIds.map((playerId: string) => 
        dynamoDB.get({
          TableName: PLAYER_TABLE,
          Key: { id: playerId }
        }).promise()
      );
      
      const playerResults = await Promise.all(playerPromises);
      schedule.players = playerResults.map(result => result.Item).filter(Boolean);
    } else {
      schedule.players = [];
    }
    
    return schedule;
  } catch (error) {
    console.error('Error creating schedule:', error);
    throw error;
  }
};

// Update an existing schedule
export const updateSchedule = async (event: AppSyncResolverEvent<{ id: string, input: any }, any>) => {
  const { id, input } = event.arguments;
  
  try {
    // Get the current schedule first
    const currentScheduleResult = await dynamoDB.get({
      TableName: SCHEDULE_TABLE,
      Key: { id }
    }).promise();
    
    const currentSchedule = currentScheduleResult.Item;
    if (!currentSchedule) {
      throw new Error(`Schedule with ID ${id} not found`);
    }
    
    // Handle player changes if playerIds are being updated
    if (input.playerIds) {
      const currentPlayerIds = currentSchedule.playerIds || [];
      const newPlayerIds = input.playerIds;
      
      // Players to remove (decrement weeksScheduled)
      const playersToRemove = currentPlayerIds.filter((playerId: string) => !newPlayerIds.includes(playerId));
      if (playersToRemove.length > 0) {
        const removePromises = playersToRemove.map((playerId: string) => 
          dynamoDB.update({
            TableName: PLAYER_TABLE,
            Key: { id: playerId },
            UpdateExpression: 'ADD weeksScheduled :dec',
            ExpressionAttributeValues: {
              ':dec': -1
            }
          }).promise()
        );
        
        await Promise.all(removePromises);
      }
      
      // Players to add (increment weeksScheduled)
      const playersToAdd = newPlayerIds.filter((playerId: string) => !currentPlayerIds.includes(playerId));
      if (playersToAdd.length > 0) {
        const addPromises = playersToAdd.map((playerId: string) => 
          dynamoDB.update({
            TableName: PLAYER_TABLE,
            Key: { id: playerId },
            UpdateExpression: 'ADD weeksScheduled :inc',
            ExpressionAttributeValues: {
              ':inc': 1
            }
          }).promise()
        );
        
        await Promise.all(addPromises);
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
    
    // Update the schedule
    const result = await dynamoDB.update({
      TableName: SCHEDULE_TABLE,
      Key: { id },
      UpdateExpression: updateExpression,
      ExpressionAttributeNames: expressionAttributeNames,
      ExpressionAttributeValues: expressionAttributeValues,
      ReturnValues: 'ALL_NEW'
    }).promise();
    
    const updatedSchedule = result.Attributes;
    
    // Fetch player details for the response
    if (updatedSchedule.playerIds && updatedSchedule.playerIds.length > 0) {
      const playerPromises = updatedSchedule.playerIds.map((playerId: string) => 
        dynamoDB.get({
          TableName: PLAYER_TABLE,
          Key: { id: playerId }
        }).promise()
      );
      
      const playerResults = await Promise.all(playerPromises);
      updatedSchedule.players = playerResults.map(result => result.Item).filter(Boolean);
    } else {
      updatedSchedule.players = [];
    }
    
    return updatedSchedule;
  } catch (error) {
    console.error('Error updating schedule:', error);
    throw error;
  }
};
