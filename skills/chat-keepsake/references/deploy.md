# Deploying a keepsake page

A link on a domain the commissioner owns beats a file attachment. It opens on a phone with
no download, and it can be updated after sending.

These notes are written for Cloudflare Pages with a domain already on Cloudflare
nameservers. Adapt freely.

---

## The page itself

Keep it to one self-contained `index.html` plus an `img/` directory. No build step, no
framework. It has to still work in five years when someone opens the link again.

Webfonts from a CDN are fine for the page (the browser fetches them without trouble), but
not for PDF generation. See `gotchas.md`.

---

## Deploy

```bash
# once
npx wrangler pages project create <project> --production-branch main

# every time
npx wrangler pages deploy site --project-name <project> --branch main --commit-dirty=true
```

**`--branch main` is not optional.** Wrangler infers the environment from your git branch,
and on any other branch it publishes a *preview* alias while production keeps serving the
old build, reporting success either way. Passing `--branch main` forces production.

Print the file list before deploying. Anything sitting in the directory ships.

```bash
find site -type f | sort
```

---

## Custom domain

Two separate steps, and the second one is easy to forget because nothing errors.

**1. Attach the domain to the Pages project.** Wrangler has no command for this, so use the
API. Wrangler's own OAuth token has the necessary scope and is on disk:

```bash
TOK=$(python3 -c "
import re,os
p=os.path.expanduser('~/Library/Preferences/.wrangler/config/default.toml')
print(re.search(r'oauth_token\s*=\s*\"([^\"]+)\"', open(p).read()).group(1))")

curl -s -X POST \
  "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/pages/projects/$PROJECT/domains" \
  -H "Authorization: Bearer $TOK" -H "Content-Type: application/json" \
  --data '{"name":"sub.example.dev"}'
```

It returns `status: initializing`.

**2. Create the DNS record yourself.** Attaching a Pages custom domain does **not** create
it, and the domain sits in `pending` forever precisely because the record is missing.

```bash
./dns.sh add sub CNAME <project>.pages.dev --proxied
```

Workers custom domains *do* self-wire their DNS. Pages ones do not. Do not generalise from
one to the other.

---

## Certificates

Each hostname gets its own certificate and is dead over HTTPS until it has one. Budget up to
about fifteen minutes, though it can be much faster: one hostname answered 200 in ninety
seconds because the edge already had a certificate covering it.

Verify with a loop rather than guessing:

```bash
for i in $(seq 1 40); do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 https://sub.example.dev)
  [ "$code" = "200" ] && { echo "live after ~$((i*30))s"; break; }
  sleep 30
done
```

A 522 during this window is normal and not a misconfiguration.

---

## Confirming the deploy actually landed

Compare bytes, not greps. A grep against the live URL can hit a stale connection and tell
you the deploy failed when it did not.

```bash
LOCAL=$(wc -c < site/index.html)
curl -s "https://sub.example.dev/?cb=$RANDOM" -o /tmp/edge.html
echo "local $LOCAL / edge $(wc -c < /tmp/edge.html)"
diff <(tr -d ' \t' < site/index.html) <(tr -d ' \t' < /tmp/edge.html) && echo identical
```

Also note that Pages serves `index.html` for unknown paths, so a stray file path returning
200 does not mean the file shipped. Check the body for a string only that file contains.

---

## Privacy

The URL is unguessable but public. Anything on the page is readable by anyone with the link,
including any embedded webhook. Do not put an address, a phone number, or a third party's
private business on it, and strip EXIF from every image.

If you want it properly private, Cloudflare Access can put an email gate in front of the
hostname, at the cost of making the recipient sign in. For a birthday page that is usually
the wrong trade.
