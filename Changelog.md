# Changelog

## [v1.0.0] - 2024-06-16
### Added
- Initial release of SQLiteTrim.
- **GUI and Terminal Interfaces**: Users can choose between a graphical interface or terminal commands for interacting with SQLite databases.
- **Recreate Database with Sequential IDs**: Functionality to reorder IDs in a database sequentially starting from a specified ID.
- **Merge Databases**: Combine two SQLite databases, ensuring unique client entries and handling port conflicts.
- **Delete Database Rows**: Delete single rows or a range of rows from the database and recreate the database with sequential IDs.
- **Environment Detection**: Automatic detection of the environment (GUI or terminal) and appropriate handling of file selection and user inputs.
- **Backup Recommendation**: Prominent notice to users to back up their data before using the tool.
- **Dependency Checks**: Ensures necessary dependencies like Tkinter are installed for GUI operations.

### Notes
- **Merging Databases**: When merging, ensure no identical ports exist in both databases to avoid conflicts.
- **New Feature**: Detection and merging of identical ports' clients into one entry in the final database.
- **Environment Requirements**: Detailed requirements for running the tool in both GUI and terminal environments.
- **Screenshots**: Included screenshots for a better understanding of the tool’s interface and processes.

### License
- This project is licensed under the MIT License.

### Contributions
- Contributions are welcome! Please fork the repository and submit pull requests for any features, bug fixes, or improvements.

### Acknowledgements
- Developed by [g3ntrix](https://github.com/g3ntrix)
