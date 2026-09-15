"""vqapr: author economic decisions, not object graphs.

**The documented surface is the CLI**, and `vqapr.public` is the supported implementation surface
it stands on -- and the one an author writes a strategy, datamodel, exchange or compliance rule
against, aliased once as `from vqapr import public as vq`. Declaring and installing a component is
`vqapr register`; proving a run is ready is `vqapr check`; running it is `vqapr run`.

`vqapr.open()` and the `Project` facade behind it are **gone**. They were the destination of an
earlier design in which `vqapr.public` was the legacy layer to be deleted; a PEP 669 trace of a
complete CLI journey inverted that finding. `docs/design/agent-first-surface.md` records the
measurement and the ruling; the deletion itself is `docs/implementations/124`. `vqapr.authoring`,
a second name for the author's classes, went in 0.16.0 (record `279`): there is one author surface.

The capability import stays lazy so that `import vqapr` stays cheap, and so that a leaf capability
remains importable without dragging heavier layers in behind it --
`tests/boundaries/test_capability_absence.py` enforces exactly that.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # The lazy `__getattr__` below is the runtime door; these are the same names for the checker.
    from vqapr import public

    __version__: str

__all__ = ("public",)

_CAPABILITIES = frozenset({"public"})


def __getattr__(name: str):
    """Resolve capability modules, and `__version__`, on first attribute access."""
    import importlib

    if name == "__version__":
        # The one version answer (record `298`), resolved the way a capability is.
        return importlib.import_module("vqapr._internal.version").package_version()
    if name in _CAPABILITIES:
        module = importlib.import_module(f"vqapr.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module 'vqapr' has no attribute {name!r}")
