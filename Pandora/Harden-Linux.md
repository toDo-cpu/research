# Harden the system with style for fun and security

## Introduction

Why should you haden your linux system ? When you setup a computer you have to think about the compromises of usuability, performaces, and security. My goal here is to setup a secure system white performance. Because the server will have interfaces offered by services to use it. They are not going to maintain the server, I'm the only one.

Here this is a guide for people who are paranoiac about security, like you are going to store sensistive data on this server so it have to be secured. But what does that mean ?

For me a server should do 2 thing to be secured:
 - prevent from being compromised
 - minismise the compromission surface if it get compromised

Like we are never safe from vulnerabilities or user error. Even if you have the best anti virus and users are well formed you are not safe at 100%. As we always say: "the vulnerability is between the chair and the keyboard". So you must have protocols or think about the situation where on of your service is compromised. This is why I'm hardening the system. The minimize the attack surface and if a service is compromised minimize the impact on the system. This is the Principe of least privilege.

Before we start, let me introduce you some guidelines to harden your system, if a service or feature is not needed by your system, remove it. Do not harden production server before you had tested on a debug server. Also always do backup of your system and files.

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

**Lock user after multiple login attempts.**
**pam** by default lock a user for 10 minutes after 3 failed login attempt in 15 minutes. By default it is disable for root. So l'ets enable it and change the parameters:

```
faillock --user root --reset
```
Edit the file `/etc/security/faillock.conf` and change:
 - `unlock_time`: change the lockout time (in seconds).
 - `fail_interval`: the time in which the failed login can lock the user
 - `deny`: the number of failed login needed to lockout.
And to make this configuration persistent, change the parameter `dir` in `/etc/security/failloc.conf` to `/var/lib/faillock`.

**Delay between authentication**.

Add login delay between each authentication:
```
in /etc/pam.d/system-login
----------------------------

auth optional pam_faildelay.so delay=4000000
```
It add a delay of at least 4 secondes ( the number is given in microsecond)

**Use sudo instead of su**.

You should use sudo instead of su for theses reasons:
 - keep a log of which user as run privileged command
 - do not spawn a root shell, so prevent the exeuction of command which do not need to be run as root (remember **least privileges**)
 - You can allow a user to use a specific commands.

**Change the password asked by sudo.**
You should also force sudo to ask for the root password instead of the user password. So if a user which can execute sudo is compromised by an attacker. The attacker should find the root password instead the user password. you can change by adding `Defaults targetpw` in the `/etc/sudoers`. If you are afraid of brute force attack against the root password. You can restrict this to a specific group.

```
Defaults:%wheel targetpw
%wheel ALL=(ALL) ALL
```
rt 2. It weel restrict for the **wheel** group
> You should **always** edit `/etc/suddoers` with visudo, because before writing into the file, **visudo** will check for syntax. If the syntax is not correct sudo can not work.

**Disable root.**

Now you can disable root (but still use it with sudo) with
```
passwd --lock root
```
or you can do the next tips.

**Disable root login over ssh**.
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

**Administrate your users.**

Do you remember the principe of **least privileges** ? Well this part is important because we are going to manager our users.
So here is the plan. Remember **root** account is locked or we can not log into root with ssh
For my servers, I'm going to do this:
- 1 group named service which handle all service
- 1 user per service in group service, for example an user run/administrate **apache2** server. So it can access to **apache2.service**, access to apache logs. Dont set password to theses account. If you want to access to theses account use `sudo su {user}` instead. You can also add your ssh key in `/home/{user}/.ssh/authorized_keys` to manage remotly your service without connecting to the "master" user.
- 1 user named log-collector which get log and send them to a backup.
- 1 user to administrate all this stuff. This user can run sudo but not the other users

### Paswords

**Increase hash round for password.**

In order to increase the hash round perform by shadow. This will prevent that an attacker read the content of `/etc/shadow`, get the password hashes and bruteforce them. But in counterpart it will take longer to login.
For this edit `/etc/pam.d/passwd` and add this line:

```
password required pam_unix.so sha512 shadow nullok rounds=6000
```
Here I increased the number of round in the hash function to 6000 (default 5000).
Btw I highly recommend you to use sha512, it provide  the more longest hash.

> NOTE: the password are not updated automatically, you have to do it manually with `passwd`.

**Use a password manager**

