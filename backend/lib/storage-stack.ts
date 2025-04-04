import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

export class StorageStack extends cdk.Stack {
  public readonly playerTable: dynamodb.Table;
  public readonly scheduleTable: dynamodb.Table;
  public readonly swapRequestTable: dynamodb.Table;
  public readonly scoreTable: dynamodb.Table;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Create Player Table
    this.playerTable = new dynamodb.Table(this, 'PlayerTable', {
      tableName: 'GolfLeague-Players',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // Add GSI for email lookup
    this.playerTable.addGlobalSecondaryIndex({
      indexName: 'EmailIndex',
      partitionKey: { name: 'email', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Create Schedule Table
    this.scheduleTable = new dynamodb.Table(this, 'ScheduleTable', {
      tableName: 'GolfLeague-Schedules',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // Add GSI for date lookup
    this.scheduleTable.addGlobalSecondaryIndex({
      indexName: 'DateIndex',
      partitionKey: { name: 'date', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Create Swap Request Table
    this.swapRequestTable = new dynamodb.Table(this, 'SwapRequestTable', {
      tableName: 'GolfLeague-SwapRequests',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // Add GSIs for swap request lookups
    this.swapRequestTable.addGlobalSecondaryIndex({
      indexName: 'RequestorIdIndex',
      partitionKey: { name: 'requestorId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'createdAt', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    this.swapRequestTable.addGlobalSecondaryIndex({
      indexName: 'TargetIdIndex',
      partitionKey: { name: 'targetId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'createdAt', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    this.swapRequestTable.addGlobalSecondaryIndex({
      indexName: 'StatusIndex',
      partitionKey: { name: 'status', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'createdAt', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Create Score Table
    this.scoreTable = new dynamodb.Table(this, 'ScoreTable', {
      tableName: 'GolfLeague-Scores',
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
    });

    // Add GSIs for score lookups
    this.scoreTable.addGlobalSecondaryIndex({
      indexName: 'PlayerIdIndex',
      partitionKey: { name: 'playerId', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    this.scoreTable.addGlobalSecondaryIndex({
      indexName: 'ScheduleIdIndex',
      partitionKey: { name: 'scheduleId', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    });

    // Outputs
    new cdk.CfnOutput(this, 'PlayerTableName', {
      value: this.playerTable.tableName,
      description: 'The name of the player table',
    });

    new cdk.CfnOutput(this, 'ScheduleTableName', {
      value: this.scheduleTable.tableName,
      description: 'The name of the schedule table',
    });

    new cdk.CfnOutput(this, 'SwapRequestTableName', {
      value: this.swapRequestTable.tableName,
      description: 'The name of the swap request table',
    });

    new cdk.CfnOutput(this, 'ScoreTableName', {
      value: this.scoreTable.tableName,
      description: 'The name of the score table',
    });
  }
}
