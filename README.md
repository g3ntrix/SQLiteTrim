# SQLiteTrim

**SQLiteTrim** is a specialized Python tool designed to help manage x-ui SQLite databases by removing excessive rows without affecting the overall functionality. This ensures that user creation and management remain seamless by maintaining correct sequential IDs.

## Features

- Interactive Menu: Provides a user-friendly interface to select deletion options.
- Single Row Deletion: Delete a specific row by its ID.
- Range Deletion: Delete a range of rows by specifying start and end IDs.
- Sequential Renumbering: Automatically renumbers remaining rows to maintain sequential order.
- Safe Operations: Modifies a copy of the original database to ensure data safety.

## Why SQLiteTrim?

x-ui databases can accumulate excessive rows over time, which can lead to inefficiencies and potential issues in managing user data. SQLiteTrim was developed to address this by allowing administrators to remove unwanted rows while preserving the functionality and integrity of the database. By maintaining correct sequential IDs, the tool ensures that the database remains optimized for user creation and other operations.

## Usage

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/g3ntrix/SQLiteTrim.git
    cd SQLiteTrim
    ```

2. **Run the Script**:
    ```sh
    python sqlite_trim.py
    ```

3. **Follow the Interactive Prompts**:
    - Choose to delete a single row or a range of rows.
    - Enter the ID(s) as prompted.
    - The modified database will be saved with a new name, preserving the original file.

## Important Notes

1. **Backup your data** before using this tool. SQLiteTrim is in the early phase of development and may contain bugs.
2. Ensure that the `x-ui.db` file is named exactly as `x-ui.db` and placed in the directory where you run the tool.

## Screenshot

<img src="SC/1.jpg" alt="Screenshot" width="300">

## Requirements

- Python 3.x
- SQLite3

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any features, bug fixes, or improvements.

## Acknowledgements

Developed by [g3ntrix](https://github.com/g3ntrix)
