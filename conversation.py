import random
from datetime import datetime

GREETINGS = [
    "hey", "yo", "sup", "wsg", "heyyy", "hiii", "ayo", "heyy",
    "hi", "hello", "yooo", "ayyy", "henlo", "wassup", "waddup",
    "yo yo", "ayoo", "heyo", "what's good", "howdy",
]

GROUPS = [
    "guys", "everyone", "yall", "gang", "people", "chat",
    "bois", "fam", "homies", "fellas", "boys",
]

FILLERS = [
    "ngl", "tbh", "fr", "ong", "lowkey", "highkey", "deadass",
    "no cap", "icl", "istg", "honestly", "literally", "actually",
    "bruh", "bro", "man", "dude", "like", "", "", "", "",
]

ADJ_GOOD = [
    "fire", "goated", "elite", "valid", "based", "bussin", "peak",
    "insane", "crazy good", "sick", "dope", "clean", "hard",
    "underrated", "legendary", "unmatched", "next level", "beautiful",
    "immaculate", "top tier", "cracked", "godly", "nuts", "wild",
]

ADJ_BAD = [
    "mid", "trash", "dead", "boring", "overrated", "wack", "ass",
    "terrible", "awful", "dry", "stale", "basic", "generic",
    "dog water", "down bad", "cooked", "chalked", "yikes", "not it",
]

MOODS = [
    "bored", "tired", "hungry", "hyped", "excited", "stressed",
    "happy", "sad", "lonely", "energetic", "sleepy", "lazy",
    "motivated", "chill", "vibing", "cozy", "goofy",
]

ACTIVITIES = [
    "playing", "watching", "listening to", "eating", "studying",
    "working on", "vibing to", "grinding", "chilling with",
    "streaming", "downloading", "trying", "getting into",
    "procrastinating on", "binging",
]

GAMES = [
    "valorant", "fortnite", "minecraft", "apex", "cod", "league",
    "overwatch", "cs2", "gta", "rocket league", "roblox",
    "elden ring", "palworld", "deadlock", "warzone", "stardew",
]

MUSIC = [
    "rap", "lofi", "rock", "pop", "r&b", "drill", "phonk",
    "jazz", "trap", "edm", "indie", "metal",
    "the new album", "that new song", "my playlist",
    "tyler the creator", "kanye", "drake", "kendrick", "travis scott",
    "the weeknd", "sza", "frank ocean",
]

FOOD = [
    "pizza", "burgers", "ramen", "sushi", "tacos", "wings",
    "fries", "pasta", "chicken", "noodles", "ice cream",
    "boba", "subway", "mcdonalds", "chipotle", "wingstop",
]

SHOWS = [
    "one piece", "breaking bad", "attack on titan", "jjk",
    "demon slayer", "arcane", "invincible", "the boys",
    "stranger things", "squid game", "tiktok compilations",
    "youtube shorts", "twitch streams",
]

OPINIONS = [
    "i think", "imo", "in my opinion", "i feel like",
    "not gonna lie", "hear me out", "hot take but",
    "unpopular opinion but", "controversial take but",
    "ok but fr", "real talk", "no but actually",
]

AGREEMENTS = [
    "facts", "real", "fr", "ong", "valid", "true", "exactly",
    "thats what im saying", "big facts", "W take", "this",
    "say it louder", "preach", "couldnt agree more",
    "literally this", "100%", "spot on", "you right",
    "exactly bro", "nah you spittin", "W", "real talk",
    "thats so true", "yessir", "on god bro",
]

DISAGREEMENTS = [
    "nah", "cap", "idk about that", "disagree tbh",
    "eh not really", "bruh no lol", "respectfully no",
    "L take", "thats crazy to say", "you trippin",
    "nah bro what", "hard disagree", "wrong", "wdym",
    "bro what are you saying", "nah youre bugging",
]

REACTIONS = [
    "lmaooo", "bruhh", "no way", "wait what", "LMAO",
    "im dead 💀", "crying rn 😭", "nahhh 💀", "bro what",
    "thats crazy", "yooo", "sheesh", "pause",
    "huh", "no shot", "im screaming", "bro im dying",
]

CLOSERS = [
    "lol", "haha", "fr", "💀", "", "", "", "",
    "lmao", "xd", "😭", "bruh", "man", "tho", "ngl",
]

TRANSITIONS = [
    "anyway", "btw", "on another note", "but fr tho",
    "speaking of which", "oh also", "wait", "yo",
    "random but", "off topic but", "also", "so",
]

QUESTION_STARTERS = [
    "what do yall think about", "anyone else into",
    "who here likes", "thoughts on", "have yall tried",
    "whats everyones favorite", "do yall fw",
    "is it just me or", "yall ever",
]

