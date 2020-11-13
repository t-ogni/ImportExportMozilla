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
to_copy = True
profiles_logins = []
json_logins = []
profiles_paths = []
key = ''


def get_new_prof(profile: Path):
    global profiles_logins, json_logins, profiles_paths, key
    print('\t', profile.absolute())
    try:
        key = mozbp.askpass(profile)

    except mozbp.NoDatabase:
        print(f"\t\tthis profile has no database")
        return

    except AttributeError:
        print(f"\t\tthis profile cannot be decrypted (after FF.72)")
        return

    profiles_paths.append(profile)
    jsonLogins = mozbp.getJsonLogins(profile)
    json_logins.append(jsonLogins)
    logins = mozbp.exportLogins(key, jsonLogins, ['hostname', 'login', 'password', 'timePasswordChanged'])
    profiles_logins.append(logins)
    print("successfully added profile")
    return


if not output_path.exists():
    output_path.mkdir()

profiles = mozbp.findProfiles()
print('which profile need to use?')
for i, pr in enumerate(profiles):
    print(f"{i}: {pr}")

print()
while True:
    com = input("(type 'h' to help): ")

    if not com or com == 'brk':
        if len(profiles_logins) > 1:
            break
        else:
            print("need more profiles to merge")

    elif com.isdigit():
        get_new_prof(profiles[int(com)])

    elif com in ('h', 'help'):
        print(
            "h, help - call this menu \n"
            "%num% - choose profile \n"
            "p, %path% - write your path. ('//%path%' for server)\n"
            "brk, enter (clear string) - continue \n"
            "c - copy files ('Джентельменский Набор') [ratio]"
        )

    elif com == 'p':
        get_new_prof(Path(input("path: ")))

    elif com == 'c':
        to_copy = not to_copy
        if to_copy:
            print("file will be copied")
        else:
            print("nothing will be copied")

    else:
        if com.startswith("//"):
            if sys.platform in ('win32', 'cygwin'):
                path = PureWindowsPath(com)  # windows
                get_new_prof(path)
            else:
                path = Path(com)  # linux
                get_new_prof(path)
        else:
            path = Path(com)
            get_new_prof(path)

        if path.exists():
            get_new_prof(path)
        else:
            print("unknown command")

if to_copy:
    print(f"\n copying files to {output_path.absolute()}")
    for copy_file in copy_list:
        try:
            copy2(copy_file.replace('%profile%', str(profiles_paths[0].absolute())),
                  str(output_path.absolute()) + copy_file.replace('%profile%', ''))
        except Exception as err:
            print(f"something went wrong being copying: {err}")
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
                        "a - add to branch \n"
                        "s - skip \n"
                        "%anykey% - show difference / new account"
                    )
                elif i == 'a':
                    mozbp.addNewLogin(key, global_json, login)
                    all_logins.append(login)
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
                            print(
                                f"modify-time  | {l['timePasswordChanged']:<25}| {login['timePasswordChanged']:<25} \n")
                            site_found = True
                    if not site_found:
                        print("description  | new ")
                        print(f"login       | {l['login']:<25}")
                        print(f"password    | {l['password']:<25}")
                        print(f"modify-time | {l['timePasswordChanged']:<25}\n")

mozbp.dumpJsonLogins(output_path, global_json)
print('\n done. exiting...')
#   ./profiles/nn


''' network dir solution
os.chdir(join(r'//server-01', 'directory', 'filename.txt'))
path = Path()
path = path.resolve()
'''
