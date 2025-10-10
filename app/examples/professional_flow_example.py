"""
Professional Flow System Example
Complete example showing how to use the professional flow system
"""
from app.services.professional_unified_flow_loader import create_professional_unified_flow_loader
from app.services.professional_flow_system import create_function_executor, create_data_source_manager


def example_professional_flow_usage():
    """Example of using the professional flow system"""
    
    print("🚀 Professional Flow System Example")
    print("=" * 50)
    
    # Create loader
    loader = create_professional_unified_flow_loader("app/flows")
    
    # Load all flows (Python, JSON, YAML)
    print("\n📂 Loading flows...")
    flows = loader.load_all_flows()
    
    print(f"\n✅ Loaded {len(flows)} flows:")
    for flow_id, flow in flows.items():
        print(f"  - {flow_id}: {flow.name}")
        print(f"    Steps: {len(flow.steps)}")
        print(f"    Data Sources: {len(flow.data_sources)}")
        print(f"    Functions: {len(flow.functions)}")
        print(f"    Variables: {len(flow.variables)}")
    
    # Validate flows
    print("\n🔍 Validating flows...")
    for flow_id in flows.keys():
        validation = loader.validate_flow_file(flow_id)
        status = "✅" if validation["valid"] else "❌"
        print(f"  {status} {flow_id}")
        
        if not validation["valid"]:
            for issue in validation["issues"]:
                print(f"    ⚠️ {issue}")
    
    # Show flow details
    print("\n📋 Flow Details:")
    for flow_id, flow in flows.items():
        print(f"\n  📄 {flow_id}:")
        print(f"    Name: {flow.name}")
        print(f"    Description: {flow.description}")
        print(f"    Start Step: {flow.start_step}")
        print(f"    Variables: {list(flow.variables.keys())}")
        print(f"    Data Sources: {list(flow.data_sources.keys())}")
        print(f"    Functions: {list(flow.functions.keys())}")
        print(f"    Error Handlers: {list(flow.error_handling.keys())}")
        
        # Show first few steps
        print("    Steps:")
        for i, (step_id, step) in enumerate(list(flow.steps.items())[:5]):
            print(f"      {i+1}. {step_id} ({step.type.value}) -> {step.next_step}")
            if step.functions:
                print(f"         Functions: {[f.name for f in step.functions]}")
            if step.data_sources:
                print(f"         Data Sources: {[ds.name for ds in step.data_sources]}")
        
        if len(flow.steps) > 5:
            print(f"      ... and {len(flow.steps) - 5} more steps")
    
    # Example of format conversion
    print("\n🔄 Format Conversion Example:")
    try:
        # Convert JSON to YAML
        loader.convert_format("professional_order", "yaml", "professional_order_converted")
        print("✅ Converted professional_order.json to professional_order_converted.yaml")
    except Exception as e:
        print(f"ℹ️ Conversion example skipped: {e}")
    
    # Example of function execution
    print("\n⚙️ Function Execution Example:")
    function_executor = create_function_executor()
    
    # Test email validation
    email_result = function_executor.execute_function(
        type('FunctionConfig', (), {
            'name': 'validate_email',
            'module': 'app.utils.flow_functions',
            'function': 'validate_email',
            'parameters': {'email': 'test@example.com'},
            'timeout': 5,
            'retry_count': 2,
            'error_handler': None,
            'cache_result': False
        })(),
        {'user_email': 'test@example.com'}
    )
    
    print(f"  Email validation result: {email_result}")
    
    # Test order calculation
    calc_result = function_executor.execute_function(
        type('FunctionConfig', (), {
            'name': 'calculate_total',
            'module': 'app.utils.flow_functions',
            'function': 'calculate_order_total',
            'parameters': {
                'items': [{'price': 15.99, 'quantity': 2}],
                'delivery_fee': 5.0,
                'tax_rate': 0.10
            },
            'timeout': 10,
            'retry_count': 3,
            'error_handler': None,
            'cache_result': True
        })(),
        {'order_items': [{'price': 15.99, 'quantity': 2}], 'delivery_fee': 5.0, 'tax_rate': 0.10}
    )
    
    print(f"  Order calculation result: {calc_result}")
    
    # Example of data source usage
    print("\n📊 Data Source Example:")
    data_manager = create_data_source_manager()
    
    # Test file data source
    file_source = type('DataSource', (), {
        'name': 'test_file',
        'type': type('DataSourceType', (), {'FILE': 'file'})().FILE,
        'config': {'path': 'app/flows/welcome.json'},
        'cache_ttl': 300
    })()
    
    file_result = data_manager.get_data(file_source)
    print(f"  File data source result: {file_result.get('success', False)}")
    
    print("\n🎉 Example completed!")


