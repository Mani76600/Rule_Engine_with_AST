# Rule Engine with AST

## Project Overview

A simple 3-tier rule engine application(Simple UI, API and Backend, Data) to determine user eligibility based on attributes like age, department, income, spend etc.The system can use Abstract Syntax Tree (AST) to represent conditional rules and allow for dynamic creation,combination, and modification of these rules.

### Key Features
- Visual rule creation through web interface
- RESTful API for programmatic rule management
- Dynamic rule combination using AST
- Real-time rule evaluation
- MongoDB persistence
- Complex conditional logic support (AND/OR operations)
- Comprehensive error handling and validation

## System Architecture

### Three-Tier Architecture
1. **Presentation Layer (Frontend)**
   - Web interface built with HTML, CSS, and JavaScript
   - Intuitive forms for rule creation and evaluation
   - Real-time result visualization

2. **Application Layer (Backend)**
   - Flask-based RESTful API
   - AST implementation for rule processing
   - Rule combination logic
   - Data validation and error handling

3. **Data Layer**
   - MongoDB for rule storage
   - Efficient document-based schema
   - Persistent rule management

### Component Diagram
```
[Web Interface] ←→ [Flask API] ←→ [MongoDB]
     ↑               ↑
     |               |
[User Input]    [Rule Processing]
                [AST Management]
```

## Prerequisites

### System Requirements
- Python 3.8+
- MongoDB 4.4+
- Modern web browser
- Postman (for API testing)

### Required Python Packages
```
Flask>=2.2.5
flask-sqlalchemy>=3.1.1
pymongo
```

## Installation Guide

1. **Clone Repository**
```bash
git clone https://github.com/yourusername/rule-engine.git
cd rule-engine
```

2. **Set Up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure MongoDB**
```bash
# Start MongoDB service
mongod --dbpath /your/data/path

# Verify MongoDB connection
mongo
> use rule_engine
```

5. **Start Application**
```bash
python app.py
```

## Detailed Testing Guide

### 1. Web Interface Testing

#### A. Creating a Complex Rule
1. Open `http://localhost:5000` in your browser
2. Navigate to "Create Rule" section
3. Enter the following complex rule:
```
((age > 30 AND department == 'Sales') OR (age < 25 AND department == 'Marketing')) AND (salary > 50000 OR experience > 5)
```

**Expected Result:**
```json
{
  "status": "Rule created",
  "rule_id": "60d5ec49cbe1234567890abc",
  "rule": "((age > 30 AND department == 'Sales') OR (age < 25 AND department == 'Marketing')) AND (salary > 50000 OR experience > 5)",
  "ast": {
    "type": "operator",
    "value": "AND",
    "left": {
      "type": "operator",
      "value": "OR",
      "left": {
        "type": "operator",
        "value": "AND",
        "left": {
          "type": "operand",
          "value": "age > 30"
        },
        "right": {
          "type": "operand",
          "value": "department == 'Sales'"
        }
      },
      "right": {
        "type": "operator",
        "value": "AND",
        "left": {
          "type": "operand",
          "value": "age < 25"
        },
        "right": {
          "type": "operand",
          "value": "department == 'Marketing'"
        }
      }
    },
    "right": {
      "type": "operator",
      "value": "OR",
      "left": {
        "type": "operand",
        "value": "salary > 50000"
      },
      "right": {
        "type": "operand",
        "value": "experience > 5"
      }
    }
  }
}
```

#### B. Combining Multiple Rules
1. In the "Combine Rules" section, enter the following rule IDs:
```
60d5ec49cbe1234567890abc,60d5ec49cbe1234567890def
```

**Expected Result:**
```json
{
  "status": "Rules combined",
  "combined_rule_id": "60d5ec49cbe1234567890ghi",
  "operator": "AND",
  "combined_ast": {
    "type": "operator",
    "value": "AND",
    "left": {
       //First rule AST
    },
    "right": {
       //Second rule AST
    }
  }
}
```

#### C. Evaluating Complex Rules
1. In the "Evaluate Rule" section, enter the following AST:
```json
{
  "type": "operator",
  "value": "AND",
  "left": {
    "type": "operator",
    "value": "OR",
    "left": {
      "type": "operator",
      "value": "AND",
      "left": {
        "type": "operand",
        "value": "age > 30"
      },
      "right": {
        "type": "operand",
        "value": "department == 'Sales'"
      }
    },
    "right": {
      "type": "operator",
      "value": "AND",
      "left": {
        "type": "operand",
        "value": "age < 25"
      },
      "right": {
        "type": "operand",
        "value": "department == 'Marketing'"
      }
    }
  },
  "right": {
    "type": "operator",
    "value": "OR",
    "left": {
      "type": "operand",
      "value": "salary > 50000"
    },
    "right": {
      "type": "operand",
      "value": "experience > 5"
    }
  }
}
```

