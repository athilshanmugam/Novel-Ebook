# When Hearts Whisper - E-Book Library System

A beautiful, interactive e-book with a complete library card system for tracking user reading sessions and personalized character names.

## Features

### For Readers
- **📚 Library Card System**: Unique library IDs for each user
- **🔐 User Authentication**: Login with library ID to track reading progress
- **📝 Personalized Names**: Customize character names for a personal reading experience
- **📊 Reading Statistics**: Track pages read, sessions, and reading patterns
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **🎨 Navigation**: Easy page-by-page navigation with Previous/Next buttons
- **⌨️ Keyboard Support**: Use arrow keys to navigate through pages
- **👆 Touch/Swipe Support**: Swipe left/right on mobile devices to navigate
- **🔤 Font Size Control**: Adjust text size for comfortable reading
- **🌙 Dark/Light Theme**: Toggle between light and dark reading modes
- **📈 Reading Progress**: Visual progress bar at the bottom of the screen
- **🔖 Bookmark Feature**: Automatically saves your reading progress
- **🎨 Beautiful Typography**: Elegant fonts optimized for reading

### For Administrators
- **📊 Admin Dashboard**: Complete overview of all users and statistics
- **👥 User Management**: View all library card holders and their data
- **📈 Analytics**: Track total users, sessions, pages read, and name combinations
- **🔍 Search Functionality**: Find users by library ID
- **📋 Detailed Reports**: View individual user reading patterns and preferences
- **📊 Data Export**: Export user statistics to CSV format

## How to Use

### For Readers

1. **Start the Application**: 
   ```bash
   python app.py
   ```

2. **Open the E-Book**: Navigate to `http://localhost:5000` in your browser

3. **Get a Library Card**:
   - Click "New Card" to create a new library ID
   - Save your library ID (format: LIB-XXXX-XXXX)

4. **Login**:
   - Enter your library ID and click "Login"
   - Your reading statistics will be displayed

5. **Personalize Your Story**:
   - Enter custom names for the female and male characters
   - Click "Start Reading" to begin

6. **Enjoy Reading**:
   - Navigate using Previous/Next buttons or arrow keys
   - Adjust font size and theme as needed
   - Your progress is automatically saved

### For Administrators

1. **Access Admin Panel**: Open `admin.html` in your browser

2. **View Statistics**: 
   - Total users, sessions, pages read, and name combinations
   - Real-time data updates

3. **Manage Users**:
   - View all library card holders
   - Search for specific users
   - View detailed user statistics

4. **Export Data**: Download user statistics as CSV file

## File Structure

```
novel/
├── app.py                 # Flask backend with library card system
├── index.html            # Main e-book interface
├── admin.html            # Admin dashboard
├── script.js             # Frontend functionality
├── names.db              # SQLite database
├── book-cover.png        # Book cover image
├── README.md             # This file
└── When Hearts Whisper ..pdf  # Original PDF source
```

## Database Schema

### Users Table
- `id`: Unique user identifier
- `library_id`: Library card number (LIB-XXXX-XXXX format)
- `created_at`: Account creation timestamp
- `last_access`: Last login timestamp
- `access_count`: Total number of logins

### User Sessions Table
- `id`: Session identifier
- `user_id`: Reference to user
- `session_start`: Session start timestamp
- `session_end`: Session end timestamp
- `pages_read`: Number of pages read in session

### User Names Table
- `id`: Name combination identifier
- `user_id`: Reference to user
- `female_name`: Custom female character name
- `male_name`: Custom male character name
- `created_at`: First usage timestamp
- `usage_count`: Number of times this combination was used

## API Endpoints

### User Management
- `POST /api/create-user` - Create new library card
- `POST /api/login` - Login with library ID
- `POST /api/save-names` - Save character names
- `POST /api/update-session` - Update reading progress
- `POST /api/end-session` - End reading session

### Statistics
- `GET /api/user-stats/<user_id>` - Get individual user statistics
- `GET /api/admin/stats` - Get overall system statistics

## Technical Details

- **Backend**: Flask with SQLite database
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Database**: SQLite with proper foreign key relationships
- **Session Management**: Automatic session tracking and cleanup
- **Data Persistence**: Local storage for user preferences, database for analytics

## Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (iOS Safari, Chrome Mobile)

## Security Features

- Unique library IDs prevent unauthorized access
- Session-based tracking for accurate analytics
- Input validation and error handling
- Secure database queries with parameterized statements

## Customization

To customize the e-book:

1. **Content**: Edit the HTML content in `index.html`
2. **Styling**: Modify Tailwind classes or add custom CSS
3. **Functionality**: Update JavaScript features in `script.js`
4. **Database**: Modify schema in `app.py` init_db() function

## Reading Experience

The e-book provides a premium reading experience with:
- Clean, distraction-free layout
- Optimal line spacing and typography
- Smooth page transitions
- Progress tracking with detailed analytics
- Personalized character names
- Responsive design for all screen sizes

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install flask flask-cors
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Access the E-Book**:
   - Reader interface: `http://localhost:5000`
   - Admin panel: Open `admin.html` in browser

4. **Create Your First Library Card**:
   - Click "New Card" to get a library ID
   - Use this ID to login and start reading

Enjoy reading "When Hearts Whisper" with your personalized library experience! 📚✨ 