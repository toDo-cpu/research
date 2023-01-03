# Part 2. Harden the system with style for fun and security

## Introduction

Why should you haden your linux system ? When you setup a computer you have to think about the compromises of usuability, performaces, and security. My goal here is to setup a secure system white performance. Because the server will have interfaces offered by services to use it. They are not going to maintain the server, I'm the only one.

Here this is a guide for people who are paranoiac about security, like you are going to store sensistive data on this server so it have to be secured. But what does that mean ?

For me a server should do 2 thing to be secured:
 - prevent from being compromised
 - minismise the compromission surface if it get compromised

Like we are never safe from vulnerabilities or user error. Even if you have the best antivirus and users are well formed you are not safe at 100%. As we always say: "the vulnerabilitiy is betweem the chair and the keyboard". So you must have protocols or think abouth the situation where on of your service is compromised. This is why I'm hardenning the system. The minimize the attack surface and if a service is compromised minimize the impact on the system. This is the principe of leat privilege

## 1. Hardware

### CPU

**Microcode**

To install security update, you have to install your CPU's microcode, microcode is "a layer of hardware level instruction that implement higher-level instruction" following [wikipedia](https://en.wikipedia.org/wiki/Microcode). Theses are  a layer of security provided by your processor manufacturer. To install theses:
```
sudo pacman -S intel-ucode
sudo pacman -S amd-ucode
```
Depending on your cpu. After you can enable early loading of microcode [here](https://wiki.archlinux.org/title/Microcode#Early_loading) or you can enable it later.I' gonna load theses later because I have to reconfigure the kernel and I'm a little busy.

## 2. User management

### Authentication

**Lock user after multiple login attempts**
**pam** by default lock a user for 10 minutes after 3 failed login attempt in 15 minutes. By default it is disable for root. So l'ets enable it and change the parameters:
```
faillock --user root --reset
```
Edit the file `/etc/security/faillock.conf` and change:
 - `unlock_time`: change the lockout time (in seconds).
 - `fail_interval`: the time in which the failed login can lock the user
 - `deny`: the number of failed login needed to lockout.
And to make this configuration persistent, change the parameter `dir` in `/etc/security/failloc.conf` to `/var/lib/faillock`.

**Delay between auth**

Add login delay between each authentication:
```
in /etc/pam.d/system-login
----------------------------

auth optional pam_faildelay.so delay=4000000
```
It add a delay of at least 4 secondes ( the number is given in microsecond)

**Use sudo instead of su**

You should use sudo instead of su for theses reasons:
 - keep a log of which user as run privileged command
 - do not spawn a root shell, so prevent the exeuction of command which do not need to be run as root (remember **least privileges**)
 - You can allow a user to use a specific commands.

**Change the password asked by sudo**
<<<<<<< HEAD
You should also force sudo to ask for the root password instead of the user password. So if a user which can execute sudo is compromised by an attacker. The attacker should find the root password instead the user password. you can change by adding `Defaults targetpw` in the `/etc/sudoers`. If you are afraid of bruteforce attack against the root password. You can restrict this to a specific group.
=======

You should also force sudo to ask for
the root password instead of the user password. So if a user which can execute sudo is compromised by an attacker. The attacker should find the root password instead the user password. you can change by adding `Defaults targetpw` in the `/etc/sudoers`. If you are afraid of bruteforce attack against the root password. You can restrict this to a specific group.
>>>>>>> 6a71765 (fix typo)
```
Defaults:%wheel targetpw
%wheel ALL=(ALL) ALL
```
It weel restrict for the **wheel** group
> You should **always** edit `/etc/suddoers` with visudo, because before writing into the file, **visudo** will check for syntax. If the syntax is not correct sudo can not work.

**Disable root**

Now you can disable root (but still use it with sudo) with
```
passwd --lock root
```
or you can do the next tips

**Disable root login over ssh**
<<<<<<< HEAD
The well known no root login on ssh, open `/etc/ssh/sshd_config` and edit:
=======

The well known no root login on ssh, open `/etc/sshd/sshd_config` and edit:
>>>>>>> 6a71765 (fix typo)
```
# Authentication:

#LoginGraceTime 2m
PermitRootLogin no
#StrictModes yes
#MaxAuthTries 6
#MaxSessions 10
```
So now to administrate the system you have to use `sudo su` or to run sudo with privileged user.

**Administrate your users**

Do you remember the principe of **least privileges** ? Well this part is important because we are going to manager our users.
So here is the plan. Remember **root** account is locked or we can not log into root with ssh
For my servers, I'm going to do this:
- 1 group named service which handle all service
- 1 user per service in group service, for example an user run/administrate **apache2** server. So it can access to **apache2.service**, access to apache logs. Dont set password to theses account. If you want to access to theses account use `sudo su {user}` instead. You can also add your ssh key in `/home/{user}/.ssh/authorized_keys` to manage remotly your service without connecting to the "master" user.
- 1 user named log-collector which get log and send them to a backup.
- 1 user to administrate all this stuff. This user can run sudo but not the other users

### Paswords

**Increase hash round for password**

In order to increase the hash round perform by shadow. This will prevent that an attacker read the content of `/etc/shadow`, get the password hashes and bruteforce them. But in counterpart it will take longer to login.
For this edit `/etc/pam.d/passwd` and add this line:
```
password required pam_unix.so sha512 shadow nullok rounds=6000
```
Here I increased the number of round in the hash function to 6000 (default 5000).
Btw I higlhy recommend you to use sha512, it provid  the more longest hash
> NOTE: the password are not updated autmatically, you have to do it manually with `passwd`.

**Use a password manager**

Imagine, you have a fully hardened system. With crasy security stuff but you get hacked because you use 1 password and it have been leaked. This is very sad right ? And the attacker will pay a mickey of your head. So use a password manager to ensure that your password for opening the system is unique and not reused. In the next article, I will show you how to setup the password manager **passbolt**. To create strong password, follow this [guide](https://wiki.archlinux.org/title/Security#Passwords) from the arch wiki.


## 3. System

##Processes

**Limit the amount of process per users**
To prevent fork bombs or ddos, you can limit the number of process that a use can spwan.
Add this line to `/etc/security/limits.conf`:
```
* soft nproc 100
* hard nproc 200
```
It will set a limit of 100 process per user, this number can be increased to 200 with `prlimit`

**
### Filesystem

**Prevent hardlink and symlink issue**

There is security issues with hardlinks and symlink and the kernel prevent theses issue. Ensure thath `fs.protected_hardlinks` and `fs.protected_symlinks` sysctl switches are enable.

### Disks

**Use quotas**

You should also take care of disk usage by directory like `/var` of `/tmp` which can take down services. To prevent this we are going to use quotas: from [wikipedia](https://en.wikipedia.org/wiki/Disk_quota) "A disk quota is a limit set by a system administrator that restricts certain aspects of file system usage on modern operating systems. The function of using disk quotas is to allocate limited disk space in a reasonable way."
//TODO

**Mount with less prvilieges**
You can mount a volume options like `nodev` which don't interpret charactor or block special device on this filesystem.
Here are the most relevant for what we need:
 - `nodev`
 - `nosuid`: Do not allow set-user-identifier or set-group-identifier bits to take effect.
 - `noexec`: Do not allow direct execution of any binaries on the mounted file system.
> stolen from archlinux [wiki](https://wiki.archlinux.org/title/Security#Mount_options)
You should always mount your filesystem used for data with `nodev`, `nosuid`, `noexec`.
Imagine you have a sftp server which use a mounted drive at `/mnt/sftp-storage`. You mount it with:
```
sudo mount --mkdir noexec nodev nosuid /dev/XXX /mnt/sft-storage
sudo genfstab >> /etc/fstab
```
Now imagine your there is a vulnerability in your sftp server which allow an attacker to execute file stored on the sftp server. This will prevent this.

**File permissions**
//TODO




## Sources
 - https://wiki.archlinux.org/title/Security
 - https://theprivacyguide1.github.io/linux\_hardening\_guide#kernel