QUESTION_ENDERS = [
    "?", "??", " lol?", " tho?", " fr?",
    "? just curious", "? be honest",
]

def _humanize(text: str) -> str:
    if random.random() < 0.75:
        text = text.lower()
    elif random.random() < 0.3:
        text = text[0].upper() + text[1:] if text else text

    if random.random() < 0.08 and len(text) > 10:
        idx = random.randint(3, len(text) - 2)
        text = text[:idx] + text[idx] + text[idx:]

    if random.random() < 0.6:
        text = text.replace("'", "")

    if random.random() < 0.05:
        text += random.choice([".", "..", "...", " lol", " haha"])

    return text.strip()

def _pick(pool):
    return random.choice(pool)

def _maybe(text: str, chance: float = 0.4) -> str:
    return text if random.random() < chance else ""

def _time_greet() -> str:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return random.choice(["gm", "good morning", "morning"])
    elif 12 <= hour < 17:
        return random.choice(["good afternoon", "afternoon", "hey"])
    elif 17 <= hour < 21:
        return random.choice(["good evening", "hey"])
    else:
        return random.choice(["late night gang", "whos still up", "cant sleep", "night owls wya"])

def _gen_anecdote(topic: str = None) -> str:
    gaming_stories = [
        lambda: f"bro i was in a {_pick(GAMES)} game {random.choice(['yesterday', 'earlier', 'last night'])} and {random.choice(['my teammate threw so hard', 'i hit the craziest clip', 'the lag was insane', 'i got the most insane clutch'])} {_pick(CLOSERS)}",
        lambda: f"not even kidding i played {_pick(GAMES)} for like {random.randint(3, 8)} hours straight {random.choice(['yesterday', 'last weekend'])} and didnt even realize {_pick(CLOSERS)}",
    ]
    food_stories = [
        lambda: f"bro i just had {_pick(FOOD)} and it was {_pick(ADJ_GOOD)} like {random.choice(['best ive had', 'it hit different today'])}",
        lambda: f"i tried {_pick(FOOD)} for the first time {random.choice(['yesterday', 'recently'])} and {random.choice(['its actually so good', 'mid ngl'])}",
    ]
    life_stories = [
        lambda: f"not gonna lie {random.choice(['school', 'work', 'life'])} has been {random.choice(['kicking my ass', 'going crazy', 'so boring'])} {_pick(FILLERS)}",
        lambda: f"i stayed up till {random.randint(2, 5)}am {random.choice(['doing homework', 'watching youtube', 'playing games'])} and now im {random.choice(['dead', 'a zombie', 'running on 3hrs sleep'])} {_pick(CLOSERS)}",
    ]
    all_stories = gaming_stories + food_stories + life_stories
    if topic:
        topic_lower = topic.lower()
        if any(g in topic_lower for g in ['game', 'play', 'rank'] + [x.lower() for x in GAMES]):
            all_stories = gaming_stories
        elif any(f in topic_lower for f in ['food', 'eat', 'hungry'] + [x.lower() for x in FOOD]):
            all_stories = food_stories
    return random.choice(all_stories)()

