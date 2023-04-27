import random, subprocess

def bit(): return random.randrange(2)
def random_size():
    time = 30
    while bit(): time *= 2
    return time
def find_next_task(all_tasks, done_task_ids, seconds):
    for task_id, (low, high) in all_tasks:
        if task_id in done_task_ids: continue
        if not low <= seconds <= high: continue
        return task_id
def do_task(task_id, t):
    print("Do: ", task_id)
    print()
    subprocess.check_output(['speak', '-v', 'english-mb-en1', task_id])
    p = subprocess.Popen(["timer", f"{t}s", task_id])
    p.wait()

if __name__ == "__main__":
    done_tasks = set()
    while True:
        t = random_size()
        with open("task_queue.py") as f:
            tasks = eval(f.read(), {'INF':999999999})
        task = find_next_task(tasks, done_tasks, t)
        if task is None:
            done_tasks = set()
            task = find_next_task(tasks, done_tasks, t)
        do_task(task, t)
