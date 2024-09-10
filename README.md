# Smart Waste Web Application

## Overview

This project is a Smart Waste Management System built with Flask. <br/>
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


## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/Ghyghi/wasteManagement.git
    cd smart_waste_management
    ```

2. Create a virtual environment and activate it:
    On Mac
    ```bash
    virtualenv <environment name>
    source <environment name>/bin/activate
    ```
    On Windows
    ```bash
    python3 -m venv <environment name>
    './<environment name>/Scripts/activate.bat'
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    OR
   ```bash
    pip3 install -r requirements.txt
    ```

5. Configure the database in `app/config.py`. Create the MySQL database and name it "Smart".

6. Add the necessary Google API credentials:
- Through the Google Cloud Console enable the Gmail and Calendar APIs.
- Download the credentials file and rename it "credentials.json"
- Save the credentials file in your virtual environment folder
- Set up environmental variables: SECRET_KEY, ENV_FOLDER, and API_KEY. Assign them their corresponding values.
- Add a __main__ function to the mailapi.py file :<br/>
e.g:
```
if __name__=="__main__":
    get_credentials()
    get_gmail_service()
    get_calendar_service()
    email='youremail@gmail.com'
    subject='Test Email'
    html_content='This is a test'
    send_email(email, subject, html_content)
    user_emails =['email1@gmail.com', 'email2@gmail.com.com']
    summary = 'remainder'
    user_location = 'location'
    startdate = 'any datetime'
    user_choice = 'weekly'
    create_calendar_reminder(user_emails, user_location, startdate, user_choice)
    send_email_notification(user_emails, summary)
```
- Make the necessary changes to make sure that you receive the test emails
- Test it by running: <br/>
```bash
python waste/mailapi.py
```
OR
```bash
python3 waste/mailapi.py
```
- When prompted, please select the Google account you want to be associated with your application. <br/>
This will allow Google to verify your application.

6. Run the application:
```bash
python run.py
```
OR
```bash
python3 run.py
```
