# Сборка статьи №6 «Собор» — strasbourg-cathedral

Файлы кладутся в корень `strasbourgwalk/` с заменой.

- `render_article.py` — добавлена запись `strasbourg-cathedral` в CONFIG (hero, крошки, кнопки, картинки, карточка аудиогида перед «How to buy tickets», финальный баннер). Больше ничего в файле не менялось.
- `drafts/06-cathedral.md` — утверждённый английский мастер.
- `tr_strasbourg-cathedral.json` — карта перевода статьи на 7 языков (fr, de, es, it, pt, pl, ru), собрана из вычитанных текстов.
- `drafts/06-cathedral-<lang>.md` — исходные тексты переводов, для справки; генератор их не читает.

## Команды

```
python3 render_article.py drafts/06-cathedral.md
python3 gen_article.py strasbourg-cathedral
python3 gen.py
python3 gen_guides.py
python3 check_links.py
```

`gen_article.py` должен напечатать по каждому языку `OK … no-match=0 english-left=none`.
`check_links.py` должен вернуть 0. Только после этого — коммит и пуш.

## Что проверено до передачи

- Все 124–125 ключей карты на каждом языке находятся в отрендеренной английской странице (no-match = 0).
- После подстановки в тексте статьи не осталось английских фраз. Английскими остаются только общие блоки шаблона (карточка аудиогида, блок автора, раскрытие, заголовки «Frequently asked questions» / «Continue exploring») — их переводит общая карта `tr_<lang>.json`, как на уже опубликованных страницах.
