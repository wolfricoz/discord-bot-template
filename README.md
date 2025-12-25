# Discord Bot Template
This repository is just a quick start for a discord bot including the database. This is mainly for personal use but if you are using this and get stuck, feel free to reach out on discord at: ricostryker.

## Getting Started

Follow these steps to get your bot up and running.

### Prerequisites
- **Python 3.13+**: The bot is built using a modern version of Python.
- **MySQL Server**: A database is required for data persistence.
- **Git**: For cloning the repository.

### 1. Install Python
Download and install Python 3.10 or newer from the [official Python website](https://www.python.org/downloads/).

**Important:** During installation on Windows, make sure to check the box that says **"Add Python to PATH"**.

### 2. Set up MySQL Database
You need to install and configure a MySQL server.

1.  Download and install MySQL Server from the [official website](https://dev.mysql.com/downloads/mysql/).
2.  During the setup, you will create a root user and password. Remember them.
3.  Connect to your MySQL server and run the following commands to create a dedicated database and user for your bot. Replace `your_database_name`, `your_user`, and `your_password` with your desired credentials.

    ```sql
    CREATE DATABASE your_database_name;
    CREATE USER 'your_user'@'localhost' IDENTIFIED BY 'your_password';
    GRANT ALL PRIVILEGES ON your_database_name.* TO 'your_user'@'localhost';
    FLUSH PRIVILEGES;
    ```

### 3. Configure Environment
Sensitive information like your bot token and database credentials are stored in an environment file.

1.  In the project's root directory, you will find a file named `.env.example`. Make a copy of this file and name it `.env`.
2.  Open the new `.env` file with a text editor and fill in the required values:
    - `TOKEN`: Your Discord bot's token.
    - `DEV`: The ID of your development/testing Discord server.
    - `DB_USER`: The MySQL username you created (`your_user`).
    - `DB_PASSWORD`: The password for the MySQL user (`your_password`).
    - `DB_HOST`: The address of your database server (usually `localhost`).
    - `DB_DATABASE`: The name of the database you created (`your_database_name`).

### 4. Install Dependencies
Open your terminal or command prompt, navigate to the project directory, and run the following command to install the necessary Python libraries listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 5. Run the Bot
Once everything is set up, you can start the bot with this command:

```bash
python main.py
```

## Advanced: Running the FastAPI Web Server

This template includes an optional FastAPI web server, which can be used for health checks, dashboards, or a public API.

To run the web server locally for development, you will need `uvicorn`. It should already be installed from `requirements.txt`.

Run the following command from the project's root directory:

```bash
uvicorn main:app --reload
```

- `main:app` tells uvicorn to find the `app` object inside the `main.py` file.
- `--reload` makes the server restart automatically after you make code changes.

You can now access the API at `http://127.0.0.1:8000` in your browser.


## AI DISCLAIMER
The comments in this codebase were generated or altered by AI to improve clarity and understanding, because english is my second language. All code has been written by a human developer, but the comments may have been modified by AI assistance.

## License
This project is licensed under the MIT License - see the [LICENSE](license) file for details

## Acknowledgments
- Thanks to discord.py and FastAPI communities for their excellent libraries and documentation.

## Documentation
Each library used in this project has its own documentation, here are some useful links:
- [discord.py Documentation](https://discordpy.readthedocs.io/en/stable/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [sqlalchemy Documentation](https://docs.sqlalchemy.org/en/20/)
- [setting up your first server](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-22-04)

## Contact
For any issues regarding the template, please open an issue on GitHub. If you need further assistance I highly recommend you join the [discord.py support server](https://discord.gg/dpy) and to google the issues, you will learn the most from this!

## Contributing
Feel free to fork the repository and submit pull requests. Any contributions to improve the bot are welcome!

## Donations
If you find this template helpful and would like to support its development, consider donating via [stripe](https://buy.stripe.com/7sYbJ17fYeGY45bgygao803). Your support is greatly appreciated!