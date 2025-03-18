# Development Guide

This guide provides instructions for setting up and running the project, specifically for Python developers.

## Prerequisites

-   Python 3.7+ (or higher)
-   `pip` (Python package installer)
-   `virtualenv` or `venv` (for virtual environment management)
-   Git

## Setup Instructions

1.  **Clone the Repository:**

    Open your terminal and navigate to the directory where you want to clone the project. Then, run the following command:

    ```bash
    git clone git@github.com:varlabz/dumsum.git
    ```

2.  **Navigate to the Project Directory:**

    ```bash
    cd dumsum
    ```

3.  **Create and Activate a Virtual Environment (Recommended):**

    It's best practice to create a virtual environment to isolate project dependencies.

    ```bash
    # Create a virtual environment
    python -m venv env

    # Activate the virtual environment
    source env/bin/activate  # On Linux/macOS
    # env\\Scripts\\activate  # On Windows
    ```

4.  **Install Dependencies:**

    Install the required Python dependencies using `pip`:

    ```bash
    pip install -r requirements.txt
    ```
    It is recommended to upgrade pip before installing dependencies:
    ```bash
    pip install --upgrade pip
    ```

5.  **Prepare Resume Data:**

    Place your resume in Markdown format at `data/resume.md`. See the [example](https://chatgpt.com/canvas/shared/67d9bb9721288191a9daa49eea914666) for the expected structure.

6. **Set up API keys**:
   Copy `.key.example` to `.key` and add your API keys.

## Running the Bot

**Note:** Ensure you are using the correct Python version (3.7+).

1.  **Get Help:**

    To see available command-line options, run:

    ```bash
    python src/linkedin.py --help
    ```

    This will display the following usage information:

    ```
    usage: linkedin.py [-h] [--matcher MATCHER] [--matcher-ignore MATCHER_IGNORE] [--speed SPEED] [--click-apply] [--click-easy-apply] [--debug-easy-apply-form] [--debug-matcher] [--debug-1page]

    LinkedIn Bot

    options:
      -h, --help            show this help message and exit
      --matcher MATCHER     Use resume matcher to filter job positions (default 70). Specify a percentage (0-100) for matching threshold.
      --matcher-ignore MATCHER_IGNORE
                              Use resume matcher to mark as ignore (default 50). Specify a percentage (0-100) for matching threshold.
      --speed SPEED         Speed of the process. 0 - slow(default), 1 - fast
      --click-apply         Click to 'Apply' button
      --click-easy-apply    Click to 'Easy Apply' button
      --debug-easy-apply-form
                              Debug: use 'easy apply' form to current position only
      --debug-matcher       Debug: show match value only
      --debug-1page         Debug: run 1 page only and apply to 'easy apply' position
    ```

2.  **Run with Default Settings:**

    To start the bot with default settings, simply run:

    ```bash
    python src/linkedin.py
    ```

    This will find job pages, iterate through positions, and calculate a match value based on your resume. Positions with a match score below the `matcher-ignore` value (default 50) will be marked as "don't show again."