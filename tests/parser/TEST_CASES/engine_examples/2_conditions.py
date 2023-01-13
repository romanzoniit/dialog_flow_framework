import re
from dff.script import TRANSITIONS
from dff.script import RESPONSE
import dff.script.conditions as cnd
from dff.pipeline import Pipeline

toy_script = {
    'greeting_flow': {
        'start_node': {
            RESPONSE: '',
            TRANSITIONS: {
                'node1': cnd.exact_match('Hi'),
            },
        },
        'node1': {
            RESPONSE: 'Hi, how are you?',
            TRANSITIONS: {
                'node2': cnd.regexp('.*how are you', re.IGNORECASE),
            },
        },
        'node2': {
            RESPONSE: 'Good. What do you want to talk about?',
            TRANSITIONS: {
                'node3': cnd.all([cnd.regexp('talk'), cnd.regexp('about.*music')]),
            },
        },
        'node3': {
            RESPONSE: 'Sorry, I can not talk about music now.',
            TRANSITIONS: {
                'node4': cnd.regexp(re.compile('Ok, goodbye.')),
            },
        },
        'node4': {
            RESPONSE: 'bye',
            TRANSITIONS: {
                'node1': cnd.any([hi_lower_case_condition, cnd.exact_match('hello')]),
            },
        },
        'fallback_node': {
            RESPONSE: 'Ooops',
            TRANSITIONS: {
                'node1': complex_user_answer_condition,
                'fallback_node': predetermined_condition(True),
            },
        },
    },
}

pipeline = Pipeline.from_script(toy_script, start_label=('greeting_flow', 'start_node'), fallback_label=('greeting_flow', 'fallback_node'))