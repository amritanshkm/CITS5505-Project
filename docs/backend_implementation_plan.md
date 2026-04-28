# Backend Implementation Roadmap (Phased Approach)

To ensure stability and logical progression, we will transition our current mock frontend into a fully operational Flask/SQLAlchemy backend through these specific, isolated phases. **No step will be skipped to "rush" to the finish line.**

---

### Phase 1: Environment & Schema Initialization (Foundation)
* **Goal**: Establish the base database without writing application logic.
* **Tasks**:
  1. Set up `.env` for `SECRET_KEY` and `SQLALCHEMY_DATABASE_URI` (SQLite).
  2. Implement `app.models` translating our `database_models.md` exactly into SQLAlchemy ORM structure.
  3. Wire up `SQLAlchemy` and `Flask-Migrate` within `app/__init__.py`.
  4. Execute `flask db init`, `flask db migrate`, and `flask db upgrade` to stamp the initial database layout into the repo history.

### Phase 2: User Authentication Engine
* **Goal**: Replace the `MOCK_USER` constant with actual login/registration.
* **Tasks**:
  1. Wire up `Flask-Login` standard configurations (e.g. `login_manager.user_loader`).
  2. Refactor `routes.py` -> `/register` and `/login` to use `User.query` and `generate_password_hash` / `check_password_hash`.
  3. Implement the `@login_required` decorator globally on sensitive pages (like Profile).

### Phase 3: Core Event Management (CRUD)
* **Goal**: Enable actual creation, display, editing, and deletion of events.
* **Tasks**:
  1. **Create**: Route `/create_event` properly inserts an `Event` tied to `current_user.id`.
  2. **Read**: Route `/` and `/event/<id>` fetch events systematically from the DB instead of `EVENTS = []`.
  3. **Update/Delete**: Secure `/event/<id>/edit` enforcing `current_user.id == event.creator_id`.
  4. Ensure images or map coordinates correctly persist into the SQLite database.

### Phase 4: Interactive Discussion & Operations
* **Goal**: Bring life to the comment section, announcements, and N:N relationships.
* **Tasks**:
  1. Add Comment creation and scoped deletion.
  2. Add Announcement persistence.
  3. Un-mock the Like and Bookmark buttons: wire them up to internal endpoints (like `/api/event/<id>/like`) which modify the `user_event_likes` associative model. This prevents the fake JS counter from being used.

### Phase 5: Payment Validation & Order Generation
* **Goal**: Formalize the Checkout workflow and "My Profile" integrations.
* **Tasks**:
  1. Route `/event/<id>/payment` will strictly utilize `PaymentForm.validate_on_submit()` for backend validation against payload manipulation.
  2. Upon success, an `Order` model will be committed.
  3. `/profile` will dynamically pull `current_user.orders` to recreate the tickets instead of utilizing `MOCK_ORDERS`.

### Phase 6: Automated Quality Assurance (Required Testing)
* **Goal**: Fulfill the stringent unit testing and UI testing requirements.
* **Tasks**:
  1. **Unit Testing (`pytest` / `unittest`)**: Create >= 5 testing functions verifying Password Hashing, User Registration rejection for duplicates, and Capacity calculations.
  2. **Automated Selenium Tests**: Write 5 scripts testing full User Flows on the browser (e.g., Robot clicks Registration, types User, clicks Submit, verifies Redirection to `/login`).
