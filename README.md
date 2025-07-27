# Weather Forecast Microservice (WIP)

This repository currently hosts a **work-in-progress** microservice for fetching weather forecasts.

## Current State: Weather Forecast Microservices

This repository now hosts two functional microservices for fetching weather forecasts:

-   **US Weather Microservice**: `us_mcp_server.py` provides basic weather data, primarily serving as a testbed for the microservice architecture.
-   **UK Met Office Microservice**: `UK_Met_Office_Site_Specific_Forecast_MCP.py` integrates with the **UK Met Office Site-Specific forecast API** via the Met Office DataHub (https://datahub.metoffice.gov.uk/) to provide UK-specific weather data and forecast parameters.

## Getting Started

### US Weather Microservice

To run the US weather microservice:

1.  Ensure you have Python installed.
2.  Install any necessary dependencies (if any, typically listed in `pyproject.toml` or `requirements.txt`).
3.  Run the server:
    ```bash
    python us_mcp_server.py
    ```

### UK Met Office Microservice

To run the UK Met Office microservice:

1.  Ensure you have Python installed.
2.  Install any necessary dependencies (if any, typically listed in `pyproject.toml` or `requirements.txt`).
3.  **Set up API Credentials**: You will need to obtain API credentials from the Met Office DataHub. Create a `private` directory in the project root and add a file named `met_office_api_key.txt` inside it. This file should contain your API key.
    ```
    # Example: private/met_office_api_key.txt
    YOUR_MET_OFFICE_API_KEY_HERE
    ```
4.  Run the server:
    ```bash
    python UK_Met_Office_Site_Specific_Forecast_MCP.py
    ```

## Contributing

Contributions are welcome as the project evolves. Please open an issue or pull request.

## License

This project is licensed under the [MIT License](LICENSE).