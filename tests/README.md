# Tests Directory

This directory contains all the essential tests for the Business API Template WhatsApp system.

## Structure

```
tests/
├── README.md                           # This file
├── test_real_whatsapp_api.py          # Real WhatsApp API integration tests
├── test_whatsapp_message_types.py     # All WhatsApp message types tests
├── test_message_types_flow.json       # JSON flow for message types test
└── unit/
    ├── test_whatsapp_flows_standalone.py    # Standalone flow system tests
    └── test_professional_flow_system.py     # Professional flow system unit tests
```

## Test Files

### 1. `test_real_whatsapp_api.py`
**Purpose**: Tests real WhatsApp API integration with actual credentials
- ✅ Tests environment configuration
- ✅ Tests simple message sending
- ✅ Tests flow conversation initiation
- ✅ Uses real WhatsApp Business API credentials from `.env`

**Usage**:
```bash
# Activate virtual environment
.\env\Scripts\activate

# Run with default phone number
python tests/test_real_whatsapp_api.py

# Run with specific phone number
python tests/test_real_whatsapp_api.py 5492625661694
```

**Requirements**:
- Valid `.env` file with WhatsApp credentials
- Active internet connection
- WhatsApp Business API access

### 2. `test_whatsapp_message_types.py`
**Purpose**: Tests ALL native WhatsApp message types using real API calls
- ✅ Tests text messages (text)
- ✅ Tests interactive buttons (interactive)
- ✅ Tests interactive lists (interactive)
- ✅ Tests image messages (image)
- ✅ Tests document messages (document)
- ✅ Tests audio messages (audio)
- ✅ Tests video messages (video)
- ✅ Tests location messages (location)
- ✅ Tests contact messages (contacts)
- ✅ Tests sticker messages (sticker)
- ⚠️ Tests template messages (template - requires approval)
- ✅ Uses JSON flow definition (`test_message_types_flow.json`)
- ✅ Uses native WhatsApp API message types (no text fallbacks)
- ✅ Direct API calls to WhatsApp Business API

**Usage**:
```bash
# Run with default test number
python tests/test_whatsapp_message_types.py

# Run with specific phone number
python tests/test_whatsapp_message_types.py 1234567890
```

**Requirements**:
- Valid `.env` file with WhatsApp credentials
- Active internet connection
- WhatsApp Business API access
- JSON flow file (`test_message_types_flow.json`)
- `aiohttp` library for direct API calls

**Installation**:
```bash
# Install testing requirements
pip install -r requirements-testing.txt

# Or install specific dependencies
pip install aiohttp pytest pytest-asyncio python-dotenv
```

**Files**:
- `test_whatsapp_message_types.py` - Main test script
- `test_message_types_flow.json` - JSON flow definition

### 3. `test_whatsapp_flows_standalone.py`
**Purpose**: Tests flow system without external dependencies (mock services)
- ✅ Tests flow loading from JSON/YAML files
- ✅ Tests flow execution with mock services
- ✅ Tests different flow types (main, order)
- ✅ No external dependencies required

**Usage**:
```bash
python tests/unit/test_whatsapp_flows_standalone.py
python tests/unit/test_whatsapp_flows_standalone.py "1234567890"
```

**Features**:
- Uses test flows (`test_main.json`, `test_order.json`) without emojis
- Simulates WhatsApp service responses
- Tests conversation state management
- Validates flow step execution

### 4. `test_professional_flow_system.py`
**Purpose**: Unit tests for the professional flow system components
- ✅ Tests FlowBuilder DSL
- ✅ Tests FunctionExecutor
- ✅ Tests DataSourceManager
- ✅ Tests flow validation
- ✅ Tests error handling

**Usage**:
```bash
# Run with pytest
pytest tests/unit/test_professional_flow_system.py -v

# Run specific test class
pytest tests/unit/test_professional_flow_system.py::TestProfessionalFlowBuilder -v
```

## Running Tests

### Prerequisites
1. Install test dependencies:
```bash
pip install -r requirements-testing.txt
```

2. Ensure virtual environment is activated:
```bash
.\env\Scripts\activate
```

### Running All Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_real_whatsapp_api.py -v
```

### Running Individual Tests
```bash
# WhatsApp message types test
python tests/test_whatsapp_message_types.py 1234567890

# Standalone flow test
python tests/unit/test_whatsapp_flows_standalone.py

# Professional flow system tests
pytest tests/unit/test_professional_flow_system.py -v
```

## Test Configuration

### Environment Variables
For real API tests, ensure your `.env` file contains:
```env
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_verify_token
WHATSAPP_API_URL=https://graph.facebook.com/v23.0
```

### Phone Number Format
- **Real API tests**: Use format `5492625661694` (no +, no spaces)
- **Standalone tests**: Can use any format, will be normalized

### Flow Files
- **Production flows**: `app/flows/main.json` (with emojis)
- **Test flows**: `app/flows/test_*.json` (without emojis for Windows console)

## Test Categories

### Integration Tests
- `test_real_whatsapp_api.py` - Tests real WhatsApp API integration

### Unit Tests
- `test_whatsapp_flows_standalone.py` - Tests flow system logic
- `test_professional_flow_system.py` - Tests individual components

### Mock Tests
- All tests use mock services where appropriate to avoid external dependencies

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check that project root is in Python path
   - Verify all dependencies are installed

2. **WhatsApp API Errors**
   - Verify `.env` credentials are correct
   - Check phone number format (no +, no spaces)
   - Ensure WhatsApp Business API is properly configured

3. **Unicode/Emoji Errors**
   - Test flows use ASCII-only messages
   - Production flows include emojis for user experience
   - Windows console may have encoding issues

4. **Flow Loading Errors**
   - Ensure `app/flows/` directory exists
   - Check JSON/YAML syntax in flow files
   - Verify flow file permissions

### Debug Mode
Add debug output to any test by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

When adding new tests:

1. **Follow naming convention**: `test_*.py`
2. **Add proper docstrings**: Describe what the test does
3. **Use appropriate mocks**: Avoid external dependencies
4. **Test edge cases**: Include error scenarios
5. **Update this README**: Document new test files

## Test Data

Test flows are located in `app/flows/test_*.json`:
- `test_main.json` - Simple greeting flow
- `test_order.json` - Complex order processing flow

These flows are designed for testing and don't include emojis to avoid Windows console encoding issues.