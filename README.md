# Event Finder + Sharing

## Description
This is the group project for CITS5505: Agile Web Development.
The application is an **Event Finder & Sharing Platform** that allows users to create events, view them on a map/list, and join or share events with others. It provides a reactive frontend built with Bootstrap and a robust backend powered by Flask and SQLite.

## Team Members

| UWA ID | Name | GitHub Username |
| :--- | :--- | :--- |
| 24350545 | Neha Pathare | [@nehap523](https://github.com/nehap523) |
| 24473572 | Sainath Reddy Mogullanolla | [@sainath282001](https://github.com/sainath282001) |
| 24703293 | Amritansh Kaur Mamotra | [@amritanshkm](https://github.com/amritanshkm) |
| 24290498 | Nyx Chen | [@hot-tofu-curd](https://github.com/hot-tofu-curd) |

## How to Launch the Application

1. **Set Up a Virtual Environment**:
   It is highly recommended to run this project inside a Python virtual environment.
   ```bash
   python -m venv venv
   ```
   Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

2. **Install Dependencies**:
   Ensure you have activated your virtual environment, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Create a `.env` file in the root directory (next to `run.py`) and insert the following local configurations:
   ```env
   SECRET_KEY=dev-secret-key-for-local-testing
   DATABASE_URL=sqlite:///app.db
   ```
   *(Note: NEVER commit real production secrets to GitHub. `.env` is deliberately ignored by git.)*

4. **Initialize the Database**:
   Establish the local SQLite database schema by running the Flask-Migrate upgrade command:
   ```bash
   flask db upgrade
   ```
   *(This step strictly expects `DATABASE_URL` and `app/models.py` structural relations to build the initial `app.db` local instance.)*

5. **Run the Application**:
   Execute the `run.py` file to start the Flask development server:
   ```bash
   python run.py
   ```
   The application will be accessible at `http://127.0.0.1:5000/`.

## Running the Tests

To adhere to robust software engineering standards and the project rubric, we have established a comprehensive test suite covering both Backend Logic and User Interface Automation. Our tests are orchestrated using `pytest`.

### 1. Backend Unit Tests
We have built **5 Unit Tests** that instantiate an isolated in-memory SQLite database (`sqlite:///:memory:`) to verify the behavior of backend models and routing.

Tests included:
- Verifying the mathematical integrity of the salted password hashing function (`test_password_hashing`).
- Verifying successful Commit to db on User Registration (`test_register_commits_to_db`).
- Ensuring `WTForms` correctly intercepts duplicate email registrations via `ValidationError` (`test_register_duplicate_email_fails`).
- Handling Flask-Login session management correctly upon login (`test_login_success_handles_session`).
- Correct rejection of invalid login credentials (`test_login_failure_bad_password`).
- **Executing robust CRUD data flows over the `Event` Model (`tests/test_events.py`)**: Operating entirely inside an isolated, high-speed in-memory database, this script acts as an automated user to verify edge-to-edge backend safety:
  1. **Create Account**: Bootstraps a dummy User account robustly into the test DB.
  2. **Create Event Data**: Simulates filling out a "PyTest Conference" activity payload, inserts it via ORM, and intercepts the DB yield.
  3. **Verification**: Asserts coordinate mappings function properly upon retrieval.
  4. **Update DB**: Manually alters the event title, fires a `commit()`, and verifies the DB snapshot changed correctly.
  5. **Simulate M2M Interactions**: Attaches Comments, Announcements, and Bookmarks to simulate Phase 4 N:N traffic.
  6. **Wipe State**: Invokes `db.session.delete()` to safely demolish all related assets via SQL cascade.
- **Validating Checkout ledgers & Capacity Boundary Limits (`tests/test_orders.py`)**: Specifically assesses the Phase 5 implementation by asserting correct `Order` ledger generation flows. Checks include boundary validations ensuring an Event rejects registrations safely with flashed errors if maximum ticket `capacity` limits are exceeded by concurrent joining users.

**To run the Unit Tests:**
```bash
python -m pytest tests/test_auth.py
python -m pytest tests/test_events.py
# Or to run the entire suite at once: python -m pytest tests/
```

### 2. Live Server UI Automation (Selenium)
We have implemented **5 E2E GUI Automation Tests** that utilize the Headless Chrome WebDriver to interact with our application precisely as a human being would.

Tests included:
- Validation of Site Layout & Title (`test_home_page_title`).
- Intercepting empty login attempts via frontend JS Validation (`test_login_empty_form_validation`).
- Creating randomized credentials and driving through the Registration flow via Keyboard simulation (`test_register_flow_e2e`).
- E2E flow driving through Login and confirming Dynamic Navbar state shift post-authentication (`test_login_flow_e2e`).
- Explicit endpoint hijacking attempt (`/profile`) being intercepted by `@login_required` bouncing the user out (`test_protected_route_rejection`).

**To run the Selenium Tests:**
*Ensure your Flask Live Server is running locally on port 5000 before executing these tests.*
```bash
python -m pytest tests/test_selenium.py
```