## Project Goal
Simplify the job application process.

Benefits:
- Faster application submissions
- Consistent application process
- Reduced manual effort
- Better time management for job seekers

<img src="img/match.gif" alt="Match GIF" width="400">

## Process Flow
<details>
<summary>Click to expand</summary>

```mermaid
graph TD
    A[Start] --> B[Get list of positions on page]
    
    B --> C[Process Position]
    
    C --> C1[Compare resume to job description]
    C1 --> C2{Match > 70%?}
    C2 -->|Yes| C3[Start Easy Apply Form]
    C2 -->|No| C4[Go to next position]
    
    C3 --> F1[Get form field]
    F1 --> F2{Have info in history/resume for field?}
    F2 -->|Yes| F3[Auto-fill field]
    F2 -->|No| F4[Wait for user input]
    
    F3 --> F5{More fields?}
    F4 --> F5
    
    F5 -->|Yes| F1
    F5 -->|No| F6{All required fields completed?}
    
    F6 -->|Yes| F7[Press Next button]
    F6 -->|No| F4
    
    F7 --> C4
    
    C4 --> C5{More positions on page?}
    C5 -->|Yes| C
    C5 -->|No| D{Have next page?}
    
    D -->|Yes| E[Go to next page]
    E --> B
    D -->|No| G[End]
```
</details>

## Running with Docker (recommended)

Instructions for building and running the application using Docker can be found in [DOCKER.md](DOCKER.md).

## Development Setup

Instructions for setting up the development environment can be found in [DEVELOPMENT.md](DEVELOPMENT.md).

## Usage 

1. **Log In**:  Sign in to your LinkedIn account.
2. **Go to the Search Page**: Navigate to the job search page.
3. **Set Filters and Criteria**: In the search fields, enter the filters and criteria (e.g., job title, location, experience level) to find relevant job listings.
4. **Start the Search**: Click the search button to view results based on your specifications.
5. **Run the Bot**: Once the results load, activate the bot.


## DISCLAIMER

By using this project (the "Project"), you acknowledge and agree to the following terms and conditions:

**No Warranty:** The Project is provided "as is" without any warranty of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, and non-infringement.  The authors or contributors of the Project make no representations or warranties about the accuracy, completeness, reliability, suitability, or availability with respect to the Project or the information, products, services, or related graphics contained in the Project for any purpose.  Any reliance you place on such information is therefore strictly at your own risk.

**No Liability:** In no event will the authors or contributors of the Project be liable for any loss or damage including without limitation, indirect or consequential loss or damage, or any loss or damage whatsoever arising from loss of data or profits arising out of, or in connection with, the use of this Project.  This includes, but is not limited to, any errors or omissions in the content of the Project.

**Non-Commercial Use:**  This Project is provided for non-commercial use only.  You may not use this Project for any commercial purpose, including but not limited to selling, licensing, or distributing the Project or any derivative works thereof for profit.

**Use at Your Own Risk:** You understand and agree that you are using the Project entirely at your own risk.  You are solely responsible for any consequences, losses, or damages that may result from your use of the Project.

By using the Project, you signify your acceptance of this disclaimer. If you do not agree to this disclaimer, do not use the Project.

## License

This project is licensed under the [MIT License](LICENSE.md).