from collections import defaultdict
import shlex
import shutil
import subprocess
from subprocess import Popen, PIPE, STDOUT, DEVNULL
import sys
import os
# from distutils.version import LooseVersion
from packaging.version import Version
import platform
import requests
import asyncio
import time
import webbrowser
import re
from os.path import expanduser
import json
import signal
import argparse
from textwrap import wrap


from .pick import pick


REGISTRY_BASE_URL = 'registry.gitlab.au.dk'

def newer_version_of_package():
    cmd = 'conda search -c mbgexercises mbg-exercise-client'
    # cmd = shlex.split(cmd)
    # cmd[0] = shutil.which(cmd[0])    
    p = Popen(shlex.split(cmd), stdout=PIPE, stderr=DEVNULL, text=True)
    conda_search, _ = p.communicate()
    newest_version = conda_search.strip().splitlines()[-1].split()[1]

    cmd = 'conda list -f mbg-exercise-client'
    p = Popen(shlex.split(cmd), stdout=PIPE, stderr=DEVNULL, text=True)
    conda_search, _ = p.communicate()
    this_version = conda_search.strip().splitlines()[-1].split()[1]

    if Version(newest_version) > Version(this_version):
        return newest_version


def docker_installed():
    if platform.system() == 'Darwin':
        return shutil.which('docker')
    if platform.system() == 'Linux':
        return shutil.which('docker')
    if platform.system() == 'Windows':
        return shutil.which('docker')
    return False


def select_image(image_name_list):

    image_tree = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
    for image_name in image_name_list:
        c, w, v = image_name.split('-')
        image_tree[c.replace('_', ' ')][w.replace('_', ' ')][v.replace('_', ' ')] = image_name

    KEY_CTRL_C = 3
    KEY_ESCAPE = 27
    QUIT_KEYS = (KEY_CTRL_C, KEY_ESCAPE, ord("q"))
    title = "\n Select course: "
    options = list(image_tree.keys())
    course, index = pick(
        options, title, indicator="=>", default_index=0, quit_keys=QUIT_KEYS
    )
    title = "\n Select week: "
    options = list(image_tree[course].keys())
    week, index = pick(
        options, title, indicator="=>", default_index=0, quit_keys=QUIT_KEYS
    )
    title = "\n Select exercise: "
    options = list(image_tree[course][week].keys())
    exercise, index = pick(
        options, title, indicator="=>", default_index=0, quit_keys=QUIT_KEYS
    )

    selected_image = image_tree[course][week][exercise]
    return selected_image


def get_registry_listing(registry):
    s = requests.Session()
    # s.auth = ('user', 'pass')
    s.headers.update({'PRIVATE-TOKEN': 'glpat-tiYpz3zJ95qzVXnyN8--'})
    # s.headers.update({'PRIVATE-TOKEN': 'glpat-BmHo-Fh5R\_TvsTHqojzz'})
    images = {}
    r  = s.get(registry,  headers={ "Content-Type" : "application/json"})
    if not r.ok:
      r.raise_for_status()
    for entry in r.json():
        name = entry['path'].split('/')[-1]
        images[name] = entry['location']
    return images


def open_browser(url, force_chrome=False):
    if platform.platform().startswith('Darwin') or platform.platform().startswith('macOS-'):
        chrome_path = r'open -a /Applications/Google\ Chrome.app %s'
        if force_chrome and os.path.exists('/Applications/Google Chrome.app'):
            webbrowser.get(chrome_path).open(url, new=2)
        else:
            webbrowser.open(url, new=2)
    elif platform.platform().startswith('Windows'):
        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        if force_chrome and os.path.exists(os.path.abspath(os.path.join(os.sep, 'Program Files (x86)', 'Google', 'Chrome', 'Application', 'chrome.exe'))):
            webbrowser.get(chrome_path).open(url, new=2)
        else:
            webbrowser.open(url, new=2)
    else:
        chrome_path = '/usr/bin/google-chrome %s'
        if force_chrome and os.path.exists('/usr/bin/google-chrome'):
            webbrowser.get(chrome_path).open(url, new=2)
        else:
            webbrowser.open(url, new=2)


