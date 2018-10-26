#!/usr/bin/env python3
"""A tag-based chatbot framework."""

import re
from collections import Counter

import time


class ChatBot:
    """A tag-based chatbot framework

    This class is not meant to be instantiated. Instead, it provides helper
    functions that subclasses could use to create a tag-based chatbot. There
    are two main components to a chatbot:

    * A set of STATES to determine the context of a message.
    * A set of TAGS that match on words in the message.

    Subclasses must implement two methods for every state (except the
    default): the `on_enter_*` method and the `respond_from_*` method. For
    example, if there is a state called "confirm_delete", there should be two
    methods `on_enter_confirm_delete` and `respond_from_confirm_delete`.

    * `on_enter_*()` is what the chatbot should say when it enters a state.
        This method takes no arguments, and returns a string that is the
        chatbot's response. For example, a bot might enter the "confirm_delete"
        state after a message to delete a reservation, and the
        `on_enter_confirm_delete` might return "Are you sure you want to
        delete?".

    * `respond_from_*()` determines which state the chatbot should enter next.
        It takes two arguments: a string `message`, and a dictionary `tags`
        which counts the number of times each tag appears in the message. This
        function should always return with calls to either `go_to_state` or
        `finish`.

    The `go_to_state` method automatically calls the related `on_enter_*`
    method before setting the state of the chatbot. The `finish` function calls
    a `finish_*` function before setting the state of the chatbot to the
    default state.

    The TAGS class variable is a dictionary whose keys are words/phrases and
    whose values are (list of) tags for that word/phrase. If the words/phrases
    match a message, these tags are provided to the `respond_from_*` methods.
    """

    STATES = []
    TAGS = {}

    def __init__(self, default_state):
        """Initialize a Chatbot.

        Arguments:
            default_state (str): The starting state of the agent.
        """
        if default_state not in self.STATES:
            print(' '.join([
                f'WARNING:',
                f'The default state {default_state} is listed as a state.',
                f'Perhaps you mean {self.STATES[0]}?',
            ]))
        self.default_state = default_state
        self.state = self.default_state
        self.tags = {}
        self._check_states()
        self._check_tags()

    def _check_states(self):
        """Check the STATES to make sure that relevant functions are defined."""
        for state in self.STATES:
            prefixes = []
            if state != self.default_state:
                prefixes.append('on_enter')
            prefixes.append('respond_from')
            for prefix in prefixes:
                if not hasattr(self, f'{prefix}_{state}'):
                    print(' '.join([
                        f'WARNING:',
                        f'State "{state}" is defined',
                        f'but has no response function self.{prefix}_{state}',
                    ]))

    def _check_tags(self):
        """Check the TAGS to make sure that it has the correct format."""
        for phrase in self.TAGS:
            tags = self.TAGS[phrase]
            if isinstance(tags, str):
                self.TAGS[phrase] = [tags]
            tags = self.TAGS[phrase]
            assert isinstance(tags, (tuple, list)), ' '.join([
                'ERROR:',
                'Expected tags for {phrase} to be str or List[str]',
                f'but got {tags.__class__.__name__}',
            ])

    def go_to_state(self, state):
        """Set the chatbot's state after responding appropriately.

        Arguments:
            state (str): The state to go to.

        Returns:
            str: The response of the chatbot.
        """
        assert state in self.STATES, f'ERROR: state "{state}" is not defined'
        assert state != self.default_state, ' '.join([
            'WARNING:',
            f"do not call `go_to_state` on the default state {self.default_state};",
            f'use `finish` instead',
        ])
        on_enter_method = getattr(self, f'on_enter_{state}')
        response = on_enter_method()
        self.state = state
        return response

    def chat(self):
        """Start a chat with the chatbot."""
        try:
            message = input('> ')
            while message.lower() not in ('exit', 'quit'):
                print()
                print(f'{self.__class__.__name__}: {self.respond(message)}')
                print()
                message = input('> ')
        except (EOFError, KeyboardInterrupt):
            print()
            exit()

    def respond(self, message):
        """Respond to a message.

        Arguments:
            message (str): The message from the user.

        Returns:
            str: The response of the chatbot.
        """
        respond_method = getattr(self, f'respond_from_{self.state}')
        return respond_method(message, self._get_tags(message))

    def finish(self, manner):
        """Set the chatbot back to the default state

        This function will call the appropriate `finish_*` method.

        Arguments:
            manner (str): The type of exit from the flow.

        Returns:
            str: The response of the chatbot.
        """
        response = getattr(self, f'finish_{manner}')()
        self.state = self.default_state
        return response

    def _get_tags(self, message):
        """Find all tagged words/phrases in a message.

        Arguments:
            message (str): The message from the user.

        Returns:
            Dict[str, int]: A count of each tag found in the message.
        """
        counter = Counter()
        msg = message.lower()
        for phrase, tags in self.TAGS.items():
            if re.search(r'\b' + phrase.lower() + r'\b', msg):
                counter.update(tags)
        return counter


