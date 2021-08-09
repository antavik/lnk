# ✂️ lnk
Small API to cut links.

## Example
1. Get link
https://test.com

2. Pass to API
```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"url":"https://test.com", "uid":"your-uid", "ttl":"10m"}' \
  http://localhost:8010/
```
You'll get response with a cutted link.
  
3. Use a cutted link

## Build application
```make build```

## Run application in _dev_ mode
``` make run```

## 🎯 TODO
- [ ] Fix response if app run in a docker conteiner (bug with host url)
- [ ] Persistent links