def docker_command(command, silent=False, return_json=False):
    if silent:
        subprocess.run(shlex.split(command), check=False, stdout=DEVNULL, stderr=DEVNULL)
        return
    if return_json:
        result = []
        for line in subprocess.check_output(shlex.split(command + ' --format json')).decode().strip().splitlines():
            result.append(json.loads(line))
        return result
    else:
        return subprocess.check_output(shlex.split(command)).decode().strip()


def docker_volume_ls():
    return docker_command('docker volume ls', return_json=True)


def docker_images():
    return docker_command('docker images', return_json=True)


def docker_pull(image_url):
    print("\nDownloading resources, this may take a while...\n")
    # return os.system(f'docker pull {image_url}:main')
    docker_command(f'docker pull {image_url}:main', silent=True)


def docker_containers():
    return docker_command('docker ps', return_json=True)


def docker_prune_containers():
    docker_command(f'docker container prune --filter="Name={REGISTRY_BASE_URL}*"', silent=True)


def docker_prune_volumes():
    docker_command(f'docker volume --filter="Name={REGISTRY_BASE_URL}*"')


def docker_prune_all():
    docker_command(f'docker prune -a', silent=True)


def docker_rm_image(image, force=False):
    if force:
        docker_command(f'docker image rm -f {image}', silent=True)
    else:
        docker_command(f'docker image rm {image}', silent=True)


def docker_kill(container_id):
    docker_command(f'docker kill {container_id}', silent=True)


def docker_cleanup():
    for image in docker_images():
        if image['Repository'].startswith(REGISTRY_BASE_URL):
            docker_rm_image(image['ID'])
    docker_prune_containers()
    docker_prune_volumes()
    docker_prune_all()


def docker_image_exists(image_url):
    for image in docker_images():
        if image['Repository'].startswith(image_url):
            return True
    return False


def above_subdir_limit(allowed_depth):
    for dir, _, _ in os.walk('.'):
        if len(dir.split('/')) > allowed_depth:
            return True
    return False


def wrap_text(text):
    return "\n".join(wrap(' '.join(text.split()), 80))    


