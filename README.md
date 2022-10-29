# ✂️ lnk
Small API to cut links. Runs over app memory or Redis (for persistant links).

## Example
1. Pass your URL to API
```
curl \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --header "X-Lnk-Token: your-token" \
  --request POST \
  --data 'url=https://my-test-url.com&uid=your-uid&ttl=10m' \
  http://localhost:8010/
```
You'll get response with a cutted link.
  
2. Use a cutted link

## Build run application in __dev__ mode
```docker-compose -f docker-compose.dev.yml up```

## Run tests
```docker-compose -f docker-compose.dev.yml run lnk /usr/share/python3/app/bin/pytest```

## Run linter
```docker-compose -f docker-compose.dev.yml run lnk /usr/share/python3/app/bin/flake8```
