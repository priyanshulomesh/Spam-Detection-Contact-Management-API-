# Spam Detection Application Backend

## Project Overview

This is a Django-based REST API backend for a mobile application that allows users to:

- Register and manage user profiles
- Search contacts by name or phone number
- Report spam numbers
- Protect user privacy with controlled information sharing

## Key Requirements

### User Registration

- Mandatory fields: Name, Phone Number, Password
- Optional field: Email Address
- One phone number per user
- Authentication required for all app functionalities

### Contact Management

- Users can have zero or more personal contacts
- Global database combines all registered users and their contacts
- Contacts may or may not be registered app users

### Search Functionality

#### Name Search

- Search across global database
- Results prioritized as:
  1. Names starting with search query
  2. Names containing (but not starting with) search query
- Results display:
  - Name
  - Phone Number
  - Spam Likelihood

#### Phone Number Search

- If number belongs to a registered user, show only that result
- Otherwise, show all matching contacts from global database
- Multiple users can have different names for same phone number

### Contact Details

- Clicking search result shows full details
- Email visible only if:
  - Contact is a registered user
  - Searcher is in contact's personal contact list

### Spam Reporting

- Users can mark any number as spam
- Spam status applies across global database
- Works for registered and unregistered numbers

## Architecture Overvew

The backend follows a Model-View-Controller (MVC) architecture pattern adapted to Django's structure. The key components include:

1. Models:

Represent the database structure.

Define the User, Contact, UserPhoneContact and ReportDetails models.

2. Views:

Handle HTTP requests and responses.

Each view corresponds to an API endpoint.

3. URLs:

Map endpoints to their respective views.

### Authentication

- JWT (JSON Web Token) based authentication
- Secure login mechanism
- All endpoints require authentication

### Data Models

- User Model
- Contact Model
- User Phone Contact Model
- Report Details Model

### API Endpoints

- `/register/`(POST): User registration
- `/login/`(POST): User authentication
- `/search_by_name/`(GET): Search contacts by name
- `/search_by_number/`(GET): Search contacts by phone number
- `/report_number/`(POST): Report spam numbers
- `/get_contact_details/`(GET): Retrieve full contact information

## Security Considerations

- Password hashing
- Token-based authentication
- Controlled information access
- Unique constraints on user and contact data

## Development Setup

### Prerequisites

- Python 3.12+
- Django
- Django Rest Framework
- Simple JWT

### Installation Steps

1. Install dependencies
   ```
   pip install -r requirements.txt
   ```
2. Configure database settings
3. Run migrations
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Populate Initial Data (for Testing)
   ```
   python manage.py populate_data
   ```
5. Run development server
   ```
   python manage.py runserver
   ```
6. Testing JWT Authentication
   ```
   Use an API client like Postman to test login and other API endpoints.
   Set the authorization header in your requests to pass the JWT token:
   Key: Authorization
   Value: Bearer <your-jwt-token>
   Replace <your-jwt-token> with the token you received during login.
   ```
