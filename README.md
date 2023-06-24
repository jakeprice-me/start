# Start

My personal start/home/new-tab page with a searchable list of my most visited links/bookmarks.

![](public/assets/images/screenshot.png)

## Dependencies

The search feature is powered by, and completely dependant on [Typesense](https://typesense.org/), and uses the excellent [typesense-instantsearch-adapter](https://github.com/typesense/typesense-instantsearch-adapter). I have a Docker container running Typesense that the application code talks too. Complete overkill really, and long-term I may look at using something like [Fuse.js](https://fusejs.io/).

I also know very little about Javascript, so it's all a bit bodged together, but it works and, I think, looks nice - so who cares!

## Configuration

`config_template.yml` should be renamed to `config.yml` and variables updated.

## Search-Only API Key

**Warning** - There's a publically accessible API key that will be viewable if you host this on the web. It's in a file that's created by `main.py` called `typesense_adaptor.js`. The key is scoped to have search-only permissions, so it doesn't give any risky access out. 

If you were to host the site on the public internet, somebody could try and bring down your Typesense server by overwhelming it with `curl` requests, but I don't much care at the moment, because I host the application locally on my LAN, and via Tailscale for when I'm out and about - so it's not an issue for me right now. In the long-term I'll come up with a better solution, but for now I don't really mind. 

Here's how to create a search-only key.

```sh
curl "https://${TYPESENSE_SERVER}/keys" \
    -X POST \
    -H "X-TYPESENSE-API-KEY: ${TYPESENSE_API_KEY}" \
    -H 'Content-Type: application/json' \
    -d '{"description":"Search-only key.","actions": ["documents:search"], "collections": ["start"]}'
```

## Usage

The `links_template.yml` should be renamed to `links.yml` and serves as a list of bookmarks to index and add to the webpage. It's easy enough to add links, just follow the format below.

```yaml
---
- number: 1
  title: Brave Search
  url: https://search.brave.com
  icon: https://t1.gstatic.com/faviconV2?url={url}&client=SOCIAL&type=FAVICON
  category: organisation
  tags: [search]
- number: 2
  title: Fastmail Inbox
  url: https://app.fastmail.com
  icon: https://t1.gstatic.com/faviconV2?url={url}&client=SOCIAL&type=FAVICON
  category: organisation
  tags: [email, mail]
```

After adding links, you need to run the `main.py` script to import them into Typesense, and then you can refresh the webpage to see the latest list of links. This script should be run after any changes to colours defined in the `config.yml` file as well, as it rebuilds the webpage.

```sh
python3 main.py
```

You'll need to serve the `public/` directory up using a webserver. I use [Caddy](https://caddyserver.com/).

