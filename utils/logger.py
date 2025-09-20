def log_event(event):
    with open("log.txt", "a") as f:
        f.write(event + "\n")
