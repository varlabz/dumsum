## Setting Up Chrome for Remote Debugging

### For Mac OS:
1. **Launch Google Chrome with Remote Debugging**  
   Open Terminal and run:
   ```bash
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222
   ```

### For Windows:
1. Create a shortcut to Chrome
2. Right-click > Properties
3. Add to target: `--remote-debugging-port=9222`
4. Apply changes
5. Use this shortcut to launch Chrome

### For Linux:
```bash
google-chrome --remote-debugging-port=9222
```

- **Verify Chrome's Command Line Parameters**  
   To confirm that Chrome is running with the correct remote debugging flag, open the following URL in Chrome:
   ```
   chrome://version/
   ```
   Under the section titled **"Command Line"**, ensure that the parameter `--remote-debugging-port=9222` is present. This confirms that Chrome is ready to accept remote debugging sessions.

- **Check if Remote Debugging is Active**  
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

## Obtaining a GitHub Authentication Token

If you don’t already have a GitHub authentication token, follow these steps:

1. Visit GitHub's [Personal Access Tokens](https://github.com/settings/tokens) page.
2. Click **Generate new token**.
3. Select the appropriate scopes required for your repository access.
4. Once generated, store the token safely for use with Git operations.

For more details, check out this GitHub [discussion](https://github.com/orgs/community/discussions/74701) on generating access tokens.

