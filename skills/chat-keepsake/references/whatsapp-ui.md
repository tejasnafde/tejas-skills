# Rendering messages as the real thing

Generic rounded bubbles read as a slideshow. A message block that looks like the actual app
reads as a document, and the recipient recognises it instantly, because it is what their
phone looks like. This is the single highest-return detail in the whole build.

The trick is that the message block should look like a screenshot embedded in an editorial
page. Keep the page around it in your own design language, and make the block itself
faithful.

---

## WhatsApp dark mode

```css
--wa-bg:   #0b141a;   /* chat background            */
--wa-in:   #1f2c34;   /* incoming bubble (them)     */
--wa-out:  #005c4b;   /* outgoing bubble (you)      */
--wa-text: #e9edef;   /* message text, both sides   */
--wa-meta: #8696a0;   /* timestamps, incoming       */
--wa-pill: #182229;   /* the centred date pill      */
--wa-tick: #53bdeb;   /* read receipt blue          */
```

Outgoing timestamps are `rgba(233,237,239,.62)`, not `--wa-meta`.

## WhatsApp light mode

```css
--wa-bg:   #efeae2;
--wa-in:   #ffffff;
--wa-out:  #d9fdd3;
--wa-text: #111b21;
--wa-meta: #667781;
--wa-pill: #ffffff;
--wa-tick: #53bdeb;
```

---

## Geometry

- Bubble radius **8px** (`.5rem`). Not pill-shaped. This is the most common mistake.
- The **first** bubble in a run gets a tail and squares off that corner. Later bubbles in
  the same run from the same sender have no tail and are fully rounded.
- Bubble max width about **84%** of the container.
- Gap **2 to 3px** between messages in a run, about **8px** between runs.
- Message font size around `.9rem`, line-height `1.4`. Use a UI sans, never your body serif.
- Bubble shadow is almost nothing: `0 1px .5px rgba(11,20,26,.5)`.

### The tail

```css
.msg.them.tail .bub { border-top-left-radius: 0; }
.msg.them.tail .bub::before{
  content:""; position:absolute; top:0; left:-8px; width:8px; height:9px;
  background:var(--wa-in); clip-path:polygon(100% 0, 0 0, 100% 100%);
}
.msg.me.tail .bub { border-top-right-radius: 0; }
.msg.me.tail .bub::after{
  content:""; position:absolute; top:0; right:-8px; width:8px; height:9px;
  background:var(--wa-out); clip-path:polygon(0 0, 100% 0, 0 100%);
}
```

### Timestamps

The time sits **inside** the bubble, bottom right, and the text reserves room for it. This
is what makes it look real rather than captioned.

```css
.bub { padding: .36rem 3.35rem .36rem .58rem; }   /* right padding = time gutter */
.msg.me .bub { padding-right: 4.3rem; }           /* outgoing also carries ticks */
.t { position:absolute; right:.5rem; bottom:.24rem; font-size:.56rem;
     display:flex; align-items:center; gap:.16rem; white-space:nowrap; }
```

Reserve more room on outgoing bubbles. If you do not, short messages collide with their own
timestamp, which looks broken and is easy to miss until someone points at it.

For a message long enough to wrap, move the time to its own line instead:

```css
.bub--long { padding-right:.58rem; padding-bottom:1.05rem; }
```

### Ticks

Two check marks in `--wa-tick`, tightly kerned, outgoing only:

```html
<span class="t">6:43 pm <i class="tick">✓✓</i></span>
```
```css
.tick { color:var(--wa-tick); font-size:.62rem; letter-spacing:-.14em; }
```

Only put ticks on outgoing messages. Incoming messages never show them.

### Date pill

Centred, uppercase, small, in `--wa-pill`, at the top of each block. One per block is
enough; you are showing an excerpt, not a whole day.

### Photo albums

Multiple images sent together render as a 2x2 grid inside one bubble with a `+N` overlay on
the fourth tile, radius 5px, 2px gaps, about 11.5rem wide. If you have the real images, use
them. Cropping textbook pages or documents square from the top keeps the readable part.

---

## Markup shape

```html
<div class="chat">
  <div class="chat-date">7 November 2016</div>

  <div class="msg me tail">
    <div class="bub">Can u pls send me chem Chapt ke txtbk ke pics
      <span class="t">6:39 pm <i class="tick">✓✓</i></span></div>
  </div>

  <div class="msg them tail">
    <div class="bub">Pura chapt?<span class="t">6:45 pm</span></div>
  </div>
  <div class="msg them">
    <div class="bub">Questions bhi chahie kya<span class="t">7:01 pm</span></div>
  </div>
</div>
```

`me` and `them` set the side and colour. `tail` marks the first message of a run.

---

## Rules

- **Real timestamps, from the export.** Not approximations. They are visible, so a wrong
  one is a visible lie.
- **Never clean up the text.** Typos, missing punctuation, keysmashes, mixed scripts,
  doubled emoji. The voice is the point. `verify_quotes.py` enforces this by comparing
  against the raw export.
- **Trim the exchange, do not edit it.** Cutting messages from either end is fine. Changing
  what remains is not.
- **Do not stage a screenshot of something that happened last week.** They were there.
- **Match the app they actually use.** If the export is Telegram or iMessage, use those
  colours instead. iMessage: outgoing `#0b93f6` with white text, incoming `#26252a` on
  dark. Telegram outgoing `#8774e1` on dark.
