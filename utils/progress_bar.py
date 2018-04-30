def progress_bar(_min, _max):
    def update_progress(current, text="Progress:"):
        workdone = current / (_max - _min)

        print("\r{0} [{1:50s}] {2:.1f}%".format(text, "#" * int(workdone * 50),
                workdone*100), end="", flush=True)

        if workdone == 1:
            print("\n")

    return update_progress