2. Enter the following test data:
```json
{
  "age": 32,
  "department": "Sales",
  "salary": 60000,
  "experience": 6
}
```

**Expected Result:**
```json
{
  "result": true,
  "evaluation_details": {
    "conditions_met": [
      "age > 30",
      "department == 'Sales'",
      "salary > 50000",
      "experience > 5"
    ],
    "final_result": true
  }
}
```

### 2. API Testing with Postman

#### A. Complex Rule Creation Test
**Request:**
```http
POST http://localhost:5000/create_rule
Content-Type: application/json

{
  "rule": "((age > 30 AND department == 'Sales') OR (age < 25 AND department == 'Marketing')) AND (salary > 50000 OR experience > 5)"
}
```

**Response:**
```json
{
  "status": "Rule created",
  "rule_id": "60d5ec49cbe1234567890abc",
  "ast": {
    // Full AST structure as shown above
  }
}
```

#### B. Rule Combination Test
**Request:**
```http
POST http://localhost:5000/combine_rules
Content-Type: application/json

{
  "rule_ids": [
    "60d5ec49cbe1234567890abc",
    "60d5ec49cbe1234567890def"
  ],
  "operator": "AND"
}
```

**Response:**
```json
{
  "status": "Rules combined",
  "combined_rule_id": "60d5ec49cbe1234567890ghi",
  "combined_ast": {
   //Combined AST structure
  }
}
```

#### C. Rule Evaluation Test
**Request:**
```http
POST http://localhost:5000/evaluate_rule
Content-Type: application/json

{
  "ast": {
    //Full AST structure as shown above
  },
  "data": {
    "age": 32,
    "department": "Sales",
    "salary": 60000,
    "experience": 6
  }
}
```

**Response:**
```json
{
  "result": true,
  "evaluation_path": [
    {
      "condition": "age > 30",
      "result": true
    },
    {
      "condition": "department == 'Sales'",
      "result": true
    },
    {
      "condition": "salary > 50000",
      "result": true
    },
    {
      "condition": "experience > 5",
      "result": true
    }
  ]
}
```
## Error Response Examples

### 1. Invalid Rule Syntax
```json
{
  "status": "Failed",
  "error": "Invalid rule syntax: Missing operator between conditions",
  "details": {
    "position": 15,
    "found": "department",
    "expected": ["AND", "OR"]
  }
}
```

### 2. Invalid Rule Combination
```json
{
  "status": "Failed",
  "error": "Invalid rule combination request",
  "details": {
    "message": "Rule ID not found: 60d5ec49cbe1234567890abc",
    "valid_ids": ["60d5ec49cbe1234567890def"]
  }
}
```

### 3. Invalid Evaluation Data
```json
{
  "status": "Failed",
  "error": "Invalid evaluation data",
  "details": {
    "missing_fields": ["salary", "experience"],
    "required_fields": ["age", "department", "salary", "experience"]
  }
}
```

[Rest of the sections remain the same]

Would you like me to add more specific test cases or expand any particular section further?

## Performance Considerations

1. **AST Optimization**
   - Minimizes tree depth
   - Reduces redundant nodes
   - Optimizes evaluation path

2. **Database Indexing**
   ```javascript
   db.rules.createIndex({"created_at": 1})
   db.rules.createIndex({"rule_string": 1})
   ```

## Security Measures

1. Input Validation
   - Rule string sanitization
   - JSON schema validation
   - MongoDB injection prevention

2. Safe Evaluation
   - Restricted eval environment
   - Sanitized data access
   - Error boundary implementation

## Troubleshooting Guide

### Common Issues and Solutions

1. **MongoDB Connection Failed**
   ```bash
   # Check MongoDB service
   sudo service mongod status
   
   # Verify connection string
   mongo --eval "db.serverStatus()"
   ```

2. **Invalid Rule Syntax**
   - Verify operators (AND, OR)
   - Check condition format
   - Ensure proper parentheses

3. **Rule Evaluation Failed**
   - Validate data format
   - Check AST structure
   - Verify attribute names



##Result




https://github.com/user-attachments/assets/c7b9f0e4-ad5a-4901-851b-2dc1f8a6bbda



## Contributing

1. Fork repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request