def launch_exercise():

    description = """
    Bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla
    bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla
    bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla
    bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla.
    """

    not_wrapped = """Bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla."""

    description = wrap_text(description) + "\n\n" + not_wrapped

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                        description="description")

    parser.add_argument("-v", "--verbose",
                    dest="verbose",
                    action='store_true',
                    help="Print debugging information")
    parser.add_argument("-a", "--vip",
                    dest="vip",
                    action='store_true',
                    help="Download the VIP version of the exercise")
    parser.add_argument("-n", "--no-mount-limit",
                    dest="no_mount_limit",
                    action='store_true',
                    help="Override check for maximum depths of mounted directories")

    # cleanup docker images and containers when terminal window is closed
    cleanup = False

    args = parser.parse_args()

    newer_version = newer_version_of_package()
    if newer_version:
        print(f'Package needs to update. Try again once this update completes.')
        cmd = f"conda install -y -q -c mbgexercises mbg-exercises={newer_version}"
        os.system(cmd)

    # user home directory and parent working directory
    home = expanduser("~")
    pwd = os.getcwd()

    subdir_limit = 1
    if not args.no_mount_limit:
        if above_subdir_limit(subdir_limit):
            msg = f"""Please run this command in a directory where the depth of 
                sub-directories is at most {subdir_limit}. Ideally, in a directory 
                with no sub-directories"""
            print(wrap_text(msg))
            sys.exit(1)

    if not docker_installed():
        print('Docker is not installed')
        sys.exit(1) 

    # get registry listing
    registry = 'https://gitlab.au.dk/api/v4/groups/mbg-exercises/registry/repositories'
    images = get_registry_listing(registry)

    # select image using menu prompt
    image = select_image(sorted(images))
    image_url = images[image]

    # get local images
    local_images = docker_images()
    # pull image if not already present
    if not docker_image_exists(image_url):
        docker_pull(image_url)
        assert docker_image_exists(image_url)
        
    # replace backslashes with forward slashes and C: with /c for windows
    if platform.system() == 'Windows':
        pwd = pwd.replace('\\', '/').replace('C:', '/c')
        home = home.replace('\\', '/').replace('C:', '/c')  

    # command for running jupyter docker container
    cmd = f"docker run --rm --mount type=bind,source={home}/.ssh,target=/tmp/.ssh --mount type=bind,source={home}/.anaconda,target=/root/.anaconda --mount type=bind,source={pwd},target={pwd} -w {pwd} -i -t -p 8888:8888 {image_url}:main"

    # run docker container
    with Popen(shlex.split(cmd), stdout=DEVNULL, stderr=DEVNULL) as docker_run_p:
        # try block to allow normal exceptions in subprocess with-block
        try:
            time.sleep(2)

            # get id of running container
            for cont in docker_containers():
                if cont['Image'].startswith(image_url):
                    run_container_id  = cont['ID']
                    break
            else:
                print('No running container with image')
                sys.exit(1)    

            # signal handler for cleanup when terminal window is closed
            def handler(signum, frame):
                docker_kill(run_container_id)
                docker_run_p.kill()
                docker_run_p.wait()
                if cleanup:
                    docker_cleanup()
                # sys.exit(1)
                raise Exception

            signal.signal(signal.SIGTERM, handler)
            signal.signal(signal.SIGINT, handler)
            match platform.system():
                case 'Mac':
                    signal.signal(signal.SIGHUP, handler)
                case 'Linux':
                    signal.signal(signal.SIGHUP, handler)
                case 'Windows':
                    signal.signal(signal.SIGBREAK, handler)
                    signal.signal(signal.SIGABRT, handler)


            cmd = f"docker logs --follow {run_container_id}"
            with Popen(shlex.split(cmd), stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True) as docker_log_p:
                # try block to allow normal exceptions in subprocess with-block
                try:
                    while True:
                        time.sleep(0.1)
                        line = docker_log_p.stdout.readline()#.decode().strip()
                        match= re.search(r'https?://127.0.0.1\S+', line)
                        if match:
                            token_url = match.group(0)
                            break
                
                    open_browser(token_url)

                    for _ in range(9999999999999):
                        time.sleep(10)


                except Exception as e:
                    docker_log_p.kill()
                    docker_log_p.wait()
                    raise e

#            docker_kill(run_container_id)

        except Exception as e:
            docker_run_p.kill()
            docker_run_p.wait()
            raise e
        finally:
            docker_kill(run_container_id)
            if cleanup:
                docker_cleanup()



        # docker system df
        # docker system df -v

        # docker system prune -a





            # from flask import Flask
            # app = Flask(__name__)

            # @app.route('/')
            # def display():
            #     return "Looks like it works!"

            # app.run(port=8888)



















# import signal
# os.kill(self.p.pid, signal.CTRL_C_EVENT)

    # stdout, stderr = docker_run_p.communicate()
    # if stdout:
    #     print(f'[stdout] {stdout}', end='', flush=True)
    # if stderr:
    #     print(f'[stderr] {stderr}', end='', flush=True, file=sys.stderr)



# JUST START DOCKER RUN WITH POPEN NONBLOCKING, THEN START DOCKER LOGS WITH POPEN NONBLOCKING, THEN READ FROM THIER STREAMS IN LOOP.


    # args = f"run --rm --mount type=bind,source={user_home}/.ssh,target=/tmp/.ssh --mount type=bind,source={user_home}/.anaconda,target=/root/.anaconda --mount type=bind,source={pwd},target={pwd} -w {pwd} -i -t -p 8888:8888 {image_url}:main".split()

    # proc = await asyncio.create_subprocess_exec('docker', args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)


# # USE RUNNER TO CAPTURE OUTPUT stream FROM 'docker logs --follow <container_id>'


