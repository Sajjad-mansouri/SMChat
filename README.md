# SMChat

SMChat is a Django-based chat application inspired by messaging platforms such as Telegram. It provides account management, direct conversations, groups, channels, conversation membership management, and WebSocket-based message handling.

The project uses Django REST Framework for its API and Django Channels for WebSocket communication. It includes JWT authentication for API requests and a custom JWT middleware for WebSocket connections.

**Project status:** Local development  
**Database:** SQLite  
**Frontend:** HTML, CSS, and vanilla JavaScript  
**Automated tests:** Not implemented

## Features

### Account Management

- Custom Django user model with email as the authentication identifier.
- Username uniqueness for non-empty usernames.
- User profile information, including profile image, birthday, and bio.
- User registration with email activation.
- Login and logout-related configuration.
- Password reset and password confirmation workflows.
- Account information page and account deletion endpoint.
- Profile updates through the REST API.

### Conversations

The application defines three conversation types:

- **Direct conversations:** Conversations between individual users.
- **Groups:** Group conversations with membership and role information.
- **Channels:** Channel conversations with a creator and membership records.

Conversation models support:

- Names and descriptions.
- Public and private visibility.
- Profile images.
- Active and inactive status.
- Join-request settings.
- Creation and modification timestamps.

### Membership Management

The membership model supports:

- Owner, admin, and member roles.
- Membership acceptance status.
- Membership creation timestamps.
- A uniqueness constraint preventing duplicate membership records for the same user and conversation.

The API includes endpoints for adding members, updating membership records, and removing memberships.

### Messaging

The message model supports:

- Text messages.
- File attachments.
- Image attachments.
- Replies to existing messages.
- Message creation and modification timestamps.
- Message-to-user read tracking through a separate model.

The WebSocket consumer creates message records in the database and broadcasts messages to connected clients in the corresponding channel group.

### Real-Time Communication

SMChat uses Django Channels and an ASGI application to handle WebSocket connections.

The WebSocket consumer includes:

- Message broadcasting to a conversation's channel group.
- Message creation through WebSocket events.
- Reply information in outgoing messages.
- File upload handling using binary WebSocket frames.
- Upload progress notifications.
- Upload cancellation handling.
- A 50 MB size threshold that determines how temporary upload data is buffered.

The configured channel layer uses Django Channels' in-memory channel layer.

### User Search

The authenticated search endpoint supports:

- Searching users by username.
- Searching public groups and channels by name.
- Returning user and conversation search results.
- Excluding the current user from user search results.

### Blocking

The application includes a block-list model and API functionality for creating and removing block-list entries.

The WebSocket consumer also checks block-list records before allowing messages in direct conversations.

### Authentication and Authorization

The project includes:

- Django authentication for the web interface.
- JWT authentication for REST API requests.
- JWT token generation, refresh, and verification endpoints.
- Custom JWT authentication middleware for WebSocket connections.
- Object-level permission classes for membership, conversation ownership, membership removal, and accepted membership status.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application programming language |
| Django 5.2 | Web framework and account management |
| Django REST Framework | REST API |
| Django REST Framework Simple JWT | JWT authentication |
| Django Channels | WebSocket communication |
| Daphne | ASGI server |
| SQLite | Database |
| HTML | Page structure |
| CSS | Page styling |
| Vanilla JavaScript | Frontend behavior |
| Pillow | Image-processing dependency |

The exact Python version and operating system used for development are not specified in the available project information.

## Project Structure

```text
SMChat/
├── account/
│   ├── templates/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── jwt_auth_middleware.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── api/
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── chat/
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── consumers.py
│   ├── models.py
│   ├── routing.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── config/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── media/
├── static/
├── manage.py
└── requirements.txt
```

The tree reflects the structure provided for the project. Additional frontend files or directories may exist but have not been included in the supplied structure.

## Requirements

- Python
- The Python packages listed in `requirements.txt`
- SQLite
- A terminal for running Django management commands

## Installation and Setup

### 1. Clone the repository

Clone the SMChat repository and move into the project directory.

```bash
git clone <repository-url>
cd SMChat
```

Replace `<repository-url>` with the actual repository URL. A repository URL was not provided.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate the virtual environment.

