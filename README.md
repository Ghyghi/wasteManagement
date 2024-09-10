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
- Add a __main__ function to the mailapi.py file and test it by running:
    ```bash
    python waste/mailapi.py
    ```
    OR
    ```bash
    python3 waste/mailapi.py
    ```
This will allow Google to verify your application.

6. Run the application:
    ```bash
    python run.py
    ```
    OR
   ```bash
    python3 run.py
    ```
