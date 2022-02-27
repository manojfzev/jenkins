#!/bin/bash
user=ciscat-user
useradd $user -m
mkdir /home/$user/.ssh
chmod 700 /home/$user/.ssh
touch /home/$user/.ssh/authorized_keys
chmod 644 /home/$user/.ssh/authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC9XVqoscJ2iUL01u9G1iCGyESMTnMfF/goMbfNHvVAF89FvAZsjHVqmqMMS8PREI0ZCkxo7ZU2gG8k0BqLoYLtFGPnGuhPlNon+dEULj9sPpTz1AdxyeQ1ZgktBGl+WP/FHVnZ70OPiP7znFQqV5hFh5JfMoaQ6luxJzcHoPpmJK+L/PBf6gMxpgk2GIKq2a/3AnTJqK6QlPzzzG73plLRZ0BtVciOmH6IOhCs7r+FLyoL1WzZUHDZ5yEkPfkpA6/ItXT6GYrTKEcNyTI/i2VQk+cO0uMDLsngIF0VLtrZZEmMyrkDkLHT+tD9wGghzD0Vb8fvGv9xQtiOB7IVCiA1 root@cis-cat-host" >> /home/$user/.ssh/authorized_keys
chown -R $user:$user /home/$user/.ssh
echo "$user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers


