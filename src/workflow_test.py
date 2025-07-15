#!/usr/bin/env python3
"""
Test script for validating Dify workflow configuration
Provides utilities to test the LEXICON workflow without making actual API calls
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add src directory to path
sys.path.append(str(Path(__file__).parent))

from dify_workflow_clean import DifyWorkflow


class WorkflowTester:
    def __init__(self):
        self.workflow = DifyWorkflow()
        
    def test_node_connections(self) -> Dict[str, Any]:
        """Test that all nodes are properly connected."""
        config = self.workflow.create_daubert_workflow()
        nodes = {node["id"]: node for node in config["nodes"]}
        edges = config.get("edges", [])
        
        # Build adjacency list
        connections = {node_id: {"incoming": [], "outgoing": []} for node_id in nodes}
        
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            connections[source]["outgoing"].append(target)
            connections[target]["incoming"].append(source)
        
        # Check connectivity
        issues = []
        
        # Start node should have no incoming edges
        if connections["start"]["incoming"]:
            issues.append("Start node has incoming edges")
            
        # End node should have no outgoing edges
        if connections["end"]["outgoing"]:
            issues.append("End node has outgoing edges")
            
        # All other nodes should have at least one incoming and one outgoing
        for node_id, conns in connections.items():
            if node_id not in ["start", "end"]:
                if not conns["incoming"]:
                    issues.append(f"Node {node_id} has no incoming edges")
                if not conns["outgoing"]:
                    issues.append(f"Node {node_id} has no outgoing edges")
        
        return {
            "connected": len(issues) == 0,
            "issues": issues,
            "connections": connections
        }
    
    def test_variable_references(self) -> Dict[str, Any]:
        """Test that all variable references are valid."""
        config = self.workflow.create_daubert_workflow()
        
        # Extract available variables from start node
        start_vars = set()
        for node in config["nodes"]:
            if node["id"] == "start":
                for var in node["data"]["variables"]:
                    start_vars.add(f"inputs.{var['name']}")
                break
        
        # Track outputs from each node
        node_outputs = {"inputs": start_vars}
        issues = []
        
        # Process nodes in order (following edges)
        processed = set()
        to_process = ["start"]
        
        edges = {edge["source"]: edge["target"] for edge in config.get("edges", [])}
        
        while to_process:
            current = to_process.pop(0)
            if current in processed:
                continue
                
            processed.add(current)
            
            # Find node configuration
            node_config = None
            for node in config["nodes"]:
                if node["id"] == current:
                    node_config = node
                    break
            
            if not node_config:
                continue
                
            # Add node output to available variables
            if current != "start" and current != "end":
                node_outputs[current] = {f"{current}.output"}
            
            # Check variable references in prompts and contexts
            if "data" in node_config:
                data = node_config["data"]
                
                # Check prompt for variable references
                if "prompt" in data:
                    prompt = data["prompt"]
                    # Find all {{variable}} references
                    import re
                    var_refs = re.findall(r'\{\{([^}]+)\}\}', prompt)
                    
                    for var_ref in var_refs:
                        var_ref = var_ref.strip()
                        # Check if variable is available
                        var_found = False
                        for available_set in node_outputs.values():
                            if any(var_ref.startswith(av.split('.')[0]) for av in available_set):
                                var_found = True
                                break
                        
                        if not var_found and not var_ref.startswith("#"):
                            issues.append(f"Node {current}: Unknown variable reference {{{{var_ref}}}}")
                
                # Check context references
                if "context" in data:
                    context = data["context"]
                    var_refs = re.findall(r'\{\{([^}]+)\}\}', context)
                    for var_ref in var_refs:
                        var_ref = var_ref.strip()
                        var_found = False
                        for available_set in node_outputs.values():
                            if any(var_ref.startswith(av.split('.')[0]) for av in available_set):
                                var_found = True
                                break
                        
                        if not var_found:
                            issues.append(f"Node {current}: Unknown context variable {{{{var_ref}}}}")
            
            # Add next node to process
            if current in edges:
                to_process.append(edges[current])
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "available_variables": {k: list(v) for k, v in node_outputs.items()}
        }
    
    def test_required_fields(self) -> Dict[str, Any]:
        """Test that all nodes have required fields."""
        config = self.workflow.create_daubert_workflow()
        issues = []
        
        for node in config["nodes"]:
            node_id = node.get("id", "unknown")
            
            # Check required fields for all nodes
            if "type" not in node:
                issues.append(f"Node {node_id}: Missing 'type' field")
            if "data" not in node:
                issues.append(f"Node {node_id}: Missing 'data' field")
            
            # Check type-specific requirements
            if node.get("type") == "llm":
                data = node.get("data", {})
                if "model" not in data:
                    issues.append(f"Node {node_id}: LLM node missing 'model' configuration")
                if "prompt" not in data:
                    issues.append(f"Node {node_id}: LLM node missing 'prompt'")
            
            elif node.get("type") == "start":
                data = node.get("data", {})
                if "variables" not in data:
                    issues.append(f"Node {node_id}: Start node missing 'variables'")
                else:
                    for var in data["variables"]:
                        if "name" not in var:
                            issues.append(f"Node {node_id}: Variable missing 'name'")
                        if "field_type" not in var:
                            issues.append(f"Node {node_id}: Variable {var.get('name', 'unknown')} missing 'field_type'")
            
            elif node.get("type") == "end":
                data = node.get("data", {})
                if "outputs" not in data:
                    issues.append(f"Node {node_id}: End node missing 'outputs'")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def generate_test_inputs(self) -> Dict[str, Any]:
        """Generate sample test inputs based on workflow configuration."""
        config = self.workflow.create_daubert_workflow()
        
        # Find start node variables
        test_inputs = {}
        for node in config["nodes"]:
            if node["id"] == "start":
                for var in node["data"]["variables"]:
                    var_name = var["name"]
                    var_type = var.get("field_type", "text")
                    
                    # Generate appropriate test data
                    if var_type == "select":
                        options = var.get("options", [])
                        if var.get("multiple"):
                            test_inputs[var_name] = options[:2] if len(options) > 1 else options
                        else:
                            test_inputs[var_name] = options[0] if options else ""
                    elif var_type == "file":
                        test_inputs[var_name] = ["test_expert_report.pdf", "test_deposition.pdf"]
                    elif var_name == "expert_name":
                        test_inputs[var_name] = "Dr. Jane Smith"
                    elif var_name == "user_ID":
                        test_inputs[var_name] = var.get("default", "test_user")
                    elif var_name == "database_password":
                        test_inputs[var_name] = var.get("default", "test_password")
                    else:
                        test_inputs[var_name] = f"test_{var_name}"
                
                break
        
        return test_inputs
    
    def visualize_workflow(self) -> str:
        """Generate a simple text visualization of the workflow."""
        config = self.workflow.create_daubert_workflow()
        edges = config.get("edges", [])
        
        # Build adjacency list
        graph = {}
        for edge in edges:
            if edge["source"] not in graph:
                graph[edge["source"]] = []
            graph[edge["source"]].append(edge["target"])
        
        # Generate visualization
        lines = ["Workflow Structure:", "=" * 50]
        
        def traverse(node, indent=0):
            # Find node details
            node_details = None
            for n in config["nodes"]:
                if n["id"] == node:
                    node_details = n
                    break
            
            node_type = node_details.get("type", "unknown") if node_details else "unknown"
            prefix = "  " * indent + "→ " if indent > 0 else ""
            lines.append(f"{prefix}[{node}] ({node_type})")
            
            # Add node description if LLM
            if node_type == "llm" and node_details:
                model = node_details.get("data", {}).get("model", {})
                if isinstance(model, dict):
                    model_name = model.get("name", "unknown")
                else:
                    model_name = model
                lines.append(f"{'  ' * (indent + 1)}Model: {model_name}")
            
            # Traverse children
            if node in graph:
                for child in graph[node]:
                    traverse(child, indent + 1)
        
        traverse("start")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def run_all_tests(self) -> None:
        """Run all validation tests and display results."""
        print("🔍 Running Dify Workflow Validation Tests")
        print("=" * 60)
        
        # Test 1: Basic validation
        print("\n1. Basic Workflow Validation")
        validation = self.workflow.validate_workflow()
        if validation["valid"]:
            print("   ✓ Configuration structure is valid")
            print(f"   - {validation['node_count']} nodes configured")
            print(f"   - {validation['edge_count']} edges configured")
        else:
            print("   ✗ Configuration has errors:")
            for error in validation["errors"]:
                print(f"     - {error}")
        
        # Test 2: Node connections
        print("\n2. Node Connection Test")
        conn_test = self.test_node_connections()
        if conn_test["connected"]:
            print("   ✓ All nodes are properly connected")
        else:
            print("   ✗ Connection issues found:")
            for issue in conn_test["issues"]:
                print(f"     - {issue}")
        
        # Test 3: Variable references
        print("\n3. Variable Reference Test")
        var_test = self.test_variable_references()
        if var_test["valid"]:
            print("   ✓ All variable references are valid")
        else:
            print("   ✗ Variable reference issues:")
            for issue in var_test["issues"]:
                print(f"     - {issue}")
        
        # Test 4: Required fields
        print("\n4. Required Fields Test")
        field_test = self.test_required_fields()
        if field_test["valid"]:
            print("   ✓ All required fields are present")
        else:
            print("   ✗ Missing required fields:")
            for issue in field_test["issues"]:
                print(f"     - {issue}")
        
        # Display workflow visualization
        print("\n5. Workflow Visualization")
        print(self.visualize_workflow())
        
        # Generate test inputs
        print("\n6. Sample Test Inputs")
        test_inputs = self.generate_test_inputs()
        print(json.dumps(test_inputs, indent=2))
        
        # Summary
        print("\n" + "=" * 60)
        all_valid = (validation["valid"] and conn_test["connected"] and 
                    var_test["valid"] and field_test["valid"])
        
        if all_valid:
            print("✅ All tests passed! Workflow is ready for deployment.")
        else:
            print("❌ Some tests failed. Please fix the issues above.")
        
        return all_valid


if __name__ == "__main__":
    tester = WorkflowTester()
    
    # Run all tests
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)