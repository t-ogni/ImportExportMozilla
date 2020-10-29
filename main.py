import csv
from pathlib import Path

import mozbp  # mozilla bypass

profile_paths = []  # ['./profiles/nn']
#profile_paths.append(Path('./profiles/nn'))
csv_out = 'end_%iter%.csv'

while len(profile_paths) < 2:
    profile_paths.append(mozbp.guessDir().expanduser())
    print(type(profile_paths[-1]))

for iter, profile in enumerate(profile_paths):
    try:
        key = mozbp.askpass(profile)
    except mozbp.NoDatabase:
        print(f"{profile}: this profile has no database")
    jsonLogins = mozbp.getJsonLogins(profile)
    logins = mozbp.exportLogins(key, jsonLogins)
    with open(csv_out.replace('%iter%', str(iter)), 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["url", "username", "password"])
        writer.writerows(logins)
