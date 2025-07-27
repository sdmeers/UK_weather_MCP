# Weather Forecast Microservice (WIP)

This repository currently hosts a **work-in-progress** microservice for fetching weather forecasts.

## Current State: US Weather (Test Project)

The `us_mcp_server.py` file contains a basic implementation for fetching weather data, primarily serving as a testbed for the microservice architecture. This is a temporary setup.

## Future Direction: UK Met Office Integration

The primary goal of this project is to reimplement the weather forecasting logic to utilize the **UK Met Office Site-Specific forecast API** via the Met Office DataHub (https://datahub.metoffice.gov.uk/). This will involve:

-   Integration with the Met Office DataHub API.
-   Handling UK-specific weather data and forecast parameters.
-   Refactoring the existing test implementation.

## Getting Started (Current Test Server)

To run the current US weather test server:

1.  Ensure you have Python installed.
2.  Install any necessary dependencies (if any, typically listed in `pyproject.toml` or `requirements.txt`).
3.  Run the server:
    ```bash
    python us_mcp_server.py
    ```

Further instructions will be provided as the UK Met Office integration progresses.

## Contributing

Contributions are welcome as the project evolves. Please open an issue or pull request.

## License

This project is licensed under the [MIT License](LICENSE).