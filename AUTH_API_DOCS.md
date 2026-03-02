# Authentication & Profile API Documentation

## Overview

Complete JWT-based authentication and profile management system with calorie goal calculations using the Mifflin-St Jeor equation.

## Features

- ✅ User registration with email & password
- ✅ Secure password hashing with bcrypt
- ✅ JWT token authentication (7-day expiration)
- ✅ Protected routes with Bearer token
- ✅ Profile creation (onboarding)
- ✅ BMR calculation (Mifflin-St Jeor equation)
- ✅ TDEE calculation with activity multipliers
- ✅ Calorie goal calculation with goal adjustments
- ✅ Profile updates with automatic recalculation
- ✅ Safety minimums: 1200 cal (female), 1500 cal (male)

## Technology Stack

- **Authentication**: JWT (pyjwt) with HS256 algorithm
- **Password Hashing**: bcrypt with auto-generated salts
- **Database**: MongoDB with unique indexes on users.email and profiles.user_id

## API Endpoints

### 1. Register User

**POST** `/api/auth/register`

Create a new user account.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Validation Rules:**

- Email: Must be valid format (regex validated)
- Password: Minimum 8 characters

**Response (201 Created):**

```json
{
  "user": {
    "_id": "string",
    "email": "user@example.com",
    "created_at": "2026-02-06T18:00:00.000Z",
    "updated_at": "2026-02-06T18:00:00.000Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**

- `400 Bad Request`: Invalid email format, password too short, or email already registered

---

### 2. Login User

**POST** `/api/auth/login`

Authenticate and receive JWT token.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response (200 OK):**

```json
{
  "user": {
    "_id": "string",
    "email": "user@example.com",
    "created_at": "2026-02-06T18:00:00.000Z",
    "updated_at": "2026-02-06T18:00:00.000Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses:**

- `400 Bad Request`: Missing email or password
- `401 Unauthorized`: Invalid email or password

---

### 3. Complete Onboarding (Create Profile)

**POST** `/api/profile/onboarding`

🔒 **Protected** - Requires Bearer token

Create user profile and calculate calorie goal.

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "sex": "male",
  "age": 30,
  "height_cm": 180,
  "weight_kg": 75,
  "activity_level": "moderate",
  "goal": "maintain_weight"
}
```

**Field Options:**

| Field            | Type    | Options                                                     | Validation   |
| ---------------- | ------- | ----------------------------------------------------------- | ------------ |
| `sex`            | string  | `"male"`, `"female"`                                        | Required     |
| `age`            | integer | -                                                           | 13-120 years |
| `height_cm`      | number  | -                                                           | 50-300 cm    |
| `weight_kg`      | number  | -                                                           | 20-500 kg    |
| `activity_level` | string  | `"sedentary"`, `"light"`, `"moderate"`, `"very"`, `"extra"` | Required     |
| `goal`           | string  | `"lose_weight"`, `"maintain_weight"`, `"gain_weight"`       | Required     |

**Activity Level Multipliers:**

- `sedentary`: 1.2 (little or no exercise)
- `light`: 1.375 (light exercise 1-3 days/week)
- `moderate`: 1.55 (moderate exercise 3-5 days/week)
- `very`: 1.725 (hard exercise 6-7 days/week)
- `extra`: 1.9 (very hard exercise, physical job)

**Goal Adjustments:**

- `lose_weight`: -500 calories/day (~0.5 kg/week)
- `maintain_weight`: 0 calories/day
- `gain_weight`: +500 calories/day (~0.5 kg/week)

**Response (200 OK):**

```json
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
    "bmr": 1730,
    "tdee": 2682,
    "calorie_goal": 2682,
    "created_at": "2026-02-06T18:00:00.000Z",
    "updated_at": "2026-02-06T18:00:00.000Z"
  },
  "calorie_goal": 2682
}
```

**Calculations Explained:**

1. **BMR (Basal Metabolic Rate)** - Mifflin-St Jeor equation:
   - Male: `BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) + 5`
   - Female: `BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age) - 161`

2. **TDEE (Total Daily Energy Expenditure)**:
   - `TDEE = BMR × activity_multiplier`

3. **Calorie Goal**:
   - `calorie_goal = TDEE + goal_adjustment`
   - Apply safety minimums: 1200 (female) or 1500 (male)

**Error Responses:**

- `400 Bad Request`: Validation errors (returns errors object with field-specific messages)
- `401 Unauthorized`: Missing, invalid, or expired token

---

### 4. Get Profile

**GET** `/api/profile/me`

🔒 **Protected** - Requires Bearer token

Retrieve current user's profile.

**Headers:**

```
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
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
    "bmr": 1730,
    "tdee": 2682,
    "calorie_goal": 2682,
    "created_at": "2026-02-06T18:00:00.000Z",
    "updated_at": "2026-02-06T18:00:00.000Z"
  },
  "calorie_goal": 2682
}
```

**Error Responses:**

- `401 Unauthorized`: Missing, invalid, or expired token
- `404 Not Found`: Profile not found (user hasn't completed onboarding)

---

### 5. Update Profile

**PUT** `/api/profile/me`

🔒 **Protected** - Requires Bearer token

Update profile with automatic recalculation of calorie goal. Supports partial updates.

**Headers:**

```
Authorization: Bearer <token>
```

**Request Body (all fields optional):**

```json
{
  "weight_kg": 70,
  "goal": "lose_weight"
}
```

Any subset of fields from onboarding can be updated. Unchanged fields retain current values.

**Response (200 OK):**

```json
{
  "profile": {
    "_id": "string",
    "user_id": "string",
    "sex": "male",
    "age": 30,
    "height_cm": 180.0,
    "weight_kg": 70.0,
    "activity_level": "moderate",
    "goal": "lose_weight",
    "bmr": 1675,
    "tdee": 2596,
    "calorie_goal": 2096,
    "created_at": "2026-02-06T18:00:00.000Z",
    "updated_at": "2026-02-06T18:05:00.000Z"
  },
  "calorie_goal": 2096
}
```

**Error Responses:**

- `400 Bad Request`: Validation errors for provided fields
- `401 Unauthorized`: Missing, invalid, or expired token
- `404 Not Found`: Profile not found (user hasn't completed onboarding)

---

## Authentication Flow

### Typical User Journey

1. **Registration**: `POST /api/auth/register`
   - User provides email & password
   - System creates user account
   - Returns JWT token

2. **Profile Creation**: `POST /api/profile/onboarding`
   - User provides physical stats & goals
   - System calculates BMR, TDEE, and calorie goal
   - Returns profile with calorie target

3. **Ongoing Usage**:
   - Login when needed: `POST /api/auth/login`
   - View profile: `GET /api/profile/me`
   - Update stats: `PUT /api/profile/me` (e.g., after weight loss)
   - Use calorie goal for workout/nutrition tracking

### Token Management

**Token Format:**

- Algorithm: HS256
- Expiration: 7 days from issuance
- Payload: `{ "user_id": "string", "exp": timestamp, "iat": timestamp }`

**Using Tokens:**

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Token Errors:**

- `Token has expired`: User must login again
- `Invalid token`: Malformed or tampered token
- `Authorization header is required`: No token provided
- `Invalid authorization header format`: Must be "Bearer <token>"

---

## Database Collections

### Users Collection

**Schema:**

```javascript
{
  _id: ObjectId,
  email: string (lowercase, unique index),
  password_hash: string (bcrypt),
  created_at: datetime,
  updated_at: datetime
}
```

**Indexes:**

- `email`: Unique index for fast lookups and duplicate prevention

### Profiles Collection

**Schema:**

```javascript
{
  _id: ObjectId,
  user_id: ObjectId (unique index),
  sex: string,
  age: integer,
  height_cm: number,
  weight_kg: number,
  activity_level: string,
  goal: string,
  bmr: integer,
  tdee: integer,
  calorie_goal: integer,
  created_at: datetime,
  updated_at: datetime
}
```

**Indexes:**

- `user_id`: Unique index for fast lookups and one-to-one relationship

---

## Example Usage

### cURL Examples

**Register:**

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass123"}'
```

