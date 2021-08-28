# Introduction

`template_tree` is an Ansible module that lets you
replicate a directory tree of templates and files from your local host to a
remote  host. It will automatically create directory entries where required, and
can optionally remove files not present in the source directory.

The main purpose of this module is to simplify the common scenario of
copying one or more local files to a target directory, checking for files that
were already present on the server but not on your host, and then removing those
files. In a way, it's like `rsync`, but for Ansible.

Let's say you want to create the following configuration structure on a
webserver:
```
/etc/nginx
├── http.conf.d
│   ├── site.conf
│   ├── wiki.conf
│   └── fileserver.conf
├── nginx.conf
├── ssl.conf
├── proxy_settings.conf
├── mime.types
└── ffdhe4096.pem

/srv/http/static
├── index.html
├── blog
│   ├── index.html
│   ├── post1.html
│   ├── post2.html
│   └── post3.html
└── about
    └── index.html
```
`http.conf.d` contains one configuration file for each site you want to serve.
These will be different on each host.

`nginx.conf` is the main nginx configuration file, which is largely the same on
each host, but needs to be templated with a few variables. The same applies to
`ssl.conf`.

`proxy_settings.conf` contains proxy header settings for reverse proxies. This
file has the same content on all hosts.

`/srv/http/static` contains static files served from one of your sites. The
contents of this directory will vary, with new directories and files being
added or removed over time.

Now, if your `httpserver` role looks like this:
```
files
├── hosts
│   └── webserver01
│       ├── sites
│       │   ├── site.conf
│       │   ├── wiki.conf
│       │   └── fileserver.conf
│       └── static_files
│           ├── index.html
│           ├── blog
│           │   ├── index.html
│           │   ├── post1.html
│           │   ├── post2.html
│           │   └── post3.html
│           └── about
│               └── index.html
└── ffdhe4096.pem

roles/httpserver
├── tasks
│   └── main.yml
├── files
    ├── mime.types
    └── proxy_settings.conf.j2
└── templates
    ├── nginx.conf.j2
    └── ssl.conf.j2
```
... then all you need is the following tasks to generate the aforementioned
nginx configuration structure.
```yaml
# tasks/main.yml

- name: Installing configuration files
  template_tree:
    # Look for files and templates in the following directories.
    # Their contents will be merged together into the destination directory.
    src:
    # These entries respect the Ansible search order, so the module will start
    # looking in the role directory before moving on to the play directory.
    # These directories are fetched from the role:
    - templates/
    - files/
    # This file is not present in the role, and is fetched from the play files.
    - ffdhe4096.pem
    # Copy or template discovered files to the following directory.
    dest: /etc/nginx
    # Any copied or templated files will receive the following mode.
    file_mode: 0644
    # Created directories will be set to this mode.
    directory_mode: 0755

- name: Installing websites
  template_tree:
    # No need to use a list if you only have a single source directory/file.
    src: hosts/{{ inventory_hostname_short }}/sites/
    dest: /etc/nginx/conf.d
    # Setting 'exclusive' to true will ensure any files not present on the local
    # host are removed from the destination directory.
    exclusive: true
    file_mode: 0644
    directory_mode: 0755

- name: Installing static files
  template_tree:
    # Add a trailing slash to directories to copy only their contents.
    # Leave the slash out to also generate the source directory on the host.
    # (just like rsync)
    src: hosts/{{ inventory_hostname_short }}/static_files/
    dest: /srv/http/static
    exclusive: true
    file_mode: 0644
    directory_mode: 0755
```

Note that any file ending with a `.j2` extension will be templated, and the
extension will be removed.

# Installation

Drop `template_tree.py` into your action plugin directory. Normally this will be
the `action_plugins` directory in the directory that contains your playbooks.

For more information, see [adding a plugin locally](https://docs.ansible.com/ansible/latest/dev_guide/developing_locally.html#adding-a-plugin-locally)
on Ansible.
