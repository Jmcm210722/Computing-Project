# Frontend Integration Prompt for BodyBalance Backend

## Context

You are building a React frontend for BodyBalance, a workout tracking application similar to RepCount. The backend is a Flask API running on `http://localhost:5000` with CORS enabled. It provides complete authentication, profile management, and workout tracking functionality.

## Backend Architecture

**Base URL**: `http://localhost:5000`

**Technology Stack**:

- Flask 3.1.2 with CORS enabled
- MongoDB database
- JWT authentication (7-day expiration)
- Bcrypt password hashing

**CORS Configuration**:

- All `/api/*` routes have CORS enabled
- All origins accepted (`*`)
- No additional headers required for CORS

## Authentication System

### Authentication Flow

1. **Registration** → User creates account
2. **Login** → User receives JWT token
3. **Onboarding** → User completes profile (gets calorie goal)
4. **Ongoing Usage** → User tracks workouts with authenticated endpoints

### Token Management

**Token Storage**: Save JWT token in localStorage or secure cookie after login/registration

**Token Usage**: Include in Authorization header for protected endpoints:

```javascript
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

**Token Expiration**: 7 days (604,800 seconds)

**Refresh Flow**: When token expires, redirect user to login

## Complete API Reference

### 1. Authentication Endpoints

#### Register User

```
POST /api/auth/register

Request Body:
{
  "email": "user@example.com",
  "password": "securepass123"
}

Response (201):
{
  "user": {
    "_id": "string",
    "email": "user@example.com",
    "created_at": "2026-02-06T18:00:00.000Z",
    "updated_at": "2026-02-06T18:00:00.000Z"
  },
  "token": "eyJhbG..."
}

Errors:
- 400: Invalid email format, password too short, email already exists
```

#### Login User

```
POST /api/auth/login

Request Body:
{
  "email": "user@example.com",
  "password": "securepass123"
}

Response (200):
{
  "user": { ... },
  "token": "eyJhbG..."
}

Errors:
- 400: Missing email or password
- 401: Invalid credentials
```

### 2. Profile Endpoints (Protected)

#### Complete Onboarding

```
POST /api/profile/onboarding
Headers: Authorization: Bearer <token>

Request Body:
{
  "sex": "male",              // "male" | "female"
  "age": 30,                  // 13-120
  "height_cm": 180,           // 50-300
  "weight_kg": 75,            // 20-500
  "activity_level": "moderate", // "sedentary" | "light" | "moderate" | "very" | "extra"
  "goal": "maintain_weight"   // "lose_weight" | "maintain_weight" | "gain_weight"
}

Response (200):
{
  "profile": {
    "_id": "string",
    "user_id": "string",
    "sex": "male",
    "age": 30,
    "height_cm": 180.0,
    "weight_kg": 75.0,
    "activity_level": "moderate",
    "goal": "maintain_weight",
    "bmr": 1730,              // Basal Metabolic Rate
    "tdee": 2682,             // Total Daily Energy Expenditure
    "calorie_goal": 2682,     // Calculated calorie target
    "created_at": "2026-02-06T18:00:00.000Z",
    "updated_at": "2026-02-06T18:00:00.000Z"
  },
  "calorie_goal": 2682
}

Errors:
- 400: Validation errors (returns object with field-specific errors)
- 401: Invalid/expired token
```

#### Get Profile

```
GET /api/profile/me
Headers: Authorization: Bearer <token>

Response (200):
{
  "profile": { ... },
  "calorie_goal": 2682
}

