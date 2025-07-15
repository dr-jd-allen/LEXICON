#!/usr/bin/env python3
"""
Script to help import the workflow configuration into Dify
This generates the configuration in a format ready for Dify Studio
"""

import json
from dify_workflow_clean import DifyWorkflow

def generate_dify_import_format():
    """Generate workflow configuration in Dify's import format."""
    workflow = DifyWorkflow()
    config = workflow.create_daubert_workflow()
    
    # Convert to Dify's expected format
    dify_format = {
        "version": "0.1.0",
        "kind": "app",
        "app": {
            "name": config["name"],
            "description": config["description"],
            "icon": "🏛️",
            "icon_background": "#E0F2FE",
            "mode": "workflow",
            "config": {
                "version": "0.1.0"
            }
        },
        "workflow": {
            "nodes": [],
            "edges": config["edges"],
            "viewport": {
                "x": 0,
                "y": 0,
                "zoom": 1
            }
        }
    }
    
    # Transform nodes to Dify format
    x_position = 100
    y_position = 100
    
    for node in config["nodes"]:
        dify_node = {
            "id": node["id"],
            "type": node["type"],
            "position": {
                "x": x_position,
                "y": y_position
            },
            "data": node["data"]
        }
        
        # Add visual positioning
        if node["type"] == "start":
            dify_node["position"] = {"x": 100, "y": 200}
        elif node["id"] == "research_agent":
            dify_node["position"] = {"x": 400, "y": 200}
        elif node["id"] == "find_contradictions":
            dify_node["position"] = {"x": 700, "y": 200}
        elif node["id"] == "find_precedent":
            dify_node["position"] = {"x": 1000, "y": 200}
        elif node["id"] == "draft_argument":
            dify_node["position"] = {"x": 1300, "y": 200}
        elif node["type"] == "end":
            dify_node["position"] = {"x": 1600, "y": 200}
        
        dify_format["workflow"]["nodes"].append(dify_node)
    
    return dify_format

def generate_node_by_node_guide():
    """Generate a step-by-step guide for manual creation."""
    workflow = DifyWorkflow()
    config = workflow.create_daubert_workflow()
    
    guide = ["# Step-by-Step Dify Studio Configuration Guide\n"]
    
    for i, node in enumerate(config["nodes"], 1):
        guide.append(f"\n## Step {i}: {node['id'].replace('_', ' ').title()} Node\n")
        
        if node["type"] == "start":
            guide.append("1. The Start node should already exist\n")
            guide.append("2. Click on it and add these variables:\n")
            for var in node["data"]["variables"]:
                guide.append(f"   - **{var['name']}**:")
                guide.append(f"     - Type: {var['field_type']}")
                guide.append(f"     - Required: {var.get('required', False)}")
                if 'default' in var:
                    guide.append(f"     - Default: {var['default']}")
                if 'options' in var:
                    guide.append(f"     - Options: {', '.join(var['options'])}")
                guide.append("")
        
        elif node["type"] == "llm":
            guide.append(f"1. Drag an 'LLM' node from the left panel\n")
            guide.append(f"2. Connect it to the previous node\n")
            guide.append(f"3. Configure:\n")
            
            data = node["data"]
            if "model" in data and isinstance(data["model"], dict):
                guide.append(f"   - **Model**: {data['model']['name']}")
                params = data['model'].get('completion_params', {})
                guide.append(f"   - **Temperature**: {params.get('temperature', 0.7)}")
                guide.append(f"   - **Max Tokens**: {params.get('max_tokens', 4000)}")
            
            guide.append(f"\n4. **System Prompt** (copy exactly):\n")
            guide.append("```")
            guide.append(data.get("prompt", ""))
            guide.append("```\n")
        
        elif node["type"] == "end":
            guide.append("1. The End node should already exist\n")
            guide.append("2. Connect the last node to it\n")
            guide.append("3. Configure outputs:\n")
            for output in node["data"]["outputs"]:
                guide.append(f"   - {output['name']}: {output['value']}")
    
    return "\n".join(guide)

if __name__ == "__main__":
    # Generate import format
    import_config = generate_dify_import_format()
    
    # Save as JSON for import
    with open("dify_workflow_import.json", "w") as f:
        json.dump(import_config, f, indent=2)
    
    print("✅ Generated dify_workflow_import.json")
    
    # Generate manual guide
    guide = generate_node_by_node_guide()
    
    # Save guide
    with open("DIFY_MANUAL_SETUP_GUIDE.md", "w") as f:
        f.write(guide)
    
    print("✅ Generated DIFY_MANUAL_SETUP_GUIDE.md")
    
    print("\n📋 Quick Import Instructions:")
    print("1. In Dify Studio, look for 'Import' or 'Import Workflow' button")
    print("2. Upload or paste the contents of dify_workflow_import.json")
    print("3. If import isn't available, follow DIFY_MANUAL_SETUP_GUIDE.md")
    
    print("\n🔗 Node Connection Order:")
    print("START → research_agent → find_contradictions → find_precedent → draft_argument → END")