# # if proc takes very long to complete, the CPUs are free to use cycles for 
# # other processes
# stdout, stderr = await proc.communicate()


    sys.exit()

    args = f"run --rm --mount type=bind,source={user_home}/.ssh,target=/tmp/.ssh --mount type=bind,source={user_home}/.anaconda,target=/root/.anaconda --mount type=bind,source={pwd},target={pwd} -w {pwd} -i -t -p 8888:8888 {image_url}:main".split()
    asyncio.run(run_docker(args))

    # container_id = subprocess.check_output('docker ps -q', shell=True).decode().strip()

    # args = f"docker logs --follow {container_id}".split()
    # asyncio.run(run_docker(args))


    # alternative
    #          -t -i
    # args = f"run --attach stdout --attach stderr --rm --mount type=bind,source=/Users/kmt/.ssh,target=/tmp/.ssh --mount type=bind,source=/Users/kmt/.anaconda,target=/root/.anaconda --mount type=bind,source=/Users/kmt/google_drive/projects/mbg-exercise-client,target=/Users/kmt/google_drive/projects/mbg-exercise-client -w /Users/kmt/google_drive/projects/mbg-exercise-client -p 8888:8888 registry.gitlab.au.dk/au81667/mbg-docker-exercises:main".split()

    # args = f"run -d --name kaspertest --rm --mount type=bind,source=/Users/kmt/.ssh,target=/tmp/.ssh --mount type=bind,source=/Users/kmt/.anaconda,target=/root/.anaconda --mount type=bind,source=/Users/kmt/google_drive/projects/mbg-exercise-client,target=/Users/kmt/google_drive/projects/mbg-exercise-client -w /Users/kmt/google_drive/projects/mbg-exercise-client -p 8888:8888 registry.gitlab.au.dk/au81667/mbg-docker-exercises:main  ; docker attach kaspertest".split()

    # args = f"run --pull=always --rm --mount type=bind,source={user_home}/.ssh,target=/tmp/.ssh --mount type=bind,source={user_home}/.anaconda,target=/root/.anaconda --mount type=bind,source={pwd},target={pwd} -w {pwd} -i -t -p 8888:8888 {image_url}:main".split()
    # args = f"run --rm --mount type=bind,source={user_home}/.ssh,target=/tmp/.ssh --mount type=bind,source={user_home}/.anaconda,target=/root/.anaconda --mount type=bind,source={pwd},target={pwd} -w {pwd} -i -t -p 8888:8888 {image_url}:main".split()

    # # args = f"run -t -i --attach stdout --attach stderr --rm --mount type=bind,source=/Users/kmt/.ssh,target=/tmp/.ssh --mount type=bind,source=/Users/kmt/.anaconda,target=/root/.anaconda --mount type=bind,source=/Users/kmt/google_drive/projects/mbg-exercise-client,target=/Users/kmt/google_drive/projects/mbg-exercise-client -w /Users/kmt/google_drive/projects/mbg-exercise-client -p 8888:8888 registry.gitlab.au.dk/au81667/mbg-docker-exercises:main".split()

    # asyncio.run(run_docker(args))

#docker run --attach stdout --attach stderr --name kaspertest --rm --mount type=bind,source=/Users/kmt/.ssh,target=/tmp/.ssh --mount type=bind,source=/Users/kmt/.anaconda,target=/root/.anaconda --mount type=bind,source=/Users/kmt/google_drive/projects/mbg-exercise-client,target=/Users/kmt/google_drive/projects/mbg-exercise-client -w /Users/kmt/google_drive/projects/mbg-exercise-client -p 8888:8888 registry.gitlab.au.dk/au81667/mbg-docker-exercises:main

#docker run -d --name kaspertest --rm --mount type=bind,source=/Users/kmt/.ssh,target=/tmp/.ssh --mount type=bind,source=/Users/kmt/.anaconda,target=/root/.anaconda --mount type=bind,source=/Users/kmt/google_drive/projects/mbg-exercise-client,target=/Users/kmt/google_drive/projects/mbg-exercise-client -w /Users/kmt/google_drive/projects/mbg-exercise-client -p 8888:8888 registry.gitlab.au.dk/au81667/mbg-docker-exercises:main ; docker attach kaspertes

