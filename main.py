from pathlib import Path, PureWindowsPath
import mozbp  # mozilla bypass
import sys
from shutil import copy2  # copy files

profile_paths = []
output_path = Path('./profile/')

copy_list = '''\
%profile%\\content-prefs.sqlite
%profile%\\cookies.sqlite
%profile%\\favicons.sqlite
%profile%\\key4.db
%profile%\\permissions.sqlite
%profile%\\places.sqlite
%profile%\\sessionstore.jsonlz4\
'''.split('\n')
to_copy = False

if not output_path.exists():
    output_path.mkdir()

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

    elif com.isdigit():
        profile_paths.append(profiles[int(com)]['path'])
        print("added")

    elif com in ('h', 'help'):
        print(
            "h, help - call this menu \n"
            "%num% - choose profile \n"
            "p, %path% - write your path. ('//%path%' for server)\n"
            "brk, enter (clear string) - continue \n"
            "c - copy files ('Джентельменский Набор') [ratio]"
        )

    elif com == 'p':
        profile_paths.append(Path(input("path: ")))
        print("added")

    elif com == 'c':
        to_copy = not to_copy
        print(f'ratio swiched to {to_copy}')

    else:
        if com.startswith("//"):
            if sys.platform in ('win32', 'cygwin'):
                path = PureWindowsPath(com)  # windows
            else:
                path = Path(com)  # linux
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


if to_copy:
    print(f"\n copying files to {output_path.absolute()}")
    for copy_file in copy_list:
        try:
            copy2(copy_file.replace('%profile%', str(profile_paths[0].absolute())),
                 str(output_path.absolute()) + copy_file.replace('%profile%', ''))
        except Exception as err:
            print(f"something went wrong: {err}")
    print()

all_logins = profiles_logins[0]
global_json = json_logins[0]
all_logins[0]['password'] = 'wqdf'
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
                    mozbp.delNewLogin(key, jsonLogins, l)
                    mozbp.addNewLogin(key, global_json, login)
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
                            print("description  | old                      | new ")
                            print(f"login        | {l['login']:<25}| {login['login']:<25}")
                            print(f"password     | {l['password']:<25}| {login['password']:<25}")
                            print(f"modify-time  | {l['timePasswordChanged']:<25}| {login['timePasswordChanged']:<25} \n")
                            site_found = True
                    if not site_found:
                        print("description  | new ")
                        print(f"login       | {l['login']:<25}")
                        print(f"password    | {l['password']:<25}")
                        print(f"modify-time | {l['timePasswordChanged']:<25}\n")

mozbp.dumpJsonLogins(output_path, global_json)
#   ./profiles/nn


''' network dir solution
os.chdir(join(r'//server-01', 'directory', 'filename.txt'))
path = Path()
path = path.resolve()
'''