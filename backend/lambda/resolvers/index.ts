import { AppSyncResolverHandler } from 'aws-lambda';
import * as playerResolvers from './playerResolvers';
import * as scheduleResolvers from './scheduleResolvers';
import * as swapRequestResolvers from './swapRequestResolvers';
import * as scoreResolvers from './scoreResolvers';

// Define the resolver map
const resolvers: Record<string, Record<string, any>> = {
  Query: {
    // Player queries
    getPlayer: playerResolvers.getPlayer,
    listPlayers: playerResolvers.listPlayers,
    getPlayerByEmail: playerResolvers.getPlayerByEmail,
    
    // Schedule queries
    getSchedule: scheduleResolvers.getSchedule,
    listSchedules: scheduleResolvers.listSchedules,
    getSchedulesByDate: scheduleResolvers.getSchedulesByDate,
    getPlayerSchedules: scheduleResolvers.getPlayerSchedules,
    
    // Swap request queries
    getSwapRequest: swapRequestResolvers.getSwapRequest,
    listSwapRequests: swapRequestResolvers.listSwapRequests,
    getSwapRequestsByRequestor: swapRequestResolvers.getSwapRequestsByRequestor,
    getSwapRequestsByTarget: swapRequestResolvers.getSwapRequestsByTarget,
    getSwapRequestsByStatus: swapRequestResolvers.getSwapRequestsByStatus,
    
    // Score queries
    getScore: scoreResolvers.getScore,
    listScores: scoreResolvers.listScores,
    getScoresByPlayer: scoreResolvers.getScoresByPlayer,
    getScoresBySchedule: scoreResolvers.getScoresBySchedule,
  },
  Mutation: {
    // Player mutations
    createPlayer: playerResolvers.createPlayer,
    updatePlayer: playerResolvers.updatePlayer,
    
    // Schedule mutations
    createSchedule: scheduleResolvers.createSchedule,
    updateSchedule: scheduleResolvers.updateSchedule,
    
    // Swap request mutations
    createSwapRequest: swapRequestResolvers.createSwapRequest,
    updateSwapRequest: swapRequestResolvers.updateSwapRequest,
    acceptSwapRequest: swapRequestResolvers.acceptSwapRequest,
    rejectSwapRequest: swapRequestResolvers.rejectSwapRequest,
    adminOverrideSwapRequest: swapRequestResolvers.adminOverrideSwapRequest,
    
    // Score mutations
    createScore: scoreResolvers.createScore,
    updateScore: scoreResolvers.updateScore,
  },
};

// Main handler function
export const handler: AppSyncResolverHandler<any, any> = async (event) => {
  console.log('Event:', JSON.stringify(event, null, 2));
  
  const typeName = event.info.parentTypeName;
  const fieldName = event.info.fieldName;
  
  if (resolvers[typeName] && resolvers[typeName][fieldName]) {
    return await resolvers[typeName][fieldName](event);
  }
  
  throw new Error(`Resolver for ${typeName}.${fieldName} not found`);
};
