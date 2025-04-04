# Golf League Manager

A serverless web application to manage a golf league schedule, player swaps, scoring, and communications.

## Overview

This application manages a 10-player golf league running from April 28th to August 18th, 2025, with 4 players scheduled each week. It handles player schedules, facilitates swaps, tracks scores, and enables communications.

## Features

- Authentication & User Management
- Schedule Management
- Swap Management
- Score Tracking
- Communications
- Admin Functions

## Architecture

- **Frontend**: React SPA with Material-UI
- **API Layer**: AWS AppSync (GraphQL)
- **Authentication**: Amazon Cognito
- **Database**: Amazon DynamoDB
- **Notifications**: Amazon SNS, Amazon SES
- **Infrastructure**: AWS CDK with TypeScript

## Development

### Prerequisites

- Node.js (v14 or later)
- AWS CLI configured with appropriate credentials
- AWS CDK installed globally

### Setup

1. Clone the repository
2. Install dependencies: `npm install`
3. Deploy the infrastructure: `npm run cdk deploy`
4. Start the local development server: `npm run start`

## Testing

- Backend: Jest for unit tests
- Frontend: React Testing Library
- E2E: Selenium

## Deployment

The application is deployed using AWS CDK to set up all required AWS resources.
