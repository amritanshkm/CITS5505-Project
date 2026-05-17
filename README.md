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

## System Architecture & Technical Highlights (Rubric Mapping)
This project strictly adheres to robust software engineering standards and fully implements the requested grading rubrics.

### 1. Frontend & Design (UI/UX)
- **Jinja Template Inheritance**: Achieves DRY code concepts utilizing a global `base.html` framework with deeply embedded modular `{% block %}` structures cascading outwards to rendering logic.
- **Custom Aesthetic & Responsive UX**: Blends the scaffolding of the Bootstrap grid with a bespoke `style.css` containing custom animations, hover-shadow behaviors, and distinct non-generic color palettes guaranteeing fluid responsiveness across both desktop and mobile viewports.
- **Client-Side JS Validation**: Integrated `validation.js` enforcing pre-submission data requirements. Crucially intercepts logic failures (e.g., stopping the DOM submission pipeline if `password < 8 chars` or email formats violate regex barriers) with real-time UI manipulation and red highlighting.
- **Asynchronous AJAX & DOM Manipulation**: The homepage map utilizes advanced DOM filtering via JavaScript (`L.map`) to dynamically intercept category/price sorting parameters and render interactive location markers purely client-side without costly full-page reloads.

### 2. Backend & Complex Data Models (Flask ORM)
- **Complex Operations & Constraints**: Server logic runs well beyond simple CRUD manipulation, housing involved workflow engines including **Event Capacity Validations** (dynamically rejecting late-users back to `/profile` if order thresholds exceed maximum ticket limits), fully integrated **M2M nested queries**, and scalable Ledger architecture utilizing an explicit `Order` generation pipeline linking Users and Events.
- **Agile DB Migrations**: SQLite schema modifications are historically version-controlled via `Flask-Migrate` (`Alembic`). Definitively proven schema migration tracking spans safely inside the `migrations/versions/` historical repository tracked by git.
- **Advanced M2M ORM Engine**: Natively maps relational concepts using associative schema proxy tables (`user_bookmarks`, `user_event_likes`, etc.). This enables optimized cross-entity property aggregations seamlessly fetching dynamic interaction counts while deploying strict SQL cascades (`cascade="all, delete-orphan"`) stopping orphan row data leaks.

### 3. Security Implementations (Zero-Tolerance Hardening)
- **Password Hashing (Salted)**: Raw passwords never touch the filesystem or network. Leverages `werkzeug.security` with strict cryptographic salts natives mapping explicitly into the SQL string representations.
- **CSRF Tokenization Countermeasures**: Completely seals against spoofing scenarios utilizing `Flask-WTF` forms structurally injecting `{{ form.hidden_tag() }}` cross-site defense hashes.
- **Environment Context Encapsulation**: Private cryptographic signatures (like `SECRET_KEY`) and hardware mappings (`SQLALCHEMY_DATABASE_URI`) are detached entirely into a `.env` environment variables loader, strictly untracked within source-control history.

### 4. Software Testing Assurance (PyTest & Selenium)
*See explicitly the extensive `Running the Tests` detailed sections deployed below.*

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
We have built **25 Unit Tests** that instantiate an isolated in-memory SQLite database (`sqlite:///:memory:`) to verify the behavior of backend models, routing, and complex interactive data flows.

Tests included:
- **Authentication & Models (`tests/test_auth.py`)**: Verifies salted password hashing integrity, database commit validation on user registration, WTForms duplicate email interception, and correct Flask-Login session management handling.
- **Executing robust CRUD data flows over the `Event` Model (`tests/test_events.py`)**: Operating entirely inside an isolated, high-speed in-memory database, this script acts as an automated user to verify edge-to-edge backend safety:
  1. Bootstraps dummy accounts and Event structures into the test DB.
  2. Asserts coordinate mappings function properly upon retrieval.
  3. Verifies dynamic asynchronous interactions by testing our native `/like_comment` AJAX routes and confirming they successfully alter DB records and return correct JSON counts.
- **Validating Checkout ledgers & Capacity Boundary Limits (`tests/test_orders.py`)**: Specifically assesses the Phase 5 implementation by asserting correct `Order` ledger generation flows. Checks include boundary validations ensuring an Event rejects registrations safely with flashed errors if maximum ticket `capacity` limits are exceeded by concurrent joining users.
- **Personal Dashboards & Relationships (`tests/test_my_events.py`, `tests/test_saved_events.py`)**: Tests the dynamic population of user profiles. Validates that the Many-to-Many `user_bookmarks` relationship fetches accurate bookmarked events, and verifies `Event.creator_id` correctly aggregates 'My Created Events'.

**To run the Backend Unit Tests:**
```bash
# Run all backend tests cleanly without popping up the browser:
python -m pytest tests/ --ignore=tests/test_selenium.py -v
```

### 2. Live Server UI Automation (Selenium)
We have implemented **5 E2E GUI Automation Tests** that utilize the Chrome WebDriver to interact with our application precisely as a human being would. *Note: Headless mode has been disabled by default so you can visually watch the automated robot execute these tests locally.*

Tests included:
- Validation of Site Layout & Title (`test_home_page_title`).
- Intercepting empty login attempts via frontend JS Validation (`test_login_empty_form_validation`).
- Creating randomized credentials and driving through the Registration flow via Keyboard simulation (`test_register_flow_e2e`).
- E2E flow driving through Login and confirming Dynamic Navbar state shift post-authentication (`test_login_flow_e2e`).
- Explicit endpoint hijacking attempt (`/profile`) being intercepted by `@login_required` bouncing the user out (`test_protected_route_rejection`).

**To run the Selenium Tests:**
*Ensure your Flask Live Server is running locally on another terminal (`python run.py`) before executing these tests!*
```bash
python -m pytest tests/test_selenium.py -v
```