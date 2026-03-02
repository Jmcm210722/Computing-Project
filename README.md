# BodyBalance - Workout API

This Flask backend implements a complete workout-tracking API using raw PyMongo (no ORM). It follows the data model and rules described in the requirements:

- Static collections: `muscle_groups`, `exercises` (seeded)
- Dynamic collection: `workouts` (created per user)

Document structure for `workouts` follows the provided schema. Key points:

- Exercises do not store sets or weight/reps — those are kept inside `entries[].sets`.
- Each user may have at most one `in_progress` workout.
- Sets are stored as objects inside `entries[].sets[]` with weight and reps together.

## Quick Start (Development)

1. Create a virtualenv and install deps:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

2. Run MongoDB locally or set `MONGO_URI` to your cluster.

3. Seed the database:

```bash
python scripts\seed_muscle_groups.py
python scripts\seed_exercises.py
```

4. Start the app:

```bash
set MONGO_URI=mongodb://localhost:27017
python app.py
```

The app will start on `http://localhost:5000`.

## API Endpoints

### Muscle Groups & Exercises (Read-Only)

#### GET `/api/muscle-groups`

Fetch all muscle groups sorted by order.

#### GET `/api/exercises`

Fetch all exercises, optionally filtered by muscle group.

- Query parameters:
  - `muscle_group_id` (optional)
  - `user_id` (optional): include the user's custom exercises along with seeded ones

#### GET `/api/exercises/<exercise_id>`

Fetch a single exercise by ID.

#### POST `/api/exercises`

Create a custom exercise for a user within a muscle group.

**Request:**
`{"user_id":"string","name":"string","primary_muscle_id":"string","secondary_muscle_ids":["string"],"equipment":"string","category":"string"}`

### Workouts (Write & Read)

#### POST `/api/workouts/start`

Create a new workout or resume an existing in-progress workout.

**Request:** `{"user_id": "string", "muscle_group_id": "string (opt)", "title": "string (opt)"}`

#### GET `/api/workouts/<workout_id>`

Fetch a specific workout by ID.

#### GET `/api/workouts`

List all workouts for a user.

- Query parameters: `user_id` (required), `status` (optional: "in_progress" or "completed")

#### POST `/api/workouts/<workout_id>/entries`

Add an exercise entry to a workout.

**Request:** `{"exercise_id": "string", "exercise_name_snapshot": "string", "notes": "string (opt)"}`

#### DELETE `/api/workouts/<workout_id>/entries/<entry_id>`

Delete an exercise entry from a workout (removes the entry and all its sets).

**Request:** No body required

#### POST `/api/workouts/<workout_id>/entries/<entry_id>/sets`

Add a set to an exercise entry.

**Request:** `{"reps": int, "weight": number (opt), "notes": "string (opt)"}`

#### PUT `/api/workouts/<workout_id>/entries/<entry_id>/sets/<set_number>`

Edit an existing set in an exercise entry.

**Request:** `{"reps": int (opt), "weight": number (opt), "notes": "string (opt)"}`

At least one field must be provided (reps, weight, or notes).

#### DELETE `/api/workouts/<workout_id>/entries/<entry_id>/sets/<set_number>`

Delete a set from an exercise entry.

Remaining sets are automatically renumbered (e.g., if you delete set 2, the old set 3 becomes set 2).

**Request:** No body required

#### POST `/api/workouts/<workout_id>/finish`

Mark a workout as completed.

**Request:** `{"user_id": "string"}`

## Example Workflow

```bash
# 1. Start a workout
curl -X POST http://localhost:5000/api/workouts/start \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user123","muscle_group_id":"mg_chest","title":"Chest Day"}'

# 2. Get all chest exercises
curl http://localhost:5000/api/exercises?muscle_group_id=mg_chest

# 3. Add an exercise entry
curl -X POST http://localhost:5000/api/workouts/$WORKOUT_ID/entries \
  -H "Content-Type: application/json" \
  -d '{"exercise_id":"ex_bench_press","exercise_name_snapshot":"Bench Press"}'

# 3b. Delete an exercise entry
curl -X DELETE http://localhost:5000/api/workouts/$WORKOUT_ID/entries/$ENTRY_ID

# 4. Add a set
curl -X POST http://localhost:5000/api/workouts/$WORKOUT_ID/entries/$ENTRY_ID/sets \
  -H "Content-Type: application/json" \
  -d '{"reps":8,"weight":185}'

# 4b. Edit a set (e.g., change reps from 8 to 10)
curl -X PUT http://localhost:5000/api/workouts/$WORKOUT_ID/entries/$ENTRY_ID/sets/1 \
  -H "Content-Type: application/json" \
  -d '{"reps":10}'

# 4c. Delete a set
curl -X DELETE http://localhost:5000/api/workouts/$WORKOUT_ID/entries/$ENTRY_ID/sets/1

# 5. Finish workout
curl -X POST http://localhost:5000/api/workouts/$WORKOUT_ID/finish \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user123"}'

# 6. Fetch completed workouts
curl "http://localhost:5000/api/workouts?user_id=user123&status=completed"
```

## Testing

```bash
python scripts\smoke_test.py
```

## Database

Default: `mongodb://localhost:27017` / `bodybalance` database

Environment variables:

- `MONGO_URI`: MongoDB connection string
- `DB_NAME`: Database name
