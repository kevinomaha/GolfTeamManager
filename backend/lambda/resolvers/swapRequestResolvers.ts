import { AppSyncResolverEvent } from 'aws-lambda';
import { DynamoDB } from 'aws-sdk';
import { v4 as uuidv4 } from 'uuid';

const dynamoDB = new DynamoDB.DocumentClient();
const SWAP_REQUEST_TABLE = process.env.SWAP_REQUEST_TABLE || 'GolfLeague-SwapRequests';
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

// Helper function to populate swap request with related entities
const populateSwapRequest = async (swapRequest: any) => {
  if (!swapRequest) return null;
  
  // Get requestor details
  swapRequest.requestor = await getPlayerDetails(swapRequest.requestorId);
  
  // Get target details
  swapRequest.target = await getPlayerDetails(swapRequest.targetId);
  
  // Get requestor week details
  swapRequest.requestorWeek = await getScheduleDetails(swapRequest.requestorWeekId);
  
  // Get target week details
  swapRequest.targetWeek = await getScheduleDetails(swapRequest.targetWeekId);
  
  return swapRequest;
};

// Get a swap request by ID
export const getSwapRequest = async (event: AppSyncResolverEvent<{ id: string }, any>) => {
  const { id } = event.arguments;
  
  try {
    const result = await dynamoDB.get({
      TableName: SWAP_REQUEST_TABLE,
      Key: { id }
    }).promise();
    
    return await populateSwapRequest(result.Item);
  } catch (error) {
    console.error('Error getting swap request:', error);
    throw error;
  }
};

// List all swap requests
export const listSwapRequests = async () => {
  try {
    const result = await dynamoDB.scan({
      TableName: SWAP_REQUEST_TABLE
    }).promise();
    
    const swapRequests = result.Items || [];
    
    // Populate each swap request with related entities
    const populatedRequests = await Promise.all(
      swapRequests.map(request => populateSwapRequest(request))
    );
    
    return populatedRequests;
  } catch (error) {
    console.error('Error listing swap requests:', error);
    throw error;
  }
};

// Get swap requests by requestor
export const getSwapRequestsByRequestor = async (event: AppSyncResolverEvent<{ requestorId: string }, any>) => {
  const { requestorId } = event.arguments;
  
  try {
    const result = await dynamoDB.query({
      TableName: SWAP_REQUEST_TABLE,
      IndexName: 'RequestorIdIndex',
      KeyConditionExpression: 'requestorId = :requestorId',
      ExpressionAttributeValues: {
        ':requestorId': requestorId
      }
    }).promise();
    
    const swapRequests = result.Items || [];
    
    // Populate each swap request with related entities
    const populatedRequests = await Promise.all(
      swapRequests.map(request => populateSwapRequest(request))
    );
    
    return populatedRequests;
  } catch (error) {
    console.error('Error getting swap requests by requestor:', error);
    throw error;
  }
};

// Get swap requests by target
export const getSwapRequestsByTarget = async (event: AppSyncResolverEvent<{ targetId: string }, any>) => {
  const { targetId } = event.arguments;
  
  try {
    const result = await dynamoDB.query({
      TableName: SWAP_REQUEST_TABLE,
      IndexName: 'TargetIdIndex',
      KeyConditionExpression: 'targetId = :targetId',
      ExpressionAttributeValues: {
        ':targetId': targetId
      }
    }).promise();
    
    const swapRequests = result.Items || [];
    
    // Populate each swap request with related entities
    const populatedRequests = await Promise.all(
      swapRequests.map(request => populateSwapRequest(request))
    );
    
    return populatedRequests;
  } catch (error) {
    console.error('Error getting swap requests by target:', error);
    throw error;
  }
};

// Get swap requests by status
export const getSwapRequestsByStatus = async (event: AppSyncResolverEvent<{ status: string }, any>) => {
  const { status } = event.arguments;
  
  try {
    const result = await dynamoDB.query({
      TableName: SWAP_REQUEST_TABLE,
      IndexName: 'StatusIndex',
      KeyConditionExpression: '#status = :status',
      ExpressionAttributeNames: {
        '#status': 'status'
      },
      ExpressionAttributeValues: {
        ':status': status
      }
    }).promise();
    
    const swapRequests = result.Items || [];
    
    // Populate each swap request with related entities
    const populatedRequests = await Promise.all(
      swapRequests.map(request => populateSwapRequest(request))
    );
    
    return populatedRequests;
  } catch (error) {
    console.error('Error getting swap requests by status:', error);
    throw error;
  }
};

