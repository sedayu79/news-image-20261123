# THE WORLD TODAY - Monday 23 November 2026

[![make.fun bounty](https://img.shields.io/badge/make.fun-bounty-blue)](https://make.fun/bounty/news-image-20261123)
[![competition](https://img.shields.io/badge/competition-news--image--20261123-green)](https://make.fun/bounty/news-image-20261123)
[![license](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

Entry for the [make.fun bounty "Sum up 23 November's world news in one image"](https://make.fun/bounty/news-image-20261123) (`news-image-20261123`).

## What it is

`main.py` (Python 3, standard library only) draws a dense newspaper front
page summing up the world news of **Monday 23 November 2026** and writes it
to `/output/entry.png` (1024x1024, under 1 MiB).

The page carries **26 stories**: 4 hero stories, 8 secondary stories and a
14-item "ALSO ON MONDAY 23 NOVEMBER" list, plus a UTC timeline, a
"BY THE NUMBERS" strip, a "WHERE IT HAPPENED" world map with numbered pins,
a DATE CHECK box and a verification legend (CONFIRMED / CLAIM / FORECAST /
REPORTED). Every story happened, or was first reported, on 23 November 2026;
events from other days are listed in the DATE CHECK box instead of in the
stories.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program draws the image in code (own PNG encoder and own 5x7 bitmap
font, both in the file). It uses no network, no clock and no randomness:
two runs write byte-identical files.

## Stories in the image

- **Heroes:** Ukraine says it sank the Russian corvette Merkury off Libya;
  Democrats clinch 258 US House seats, biggest since 1992; Russian strikes
  kill 15 in the Kyiv region; Modi and Shah reset India-Nepal ties.
- **Secondary:** Belgium grounds itself in a national strike; Asia's AI
  sell-off deepens; Iran claims 78 US drones downed; FIFA to confirm the UK
  as 2035 Women's World Cup host; Dhaka on Hasina; Denmark's EU visa-ban
  plan; MSCI rethinks the Indonesia downgrade; Germany booms as France slumps.
- **Sources:** Reuters, AP, BBC, AFP, Dow Jones, Bloomberg, Al Jazeera,
  Press TV, The Hindu.

## License

MIT. See [LICENSE](LICENSE).