**Linux or macOS:**

```bash
source venv/bin/activate
```

**Windows:**

```powershell
venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

The project uses `python-decouple` to read settings from environment configuration.

The supplied settings require the following values:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Django debug setting |
| `ALLOWED_HOSTS` | Allowed host names, parsed as a comma-separated list |
| `TIME_ZONE` | Django time zone |
| `EMAIL_BACKEND` | Email backend configuration |
| `DATABASAE_ENGINE` | Database engine setting |
| `DATABASAE_NAME` | Database name or path |
| `DATABASAE_USER` | Database user |
| `DATABASAE_PASSWORD` | Database password |
| `DATABASAE_HOST` | Database host |
| `DATABASAE_PORT` | Database port |

**Important:** The database variable names above intentionally match the supplied `settings.py`, including the spelling `DATABASAE_*`. The current settings do not use the usual `DATABASE_*` spelling.

SQLite is the database identified for this project, but the actual values of the database environment variables were not provided. Configure them to match the current settings and your local SQLite setup. Do not assume that a standard SQLite configuration will work without checking the required variables.

The precise email configuration, allowed-host values, secret-key value, and time zone must also be supplied by your local environment.

Do not commit actual secret keys, passwords, or other private environment values to version control.

### 5. Apply database migrations

Run:

```bash
python manage.py migrate
```

The project defines custom user, profile, conversation, membership, message, read-tracking, and block-list models. Apply the migrations present in the repository to initialize the database.

### 6. Create an administrator account

If you need access to the Django administration interface, run:

```bash
python manage.py createsuperuser
```

The custom user model uses email as `USERNAME_FIELD` and requires a username in addition to the other required account fields.

### 7. Start the application

The supplied development server command uses Daphne:

```bash
daphne -b 127.0.0.1 -p 8000 config.asgi:application
```

This starts the ASGI application on `127.0.0.1`, port `8000`.

Open the application at:

```text
http://127.0.0.1:8000/
```

The main chat page uses the `chat/main.html` template and requires login.

**Setup note:** The commands above reflect the supplied project configuration. Successful startup also depends on correct environment variables, installed dependencies, available migrations, and the local database configuration.

## API Endpoints

The API is mounted under `/api/`.

The following routes are defined in the supplied URL configuration.

### Authentication

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/token/` | Obtain a JWT token pair |
| POST | `/api/token/refresh/` | Refresh an access token |
| POST | `/api/token/verify/` | Verify a token |
| POST | `/api/login/` | Authenticate using email and password and return JWT tokens |

The project also provides browser-based account registration, login, and password reset pages under `/account/`.

### Search and Conversations

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/search/` | Search users and public conversations |
| GET | `/api/conversations/<conversation_type>/` | List conversations by type |
| GET | `/api/conversation/<conversation_type>/<conversation_id>/` | Retrieve conversation details |
| GET | `/api/conversation/<conversation_type>/user/<user_id>/` | Retrieve a user for direct-conversation handling |
| GET | `/api/conversation/<conversation_type>/profile/<conversation_id>/` | Retrieve conversation profile information |
| GET | `/api/conversation/<conversation_type>/user/<user_id>/profile/` | Retrieve user information for profile handling |
| POST | `/api/conversation/create/` | Create a conversation |
| PUT/PATCH | `/api/conversation/<pk>/update/` | Update a conversation |
| GET | `/api/conversation/<pk>/setting/` | Retrieve group or channel settings |
| DELETE | `/api/conversation/<pk>/delete/` | Delete a group or channel |

The conversation type is represented by a slug. The model defines `direct`, `group`, and `channel` as its available choices.

### Membership Management

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/membership/add/` | Create a membership record |
| PUT/PATCH | `/api/membership/<pk>/update/` | Update a membership record |
| DELETE | `/api/membership/<pk>/delete/` | Remove a membership record |