def compare_formats():
    """Compare Python, JSON, and YAML formats"""
    
    print("\n📊 Format Comparison")
    print("=" * 30)
    
    # Load the same flow in different formats
    loader = create_professional_unified_flow_loader("app/flows")
    
    formats = {
        "Python": "professional_order_python",
        "JSON": "professional_order",
        "YAML": "professional_order_yaml"
    }
    
    for format_name, flow_id in formats.items():
        try:
            flow = loader.load_flow_from_file(flow_id)
            print(f"\n{format_name}:")
            print(f"  ID: {flow.id}")
            print(f"  Name: {flow.name}")
            print(f"  Steps: {len(flow.steps)}")
            print(f"  Data Sources: {len(flow.data_sources)}")
            print(f"  Functions: {len(flow.functions)}")
            print(f"  Variables: {len(flow.variables)}")
            print(f"  Error Handlers: {len(flow.error_handling)}")
        except Exception as e:
            print(f"\n{format_name}: Error loading - {e}")
    
    print("\n📈 Format Characteristics:")
    print("  Python:")
    print("    ✅ Full IDE support")
    print("    ✅ Type checking")
    print("    ✅ Debugging")
    print("    ✅ Version control friendly")
    print("    ❌ More verbose")
    
    print("\n  JSON:")
    print("    ✅ Universal support")
    print("    ✅ Schema validation")
    print("    ✅ API integration")
    print("    ✅ Fast parsing")
    print("    ❌ No comments")
    print("    ❌ Verbose syntax")
    
    print("\n  YAML:")
    print("    ✅ Human readable")
    print("    ✅ Comments support")
    print("    ✅ Less verbose")
    print("    ✅ Multiline text")
    print("    ❌ Indentation sensitive")
    print("    ❌ Slower parsing")


def show_advanced_features():
    """Show advanced features of the professional flow system"""
    
    print("\n🔧 Advanced Features")
    print("=" * 25)
    
    print("\n1. 📊 Data Sources:")
    print("   • Database queries with caching")
    print("   • API calls with retry logic")
    print("   • File loading (JSON/YAML)")
    print("   • Memory storage")
    print("   • Static data")
    
    print("\n2. ⚙️ Function Execution:")
    print("   • Custom Python functions")
    print("   • Parameter substitution")
    print("   • Error handling")
    print("   • Result caching")
    print("   • Timeout management")
    
    print("\n3. 🛡️ Error Handling:")
    print("   • Function-level error handlers")
    print("   • Step-level error handlers")
    print("   • Flow-level error handlers")
    print("   • Automatic retry logic")
    print("   • Graceful degradation")
    
    print("\n4. 🔄 Format Support:")
    print("   • Python builder pattern")
    print("   • JSON configuration")
    print("   • YAML configuration")
    print("   • Automatic conversion")
    print("   • Validation and linting")
    
    print("\n5. 📈 Professional Features:")
    print("   • Comprehensive logging")
    print("   • Performance monitoring")
    print("   • Flow validation")
    print("   • Metadata support")
    print("   • Version control")
    
    print("\n6. 🎯 Use Cases:")
    print("   • E-commerce order flows")
    print("   • Customer support")
    print("   • Appointment booking")
    print("   • Lead qualification")
    print("   • Survey collection")


if __name__ == "__main__":
    example_professional_flow_usage()
    compare_formats()
    show_advanced_features()