Imagine, you have a fully hardened system. With crazy security stuff but you get hacked because you use 1 password and it have been leaked. This is very sad right ? And the attacker will pay a mickey of your head. So use a password manager to ensure that your password for opening the systeCPUm is unique and not reused. In the next article, I will show you how to setup the password manager **passbolt**. To create strong password, follow this [guide](https://wiki.archlinux.org/title/Security#Passwords) from the arch wiki.

**Remove `pam_ccreds`**

The package `pam_ccreds` is responsible for caching password.  If an attacker obtain control of the system, he can compromise cached password.


## 3. System

### Processes

**Limit the amount of process per users**
To prevent fork bombs or ddos, you can limit the number of process that a use can spwan.
Add this line to `/etc/security/limits.conf`:

```
* soft nproc 100
* hard nproc 200
```
It will set a limit of 100 process per user, this number can be increased to 200 with `prlimit`

### Filesystem

**Prevent hardlink and symlink issue**

There is security issues with hardlinks and symlink and the kernel prevent theses issue. Ensure thath `fs.protected_hardlinks` and `fs.protected_symlinks` sysctl switches are enable.

**Disable Network Filesystemes**

```
# chkconfig nfslock off
# chkconfig rpcgssd off
# chkconfig rpcidmapd off
# chkconfig netfs off
```

To check if you have mounted Net Filesystems : `# mount -t nfs,nfs4,smbfs,cifs,ncpfs`

### Disks

**Use quotas**

You should also take care of disk usage by directory like `/var` of `/tmp` which can take down services. To prevent this we are going to use quotas: from [wikipedia](https://en.wikipedia.org/wiki/Disk_quota) "A disk quota is a limit set by a system administrator that restricts certain aspects of file system usage on modern operating systems. The function of using disk quotas is to allocate limited disk space in a reasonable way."
//TODO

**Mount with less prvilieges**
You can mount a volume options like `nodev` which don't interpret char actor or block special device on this filesystem.
Here are the most relevant for what we need:

 - `nodev`
 - `nosuid`: Do not allow set-user-identifier or set-group-identifier bits to take effect.
 - `noexec`: Do not allow direct execution of any binaries on the mounted file system.
> Stolen from archlinux [wiki](https://wiki.archlinux.org/title/Security#Mount_options).
You should always mount your filesystem used for data with `nodev`, `nosuid`, `noexec`.
Imagine you have a sftp server which use a mounted drive at `/mnt/sftp-storage`. You mount it with:
```
sudo mount --mkdir noexec nodev nosuid /dev/XXX /mnt/sft-storage
sudo genfstab >> /etc/fstab
```
Now imagine your there is a vulnerability in your sftp server which allow an attacker to execute file stored on the sftp server. This will prevent this.

For the common path you should follow theses instructions:

- `nodev` for non root local partition
- `nodev`, `nosuid`,`noexec` for removable sotarge partitions. You can find removable media in the fstab which contain strings like `floppy` or `cdrom`
- `nodev`, `nosuid`, `noexec` for `/tmp` and `/dev/shm`



**Disable unkown filesystems**

To prevent for mounting uncommon filesystems, add theses lines to `/etc/modprobe.conf`

```
install cramfs /bin/true
install freevxfs /bin/true
install jffs2 /bin/true
install hfs /bin/true
install hfsplus /bin/true
install squashfs /bin/true
install udf /bin/true
```

**File permissions**

**Verify permissions of sensible files**

Run this  as root. This is the default permissions for theses files. some utilities need to access t `passwd` file but not `shadow` which contain the hashed passwords.

```
cd /etc
chown root:root passwd shadow group gshadow
chmod 644 passwd group
chmod 400 shadow gshadow
```

**Find non well configured files**

The [NSA rhel5 hardening](https://web.archive.org/web/20160307150120/http://www.nsa.gov/ia/_files/os/redhat/rhel5-guide-i731.pdf) guide provide a good sections for the configuration of files.

To find world-writable directories which do not have the sticky bit, use:

```# find PART -xdev -type d \( -perm -0002 -a ! -perm -1000 \) -print```

> World-Writable files are files which can be modified by any user on the system

To find all world-writable files:

```# find PART -xdev -type f -perm -0002 -print```

To find **SUID**/**SGID** file run:

```# find PART -xdev \( -perm -4000 -o -perm -2000 \) -type f -print```

To find the files which do not have owner run:

```find PART -xdev \( -nouser -o -nogroup \) -print```

## 4. Network configuration

**Disable network functionalities**

If you server is not a **firewall**, **gateway** or any service which pass IP traffic between network. Add theses lines to `/etc/sysctl.conf`:

```net.ipv4.ip forward = 0
net.ipv4.conf.all.send redirects = 0
net.ipv4.conf.default.send redirects = 0
```

Add theses lines to `/etc/sysctl.conf`:

```net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_messages = 1
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

```

From the NSA guide:

```These options improve Linux’s ability to defend against certain types of IPv4 protocol attacks.
The accept source route, accept redirects, and secure redirects options are turned off to disable IPv4
protocol features which are considered to have few legitimate uses and to be easy to abuse.
The net.ipv4.conf.all.log martians option logs several types of suspicious packets, such as spoofed packets,
source-routed packets, and redirects.
The icmp echo ignore broadcasts icmp ignore bogus error messages options protect against ICMP attacks.
The tcp syncookies option uses a cryptographic feature called SYN cookies to allow machines to continue to
accept legitimate connections when faced with a SYN flood attack. See [13] for further information on this option.
The rp filter option enables RFC-recommended source validation. It should not be used on machines which
are routers for very complicated networks, but is helpful for end hosts and routers serving small networks.
For more information on any of these, see the kernel source documentation file
/Documentation/networking/ip-sysctl.txt.2
```

**Disable wireless functionnalities**:

If your system is not a laptop and don't need the wireless, disable it:

- physically by removing your wifi card (you can inspect your hadrware with `lspci` and `lsusb`) 

- Remove wireless interface, use `ifconfig -a` and `iwconfig`. Then remove the file `/etc/sysconfig/network-scripts/ifcfg-{interface}` with your wireless interface to remove it. You can then remove the kernel driver reponsible for supporting wireless Ethernet decies : `rm -r /lib/modules/kernelversion(s) /kernel/drivers/net/wireless`

  > You must run the last command every time the kernel is upgrade

- Disable IPv6 if your system don't use i, add this line `install ipv6 /bin/true` to`/etc/modprobe.conf`

  Also to prevent the configuration of IPv6 for interfaces, add theses 2 lines in to `/etc/sysconfig/network`:

  - `NETWORKING_IPV6=no`
  - `IPV6INIT=no`

- use and configure`iptables`

- Disable uncommon protocoles if your system do not use theme, add theses lines into `/etc/modprobe.conf`

  - `install dccp /bin/true` Disable `DCCP`
  - `install sctp /bin/true` Disable `SCTP`
  - `install rds /bin/true` Disable `RDS`
  - `install tipc /bin/true` Disable `TIPC`

## 5. Use logs

Check section `2.6` of the NSA guide cnfigure logging

## 6. Services

Here we are going to secure the servics running on our server.

#### OpenSSH

The configuration file is located in ` /etc/ssh/sshd_congif`

- Ensure protocol 2 is used. Check for the line `Protocol 2` 
- You can deny the access of use through ssh: `DenyUsers USER1 USER2`
- Disable empty password `PermitEmptyPassword no`
- Disable root login `PermitRootLogin no`
- Disable host based authentication `HostbasedAuthentication no`
- Disable unsecure access through `rsh`: `IgnoreRhosts yes`
- Configure `iptables` rule according to the usage of ssh 

#### DHCP

If you do not need `DHCP`, configure your interface to use static ip. 

For each interfaces **INTERFACE** edit `/etc/sysconfig/network-scripts/ifcfg-INTERFACE`:

- `BOOTPROTO=statis`
- configure your ip addr, gateway and netmask with:
  - `NETMASK: 255.255.255.0`
  - `IPADDR: 192.168.1.3`
  - `GATEWAY: 192.168.1.1`

#### Bind9

- Run DNS in `chroot` jail ( see package `bind-chroot`)

##  Sources

 - https://wiki.archlinux.org/title/Security
 - [https://theprivacyguide1.github.io/linux\_hardening\_guide#kernel](https://theprivacyguide1.github.io/linux\_hardening\_guide#kernel)
 - [NSA rhel5 guide](https://web.archive.org/web/20160307150120/http://www.nsa.gov/ia/_files/os/redhat/rhel5-guide-i731.pdf)
 - 

