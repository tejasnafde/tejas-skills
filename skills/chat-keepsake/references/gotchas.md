# Gotchas

Every item here was hit for real while building one of these. In build order.

---

## Reading the export

**Sub-agents paraphrase and reorder.** They do not flag it. In one run about one quote in
ten came back with the message order wrong, the speaker wrong, or two exchanges merged
into one. One example: an agent reported a four-message exchange in an order that made the
recipient's kindest line read as a reply to something it did not reply to.

Treat every agent report as a lead. Grep the quote out of the raw export and read twenty
lines around it before it enters a draft. Then run `verify_quotes.py` before every deploy.

**Give each reader its era's peculiarity.** "This year has 43 messages, find out why"
produces a far better report than "read this chunk". The agent hunts instead of summarising.

**Chunk on month boundaries, not year boundaries.** One year can hold a third of a decade's
messages. `parse_chat.py` packs monthly buckets greedily for this reason.

**Continuation lines matter.** A long message wrapped onto multiple lines in the export
will be silently dropped or attributed wrongly by a naive line-by-line parser. Stitch any
line that does not start with a timestamp onto the previous message.

---

## Facts

**Compute who speaks first after each silence, and check the claim you want to make.**
It is tempting to write "you always reached out first". In one archive that was true for
the recent years and false for the two longest silences, which the other person broke.
`parse_chat.py` emits `silence_breakers` so the claim can be checked rather than felt.

**Check outcomes, not just intentions.** A line saying "you were right, I did not buy it"
was false: the chat showed the purchase continuing three messages later, and a follow-up
weeks after that. If the page asserts a result, grep the result.

**Photo timestamps are the cheapest insight available.** Ask for the date of every photo.
Cross-reference against the chat. In one run three of seven turned out to be from days the
two people were together, and the most recent was the last time that ever happened. Nobody
had noticed.

**Beware anachronism.** A line quoted from 2018 sitting in a 2016 chapter reads fine to you
and wrong to the person who lived it. Note the date of everything and place it accordingly.

---

## Tooling

**Chromium will not screenshot taller than 16384px.** Past that the image is silently
truncated, and the blank remainder renders **white**, which fools naive "find the last
non-background row" trimming into reporting the page is longer than it is. Symptoms: the
detected content height is always one pixel below your window height. Use `capture.py`,
which caps the height and offers `--skip N` to hide leading sections so the tail renders.

**A tall capture window destroys `100svh`.** The hero becomes as tall as the window, so a
30000px window gives a 30000px hero and everything else is off-screen. Pin it during
capture only.

**Scroll reveals and timed intros do not survive a naive screenshot.** IntersectionObserver
reveals stay at opacity 0, and a timed sequence is caught mid-fade. Symptom: max pixel
luminance around 40 out of 255 in an otherwise legible design. Pass
`--force-prefers-reduced-motion` and have the page snap to its final state under it.

**`--print-to-pdf` does not wait for webfonts.** The PDF renders in a fallback face and,
worse, two different font choices produce byte-identical PDFs, which is the giveaway. Use
fonts already installed locally. On macOS, good handwriting faces: Bradley Hand,
Noteworthy, Chalkboard, Snell Roundhand, Apple Chancery. Verify by checking that two
variants differ in file size.

**Google Fonts CSS fetched with `curl` returns an HTML interstitial**, not CSS, so you
cannot easily download and inline a woff2 that way. The browser reaches it fine for
on-screen rendering; it is only the shell fetch that fails.

**Do not let a failing glob abort your cleanup.** In zsh, `rm -f prev-*.png` with no
matches raises `no matches found` and the whole command stops, leaving temporary files in
the directory you are about to deploy. Delete named files explicitly, or check first.

**Deploy only what you meant to.** A capture copy left next to `index.html` will be
uploaded. Print the file list before deploying. Note that Cloudflare Pages serves
`index.html` for unknown paths, so a stray path returning 200 does not prove the file
shipped; check the response body for something only that file contains.

**A `<span>` with `width` and `height` is an inline element and browsers ignore both.**
A bar chart built from nested spans renders its tracks and no fills, and it looks like a
JavaScript or specificity problem, so that is where you waste the time. It shipped on a
live page and was only caught by screenshotting that one section deliberately. Set
`display:block` on anything you are sizing. Grid and flex *items* are blockified
automatically, which is why the outer track worked and the inner fill did not.

**Screenshot every section at least once.** A component can be broken for the entire build
and invisible in review, because you scroll past a chart and read the prose. Render each
section on its own and look at it.

---

## Verification

**Byte-compare the deployed page against your local file.** A content grep against a live
URL can hit a stale connection and report old content even when the deployment is correct.
Compare sizes first, then `diff` the whitespace-stripped bodies. In one run a grep said the
deploy had failed when it had in fact succeeded.

**Cache-bust when checking.** Append a random query string. Cloudflare serves
`cache-control: max-age=0, must-revalidate` for Pages HTML, but propagation still takes a
few seconds after a deploy.

---

## Privacy

**Strip EXIF from every image.** Two of four photos in one run carried GPS coordinates for
someone's home. These pages go on public URLs, even if the URL is unguessable.

```python
from PIL import Image
im = Image.open(p).convert("RGB")
clean = Image.new("RGB", im.size)
clean.putdata(list(im.getdata()))          # drops all metadata
clean.save(p, "JPEG", quality=85, optimize=True, progressive=True)
```

**An embedded webhook URL is public.** Anyone with the page can read it out of the source
and post to that channel. Fine for a day; tell the commissioner to delete it afterwards.

**Do not put a third party's private history on the page.** Archives are full of other
people: exes, family, friends' break-ups, someone's therapy. The recipient did not consent
to being written about, and neither did anyone else in there. One draft carried a detail
about a gift bought for a former partner, which was accurate and completely wrong to
include.
