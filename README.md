# Pokémon Battle Simulator

A small Pokémon Battle Simulator built with Flask, designed to simulate battles between Pokémon, manage Pokémon data, and cache results for optimized performance.

## Table of Contents

- [Features](#features)
- [Setup](#setup)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Demo](#demo)
- [UML Diagram](#uml-diagram)

## Features

- **Battle Simulation**: Simulate battles between two Pokémon with calculated damage and a declared winner.
- **Data Management**: Load and manage Pokémon data from a CSV file.
- **Caching**: Utilize Redis caching to optimize performance.
- **Asynchronous Processing**: Battles are processed asynchronously using Python's `threading` module, ensuring the application remains responsive.
- **Lazy Evaluation**: Efficient data handling using generators and decorators.
- **Factory Method Pattern**: The **Factory Method Design Pattern** is applied in the `Generator` class to create instances of different ID generators (`IDGenerator`, `UUIDGenerator`) based on the required format.


## Setup

### Prerequisites

- Python 3.8+
- Redis server (for caching)
- Flask and other dependencies (listed in `requirements.txt`)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/rushikesh-shinde-pyd/PokemonBattle.git
    cd PokemonBattle
    ```

2. Create and activate a virtual environment:

    - **On macOS and Linux**:

        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

    - **On Windows**:

        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up Redis:

    Ensure Redis is installed and running on your local machine.

5. Load Pokémon data:

    The Pokémon data is loaded from a CSV file located at `files/pokemon.csv`.

## Usage

### Running the Application

To start the Flask application, use the following command:

```bash
python app.py
```
2. Access the API at `http://127.0.0.1:5000`.

## API Documentation

For a detailed view of the API endpoints, including request and response examples, visit the [ API Documentation](https://documenter.getpostman.com/view/9822314/2sA3s3GqyF).

## Logging

Logs are stored in `log/app.log`, and the log files are rotated when they reach 10KB in size, keeping the last three logs.

## Testing

To test the application, you can use tools like `Postman` to interact with the API endpoints.

## Demo

See the Pokémon Battle Simulator in action with this [demo video](https://www.awesomescreenshot.com/video/30377833?key=eba8e82a8be3593939c8d56e79b1b6ad).

## UML Diagram

[Diagram](https://lucid.app/lucidchart/a633beac-0341-425e-9d1b-ae763a2d4aaa/edit?viewport_loc=-3093%2C-1042%2C4168%2C1681%2C0_0&invitationId=inv_da07aca5-9b22-49e2-bfd0-06b966ddf38d)