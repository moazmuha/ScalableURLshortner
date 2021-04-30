with open("requests", "w") as f:
    for i in range(3000):
        f.write(f"http://127.0.0.1:4000/?short=ouzzy{i}&long=youtube.com\n")