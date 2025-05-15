# Steam Game Data Fetcher

An ETL pipeline project that ingests, cleans, and structures Steam public app data using Python, designed to run within a Docker container using Docker Compose. It retrieves a list of all Steam applications, extracts their AppIDs, and then iteratively fetches detailed information for each application.

## How it Works

The script performs the following steps:

1.  **Fetch App List**: Retrieves a complete list of applications from the Steam API.
    ```
    Steam API (GetAppList)  ─────>  /json/applist.json
    ```
2.  **Extract AppIDs**: Parses `applist.json` to extract unique, sorted AppIDs for applications with names.
    ```
    /json/applist.json      ─────>  /json/appids.json
    ```
3.  **Fetch App Details**: Iteratively queries the Steam API for detailed information for each AppID.
    *   The process can be controlled by environment variables to fetch data in batches and resume.
    *   Fetched data is cleaned and structured.
    ```
    /json/appids.json ────┐
                          │ (Loop for each AppID in batch)
                          V
    Steam API (appdetails) ───> Clean Data ───┬───> /json/raw_data.json (contains new + previous data)
                                              ├───> /json/errorLogs.json
                                              └───> /json/intervalLogs.txt (progress log)
    ```

## Running with Docker Compose

This script is intended to be run using Docker Compose.

1.  Ensure you have Docker and Docker Compose installed.
2.  Configure your `docker-compose.yml` to:
    *   Build and run this Python script.
    *   Mount a volume to `/json/` inside the container for persistent storage of output files (e.g., by adding `volumes: ['./data:/json']` to your service definition, where `./data` is a directory on your host).
    *   Set any necessary environment variables (see below).
3.  Run the container:
    ```bash
    docker-compose up -d
    ```
    (Use `docker-compose up` to view logs directly, or `docker-compose logs -f <service_name>` for a running container).

## Environment Variables

The script uses the following environment variables, typically set in your `docker-compose.yml`:

*   `SAVE_STATE`: (Optional) File writing mode for `applist.json` and `appids.json`.
    *   `w` (default): Overwrite if files exist.
    *   `x`: Create new; fail if files exist.
*   `LAST_NO`: (Optional) The starting index (negative, from the end of the `appids` list) for fetching detailed app data. Default: `-1`.
*   `RANGE_LAST`: (Optional) The ending index (negative) for fetching. The loop stops when `LAST_NO` becomes less than `RANGE_LAST`. Default: `-1000`.
*   `INTERVALS`: (Optional) The number of AppIDs to process in each batch of detailed data fetching. Default: `100`.

## Output Files

The script generates the following files in the `/json/` directory (inside the container, mapped to your host via Docker volume):

*   `applist.json`: Raw JSON response from the `GetAppList` Steam API endpoint.
*   `appids.json`: A JSON list of sorted, unique AppIDs extracted from `applist.json`.
*   `raw_data.json`: A JSON list of structured, cleaned data for each fetched application. When resuming, previously fetched data is loaded and combined with newly fetched data before rewriting this file.
*   `errorLogs.json`: A JSON list of AppIDs that resulted in errors during the data fetching process, along with the error message.
*   `intervalLogs.txt`: A text file logging the progress of batch data fetching (appended with each batch completion).


## License

This work is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

You are free to:

- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:

- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- **NonCommercial** — You may not use the material for commercial purposes.
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

See the full license text here: [https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode)