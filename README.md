# Daraz UI Automation Framework

A robust test automation suite for daraz.pk built with Python, Playwright, and Behave (BDD). This framework implements the Page Object Model (POM) to ensure maintainability and scalability for end-to-end testing of e-commerce workflows.

## Features

- **Behavior Driven Development (BDD)**: Human-readable Gherkin feature files for test definition.
- **Page Object Model (POM)**: Complete separation of UI elements and test logic.
- **Cross-Browser Support**: Configurable execution on Chromium and Firefox via Playwright.
- **Multi-Source Data Driven Testing**: Integration with Excel, SQLite database, and Redis (with JSON fallback).
- **Automated Reporting**: Detailed execution reports including failed scenario screenshots and logs.
- **CI/CD Integration**: GitHub Actions workflow for automated regression testing on every pull request.

## Technology Stack

- **Language**: Python 3.11+
- **Browser Engine**: Playwright
- **BDD Runner**: Behave
- **Reporting**: Allure
- **Data Handling**: Pandas, OpenPyXL, SQLite3, Redis-py
- **Configuration**: Python-dotenv, Behave.ini

## Project Structure

```text
daraz-automation-framework/
├── .github/workflows/      # CI/CD configurations
├── features/               # Gherkin feature files
│   ├── steps/              # Step definitions (glue code)
│   └── environment.py      # Hooks (Setup/Teardown)
├── pages/                  # Page Object Model classes
├── utils/                  # Core utilities (browser factory, data readers)
├── test_data/              # Excel and JSON data files
├── db/                     # SQL database and setup scripts
├── reports/                # Generated test results
├── requirements.txt        # Project dependencies
└── behave.ini              # Behave runner configuration
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Allure CLI (for viewing reports)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hamnaasiif/daraz-qa-automation-testing.git
   cd daraz-automation-framework
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m playwright install chromium firefox
   ```

4. Initialize the test database:
   ```bash
   python db/setup_database.py
   ```

## Execution

Running all tests:
```bash
behave
```

Running specific tags:
```bash
behave --tags @smoke
behave --tags @search
```

Running on a specific browser:
```bash
# Via environment variable
BROWSER=firefox behave
```

## Reporting

Test results are automatically stored in the `allure-results` directory. To generate and open the HTML report, use:

```bash
behave -f allure_behave.formatter:AllureFormatter -o allure-results/
allure generate allure-results/ --clean -o allure-report/
allure open allure-report/
```

## Data Management

- **Excel**: Test parameters are pulled from `test_data/products.xlsx`.
- **Database**: Product IDs and search terms validated against the SQLite database in `db/test_data.db`.
- **Redis**: Popular search terms and shared state managed via Redis, with automatic fallback to local JSON in `test_data/redis_data.json`.


