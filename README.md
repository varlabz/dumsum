## Prerequisites
Before proceeding, ensure that the following tools are installed and configured on your system:
- **Docker**: You will need Docker to build and run the container.
- **Google Chrome Browser**: This is required for running script.

### Setting Up Chrome for Remote Debugging

To enable Chrome's remote debugging feature, follow these steps:

1. **Launch Google Chrome with Remote Debugging on Mac OS**  
   Open the terminal and run the following command to start Chrome with the remote debugging port enabled:
   ```bash
   open -a "Google Chrome.app" --args --remote-debugging-port=9222
   ```
   This command will open Google Chrome and set it to listen for debugging connections on port `9222`.

2. **Verify Chrome's Command Line Parameters**  
   To confirm that Chrome is running with the correct remote debugging flag, open the following URL in Chrome:
   ```
   chrome://version/
   ```
   Under the section titled **"Command Line"**, ensure that the parameter `--remote-debugging-port=9222` is present. This confirms that Chrome is ready to accept remote debugging sessions.

3. **Check if Remote Debugging is Active**  
   In your browser, navigate to the following URL to check if Chrome’s debugging is accessible:
   ```
   http://localhost:9222/json/version/
   ```
   If everything is set up correctly, you should receive a JSON response similar to this:
   ```json
   {
      "Browser": "Chrome/129.0.6668.101",
      "Protocol-Version": "1.3",
      "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
      "V8-Version": "12.9.202.27",
      "WebKit-Version": "537.36 (@129d018cd38423003cd025fe9ef01c75a897203b)",
      "webSocketDebuggerUrl": "ws://localhost:9222/devtools/browser/5c17626d-5a62-4060-8f17-dc20ff9609de"
   }
   ```
   This response confirms that the remote debugging service is active and ready for connections.

### Building and Running the Docker Container

1. **Build the Docker Image Locally**  
   You can build the Docker image from a local Dockerfile by using the following command:
   ```bash
   docker build -t linkedin-pw .
   ```
   This will create an image tagged as `linkedin-pw`.

2. **Build the Docker Image from a Git Repository**  
   If your Dockerfile is hosted in a Git repository, you can build the image directly from the repository. Ensure that you have your GitHub authentication token, then use this command:
   ```bash
   docker build -t linkedin-pw https://${GIT_AUTH_TOKEN}@github.com/var-lab/dumsum.git
   ```
   Replace `GIT_AUTH_TOKEN` with your actual GitHub authentication token.

3. **Pull Pre-built Docker Image**  
   Alternatively, you can pull the image directly using:
   ```bash
   docker pull testlabz/linkedin-pw
   ```

4. **Run the Docker Container**  
   To start the Docker container, use the following command:
   ```bash
   docker run -it --rm --add-host host.docker.internal:host-gateway -v ./data:/app/data linkedin-pw
   ```
   This command will:
   - Run the `linkedin-pw` container interactively (`-it`) and remove it when stopped (`--rm`).
   - Add a network route from the container to your host machine using `--add-host`.
   - Mount the local `./data` directory into the container at `/app/data`.

### Obtaining a GitHub Authentication Token
If you don’t already have a GitHub authentication token, follow these steps:

1. Visit GitHub's [Personal Access Tokens](https://github.com/settings/tokens) page.
2. Click **Generate new token**.
3. Select the appropriate scopes required for your repository access.
4. Once generated, store the token safely for use with Git operations.

For more details, check out this GitHub [discussion](https://github.com/orgs/community/discussions/74701) on generating access tokens.

