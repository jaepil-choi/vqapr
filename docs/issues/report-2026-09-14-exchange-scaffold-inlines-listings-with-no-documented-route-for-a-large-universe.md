# The exchange scaffold writes every listing as a literal taken from `--instruments`, and nothing documents the `config:` route that a whole-market universe needs

**Status: UNTRIAGED — reported by testbed, not yet judged by the owner.**

| | |
|---|---|
| vqapr version | `0.16.0` |
| installed from | `../../vqapr/dist/vqapr-0.16.0-py3-none-any.whl` (built from tag `v0.16.0`) |
| reported | 2026-09-14 |
| reporter | `kaist-thesis/vqapr-scenario-testbed`, run 4 (FF3 factor scenario), evaluator-verified |
| python / OS | 3.12.13 / Windows 11 |

**Related:** no earlier report found. `vqapr-make-strategy/references/factor-portfolios.md:51` says a strategy has no config channel; this is the exchange side.

## What I was doing

The run 4 factor legs trade every KOSPI/KOSDAQ common stock in the price table on a frictionless
academic venue, with divisible, long-only listings. That is a couple of thousand names per June
universe. Every traded name needs a listing on the venue, so the agent needed a way to list a few
thousand ids.

## What I expected

`vqapr-make-exchange/SKILL.md`, lines 19–30, sends the user to the scaffold: `vqapr new exchange
<id> --instruments A005930 A000660 --out venue.py`. It then says "**Every instrument the run trades
needs a listing here**, or preflight refuses it by name." The scaffold's module docstring says
"Edit the listing set below". I expected the scaffold or the skill to say how to supply that set
when it runs to thousands of names.

## What happened

The original run (`FINDINGS.md`, F-005): "the exchange scaffold writes each id as a literal inside
`Venue.__init__` (`"A005930": _rule("A005930"),`), fed by `--instruments` on the command line; the
sample instead takes `instruments` as a constructor argument filled from the YAML's `config:`. …
neither the scaffold comment nor the make-exchange skill mentions the `config:` route for listings
(the skill shows `config:` only for rates)." The agent resolved it by guess and copied the sample.

I checked this again on 0.16.0:

    $ uv run vqapr --project-root . new exchange ff-venue --profile academic --instruments A005930 A000660 --out exch/ff_venue.py
    {"declaration": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\exch\\ff_venue.yaml", "kind": "exchange", "ok": true, "path": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1\\exch\\ff_venue.py", "stage": "template.new", "workspace_root": "C:\\Users\\최재필\\AppData\\Local\\Temp\\claude\\D--chljeffreyz-DevProjects-kaist-thesis\\34d7bcbd-efcb-4623-8d58-06ac84dc2c3d\\scratchpad\\verify-v1"}

`ff_venue.py`, lines 48–52:

```python
    def __init__(self) -> None:
        super().__init__(listings={
        "A005930": _rule("A005930"),
        "A000660": _rule("A000660"),
        })
```

`ff_venue.yaml` has no `config:`. It declares only `kind: exchange`, `path: ff_venue.py` and
`object_name: Venue`.

- **The `krx` scaffold does the same.** `--profile krx` writes the ids as an inline module
  constant (`INSTRUMENTS = ("K000001", "K000002", ...)`).
- **`vqapr new --help`** documents the flag only as "instrument ids to list on a new exchange
  (defaults to two placeholders)".
- **The other route exists, and works.** The `vqapr new sample` `exchange.py` takes `def
  __init__(self, instruments: Sequence[str])`, and `sample.yaml` fills it from `config:
  instruments: [K000001, …]`. The run 4 legs used that pattern, and all of them completed.
- **No skill describes it for listings.**
  - `config` appears in `vqapr-make-exchange/SKILL.md` only for `KrxExchange` rates, at lines
    55–77: "`KrxExchange` takes its rates as constructor arguments, so a registration sets them
    from `config:`".
  - The strategy side says the opposite: `vqapr-make-strategy/references/factor-portfolios.md:51`,
    "there is no config channel".

## Reproduction

1. `uv run vqapr new exchange ff-venue --profile academic --instruments A005930 A000660 --out ff_venue.py`.
   The listings come out as literals and the `.yaml` has no `config:`.
2. `uv run vqapr new exchange krx-venue --profile krx --instruments K000001 K000002 --out krx_venue.py`.
   The ids come out as an inline tuple.
3. `uv run vqapr new sample --out ./sample`. Its `exchange.py` and `sample.yaml` use a constructor
   argument filled from `config:`.
4. Search the installed skills for `config`. There is no listing route.

Reproduced 1 of 1 attempts. Deterministic.

## Impact

Worked around by guess, at a cost of a few minutes and no change to any result. The agent had
happened to read the sample.

A user who starts from the scaffold, as the skill says to, has two options for a whole-market
universe:

- a command line carrying thousands of ids;
- a generated `.py` file.

Neither is described either.

## What would have prevented it

A line in the scaffold's docstring or in `vqapr-make-exchange/SKILL.md`: "for a large universe,
take `instruments` as a constructor argument and list them under `config:` in the registration, as
`vqapr new sample`'s `exchange.py` does."
