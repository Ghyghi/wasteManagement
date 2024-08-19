# Smart Waste Web Application

## Overview

This project is a Smart Waste Management System built with Flask. It allows users to manage waste collection schedules, track recycling efforts, and view environmental impact metrics.

## Features

- Schedule waste collection
- Track recycling efforts
- View environmental impact metrics

## Functionalities

User Registration and Login
Waste Collection Schedule
Recycling Tracker
Waste Collection Services Management
Admin Dashboard


## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/smart_waste_management.git
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
    If this gives you an error try "pip3"

4. Configure the database in `app/config.py`.

5. Run the application:
    ```bash
    python run.py
    ```
    If this gives you an error try "python3"

## Testing

Run the tests with:
```bash
pytest
```
