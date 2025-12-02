"""
Swagger/OpenAPI documentation for Flask Mini API.

This module provides API documentation using Flask-RESTX.
"""

from flask_restx import Api, Resource, fields, Namespace
from flask import Blueprint

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Create API instance
api = Api(
    api_bp,
    version='1.0.0',
    title='Flask Mini API',
    description='A simple REST API for managing tasks and users',
    doc='/docs/',
    contact='Flask Mini API Team',
    contact_email='team@flaskminiapi.com'
)

# Create namespaces
tasks_ns = Namespace('tasks', description='Task operations')
users_ns = Namespace('users', description='User operations')
auth_ns = Namespace('auth', description='Authentication operations')

# Add namespaces to API
api.add_namespace(tasks_ns)
api.add_namespace(users_ns)
api.add_namespace(auth_ns)

# Define models
task_model = api.model('Task', {
    'id': fields.Integer(readonly=True, description='Task ID'),
    'title': fields.String(required=True, description='Task title', max_length=200),
    'description': fields.String(description='Task description', max_length=1000),
    'completed': fields.Boolean(description='Task completion status'),
    'priority': fields.String(description='Task priority', enum=['low', 'medium', 'high']),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readonly=True, description='Last update timestamp')
})

task_input_model = api.model('TaskInput', {
    'title': fields.String(required=True, description='Task title', max_length=200),
    'description': fields.String(description='Task description', max_length=1000),
    'completed': fields.Boolean(description='Task completion status'),
    'priority': fields.String(description='Task priority', enum=['low', 'medium', 'high'])
})

user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='User ID'),
    'username': fields.String(required=True, description='Username', max_length=50),
    'email': fields.String(required=True, description='Email address', max_length=100),
    'api_key': fields.String(readonly=True, description='API key'),
    'created_at': fields.DateTime(readonly=True, description='Creation timestamp'),
    'updated_at': fields.DateTime(readonly=True, description='Last update timestamp')
})

user_input_model = api.model('UserInput', {
    'username': fields.String(required=True, description='Username', max_length=50),
    'email': fields.String(required=True, description='Email address', max_length=100)
})

register_model = api.model('Register', {
    'username': fields.String(required=True, description='Username', max_length=50),
    'email': fields.String(required=True, description='Email address', max_length=100)
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username', max_length=50)
})

error_model = api.model('Error', {
    'error': fields.String(description='Error type'),
    'message': fields.String(description='Error message'),
    'status_code': fields.Integer(description='HTTP status code')
})

success_model = api.model('Success', {
    'message': fields.String(description='Success message'),
    'data': fields.Raw(description='Response data')
})

# Task endpoints documentation
@tasks_ns.route('/')
class TaskList(Resource):
    @api.doc('list_tasks')
    @api.marshal_list_with(task_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get all tasks"""
        pass

    @api.doc('create_task')
    @api.expect(task_input_model)
    @api.marshal_with(success_model, code=201)
    @api.response(400, 'Bad Request', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def post(self):
        """Create a new task"""
        pass

@tasks_ns.route('/<int:task_id>')
@api.param('task_id', 'Task ID')
class Task(Resource):
    @api.doc('get_task')
    @api.marshal_with(task_model)
    @api.response(404, 'Task not found', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self, task_id):
        """Get a specific task by ID"""
        pass

    @api.doc('update_task')
    @api.expect(task_input_model)
    @api.marshal_with(success_model)
    @api.response(400, 'Bad Request', error_model)
    @api.response(404, 'Task not found', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def put(self, task_id):
        """Update an existing task"""
        pass

    @api.doc('delete_task')
    @api.marshal_with(success_model)
    @api.response(404, 'Task not found', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def delete(self, task_id):
        """Delete a task"""
        pass

# User endpoints documentation
@users_ns.route('/')
class UserList(Resource):
    @api.doc('list_users')
    @api.marshal_list_with(user_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self):
        """Get all users"""
        pass

    @api.doc('create_user')
    @api.expect(user_input_model)
    @api.marshal_with(success_model, code=201)
    @api.response(400, 'Bad Request', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def post(self):
        """Create a new user"""
        pass

@users_ns.route('/<int:user_id>')
@api.param('user_id', 'User ID')
class User(Resource):
    @api.doc('get_user')
    @api.marshal_with(user_model)
    @api.response(404, 'User not found', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def get(self, user_id):
        """Get a specific user by ID"""
        pass

    @api.doc('update_user')
    @api.expect(user_input_model)
    @api.marshal_with(success_model)
    @api.response(400, 'Bad Request', error_model)
    @api.response(404, 'User not found', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def put(self, user_id):
        """Update an existing user"""
        pass

    @api.doc('delete_user')
    @api.marshal_with(success_model)
    @api.response(404, 'User not found', error_model)
    @api.response(401, 'Unauthorized', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def delete(self, user_id):
        """Delete a user"""
        pass

# Authentication endpoints documentation
@auth_ns.route('/register')
class Register(Resource):
    @api.doc('register_user')
    @api.expect(register_model)
    @api.marshal_with(success_model, code=201)
    @api.response(400, 'Bad Request', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def post(self):
        """Register a new user and get API key"""
        pass

@auth_ns.route('/login')
class Login(Resource):
    @api.doc('login_user')
    @api.expect(login_model)
    @api.marshal_with(success_model)
    @api.response(400, 'Bad Request', error_model)
    @api.response(404, 'User not found', error_model)
    @api.response(500, 'Internal Server Error', error_model)
    def post(self):
        """Login with username and get API key"""
        pass

# Health check endpoint
@api.route('/health')
class Health(Resource):
    @api.doc('health_check')
    def get(self):
        """Health check endpoint"""
        pass

# Blueprint will be registered in main.py
