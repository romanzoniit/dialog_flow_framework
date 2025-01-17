# %% [markdown]
"""
# Core: 4. Transitions

This tutorial shows settings for transitions between flows and nodes.
First of all, let's do all the necessary imports from DFF.
"""

# %%
import re

from dff.script import TRANSITIONS, RESPONSE, Context, NodeLabel3Type, Message
import dff.script.conditions as cnd
import dff.script.labels as lbl
from dff.pipeline import Pipeline
from dff.utils.testing.common import (
    check_happy_path,
    is_interactive_mode,
    run_interactive_mode,
)

# %% [markdown]
"""
Let's define the functions with a special type of return value:

    NodeLabel3Type == tuple[str, str, float]

which means that transition returns a `tuple`
with flow name, node name and priority.
"""


# %%
def greeting_flow_n2_transition(_: Context, __: Pipeline, *args, **kwargs) -> NodeLabel3Type:
    return ("greeting_flow", "node2", 1.0)


def high_priority_node_transition(flow_label, label):
    def transition(_: Context, __: Pipeline, *args, **kwargs) -> NodeLabel3Type:
        return (flow_label, label, 2.0)

    return transition


# %% [markdown]
"""
Priority is needed to select a condition
in the situation where more than one condition is `True`.
All conditions in `TRANSITIONS` are being checked.
Of the set of `True` conditions,
the one that has the highest priority will be executed.
Of the set of `True` conditions with largest
priority the first met condition will be executed.

Out of the box `dff.script.core.labels`
offers the following methods:

* `lbl.repeat()` returns transition handler
    which returns `NodeLabelType` to the last node,

* `lbl.previous()` returns transition handler
    which returns `NodeLabelType` to the previous node,

* `lbl.to_start()` returns transition handler
    which returns `NodeLabelType` to the start node,

* `lbl.to_fallback()` returns transition
    handler which returns `NodeLabelType` to the fallback node,

* `lbl.forward()` returns transition handler
    which returns `NodeLabelType` to the forward node,

* `lbl.backward()` returns transition handler
    which returns `NodeLabelType` to the backward node.

There are three flows here: `global_flow`, `greeting_flow`, `music_flow`.
"""

# %%
toy_script = {
    "global_flow": {
        "start_node": {  # This is an initial node,
            # it doesn't need a `RESPONSE`.
            RESPONSE: Message(),
            TRANSITIONS: {
                ("music_flow", "node1"): cnd.regexp(r"talk about music"),  # first check
                ("greeting_flow", "node1"): cnd.regexp(r"hi|hello", re.IGNORECASE),  # second check
                "fallback_node": cnd.true(),  # third check
                # "fallback_node" is equivalent to
                # ("global_flow", "fallback_node").
            },
        },
        "fallback_node": {  # We get to this node if
            # an error occurred while the agent was running.
            RESPONSE: Message(text="Ooops"),
            TRANSITIONS: {
                ("music_flow", "node1"): cnd.regexp(r"talk about music"),  # first check
                ("greeting_flow", "node1"): cnd.regexp(r"hi|hello", re.IGNORECASE),  # second check
                lbl.previous(): cnd.regexp(r"previous", re.IGNORECASE),  # third check
                # lbl.previous() is equivalent
                # to ("previous_flow", "previous_node")
                lbl.repeat(): cnd.true(),  # fourth check
                # lbl.repeat() is equivalent to ("global_flow", "fallback_node")
            },
        },
    },
    "greeting_flow": {
        "node1": {
            RESPONSE: Message(text="Hi, how are you?"),
            # When the agent goes to node1, we return "Hi, how are you?"
            TRANSITIONS: {
                (
                    "global_flow",
                    "fallback_node",
                    0.1,
                ): cnd.true(),  # second check
                "node2": cnd.regexp(r"how are you"),  # first check
                # "node2" is equivalent to ("greeting_flow", "node2", 1.0)
            },
        },
        "node2": {
            RESPONSE: Message(text="Good. What do you want to talk about?"),
            TRANSITIONS: {
                lbl.to_fallback(0.1): cnd.true(),  # third check
                # lbl.to_fallback(0.1) is equivalent
                # to ("global_flow", "fallback_node", 0.1)
                lbl.forward(0.5): cnd.regexp(r"talk about"),  # second check
                # lbl.forward(0.5) is equivalent
                # to ("greeting_flow", "node3", 0.5)
                ("music_flow", "node1"): cnd.regexp(r"talk about music"),  # first check
                # ("music_flow", "node1") is equivalent
                # to ("music_flow", "node1", 1.0)
                lbl.previous(): cnd.regexp(r"previous", re.IGNORECASE),  # third check
            },
        },
        "node3": {
            RESPONSE: Message(text="Sorry, I can not talk about that now."),
            TRANSITIONS: {lbl.forward(): cnd.regexp(r"bye")},
        },
        "node4": {
            RESPONSE: Message(text="Bye"),
            TRANSITIONS: {
                "node1": cnd.regexp(r"hi|hello", re.IGNORECASE),  # first check
                lbl.to_fallback(): cnd.true(),  # second check
            },
        },
    },
    "music_flow": {
        "node1": {
            RESPONSE: Message(
                text="I love `System of a Down` group, would you like to talk about it?"
            ),
            TRANSITIONS: {
                lbl.forward(): cnd.regexp(r"yes|yep|ok", re.IGNORECASE),
                lbl.to_fallback(): cnd.true(),
            },
        },
        "node2": {
            RESPONSE: Message(
                text="System of a Down is an Armenian-American heavy metal band formed in 1994."
            ),
            TRANSITIONS: {
                lbl.forward(): cnd.regexp(r"next", re.IGNORECASE),
                lbl.repeat(): cnd.regexp(r"repeat", re.IGNORECASE),
                lbl.to_fallback(): cnd.true(),
            },
        },
        "node3": {
            RESPONSE: Message(
                text="The band achieved commercial success with the release of five studio albums."
            ),
            TRANSITIONS: {
                lbl.forward(): cnd.regexp(r"next", re.IGNORECASE),
                lbl.backward(): cnd.regexp(r"back", re.IGNORECASE),
                lbl.repeat(): cnd.regexp(r"repeat", re.IGNORECASE),
                lbl.to_fallback(): cnd.true(),
            },
        },
        "node4": {
            RESPONSE: Message(text="That's all what I know."),
            TRANSITIONS: {
                greeting_flow_n2_transition: cnd.regexp(r"next", re.IGNORECASE),  # second check
                high_priority_node_transition("greeting_flow", "node4"): cnd.regexp(
                    r"next time", re.IGNORECASE
                ),  # first check
                lbl.to_fallback(): cnd.true(),  # third check
            },
        },
    },
}