# docker run -d --name topdemo alpine top -b

# docker attach topdemo

#docker run -d --name tester --rm --mount type=bind,source=/Users/kmt/.ssh,target=/tmp/.ssh --mount type=bind,source=/Users/kmt/.anaconda,target=/root/.anaconda --mount type=bind,source=/Users/kmt/google_drive/projects/mbg-exercise-client,target=/Users/kmt/google_drive/projects/mbg-exercise-client -w /Users/kmt/google_drive/projects/mbg-exercise-client -p 8888:8888 registry.gitlab.au.dk/au81667/mbg-docker-exercises:main -b

# docker run -d --name kaspertest --rm --mount type=bind,source=/Users/kmt/.ssh,target=/tmp/.ssh --mount type=bind,source=/Users/kmt/.anaconda,target=/root/.anaconda --mount type=bind,source=/Users/kmt/google_drive/projects/mbg-exercise-client,target=/Users/kmt/google_drive/projects/mbg-exercise-client -w /Users/kmt/google_drive/projects/mbg-exercise-client -p 8888:8888 registry.gitlab.au.dk/au81667/mbg-docker-exercises:main -b -t ; docker attach kaspertest

#     check_docker_running()

#     registry_listing = get_registry_listing()

# client.images.pull('kaspermunch/sap')

#     course_mapping = get_course_mapping()

#     course = get_user_input(course_mapping)

#     week_mapping = get_week_mapping()

#     check_no_other_exercise_container_running()

#     check_no_other_local_jupyter_running()

#     # https://docker-py.readthedocs.io/en/stable/
#     client = docker.from_env()
#     client.images.pull('nginx')
#     container = client.containers.run("bfirsh/reticulate-splines", detach=True)
#     for line in container.logs(stream=True):
#         print(line.strip())
#     container.stop()

#     launch_docker(course, week_mapping)

#     report_disk_space()

#     purge_docker_images_and_containers()


# #!/usr/bin/env python3

# import docker, getpass

# client = docker.from_env()

# my_pw = getpass.getpass(prompt='Password: ')

# sec_name = 'TestSec'
# noise = client.secrets.create(name=sec_name,  
#                               data=str.encode(my_pw))
# secret_id = client.secrets.list(filters={'name': sec_name})[0].id

# secRef = docker.types.SecretReference(secret_id, sec_name)

# print(type(secRef))

# client.services.create('alpine:latest',
#                        name='TestSvc',
#                        hostname='test_host',
#                        secrets=[secRef],
#                        command='sleep 999',)






# >>> import platform
# >>> platform.system()
# 'Darwin'
# >>> platform.processor()
# 'i386'
# >>> platform.platform()
# 'Darwin-10.8.0-i386-64bit'
# >>> platform.machine()
# 'i386'
# >>> platform.version()
# 'Darwin Kernel Version 10.8.0: Tue Jun  7 16:33:36 PDT 2011; root:xnu-1504.15.3~1/RELEASE_I386'
# >>> platform.uname()
# ('Darwin', 'Hostname.local', '10.8.0', 'Darwin Kernel Version 10.8.0: Tue Jun  7 16:33:36 PDT 2011; root:xnu-1504.15.3~1/RELEASE_I386', 'i386', 'i386')




# 1. Activate a MBGexercises environment  
# 2. Check for package updates of mbg-exercise-client package at the mbgexercises anaconda channel
# 3. Update package if necessary and reimport package after update to use new version  
# 4. Read registry listing using API requests library (see above)  
# 5. Read yml file mapping English to Danish course names (see above)
# 6. Take user input through to pick course
# 7. Read yml file mapping exercises to week numbers (see above)
# 8. Check that docker is installed
# 9. Check that docker is running  
# 10. Check that no other exercise container is running  
# 11. Check that no other local jupyter is using a port  
# 12. Launch docker run as a process in a separate thread (like in slurm-jupyter)  
# 13. Read URL from the output and launch the browser like in  (like in slurm-jupyter)  
# 14. Make sure the script cannot be shut down with keyboard interrupt or kill without cleaning up  
# 15. Report how much disk space images and containers currently use  
# 16. Ask to purge docker images and containers \[Y\]/n and do so  
# 17. Exit




# from collections import defaultdict
# from bullet import Bullet, colors, VerticalPrompt, SlidePrompt, ScrollBar, emojis

# options = dict(
#     indent = 0,
#     shift = 0,
#     align = 2, 
#     margin = 1,
#     # bullet = "★",
#     pointer = "★",
#     pad_right = 10,
#     height = 10,    
#     # bullet_color=colors.bright(colors.foreground["default"]),
#     word_color=colors.bright(colors.foreground["default"]),
#     word_on_switch=colors.bright(colors.foreground["green"]),
#     background_color=colors.background["default"],
#     background_on_switch=colors.background["default"],
#     return_index=False
# )

# image_name_list = [
#     'Biomolekylær_struktur_og_funktion-uge1-v1',
#     'Biomolekylær_struktur_og_funktion-uge2-v1',
#     'Bioinformatik_og_programmering-uge_1-v1',
#     'Bioinformatik_og_programmering-uge_2-v1',
# ]

# image_tree = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))
# for image_name in image_name_list:
#     c, w, v = image_name.split('-')
#     image_tree[c.replace('_', ' ')][w.replace('_', ' ')][v.replace('_', ' ')] = image_name

# # cli = ScrollBar(
# #     "How are you feeling today? ", 
# #     choices = list(image_tree.keys()) + ['asdf']*15,
# #     height = 15,
# #     **options
# # )
# # result = cli.launch()
# # print(result)

# cli = ScrollBar(prompt = "\n Select course: ", choices = list(image_tree.keys())*15, **options)
# course = cli.launch()
# cli = ScrollBar(prompt = "\n Select exercise: ", choices = list(image_tree[course].keys()), **options)
# week = cli.launch()
# cli = ScrollBar(prompt = "\n Select version: ", choices = list(image_tree[course][week].keys()), **options)
# version = cli.launch()
# selected_image = image_tree[course][week][version]


# # cli = SlidePrompt([
# #     Bullet(prompt = "\nSelect course: ", choices = list(image_tree.keys()), **options),
# #     Bullet(prompt = "\nSelect week: ", choices = list(image_tree[course].keys()), **options),
# #     Bullet(prompt = "\nSelect version: ", choices = list(image_tree[course][week].keys()), **options)
# # ])
# # course, week, version = cli.launch()
# # selected_image = image_tree[course][week][version]




# # course_menu = Bullet(
# #         prompt = "\nSelect course: ",
# #         choices = ["Biomolekylær struktur og funktion", "Bioinformatik og programmering", "orange", "watermelon", "strawberry"], 
# #         indent = 3,
# #         shift = 0,
# #         align = 3, 
# #         margin = 1,
# #         bullet = "★",
# #         # bullet_color=colors.bright(colors.foreground["cyan"]),
# #         # word_color=colors.bright(colors.foreground["yellow"]),
# #         # word_on_switch=colors.bright(colors.foreground["yellow"]),
# #         # background_color=colors.background["black"],
# #         # background_on_switch=colors.background["black"],
# #         pad_right = 10
# #     )
# # week_menu = Bullet(
# #         prompt = "\nSelect week: ",
# #         choices = ["week1", "week2"], 
# #         indent = 3,
# #         shift = 0,
# #         align = 3, 
# #         margin = 1,
# #         bullet = "★",
# #         # bullet_color=colors.bright(colors.foreground["cyan"]),
# #         # word_color=colors.bright(colors.foreground["yellow"]),
# #         # word_on_switch=colors.bright(colors.foreground["yellow"]),
# #         # background_color=colors.background["black"],
# #         # background_on_switch=colors.background["black"],
# #         pad_right = 10
# #     )


# # cli = VerticalPrompt([course_menu, week_menu], spacing = 0)

