# Building personas

Demographics carry most of the signal: in the paper, removing them cut the
agreement with people from about 90% to 50%. A good persona file is the most
important input.

## Start from the app's real users

Use the app's own numbers, and write down where they came from in `source`:

- Play Console: Statistics (country, device, Android version), and Ratings
  and reviews for language and complaints.
- App Store Connect: App Analytics (territory, device).
- Product analytics: age, city and usage where the app records them.
- Interview notes, support mail and reviews: what real users care about.

For an app with no users yet, describe the intended audience and keep
`calibrated: false`.

## Mix

- 30 to 50 personas. Fewer than 10 is refused by the script.
- Match the real proportions: if 70% of users are in India, about 70% of
  personas are.
- Spread age, income, city size, phone (budget Android, flagship, iPhone),
  free time and current habits (what they use today instead).
- Include people who are unlikely to want the app. A panel of fans ranks
  everything high.

## One persona

One line, concrete, no adjectives that tell the model what to think:

> 24-year-old man, delivery rider in Delhi, low income, cheap Android with little storage

Good fields: age, gender, job, city, income band, phone, one habit that
matters for the app. Do not write "tech-savvy and loves new apps": that decides
the answer for the model.

## File

See [`examples/personas.example.json`](../examples/personas.example.json):

```json
{
  "audience": "urban India smartphone users, 18 to 45",
  "calibrated": false,
  "source": "Play Console statistics 2026-11, 1,200 installs",
  "personas": [{"id": "p01", "description": "..."}]
}
```

`audience` appears in every report. Keep the same file between runs on the same
app so results stay comparable; when you change it, give the file a new name.
