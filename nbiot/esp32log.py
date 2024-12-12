import os

class Log():
    def __init__(self, rtc):
        self.rtc = rtc

    def log(self, mess, logtype="I", wtype="a+b"):
        try:
            if wtype == "w+b":
                os.rename("esp32.log", "0_esp32.log")
        except:
            pass

        f = open("esp32.log", wtype)
        try:
            rdt = self.rtc.datetime()
            f.write("{} {}/{}/{} {}:{}:{} {}\n".format(logtype, rdt[0], rdt[1], rdt[2], rdt[4], rdt[5], rdt[6], mess))
        except:
            f.write("{} {} {}\n".format(logtype, "1900/01/01 00:00:00", mess))
        f.close()

    def queue(self, mess, fname="queue.log"):
        f = open(fname, "a+b")
        f.write("{}\n".format(mess))
        f.close()

    def queueRefresh(self):
        try:
            os.remove("queue.log")
            os.rename("queue_missed.log", "queue.log")
            os.remove("queue_missed.log")
        except:
            print("No Refresh file")

