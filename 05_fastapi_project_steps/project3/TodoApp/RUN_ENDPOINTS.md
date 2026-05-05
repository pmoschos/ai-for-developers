# Οδηγός Δοκιμής και Εκτέλεσης Endpoints (TodoApp)

Αυτός ο οδηγός περιγράφει τη λογική σειρά με την οποία πρέπει να δοκιμάσετε τα endpoints του **TodoApp** μέσω του Swagger UI (`http://127.0.0.1:8000/docs`), ώστε να κατανοήσετε πλήρως το flow της εφαρμογής (Authentication, Authorization, CRUD operations).

Περιλαμβάνει τα ακριβή δεδομένα (JSON payloads) που πρέπει να συμπληρώσετε σε κάθε βήμα.

---

## 🚀 Εκκίνηση Εφαρμογής
Βεβαιωθείτε ότι βρίσκεστε στο φάκελο `TodoApp` και τρέξτε τον server:
```bash
uvicorn main:app --reload
```
Ανοίξτε τον browser σας στο: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## ΒΗΜΑ 1: Εγγραφή Χρηστών (`/auth/`)
Τα default endpoints είναι "κλειδωμένα". Πρέπει πρώτα να δημιουργήσουμε λογαριασμούς.

1. Ανοίξτε το **`POST /auth/`** (Create User).
2. Πατήστε **Try it out**.
3. **Δημιουργία Απλού Χρήστη**: Γράψτε το παρακάτω JSON στο πεδίο Request body:
```json
{
  "username": "johndoe",
  "email": "john@test.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "mypassword123",
  "role": "user"
}
```
*Πατήστε Execute.*

4. **Δημιουργία Admin**: Προσθέστε έναν νέο χρήστη, βάζοντας `role: "admin"`:
```json
{
  "username": "admin_anna",
  "email": "anna@test.com",
  "first_name": "Anna",
  "last_name": "Smith",
  "password": "adminpassword123",
  "role": "admin"
}
```
*Πατήστε Execute.*

---

## ΒΗΜΑ 2: Σύνδεση (Login / Token)
Θα συνδεθούμε με τον *απλό χρήστη* για να λάβουμε το JWT Bearer Token.

1. Πηγαίνετε στο **`POST /auth/token`**. Πατήστε **Try it out**.
2. Συμπληρώστε τα πεδία της φόρμας (δεν είναι JSON, είναι `x-www-form-urlencoded`):
    *   **username**: `johndoe`
    *   **password**: `mypassword123`
    *   *(Αφήστε το `grant_type`, `scope`, `client_id`, `client_secret` κενά)*
3. Πατήστε Execute. Στο Response Body θα δείτε ένα `access_token`. 
4. **Login στο Swagger**: Ανεβείτε πάνω-πάνω στη σελίδα του Swagger, πατήστε το πράσινο κουμπί **Authorize 🔒**.
    * Εισάγετε τον κωδικό: `mypassword123`  (και το username)
    * Πατήστε **Authorize**. Πλέον, το Swagger θα περνάει το Token αυτόματα.

---

## ΒΗΜΑ 3: Διαχείριση Todos (`/todo`)
Είμαστε συνδεδεμένοι ως `johndoe`.

1. **`GET /` (Read All)**: Τρέξτε το. Θα επιστρέψει `[]`.
2. **`POST /todo` (Create Todo)**: Πατήστε Try it out και εισάγετε το JSON:
```json
{
  "title": "Διάβασμα Python",
  "description": "Μελέτη FastAPI, Pydantic, και SQLAlchemy",
  "priority": 5,
  "complete": false
}
```
*Πατήστε Execute. Και πάλι, δημιουργήστε και δεύτερο:*
```json
{
  "title": "Αγορά Supermarket",
  "description": "Γάλα, Καφές, Αυγά",
  "priority": 2,
  "complete": false
}
```

3. **`GET /` (Read All)**: Τρέξτε το ξανά. Τώρα βλέπετε και τα 2 Todos. Ας πούμε ότι το δεύτερο πήρε `id: 2`.
4. **`GET /todo/{todo_id}`**: Εισάγετε **todo_id**: `2`. Θα δείτε μόνο αυτό.
5. **`PUT /todo/{todo_id}`**: Εισάγετε **todo_id**: `2` και ενημερώστε το JSON σε completed:
```json
{
  "title": "Αγορά Supermarket",
  "description": "Γάλα, Καφές, Αυγά",
  "priority": 2,
  "complete": true
}
```
6. **`DELETE /todo/{todo_id}`**: Εισάγετε **todo_id**: `2` και πατήστε Execute.

---

## ΒΗΜΑ 4: Προφίλ Χρήστη (`/user/`)
Συνεχίζουμε ως `johndoe`.

1. **`GET /user/`**: Απλά τρέξτε το. Επιστρέφει όλο το record: `{"id": 1, "username": "johndoe", "email": "john@test.com" ...}`
2. **`PUT /user/password`**: Αλλαγή κωδικού. Εισάγετε το JSON:
```json
{
  "password": "mypassword123",
  "new_password": "supernewpassword"
}
```
*Μετά από αυτό, θα χρειαστεί να κάνετε Logout και Login ξανά με το `supernewpassword`!*

---

## ΒΗΜΑ 5: Δοκιμή Δικαιωμάτων Διαχειριστή (`/admin/`)
Αποσυνδεθείτε (κουμπί Authorize -> Logout) και συνδεθείτε ξανά μέσω του **`POST /auth/token`** ή του **Authorize 🔒**, χρησιμοποιώντας τα στοιχεία:
*   **username**: `admin_anna`
*   **password**: `adminpassword123`

1. Ως `admin_anna`, χρησιμοποιήστε το **`POST /todo`** και φτιάξτε ένα δικό σας Todo:
```json
{
  "title": "Admin Dashboard Review",
  "description": "Έλεγχος των backend services",
  "priority": 5,
  "complete": false
}
```
2. **`GET /admin/todo`**: Τρέξτε το! Επειδή είστε admin (role: "admin"), η βάση θα επιστρέψει:
    * Το `Διάβασμα Python` (του `johndoe`)
    * Το `Admin Dashboard Review` (της `admin_anna`)
3. **`DELETE /admin/todo/{todo_id}`**: Βρείτε το ID του "Διάβασμα Python" (π.χ. `id: 1`). Εισάγετε **todo_id**: `1`. Πατήστε Execute. Ο Admin μόλις διέγραψε επιτυχώς το Todo ενός άλλου χρήστη!