// Create a new swap request
export const createSwapRequest = async (event: AppSyncResolverEvent<{ input: any }, any>) => {
  const { input } = event.arguments;
  const id = uuidv4();
  
  const swapRequest = {
    id,
    requestorId: input.requestorId,
    requestorWeekId: input.requestorWeekId,
    targetId: input.targetId,
    targetWeekId: input.targetWeekId,
    proposedDate: input.proposedDate,
    reason: input.reason || null,
    status: 'PENDING',
    createdAt: new Date().toISOString()
  };
  
  try {
    // Verify that the requestor is scheduled for the requestor week
    const requestorWeek = await getScheduleDetails(input.requestorWeekId);
    if (!requestorWeek.playerIds.includes(input.requestorId)) {
      throw new Error('Requestor is not scheduled for the specified week');
    }
    
    // Verify that the target is scheduled for the target week
    const targetWeek = await getScheduleDetails(input.targetWeekId);
    if (!targetWeek.playerIds.includes(input.targetId)) {
      throw new Error('Target is not scheduled for the specified week');
    }
    
    // Create the swap request
    await dynamoDB.put({
      TableName: SWAP_REQUEST_TABLE,
      Item: swapRequest,
      ConditionExpression: 'attribute_not_exists(id)'
    }).promise();
    
    // Populate the swap request with related entities for the response
    return await populateSwapRequest(swapRequest);
  } catch (error) {
    console.error('Error creating swap request:', error);
    throw error;
  }
};

// Update a swap request
export const updateSwapRequest = async (event: AppSyncResolverEvent<{ id: string, input: any }, any>) => {
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
    // Get the current swap request
    const currentSwapRequest = await getSwapRequest({ arguments: { id } } as any);
    
    if (!currentSwapRequest) {
      throw new Error(`Swap request with ID ${id} not found`);
    }
    
    // Update the swap request
    const result = await dynamoDB.update({
      TableName: SWAP_REQUEST_TABLE,
      Key: { id },
      UpdateExpression: updateExpression,
      ExpressionAttributeNames: expressionAttributeNames,
      ExpressionAttributeValues: expressionAttributeValues,
      ReturnValues: 'ALL_NEW'
    }).promise();
    
    // Populate the updated swap request with related entities
    return await populateSwapRequest(result.Attributes);
  } catch (error) {
    console.error('Error updating swap request:', error);
    throw error;
  }
};

// Accept a swap request
export const acceptSwapRequest = async (event: AppSyncResolverEvent<{ id: string }, any>) => {
  const { id } = event.arguments;
  
  try {
    // Get the current swap request
    const swapRequest = await getSwapRequest({ arguments: { id } } as any);
    
    if (!swapRequest) {
      throw new Error(`Swap request with ID ${id} not found`);
    }
    
    if (swapRequest.status !== 'PENDING') {
      throw new Error(`Swap request is not in PENDING status`);
    }
    
    // Update the swap request status
    const updateResult = await dynamoDB.update({
      TableName: SWAP_REQUEST_TABLE,
      Key: { id },
      UpdateExpression: 'set #status = :status',
      ExpressionAttributeNames: {
        '#status': 'status'
      },
      ExpressionAttributeValues: {
        ':status': 'ACCEPTED'
      },
      ReturnValues: 'ALL_NEW'
    }).promise();
    
    // Perform the actual swap in the schedules
    const requestorWeek = await getScheduleDetails(swapRequest.requestorWeekId);
    const targetWeek = await getScheduleDetails(swapRequest.targetWeekId);
    
    // Update requestor week (remove requestor, add target)
    const requestorWeekPlayerIds = requestorWeek.playerIds.filter((id: string) => id !== swapRequest.requestorId);
    requestorWeekPlayerIds.push(swapRequest.targetId);
    
    await dynamoDB.update({
      TableName: SCHEDULE_TABLE,
      Key: { id: swapRequest.requestorWeekId },
      UpdateExpression: 'set playerIds = :playerIds',
      ExpressionAttributeValues: {
        ':playerIds': requestorWeekPlayerIds
      }
    }).promise();
    
    // Update target week (remove target, add requestor)
    const targetWeekPlayerIds = targetWeek.playerIds.filter((id: string) => id !== swapRequest.targetId);
    targetWeekPlayerIds.push(swapRequest.requestorId);
    
    await dynamoDB.update({
      TableName: SCHEDULE_TABLE,
      Key: { id: swapRequest.targetWeekId },
      UpdateExpression: 'set playerIds = :playerIds',
      ExpressionAttributeValues: {
        ':playerIds': targetWeekPlayerIds
      }
    }).promise();
    
    // Populate the updated swap request with related entities
    return await populateSwapRequest(updateResult.Attributes);
  } catch (error) {
    console.error('Error accepting swap request:', error);
    throw error;
  }
};

