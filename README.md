## prerequisites
- docker
- chrome browser



Mac OS
```
open -a "Google Chrome.app" --args --remote-debugging-port=9222
```

### check chrome parameters and check "Command Line:" for  --remote-debugging-port=9222
```
chrome://version/
```

### check in browser if debugging available

http://localhost:9222/json/version/ with response like

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


### build docker and run docker
- docker build -t linkedin-pw .
- docker build -t linkedin-pw https://${GIT_AUTH_TOKEN}@github.com/username/repository.git
- docker pull testlabz/linkedin-pw
- docker run -it --rm --add-host host.docker.internal:host-gateway -v ./data:/app/data linkedin-pw 

### how to get git auth token
https://github.com/orgs/community/discussions/74701
