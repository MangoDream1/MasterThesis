from time import gmtime, strftime

def progress_bar(_min, _max):
    def update_progress(current, text="Progress:"):
        workdone = current / (_max - _min)
        time = strftime("%H:%M:%S", gmtime())

        print("\r{0} [{1:50s}] {2:.1f}% - {3}".format(text, "#" * int(workdone * 50),
                workdone*100, time), end="", flush=True)

        if workdone == 1:
            print("\n")

    return update_progress
