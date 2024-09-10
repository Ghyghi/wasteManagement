# Smart Waste Web Application

## Overview

This project is a Smart Waste Management System built with Flask.  
It allows users to manage waste collection schedules, track recycling efforts, and view environmental impact metrics.

## Features

- Schedule waste collection
- Join a collection route

## Functionalities

- User Registration and Login
- Waste Collection Schedule
- Waste Collection Services Management
- Admin Dashboard
- Admin Confirms Collectors

## Prerequisites

- Python 3.10 or higher(Python 3.12.3 is recommended)
- Flask
- MySQL
- Google API credentials for Gmail and Calendar
- Git
- Virtualenv or venv for creating a virtual environment

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Ghyghi/wasteManagement.git
    cd smart_waste_management
    ```

2. **Create a virtual environment and activate it:**

    - **On Mac:**
      ```bash
      virtualenv <environment_name>
      source <environment_name>/bin/activate
      ```

    - **On Windows:**
      ```bash
      python3 -m venv <environment_name>
      .\<environment_name>\Scripts\activate.bat
      ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    OR
    ```bash
    pip3 install -r requirements.txt
    ```

4. **Configure the database in `app/config.py`.**  
   Create the MySQL database and name it "Smart".

5. **Add the necessary Google API credentials:**
    - Through the Google Cloud Console, enable the Gmail and Calendar APIs.
    - Download the credentials file and rename it `credentials.json`.
    - Save the credentials file in your virtual environment folder.
    - Set up environmental variables: `SECRET_KEY`, `ENV_FOLDER`, and `API_KEY`. Assign them their corresponding values.
    - Add a `__main__` function to the `mailapi.py` file:

    ```python
    if __name__ == "__main__":
        get_credentials()
        get_gmail_service()
        get_calendar_service()
        email = 'youremail@gmail.com'
        subject = 'Test Email'
        html_content = 'This is a test'
        send_email(email, subject, html_content)
        user_emails = ['email1@gmail.com', 'email2@gmail.com']
        summary = 'Reminder'
        user_location = 'Location'
        startdate = 'Any datetime'
        user_choice = 'Weekly'
        create_calendar_reminder(user_emails, user_location, startdate, user_choice)
        send_email_notification(user_emails, summary)
    ```

    - Make the necessary changes to ensure you receive the test emails.
    - Test it by running:
    ```bash
    python waste/mailapi.py
    ```
    OR
    ```bash
    python3 waste/mailapi.py
    ```

    - When prompted, select the Google account you want to associate with your application.  
      This will allow Google to verify your application.

6. **Run the application:**
    ```bash
    python run.py
    ```
    OR
    ```bash
    python3 run.py
    ```

## Project Structure

- Primary Folder: wasteManagement
- Secondary Folders: env, migrations, waste
- Inside waste: static, templates, and the python files
## Configuration Details

- **Database Configuration:**
  - Open `config.py` and set up the database URI according to your MySQL credentials.

- **Google API Configuration:**
  - Place the `credentials.json` file in the root directory and ensure it is correctly set up for both Gmail and Calendar API.

## Environment Variables

- `SECRET_KEY`: Your Flask secret key for session management.
- `ENV_FOLDER`: The folder where the Google API credentials are stored.
- `API_KEY`: Your Google API key.
  
## Contribution
Contributions are welcome! Please follow these steps:

1. **Fork the repository.**
2. **Create a new branch (git checkout -b feature-branch).**
3. **Commit your changes (git commit -m 'Add new feature').**
4. **Push to the branch (git push origin feature-branch).**
5. **Open a pull request.**

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE (Version 3, 29 June 2007).  Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed. For more details, see the [LICENSE](LICENSE) file.

This Markdown file now provides a complete and detailed guide to setting up, using, and contributing to the Smart Waste Web Application.