**Login:**

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass123"}'
```

**Onboarding:**

```bash
curl -X POST http://localhost:5000/api/profile/onboarding \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "sex": "male",
    "age": 30,
    "height_cm": 180,
    "weight_kg": 75,
    "activity_level": "moderate",
    "goal": "maintain_weight"
  }'
```

**Get Profile:**

```bash
curl http://localhost:5000/api/profile/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Update Profile:**

```bash
curl -X PUT http://localhost:5000/api/profile/me \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"weight_kg": 72, "goal": "lose_weight"}'
```

### JavaScript/React Example

```javascript
// Register
const registerResponse = await fetch(
  "http://localhost:5000/api/auth/register",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email: "user@example.com",
      password: "securepass123",
    }),
  },
);
const { token, user } = await registerResponse.json();

// Save token (e.g., localStorage)
localStorage.setItem("authToken", token);

// Onboarding
const onboardingResponse = await fetch(
  "http://localhost:5000/api/profile/onboarding",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      sex: "male",
      age: 30,
      height_cm: 180,
      weight_kg: 75,
      activity_level: "moderate",
      goal: "maintain_weight",
    }),
  },
);
const { profile, calorie_goal } = await onboardingResponse.json();

// Get Profile
const profileResponse = await fetch("http://localhost:5000/api/profile/me", {
  headers: { Authorization: `Bearer ${token}` },
});
const { profile } = await profileResponse.json();
```

---

## Security Considerations

### Password Security

- Passwords hashed with bcrypt (salt rounds: default)
- Password hashes never returned in API responses
- Minimum password length: 8 characters

### Token Security

