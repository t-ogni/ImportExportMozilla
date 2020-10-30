# import csv
from pathlib import Path, PureWindowsPath
import mozbp  # mozilla bypass

profile_paths = []
output_path = './'
profiles = mozbp.findProfiles()
print('which profile need to use?')
for i, pr in enumerate(profiles):
    print(f"{i}: {pr['name']}")

print()
while True:
    com = input("(type 'h' to help): ")

    if not com or com == 'brk':
        if len(profile_paths) > 1:
            break
        else:
            print("need more profiles to merge")

    elif com in ('h', 'help'):
        print(
            "h, help - call this menu \n"
            "%num% - choose profile \n"
            "p, %path% - write your path. ('//%path%' for server)\n"
            "brk, enter (clear string) - continue \n"
        )

    elif com == 'p':
        profile_paths.append(Path(input("path: ")))
        print("added")

    elif com.isdigit():
        profile_paths.append(profiles[int(com)]['path'])
        print("added")

    else:
        if com.startswith("//"):
            path = PureWindowsPath(com)
        else:
            path = Path(com)

        if path.exists():
            profile_paths.append(path)
            print("added")
        else:
            print("unknown command")

print("using profiles:")
profiles_logins = []
json_logins = []
for ITEM_ID, profile in enumerate(profile_paths):
    print('\t', profile.absolute())
    try:
        key = mozbp.askpass(profile)
    except mozbp.NoDatabase:
        print(f"{ITEM_ID}: this profile has no database")
        exit(99)
    except AttributeError:
        print(f"{ITEM_ID}: this profile cannot be decrypted (after FF.72)")
        exit(100)

    jsonLogins = mozbp.getJsonLogins(profile)
    json_logins.append(jsonLogins)
    logins = mozbp.exportLogins(key, jsonLogins, ['hostname', 'login', 'password', 'timePasswordChanged'])
    profiles_logins.append(logins)

all_logins = profiles_logins[0]
global_json = json_logins[0]
for logins in profiles_logins:
    for login in logins:
        if login not in all_logins:
            print('different', login['hostname'])
            while True:
                i = input('(h to help) >> ')
                if i == 'h':
                    print(
                        "h - this menu \n"
                        "r %n% - replace with current founded account \n"
                        "a - add to branch \n"
                        "s - skip \n"
                        "%anykey% - show difference / new account"
                    )
                elif i == 'a':
                    mozbp.addNewLogin(key, global_json, login)
                    all_logins.append(login)
                    break

                elif i.startswith('r '):
                    l_id = int(i.replace('r ', ''))
                    l_found = []
                    for l in all_logins:
                        if l['hostname'] == login['hostname'] and \
                                (l['login'] == login['login'] or
                                 l['password'] == login['password']):
                            l_found.append(l)
                    replace_index = all_logins.index(l_found[l_id])
                    all_logins[replace_index] = l
                    break

                elif i == 's':
                    break

                else:
                    site_found = False
                    print(f"site: {login['hostname']} \n")
                    for l in all_logins:
                        if l['hostname'] == login['hostname'] and \
                                (l['login'] == login['login'] or
                                 l['password'] == login['password']):
                            print("description  | old                     | new ")
                            print(f"login        | {l['login']:<25}| {login['login']:<25}")
                            print(f"password     | {l['password']:<25}| {login['password']:<25}")
                            print(f"modify-time  | {l['timePasswordChanged']:<25}| {login['timePasswordChanged']:<25} \n")
                            site_found = True
                    if not site_found:
                        print("description  | new ")
                        print(f"login       | {l['login']:<25}")
                        print(f"password    | {l['password']:<25}")
                        print(f"modify-time | {l['timePasswordChanged']:<25}\n")

mozbp.dumpJsonLogins(Path(output_path), global_json)
#   ./profiles/nn

'''
%APPDATA%\Mozilla\Firefox\Profiles\*\content-prefs.sqlite
%APPDATA%\Mozilla\Firefox\Profiles\*\cookies.sqlite
%APPDATA%\Mozilla\Firefox\Profiles\*\favicons.sqlite
%APPDATA%\Mozilla\Firefox\Profiles\*\key4.db
%APPDATA%\Mozilla\Firefox\Profiles\*\logins.json
%APPDATA%\Mozilla\Firefox\Profiles\*\permissions.sqlite
%APPDATA%\Mozilla\Firefox\Profiles\*\places.sqlite
%APPDATA%\Mozilla\Firefox\Profiles\*\sessionstore.jsonlz4
'''