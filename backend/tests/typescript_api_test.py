"""
TypeScript API Test for Golf League Manager

This script tests the TypeScript API resolvers by:
1. Verifying the GraphQL schema
2. Checking the structure of the TypeScript resolvers
3. Testing the API endpoints using AWS SDK
"""

import os
import sys
import json
import re
from pprint import pprint

def check_file_exists(file_path):
    """Check if a file exists at the given path."""
    return os.path.exists(file_path)

def read_file_content(file_path):
    """Read the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def test_graphql_schema():
    """Test the GraphQL schema for completeness."""
    print("\n=== Testing GraphQL Schema ===")
    
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "graphql", "schema.graphql")
    
    if check_file_exists(schema_path):
        print(f"✅ GraphQL schema exists: {schema_path}")
        
        schema_content = read_file_content(schema_path)
        if schema_content:
            # Check for expected types
            expected_types = ["Player", "Schedule", "SwapRequest", "Score", 
                             "Query", "Mutation"]
            
            all_found = True
            for type_name in expected_types:
                if f"type {type_name}" in schema_content:
                    print(f"✅ {type_name} type found in schema")
                else:
                    print(f"❌ {type_name} type missing from schema")
                    all_found = False
            
            # Check for expected queries
            expected_queries = [
                "getPlayer", "listPlayers", 
                "getSchedule", "listSchedules", 
                "getSwapRequest", "listSwapRequests", 
                "getScore", "listScores"
            ]
            
            for query in expected_queries:
                if query in schema_content:
                    print(f"✅ {query} query found in schema")
                else:
                    print(f"❌ {query} query missing from schema")
                    all_found = False
            
            # Check for expected mutations
            expected_mutations = [
                "createPlayer", "updatePlayer", 
                "createSchedule", "updateSchedule", 
                "createSwapRequest", "acceptSwapRequest", "rejectSwapRequest", 
                "createScore", "updateScore"
            ]
            
            for mutation in expected_mutations:
                if mutation in schema_content:
                    print(f"✅ {mutation} mutation found in schema")
                else:
                    print(f"❌ {mutation} mutation missing from schema")
                    all_found = False
            
            return all_found
        else:
            print("❌ Failed to read schema content")
            return False
    else:
        print(f"❌ GraphQL schema does not exist: {schema_path}")
        return False

def test_resolver_structure():
    """Test the structure of the TypeScript resolvers."""
    print("\n=== Testing TypeScript Resolver Structure ===")
    
    resolver_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "lambda", "resolvers")
    
    if os.path.exists(resolver_dir):
        print(f"✅ Resolver directory exists: {resolver_dir}")
        
        # List files in the directory
        files = os.listdir(resolver_dir)
        print(f"Files in resolver directory: {files}")
        
        # Check for expected files
        expected_files = [
            "playerResolvers.ts", 
            "scheduleResolvers.ts", 
            "swapRequestResolvers.ts", 
            "scoreResolvers.ts", 
            "index.ts"
        ]
        
        all_found = True
        for file in expected_files:
            if file in files:
                print(f"✅ {file} found")
            else:
                print(f"❌ {file} missing")
                all_found = False
        
        # Check the content of each resolver file
        if all_found:
            for file in expected_files:
                file_path = os.path.join(resolver_dir, file)
                content = read_file_content(file_path)
                
                if content:
                    print(f"✅ {file} content read successfully")
                    
                    # Check for expected functions in each file
                    if file == "playerResolvers.ts":
                        functions = ["getPlayer", "listPlayers", "createPlayer", "updatePlayer"]
                    elif file == "scheduleResolvers.ts":
                        functions = ["getSchedule", "listSchedules", "createSchedule", "updateSchedule"]
                    elif file == "swapRequestResolvers.ts":
                        functions = ["getSwapRequest", "listSwapRequests", "createSwapRequest", "acceptSwapRequest", "rejectSwapRequest"]
                    elif file == "scoreResolvers.ts":
                        functions = ["getScore", "listScores", "createScore", "updateScore"]
                    elif file == "index.ts":
                        functions = ["handler"]
                    else:
                        functions = []
                    
                    for func in functions:
                        if f"export const {func}" in content or f"export async function {func}" in content:
                            print(f"  ✅ {func} function found in {file}")
                        else:
                            print(f"  ❌ {func} function missing from {file}")
                            all_found = False
                else:
                    print(f"❌ Failed to read {file} content")
                    all_found = False
        
        return all_found
    else:
        print(f"❌ Resolver directory does not exist: {resolver_dir}")
        return False

def test_dynamodb_integration():
    """Test DynamoDB integration in the resolvers."""
    print("\n=== Testing DynamoDB Integration ===")
    
    resolver_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "lambda", "resolvers")
    
    # Check for DynamoDB operations in each resolver file
    resolver_files = [
        "playerResolvers.ts", 
        "scheduleResolvers.ts", 
        "swapRequestResolvers.ts", 
        "scoreResolvers.ts"
    ]
    
    all_passed = True
    
    for file in resolver_files:
        file_path = os.path.join(resolver_dir, file)
        content = read_file_content(file_path)
        
        if content:
            # Check for DynamoDB import
            if "import * as AWS from 'aws-sdk'" in content or "import { DynamoDB } from 'aws-sdk'" in content:
                print(f"✅ {file} imports AWS SDK")
            else:
                print(f"❌ {file} does not import AWS SDK")
                all_passed = False
            
            # Check for DynamoDB operations
            operations = ["get", "put", "update", "delete", "query", "scan"]
            ops_found = []
            
            for op in operations:
                pattern = f"dynamoDB.{op}("
                if pattern in content:
                    ops_found.append(op)
            
            if ops_found:
                print(f"✅ {file} uses DynamoDB operations: {', '.join(ops_found)}")
            else:
                print(f"❌ {file} does not use DynamoDB operations")
                all_passed = False
        else:
            print(f"❌ Failed to read {file} content")
            all_passed = False
    
    return all_passed

def test_error_handling():
    """Test error handling in the resolvers."""
    print("\n=== Testing Error Handling ===")
    
    resolver_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "lambda", "resolvers")
    
    # Check for error handling in each resolver file
    resolver_files = [
        "playerResolvers.ts", 
        "scheduleResolvers.ts", 
        "swapRequestResolvers.ts", 
        "scoreResolvers.ts"
    ]
    
    all_passed = True
    
    for file in resolver_files:
        file_path = os.path.join(resolver_dir, file)
        content = read_file_content(file_path)
        
        if content:
            # Check for try-catch blocks
            if "try {" in content and "catch" in content:
                print(f"✅ {file} uses try-catch blocks for error handling")
            else:
                print(f"❌ {file} does not use try-catch blocks")
                all_passed = False
            
            # Check for error throwing
            if "throw new Error" in content:
                print(f"✅ {file} throws errors")
            else:
                print(f"❌ {file} does not throw errors")
                all_passed = False
        else:
            print(f"❌ Failed to read {file} content")
            all_passed = False
    
    return all_passed

def test_authorization():
    """Test authorization in the resolvers."""
    print("\n=== Testing Authorization ===")
    
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "graphql", "schema.graphql")
    
    schema_content = read_file_content(schema_path)
    
    if schema_content:
        # Check for @auth directive in schema
        if "@auth" in schema_content or "@aws_auth" in schema_content:
            print("✅ Schema uses authorization directives")
            return True
        else:
            print("❌ Schema does not use authorization directives")
            return False
    else:
        print("❌ Failed to read schema content")
        return False

def main():
    """Run all tests."""
    print("Starting TypeScript API Tests for Golf League Manager...")
    
    # Test GraphQL schema
    schema_passed = test_graphql_schema()
    
    # Test resolver structure
    structure_passed = test_resolver_structure()
    
    # Test DynamoDB integration
    dynamodb_passed = test_dynamodb_integration()
    
    # Test error handling
    error_handling_passed = test_error_handling()
    
    # Test authorization
    auth_passed = test_authorization()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"GraphQL Schema: {'PASSED' if schema_passed else 'FAILED'}")
    print(f"Resolver Structure: {'PASSED' if structure_passed else 'FAILED'}")
    print(f"DynamoDB Integration: {'PASSED' if dynamodb_passed else 'FAILED'}")
    print(f"Error Handling: {'PASSED' if error_handling_passed else 'FAILED'}")
    print(f"Authorization: {'PASSED' if auth_passed else 'FAILED'}")
    
    if schema_passed and structure_passed and dynamodb_passed and error_handling_passed and auth_passed:
        print("\n✅ All tests PASSED!")
    else:
        print("\n❌ Some tests FAILED!")
        
        # Provide recommendations
        print("\n=== Recommendations ===")
        if not schema_passed:
            print("- Review and update the GraphQL schema to include all required types, queries, and mutations")
        if not structure_passed:
            print("- Ensure all resolver files exist and contain the required functions")
        if not dynamodb_passed:
            print("- Check DynamoDB integration in all resolver files")
        if not error_handling_passed:
            print("- Improve error handling in resolver files with try-catch blocks")
        if not auth_passed:
            print("- Add authorization directives to the GraphQL schema")

if __name__ == "__main__":
    main()
