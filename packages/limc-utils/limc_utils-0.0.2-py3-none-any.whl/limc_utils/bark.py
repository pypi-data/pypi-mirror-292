from urllib.request import urlopen
import os


def bark(msg, bark=None):
    if bark is None:
        bark = os.getenv("BARK")
    if not bark:
        return
    url = "https://api.day.app/{0}/{1}/".format(bark, msg)
    try:
        urlopen(url)
    except:
        pass
