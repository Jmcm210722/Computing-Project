#  BodyBalance

A modern React-based workout tracking application that connects to a Flask backend API. Track your exercises, sets, reps, and workout history with an intuitive interface.

## Features

-  **Start Workouts** - Create new workouts by selecting muscle groups
-  **Exercise Library** - Browse 44+ pre-loaded exercises or create custom ones
-  **Real-time Set Logging** - Log sets with weight and reps as you go
-  **Workout History** - View completed workouts with detailed statistics
-  **Auto-save** - All data is persisted to your backend
-  **User Tracking** - Each user has their own workout data

## Prerequisites

- Node.js (v16 or higher)
- Flask Backend running at `http://localhost:5000`
- Your backend must have CORS enabled for the frontend

## Installation

```bash
# Install dependencies
npm install

# Start the development server
npm run dev
```

The app will be available at `http://localhost:5173` (or next available port).

## Usage

### 1. Start a Workout

- Click "Start New Workout" on the home screen
- Select a muscle group (Chest, Back, Legs, Shoulders, Biceps, Triceps, Core)

### 2. Add Exercises

- Browse the exercise list for your selected muscle group
- Select an exercise and click "Add Exercise"

### 3. Log Sets

- Expand an exercise in your active workout
- Enter reps and weight (or check "Bodyweight only")
- Click "Log Set" to record it
- Repeat for each set

### 4. Complete Workout

- Add more exercises as needed
- Click "Complete Workout" when finished
- View your workout in the history

### 5. View History

- Click "View Workout History" from home
- See all completed workouts with stats
- Expand workouts to view detailed set information

## API Connection

The app connects to `http://localhost:5000/api` by default. To change this:

1. Open [src/api.js](src/api.js)
2. Modify the `API_BASE` constant

```javascript
const API_BASE = "http://your-backend-url:port/api";
```

## Project Structure

```
src/
├── api.js                    # API service layer (11 endpoints)
├── context/
│   └── WorkoutContext.jsx    # Global state management
├── screens/
│   ├── StartScreen.jsx       # Home screen
│   ├── MuscleGroupSelector.jsx
│   ├── ExerciseList.jsx
│   ├── ActiveWorkout.jsx     # Workout in progress
│   └── WorkoutHistory.jsx
├── components/
│   ├── ErrorAlert.jsx
│   ├── LoadingSpinner.jsx
│   └── SetLogger.jsx         # Form to log sets
└── App.jsx                   # Main app component
```

## Technologies Used

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Context API** - State management
- **Fetch API** - HTTP requests

## Backend Requirements

Your Flask backend should expose these endpoints:

- `GET /api/muscle-groups` - List muscle groups
- `GET /api/exercises` - List exercises (with filters)
- `POST /api/exercises` - Create custom exercise
- `POST /api/workouts/start` - Start new workout
- `GET /api/workouts/<id>` - Get workout details
- `GET /api/workouts` - List user workouts
- `POST /api/workouts/<id>/entries` - Add exercise to workout
- `POST /api/workouts/<id>/entries/<entry_id>/sets` - Log a set
- `POST /api/workouts/<id>/finish` - Complete workout

## Development

```bash
# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## User ID

Each user is assigned a unique ID (visible on the start screen). This ID is used to track workouts and custom exercises. In production, replace this with your authentication system.

## Contributing

This is a frontend application designed to work with the BodyBalance Flask API. Ensure your backend is running before using the app.

## License

MIT
