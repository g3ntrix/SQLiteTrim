## Usage

1. **Run the Installation and Script**:
    ```sh
    bash -c "$(curl -fsSL https://raw.githubusercontent.com/g3ntrix/SQLiteTrim/main/install_and_run.sh)"
    ```

## Important Notes

1. **Backup your data** before using this tool. SQLiteTrim is in the early phase of development and may contain bugs.
2. **Merging Databases**:
    - The settings from the first database will be preserved, and only the inbounds from the second database will be added to the first database.
    - The IDs of the new database will be sorted automatically.
    - **Improved Feature**: The tool can now detect identical ports and merge their clients into one in the final database. Unique clients from both databases will be combined under the same port, and client traffic data will be accurately aggregated. If specific client data is missing, the parent inbound traffic data will be used.
3. **Environment Requirements**:
    - For GUI operation, ensure Tkinter is installed and available on your system.
    - For terminal operation, ensure your environment supports standard Python input/output operations.

## Screenshots

<table>
  <tr>
    <td style="text-align: center;"><img src="SC/2.jpg" alt="Menu" width="90%"></td>
    <td style="text-align: center;"><img src="SC/1.jpg" alt="Process" width="90%"></td>
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

[Read this in Persian (فارسی)](README_FA.md)

---

### Key Changes:
1. **Status Display**: Real-time status messages to provide feedback during the merge process.
2. **Client Traffic Merging**: Enhanced logic to merge client traffic data, ensuring accurate aggregation based on parent usage when specific client data is missing.
3. **Similar Ports Detection**: Identify and display similar ports found during the merge process for better clarity.
4. **Error Handling**: Further improved error handling with clear messages for operational errors and warnings.
5. **Code Refactoring**: Additional refactoring for better readability and maintainability.
6. **User Interaction**: Enhanced GUI and terminal interface logic for improved user interaction.
7. **Bug Fixes**: Resolved issues where client traffic data was not correctly merged, particularly for clients under the same port.