def _build_multi_sentence(parts: list) -> str:
    parts = [p.strip() for p in parts if p.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    connectors = [" ", "\n", " and ", " but ", ". ", " tho. "]
    result = parts[0]
    for part in parts[1:]:
        result += random.choice(connectors) + part
    return result

class ConversationEngine:
    def __init__(self):
        self._topics = ['general', 'gaming', 'music', 'food', 'vibes', 'random', 'opinion', 'shows', 'life']
        self._current_topic = random.choice(self._topics)
        self._depth = 0
        self._max_depth = random.randint(4, 9)
        self._history = []
        self._mood = random.choice(['chill', 'hype', 'curious', 'goofy'])
        self._mood_counter = 0

    def _remember(self, msg: str):
        self._history.append(msg.lower().strip())
        if len(self._history) > 8:
            self._history.pop(0)

    def _shift_mood(self):
        self._mood_counter += 1
        if self._mood_counter > random.randint(3, 6):
            self._mood_counter = 0
            old = self._mood
            self._mood = random.choice([m for m in ['chill', 'hype', 'curious', 'goofy', 'tired'] if m != old])

    def _switch_topic(self):
        old = self._current_topic
        self._current_topic = random.choice([t for t in self._topics if t != old])
        self._depth = 0
        self._max_depth = random.randint(4, 9)

    def _detect_topic(self, text: str) -> str:
        text = text.lower()
        if any(g in text for g in GAMES) or any(w in text for w in ['game', 'play', 'ranked', 'lobby']):
            return 'gaming'
        if any(m in text for m in MUSIC) or any(w in text for w in ['song', 'music', 'listen', 'playlist']):
            return 'music'
        if any(f in text for f in FOOD) or any(w in text for w in ['food', 'eat', 'hungry']):
            return 'food'
        if any(s in text for s in SHOWS) or any(w in text for w in ['show', 'anime', 'movie', 'watch']):
            return 'shows'
        return None

    def _gen_greeting(self) -> str:
        roll = random.random()
        if roll < 0.15:
            return _time_greet()
        elif roll < 0.35:
            return f"{_pick(GREETINGS)} {_pick(GROUPS)} {_maybe(_pick(CLOSERS))}"
        elif roll < 0.55:
            parts = [
                f"{_pick(GREETINGS)} {_maybe(_pick(GROUPS))}",
                random.choice(["whats good", "how is everyone", "wsp", "hows everyone doing"]),
            ]
            return _build_multi_sentence(parts)
        else:
            return random.choice([
                f"just got home wsp {_pick(GROUPS)}",
                f"im back {_pick(CLOSERS)} what i miss",
                f"yoo whos online rn",
            ])

    def _gen_gaming_starter(self) -> str:
        game = _pick(GAMES)
        templates = [
            lambda: f"anyone {_pick(ACTIVITIES)} {game} rn",
            lambda: f"who tryna play some {game} {_pick(CLOSERS)}",
            lambda: f"bro {game} is {_pick(ADJ_GOOD)} {_pick(FILLERS)}",
            lambda: _gen_anecdote('gaming'),
        ]
        return random.choice(templates)()

    def _gen_music_starter(self) -> str:
        music = _pick(MUSIC)
        templates = [
            lambda: f"anyone else {_pick(ACTIVITIES)} {music} rn",
            lambda: f"{music} hits different {random.choice(['at night', 'rn', 'late'])} {_pick(FILLERS)}",
            lambda: f"been vibing to {music} all day {_pick(CLOSERS)}",
        ]
        return random.choice(templates)()

    def _gen_food_starter(self) -> str:
        food = _pick(FOOD)
        templates = [
            lambda: f"im so {random.choice(['hungry', 'starving'])} rn {_pick(FILLERS)} want some {food}",
            lambda: f"{food} or {_pick(FOOD)} and why {_pick(QUESTION_ENDERS)}",
            lambda: f"bro i just had {food} and it was {_pick(ADJ_GOOD)} {_pick(FILLERS)}",
        ]
        return random.choice(templates)()

    def _gen_vibes_starter(self) -> str:
        templates = [
            lambda: f"im so {_pick(MOODS)} rn {_pick(FILLERS)}",
            lambda: f"who else is {_pick(MOODS)} {random.choice(['rn', 'today'])}",
            lambda: f"anyone else just {random.choice(['vibing', 'chilling', 'doing nothing'])} rn {_pick(CLOSERS)}",
        ]
        return random.choice(templates)()

    def _gen_shows_starter(self) -> str:
        show = _pick(SHOWS)
        templates = [
            lambda: f"anyone watching {show} rn {_pick(QUESTION_ENDERS)}",
            lambda: f"bro {show} is {_pick(ADJ_GOOD)} {_pick(FILLERS)} like genuinely",
            lambda: f"hot take but {show} is {random.choice(['overrated', 'mid', 'goated'])} {_pick(FILLERS)}",
        ]
        return random.choice(templates)()

    def _gen_random_starter(self) -> str:
        debates = ["pineapple on pizza", "cats vs dogs", "android vs iphone", "morning vs night"]
        templates = [
            lambda: f"{_pick(OPINIONS)} {random.choice(debates)} {_pick(CLOSERS)}",
            lambda: f"random question but {_pick(QUESTION_STARTERS)} {random.choice(debates)}{_pick(QUESTION_ENDERS)}",
        ]
        return random.choice(templates)()

    def _gen_opinion_starter(self) -> str:
        subject = random.choice([_pick(GAMES), _pick(MUSIC), _pick(FOOD), _pick(SHOWS), "school", "gym"])
        templates = [
            lambda: f"{_pick(OPINIONS)} {subject} is {random.choice([_pick(ADJ_GOOD), _pick(ADJ_BAD)])} and heres why",
            lambda: f"rate {subject} out of 10 {_pick(CLOSERS)}",
        ]
        return random.choice(templates)()

    def _gen_life_starter(self) -> str:
        return _gen_anecdote('life')

    def _gen_agree_reply(self, last_msg: str) -> str:
        base = _pick(AGREEMENTS)
        roll = random.random()
        if roll < 0.3:
            return f"{base} {_pick(FILLERS)}"
        elif roll < 0.6:
            return f"{base}. {random.choice(['same here', 'thats literally me', 'i feel the same way'])} {_pick(CLOSERS)}"
        else:
            return f"{base} {_pick(FILLERS)}. like {random.choice(['thats so true', 'its not even close'])} {_pick(CLOSERS)}"

    def _gen_disagree_reply(self, last_msg: str) -> str:
        base = _pick(DISAGREEMENTS)
        roll = random.random()
        if roll < 0.3:
            return f"{base} {_pick(FILLERS)}"
        elif roll < 0.6:
            return f"{base}. {random.choice(['explain how', 'how tho', 'since when'])} {_pick(CLOSERS)}"
        else:
            return f"bro {base} {_pick(CLOSERS)}. {random.choice(['i respect your opinion but', 'dont take this the wrong way but'])} gotta disagree"

    def _gen_question_reply(self, last_msg: str) -> str:
        roll = random.random()
        if roll < 0.3:
            return f"{random.choice(['hmm', 'good question'])} {random.choice(['not sure', 'i think so', 'maybe', 'definitely'])} {_pick(FILLERS)}"
        else:
            return f"honestly id say {random.choice(['yes', 'no', 'it depends'])} {_pick(FILLERS)}. but that's just me"

    def _gen_reaction_reply(self, last_msg: str) -> str:
        base = _pick(REACTIONS)
        if random.random() < 0.5:
            return base
        return f"{base} {_pick(CLOSERS)}"

    def _gen_follow_up(self, last_msg: str) -> str:
        roll = random.random()
        if roll < 0.3:
            return f"wait {random.choice(['really', 'fr', 'actually'])} {_pick(CLOSERS)}. {random.choice(['tell me more', 'elaborate'])}"
        else:
            return f"bro {random.choice(['same', 'literally me', 'mood'])} {_pick(FILLERS)}. {random.choice(['its always like that', 'happens to the best of us'])}"

    def _gen_continue_convo(self, last_msg: str) -> str:
        last_lower = last_msg.lower()
        if any(g in last_lower for g in GAMES) or any(w in last_lower for w in ['game', 'play', 'ranked']):
            return f"we should run some games sometime {_pick(FILLERS)}. im usually on {random.choice(['at night', 'weekends'])} {_pick(CLOSERS)}"
        if any(f in last_lower for f in FOOD) or any(w in last_lower for w in ['food', 'eat', 'hungry']):
            return f"craving {_pick(FOOD)} so bad rn {_pick(CLOSERS)}"
        
        roll = random.random()
        if roll < 0.3:
            return self._gen_agree_reply(last_msg)
        elif roll < 0.6:
            return self._gen_follow_up(last_msg)
        else:
            return _gen_anecdote()

    def generate_starter(self) -> str:
        self._depth = 0
        self._shift_mood()
        generators = {
            'general': self._gen_greeting,
            'gaming': self._gen_gaming_starter,
            'music': self._gen_music_starter,
            'food': self._gen_food_starter,
            'vibes': self._gen_vibes_starter,
            'random': self._gen_random_starter,
            'opinion': self._gen_opinion_starter,
            'shows': self._gen_shows_starter,
            'life': self._gen_life_starter,
        }
        gen = generators.get(self._current_topic, self._gen_greeting)
        msg = _humanize(gen())
        self._remember(msg)
        return msg

    def generate_reply(self, last_message: str) -> str:
        self._depth += 1
        self._shift_mood()
        
        detected = self._detect_topic(last_message)
        if detected:
            self._current_topic = detected

        if self._depth >= self._max_depth:
            self._switch_topic()
            return self.generate_starter()

        is_question = last_message.rstrip().endswith('?')
        if is_question:
            msg = self._gen_question_reply(last_message)
        else:
            roll = random.random()
            if roll < 0.25:
                msg = self._gen_agree_reply(last_message)
            elif roll < 0.50:
                msg = self._gen_continue_convo(last_message)
            elif roll < 0.70:
                msg = self._gen_follow_up(last_message)
            elif roll < 0.85:
                msg = self._gen_reaction_reply(last_message)
            else:
                msg = self._gen_disagree_reply(last_message)

        msg = _humanize(msg)
        self._remember(msg)
        return msg

    def get_message(self, last_message: str = None, is_starter: bool = False) -> str:
        if is_starter or not last_message:
            return self.generate_starter()
        return self.generate_reply(last_message)

    def get_reaction_emoji(self) -> str:
        return random.choice(["💀", "😭", "😂", "👍", "🔥"])
