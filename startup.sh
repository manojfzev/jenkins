#!/bin/bash
user=ciscat-user
useradd $user -m
mkdir /home/$user/.ssh
chmod 700 /home/$user/.ssh
touch /home/$user/.ssh/authorized_keys
chmod 644 /home/$user/.ssh/authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDsYmUjfIExHZ4vftoKch1txL3/tTRQSXyXNhrs/ouvJO6YV/rIdijIaCGgEprZSPL+BRY9iMYbVUb2nMaxCeAhx07JdhSeBYuoMwamKxTKTmXF81yqRUMfmhiZrljCCB1llEzwongNr0liodvlKscu0abSbixBir58WZd8eyOcjdsuKH/IIvxmIUW8oBL3d3tU5KpubkUo2mYIvWXTzstA3IVxECKyfKUFc8PrVGeS9C7BDgvRnaF7Ez42wmbWAVcIl2CsSKMMpikOsh84S0BfxrfCiedt1uZ3HYxy15CKWAs8I4/eVl4BkyYRWz2UXRYqWX5gAVwBB+4Tr4HFmC9X root@clops-jenkins-slave-template-1" >> /home/$user/.ssh/authorized_keys
chown -R $user:$user /home/$user/.ssh
echo "$user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers


