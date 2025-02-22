#@title **Create User**
#@markdown Enter Username and Password

import os

username = "user" #@param {type:"string"}
password = "root" #@param {type:"string"}

print("Creating User and Setting it up")

# Creation of user
os.system(f"useradd -m {username}")

# Add user to sudo group
os.system(f"adduser {username} sudo")
    
# Set password of user to 'root'
os.system(f"echo '{username}:{password}' | sudo chpasswd")

# Change default shell from sh to bash
os.system("sed -i 's/\/bin\/sh/\/bin\/bash/g' /etc/passwd")

print(f"User created and configured having username `{username}` and password `{password}`")


#@title **RDP**
#@markdown  It takes 4-5 minutes for installation

import os
import subprocess

#@markdown  Visit http://remotedesktop.google.com/headless and copy the command after Authentication

CRP = "DISPLAY= /opt/google/chrome-remote-desktop/start-host --code=\"4/0ARtbsJpGAEBvUmSxaKWbiGIPhjR9vGOjUJyzB3esRFHPyf8nh2tt0XYMdUnfaA2YH7yhXg\" --redirect-url=\"https://remotedesktop.google.com/_/oauthredirect\" --name=$(hostname)" #@param {type:"string"}

#@markdown Enter a Pin (more or equal to 6 digits)
Pin = 123456 #@param {type: "integer"}

#@markdown Autostart Notebook in RDP
Autostart = False #@param {type: "boolean"}


class CRD:
    def __init__(self, user):
        os.system("apt update")
        self.installCRD()
        self.installDesktopEnvironment()
        self.installGoogleChorme()
        self.finish(user)
        print("\nRDP created succesfully move to https://remotedesktop.google.com/access")

    @staticmethod
    def installCRD():
        print("Installing Chrome Remote Desktop")
        subprocess.run(['wget', 'https://dl.google.com/linux/direct/chrome-remote-desktop_current_amd64.deb'], stdout=subprocess.PIPE)
        subprocess.run(['dpkg', '--install', 'chrome-remote-desktop_current_amd64.deb'], stdout=subprocess.PIPE)
        subprocess.run(['apt', 'install', '--assume-yes', '--fix-broken'], stdout=subprocess.PIPE)

    @staticmethod
    def installDesktopEnvironment():
        print("Installing Desktop Environment")
        os.system("export DEBIAN_FRONTEND=noninteractive")
        os.system("apt install --assume-yes xfce4 desktop-base xfce4-terminal")
        os.system("bash -c 'echo \"exec /etc/X11/Xsession /usr/bin/xfce4-session\" > /etc/chrome-remote-desktop-session'")
        os.system("apt remove --assume-yes gnome-terminal")
        os.system("apt install --assume-yes xscreensaver")
        os.system("systemctl disable lightdm.service")

    @staticmethod
    def installGoogleChorme():
        print("Installing Google Chrome")
        subprocess.run(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"], stdout=subprocess.PIPE)
        subprocess.run(["dpkg", "--install", "google-chrome-stable_current_amd64.deb"], stdout=subprocess.PIPE)
        subprocess.run(['apt', 'install', '--assume-yes', '--fix-broken'], stdout=subprocess.PIPE)

    @staticmethod
    def finish(user):
        print("Finalizing")
        if Autostart:
            os.makedirs(f"/home/{user}/.config/autostart", exist_ok=True)
            link = "https://colab.research.google.com/github/PradyumnaKrishna/Colab-Hacks/blob/master/Colab%20RDP/Colab%20RDP.ipynb"
            colab_autostart = """[Desktop Entry]
Type=Application
Name=Colab
Exec=sh -c "sensible-browser {}"
Icon=
Comment=Open a predefined notebook at session signin.
X-GNOME-Autostart-enabled=true""".format(link)
            with open(f"/home/{user}/.config/autostart/colab.desktop", "w") as f:
                f.write(colab_autostart)
            os.system(f"chmod +x /home/{user}/.config/autostart/colab.desktop")
            os.system(f"chown {user}:{user} /home/{user}/.config")

        os.system(f"adduser {user} chrome-remote-desktop")
        command = f"{CRP} --pin={Pin}"
        os.system(f"su - {user} -c '{command}'")
        os.system("service chrome-remote-desktop start")
        

        print("Finished Succesfully")


try:
    if CRP == "":
        print("Please enter authcode from the given link")
    elif len(str(Pin)) < 6:
        print("Enter a pin more or equal to 6 digits")
    else:
        CRD(username)
except NameError as e:
    print("'username' variable not found, Create a user first")
    
    
    #@title **SSH**

! pip install colab_ssh --upgrade &> /dev/null

#@markdown Choose a method (Agro Recommended)
ssh_method = "Ngrok" #@param ["Agro", "Ngrok"]


#@markdown Copy authtoken from https://dashboard.ngrok.com/auth (only for ngrok)
ngrokRegion = "us" #@param ["us", "eu", "ap", "au", "sa", "jp", "in"]

def runAgro():
    from colab_ssh import launch_ssh_cloudflared
    launch_ssh_cloudflared(password=password)

def runNgrok():
    from colab_ssh import launch_ssh
    from IPython.display import clear_output

    import getpass
    ngrokToken = "1yoSDwXI4Oqpk1SnfujML1bBNvK_4btx6DesZDkQzSaPE5GYU"

    launch_ssh(ngrokToken, password, region=ngrokRegion)
    clear_output()

    print("ssh", user, end='@')
    ! curl -s http://localhost:4040/api/tunnels | python3 -c \
            "import sys, json; print(json.load(sys.stdin)['tunnels'][0]['public_url'][6:].replace(':', ' -p '))"

try:
    user = username
    password = password
except NameError:
    print("No user found, using username and password as 'root'")
    user='root'
    password='root'


if ssh_method == "Agro":
    runAgro()
if ssh_method == "Ngrok":
    runNgrok()
