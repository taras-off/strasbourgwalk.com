# LOCALIZATION BRIEF — strasbourgwalk.com landing page

You are localizing the landing page of a niche travel-guide site about Strasbourg into ONE language.

## The one rule that matters

**This is localization, not translation.** We do not translate words — we retell the meaning and the
feeling the way a living local author-guide would say it in that language. A good localized text reads
as if it had been written in that language from the start.

Test: read the sentence aloud. If you got bored, stumbled, or yawned — cut it and rewrite.
If a word can be removed without changing the meaning, remove it.

- **Short sentences. Vary the rhythm.** A long clause-stacked sentence becomes two or three short ones.
- One idea per sentence. Do not glue two ideas together with "while", "moreover", "at the same time".
- Active voice, strong verbs. Kill "is located", "is considered", "represents", "it should be noted".
- **Show, don't tell.** Keep the concrete detail, drop the empty adjective.
- Address the reader directly, in the register that language uses for a friendly guide:
  RU — «вы» со строчной · DE — Sie · FR — vous · ES — usted · IT — Lei/voi as natural · PT — você · PL — Pan/Pani formal but warm.
  Hold the same register through the whole file.
- Idioms are NOT translated literally. Use the target language's own equivalent, or drop it.
- **Russian and German run longer than English — fight it.** Cut participial constructions, doubled
  words and filler. The localized text is usually SHORTER than the original, never padded.

**Banned in every language** — the local equivalents of: hidden gem, must-see, nestled, jewel/pearl,
"in the heart of", "steeped in history", "will not leave you indifferent", "immerse yourself in the
atmosphere", "a paradise corner". If you cannot make it sound good without a cliché, you need a
concrete detail instead of an epithet.

## Facts that must be carried over EXACTLY — never "localized"

Numbers, prices, opening hours, dates, step counts, distances and years. Copy them precisely:
€9.99 · €10 · €6 · €3 · €2 · €16.20 · €7.50 · €16 · €20 · €5 · €32 · 330 steps · 66 m · 142 m ·
33 stops · 8 languages · 2.5 hours · 12:30 · 11:30 · 08:30–11:15 · 12:45–17:45 · 14:00–17:15 ·
09:30–20:00 · 10:00–18:00 · 1 h 45 · 19 trains · 1570 · 1262 · 1681 · 1871 · 1918 · 1940 · 1944 ·
1518 · 1439 · 1647–1874 · 227 years · 4,664 travellers · 5.0 · 7 reviews · 1 June 2028.

Adapt only the *format* to the language: decimal comma where the language uses one (€9,99 in FR/DE/ES/IT/PT/PL/RU),
thousands separator per local convention (4 664 in FR/RU/PL, 4.664 in DE/ES/IT/PT), 24-hour clock everywhere.

**The GPS sentence must stay factually exact in every language:** the offline GPS map SHOWS WHERE YOU ARE,
but the visitor STARTS EACH RECORDING THEMSELVES at the spot. Never write that it plays automatically.

**Proper nouns.** Keep the French forms and add the local form only where that language normally does:
Strasbourg · Petite France · Grande Île · Barrage Vauban · Ponts Couverts · Place Kléber ·
Place Gutenberg · Place Broglie · Palais Rohan · Kammerzell · Christkindelsmärik · Neustadt · the Ill.
In Russian, transliterate with the original in brackets on first mention, then transliteration only:
Страсбург, Пти-Франс (Petite France), Гранд-Иль, плотина Вобана.

## Markup rules — break these and the build breaks

Each key in the JSON is a string taken straight out of the HTML. Some contain inline markup.

1. **Keep every HTML tag exactly as it appears in the key**, in the same order, with identical
   attributes: `<strong>`, `<em>`, `<span class="ln">`, `<a href="…">…</a>`, `<br>`.
   Translate only the human-readable text between the tags. Never touch a `href` value.
2. Keep HTML entities as they are: `&amp;` `&euro;` `&rarr;` `&nbsp;` `&mdash;`.
3. Keep the arrow `→` and the bullet `·` characters where they appear.
4. Keys that are a single UI word (`EN`, `FR`, `DE`…) are language-switcher labels — **return them unchanged**.
5. The key `Guides ▾` keeps the ▾ character; translate only the word.
6. The brand string `Strasbourg<i>Walk</i>` is a wordmark — **return it unchanged in every language**.
7. Do not add, remove or reorder keys. The output JSON must have exactly the same keys as the input.

## Length limits on two keys

- The `<title>` string must stay **≤ 60 characters including " | TouringBee"**.
- The meta description must land between **150 and 158 characters**.
Count them. These two are the only keys with a hard character budget; if the natural translation
overruns, rewrite it shorter rather than exceeding the limit.

## Your job

1. Read `/home/claude/site/strings_en.json`. It has 215 keys; every value is an empty string.
2. Write the localized text into each value.
3. Save the result as `/home/claude/site/tr_<lang>.json` — same keys, filled values, UTF-8, no BOM.
4. Verify before you finish:
   - every key present, no empty value
   - no English words left in any value (watch for false friends that are genuinely correct in the
     target language — those are fine)
   - tag counts match between key and value for every key containing `<`
   - title ≤ 60 chars, meta description 150–158 chars
5. Return only: the language, the number of keys filled, the title and meta-description character
   counts, and anything you deliberately reworded rather than translated. Do not paste the JSON.
