# Rule Engine with AST

A Flask-based rule engine application that uses Abstract Syntax Trees (AST) to create, combine, and evaluate conditional rules. The system provides a simple web interface for managing rules and evaluating them against user data.

## Features

- Create rules using a simple string syntax
- Combine multiple rules into a single AST
- Evaluate rules against JSON data
- Web interface for rule management
- MongoDB backend for rule storage
- Support for complex boolean operations (AND, OR)
- Error handling for invalid rule formats

## Architecture

### Frontend
- HTML/CSS for the user interface
- JavaScript for API interactions
- Simple and intuitive form-based interface

### Backend
- Flask web framework
- MongoDB for rule storage
- Custom AST implementation for rule processing

### Data Structure
The system uses a Node-based AST structure:
```python
class Node:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type      # "operator" or "operand"
        self.value = value    # operator (AND/OR) or condition
        self.left = left      # left child node
        self.right = right    # right child node
```

## Prerequisites

- Python 3.7+
- MongoDB
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rule-engine.git
cd rule-engine
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure MongoDB is running locally on port 27017

## Project Structure

```
rule-engine/
├── static/
│   └── index.html
├── app.py
├── requirements.txt
└── README.md
```

## Running the Application

1. Start MongoDB:
```bash
mongod
```

2. Run the Flask application:
```bash
python app.py
```

3. Access the web interface at `http://localhost:5000`

## API Endpoints

### 1. Create Rule
- **Endpoint:** `/create_rule`
- **Method:** POST
- **Input:**
```json
{
    "rule": "age > 30 AND department = 'Sales'"
}
```

### 2. Combine Rules
- **Endpoint:** `/combine_rules`
- **Method:** POST
- **Input:**
```json
{
    "rule_ids": ["rule_id_1", "rule_id_2"]
}
```

### 3. Evaluate Rule
- **Endpoint:** `/evaluate_rule`
- **Method:** POST
- **Input:**
```json
{
    "ast": {
        "type": "operator",
        "value": "AND",
        "left": {...},
        "right": {...}
    },
    "data": {
        "age": 35,
        "department": "Sales",
        "salary": 60000,
        "experience": 3
    }
}
```

## Rule Format

Rules should follow this format:
- Simple conditions: `attribute operator value`
- Complex rules: `condition1 AND/OR condition2`

Example:
```
((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)
```

## Database Schema

MongoDB collection structure:
```json
{
    "rules": {
        "rule_string": "((age > 30 AND department = 'Sales') OR (age < 25 AND department = 'Marketing')) AND (salary > 50000 OR experience > 5)",
        "ast": {
            "type": "operator",
            "value": "AND",
            "left": {...},
            "right": {...}
        }
    }
}
```

## Error Handling

The application includes error handling for:
- Invalid rule syntax
- Missing or malformed data
- Database connection issues
- Invalid MongoDB ObjectIDs
- AST evaluation errors

## Testing

To test the application:
1. Create individual rules using the web interface
2. Try combining multiple rules
3. Test evaluation with different data sets
4. Verify error handling with invalid inputs

## Limitations and Future Improvements

- Currently supports basic comparison operators (>, <, =)
- Limited to AND/OR logical operators
- No user authentication/authorization
- No rule versioning
- No support for custom functions

Future improvements could include:
- Support for more complex operators
- Rule versioning system
- User authentication
- Custom function support
- Rule validation against attribute catalogs
- Rule modification capabilities
- Performance optimizations for large rule sets

## Dependencies

Core dependencies:
- Flask>=2.2.5
- flask-sqlalchemy>=3.1.1
- pymongo
