# Golf League Manager Deployment Plan

## Overview
This document outlines the steps to deploy the Golf League Manager application to AWS. The application follows a serverless architecture using AWS services such as Cognito, DynamoDB, AppSync, Lambda, S3, and CloudFront.

## Prerequisites
- AWS CLI configured with appropriate credentials
- Node.js and npm installed
- AWS CDK installed globally (`npm install -g aws-cdk`)
- Git configured for version control

## Deployment Steps

### 1. Code Repository Setup
- [x] Initialize Git repository
- [x] Create GitHub repository
- [x] Push initial codebase to GitHub
- [x] Create feature branch for development
- [x] Fix deprecated CDK constructs
- [x] Commit and push changes to GitHub

### 2. Frontend Build
- [ ] Install frontend dependencies:
  ```
  cd frontend
  npm install --legacy-peer-deps
  ```
- [ ] Build the frontend:
  ```
  npm run build
  ```
- [ ] Commit the build artifacts to the repository

### 3. Backend Deployment
- [ ] Bootstrap AWS CDK:
  ```
  cd backend
  cdk bootstrap
  ```
- [ ] Deploy the Auth Stack:
  ```
  cdk deploy GolfLeagueManagerAuthStack
  ```
- [ ] Deploy the Storage Stack:
  ```
  cdk deploy GolfLeagueManagerStorageStack
  ```
- [ ] Deploy the API Stack:
  ```
  cdk deploy GolfLeagueManagerApiStack
  ```
- [ ] Deploy the Frontend Stack:
  ```
  cdk deploy GolfLeagueManagerFrontendStack
  ```

### 4. Post-Deployment Configuration
- [ ] Create initial admin user in Cognito
- [ ] Populate DynamoDB tables with initial data
- [ ] Verify API functionality
- [ ] Verify frontend access via CloudFront URL

### 5. Testing
- [ ] Test user authentication
- [ ] Test player management
- [ ] Test schedule management
- [ ] Test swap request functionality
- [ ] Test score tracking

## Rollback Plan
In case of deployment issues, the following rollback steps should be followed:
1. Destroy the stacks in reverse order:
   ```
   cdk destroy GolfLeagueManagerFrontendStack
   cdk destroy GolfLeagueManagerApiStack
   cdk destroy GolfLeagueManagerStorageStack
   cdk destroy GolfLeagueManagerAuthStack
   ```
2. Revert to the previous stable Git commit
3. Redeploy using the stable version

## Monitoring and Maintenance
- Set up CloudWatch alarms for Lambda errors
- Monitor DynamoDB capacity
- Set up regular backups of DynamoDB tables
- Implement CI/CD pipeline for future updates

## Security Considerations
- Ensure Cognito user pool is properly configured with MFA
- Review IAM permissions for least privilege
- Implement WAF for API protection
- Set up security scanning for the codebase