class OxyCSBot(ChatBot):
    """A simple chatbot that directs students to office hours of CS professors."""

    STATES = [
        'waiting',
        'specific_faculty',
        'unknown_faculty',
        'unrecognized_faculty',
        'why_sad',
        'talk_to_professors',
        'other_factors'
        'need_help',
        'greeting',
        'clubs',
        'suicidal_response_friends',
        'anxious_breathe'
    ]

    TAGS = {

        'help': 'help',
        'hi': 'hi',
        'hello':'hi',
        'howdy': 'hi',
        "what's up": 'hi',

        # sad
        "sad": "sad",
        'hate': 'sad',
        'depressed': "sad",
        'disappointed': "sad",
        'miss': "sad",
        'hopeless': "sad",
        'disinterested': "sad",
        'empty': 'sad',
        'life is meaningless': 'sad',
        'no point in': 'sad',
        'not good': 'sad',
        'emotional': 'sad',

        # anxious
        "future": "anxious",
        "career": "anxious",
        "anxious": "anxious",
        "worried": "anxious",
        "nervous": "anxious",
        "restless": "anxious",
        "agitated": "anxious",
        "life": "anxious",
        "uneasy": "anxious",
        "troubled": "anxious",

        # failing academics
        "test": "failing academics",
        "midterm": "failing academics",
        "exams": "failing academics",
        "gpa": "failing academics",
        "classes": "failing academics",
        "disappointed": "failing academics",
        "work": "failing academics",
        "assignment": "failing academics",
        "grades": "failing academics",
        "frustrated": "failing academics",
        "annoyed": "failing academics",
        "efforts": "failing academics",
        "quit school": "failing academics",

        # social isolation
        "disconnected": "social isolation",
        "lonely": "social isolation",
        "no friends": "social isolation",
        "homesick": "social isolation",
        "don't have": "social isolation",
        "alone": "social isolation",
        "friendless": "social isolation",
        "abandoned": "social isolation",
        "care about me": "social isolation",
        "not cared for": "social isolation",
        "failing": "social isolation",

        # suicidal
        "die": "suicidal",
        "kill myself": "suicidal",
        "killed": "suicidal",
        "life": "suicidal",
        "death": "suicidal",
        "end": "suicidal",
        "commit": "suicidal",
        "feel": "suicidal",
        "useless": "suicidal",
        "worthless": "suicidal",
        "no purpose": "suicidal",
        "alive": "suicidal",

        # health issues
        "sick": "health issues",
        "don't feel well": "health issues",
        "dizzy": "health issues",
        "tired": "health issues",
        "migraine": "health issues",
        "nausea": "health issues",
        "nauseous": "health issues",
        "aches": "health issues",
        "stomachache": "health issues",

        # difficult courses
        "hard time": "difficult courses",
        "don't understand": "difficult courses",
        "material": "difficult courses",
        "hard": "difficult courses",
        "difficult": "difficult courses",
        "I'm behind": "difficult courses",
        "trouble": "difficult courses",
        "helpless": "difficult courses",

        # overload
        "too much": "courses overload",
        "overwhelming": "courses overload",
        "demanding": "courses overload",
        "so much": "courses overload",
        "overwhelmed": "courses overload",
        "burdened": "courses overload",
        "exhausted": "courses overload",
        "excessive": "courses overload",
        "overloading": "courses overload",
        "crazy": "courses overload",
        "intense": "courses overload",
        "so done": "courses overload",

        # professors
        'kathryn': 'kathryn',
        'leonard': 'kathryn',
        'justin': 'justin',
        'li': 'justin',
        'jeff': 'jeff',
        'miller': 'jeff',
        'celia': 'celia',
        'hsing-hau': 'hsing-hau',

        # generic
        'thanks': 'thanks',
        'thank you': 'thanks',
        'ty': 'thanks',
        'ok': 'success',
        'okie': 'success',
        'okay': 'success',
        'sure': 'success',
        'bye': 'success',
        'yes': 'yes',
        'ya': 'yes',
        'yep': 'yes',
        'no': 'no',
        'nope': 'no',
        'not really': 'no',
        'nah': 'no',
        'no thanks': 'no',
        'idk': 'idk',
        'not sure': 'idk',
        "don't know": 'idk'

    }

    PROFESSORS = [
        'celia',
        'hsing-hau',
        'jeff',
        'justin',
        'kathryn',
    ]

    def __init__(self):
        """Initialize the OxyCSBot.

        The `professor` member variable stores whether the target
        professor has been identified.
        """
        super().__init__(default_state='waiting')

    def respond_using(self, state, message):
        respond_method = getattr(self, f'respond_from_{state}')
        return respond_method(message, self._get_tags(message))

    # "waiting" state functions

    def respond_from_waiting(self, message, tags):

        if "sad" in tags:
            return self.go_to_state('why_sad')
        elif "suicidal" in tags:
            return self.go_to_state('suicidal_response_friends')
        elif "anxious" in tags:
            return self.go_to_state('anxious_breathe')
        elif "thanks" in tags:
            return self.finish("thanks")
        elif "idk" in tags:
            return self.go_to_state("why_sad")
        elif "help" or "hi" in tags:
            return self.go_to_state('greeting')
        else:
            return tags
        # FIXME add in anxious, idk,

    # greeting state functions

    def on_enter_greeting(self):
        return "I am here to help! How are you feeling today?"

    def respond_from_greeting(self, message, tags):
        return self.respond_using("waiting", message)

    # anxious_breath state functions

    def on_enter_anxious_breathe(self):
        return '\n'.join([
            "You must be feeling overwhelmed right now.",
            "Let's pull ourselves into the present.",
            "Please close your eyes and take 3 huge breaths."
            "Do you feel better?"
        ])

    def respond_from_anxious_breathe(self, message, tags):
        if "yes" in tags:
            return self.finish("success")
        elif "no" or "idk" in tags:
            return self.go_to_state("why_sad")

    # suicidal_response_friends state functions

    def on_enter_suicidal_response_friends(self):
        return '\n'.join([
            "I'm sorry... you must be going through a lot."
            "It's tough going through them alone."
            "Do you have any friends, family, or anyone you can talk to right now?"
        ])

    def respond_from_suicidal_response_friends(self, message, tags):
        if "idk" in tags:
            return self.finish('hotline_idk')
        elif "no" in tags:
            return self.finish('hotline')
        elif "yes" in tags:
            return self.finish('talk_to_friends')

    # "why_sad" state functions

    def on_enter_why_sad(self):
        response = '\n'.join([
            "Hmm, I'm sorry to hear that.",
            "What is on your mind?",
        ])
        return response

    def respond_from_why_sad(self, message, tags):
        if "failing academics" in tags:
            return self.go_to_state('talk_to_professors')
        elif "social isolation" in tags:
            return self.go_to_state('clubs')
        else:
            return self.finish('confused')
        # FIXME add in specific_event, suicidal

    # clubs state functions

    def on_enter_clubs(self):
        response = '\n'.join([
            "I'm sorry to hear that.",
            "School can be a very daunting experience for many people. You are not alone in this.",
            "One of the best and easiest ways to make friends or to feel more connected is to join a club.",
            "Do you have any interests? Would you be interested in joining a club?"
        ])

        return response

    def respond_from_clubs(self, message, tags):
        if 'no' in tags:
            return self.go_to_state('why_not')
        elif 'yes' in tags:
            return self.finish('join_clubs')
        elif 'idk' in tags:
            return self.finish('should_join_club')
        # FIXME need else

    # why_not state fucntions

    def on_enter_why_not(self):
        return "Hmm, I see. Why not, if I might ask?"

    def respond_from_why_not(self, message, tags):
        # FIXME paste in content of respond_from_why_sad and respond_from_why_anxious when it's finished
        return "FIXME"

    # talk_to_professors state functions

    def on_enter_talk_to_professors(self):
        response = '\n'.join([
            "Handling school is very tough. I can't imagine what you're going through.",
            "Have you tried reaching out to any professor or tutoring services available at your school?"
        ])

        return response

    def respond_from_talk_to_professors(self, messsage, tags):
        if 'no' in tags:
            return self.finish('talk_to_them')
        elif 'yes' in tags:
            return self.go_to_state('other_factors')
        else:
            return self.finish('fail')

    # "other_factors" state functions

    def on_enter_other_factors(self):
        response = '\n'.join([
            "I'm so proud of you for reaching out for resources!",
            "That's a hard thing to do. I'm sorry that it hasn't helped",
            "Maybe there are other factors that might affecting your academic life.",
            "Can you think of other reasons why you might be struggling?"
        ])

        return response

    def respond_from_other_factors(self, message, tags):
        if 'health issues' in tags:
            return self.finish('health_resources')
        elif "difficult courses" in tags:
            return self.finish('academic_resources')
        elif "courses overload" in tags:
            return self.finish('course_overload_response')
        # FIXME add why_sad responses

    # "specific_faculty" state functions

    def on_enter_specific_faculty(self):
        response = '\n'.join([
            f"{self.professor.capitalize()}'s office hours are {self.get_office_hours(self.professor)}",
            'Do you know where their office is?',
        ])
        return response

    def respond_from_specific_faculty(self, message, tags):
        if 'yes' in tags:
            return self.finish('success')
        else:
            return self.finish('location')

    # "unknown_faculty" state functions

    def on_enter_unknown_faculty(self):
        return "Who's office hours are you looking for?"

    def respond_from_unknown_faculty(self, message, tags):
        for professor in self.PROFESSORS:
            if professor in tags:
                self.professor = professor
                return self.go_to_state('specific_faculty')
        return self.go_to_state('unrecognized_faculty')

    # "unrecognized_faculty" state functions

    def on_enter_unrecognized_faculty(self):
        return ' '.join([
            "I'm not sure I understand - are you looking for",
            "Celia, Hsing-hau, Jeff, Justin, or Kathryn?",
        ])

    def respond_from_unrecognized_faculty(self, message, tags):
        for professor in self.PROFESSORS:
            if professor in tags:
                self.professor = professor
                return self.go_to_state('specific_faculty')
        return self.finish('fail')

    # "finish" functions

    def finish_confused(self):
        return "CONFUSED"

    def finish_location(self):
        return f"{self.professor.capitalize()}'s office is in {self.get_office(self.professor)}"

    def finish_success(self):
        return 'Great, let me know if you need anything else!'

    def finish_fail(self):
        return "I've tried my best but I still don't understand. Maybe try asking other students?"

    def finish_thanks(self):
        return "You're welcome!"

    def finish_checkpoint(self):
        return "CHECKPOINT BABY"

    def finish_talk_to_them(self):
        return '\n'.join([
            "You'd be surprise how helpful it is to go to office hours or to tutoring services!",
            "You can also try asking classmates for help too. You might not be the only one struggling",
            "I hope this was helpful!"
        ])

    def finish_health_resources(self):
        return '\n'.join({
            "That's really rough to go through alone.",
            "Maybe you can try going to your school's medical center or center for some help.",
            "You can also talk to your professors directly about this. They might be able to empathize!"
        })

    def finish_course_overload_response(self):
        return '\n'.join([
            "DROP A CLASS"  #FIXME
        ])

    def finish_academic_resouces(self):
        return '\n'.join([
            "ACADEMIC RESOURCES"  #FIXME
        ])

    def finish_join_clubs(self):
        return '\n'.join([
            "Cool! Next would be to check out your school's list of clubs and reach out to them about how to join.",
            "I know that seems like a lot, but I believe in you!"
        ])

    def finish_should_join_club(self):
        return '\n'.join([
            "Check out your school's list of clubs. It wouldn't hurt to see what's out there!"
        ])

    def finish_hotline_idk(self):
        return '\n'.join([
            "That's okay. No matter the case, know that you deserve to live. ",
            "And if you feel like causing harm to yourself, please call a friend or the hotline.",
            "We can also talk about what you're feeling"
        ])

    def finish_hotline(self):
        return '\n'.join([
            "Please call the suicide hotline."
        ])

    def finish_talk_to_friends(self):
        return '\n'.join([
            "I'm sure that they really care about you. Please talk to them about how you are feeling!"
        ])




if __name__ == '__main__':
    OxyCSBot().chat()