### Blocking

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/blocklist/toggle/` | Create a block-list entry |
| DELETE | `/api/blocklist/toggle/<pk>/` | Delete a block-list entry |

### Profile Management

| Method | Endpoint | Purpose |
|---|---|---|
| PUT/PATCH | `/api/update-account/` | Update the authenticated user's profile |

The profile update endpoint supports form and multipart form data.

**API documentation note:** The table lists the routes and HTTP methods supported by the configured Django REST Framework views. It is not a complete request/response specification. Request fields, response schemas, and all validation rules should be checked against the serializers and views before documenting detailed API examples.

## Account URLs

The account application is mounted under `/account/`.

| Endpoint | Purpose |
|---|---|
| `/account/` | View the authenticated user's account page |
| `/account/delete/user/<pk>/` | Delete a user account |
| `/account/register/` | Register an account |
| `/account/register/registration_done/` | Registration confirmation page |
| `/account/register/<uidb64>/<token>/` | Confirm registration |
| `/account/login/` | Login page |
| `/account/password_reset/` | Request a password reset |
| `/account/password_reset/done/` | Password-reset request confirmation |
| `/account/reset/<uidb64>/<token>/` | Confirm a password reset |
| `/account/reset/done/` | Password-reset completion page |

The registration workflow sends an activation email and uses a token-based confirmation process.

The actual email delivery configuration depends on the environment and the configured email backend.

## WebSocket Communication

SMChat defines the following WebSocket route:

```text
/ws/chat/<room_name>/
```

For example, a connection to a conversation whose ID is `12` would use the room name `12`, provided that this corresponds to the conversation used by the client.

The consumer uses the room name to construct the Channels group name:

```text
chat_<room_name>
```

The consumer handles text messages and binary frames. Text messages are processed according to their `messageType`, including message creation, file upload events, cancellation events, and status notifications.

For regular messages, the consumer:

1. Reads the conversation identifier from the incoming message.
2. Retrieves the conversation.
3. Checks its message-sending conditions.
4. Creates a database message record when appropriate.
5. Adds message metadata, including its ID and attachment URLs when available.
6. Broadcasts the outgoing event to the corresponding channel group.

The consumer also supports replies by associating a message with an existing message record.

### WebSocket Authentication

The custom JWT middleware attempts to obtain a token from either:

- The `token` query-string parameter.
- The `Authorization` header.

It validates the token and assigns the corresponding user to the WebSocket scope when authentication succeeds.

When a token is missing or invalid, the middleware assigns an anonymous user. The supplied consumer does not explicitly reject anonymous connections during its `connect()` method, so the implementation should not be described as enforcing authenticated WebSocket access.

### File Upload Handling

The consumer supports receiving binary data over the WebSocket connection and tracking upload progress.

The upload code uses temporary files and creates a message record when an upload is finalized. Files identified by the code as `image/png` are assigned to the image field; other uploads are assigned to the file field.

The consumer defines a 50 MB size threshold for selecting its temporary-file buffering approach. This threshold should not be interpreted as a fully verified upload-size validation policy.

## Configuration Notes

The supplied settings include the following configuration:

- Custom user model: `account.User`
- REST API authentication using Simple JWT
- Access token lifetime of one minute
- Refresh token lifetime of one day
- Refresh-token rotation enabled
- Blacklisting after token rotation enabled
- Django Channels using the in-memory channel layer
- ASGI application configured as `config.asgi.application`
- Django templates enabled through app directories
- Static and media file settings
- CORS allowed origins configured for local development addresses

The project also defines password validators and uses timezone-aware datetimes.

The current channel-layer configuration is in-memory. Redis or another external channel-layer backend is not configured in the supplied settings.

## Testing

Automated tests are not currently implemented, according to the supplied project information.

Although `tests.py` files exist in the project structure, their presence does not establish that automated tests have been written or executed.

No test results or test coverage claims are included in this README.

## Current Development Status

SMChat is currently a local development project.

The supplied configuration and code establish its core data models, API routes, account workflows, and WebSocket message-handling implementation. However, the available information does not establish:

- A public deployment.
- Production server configuration.
- A production-ready channel layer.
- Automated test coverage.
- Verified end-to-end behavior for every API endpoint.
- A complete WebSocket authorization policy.
- Support for every file type or image format.
- Production readiness or scalability.

These items are not presented as implemented features.

## License

No license information was provided. Add a license section only after choosing and adding an appropriate license to the repository.