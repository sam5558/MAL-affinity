#!/usr/bin/env python3

import sys
import json
import time
from decimal import DecimalException

import objectpath
from collections import OrderedDict

from jikanpy import Jikan
from aniffinity import Aniffinity
from aniffinity.exceptions import RateLimitExceededError, AniffinityException, NoAffinityError, InvalidUserError
from tabulate import tabulate


# get username from command line
if len(sys.argv) <= 1:
    print("I expected a username but you didn't give me one!")
    print('Example: python3 anifinity.py "Guts__"')
    sys.exit(1)

username = sys.argv[1].strip()

if len(sys.argv) <= 2:
    usr = username
else:
    usr = sys.argv[2].strip()

jikan = Jikan()

print("Downloading your friends from MyAnimeList...")
# friends info
ufriends = jikan.user(username=usr, request='friends')

print("Downloaded {} friends".format(len(ufriends["friends"])))

# Download the users myanimelist
print("Downloading {}'s animelist...".format(username))
af = Aniffinity(username, base_service="MyAnimeList", wait_time=2)

# e.g. results = {"some_user": affinity_val}
results = {}

# create a list of friend names
friend_names = [f["username"] for f in ufriends["friends"]]

while len(friend_names) > 0: # while the list isn't empty
    friend = friend_names[0] # get the first name
    print("Comparing {}'s list to {}...".format(username, friend))
    try:
        # calculate affinity
        affinity, shared = af.calculate_affinity(friend, service="MyAnimeList")
        # save the result
        results[friend] = round(affinity, 2)
        # remove that friend from the list
        friend_names.remove(friend)
    except RateLimitExceededError:
        print("We exceeded the rate limit!")
        # wait for a while and then try again
        time.sleep(10)
        continue
    except NoAffinityError as ne:
        print("{}".format(ne))
        # ignore this user
        friend_names.remove(friend)
        continue
    except InvalidUserError:
        print("Couldnt download list for {}. This may be because their list is private.".format(friend))
        # ignore this user
        friend_names.remove(friend)
        continue
    except DecimalException:
        # see here:
        # https://github.com/erkghlerngm44/aniffinity/blob/master/aniffinity/calcs.py#L32
        # this can happen when a user has no ratings or rates everything the same
        print("Division by zero error while trying to process list for {}...".format(friend))
        # ignore this user
        friend_names.remove(friend)
        continue
    except Exception as e:
        # exit on any other error
        print("Exception for {}: `{}`".format(friend, e))
        break

newresult = OrderedDict(sorted(results.items(), key=lambda t: t[1]))
print(tabulate([v for v in newresult.items()], headers=["Friend", "Affinity"]))