Errors:
- 401: Invalid/expired token
- 404: Profile not found (user hasn't completed onboarding)
```

#### Update Profile

```
PUT /api/profile/me
Headers: Authorization: Bearer <token>

Request Body (all fields optional):
{
  "weight_kg": 72,
  "goal": "lose_weight"
}

Response (200):
{
  "profile": { ... },  // Updated profile with recalculated calories
  "calorie_goal": 2096 // New calorie goal
}

Errors:
- 400: Validation errors
- 401: Invalid/expired token
- 404: Profile not found
```

### 3. Calorie Tracking Endpoints (Protected)

**Important**: All calorie tracking endpoints require authentication and use the user's calorie goal from their profile.

#### Get Today's Calories

```
GET /api/calories/today
Headers: Authorization: Bearer <token>

Response (200):
{
  "date": "2026-02-06",
  "goal_calories": 2682,
  "consumed_calories": 500,
  "remaining_calories": 2182,  // ALWAYS calculated on server: goal - consumed
  "items": [
    {
      "item_id": "f4431de8-c725-4ac5-9750-7219078bdd50",
      "food_name": "Chicken Breast",
      "calories": 250,
      "created_at": "2026-02-06T12:30:00.000Z"
    }
  ]
}

Note: Creates a new calorie_day document if one doesn't exist for today.
      Frontend should NEVER calculate remaining_calories - always use server value.

Errors:
- 400: User profile not found (needs onboarding)
- 401: Invalid/expired token
```

#### Add Food Item

```
POST /api/calories/items
Headers: Authorization: Bearer <token>

Request Body:
{
  "food_name": "Chicken Breast",
  "calories": 250
}

Validation:
- food_name: Required, non-empty string
- calories: Required, positive number

Response (201):
{
  "date": "2026-02-06",
  "goal_calories": 2682,
  "consumed_calories": 750,       // Updated: previous + new
  "remaining_calories": 1932,     // Recalculated: goal - consumed
  "items": [                      // Full array including new item
    {...},
    {...}
  ],
  "added_item": {                 // The newly added item
    "item_id": "uuid",
    "food_name": "Chicken Breast",
    "calories": 250,
    "created_at": "2026-02-06T12:30:00.000Z"
  }
}

CRITICAL: remaining_calories is ALWAYS calculated on the server.
          Frontend must use the returned value, not calculate locally.

Errors:
- 400: Validation error (empty food_name, missing/negative calories)
- 401: Invalid/expired token
```

#### Edit Food Item

```
PUT /api/calories/items/<item_id>
Headers: Authorization: Bearer <token>

Request Body (at least one field required):
{
  "food_name": "Grilled Chicken",  // Optional: new food name
  "calories": 280                   // Optional: new calorie value
}

Response (200):
{
  "date": "2026-02-06",
  "goal_calories": 2682,
  "consumed_calories": 530,       // Recalculated: total of all items
  "remaining_calories": 2152,     // Recalculated: goal - consumed
  "items": [...],                 // Full array with edited item
  "edited_item": {
    "item_id": "uuid",
    "food_name": "Grilled Chicken",
    "calories": 280,
    "created_at": "2026-02-06T12:30:00.000Z"
  }
}

CRITICAL: remaining_calories is ALWAYS recalculated on the server.
          Frontend must use the returned value, not calculate locally.

Errors:
- 400: Validation error (empty food_name, missing/negative calories, no fields provided)
- 404: Food item not found
- 401: Invalid/expired token
```

#### Delete Food Item

```
DELETE /api/calories/items/<item_id>
Headers: Authorization: Bearer <token>

Response (200):
{
  "message": "Food item deleted successfully",
  "date": "2026-02-06",
  "goal_calories": 2682,
  "consumed_calories": 500,       // Recalculated: previous - deleted
  "remaining_calories": 2182,     // Recalculated: goal - consumed
  "items": [...],                 // Updated array without deleted item
  "deleted_item_id": "uuid"
}

Errors:
- 404: Food item not found or no data for this date
- 401: Invalid/expired token
```

#### Get Calories by Date (Optional)

```
GET /api/calories?date=YYYY-MM-DD
Headers: Authorization: Bearer <token>

Query Params:
- date: YYYY-MM-DD format (optional, defaults to today)

Response (200):
{
  "date": "2026-02-05",
  "goal_calories": 2682,
  "consumed_calories": 2100,
  "remaining_calories": 582,
  "items": [...]
}

Errors:
- 400: Invalid date format
- 404: No data for this date
- 401: Invalid/expired token
```

#### Get Weekly Progress

```
GET /api/calories/weekly
Headers: Authorization: Bearer <token>

Response (200):
{
  "weekly_data": [
    {
      "date": "2026-02-03",
      "day_name": "Monday",
      "goal_calories": 2682,
      "consumed_calories": 2100,
      "remaining_calories": 582,
      "goal_met": true,
      "has_data": true
    },
    {
      "date": "2026-02-04",
      "day_name": "Tuesday",
      "goal_calories": 2682,
      "consumed_calories": 0,
      "remaining_calories": 2682,
      "goal_met": false,
      "has_data": false
    }
    // ... 7 days total (6 days ago through today)
  ]
}

Field Descriptions:
- date: Date in YYYY-MM-DD format
- day_name: Day of the week (Monday, Tuesday, etc.)
- goal_calories: User's daily calorie goal from profile
- consumed_calories: Total calories logged for that day
- remaining_calories: goal_calories - consumed_calories
- goal_met: true if consumed <= goal AND consumed > 0 (not logged days are false)
- has_data: true if at least one food item was logged that day

Use Cases:
- Display weekly progress chart showing goal achievement
- Visualize calorie consumption trends over 7 days
- Show streak of days meeting calorie goals
- Identify days with no tracking activity

Errors:
- 400: User profile not found (needs onboarding)
- 401: Invalid/expired token
```

**Calorie Tracking Flow**:

1. User completes onboarding (gets calorie_goal)
2. User views today's calories: `GET /api/calories/today`
3. User adds food: `POST /api/calories/items`
4. UI updates with returned `consumed_calories` and `remaining_calories`
5. User edits food: `PUT /api/calories/items/<item_id>`
6. UI updates with recalculated totals from response
7. User deletes food: `DELETE /api/calories/items/<item_id>`
8. UI updates with recalculated totals from response

**MongoDB Design**:

- Collection: `calorie_days`
- One document per user per date (unique index on `user_id + date`)
- Document structure:
  ```javascript
  {
    _id: ObjectId,
    user_id: ObjectId,
    date: "2026-02-06",
    goal_calories: 2682,        // From user profile
    consumed_calories: 500,      // Sum of all items
    remaining_calories: 2182,    // goal - consumed
    items: [
      {
        item_id: "uuid",
        food_name: "string",
        calories: number,
        created_at: datetime
      }
    ],
    created_at: datetime,
    updated_at: datetime
  }
  ```

### 4. Muscle Groups Endpoint

#### Get All Muscle Groups

```
GET /api/muscle-groups

Response (200):
[
  {
    "_id": "string",
    "name": "Chest",
    "description": "Pectorals"
  },
  // ... 7 total groups
]
```

**Available Muscle Groups**:

- Chest
- Back
- Shoulders
- Arms
- Legs
- Core
- Full Body

### 5. Exercise Endpoints

#### Get All Exercises

```
GET /api/exercises

Response (200):
[
  {
    "_id": "string",
    "name": "Bench Press",
    "muscle_group_id": "string",
    "muscle_group_name": "Chest",
    "is_custom": false,
    "created_by": null,
    "created_at": "2026-01-01T00:00:00.000Z"
  },
  // ... 44+ exercises
]
```

#### Get Single Exercise

```
GET /api/exercises/<exercise_id>

Response (200):
{
  "_id": "string",
  "name": "Bench Press",
  "muscle_group_id": "string",
  "muscle_group_name": "Chest",
  "is_custom": false
}

Errors:
- 404: Exercise not found
```

#### Create Custom Exercise

```
POST /api/exercises

Request Body:
{
  "user_id": "string",              // Required: owning user
  "name": "My Custom Exercise",     // Required: exercise name
  "muscle_group_id": "string",      // Required: muscle group selection
  "primary_muscle_id": "string",    // Optional alias of muscle_group_id
  "secondary_muscle_ids": ["string"],
  "equipment": "bodyweight",        // Optional (defaults to "bodyweight")
  "category": "custom"              // Optional (defaults to "custom")
}

Response (201):
{
  "_id": "string",
  "name": "My Custom Exercise",
  "primary_muscle_id": "string",
  "secondary_muscle_ids": [],
  "equipment": "bodyweight",
  "category": "custom",
  "is_custom": true,
  "created_by": "string",
  "created_at": "2026-02-06T18:00:00.000Z"
}

Errors:
- 400: Missing user_id, name, or muscle_group_id
- 400: Invalid muscle_group_id
```

#### Add Custom Exercise to Active Workout (Flow)

1. Create or resume the user's active workout:

```
POST /api/workouts/start

Request Body:
{
  "user_id": "string"
}
```

2. Create the custom exercise in the selected muscle group:

```
POST /api/exercises

Request Body:
{
  "user_id": "string",
  "name": "My Custom Exercise",
  "muscle_group_id": "string"
}
```

3. Add the custom exercise to the active workout:

```
POST /api/workouts/<workout_id>/entries

Request Body:
{
  "exercise_id": "ex_custom_...",
  "exercise_name_snapshot": "My Custom Exercise"
}
```

This places the custom exercise into the workout just like seeded exercises.

**Single-call option (recommended)**:

```
POST /api/workouts/<workout_id>/entries/custom

Request Body:
{
  "user_id": "string",
  "name": "My Custom Exercise",
  "muscle_group_id": "string",
  "secondary_muscle_ids": ["string"],
  "equipment": "bodyweight",
  "category": "custom",
  "notes": "string"
}

Response (201):
{
  "exercise": {
    "_id": "ex_custom_...",
    "name": "My Custom Exercise",
    "primary_muscle_id": "string",
    "secondary_muscle_ids": [],
    "equipment": "bodyweight",
    "category": "custom",
    "is_custom": true,
    "created_by": "string",
    "created_at": "2026-02-06T18:00:00.000Z"
  },
  "entry": {
    "entry_id": "string",
    "exercise_id": "ex_custom_...",
    "exercise_name_snapshot": "My Custom Exercise",
    "sets": [],
    "notes": ""
  },
  "workout": { ... }
}

Errors:
- 400: Missing user_id, name, or muscle_group_id
- 403: Workout does not belong to user
- 404: Workout not found
```

### 6. Workout Endpoints

#### Start New Workout

```
POST /api/workouts

Request Body:
{
  "name": "Push Day",           // Optional
  "user_id": "string"           // Optional: for per-user workouts
}

Response (201):
{
  "_id": "string",
  "name": "Push Day",
  "started_at": "2026-02-06T18:00:00.000Z",
  "completed_at": null,
  "entries": [],
  "user_id": "string"
}
```

#### List All Workouts

```
GET /api/workouts

Response (200):
[
  {
    "_id": "string",
    "name": "Push Day",
    "started_at": "2026-02-06T18:00:00.000Z",
    "completed_at": "2026-02-06T19:30:00.000Z",
    "entries": [ ... ],
    "duration_minutes": 90
  },
  // ... all workouts
]
```

#### Get Single Workout

```
GET /api/workouts/<workout_id>

Response (200):
{
  "_id": "string",
  "name": "Push Day",
  "started_at": "2026-02-06T18:00:00.000Z",
  "completed_at": "2026-02-06T19:30:00.000Z",
  "entries": [
    {
      "entry_id": "string",
      "exercise_id": "string",
      "exercise_name": "Bench Press",
      "sets": [
        {
          "set_number": 1,
          "weight_kg": 80,
          "reps": 10
        }
      ]
    }
  ],
  "user_id": "string"
}

Errors:
- 404: Workout not found
```

#### Add Exercise Entry to Workout

```
POST /api/workouts/<workout_id>/entries

Request Body:
{
  "exercise_id": "string",
  "exercise_name_snapshot": "Bench Press"
}

Response (200):
{
  "entry": {
    "entry_id": "string",
    "exercise_id": "string",
    "exercise_name_snapshot": "Bench Press",
    "sets": [],
    "notes": ""
  },
  "workout": { ... }
}

Errors:
- 400: Missing exercise_id or exercise_name_snapshot
- 404: Workout or exercise not found
```

#### Add Custom Exercise Entry to Workout (Single Call)

```
POST /api/workouts/<workout_id>/entries/custom

Request Body:
{
  "user_id": "string",
  "name": "My Custom Exercise",
  "muscle_group_id": "string",
  "secondary_muscle_ids": ["string"],
  "equipment": "bodyweight",
  "category": "custom",
  "notes": "string"
}

Response (201):
{
  "exercise": { ... },
  "entry": { ... },
  "workout": { ... }
}

Errors:
- 400: Missing user_id, name, or muscle_group_id
- 403: Workout does not belong to user
- 404: Workout not found
```

#### Delete Exercise Entry

```
DELETE /api/workouts/<workout_id>/entries/<entry_id>

Response (200):
{
  "message": "Entry deleted successfully"
}

Errors:
- 404: Workout or entry not found
```

#### Add Set to Exercise

```
PUT /api/workouts/<workout_id>/entries/<entry_id>/sets

Request Body:
{
  "weight_kg": 80,
  "reps": 10
}

Response (200):
{
  "workout_id": "string",
  "entry_id": "string",
  "set": {
    "set_number": 1,
    "weight_kg": 80,
    "reps": 10
  }
}

Errors:
- 400: Missing weight_kg or reps
- 404: Workout or entry not found
```

#### Edit Set

```
PUT /api/workouts/<workout_id>/entries/<entry_id>/sets/<set_number>

Request Body (all fields optional):
{
  "weight_kg": 85,
  "reps": 8
}

Response (200):
{
  "workout_id": "string",
  "entry_id": "string",
  "set": {
    "set_number": 1,
    "weight_kg": 85,
    "reps": 8
  }
}

Errors:
- 404: Workout, entry, or set not found
```

#### Delete Set

```
DELETE /api/workouts/<workout_id>/entries/<entry_id>/sets/<set_number>

Response (200):
{
  "message": "Set deleted successfully",
  "remaining_sets": [ ... ]  // Automatically renumbered
}

Errors:
- 404: Workout, entry, or set not found
```

#### Finish Workout

```
POST /api/workouts/<workout_id>/finish

Response (200):
{
  "_id": "string",
  "status": "completed",
  "started_at": "2026-02-06T18:00:00.000Z",
  "ended_at": "2026-02-06T19:30:00.000Z",
  "entries": [ ... ]
}

Errors:
- 404: Workout not found
```

### 7. Workout Progress Endpoints

#### Get Today's Workout Progress

```
GET /api/workouts/progress/today?user_id=<user_id>

Response (200):
{
  "date": "2026-02-18",
  "day_name": "Wednesday",
  "workouts_completed": 1,
  "total_sets": 8,
  "total_reps": 120,
  "total_weight": 1200.5,
  "exercises_done": 4,
  "muscle_groups": ["Chest", "Back"],
  "had_workout": true
}

Field Descriptions:
- date: Date in YYYY-MM-DD format
- day_name: Day of the week (Monday, Tuesday, etc.)
- workouts_completed: Number of completed workouts today
- total_sets: Total number of sets across all workouts today
- total_reps: Total reps across all sets
- total_weight: Total weight lifted (in kg) across all sets
- exercises_done: Count of unique exercises performed
- muscle_groups: List of muscle groups trained today
- had_workout: true if any workout was completed today

Use Cases:
- Display today's workout summary
- Show progress metrics for the current day
- Check if user worked out today before starting a new session

Errors:
- 400: user_id query parameter is required
```

```
GET /api/workouts/progress/weekly?user_id=<user_id>

Response (200):
{
  "weekly_data": [
    {
      "date": "2026-02-03",
      "day_name": "Monday",
      "workouts_completed": 2,
      "total_sets": 8,
      "total_reps": 120,
      "total_weight": 1200.5,
      "exercises_done": 4,
      "muscle_groups": ["Chest", "Back"],
      "had_workout": true
    },
    {
      "date": "2026-02-04",
      "day_name": "Tuesday",
      "workouts_completed": 0,
      "total_sets": 0,
      "total_reps": 0,
      "total_weight": 0.0,
      "exercises_done": 0,
      "muscle_groups": [],
      "had_workout": false
    }
    // ... 7 days total (6 days ago through today)
  ]
}

Field Descriptions:
- date: Date in YYYY-MM-DD format
- day_name: Day of the week (Monday, Tuesday, etc.)
- workouts_completed: Number of completed workouts on that day
- total_sets: Total number of sets across all workouts
- total_reps: Total reps across all sets
- total_weight: Total weight lifted (in kg) across all sets
- exercises_done: Count of unique exercises performed
- muscle_groups: List of muscle groups trained
- had_workout: true if any workout was completed that day

Use Cases:
- Display weekly progress chart showing workout activity
- Visualize volume trends (sets, reps, weight) over 7 days
- Show streak of days with workouts
- Track muscle group distribution per day

Errors:
- 400: user_id query parameter is required
```

#### Get Monthly Workout Statistics

```
GET /api/workouts/progress/monthly?user_id=<user_id>

Response (200):
{
  "monthly_stats": {
    "total_workouts": 15,
    "total_sets": 120,
    "total_reps": 3000,
    "total_weight": 35000.5,
    "unique_exercises": 12,
    "unique_muscle_groups": 6,
    "avg_sets_per_workout": 8.0,
    "avg_reps_per_set": 25.0,
    "most_trained_muscle_group": "Chest"
  }
}
```

Field Descriptions:

- total_workouts: Number of completed workouts this month
- total_sets: Total sets across all workouts
- total_reps: Total reps across all sets
- total_weight: Total weight lifted in kg
- unique_exercises: Number of different exercises performed
- unique_muscle_groups: Number of different muscle groups trained
- avg_sets_per_workout: Average sets per workout
- avg_reps_per_set: Average reps per set
- most_trained_muscle_group: The muscle group with most sessions

Use Cases:

- Display monthly summary card with aggregate stats
- Show fitness goals progress (total volume, exercises, variety)
- Identify primary training focus
- Track consistency (workouts per month)

Errors:

- 400: user_id query parameter is required

````

### 8. Fitness Chatbot Endpoint (Protected)

#### Send Chat Message

```
POST /api/chatbot/message
Headers: Authorization: Bearer <token>

Request Body:
{
  "message": "What are the best workouts for beginners?"
}

Response (200):
{
  "intent": "beginner_workouts",
  "reply": "For beginners, focus on full-body sessions 2-3x per week to build a base.",
  "suggested_workouts": [
    "Full-body circuit: squat, push-up, row, plank",
    "Machine-based full-body: leg press, chest press, lat pulldown",
    "Short cardio + mobility: 15 min walk + hip/shoulder mobility"
  ],
  "tips": [
    "Keep it simple: 2-3 sets of 8-12 reps",
    "Leave 1-2 reps in reserve on each set",
    "Rest 60-90 seconds between sets"
  ],
  "created_at": "2026-02-24T18:15:00.000Z"
}

Errors:
- 400: message is required
- 400: message must be 500 characters or fewer
- 401: Invalid/expired token
```

## TypeScript Types

```typescript
// Auth Types
interface User {
  _id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

interface AuthResponse {
  user: User;
  token: string;
}

// Profile Types
type Sex = "male" | "female";
type ActivityLevel = "sedentary" | "light" | "moderate" | "very" | "extra";
type Goal = "lose_weight" | "maintain_weight" | "gain_weight";

interface Profile {
  _id: string;
  user_id: string;
  sex: Sex;
  age: number;
  height_cm: number;
  weight_kg: number;
  activity_level: ActivityLevel;
  goal: Goal;
  bmr: number;
  tdee: number;
  calorie_goal: number;
  created_at: string;
  updated_at: string;
}

interface ProfileResponse {
  profile: Profile;
  calorie_goal: number;
}

// Calorie Tracking Types
interface FoodItem {
  item_id: string;
  food_name: string;
  calories: number;
  created_at: string;
}

interface CalorieDay {
  date: string; // YYYY-MM-DD
  goal_calories: number;
  consumed_calories: number;
  remaining_calories: number; // ALWAYS use server value, never calculate
  items: FoodItem[];
}

interface AddFoodResponse extends CalorieDay {
  added_item: FoodItem;
}

interface EditFoodResponse extends CalorieDay {
  edited_item: FoodItem;
}

interface DeleteFoodResponse extends CalorieDay {
  message: string;
  deleted_item_id: string;
}

interface WeeklyProgressDay {
  date: string; // YYYY-MM-DD
  day_name: string; // Monday, Tuesday, etc.
  goal_calories: number;
  consumed_calories: number;
  remaining_calories: number;
  goal_met: boolean; // true if consumed <= goal AND consumed > 0
  has_data: boolean; // true if at least one food item was logged
}

interface WeeklyProgressResponse {
  weekly_data: WeeklyProgressDay[];
}

// Workout Types
interface Set {
  set_number: number;
  weight_kg: number;
  reps: number;
}

interface Entry {
  entry_id: string;
  exercise_id: string;
  exercise_name: string;
  sets: Set[];
}

interface Workout {
  _id: string;
  name?: string;
  started_at: string;
  completed_at: string | null;
  entries: Entry[];
  user_id?: string;
  duration_minutes?: number;
}

// Exercise Types
interface Exercise {
  _id: string;
  name: string;
  muscle_group_id: string;
  muscle_group_name: string;
  is_custom: boolean;
  created_by: string | null;
  created_at: string;
}

interface CustomExerciseEntryResponse {
  exercise: {
    _id: string;
    name: string;
    primary_muscle_id: string;
    secondary_muscle_ids: string[];
    equipment: string;
    category: string;
    is_custom: boolean;
    created_by: string;
    created_at: string;
  };
  entry: {
    entry_id: string;
    exercise_id: string;
    exercise_name_snapshot: string;
    sets: Set[];
    notes?: string;
  };
  workout: Workout;
}

interface MuscleGroup {
  _id: string;
  name: string;
  description: string;
}

// Workout Progress Types
interface WorkoutProgressDay {
  date: string; // YYYY-MM-DD
  day_name: string; // Monday, Tuesday, etc.
  workouts_completed: number;
  total_sets: number;
  total_reps: number;
  total_weight: number; // kg
  exercises_done: number;
  muscle_groups: string[];
  had_workout: boolean;
}

interface TodayWorkoutProgressResponse extends WorkoutProgressDay {}

interface WeeklyWorkoutProgressResponse {
  weekly_data: WorkoutProgressDay[];
}

interface MonthlyStat {
  total_workouts: number;
  total_sets: number;
  total_reps: number;
  total_weight: number; // kg
  unique_exercises: number;
  unique_muscle_groups: number;
  avg_sets_per_workout: number;
  avg_reps_per_set: number;
  most_trained_muscle_group: string | null;
}

interface MonthlyWorkoutStatsResponse {
  monthly_stats: MonthlyStat;
}

// Chatbot Types
interface ChatbotMessageRequest {
  message: string;
}

interface ChatbotMessageResponse {
  intent: string;
  reply: string;
  suggested_workouts: string[];
  tips: string[];
  created_at: string;
}

// Error Types
interface APIError {
  error: string;
}

interface ValidationErrors {
  errors: Record<string, string>;
}
````

## React API Service Example

```typescript
// services/api.ts
const API_BASE = "http://localhost:5000";

class APIService {
  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem("authToken");
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  }

  // Auth
  async register(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  // Profile
  async completeOnboarding(
    profileData: Partial<Profile>,
  ): Promise<ProfileResponse> {
    const response = await fetch(`${API_BASE}/api/profile/onboarding`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(profileData),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async getProfile(): Promise<ProfileResponse> {
    const response = await fetch(`${API_BASE}/api/profile/me`, {
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async updateProfile(updates: Partial<Profile>): Promise<ProfileResponse> {
    const response = await fetch(`${API_BASE}/api/profile/me`, {
      method: "PUT",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  // Calorie Tracking
  async getTodaysCalories(): Promise<CalorieDay> {
    const response = await fetch(`${API_BASE}/api/calories/today`, {
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async addFoodItem(
    foodName: string,
    calories: number,
  ): Promise<AddFoodResponse> {
    const response = await fetch(`${API_BASE}/api/calories/items`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ food_name: foodName, calories }),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async editFoodItem(
    itemId: string,
    foodName?: string,
    calories?: number,
  ): Promise<EditFoodResponse> {
    const response = await fetch(`${API_BASE}/api/calories/items/${itemId}`, {
      method: "PUT",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        ...(foodName !== undefined && { food_name: foodName }),
        ...(calories !== undefined && { calories }),
      }),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async deleteFoodItem(itemId: string): Promise<DeleteFoodResponse> {
    const response = await fetch(`${API_BASE}/api/calories/items/${itemId}`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async getCaloriesByDate(date: string): Promise<CalorieDay> {
    const response = await fetch(`${API_BASE}/api/calories?date=${date}`, {
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async getWeeklyProgress(): Promise<WeeklyProgressResponse> {
    const response = await fetch(`${API_BASE}/api/calories/weekly`, {
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  // Exercises
  async getMuscleGroups(): Promise<MuscleGroup[]> {
    const response = await fetch(`${API_BASE}/api/muscle-groups`);
    return response.json();
  }

  async getExercises(): Promise<Exercise[]> {
    const response = await fetch(`${API_BASE}/api/exercises`);
    return response.json();
  }

  async createCustomExercise(
    name: string,
    muscleGroupId: string,
  ): Promise<Exercise> {
    const response = await fetch(`${API_BASE}/api/exercises`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({
        name,
        muscle_group_id: muscleGroupId,
        user_id: this.getUserId(),
      }),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async addCustomExerciseToWorkout(
    workoutId: string,
    payload: {
      user_id: string;
      name: string;
      muscle_group_id: string;
      secondary_muscle_ids?: string[];
      equipment?: string;
      category?: string;
      notes?: string;
    },
  ): Promise<CustomExerciseEntryResponse> {
    const response = await fetch(
      `${API_BASE}/api/workouts/${workoutId}/entries/custom`,
      {
        method: "POST",
        headers: this.getAuthHeaders(),
        body: JSON.stringify(payload),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async getWeeklyWorkoutProgress(
    userId: string,
  ): Promise<WeeklyWorkoutProgressResponse> {
    const response = await fetch(
      `${API_BASE}/api/workouts/progress/weekly?user_id=${userId}`,
      {
        headers: this.getAuthHeaders(),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async getTodayWorkoutProgress(
    userId: string,
  ): Promise<TodayWorkoutProgressResponse> {
    const response = await fetch(
      `${API_BASE}/api/workouts/progress/today?user_id=${userId}`,
      {
        headers: this.getAuthHeaders(),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async getMonthlyWorkoutStats(
    userId: string,
  ): Promise<MonthlyWorkoutStatsResponse> {
    const response = await fetch(
      `${API_BASE}/api/workouts/progress/monthly?user_id=${userId}`,
      {
        headers: this.getAuthHeaders(),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async sendChatMessage(message: string): Promise<ChatbotMessageResponse> {
    const response = await fetch(`${API_BASE}/api/chatbot/message`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ message }),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  // Workouts
  async startWorkout(name?: string): Promise<Workout> {
    const response = await fetch(`${API_BASE}/api/workouts`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ name, user_id: this.getUserId() }),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async getWorkouts(): Promise<Workout[]> {
    const response = await fetch(`${API_BASE}/api/workouts`, {
      headers: this.getAuthHeaders(),
    });
    return response.json();
  }

  async getWorkout(workoutId: string): Promise<Workout> {
    const response = await fetch(`${API_BASE}/api/workouts/${workoutId}`, {
      headers: this.getAuthHeaders(),
    });
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async addExerciseEntry(
    workoutId: string,
    exerciseId: string,
    exerciseName: string,
  ) {
    const response = await fetch(
      `${API_BASE}/api/workouts/${workoutId}/entries`,
      {
        method: "POST",
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          exercise_id: exerciseId,
          exercise_name_snapshot: exerciseName,
        }),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async deleteEntry(workoutId: string, entryId: string) {
    const response = await fetch(
      `${API_BASE}/api/workouts/${workoutId}/entries/${entryId}`,
      {
        method: "DELETE",
        headers: this.getAuthHeaders(),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async addSet(
    workoutId: string,
    entryId: string,
    weight: number,
    reps: number,
  ) {
    const response = await fetch(
      `${API_BASE}/api/workouts/${workoutId}/entries/${entryId}/sets`,
      {
        method: "PUT",
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ weight_kg: weight, reps }),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async editSet(
    workoutId: string,
    entryId: string,
    setNumber: number,
    weight?: number,
    reps?: number,
  ) {
    const response = await fetch(
      `${API_BASE}/api/workouts/${workoutId}/entries/${entryId}/sets/${setNumber}`,
      {
        method: "PUT",
        headers: this.getAuthHeaders(),
        body: JSON.stringify({
          ...(weight !== undefined && { weight_kg: weight }),
          ...(reps !== undefined && { reps }),
        }),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async deleteSet(workoutId: string, entryId: string, setNumber: number) {
    const response = await fetch(
      `${API_BASE}/api/workouts/${workoutId}/entries/${entryId}/sets/${setNumber}`,
      {
        method: "DELETE",
        headers: this.getAuthHeaders(),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  async finishWorkout(workoutId: string): Promise<Workout> {
    const response = await fetch(
      `${API_BASE}/api/workouts/${workoutId}/finish`,
      {
        method: "PUT",
        headers: this.getAuthHeaders(),
      },
    );
    if (!response.ok) throw new Error(await response.text());
    return response.json();
  }

  // Helper
  private getUserId(): string | null {
    // Extract user_id from stored user data or JWT token
    const userData = localStorage.getItem("user");
    return userData ? JSON.parse(userData)._id : null;
  }
}

export const api = new APIService();
```

## React Context Example

```typescript
// contexts/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { api } from '../services/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  profile: Profile | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  completeOnboarding: (profileData: Partial<Profile>) => Promise<void>;
  updateProfile: (updates: Partial<Profile>) => Promise<void>;
  isAuthenticated: boolean;
  hasProfile: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);

  useEffect(() => {
    // Load from localStorage on mount
    const savedToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('user');

    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
      loadProfile();
    }
  }, []);

  const loadProfile = async () => {
    try {
      const { profile } = await api.getProfile();
      setProfile(profile);
    } catch (error) {
      // Profile doesn't exist yet - user needs onboarding
      console.log('No profile found');
    }
  };

  const register = async (email: string, password: string) => {
    const { user, token } = await api.register(email, password);
    setUser(user);
    setToken(token);
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(user));
  };

  const login = async (email: string, password: string) => {
    const { user, token } = await api.login(email, password);
    setUser(user);
    setToken(token);
    localStorage.setItem('authToken', token);
    localStorage.setItem('user', JSON.stringify(user));
    await loadProfile();
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setProfile(null);
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  };

  const completeOnboarding = async (profileData: Partial<Profile>) => {
    const { profile } = await api.completeOnboarding(profileData);
    setProfile(profile);
  };

  const updateProfile = async (updates: Partial<Profile>) => {
    const { profile } = await api.updateProfile(updates);
    setProfile(profile);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        profile,
        login,
        register,
        logout,
        completeOnboarding,
        updateProfile,
        isAuthenticated: !!token,
        hasProfile: !!profile
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

## Suggested Frontend Flow

### 1. Authentication Pages

- **Login Page**: Email/password form → `POST /api/auth/login` → Save token → Redirect
- **Register Page**: Email/password form → `POST /api/auth/register` → Save token → Redirect to onboarding

### 2. Onboarding Page

- Form with sex, age, height, weight, activity level, goal
- `POST /api/profile/onboarding` → Display calorie goal → Redirect to dashboard

### 3. Dashboard/Home Page

- Display current calorie goal from profile
- Display remaining calories for today
- Button to "Track Calories" → Navigate to `/calories`
- List recent workouts from `GET /api/workouts`
- Button to start new workout

### 4. Calorie Tracker Page

- On load: `GET /api/calories/today` to get current state
- Display prominently:
  - **Remaining Calories** (large display)
  - Goal calories
  - Consumed calories
- **Add Food Form**:
  - Input: Food name (text)
  - Input: Calories (number)
  - Button: "Add Food"
  - On submit: `POST /api/calories/items` → Update UI with response
  - Use `remaining_calories` from response (NEVER calculate locally)
- **Food List**:
  - Display each item with name, calories, and delete button
  - Delete button: `DELETE /api/calories/items/{item_id}` → Update UI
- **Loading & Error States**:
  - Show spinner while loading
  - Show error message if API fails
  - Validate inputs before submission

### 5. Workout Session Page (Active Workout)

- `POST /api/workouts` to start
- Display muscle groups from `GET /api/muscle-groups`
- Filter exercises by muscle group from `GET /api/exercises`
- Add exercise → `PUT /api/workouts/{id}/entries`
- Add sets → `PUT /api/workouts/{id}/entries/{entry_id}/sets`
- Edit sets → `PUT /api/workouts/{id}/entries/{entry_id}/sets/{set_number}`
- Delete sets → `DELETE /api/workouts/{id}/entries/{entry_id}/sets/{set_number}`
- Delete exercises → `DELETE /api/workouts/{id}/entries/{entry_id}`
- Finish workout → `PUT /api/workouts/{id}/finish`

### 6. Workout History Page

- List all workouts from `GET /api/workouts`
- Click workout → `GET /api/workouts/{id}` to view details
- Display duration, exercises, sets, total volume

### 7. Profile Settings Page

- Display current profile from `GET /api/profile/me`
- Edit form → `PUT /api/profile/me` with updates
- Show updated calorie goal after changes

## Error Handling

```typescript
async function handleAPICall<T>(apiCall: () => Promise<T>): Promise<T> {
  try {
    return await apiCall();
  } catch (error) {
    if (error instanceof Error) {
      const message = error.message;

      // Handle specific error cases
      if (message.includes("401")) {
        // Token expired - logout and redirect to login
        localStorage.removeItem("authToken");
        window.location.href = "/login";
      } else if (message.includes("404")) {
        // Resource not found
        throw new Error("Resource not found");
      } else if (message.includes("400")) {
        // Validation error - show to user
        throw new Error("Invalid input");
      }
    }
    throw error;
  }
}

// Usage
const workouts = await handleAPICall(() => api.getWorkouts());
```

## Complete Calorie Tracker Page Example

```typescript
// pages/CaloriesPage.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { CalorieDay, FoodItem } from '../types';

export const CaloriesPage: React.FC = () => {
  const [calorieData, setCalorieData] = useState<CalorieDay | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state for adding
  const [foodName, setFoodName] = useState('');
  const [calories, setCalories] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Form state for editing
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editFoodName, setEditFoodName] = useState('');
  const [editCalories, setEditCalories] = useState('');
  const [editSubmitting, setEditSubmitting] = useState(false);

  // Load today's calorie data on mount
  useEffect(() => {
    loadTodaysCalories();
  }, []);

  const loadTodaysCalories = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getTodaysCalories();
      setCalorieData(data);
    } catch (err) {
      setError('Failed to load calorie data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddFood = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!foodName.trim()) {
      setError('Food name is required');
      return;
    }

    const caloriesNum = parseInt(calories);
    if (isNaN(caloriesNum) || caloriesNum <= 0) {
      setError('Calories must be a positive number');
      return;
    }

    try {
      setSubmitting(true);
      setError(null);

      // Add food item and get updated data
      const response = await api.addFoodItem(foodName.trim(), caloriesNum);

      // CRITICAL: Use server-calculated remaining_calories
      // NEVER calculate this locally
      setCalorieData({
        date: response.date,
        goal_calories: response.goal_calories,
        consumed_calories: response.consumed_calories,
        remaining_calories: response.remaining_calories, // From server
        items: response.items
      });

      // Reset form
      setFoodName('');
      setCalories('');
    } catch (err) {
      setError('Failed to add food item');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditStart = (item: FoodItem) => {
    setEditingId(item.item_id);
    setEditFoodName(item.food_name);
    setEditCalories(item.calories.toString());
    setError(null);
  };

  const handleEditCancel = () => {
    setEditingId(null);
    setEditFoodName('');
    setEditCalories('');
  };

  const handleEditSave = async (itemId: string) => {
    // Validation
    const newFoodName = editFoodName.trim();
    if (!newFoodName) {
      setError('Food name cannot be empty');
      return;
    }

    const newCalories = parseInt(editCalories);
    if (isNaN(newCalories) || newCalories <= 0) {
      setError('Calories must be a positive number');
      return;
    }

    try {
      setEditSubmitting(true);
      setError(null);

      // Edit food item and get updated data
      const response = await api.editFoodItem(
        itemId,
        newFoodName,
        newCalories
      );

      // CRITICAL: Use server-recalculated remaining_calories
      setCalorieData({
        date: response.date,
        goal_calories: response.goal_calories,
        consumed_calories: response.consumed_calories,
        remaining_calories: response.remaining_calories, // Recalculated on server
        items: response.items
      });

      // Clear editing state
      setEditingId(null);
      setEditFoodName('');
      setEditCalories('');
    } catch (err) {
      setError('Failed to edit food item');
      console.error(err);
    } finally {
      setEditSubmitting(false);
    }
  };

  const handleDeleteFood = async (itemId: string) => {
    try {
      setError(null);

      // Delete item and get updated data
      const response = await api.deleteFoodItem(itemId);

      // CRITICAL: Use server-recalculated remaining_calories
      setCalorieData({
        date: response.date,
        goal_calories: response.goal_calories,
        consumed_calories: response.consumed_calories,
        remaining_calories: response.remaining_calories, // Recalculated on server
        items: response.items
      });
    } catch (err) {
      setError('Failed to delete food item');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="container">
        <div className="spinner">Loading...</div>
      </div>
    );
  }

  if (!calorieData) {
    return (
      <div className="container">
        <div className="error">
          Failed to load calorie data. Please complete onboarding first.
        </div>
      </div>
    );
  }

  return (
    <div className="calories-page">
      <h1>Track Calories</h1>

      {error && (
        <div className="error-banner">{error}</div>
      )}

      {/* Calorie Summary - Large Display */}
      <div className="calorie-summary">
        <div className="remaining-calories">
          <span className="label">Remaining</span>
          <span className="value">{calorieData.remaining_calories}</span>
          <span className="unit">calories</span>
        </div>

        <div className="calorie-breakdown">
          <div className="breakdown-item">
            <span className="label">Goal</span>
            <span className="value">{calorieData.goal_calories}</span>
          </div>
          <div className="breakdown-item">
            <span className="label">Consumed</span>
            <span className="value">{calorieData.consumed_calories}</span>
          </div>
        </div>
      </div>

      {/* Add Food Form */}
      <div className="add-food-section">
        <h2>Add Food</h2>
        <form onSubmit={handleAddFood}>
          <div className="form-group">
            <label htmlFor="foodName">Food Name</label>
            <input
              id="foodName"
              type="text"
              value={foodName}
              onChange={(e) => setFoodName(e.target.value)}
              placeholder="e.g., Chicken Breast"
              disabled={submitting}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="calories">Calories</label>
            <input
              id="calories"
              type="number"
              value={calories}
              onChange={(e) => setCalories(e.target.value)}
              placeholder="e.g., 250"
              min="1"
              disabled={submitting}
              required
            />
          </div>

          <button type="submit" disabled={submitting}>
            {submitting ? 'Adding...' : 'Add Food'}
          </button>
        </form>
      </div>

      {/* Food Items List */}
      <div className="food-list-section">
        <h2>Today's Foods</h2>

        {calorieData.items.length === 0 ? (
          <p className="empty-state">
            No food logged yet today. Add your first meal above!
          </p>
        ) : (
          <ul className="food-list">
            {calorieData.items.map((item) => (
              <li key={item.item_id} className="food-item">
                {editingId === item.item_id ? (
                  // Edit Mode
                  <div className="food-item-edit">
                    <div className="form-group">
                      <input
                        type="text"
                        value={editFoodName}
                        onChange={(e) => setEditFoodName(e.target.value)}
                        placeholder="Food name"
                        disabled={editSubmitting}
                      />
                    </div>
                    <div className="form-group">
                      <input
                        type="number"
                        value={editCalories}
                        onChange={(e) => setEditCalories(e.target.value)}
                        placeholder="Calories"
                        min="1"
                        disabled={editSubmitting}
                      />
                    </div>
                    <div className="button-group">
                      <button
                        className="save-btn"
                        onClick={() => handleEditSave(item.item_id)}
                        disabled={editSubmitting}
                      >
                        {editSubmitting ? 'Saving...' : 'Save'}
                      </button>
                      <button
                        className="cancel-btn"
                        onClick={handleEditCancel}
                        disabled={editSubmitting}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  // View Mode
                  <>
                    <div className="food-info">
                      <span className="food-name">{item.food_name}</span>
                      <span className="food-calories">{item.calories} cal</span>
                    </div>
                    <div className="button-group">
                      <button
                        className="edit-btn"
                        onClick={() => handleEditStart(item)}
                        aria-label={`Edit ${item.food_name}`}
                      >
                        Edit
                      </button>
                      <button
                        className="delete-btn"
                        onClick={() => handleDeleteFood(item.item_id)}
                        aria-label={`Delete ${item.food_name}`}
                      >
                        Delete
                      </button>
                    </div>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};
```

### Weekly Progress Chart Component

```typescript
// components/WeeklyProgressChart.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { WeeklyProgressDay } from '../types';

export const WeeklyProgressChart: React.FC = () => {
  const [weeklyData, setWeeklyData] = useState<WeeklyProgressDay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWeeklyProgress();
  }, []);

  const loadWeeklyProgress = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getWeeklyProgress();
      setWeeklyData(response.weekly_data);
    } catch (err) {
      setError('Failed to load weekly progress');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Calculate max calories for chart scaling
  const maxCalories = Math.max(
    ...weeklyData.map(day => Math.max(day.consumed_calories, day.goal_calories)),
    2000 // Minimum scale
  );

  // Get percentage for bar height
  const getBarHeight = (calories: number): number => {
    return (calories / maxCalories) * 100;
  };

  // Get color based on goal achievement
  const getBarColor = (day: WeeklyProgressDay): string => {
    if (!day.has_data) return '#e0e0e0'; // Gray for no data
    if (day.goal_met) return '#4caf50'; // Green for goal met
    if (day.consumed_calories > day.goal_calories) return '#ff9800'; // Orange for over goal
    return '#2196f3'; // Blue for under goal (but has data)
  };

  // Calculate streak of days meeting goal
  const getGoalMetStreak = (): number => {
    let streak = 0;
    for (let i = weeklyData.length - 1; i >= 0; i--) {
      if (weeklyData[i].goal_met) {
        streak++;
      } else {
        break;
      }
    }
    return streak;
  };

  if (loading) {
    return (
      <div className="weekly-progress-loading">
        <p>Loading weekly progress...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="weekly-progress-error">
        <p>{error}</p>
        <button onClick={loadWeeklyProgress}>Retry</button>
      </div>
    );
  }

  const goalStreak = getGoalMetStreak();
  const daysWithData = weeklyData.filter(d => d.has_data).length;
  const goalsMetCount = weeklyData.filter(d => d.goal_met).length;

  return (
    <div className="weekly-progress-chart">
      <h2>Weekly Progress</h2>

      {/* Stats Summary */}
      <div className="progress-stats">
        <div className="stat-card">
          <span className="stat-value">{goalsMetCount}</span>
          <span className="stat-label">Goals Met</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{goalStreak}</span>
          <span className="stat-label">Current Streak</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{daysWithData}</span>
          <span className="stat-label">Days Tracked</span>
        </div>
      </div>

      {/* Bar Chart */}
      <div className="chart-container">
        <div className="chart-bars">
          {weeklyData.map((day, index) => (
            <div key={index} className="bar-wrapper">
              <div className="bar-column">
                {/* Goal line indicator */}
                <div
                  className="goal-line"
                  style={{
                    bottom: `${getBarHeight(day.goal_calories)}%`
                  }}
                  title={`Goal: ${day.goal_calories} cal`}
                />

                {/* Consumed calories bar */}
                <div
                  className="bar"
                  style={{
                    height: `${getBarHeight(day.consumed_calories)}%`,
                    backgroundColor: getBarColor(day)
                  }}
                  title={`${day.consumed_calories} cal consumed`}
                >
                  {day.has_data && (
                    <span className="bar-value">
                      {day.consumed_calories}
                    </span>
                  )}
                </div>
              </div>

              {/* Day labels */}
              <div className="bar-label">
                <div className="day-name">{day.day_name.slice(0, 3)}</div>
                <div className="date">{day.date.slice(5)}</div>
              </div>

              {/* Goal met indicator */}
              {day.goal_met && (
                <div className="goal-badge" title="Goal met!">
                  ✓
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#4caf50' }}></span>
          <span>Goal Met</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#2196f3' }}></span>
          <span>Under Goal</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#ff9800' }}></span>
          <span>Over Goal</span>
        </div>
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#e0e0e0' }}></span>
          <span>No Data</span>
        </div>
      </div>
    </div>
  );
};
```

**Sample CSS for Weekly Progress Chart**:

```css
/* WeeklyProgressChart.css */
.weekly-progress-chart {
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.weekly-progress-chart h2 {
  margin: 0 0 1.5rem;
  font-size: 1.5rem;
  color: #333;
}

/* Stats Summary */
.progress-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #4caf50;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
}

/* Chart Container */
.chart-container {
  position: relative;
  padding: 1rem 0;
  margin-bottom: 1rem;
}

.chart-bars {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
  height: 250px;
  padding: 0 0.5rem;
}

.bar-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.bar-column {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.goal-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: #f44336;
  border-radius: 1px;
  z-index: 1;
  opacity: 0.5;
}

.bar {
  width: 100%;
  max-width: 60px;
  min-height: 4px;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s ease;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 0.25rem;
  position: relative;
}

.bar:hover {
  opacity: 0.8;
  transform: translateY(-2px);
}

.bar-value {
  font-size: 0.75rem;
  font-weight: bold;
  color: white;
}

.bar-label {
  margin-top: 0.5rem;
  text-align: center;
}

.day-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #333;
}

.date {
  font-size: 0.75rem;
  color: #666;
}

.goal-badge {
  position: absolute;
  top: -1.5rem;
  background: #4caf50;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.875rem;
}

/* Legend */
.chart-legend {
  display: flex;
  gap: 1rem;
  justify-content: center;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #666;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

/* Loading & Error States */
.weekly-progress-loading,
.weekly-progress-error {
  padding: 2rem;
  text-align: center;
}

.weekly-progress-error button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.weekly-progress-error button:hover {
  background: #1976d2;
}

/* Responsive Design */
@media (max-width: 768px) {
  .progress-stats {
    flex-direction: column;
  }

  .chart-bars {
    gap: 0.25rem;
  }

  .bar {
    max-width: 40px;
  }

  .day-name {
    font-size: 0.75rem;
  }

  .date {
    font-size: 0.625rem;
  }

  .chart-legend {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}
```

**Usage Example**:

```typescript
// pages/CaloriesPage.tsx or pages/DashboardPage.tsx
import { WeeklyProgressChart } from '../components/WeeklyProgressChart';

export const CaloriesPage: React.FC = () => {
  return (
    <div className="calories-page">
      {/* Weekly Progress Chart */}
      <WeeklyProgressChart />

      {/* Daily Calorie Tracking */}
      <div className="daily-tracking">
        {/* ... existing daily tracking UI ... */}
      </div>
    </div>
  );
};
```

### Wiring from Home Button

```typescript
// pages/HomePage.tsx
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { profile } = useAuth();

  return (
    <div className="home-page">
      <h1>Welcome to BodyBalance</h1>

      {profile && (
        <div className="calorie-widget">
          <h2>Daily Calorie Goal</h2>
          <p className="calorie-goal">{profile.calorie_goal} calories</p>
          <button
            className="track-calories-btn"
            onClick={() => navigate('/calories')}
          >
            Track Calories
          </button>
        </div>
      )}

      {/* Rest of home page */}
    </div>
  );
};

// App.tsx - Add route
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { CaloriesPage } from './pages/CaloriesPage';
import { HomePage } from './pages/HomePage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/calories" element={<CaloriesPage />} />
        {/* Other routes */}
      </Routes>
    </BrowserRouter>
  );
}
```

## Key Implementation Notes

1. **Token Management**: Store JWT in localStorage after login/register, include in all protected requests
2. **Profile Check**: After login, check if profile exists (404 = needs onboarding)
3. **Calorie Display**: Show `calorie_goal` from profile prominently in dashboard
4. **Calorie Tracking - CRITICAL**: ALWAYS use `remaining_calories` from server response - NEVER calculate locally. Server handles all calorie math to ensure accuracy.
5. **Calorie Updates**: When adding/deleting food items, immediately update UI with the returned `CalorieDay` object from the API
6. **Workout State**: Track active workout ID in React state for current session
7. **Set Numbering**: Backend automatically numbers sets (1, 2, 3...) and renumbers after deletions
8. **Exercise Names**: Backend includes `exercise_name` in entries for display
9. **Muscle Groups**: Fetch once and cache in state/context for exercise filtering
10. **Custom Exercises**: Use `user_id` to filter custom exercises per user
11. **Error States**: Handle 401 (logout), 404 (not found), 400 (validation) appropriately
12. **Loading States**: Show spinners during API calls for better UX

## Testing the Backend

The backend is fully tested and working. You can verify endpoints with:

```bash
# Start backend
cd c:\Users\jamie\Documents\bodybalance_be
python app.py

# Run comprehensive tests
python scripts/test_auth.py
python scripts/test_calories.py
python scripts/smoke_test.py
```

All 25 endpoints are tested and functioning correctly.

## Workout Progress Tracker Component

The workout progress tracker mirrors the calorie tracker design with both weekly metrics and monthly aggregate statistics.

### Complete React Component

```typescript
// components/WorkoutProgressTracker.tsx
import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import type {
  WorkoutProgressDay,
  WeeklyWorkoutProgressResponse,
  MonthlyWorkoutStatsResponse,
  MonthlyStat
} from '../types';

interface WorkoutProgressTrackerProps {
  userId: string;
}

export const WorkoutProgressTracker: React.FC<WorkoutProgressTrackerProps> = ({
  userId
}) => {
  const [todayData, setTodayData] = useState<WorkoutProgressDay | null>(null);
  const [monthlyStats, setMonthlyStats] = useState<MonthlyStat | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadWorkoutProgress();
  }, [userId]);

  const loadWorkoutProgress = async () => {
    try {
      setLoading(true);
      setError(null);

      const [todayResponse, monthlyResponse] = await Promise.all([
        api.getTodayWorkoutProgress(userId),
        api.getMonthlyWorkoutStats(userId)
      ]);

      setTodayData(todayResponse);
      setMonthlyStats(monthlyResponse.monthly_stats);
    } catch (err) {
      setError('Failed to load workout progress');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="workout-progress-loading">
        <p>Loading today's workout progress...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="workout-progress-error">
        <p>{error}</p>
        <button onClick={loadWorkoutProgress}>Retry</button>
      </div>
    );
  }

  return (
    <div className="workout-progress-tracker">
      <h2>Today's Workout</h2>

      {/* Monthly Statistics Grid */}
      {monthlyStats && (
        <div className="monthly-stats">
          <div className="stat-card">
            <span className="stat-label">Workouts This Month</span>
            <span className="stat-value">{monthlyStats.total_workouts}</span>
            <span className="stat-unit">sessions</span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Total Volume</span>
            <span className="stat-value">
              {(monthlyStats.total_weight / 1000).toFixed(1)}
            </span>
            <span className="stat-unit">tons</span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Unique Exercises</span>
            <span className="stat-value">{monthlyStats.unique_exercises}</span>
            <span className="stat-unit">exercises</span>
          </div>

          <div className="stat-card">
            <span className="stat-label">Muscle Groups</span>
            <span className="stat-value">{monthlyStats.unique_muscle_groups}</span>
            <span className="stat-unit">groups</span>
          </div>
        </div>
      )}

      {/* Most Trained Muscle Group */}
      {monthlyStats && monthlyStats.most_trained_muscle_group && (
        <div className="most-trained">
          <h3>Primary Focus</h3>
          <span className="muscle-badge">
            {monthlyStats.most_trained_muscle_group}
          </span>
        </div>
      )}

      {/* Today's Workout Stats */}
      {todayData && (
        <>
          {todayData.had_workout ? (
            <>
              <div className="today-summary">
                <h3>Today's Session</h3>
                <div className="summary-stats">
                  <div className="summary-item">
                    <span className="label">Workouts</span>
                    <span className="value">{todayData.workouts_completed}</span>
                  </div>
                  <div className="summary-item">
                    <span className="label">Sets</span>
                    <span className="value">{todayData.total_sets}</span>
                  </div>
                  <div className="summary-item">
                    <span className="label">Reps</span>
                    <span className="value">{todayData.total_reps}</span>
                  </div>
                  <div className="summary-item">
                    <span className="label">Volume (kg)</span>
                    <span className="value">
                      {todayData.total_weight.toFixed(1)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Exercises Done Today */}
              <div className="today-exercises">
                <h3>Exercises ({todayData.exercises_done})</h3>
                {todayData.muscle_groups.length > 0 && (
                  <div className="muscles-breakdown">
                    <span className="breakdown-label">Muscles Trained:</span>
                    <div className="muscle-tags">
                      {todayData.muscle_groups.map((muscle, idx) => (
                        <span key={idx} className="muscle-tag">
                          {muscle}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="workout-status complete">
                <span className="status-icon">✓</span>
                <span className="status-text">Great workout today!</span>
              </div>
            </>
          ) : (
            <div className="today-summary empty">
              <h3>Today's Workout</h3>
              <div className="no-workout-message">
                <p>No workout logged yet today.</p>
                <p>Start a new workout to track your progress!</p>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
```

### Complete CSS Styling

```css
/* WorkoutProgressTracker.css */

.workout-progress-tracker {
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.workout-progress-tracker h2 {
  margin: 0 0 1.5rem;
  font-size: 1.5rem;
  color: #333;
}

.workout-progress-tracker h3 {
  margin: 1.5rem 0 1rem;
  font-size: 1.125rem;
  color: #333;
}

/* Monthly Statistics Grid */
.monthly-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
  border-left: 4px solid #2196f3;
  text-align: center;
}

.stat-card:nth-child(2) {
  border-left-color: #4caf50;
}

.stat-card:nth-child(3) {
  border-left-color: #ff9800;
}

.stat-card:nth-child(4) {
  border-left-color: #e91e63;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #2196f3;
}

.stat-card:nth-child(2) .stat-value {
  color: #4caf50;
}

.stat-card:nth-child(3) .stat-value {
  color: #ff9800;
}

.stat-card:nth-child(4) .stat-value {
  color: #e91e63;
}

.stat-unit {
  font-size: 0.75rem;
  color: #999;
  margin-top: 0.25rem;
}

/* Most Trained Muscle Group */
.most-trained {
  margin: 1.5rem 0;
  padding: 1rem;
  background: #fafafa;
  border-radius: 8px;
  text-align: center;
}

.most-trained h3 {
  margin: 0 0 0.5rem;
  color: #666;
}

.muscle-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #e91e63;
  color: white;
  border-radius: 20px;
  font-weight: 600;
}

/* Today's Workout Summary */
.today-summary {
  margin: 1.5rem 0;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f5f5f5 0%, #fafafa 100%);
  border-radius: 8px;
  border-left: 4px solid #4caf50;
}

.today-summary.empty {
  border-left-color: #ccc;
}

.today-summary h3 {
  margin: 0 0 1rem;
  color: #333;
}

.summary-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 1rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
}

.summary-item .label {
  font-size: 0.75rem;
  color: #999;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.summary-item .value {
  font-size: 1.75rem;
  font-weight: bold;
  color: #2196f3;
}

.no-workout-message {
  padding: 1.5rem;
  text-align: center;
  color: #999;
}

.no-workout-message p {
  margin: 0.5rem 0;
  font-size: 0.95rem;
}

/* Today's Exercises */
.today-exercises {
  margin: 1.5rem 0;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 8px;
}

.today-exercises h3 {
  margin: 0 0 1rem;
}

.muscles-breakdown {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.breakdown-label {
  font-size: 0.875rem;
  color: #666;
  text-transform: uppercase;
  font-weight: 500;
}

.muscle-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.muscle-tag {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid #bbdefb;
}

/* Workout Status */
.workout-status {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 500;
}

.workout-status.complete {
  background: #c8e6c9;
  color: #2e7d32;
  border-left: 4px solid #4caf50;
}

.status-icon {
  font-size: 1.25rem;
  font-weight: bold;
}

/* Loading & Error States */
.workout-progress-loading,
.workout-progress-error {
  padding: 2rem;
  text-align: center;
  color: #666;
}

.workout-progress-error button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.workout-progress-error button:hover {
  background: #1976d2;
}

/* Responsive Design */
@media (max-width: 768px) {
  .workout-progress-tracker {
    padding: 1rem;
  }

  .monthly-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .summary-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .summary-item {
    padding: 0.75rem;
  }

  .summary-item .label {
    font-size: 0.7rem;
  }

  .summary-item .value {
    font-size: 1.5rem;
  }

  .muscles-breakdown {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .monthly-stats {
    grid-template-columns: 1fr;
  }

  .summary-stats {
    grid-template-columns: 1fr;
  }

  .today-summary {
    padding: 1rem;
  }
}
```

### Integration Example

```typescript
// pages/WorkoutPage.tsx
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { WorkoutProgressTracker } from '../components/WorkoutProgressTracker';
import { WorkoutSession } from '../components/WorkoutSession';

export const WorkoutPage: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'today' | 'session'>('today');

  if (!user) {
    return <div>Please log in</div>;
  }

  return (
    <div className="workout-page">
      <div className="tab-menu">
        <button
          className={`tab-button ${activeTab === 'today' ? 'active' : ''}`}
          onClick={() => setActiveTab('today')}
        >
          Today
        </button>
        <button
          className={`tab-button ${activeTab === 'session' ? 'active' : ''}`}
          onClick={() => setActiveTab('session')}
        >
          Active Workout
        </button>
      </div>

      {activeTab === 'today' && (
        <WorkoutProgressTracker userId={user._id} />
      )}

      {activeTab === 'session' && (
        <WorkoutSession userId={user._id} />
      )}
    </div>
  );
};
```

## Summary

The backend provides:

- ✅ 5 authentication & profile endpoints
- ✅ 5 calorie tracking endpoints (with server-side calculation + weekly progress)
- ✅ 13 workout & exercise endpoints
- ✅ 3 workout progress endpoints (today + weekly + monthly statistics)
- ✅ 1 fitness chatbot endpoint (protected, rule-based)
- ✅ JWT authentication with 7-day expiration
- ✅ Calorie goal calculations (Mifflin-St Jeor equation)
- ✅ Weekly progress tracking with goal achievement metrics
- ✅ Daily progress tracker (today's metrics only)
- ✅ Monthly workout statistics with volume, frequency, and muscle group analysis
- ✅ Complete workout tracking with sets/reps
- ✅ Custom exercise creation (flexible parameters)
- ✅ Single-call custom exercise creation + workout entry
- ✅ CORS enabled for localhost frontend

**Total: 27 fully tested endpoints**

Build your frontend with confidence that the backend is production-ready and fully tested!