- JWT secret stored in environment variable (`JWT_SECRET`)
- Tokens expire after 7 days
- Tokens should be stored securely (httpOnly cookies recommended for production)
- Bearer token authentication on all protected routes

### Email Security

- Emails stored in lowercase for case-insensitive uniqueness
- Email format validated with regex
- Unique index prevents duplicate registrations

---

## Environment Variables

Required environment variables:

```bash
# MongoDB Connection
MONGO_URI=mongodb://localhost:27017/
DB_NAME=bodybalance

# JWT Authentication
JWT_SECRET=your-secret-key-change-in-production
```

**Important**: Change `JWT_SECRET` to a strong random value in production!

---

## Testing

Run the comprehensive test suite:

```bash
# Ensure Flask app is running
python app.py

# In another terminal, run tests
python scripts/test_auth.py
```

The test suite verifies:

- ✅ User registration
- ✅ User login
- ✅ Wrong password rejection
- ✅ Profile not found before onboarding
- ✅ Profile creation with calorie calculations
- ✅ Profile retrieval
- ✅ Profile updates with recalculation
- ✅ Protected route without token (401)
- ✅ Protected route with invalid token (401)

---

## Setup Instructions

1. **Install Dependencies:**

   ```bash
   pip install bcrypt pyjwt python-dotenv
   ```

2. **Create MongoDB Indexes:**

   ```bash
   python -c "import sys; sys.path.insert(0, '.'); from scripts.setup_indexes import setup_indexes; setup_indexes()"
   ```

3. **Start Flask App:**

   ```bash
   python app.py
   ```

4. **Test Endpoints:**
   ```bash
   python scripts/test_auth.py
   ```

---

## Integration with Workout API

The authentication system complements the existing workout API. To add authentication to workout endpoints:

1. Import the `require_auth` decorator from `routes.profile`
2. Apply decorator to protected workout routes
3. Access `request.user_id` in authenticated routes
4. Filter workouts by user_id for per-user isolation

Example:

```python
from routes.profile import require_auth

@workouts_bp.route('/', methods=['GET'])
@require_auth
def list_workouts():
    user_id = request.user_id  # Available after authentication
    workouts = db.workouts.find({"user_id": ObjectId(user_id)})
    # Return user's workouts only
```

---

## Calorie Calculation Reference

### BMR Formula (Mifflin-St Jeor)

**For Males:**

```
BMR = 10W + 6.25H - 5A + 5
```

**For Females:**

```
BMR = 10W + 6.25H - 5A - 161
```

Where:

- W = weight in kilograms
- H = height in centimeters
- A = age in years

### TDEE Calculation

```
TDEE = BMR × Activity Factor
```

Activity Factors:

- Sedentary (little/no exercise): 1.2
- Light (1-3 days/week): 1.375
- Moderate (3-5 days/week): 1.55
- Very Active (6-7 days/week): 1.725
- Extra Active (physical job + training): 1.9

### Calorie Goal Calculation

```
Calorie Goal = TDEE + Goal Adjustment
```

Goal Adjustments:

- Lose weight: -500 cal/day
- Maintain: 0 cal/day
- Gain weight: +500 cal/day

Safety Minimums:

- Female: max(calculated, 1200)
- Male: max(calculated, 1500)

---

## API Complete Endpoint Summary

### Public Endpoints (No Authentication)

- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Get token

### Protected Endpoints (Require Bearer Token)

- `POST /api/profile/onboarding` - Create profile
- `GET /api/profile/me` - Get profile
- `PUT /api/profile/me` - Update profile

### Workout Endpoints (Can be protected)

- `POST /api/workouts` - Start workout
- `GET /api/workouts` - List workouts
- `GET /api/workouts/<id>` - Get workout
- `PUT /api/workouts/<id>/entries` - Add exercise entry
- `DELETE /api/workouts/<id>/entries/<entry_id>` - Delete entry
- `PUT /api/workouts/<id>/entries/<entry_id>/sets` - Add set
- `PUT /api/workouts/<id>/entries/<entry_id>/sets/<set_number>` - Edit set
- `DELETE /api/workouts/<id>/entries/<entry_id>/sets/<set_number>` - Delete set
- `PUT /api/workouts/<id>/finish` - Finish workout

### Exercise Endpoints

- `GET /api/exercises` - List exercises
- `GET /api/exercises/<id>` - Get exercise
- `POST /api/exercises` - Create custom exercise
- `GET /api/muscle-groups` - List muscle groups

---

## Status Codes

- `200 OK` - Successful GET, PUT requests
- `201 Created` - Successful POST registration
- `400 Bad Request` - Validation errors, bad input
- `401 Unauthorized` - Missing/invalid/expired token, wrong credentials
- `404 Not Found` - Resource doesn't exist

---

## Support & Extensions

For questions or feature requests, refer to:

- Main README.md for workout API documentation
- This file for authentication system documentation
- Test scripts (scripts/test_auth.py) for usage examples
