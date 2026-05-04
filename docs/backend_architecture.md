# Backend Architecture Diagram & Data Flow

This document details the backend technological stack, data flow pipeline, and crucial security implementations that will support the application's robust logic, bridging the gap from simple frontend mocking to fully operational Server-Side Rendering capabilities.

## 1. Technical Stack (Backend)

* **Core Framework:** Python Flask
* **Authentication:** Flask-Login (session management capability for logged-in states)
* **Form Protection & Validation:** Flask-WTF + WTForms
* **Data Storage:** SQLite
* **Database ORM:** Flask-SQLAlchemy
* **Database Patching / Version Control:** Flask-Migrate (alembic)
* **Environment variables:** `python-dotenv` for local `.env` secure parameter injections.

---

## 2. Security Infrastructure (Zero Tolerance Rules)

### Password & Credential Hashing
We definitively ban the storage of any plain-text passwords. 
* Implemented via `werkzeug.security` utilizing **Salted Hashes** (`generate_password_hash`, `check_password_hash`).
* This secures our db even if SQLite files are externally compromised.

### CSRF Protection
* The injection of Cross-Site Request Forgery is mitigated entirely using `Flask-WTF`.
* Whenever a POST request is formed (Logins, Event Creation, Checking Out, Comments), `{{ form.hidden_tag() }}` will render a session-specific CSRF secure token strictly validated by the Flask routing logic. 

### Environment Vault (.env)
* `FLASK_APP` and crucial encryption keys (like `SECRET_KEY = os.environ.get('SECRET_KEY')`) will be strictly isolated into a `.env` file.
* `.env` is explicitly documented into `.gitignore` and omitted from GitHub history.

---

## 3. Backend Data Flow Lifecycle

A standard transaction (e.g., Joining an event / Making a payment) follows this strict pipeline:

1. **Client Action:** User presses 'Pay Now'.
2. **Frontend Interception:** Vanilla JS performs client-side Regex validation. Prevents faulty payload.
3. **Route Entry:** The payload hits `@bp.route('/event/payment', methods=['POST'])`.
4. **Security Filter:** `form.validate_on_submit()` invokes WTF to check for CSRF, datatype consistency, and hidden string length. 
5. **Authorization Verification (Role Validation):** Backend asserts the `current_user.is_authenticated`. It verifies if the current acting user meets role criteria (e.g., checks `event.creator_id == current_user.id` when deleting an event).
6. **Complex Data Query:** SQLAlchemy runs non-trivial evaluations (e.g. comparing `Order.query.filter_by(event_id).count() < event.capacity`).
7. **ORM Database Push:** `db.session.add()` & `db.session.commit()` solidifies the transaction securely.
8. **Client Response:** User is met with a UI update via `flash()` and redirected safely.

---

## 4. Role Mapping & Form Validation Strategy (Anti-Bypass Checks)

**Roles:**
* **Guest:** Read-only access to `/index` and `/event_details`.
* **Authenticated User:** Can leave comments, book tickets, like events.
* **Event Creator:** Derived purely through relationship mappings (`Event.creator_id == User.id`). Bypasses `is_creator` conditionals triggering permission sets to delete comments within their event, or delete the event itself.

**Absolute Backend Validation (Defeating JS-Bypass):**
* **The Vulnerability:** Client-side JavaScript validation (e.g., HTML5 `required`, regex JS checking in `payment.html`) is trivial. Malicious users can easily bypass the browser UI using cURL, Postman, or intercepting proxies (Burp Suite) to submit arbitrary POST data.
* **The Shield:** We **do not trust frontend data whatsoever**. Every single POST request must pass through backend Flask-WTF validation.
  * If a user skips JS validation, `PaymentForm().validate_on_submit()` on the backend will instantly reject the payload if CVV isn't exactly 3 digits, or if the string length is unsafe.
  * We also perform semantic validations (e.g., verifying `current_user` actually possesses enough funds, or verifying the ticket `order.count < event.capacity` strictly on the backend before running `db.session.commit()`).
* Registration firmly checks the database for duplication (Throws "Username taken") ensuring unique constraints at the database level rather than just the UI level.
