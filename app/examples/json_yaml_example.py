"""
Practical Example: Using JSON and YAML Flows
Example showing how to use both JSON and YAML flow configurations
"""
from app.services.unified_flow_loader import create_unified_flow_loader
from app.services.conversation_flow_builder import create_flow_executor


def example_json_yaml_usage():
    """Example of using both JSON and YAML flows"""
    
    print("🚀 JSON and YAML Flow System Example")
    print("=" * 50)
    
    # Create unified loader
    loader = create_unified_flow_loader("app/flows")
    
    # Load all flows (both JSON and YAML)
    print("\n📂 Loading flows...")
    flows = loader.load_all_flows()
    
    print(f"\n✅ Loaded {len(flows)} flows:")
    for flow_id, flow in flows.items():
        print(f"  - {flow_id}: {flow.name} ({len(flow.steps)} steps)")
    
    # Validate flows
    print("\n🔍 Validating flows...")
    for flow_id in flows.keys():
        validation = loader.validate_flow_file(flow_id)
        status = "✅" if validation["valid"] else "❌"
        print(f"  {status} {flow_id}: {validation['steps_count']} steps")
        
        if not validation["valid"]:
            for issue in validation["issues"]:
                print(f"    ⚠️ {issue}")
    
    # Get detailed info
    print("\n📋 Flow details:")
    for flow_id in flows.keys():
        info = loader.get_flow_info(flow_id)
        print(f"\n  📄 {flow_id}:")
        print(f"    Name: {info['name']}")
        print(f"    Steps: {info['steps_count']}")
        print(f"    Variables: {list(info['variables'].keys())}")
        print(f"    Error handlers: {list(info['error_handlers'].keys())}")
        
        # Show first few steps
        print("    First steps:")
        for i, step in enumerate(info['steps'][:3]):
            print(f"      {i+1}. {step['id']} ({step['type']}) -> {step['next_step']}")
        if len(info['steps']) > 3:
            print(f"      ... and {len(info['steps']) - 3} more steps")
    
    # Example of conversion
    print("\n🔄 Conversion example:")
    try:
        # Convert YAML to JSON (if welcome.yaml exists)
        loader.convert_yaml_to_json("welcome", "welcome_converted")
        print("✅ Converted welcome.yaml to welcome_converted.json")
    except FileNotFoundError:
        print("ℹ️ welcome.yaml not found, skipping conversion")
    
    try:
        # Convert JSON to YAML (if welcome.json exists)
        loader.convert_json_to_yaml("welcome", "welcome_converted")
        print("✅ Converted welcome.json to welcome_converted.yaml")
    except FileNotFoundError:
        print("ℹ️ welcome.json not found, skipping conversion")
    
    print("\n🎉 Example completed!")


def compare_json_vs_yaml():
    """Compare JSON vs YAML for the same flow"""
    
    print("\n📊 JSON vs YAML Comparison")
    print("=" * 30)
    
    # Example JSON flow
    json_example = {
        "id": "comparison",
        "name": "Comparison Flow",
        "start_step": "greeting",
        "steps": [
            {
                "id": "greeting",
                "type": "message",
                "name": "Greeting",
                "message": "Hello! Welcome to our service.",
                "next_step": "menu"
            },
            {
                "id": "menu",
                "type": "choice",
                "name": "Menu",
                "message": "Choose an option:",
                "choice_type": "buttons",
                "options": [
                    {"id": "option1", "title": "Option 1"},
                    {"id": "option2", "title": "Option 2"}
                ],
                "next_step": "end"
            },
            {
                "id": "end",
                "type": "end",
                "name": "End",
                "message": "Thank you!"
            }
        ]
    }
    
    # Equivalent YAML flow
    yaml_example = """
id: comparison
name: Comparison Flow
start_step: greeting
steps:
  - id: greeting
    type: message
    name: Greeting
    message: "Hello! Welcome to our service."
    next_step: menu
  - id: menu
    type: choice
    name: Menu
    message: "Choose an option:"
    choice_type: buttons
    options:
      - id: option1
        title: "Option 1"
      - id: option2
        title: "Option 2"
    next_step: end
  - id: end
    type: end
    name: End
    message: "Thank you!"
"""
    
    print("JSON ({} characters):".format(len(str(json_example))))
    print("```json")
    print(str(json_example)[:200] + "...")
    print("```")
    
    print("\nYAML ({} characters):".format(len(yaml_example)))
    print("```yaml")
    print(yaml_example[:200] + "...")
    print("```")
    
    print("\n📈 Comparison:")
    print(f"  JSON: {len(str(json_example))} characters")
    print(f"  YAML: {len(yaml_example)} characters")
    print(f"  YAML is {len(yaml_example) / len(str(json_example)) * 100:.1f}% of JSON size")


if __name__ == "__main__":
    example_json_yaml_usage()
    compare_json_vs_yaml()
