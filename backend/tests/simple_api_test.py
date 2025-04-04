"""
Simple API Test for Golf League Manager

This script checks if the API resolver modules can be imported and basic functionality works.
"""

import os
import sys
import importlib.util
import json

# Add the parent directory to the path so we can import the resolver modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_module_exists(module_path):
    """Check if a module exists at the given path."""
    return os.path.exists(module_path)

def import_module(module_path, module_name):
    """Import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        return None
    
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"Error importing {module_name}: {e}")
        return None

def test_resolver_imports():
    """Test if resolver modules can be imported."""
    print("\n=== Testing Resolver Module Imports ===")
    
    resolver_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "lambda", "resolvers")
    
    resolvers = [
        ("playerResolvers.py", "playerResolvers"),
        ("scheduleResolvers.py", "scheduleResolvers"),
        ("swapRequestResolvers.py", "swapRequestResolvers"),
        ("scoreResolvers.py", "scoreResolvers"),
        ("index.py", "index")
    ]
    
    all_passed = True
    
    for file_name, module_name in resolvers:
        module_path = os.path.join(resolver_dir, file_name)
        
        if check_module_exists(module_path):
            print(f"✅ {file_name} exists")
            
            module = import_module(module_path, module_name)
            if module is not None:
                print(f"✅ {module_name} imported successfully")
                
                # Check for expected functions in each module
                if module_name == "playerResolvers":
                    functions = ["getPlayer", "listPlayers", "createPlayer", "updatePlayer"]
                elif module_name == "scheduleResolvers":
                    functions = ["getSchedule", "listSchedules", "createSchedule", "updateSchedule"]
                elif module_name == "swapRequestResolvers":
                    functions = ["getSwapRequest", "listSwapRequests", "createSwapRequest", "acceptSwapRequest"]
                elif module_name == "scoreResolvers":
                    functions = ["getScore", "listScores", "createScore", "updateScore"]
                elif module_name == "index":
                    functions = ["handler"]
                else:
                    functions = []
                
                for func in functions:
                    if hasattr(module, func):
                        print(f"  ✅ {func} function exists")
                    else:
                        print(f"  ❌ {func} function missing")
                        all_passed = False
            else:
                print(f"❌ Failed to import {module_name}")
                all_passed = False
        else:
            print(f"❌ {file_name} does not exist")
            all_passed = False
    
    return all_passed

def test_resolver_structure():
    """Test the structure of the resolver directory."""
    print("\n=== Testing Resolver Directory Structure ===")
    
    resolver_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "lambda", "resolvers")
    
    if os.path.exists(resolver_dir):
        print(f"✅ Resolver directory exists: {resolver_dir}")
        
        # List files in the directory
        files = os.listdir(resolver_dir)
        print(f"Files in resolver directory: {files}")
        
        # Check for expected files
        expected_files = ["playerResolvers.py", "scheduleResolvers.py", 
                          "swapRequestResolvers.py", "scoreResolvers.py", "index.py"]
        
        all_found = True
        for file in expected_files:
            if file in files:
                print(f"✅ {file} found")
            else:
                print(f"❌ {file} missing")
                all_found = False
        
        return all_found
    else:
        print(f"❌ Resolver directory does not exist: {resolver_dir}")
        return False

def check_graphql_schema():
    """Check if the GraphQL schema file exists and is valid."""
    print("\n=== Testing GraphQL Schema ===")
    
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "graphql", "schema.graphql")
    
    if os.path.exists(schema_path):
        print(f"✅ GraphQL schema exists: {schema_path}")
        
        # Read the schema file
        try:
            with open(schema_path, 'r') as f:
                schema = f.read()
                
            # Check for expected types
            expected_types = ["Player", "Schedule", "SwapRequest", "Score", 
                             "Query", "Mutation"]
            
            all_found = True
            for type_name in expected_types:
                if f"type {type_name}" in schema:
                    print(f"✅ {type_name} type found in schema")
                else:
                    print(f"❌ {type_name} type missing from schema")
                    all_found = False
            
            return all_found
        except Exception as e:
            print(f"❌ Error reading schema file: {e}")
            return False
    else:
        print(f"❌ GraphQL schema does not exist: {schema_path}")
        return False

def main():
    """Run all tests."""
    print("Starting Simple API Tests for Golf League Manager...")
    
    # Test resolver directory structure
    structure_passed = test_resolver_structure()
    
    # Test resolver imports
    imports_passed = test_resolver_imports()
    
    # Check GraphQL schema
    schema_passed = check_graphql_schema()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Resolver Structure: {'PASSED' if structure_passed else 'FAILED'}")
    print(f"Resolver Imports: {'PASSED' if imports_passed else 'FAILED'}")
    print(f"GraphQL Schema: {'PASSED' if schema_passed else 'FAILED'}")
    
    if structure_passed and imports_passed and schema_passed:
        print("\n✅ All tests PASSED!")
    else:
        print("\n❌ Some tests FAILED!")

if __name__ == "__main__":
    main()
