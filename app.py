from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import uuid
import logging
from datetime import datetime
from contextlib import contextmanager
import os

# Import configuration
from config import config

# Get environment
env = os.environ.get('FLASK_ENV', 'development')
app_config = config[env]

# Configure logging
logging.basicConfig(level=getattr(logging, app_config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(app_config)

# Configure CORS with origins from config
CORS(app, origins="*", allow_headers="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(app_config.DATABASE_URL)
    conn.row_factory = sqlite3.Row  # Enable row factory for better data access
    try:
        yield conn
    finally:
        conn.close()

def migrate_database():
    """Migrate existing database to new schema"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Check if user_names table exists and get its current schema
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_names'")
            if not c.fetchone():
                logger.info("user_names table doesn't exist, will be created by init_db()")
                return
            
            # Get current schema
            c.execute('PRAGMA table_info(user_names)')
            current_columns = [row[1] for row in c.fetchall()]
            logger.info(f"Current user_names columns: {current_columns}")
            
            # Check if we need to migrate
            required_columns = ['id', 'user_id', 'female_name', 'male_name', 'created_at', 'usage_count']
            missing_columns = [col for col in required_columns if col not in current_columns]
            
            if not missing_columns:
                logger.info("Database schema is up to date")
                return
            
            logger.info(f"Missing columns: {missing_columns}")
            
            # Create backup of existing data
            c.execute('SELECT * FROM user_names')
            existing_data = c.fetchall()
            logger.info(f"Backing up {len(existing_data)} existing records")
            
            # Drop and recreate table with correct schema
            c.execute('DROP TABLE user_names')
            c.execute('''
                CREATE TABLE user_names (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    female_name TEXT NOT NULL,
                    male_name TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Restore data with default values for new columns
            for row in existing_data:
                # Assuming old schema had: female_name, male_name, timestamp
                female_name = row[0] if len(row) > 0 else ''
                male_name = row[1] if len(row) > 1 else ''
                timestamp = row[2] if len(row) > 2 else datetime.now()
                
                # Use a default user_id for existing records
                default_user_id = str(uuid.uuid4())
                
                c.execute('''
                    INSERT INTO user_names (user_id, female_name, male_name, created_at, usage_count)
                    VALUES (?, ?, ?, ?, ?)
                ''', (default_user_id, female_name, male_name, timestamp, 1))
            
            conn.commit()
            logger.info("Database migration completed successfully")
            
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        raise

def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        
        # Users table for library card system
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                library_id TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_access DATETIME DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        ''')
        
        # User sessions table to track each reading session
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                session_start DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_end DATETIME,
                pages_read INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # User names table to track names used by each user
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_names (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                female_name TEXT NOT NULL,
                male_name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
    
    # Run migration after init_db
    migrate_database()

def generate_library_id():
    """Generate a unique library ID in format: LIB-XXXX-XXXX"""
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    part1 = ''.join(random.choice(chars) for _ in range(4))
    part2 = ''.join(random.choice(chars) for _ in range(4))
    return f"LIB-{part1}-{part2}"

def backup_database():
    """Create a backup of the database"""
    import shutil
    from datetime import datetime
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"names_backup_{timestamp}.db"
        shutil.copy2(app_config.DATABASE_URL, backup_filename)
        logger.info(f"Database backed up to {backup_filename}")
        return True
    except Exception as e:
        logger.error(f"Failed to backup database: {e}")
        return False

@app.route('/api/create-user', methods=['POST'])
def create_user():
    """Create a new user and return library ID"""
    try:
        library_id = generate_library_id()
        user_id = str(uuid.uuid4())
        
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('INSERT INTO users (id, library_id) VALUES (?, ?)', (user_id, library_id))
            conn.commit()
        
        return jsonify({
            'success': True, 
            'user_id': user_id, 
            'library_id': library_id,
            'message': 'User created successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login_user():
    """Login user with library ID"""
    data = request.get_json()
    library_id = data.get('library_id')
    
    if not library_id:
        return jsonify({'success': False, 'error': 'Library ID required'}), 400
    
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Find user by library ID
            c.execute('SELECT id, library_id, access_count FROM users WHERE library_id = ?', (library_id,))
            user = c.fetchone()
            
            if not user:
                return jsonify({'success': False, 'error': 'Invalid Library ID'}), 404
            
            user_id, library_id, access_count = user
            
            # Update access count and last access time
            c.execute('''
                UPDATE users 
                SET access_count = access_count + 1, last_access = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (user_id,))
            
            # Create new session
            c.execute('''
                INSERT INTO user_sessions (user_id, session_start) 
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (user_id,))
            
            session_id = c.lastrowid
            
            conn.commit()
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'library_id': library_id,
            'session_id': session_id,
            'access_count': access_count + 1,
            'message': 'Login successful'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/save-names', methods=['POST'])
def save_names():
    """Save names for a specific user"""
    logger.info("=== /api/save-names endpoint called ===")
    
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")
        
        user_id = data.get('user_id')
        female = data.get('female', '').strip()
        male = data.get('male', '').strip()
        
        logger.info(f"Parsed values - user_id: {user_id}, female: {female}, male: {male}")
        
        # Input validation
        if not all([user_id, female, male]):
            logger.warning("Missing required fields")
            return jsonify({'success': False, 'error': 'User ID and both names required'}), 400
        
        # Sanitize inputs (basic validation)
        if len(female) > 50 or len(male) > 50:
            logger.warning("Name length validation failed")
            return jsonify({'success': False, 'error': 'Names must be 50 characters or less'}), 400
        
        if not female.replace(' ', '').isalnum() or not male.replace(' ', '').isalnum():
            logger.warning("Name character validation failed")
            return jsonify({'success': False, 'error': 'Names can only contain letters, numbers, and spaces'}), 400

        logger.info("Input validation passed, connecting to database...")
        
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Check if user exists
            logger.info(f"Checking if user {user_id} exists...")
            c.execute('SELECT id FROM users WHERE id = ?', (user_id,))
            user_exists = c.fetchone()
            if not user_exists:
                logger.warning(f"User {user_id} not found")
                return jsonify({'success': False, 'error': 'Invalid user ID'}), 404
            
            logger.info(f"User {user_id} found, checking for existing name combination...")
            
            # Check if this name combination already exists for this user
            c.execute('''
                SELECT id, usage_count FROM user_names 
                WHERE user_id = ? AND female_name = ? AND male_name = ?
            ''', (user_id, female, male))
            
            existing = c.fetchone()
            logger.info(f"Existing name combination found: {existing}")
            
            if existing:
                # Update usage count
                name_id, current_count = existing
                logger.info(f"Updating usage count for name_id {name_id} from {current_count} to {current_count + 1}")
                c.execute('''
                    UPDATE user_names 
                    SET usage_count = usage_count + 1, created_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (name_id,))
            else:
                # Insert new name combination
                logger.info(f"Inserting new name combination for user {user_id}")
                c.execute('''
                    INSERT INTO user_names (user_id, female_name, male_name) 
                    VALUES (?, ?, ?)
                ''', (user_id, female, male))
            
            conn.commit()
            logger.info("Database transaction committed successfully")
        
        logger.info("=== /api/save-names completed successfully ===")
        return jsonify({'success': True, 'message': 'Names saved successfully'})
        
    except Exception as e:
        logger.error(f"=== /api/save-names ERROR: {str(e)} ===")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/update-session', methods=['POST'])
def update_session():
    """Update session with pages read"""
    data = request.get_json()
    session_id = data.get('session_id')
    pages_read = data.get('pages_read', 0)
    
    if not session_id:
        return jsonify({'success': False, 'error': 'Session ID required'}), 400
    
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            c.execute('''
                UPDATE user_sessions 
                SET pages_read = ? 
                WHERE id = ?
            ''', (pages_read, session_id))
            
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Session updated'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/end-session', methods=['POST'])
def end_session():
    """End a reading session"""
    data = request.get_json()
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'success': False, 'error': 'Session ID required'}), 400
    
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            c.execute('''
                UPDATE user_sessions 
                SET session_end = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (session_id,))
            
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Session ended'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user-stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Get user statistics"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Get user info
            c.execute('''
                SELECT library_id, created_at, last_access, access_count 
                FROM users WHERE id = ?
            ''', (user_id,))
            user = c.fetchone()
            
            if not user:
                return jsonify({'success': False, 'error': 'User not found'}), 404
            
            library_id, created_at, last_access, access_count = user
            
            # Get name combinations used
            c.execute('''
                SELECT female_name, male_name, usage_count, created_at 
                FROM user_names 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            ''', (user_id,))
            names = c.fetchall()
            
            # Get session statistics
            c.execute('''
                SELECT COUNT(*) as total_sessions, 
                       SUM(pages_read) as total_pages,
                       AVG(pages_read) as avg_pages_per_session
                FROM user_sessions 
                WHERE user_id = ?
            ''', (user_id,))
            session_stats = c.fetchone()
        
        return jsonify({
            'success': True,
            'user': {
                'library_id': library_id,
                'created_at': created_at,
                'last_access': last_access,
                'access_count': access_count
            },
            'names_used': [
                {
                    'female_name': row[0],
                    'male_name': row[1],
                    'usage_count': row[2],
                    'created_at': row[3]
                } for row in names
            ],
            'session_stats': {
                'total_sessions': session_stats[0] or 0,
                'total_pages_read': session_stats[1] or 0,
                'avg_pages_per_session': round(session_stats[2] or 0, 2)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
def get_admin_stats():
    """Get overall statistics for admin panel"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Get overall statistics
            c.execute('SELECT COUNT(*) FROM users')
            total_users = c.fetchone()[0]
            
            c.execute('SELECT COUNT(*) FROM user_sessions')
            total_sessions = c.fetchone()[0]
            
            c.execute('SELECT SUM(pages_read) FROM user_sessions')
            total_pages = c.fetchone()[0] or 0
            
            c.execute('SELECT COUNT(*) FROM user_names')
            total_name_combinations = c.fetchone()[0]
            
            # Get all users with their stats
            c.execute('''
                SELECT u.id, u.library_id, u.created_at, u.last_access, u.access_count,
                       COALESCE(SUM(us.pages_read), 0) as total_pages_read,
                       COUNT(us.id) as total_sessions
                FROM users u
                LEFT JOIN user_sessions us ON u.id = us.user_id
                GROUP BY u.id
                ORDER BY u.created_at DESC
            ''')
            users = c.fetchall()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_sessions': total_sessions,
                'total_pages_read': total_pages,
                'total_name_combinations': total_name_combinations
            },
            'users': [
                {
                    'user_id': row[0],
                    'library_id': row[1],
                    'created_at': row[2],
                    'last_access': row[3],
                    'access_count': row[4],
                    'total_pages_read': row[5],
                    'total_sessions': row[6]
                } for row in users
            ]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/backup', methods=['POST'])
def create_backup():
    """Create a database backup"""
    try:
        if backup_database():
            return jsonify({'success': True, 'message': 'Database backup created successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to create backup'}), 500
    except Exception as e:
        logger.error(f"Backup error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def home():
    return 'E-Book Library API is running!'

@app.route('/frontend/')
def frontend():
    return send_from_directory('frontend', 'index.html')

@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    return send_from_directory('frontend', filename)

if __name__ == '__main__':
    init_db()
    app.run(
        debug=app_config.FLASK_DEBUG, 
        host=app_config.HOST, 
        port=app_config.PORT
    )