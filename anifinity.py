#!/usr/bin/python3.6

from collections import OrderedDict
import json
import objectpath
from jikanpy import Jikan
from aniffinity import Aniffinity
from aniffinity.exceptions import RateLimitExceededError
from aniffinity.exceptions import AniffinityException
from tabulate import tabulate

username = "myusername"
success = False


myfriends = {}
myaffi = {}
myshared = {}
myresult = {}

jikan = Jikan()

af = Aniffinity(username, base_service="MyAnimeList", wait_time=3)

# friends info
ufriends = jikan.user(username=username, request='friends')

for i in range(len(ufriends["friends"])):
    myfriends[i] = ufriends["friends"][i]["username"]
    for _ in range(2):
        try:
            myaffi[i],myshared[i] = af.calculate_affinity(myfriends[i], service="MyAnimeList")
            myresult[myfriends[i]] = round(myaffi[i],2)
        except RateLimitExceededError:
            time.sleep(5)
            continue

            # Any other aniffinity exception.
            # Affinity can't be calculated for some reason.
            # ``AniffinityException`` is the base exception class for
            # all aniffinity exceptions
        except AniffinityException:
            break

            # Exceptions not covered by aniffinity. Not sure what
            # you could do here. Feel free to handle however you like
        except Exception as e:
            print("Exception: `{}`".format(e))
            break

            # Success!
        else:
            success = True
            break

        # ``success`` will still be ``False`` if affinity can't been calculated.
        # If this is the case, you'll want to stop doing anything with this person
        # and move onto the next, so use the statement that will best accomplish this,
        # given the layout of your script

newresult = OrderedDict(sorted(myresult.items(), key=lambda t: t[1]),reverse=True)
headers = ["Friend", "Affinity"]
print(tabulate([v for v in newresult.items()],headers=headers))
