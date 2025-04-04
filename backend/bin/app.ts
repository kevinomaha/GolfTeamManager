#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AuthStack } from '../lib/auth-stack';
import { StorageStack } from '../lib/storage-stack';
import { ApiStack } from '../lib/api-stack';
import { FrontendStack } from '../lib/frontend-stack';

const app = new cdk.App();

// Define environment
const env = { 
  account: process.env.CDK_DEFAULT_ACCOUNT, 
  region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
};

// Create stacks
const authStack = new AuthStack(app, 'GolfLeagueManagerAuthStack', { env });
const storageStack = new StorageStack(app, 'GolfLeagueManagerStorageStack', { env });
const apiStack = new ApiStack(app, 'GolfLeagueManagerApiStack', {
  env,
  userPool: authStack.userPool,
  userPoolClient: authStack.userPoolClient,
  playerTable: storageStack.playerTable,
  scheduleTable: storageStack.scheduleTable,
  swapRequestTable: storageStack.swapRequestTable,
  scoreTable: storageStack.scoreTable
});
const frontendStack = new FrontendStack(app, 'GolfLeagueManagerFrontendStack', {
  env,
  userPool: authStack.userPool,
  userPoolClient: authStack.userPoolClient,
  apiEndpoint: apiStack.apiEndpoint
});

// Add tags to all resources
cdk.Tags.of(app).add('Project', 'GolfLeagueManager');
cdk.Tags.of(app).add('Environment', 'Dev');
