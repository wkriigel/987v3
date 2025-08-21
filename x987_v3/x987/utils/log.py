"""Very small logging helpers used by the pipeline.

The real project uses a richer logging framework but for the purposes of the
exercise we just need a couple of convenience functions.  ``info`` retains its
original behaviour while ``step`` and ``ok`` provide light‑weight wrappers so
other modules can signal progress without pulling in additional dependencies.
"""

def info(msg: str) -> None:
    print(msg)


def step(msg: str) -> None:
    """Log the beginning of a pipeline step."""
    info(msg)


def ok(**kwargs) -> None:
    """Log successful completion of a step with optional context."""
    if kwargs:
        parts = " ".join(f"{k}={v}" for k, v in kwargs.items())
        info(parts)
    else:
        info("ok")
