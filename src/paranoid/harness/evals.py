"""The one eval call `run` and the pilot cells share. See docs/specs/harness/command.md#run.

`inspect_ai.eval` is called through the module attribute, so the suite can wrap it.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import inspect_ai
from inspect_ai.log import EvalLog

from .models import ModelRow, generate_config
from .task import paranoid

LLM_CONNECTIONS = 4
PROVIDER_CONNECTIONS = {"baseline": 32, "jev": 4, "timestral": 1}  # each provider's own cap


@dataclass(frozen=True)
class EvalCall:
    row: ModelRow
    reasoning: str
    task_args: dict[str, Any]
    log_dir: Path
    limit: int | None = None
    epochs: int | None = None
    model_args: dict[str, Any] = field(default_factory=dict)

    @property
    def max_connections(self) -> int:
        return PROVIDER_CONNECTIONS.get(self.row.kind, LLM_CONNECTIONS)

    def line(self) -> str:
        """One line for --dry-run."""
        args = " ".join(f"{key}={value}" for key, value in self.task_args.items())
        extra = "".join(f" {name}={value}" for name, value in (("limit", self.limit), ("epochs", self.epochs)) if value)
        return f"{self.row.id} reasoning={self.reasoning} {args}{extra} log_dir={self.log_dir}"

    def run(self) -> EvalLog:
        """One eval of the paranoid task. The generate config goes in as keywords, as eval takes no config."""
        config = generate_config(self.row, self.reasoning).model_dump(exclude_none=True)
        logs = inspect_ai.eval(
            paranoid,
            model=self.row.id,
            model_args=self.model_args,
            task_args=self.task_args,
            metadata={"reasoning": self.reasoning, "kind": self.row.kind},
            log_dir=str(self.log_dir),
            limit=self.limit,
            epochs=self.epochs,
            retry_on_error=1,
            max_connections=self.max_connections,
            **config,
        )
        return logs[0]