# # result = cli.launch()
# # print("You chose:", result)

# # # result = cli.launch()
# # # print(result)

# adapters
# api_version
# attach
# attach_socket
# auth
# base_url
# build
# cert
# close
# commit
# connect_container_to_network
# containers
# cookies
# copy
# create_container
# create_container_config
# create_container_from_config
# create_endpoint_config
# create_host_config
# create_network
# create_networking_config
# create_service
# create_swarm_spec
# create_volume
# delete
# diff
# disconnect_container_from_network
# events
# exec_create
# exec_inspect
# exec_resize
# exec_start
# export
# from_env
# get
# get_adapter
# get_archive
# get_image
# get_redirect_target
# head
# headers
# history
# hooks
# images
# import_image
# import_image_from_data
# import_image_from_file
# import_image_from_image
# import_image_from_stream
# import_image_from_url
# info
# init_swarm
# insert
# inspect_container
# inspect_image
# inspect_network
# inspect_node
# inspect_service
# inspect_swarm
# inspect_task
# inspect_volume
# join_swarm
# kill
# leave_swarm
# load_image
# login
# logs
# max_redirects
# merge_environment_settings
# mount
# networks
# nodes
# options
# params
# patch
# pause
# ping
# port
# post
# prepare_request
# proxies
# pull
# push
# put
# put_archive
# rebuild_auth
# rebuild_method
# rebuild_proxies
# remove_container
# remove_image
# remove_network
# remove_service
# remove_volume
# rename
# request
# resize
# resolve_redirects
# restart
# search
# send
# services
# should_strip_auth
# start
# stats
# stop
# stream
# tag
# tasks
# timeout
# top
# trust_env
# unpause
# update_container
# update_service
# update_swarm
# verify
# version
# volumes
# wait





    # # client = docker.Client(base_url='https://registry.hub.docker.com:443')
    # client = docker.Client(
    #     base_url='tcp://gitlab.au.dk:443',
    #     # base_url='tcp://gitlab.au.dk:443/api/v4/projects/au81667%2Fmbg-docker-exercises/registry/repositories',
    #     # credstore_env={'PRIVATE-TOKEN': 'glpat-tiYpz3zJ95qzVXnyN8--'}
    #     )
    # print(client.images())
    # print(client.search('au81667/mbg-docker-exercises'))
    # client.search('kaspermunch/sap')

#     # client = docker.Client(base_url='https://registry.hub.docker.com:443')
#     client = docker.Client(base_url='https://registry.gitlab.au.dk:443')

# #    client.images(name='kaspermunch/sap')
#     client.search('au81667/mbg-docker-exercises')

#    docker pull registry.gitlab.au.dk/au81667/mbg-docker-exercises:main




    # headers = {'PRIVATE-TOKEN': 'glpat-tiYpz3zJ95qzVXnyN8--'}
    # client.get('au81667/mbg-docker-exercises', **headers)



#registry.gitlab.au.dk/au81667/mbg-docker-exercises

    # print(dir(docker.constants))

#    print(client.pull('mbg-docker-exercises'))#, auth_config={'PRIVATE-TOKEN': 'glpat-tiYpz3zJ95qzVXnyN8--'}))
    # print(*dir(client), sep='\n')

    # noise = docker.secrets()#.create_secret(name='PRIVATE-TOKEN',  
    #                          #  data=str.encode('glpat-tiYpz3zJ95qzVXnyN8--'))

    # import  getpass
    # client = docker.from_env()
    # my_pw = getpass.getpass(prompt='Password: ')
    # sec_name = 'TestSec'
    # noise = docker.secrets.create(name=sec_name,  
    #                             data=str.encode(my_pw))
    # secret_id = docker.secrets.list(filters={'name': sec_name})[0].id

    # secRef = docker.types.SecretReference(secret_id, sec_name)

    # print(type(secRef))

    # client.services.create('alpine:latest',
    #                     name='TestSvc',
    #                     hostname='test_host',
    #                     secrets=[secRef],
    #                     command='sleep 999',)



