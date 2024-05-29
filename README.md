# SQLiteTrim

**SQLiteTrim** is a specialized Python tool designed to help manage x-ui SQLite databases by removing excessive rows without affecting the overall functionality. This ensures that user creation and management remain seamless by maintaining correct sequential IDs. Additionally, the tool now supports merging two SQLite databases and offers both GUI and terminal interfaces.

## Features

- **Interactive Menu**: Provides a user-friendly interface to select deletion options.
- **Single Row Deletion**: Delete a specific row by its ID.
- **Range Deletion**: Delete a range of rows by specifying start and end IDs.
- **Sequential Renumbering**: Automatically renumbers remaining rows to maintain sequential order.
- **Database Merging**: Merge two SQLite databases while preserving settings from the first database.
- **GUI and Terminal Interfaces**: Choose between a graphical user interface or a terminal-based interface.
- **Safe Operations**: Modifies a copy of the original database to ensure data safety.

## Why SQLiteTrim?

x-ui databases can accumulate excessive rows over time, which can lead to inefficiencies and potential issues in managing user data. SQLiteTrim was developed to address this by allowing administrators to remove unwanted rows while preserving the functionality and integrity of the database. By maintaining correct sequential IDs, the tool ensures that the database remains optimized for user creation and other operations. The merging functionality further enhances the tool by allowing easy integration of multiple databases.

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

3. **Choose Interface**:
    - At startup, choose whether to use the GUI or terminal interface.

4. **Follow the Interactive Prompts**:
    - Choose to delete a single row, delete a range of rows, or merge two databases.
    - Enter the ID(s) or file paths as prompted.
    - The modified database will be saved with a new name, preserving the original file.

## Important Notes

1. **Backup your data** before using this tool. SQLiteTrim is in the early phase of development and may contain bugs.
2. Ensure that the `x-ui.db` file is named exactly as `x-ui.db` and placed in the directory where you run the tool.

## Screenshots

<table>
  <tr>
    <td style="text-align: center;"><img src="SC/2.jpg" alt="Menu" width="85%"></td>
    <td style="text-align: center;"><img src="SC/1.jpg" alt="Process" width="75%"></td>
  </tr>
</table>


## Requirements

- Python 3.x
- SQLite3
- Tkinter (for GUI)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any features, bug fixes, or improvements.

## Acknowledgements

Developed by [g3ntrix](https://github.com/g3ntrix)
