from df_engine.core.actor import Actor
from df_engine.core import keywords as kw

strs = strings = {"node": "node"}

dicts = {1: {strs["node"]: 1}}

script = {"flow": dicts[1]}

actor = Actor(
    script,
    ("flow", strings["node"]),
)
