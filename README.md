# embed.md

A lightweight markdown rendering and embedding service. Write markdown in your browser and embed it anywhere with an iframe or direct link.

## Self-Hosting Guide

### Prerequisites

- Docker (recommended)
- Python 3.9+ (for local development)
- SQLite3

### Enabling HTTPS

Recommended: use reverse proxy like Nginx or Caddy

#### Nginx Example

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Local Development Setup

1. Clone the repository:

```bash
git clone https://github.com/elimelt/embed.git
cd embed
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the development server:

```bash
uvicorn src.main:app --reload --port 8000
```

The service will be available at `http://localhost:8000`

### Docker Setup

1. Build the Docker image:

```bash
docker build -t server:embed .

```

2. Run the Docker container:

```bash
docker run -p 80:80 server:embed
```

## API Endpoints

### Create Embed

```
POST /api/embeds
Content-Type: application/json

{
    "content": "# Your Markdown Content"
}
```

### Get Document

```
GET /api/embeds/{embed_id}
Authorization: {auth_key}
```

### Update Document

```
PUT /api/embeds/{embed_id}
Authorization: {auth_key}
Content-Type: application/json

{
    "content": "# Updated Content"
}
```

### Delete Document

```
DELETE /api/embeds/{embed_id}
Authorization: {auth_key}
```

## Using the Embed

Once you've created a markdown document, you can embed it in two ways:

1. **iframe Embed**:

```html
<iframe
  src="http://your-domain/embed/{uuid}"
  width="100%"
  height="500px"
  frameborder="0"
></iframe>
```

2. **Direct Link**:

```
http://your-domain/view/{uuid}
```

## Client Keyboard Shortcuts

- `⌘ + P`: Preview markdown
- `⌘ + Enter`: Save/update current document
- `⇧ + ⌘ + Enter`: Create new document
- `⌘ + C`: Copy embed code/link

## License

MIT License - see LICENSE
