import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from datetime import datetime
from models import db, User, Task
from sqlalchemy import desc, asc

app = Flask(__name__)

# Production configurations
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_12345')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create database tables within context
with app.app_context():
    db.create_all()

# --- Authentication Decorator ---
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Context Processor for App Injection ---
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# --- Application Routes ---

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))
            
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('register'))
            
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already registered.', 'danger')
            return redirect(url_for('register'))
            
        new_user = User(name=name, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('login'))
            
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    
    # Filters & Search Inputs
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    priority_filter = request.args.get('priority', '').strip()
    sort_by = request.args.get('sort', 'newest')

    # Base query for tasks belonging to user
    query = Task.query.filter_by(user_id=user_id)
    
    # Apply Filtering Mechanics
    if search_query:
        query = query.filter(Task.title.ilike(f"%{search_query}%"))
    if status_filter:
        query = query.filter(Task.status == status_filter)
    if priority_filter:
        query = query.filter(Task.priority == priority_filter)
        
    # Sorting Mechanics
    if sort_by == 'oldest':
        query = query.order_by(asc(Task.created_at))
    elif sort_by == 'due_date':
        query = query.order_by(asc(Task.due_date))
    else: # Default: Newest First
        query = query.order_by(desc(Task.created_at))
        
    tasks = query.all()

    # Metric Statistics Calculations
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed_tasks = Task.query.filter_by(user_id=user_id, status='Completed').count()
    pending_tasks = Task.query.filter_by(user_id=user_id, status='Pending').count()
    progress_tasks = Task.query.filter_by(user_id=user_id, status='In Progress').count()
    
    completion_rate = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    metrics = {
        'total': total_tasks,
        'completed': completed_tasks,
        'pending': pending_tasks,
        'progress': progress_tasks,
        'rate': completion_rate
    }

    return render_template('dashboard.html', tasks=tasks, metrics=metrics, 
                           search=search_query, status_filter=status_filter, 
                           priority_filter=priority_filter, sort=sort_by)


@app.route('/task/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form.get('title').strip()
        description = request.form.get('description').strip()
        priority = request.form.get('priority')
        status = request.form.get('status')
        due_date_str = request.form.get('due_date')
        
        if not title or not due_date_str:
            flash('Task title and due date are mandatory.', 'danger')
            return redirect(url_for('add_task'))
            
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid format for due date.', 'danger')
            return redirect(url_for('add_task'))

        new_task = Task(
            title=title,
            description=description,
            priority=priority,
            status=status,
            due_date=due_date,
            user_id=session['user_id']
        )
        db.session.add(new_task)
        db.session.commit()
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_task.html')


@app.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    
    if request.method == 'POST':
        task.title = request.form.get('title').strip()
        task.description = request.form.get('description').strip()
        task.priority = request.form.get('priority')
        task.status = request.form.get('status')
        due_date_str = request.form.get('due_date')
        
        if not task.title or not due_date_str:
            flash('Task title and due date are required fields.', 'danger')
            return redirect(url_for('edit_task', task_id=task.id))
            
        try:
            task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid due date parsing layout.', 'danger')
            return redirect(url_for('edit_task', task_id=task.id))
            
        db.session.commit()
        flash('Task settings synced successfully.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_task.html', task=task)


@app.route('/task/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash('Task permanent drop execution completed.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    total_tasks = Task.query.filter_by(user_id=user.id).count()
    return render_template('profile.html', user=user, total_tasks=total_tasks)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)