# YouTube Channel Data Collector

## Overview

This Python script searches for YouTube channels based on a user-provided query and collects detailed information about each channel. The collected data includes the channel name, URL, Gmail address (if available), subscriber count, and links to various platforms and social media extracted from the channel's description. The data is saved to an Excel file named `Youtube_Data_Analyts.xlsx` for further analysis.

## Features

- **Channel Search:** Search for YouTube channels using a custom query.
- **Data Extraction:** Extract channel details such as name, URL, and subscriber count.
- **Email Extraction:** Attempt to find a Gmail address from the channel description or the descriptions of the channel's latest 10 videos.
- **Link Extraction:** Extract links to the channel's own website, educational platforms (Udemy, Coursera), publishing platforms (KDP, Draft2Digital, iBooks), and social media (Facebook, Instagram, X/Twitter, LinkedIn).
- **API Key Management:** Cycle through multiple API keys to handle quota limits effectively.
- **Data Persistence:** Update an existing Excel file with new data while preserving existing entries and filling in missing information.

## Usage

### Prerequisites

- Python 3.x installed on your system.
- Required Python packages: `google-api-python-client`, `pandas`, `openpyxl`.
- A Google Cloud project with the YouTube Data API v3 enabled.
- One or more API keys for the YouTube Data API.

### Setup

1. **API Keys:** Replace the placeholder API keys in the `API_KEYS` list within the script (e.g., `'AIzaSyD7HbSYVS-Cpqno4Zx8y-*************'`) with your actual API keys. **Important:** Do not commit your actual API keys to a public repository. Keep them secure and replace them locally before running the script.
2. **Permissions:** Ensure the script has write permissions in the directory where the Excel file (`Youtube_Data_Analyts.xlsx`) will be saved.

### Running the Script

1. Execute the script using Python:
2. When prompted, enter your YouTube search query (e.g., "python tutorials").
3. The script will search for channels, collect the specified data, and save it to `Youtube_Data_Analyts.xlsx`.

### Output

- The script appends new channel data to the Excel file without duplicating existing entries (based on the channel URL).
- It also attempts to fill in missing Gmail addresses for channels already present in the Excel file by checking video descriptions if needed.

## Dependencies

The script relies on the following Python packages:

- `google-api-python-client`: For interacting with the YouTube Data API.
- `pandas`: For data manipulation and Excel file operations.
- `openpyxl`: For writing data to Excel files.

Install the dependencies using the provided `requirements.txt` file:

## Notes

- **API Quotas:** The script cycles through multiple API keys when a 403 (quota exceeded) or 429 (too many requests) error occurs. Ensure you have sufficient quota across your API keys for your search volume.
- **Data Accuracy:** Email and link extraction uses regular expressions, which may not capture all formats or could occasionally misidentify data. Verify critical data manually if necessary.
- **Performance:** For channels without emails in their descriptions, the script checks up to 10 video descriptions, which may increase runtime.

## Security Note

- **API Keys:** The script includes placeholder API keys with asterisks (e.g., `'AIzaSyD7HbSYVS-Cpqno4Zx8y-*************'`). Replace these with your own keys locally, but do not upload actual keys to a public GitHub repository. Consider using environment variables or a configuration file for better security in production use.
