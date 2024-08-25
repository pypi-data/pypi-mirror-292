# Fast blockcheck
Track internet blocking over time

Could be used to: 
- check access to different websites
- to measure accessibility dynamics within some period of time

In contrast to [classic blockcheck](https://github.com/ValdikSS/blockcheck),
does not perform deep analysis, which allows it to work much faster and run
checks literally every minute.

So, if some censorship measurements are being taken right
at the moment, you can track what is happening.

For instance, you notice that some website has got blocked, if you run `fbc`
in repeat mode, you can see when another block happens, and then another one.
This chronological data could be used to determine what exact measurements
are being taken.

## Installation
```shell
pip install fast-blockcheck
```
## Usage
To run one-time check just run program without arguments:
```shell
fbc
```
Sample output:
```text
2024-08-21T21:18:55+01:00: starting test
2024-08-21T21:18:56+01:00: (200) https://en.wikipedia.org
2024-08-21T21:18:59+01:00: (200) https://www.github.com
2024-08-21T21:19:02+01:00: (200) https://www.habr.com
2024-08-21T21:19:05+01:00: (200) https://www.ya.ru
2024-08-21T21:19:08+01:00: (200) https://www.youtube.com
2024-08-21T21:19:09+01:00: (200) https://discord.com
6/6 domains loaded
```

## Features
- Can run in loop
- Structured output, so it is easy to parse for further analysis