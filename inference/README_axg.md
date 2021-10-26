```shell
curl --location --request POST 'http://localhost:8080/invocations' \
--header 'Content-Type: application/json' \
--data-raw '{
    "images": [
        "https://download-3d.s3.us-east-2.amazonaws.com/me_comp-p-500.jpg"]
}'
```