from flask import Flask, url_for, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/hello')
def hello():
    return 'Hello from Flask!'

@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {username}'

@app.route('/login', methods=['GET', 'POST'])
def login():
    return 'Login Page'

@app.get('/logout')
def logout():
    return 'Logout Page'

@app.post('/register')
def register():
    return 'Register Page'


with app.test_request_context():
    print(url_for('hello_world'))
    print(url_for('hello'))
    print(url_for('show_user_profile', username='JohnDoe'))

with app.test_request_context('/hello?name=John'):
    print(request.args.get('name'))  # Output: John
    assert request.args.get('name') == 'John'

if __name__ == '__main__':
    app.run(debug=True)
