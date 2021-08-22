# ✂️ lnk
Small API to cut links. Runs over memory cache or Redis (for persistant links).

## Example
1. Pass your URL to API
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"url":"https://my-test-url.com", "uid":"your-uid", "ttl":"10m"}' \
  http://localhost:8010/
```
You'll get response with a cutted link.
  
2. Use a cutted link

## Build application
```make build```

## Run application in _dev_ mode
``` make run```
