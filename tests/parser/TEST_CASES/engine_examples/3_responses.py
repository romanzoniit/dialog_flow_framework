from dff.script import TRANSITIONS
from dff.script import RESPONSE
import dff.script.responses as rsp
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
            RESPONSE: rsp.choice(['Hi, what is up?', 'Hello, how are you?']),
            TRANSITIONS: {
                'node2': cnd.exact_match("I'm fine, how are you?"),
            },
        },
        'node2': {
            RESPONSE: 'Good. What do you want to talk about?',
            TRANSITIONS: {
                'node3': cnd.exact_match("Let's talk about music."),
            },
        },
        'node3': {
            RESPONSE: cannot_talk_about_topic_response,
            TRANSITIONS: {
                'node4': cnd.exact_match('Ok, goodbye.'),
            },
        },
        'node4': {
            RESPONSE: upper_case_response('bye'),
            TRANSITIONS: {
                'node1': cnd.exact_match('Hi'),
            },
        },
        'fallback_node': {
            RESPONSE: fallback_trace_response,
            TRANSITIONS: {
                'node1': cnd.exact_match('Hi'),
            },
        },
    },
}

pipeline = Pipeline.from_script(toy_script, start_label=('greeting_flow', 'start_node'), fallback_label=('greeting_flow', 'fallback_node'))