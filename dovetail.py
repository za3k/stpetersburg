import random, subprocess, pickle, os.path

# Wishlist: feedback system, esp. assigned to meta
# Sub-timeboxes, ex. infinite track of "read books"
# Settings
TASK_QUEUE = "task_queue.py"
BASE_TIME = 30

# Pickling and state
INIT_STATE = { "done_tasks": set(), "ratings": dict() }
FILE = ".dovetail.pickle"
def load():
    s = {}
    if os.path.exists(FILE):
        with open(FILE, "rb") as f:
            s = pickle.load(f)
    for k in INIT_STATE:
        if k not in s:
            s[k] = INIT_STATE[k]
    return s
def save(s):
    with open(FILE, "wb") as f:
        pickle.dump(s, f)

# UI
def human_time(t):
    second = t % 60
    t //= 60
    minute = t % 60
    hour = t // 60
    if hour: s = f"{hour} hours {minute} minutes"
    elif minute and not second: s = f"{minute} minutes"
    elif minute: s = f"{minute} minutes {second} seconds"
    else: s = f"{second} seconds"
    return s
def say(text, wait=False):
    p = subprocess.Popen(['speak', '-v', 'english-mb-en1', text])
    if wait: p.wait()
def timer(task, t):
    print("Do: ", task)
    print()
    p = subprocess.Popen(["timer", f"{t}s", "done"])
    try:
        p.wait()
    except KeyboardInterrupt:
        p.kill()
def do_task(task_id, t):
    say(task_id + " " + human_time(t))
    timer(task_id, t)

# Process
def bit(): return random.randrange(2)
def random_size():
    time = BASE_TIME
    while bit(): time *= 2
    return time
def doable_tasks(all_tasks, s, seconds):
    quality = random.randrange(-1,6)/2
    tasks = [task_id for task_id, low_s in all_tasks if low_s <= seconds and rating_for(s, task_id) >= quality]
    return tasks

# Magically find all find_*_task methods
def find_tasl(all_tasks, s, seconds):
    # Eliminate based on time
    tasks = [task_id for task_id, low_s in all_tasks if low_s <= seconds]
    # Filter by quality
    quality = random.randrange(-1,6)/2
def find_largest_undone_task(all_tasks, s, seconds):
    avail = sorted([(t, task) for (task, t) in all_tasks if task not in s["done_tasks"] and t < seconds])
    return avail[0][1]
def find_next_task(all_tasks, s, seconds):
    avail = [t for t in doable_tasks(all_tasks, s, seconds) if t not in s["done_tasks"]]
    return avail[0]
def find_random_undone_task(all_tasks, s, seconds):
    avail = [t for t in doable_tasks(all_tasks, s, seconds) if t not in s["done_tasks"]]
    return random.choice(avail)
def find_random_task(all_tasks, s, seconds):
    avail = doable_tasks(all_tasks, s, seconds)
    return random.choice(avail)
def find_recent_task(all_tasks, s, seconds):
    avail = [t for t in doable_tasks(all_tasks, s, seconds) if t not in s["done_tasks"]]
    return avail[-1]
def next_alphabetical(all_tasks, s, seconds):
    avail = [t for t in doable_tasks(all_tasks, s, seconds) if t not in s["done_tasks"]]
    return sorted(avail)[0]
def last_alphabetical(all_tasks, s, seconds):
    avail = [t for t in doable_tasks(all_tasks, s, seconds) if t not in s["done_tasks"]]
    return sorted(avail)[-1]

def get_tasks():
    with open(TASK_QUEUE) as f:
        x = eval(f.read(), {"m":60,"h":3600})
    out = []
    for i in x:
        if type(i) == str:
            out.append((i,0))   
        elif len(i) == 2:
            out.append(i)
    return out

def rate_task(s, task, time):
    while True:
        try:
            rating = int(input("How was this task? 1 = bad, 2 = ok, 3 = good  "))
            break
        except ValueError:
            pass
    if task not in s["ratings"]: s["ratings"][task] = []
    s["ratings"][task].append((rating, time))
    return s
def mean(x):
    return sum(x)/len(x)
def rating_for(s, task):
    if task in s["ratings"]:
        return mean([x[0] for x in s["ratings"][task]])
    else:
        return 2.5

def main_loop(s):
    t = random_size()
    tasks = list(get_tasks())
    methods = [v for x,v in globals().items() if x.startswith("find_") and x.endswith("_task")]
    find_method = random.choice(methods)
    try:
        task = find_method(tasks, s, t)
    except IndexError:
        task = None
    if task is None:
        say("No tasks available. Resetting.")
        s["done_tasks"] = set()
        return main_loop(s)
    do_task(task, t)
    s = rate_task(s, task, t)
    s["done_tasks"].add(task)
    return s
if __name__ == "__main__":
    s = load()
    try:
        s = main_loop(s)
    finally:
        save(s)
