from flask import Flask, request, jsonify, send_from_directory
from pymongo import MongoClient
from ast import literal_eval
from bson import ObjectId
import os

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['rule_engine']
rules_collection = db['rules']

# Serve the index.html file directly
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

# Node Class for AST
class Node:
    def __init__(self, type, value=None, left=None, right=None):
        self.type = type
        self.value = value
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Node(type={self.type}, value={self.value}, left={self.left}, right={self.right})"

# Helper to convert rule string to AST (add check for None)
def create_rule_ast(rule_string):
    if rule_string is None or rule_string.strip() == "":
        return None, "Rule string cannot be empty"
    
    try:
        return build_ast(rule_string), None
    except Exception as e:
        return None, str(e)

# Helper to parse and create the AST from string-based rules
def build_ast(rule_string):
    rule_string = rule_string.replace("=", "==")  # Ensure equality is checked properly
    tokens = rule_string.split()

    if len(tokens) == 3:  # Simple condition (e.g., "age > 30")
        return Node(type="operand", value=rule_string)
    elif len(tokens) >= 5 and tokens[3] in ["AND", "OR"]:  # Complex rule (e.g., "age > 30 AND salary > 50000")
        left_expr = " ".join(tokens[:3])
        right_expr = " ".join(tokens[4:])
        return Node(type="operator", value=tokens[3], left=build_ast(left_expr), right=build_ast(right_expr))
    else:
        raise ValueError("Invalid rule format")

# Flask API for create_rule
@app.route('/create_rule', methods=['POST'])
def create_rule():
    rule_string = request.json.get('rule')
    ast, error = create_rule_ast(rule_string)
    if ast:
        rules_collection.insert_one({'rule_string': rule_string, 'ast': str(ast)})
        return jsonify({"status": "Rule created", "rule": rule_string, "ast": str(ast)}), 201
    else:
        return jsonify({"status": "Failed", "error": error}), 400

# Helper to count the frequency of operators in rule strings
def operator_frequency(rules):
    and_count = sum("AND" in rule for rule in rules)
    or_count = sum("OR" in rule for rule in rules)
    return "AND" if and_count >= or_count else "OR"

# Helper to combine two ASTs with an operator
def combine_asts(ast1, ast2, operator="AND"):
    return Node(type="operator", value=operator, left=ast1, right=ast2)

# combine_rules: This function combines multiple rules into a single AST
def combine_rules(rules):
    if not rules:
        raise ValueError("No rules provided to combine")

    asts = [build_ast(rule) for rule in rules]  # Build ASTs for each rule
    operator = operator_frequency(rules)  # Determine whether to use AND or OR based on frequency

    # Combine ASTs iteratively
    combined_ast = asts[0]
    for ast in asts[1:]:
        combined_ast = combine_asts(combined_ast, ast, operator)

    return combined_ast

@app.route('/combine_rules', methods=['POST'])
def combine_rules():
    rule_ids = request.json.get('rule_ids')
    operator = request.json.get('operator', 'AND')  # Default to AND

    # Validate input
    if not rule_ids or not isinstance(rule_ids, list) or len(rule_ids) < 2:
        return jsonify({"error": "Invalid rule list", "status": "Failed"}), 400

    try:
        # Ensure valid ObjectIds
        object_ids = []
        for id in rule_ids:
            try:
                object_ids.append(ObjectId(id.strip()))
            except Exception:
                return jsonify({"error": f"Invalid ObjectId: {id}", "status": "Failed"}), 400

        # Fetch the corresponding rules from MongoDB
        rules = list(rules_collection.find({'_id': {'$in': object_ids}}))

        # Check if enough rules were found
        if len(rules) < 2:
            return jsonify({"error": "Not enough rules found", "status": "Failed"}), 400

        # Build the ASTs from the stored data
        asts = [build_ast(rule['rule_string']) for rule in rules]

        # Combine the ASTs using the specified operator
        combined_ast = asts[0]
        for ast in asts[1:]:
            combined_ast = combine_asts(combined_ast, ast, operator=operator)

        # Store the combined AST back in MongoDB with a new ObjectId
        combined_rule_id = rules_collection.insert_one({
            'rule_string': 'Combined Rule',
            'ast': str(combined_ast)
        }).inserted_id

        # Return the combined AST and the ID for future reference
        return jsonify({
            "status": "Rules combined",
            "combined_ast": str(combined_ast),  # Provide string representation of combined AST
            "combined_rule_id": str(combined_rule_id)
        }), 200

    except Exception as e:
        return jsonify({"status": "Failed", "error": str(e)}), 400



# Helper to evaluate AST (now handling dictionary representation from MongoDB)
def evaluate_ast(node, data):
    if node['type'] == "operand":
        # Create a safe expression to evaluate
        condition = node['value']
        # Use eval safely by restricting globals and passing data as local variables
        return eval(condition, {}, data)
    
    # Recursively evaluate left and right sub-trees
    left_result = evaluate_ast(node['left'], data)
    right_result = evaluate_ast(node['right'], data)
    
    if node['value'] == "AND":
        return left_result and right_result
    elif node['value'] == "OR":
        return left_result or right_result
    else:
        raise ValueError(f"Unknown operator: {node['value']}")

# Reconstruct the Node tree from the JSON structure
def reconstruct_ast(ast_json):
    if not ast_json:
        return None
    return Node(
        type=ast_json['type'],
        value=ast_json.get('value'),
        left=reconstruct_ast(ast_json.get('left')),
        right=reconstruct_ast(ast_json.get('right'))
    )

# Correct evaluate_rule API to properly parse the AST and evaluate it
@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule():
    ast_json = request.json.get('ast')  # AST structure provided in JSON format
    data = request.json.get('data')  # e.g., {"age": 35, "department": "Sales", "salary": 60000, "experience": 3}

    if not ast_json or not data:
        return jsonify({"error": "AST and data must be provided"}), 400

    try:
        # Reconstruct the AST from the JSON
        root_node = reconstruct_ast(ast_json)

        # Evaluate the AST against the provided data
        result = evaluate_ast(root_node, data)
        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 400

# Correct evaluate_ast function to handle Node objects properly
def evaluate_ast(node, data):
    if node is None:
        return False

    # Evaluate operands (assumes 'value' contains the expression in string form for operands)
    if node.type == 'operand':
        # Use eval to evaluate the condition (assume simple expressions like 'age > 30')
        return eval(node.value, {}, data)

    # If the node is an operator, handle 'AND', 'OR' recursively
    elif node.type == 'operator':
        if node.value == 'AND':
            return evaluate_ast(node.left, data) and evaluate_ast(node.right, data)
        elif node.value == 'OR':
            return evaluate_ast(node.left, data) or evaluate_ast(node.right, data)

    # In case of unexpected node type
    return False

@app.route('/list_rules', methods=['GET'])
def list_rules():
    rules = list(rules_collection.find({}))
    result = [{'_id': str(rule['_id']), 'rule_string': rule['rule_string']} for rule in rules]
    return jsonify(result), 200


# Serve static files like CSS, JS
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(debug=True)
