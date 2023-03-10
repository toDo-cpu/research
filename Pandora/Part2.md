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

**Block root auth with su**
On BSD, by default only members of the `wheel` group can `su` to root. And this is not the default of GNU `su`. To enable this feature uncomment the line:
```
auth required pam_wheel.so use_uid
```
in `/etc/pam.d/su` and `/etc/pam.d/su-l`.

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
You should also force sudo to ask for the root password instead of the user password. So if a user which can execute sudo is compromised by an attacker. The attacker should find the root password instead the user password. you can change by adding `Defaults targetpw` in the `/etc/sudoers`. If you are afraid of bruteforce attack against the root password. You can restrict this to a specific group.
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
The well known no root login on ssh, open `/etc/ssh/sshd_config` and edit:
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
Imagin, you have a fully hardened system. With crasy security stuff but you get hacked because you use 1 password and it have been leaked. This is very sad right ? And the attacker will pay a mickey of your head. So use a password manager to ensure that your password for opening the system is unique and not reused. In the next article, I will show you how to setup the password manager **passbolt**. To create strong password, follow this [guide](https://wiki.archlinux.org/title/Security#Passwords) from the arch wiki.


## 3. Storage

### Filesystem

**Prevent hardlink and symlink issue**
There is security issues with hardlinks and symlink and the kernel prevent theses issue. Ensure thath `fs.protected_hardlinks` and `fs.protected_symlinks` sysctl switches are enable.

### Disks

**Use quotas**
You should also take care of disk usage by directory like `/var` of `/tmp` which can take down services. To prevent this we are going to use quotas: from [wikipedia](https://en.wikipedia.org/wiki/Disk_quota) "A disk quota is a limit set by a system administrator that restricts certain aspects of file system usage on modern operating systems. The function of using disk quotas is to allocate limited disk space in a reasonable way."
//TODO

**Mount with less prvilieges**
//TODO

**File encryption**
//TODO

**

## 4. Softwares

### Kernel
> Some tips can slow your system

**Use a hardened kernel**
You can use the `linux-hardened` package, which use a basic kernel hardening patch set ([see](https://wiki.archlinux.org/title/Security#Kernel_self-protection_/_exploit_mitigation)). But as I said before you can made a custom build for your kernel. The package also provided an improvement for the **ASLR** in usersapce.

**Hinding kernel symbols**
Some local root exploit use `/proc/kallsyms` which list all the kernel symbols and their address to perform attack on the kernel. You can disable the showing of `/proc/kallsyms` by setting the line `kernel.ptr_restrict` to 1 or 2 (2 for nobody can see it) in `/etc/sysctl.d/51-kptr-restrict.conf`.
> Program which use the `/proc/kallsyms` run as non root wont work anyway.

**Protect your kernel from BPF**
**BPF** or **eBPF** is a technology created to log event in the kernel. It attach to `tracepoint`, `kprobes` and other tracing thecnlogies. The BPF are run im a VM in the kernel. And as unprivilieged user, you can run a bpf in the vm. Which is very dangerous and expose directly your kernel. To prevent set the line:
```
kernel.unprivileged_bpf_disabled
```
to `1` in `/etc/sysctl.d/51-kptr-restrict.conf`.
You can also harden the **JIT** which mitigate some spraying attack but it will cost performance et the ability to debug the **eBPF**. So if your server use **eBPF** techology use it at your risk. To harden change the value of `/proc/sys/net/core/bpf_jit_harden` to `1`.

**Id your pid**
By default, every process can see the pid of other process (maybe not for privileged but I'm not sure. You can see them in `/proc`. This complicate the task of the ressource gathering when an attacker gain the access to your system and search to escalate the privileges. To hide pid, you have to mount `/proc` with ``hidepid=2`, `gid=proc` argument in the fstab. This is documented here `https://docs.kernel.org/filesystems/proc.html`. If you want to add a user to the whitelist add the user to `proc` group.
```
proc	/proc	proc	nosuid,nodev,noexec,hidepid=2,gid=proc	0	0
```
And to enable the whitelist, and the exception to `/etc/systemd/system/systemd-logind.service.d/hidepid.conf`:
```
[Service]
SupplementaryGroups=proc
```

**Disable the LKM loading**
**LKM** are driver which can be loaded dymiacly in the kernel during the runtime. Rootkit are often **LKM**. You can disable it by set `module.sig_enforce=1` ot the kernel parameter (see with your bootloader). Ensure that `CONFIG_MODULE_SIG_ALL` is set when compiling the kernel.

**Disable Kexec**
Kexec allow you to replace the running kernel. I think I dont have to explain why this is critic
Set `kernel.kexec_load_disabled` to `1` in `/etc/sysctl.d/51-kexec-restrict.conf`.

**Enable lockdown mode**
//TODO

## Sources
 - https://wiki.archlinux.org/title/Security
 - https://theprivacyguide1.github.io/linux\_hardening\_guide#kernel
