import os
while not os.path.exists(r"c:\temp\putty_cmd.log"):
    import time
    time.sleep(1)

with open(r"c:\temp\putty_cmd.log", "r+") as f:
    while True:
        d = f.read(10240)
        if d:
            print(d)
        import time
        time.sleep(0.1)