// Reject a swap request
export const rejectSwapRequest = async (event: AppSyncResolverEvent<{ id: string }, any>) => {
  const { id } = event.arguments;
  
  try {
    // Get the current swap request
    const swapRequest = await getSwapRequest({ arguments: { id } } as any);
    
    if (!swapRequest) {
      throw new Error(`Swap request with ID ${id} not found`);
    }
    
    if (swapRequest.status !== 'PENDING') {
      throw new Error(`Swap request is not in PENDING status`);
    }
    
    // Update the swap request status
    const updateResult = await dynamoDB.update({
      TableName: SWAP_REQUEST_TABLE,
      Key: { id },
      UpdateExpression: 'set #status = :status',
      ExpressionAttributeNames: {
        '#status': 'status'
      },
      ExpressionAttributeValues: {
        ':status': 'REJECTED'
      },
      ReturnValues: 'ALL_NEW'
    }).promise();
    
    // Populate the updated swap request with related entities
    return await populateSwapRequest(updateResult.Attributes);
  } catch (error) {
    console.error('Error rejecting swap request:', error);
    throw error;
  }
};

// Admin override a swap request
export const adminOverrideSwapRequest = async (event: AppSyncResolverEvent<{ id: string, approved: boolean }, any>) => {
  const { id, approved } = event.arguments;
  
  try {
    // Get the current swap request
    const swapRequest = await getSwapRequest({ arguments: { id } } as any);
    
    if (!swapRequest) {
      throw new Error(`Swap request with ID ${id} not found`);
    }
    
    // Update the swap request status
    const updateResult = await dynamoDB.update({
      TableName: SWAP_REQUEST_TABLE,
      Key: { id },
      UpdateExpression: 'set #status = :status',
      ExpressionAttributeNames: {
        '#status': 'status'
      },
      ExpressionAttributeValues: {
        ':status': approved ? 'ACCEPTED' : 'REJECTED'
      },
      ReturnValues: 'ALL_NEW'
    }).promise();
    
    // If approved, perform the actual swap in the schedules
    if (approved) {
      const requestorWeek = await getScheduleDetails(swapRequest.requestorWeekId);
      const targetWeek = await getScheduleDetails(swapRequest.targetWeekId);
      
      // Update requestor week (remove requestor, add target)
      const requestorWeekPlayerIds = requestorWeek.playerIds.filter((id: string) => id !== swapRequest.requestorId);
      requestorWeekPlayerIds.push(swapRequest.targetId);
      
      await dynamoDB.update({
        TableName: SCHEDULE_TABLE,
        Key: { id: swapRequest.requestorWeekId },
        UpdateExpression: 'set playerIds = :playerIds',
        ExpressionAttributeValues: {
          ':playerIds': requestorWeekPlayerIds
        }
      }).promise();
      
      // Update target week (remove target, add requestor)
      const targetWeekPlayerIds = targetWeek.playerIds.filter((id: string) => id !== swapRequest.targetId);
      targetWeekPlayerIds.push(swapRequest.requestorId);
      
      await dynamoDB.update({
        TableName: SCHEDULE_TABLE,
        Key: { id: swapRequest.targetWeekId },
        UpdateExpression: 'set playerIds = :playerIds',
        ExpressionAttributeValues: {
          ':playerIds': targetWeekPlayerIds
        }
      }).promise();
    }
    
    // Populate the updated swap request with related entities
    return await populateSwapRequest(updateResult.Attributes);
  } catch (error) {
    console.error('Error performing admin override on swap request:', error);
    throw error;
  }
};
