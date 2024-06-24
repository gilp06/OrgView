Here's the updated README with the requested changes:

---

# OrgView

OrgView is a comprehensive database management tool designed to assist the Career and Technical Education Department in managing information about local businesses and community organizations. It provides a centralized platform to store, search, filter, and manage organization details, making it easier to connect with community partners.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Technologies Used](#technologies-used)
- [Contributors](#contributors)

## Features

- **Centralized Database**: Store detailed information about local organizations.
- **User Authentication**: Role-based access control for Admins, Editors, and Viewers.
- **Advanced Search and Filter**: Quickly find organizations based on various criteria.
- **Data Management**: Add, edit, and delete organization details.
- **Export Functionality**: Export data to CSV for external use.
- **User-Friendly Interface**: Built with Dear PyGui for a seamless user experience.
- **ChatGPT Assistant**: Integrated ChatGPT assistant to help users with queries and provide support.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/OrgView.git
    cd OrgView
    ```

2. **Set up the virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure the database:**
    - Make sure you have PostgreSQL installed and running.
    - Create a new PostgreSQL database.
    - Update the `connection_settings.json` file with your database credentials.

5. **Run the application:**
    ```bash
    python main.py
    ```

## Usage

1. **Login:**
    - Enter your username and password on the login screen to authenticate.

2. **Main Interface:**
    - Navigate through different tabs such as Accounts and Organizations.
    - Use the search bar to find specific organizations.
    - Add new organizations by clicking the "+" button and filling in the required details.
    - Edit existing organizations by selecting them and updating the details.
    - Export organization data to CSV by clicking the "Export" button.

3. **User Management (Admins Only):**
    - Manage user roles and permissions.
    - Add, edit, and delete user accounts.

4. **ChatGPT Assistant:**
    - Use the integrated ChatGPT assistant for help and support directly within the application.

## File Structure

```
OrgView/
│
├── helper/
│   ├── chatgpt_api.py          # Handles API interactions with ChatGPT
│   ├── database_manager.py     # Handles database operations
│   ├── organization.py         # Defines the Organization class
│   ├── themes.py               # Contains themes for the GUI
│   ├── util.py                 # Utility functions
│
├── Images/                     # Contains image resources
│
├── connection_settings.json    # Database connection settings
├── requirements.txt            # Python dependencies
├── main.py                     # Main application file
└── README.md                   # This README file
```

## Technologies Used

- **Python**
- **Dear PyGui**: For the graphical user interface.
- **PostgreSQL**: For the backend database.
- **psycopg**: PostgreSQL adapter for Python.

## Contributors

- **Bill Xu**
- **Gil Powers**
