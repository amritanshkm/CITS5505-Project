# Database Models & Relational Schemas

This document defines the exact conceptual mappings that our SQLite `SQLAlchemy` ORM will adopt. It illustrates exactly how complex relationships are tied together.

## ORM Entities overview

### 1. `User` Model
Stores heavily encrypted and strictly sanitized user registration data.
* `id`: Integer, Primary Key (Auto-incrementing)
* `nickname`: String(64), Unique, Indexed
* `email`: String(120), Unique, Indexed
* `password_hash`: String(128) - Must be salted via werkzeug.
* `join_date`: DateTime, Default=UTC_Now.
* `avatar`: LargeBinary (Nullable) - Stores user profile picture up to 2MB.

### 2. `Event` Model
Represents the actual application events tied heavily to location/GIS approximations and commerce states.
* `id`: Integer, Primary Key
* `title`: String(140), Indexed
* `description`: Text
* `category`: String(50)
* `price_type`: String(20) [e.g. 'free', 'paid']
* `price_label`: String(50) [e.g. '$50.00', 'Free']
* `date`: String(30)
* `time`: String(30)
* `location`: Text
* `lat`: Float
* `lng`: Float
* `capacity`: Integer (Nullable). Allows the creator to specify a maximum number of participants. The system automatically restricts `join_event` and `payment` endpoints, disabling the UI and denying transactions when `event.orders.count() >= capacity`.
* `creator_id`: Integer, Foreign Key (`user.id`)

### 3. `Announcement` Model
Stores broadcast updates pushed independently by the event creator over time.
* `id`: Integer, Primary Key
* `content`: Text
* `timestamp`: DateTime, Default=UTC_Now, Indexed (Used for reverse chronologies)
* `event_id`: Integer, Foreign Key (`event.id`)

### 4. `Comment` Model
Hosts user discussions linked exclusively to a single event environment. 
* `id`: Integer, Primary Key
* `content`: Text
* `timestamp`: DateTime, Default=UTC_Now
* `likes`: Integer, Default=0
* `user_id`: Integer, Foreign Key (`user.id`)
* `event_id`: Integer, Foreign Key (`event.id`)

### 5. `Order` Model (Tickets/Ledger)
Acts as the immutable ledger simulating financial checkouts or free claim ticket generation.
* `order_id`: Integer, Primary Key 
* `timestamp`: DateTime, Default=UTC_Now
* `status`: String(20) [e.g. "Paid", "Free Registration", "Refunded"]
* `total`: String(20) [Snapshots the `Event.price_label` frozen in time]
* `user_id`: Integer, Foreign Key (`user.id`)
* `event_id`: Integer, Foreign Key (`event.id`)

---

## Relationship Mappings 

These ORM mapping strategies define the complex interconnectivity across the app logic ensuring cascade deletes and joins work cleanly.

### One-to-Many Relationships (1:N)
* **User 1 : N Events:** A single creator (`User`) can host infinite events. Handled via `Event.creator_id`.
* **User 1 : N Comments:** A user can leave practically infinite comments across boards. Handled via `Comment.user_id`.
* **User 1 : N Orders:** A user maintains a history of order ledgers. Handled via `Order.user_id`.
* **Event 1 : N Comments:** The discussion interface hosts hundreds of comments. Deleting an Event must Cascade delete all linked comments.
* **Event 1 : N Announcements:** The live update engine.
* **Event 1 : N Orders:** Represents attendees holding tickets to an occurrence. Essential for capacity capping logic (`event.orders.count() >= event.capacity`).

### Many-to-Many Relationships (N:N)
Implementing bookmarks and robust "like" engines requires dedicated associative secondary tables holding no intrinsic models (just mapping unique interactions dynamically).

#### 1. Bookmarking / Saved Collections
* **`user_bookmarks` (Associative Table)**
  * `user_id`: Foreign Key (`user.id`)
  * `event_id`: Foreign Key (`event.id`)
  * Allows `current_user.bookmarked_events` to retrieve collections for the Profile tab.

#### 2. Event Likes Tracking
* **`user_event_likes` (Associative Table)**
  * `user_id`: Foreign Key (`user.id`)
  * `event_id`: Foreign Key (`event.id`)
  * Ensures a user can only "Like" an event once, preventing inflated metric spamming.

#### 3. Comment Likes Tracking
* **`user_comment_likes` (Associative Table)**
  * `user_id`: Foreign Key (`user.id`)
  * `comment_id`: Foreign Key (`comment.id`)
  * Links a user to specific comment upvotes securely, updating the `Comment.likes` counter accurately.
