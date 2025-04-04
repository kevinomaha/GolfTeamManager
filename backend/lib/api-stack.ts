import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as appsync from 'aws-cdk-lib/aws-appsync';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as path from 'path';

interface ApiStackProps extends cdk.StackProps {
  userPool: cognito.UserPool;
  userPoolClient: cognito.UserPoolClient;
  playerTable: dynamodb.Table;
  scheduleTable: dynamodb.Table;
  swapRequestTable: dynamodb.Table;
  scoreTable: dynamodb.Table;
}

export class ApiStack extends cdk.Stack {
  public readonly apiEndpoint: string;

  constructor(scope: Construct, id: string, props: ApiStackProps) {
    super(scope, id, props);

    // Create AppSync API
    const api = new appsync.GraphqlApi(this, 'GolfLeagueAPI', {
      name: 'GolfLeagueManagerAPI',
      schema: appsync.SchemaFile.fromAsset(path.join(__dirname, '../graphql/schema.graphql')),
      authorizationConfig: {
        defaultAuthorization: {
          authorizationType: appsync.AuthorizationType.USER_POOL,
          userPoolConfig: {
            userPool: props.userPool,
            appIdClientRegex: props.userPoolClient.userPoolClientId,
            defaultAction: appsync.UserPoolDefaultAction.ALLOW,
          },
        },
        additionalAuthorizationModes: [
          {
            authorizationType: appsync.AuthorizationType.IAM,
          },
        ],
      },
      xrayEnabled: true,
    });

    // Create Lambda function for resolvers
    const resolverFunction = new lambda.Function(this, 'ApiResolverFunction', {
      runtime: lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset(path.join(__dirname, '../lambda/resolvers')),
      memorySize: 1024,
      timeout: cdk.Duration.seconds(30),
      environment: {
        PLAYER_TABLE: props.playerTable.tableName,
        SCHEDULE_TABLE: props.scheduleTable.tableName,
        SWAP_REQUEST_TABLE: props.swapRequestTable.tableName,
        SCORE_TABLE: props.scoreTable.tableName,
      },
    });

    // Grant permissions to Lambda
    props.playerTable.grantReadWriteData(resolverFunction);
    props.scheduleTable.grantReadWriteData(resolverFunction);
    props.swapRequestTable.grantReadWriteData(resolverFunction);
    props.scoreTable.grantReadWriteData(resolverFunction);

    // Create data sources
    const lambdaDataSource = api.addLambdaDataSource('LambdaDataSource', resolverFunction);

    // Create resolvers
    // Player resolvers
    lambdaDataSource.createResolver('GetPlayerResolver', {
      typeName: 'Query',
      fieldName: 'getPlayer',
    });

    lambdaDataSource.createResolver('ListPlayersResolver', {
      typeName: 'Query',
      fieldName: 'listPlayers',
    });

    lambdaDataSource.createResolver('CreatePlayerResolver', {
      typeName: 'Mutation',
      fieldName: 'createPlayer',
    });

    lambdaDataSource.createResolver('UpdatePlayerResolver', {
      typeName: 'Mutation',
      fieldName: 'updatePlayer',
    });

    // Schedule resolvers
    lambdaDataSource.createResolver('GetScheduleResolver', {
      typeName: 'Query',
      fieldName: 'getSchedule',
    });

    lambdaDataSource.createResolver('ListSchedulesResolver', {
      typeName: 'Query',
      fieldName: 'listSchedules',
    });

    lambdaDataSource.createResolver('CreateScheduleResolver', {
      typeName: 'Mutation',
      fieldName: 'createSchedule',
    });

    lambdaDataSource.createResolver('UpdateScheduleResolver', {
      typeName: 'Mutation',
      fieldName: 'updateSchedule',
    });

    // Swap request resolvers
    lambdaDataSource.createResolver('GetSwapRequestResolver', {
      typeName: 'Query',
      fieldName: 'getSwapRequest',
    });

    lambdaDataSource.createResolver('ListSwapRequestsResolver', {
      typeName: 'Query',
      fieldName: 'listSwapRequests',
    });

    lambdaDataSource.createResolver('CreateSwapRequestResolver', {
      typeName: 'Mutation',
      fieldName: 'createSwapRequest',
    });

    lambdaDataSource.createResolver('UpdateSwapRequestResolver', {
      typeName: 'Mutation',
      fieldName: 'updateSwapRequest',
    });

    // Score resolvers
    lambdaDataSource.createResolver('GetScoreResolver', {
      typeName: 'Query',
      fieldName: 'getScore',
    });

    lambdaDataSource.createResolver('ListScoresResolver', {
      typeName: 'Query',
      fieldName: 'listScores',
    });

    lambdaDataSource.createResolver('CreateScoreResolver', {
      typeName: 'Mutation',
      fieldName: 'createScore',
    });

    lambdaDataSource.createResolver('UpdateScoreResolver', {
      typeName: 'Mutation',
      fieldName: 'updateScore',
    });

    // Store API endpoint
    this.apiEndpoint = api.graphqlUrl;

    // Outputs
    new cdk.CfnOutput(this, 'GraphQLAPIURL', {
      value: api.graphqlUrl,
      description: 'The URL of the GraphQL API',
    });

    new cdk.CfnOutput(this, 'GraphQLAPIID', {
      value: api.apiId,
      description: 'The ID of the GraphQL API',
    });
  }
}
