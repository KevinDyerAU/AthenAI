# Creative Tool — Storage (S3 Presigned)

Purpose: upload generated content to S3 using a client-provided presigned URL.

- Workflow: `workflows/creative-tools/storage-s3.json`
- Webhook: `POST /webhook/creative/tools/storage-s3`

## Prerequisites
- A valid S3 presigned URL (client or separate signer workflow)

## Request
```json
{
  "content": {"kind":"text","output":"..."},
  "contentType": "application/json",
  "preSignedUrl": "https://s3.amazonaws.com/bucket/key?...",
  "bucket": "bucket",
  "key": "key"
}
```

## Response (shape)
- `{ status: 'ok', key, bucket, etag }`

## Recommended Next Steps
- Add server-side signer workflow with AWS credentials
- Add checksum validation and retry/backoff
- Support multi-part uploads for large files
- Add object tagging and lifecycle policy notes