# testing
happy_path = (
    (Message(text="hi"), Message(text="Hi, how are you?")),
    (Message(text="i'm fine, how are you?"), Message(text="Good. What do you want to talk about?")),
    (
        Message(text="talk about music."),
        Message(text="I love `System of a Down` group, would you like to talk about it?"),
    ),
    (
        Message(text="yes"),
        Message(text="System of a Down is an Armenian-American heavy metal band formed in 1994."),
    ),
    (
        Message(text="next"),
        Message(
            text="The band achieved commercial success with the release of five studio albums."
        ),
    ),
    (
        Message(text="back"),
        Message(text="System of a Down is an Armenian-American heavy metal band formed in 1994."),
    ),
    (
        Message(text="repeat"),
        Message(text="System of a Down is an Armenian-American heavy metal band formed in 1994."),
    ),
    (
        Message(text="next"),
        Message(
            text="The band achieved commercial success with the release of five studio albums."
        ),
    ),
    (Message(text="next"), Message(text="That's all what I know.")),
    (Message(text="next"), Message(text="Good. What do you want to talk about?")),
    (Message(text="previous"), Message(text="That's all what I know.")),
    (Message(text="next time"), Message(text="Bye")),
    (Message(text="stop"), Message(text="Ooops")),
    (Message(text="previous"), Message(text="Bye")),
    (Message(text="stop"), Message(text="Ooops")),
    (Message(text="nope"), Message(text="Ooops")),
    (Message(text="hi"), Message(text="Hi, how are you?")),
    (Message(text="stop"), Message(text="Ooops")),
    (Message(text="previous"), Message(text="Hi, how are you?")),
    (Message(text="i'm fine, how are you?"), Message(text="Good. What do you want to talk about?")),
    (
        Message(text="let's talk about something."),
        Message(text="Sorry, I can not talk about that now."),
    ),
    (Message(text="Ok, goodbye."), Message(text="Bye")),
)

# %%
pipeline = Pipeline.from_script(
    toy_script,
    start_label=("global_flow", "start_node"),
    fallback_label=("global_flow", "fallback_node"),
)

if __name__ == "__main__":
    check_happy_path(pipeline, happy_path)
    if is_interactive_mode():
        run_interactive_mode(pipeline)
