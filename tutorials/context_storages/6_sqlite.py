# %% [markdown]
"""
# 6. SQLite

This is a tutorial on using SQLite.
"""


# %%
import pathlib
from platform import system

from dff.context_storages import context_storage_factory

from dff.pipeline import Pipeline
from dff.utils.testing.common import (
    check_happy_path,
    is_interactive_mode,
    run_interactive_mode,
)
from dff.utils.testing.toy_script import TOY_SCRIPT_ARGS, HAPPY_PATH


# %%
pathlib.Path("dbs").mkdir(exist_ok=True)
db_file = pathlib.Path("dbs/sqlite.db")
db_file.touch(exist_ok=True)

separator = "///" if system() == "Windows" else "////"
db_uri = f"sqlite+aiosqlite:{separator}{db_file.absolute()}"
db = context_storage_factory(db_uri)


pipeline = Pipeline.from_script(*TOY_SCRIPT_ARGS, context_storage=db)


# %%
if __name__ == "__main__":
    check_happy_path(pipeline, HAPPY_PATH)
    if is_interactive_mode():
        run_interactive_mode(pipeline)
