# Ansible + Netmiko Lab — README

## Purpose
Step-by-step guide to create a GCP control VM, install Ansible + Netmiko, configure SSH/VPN access, run config push and backups for Cisco IOS‑XR and Nexus (NX‑OS) devices, and automate nightly backups.

This README assumes you have a GCP account and access to the Cisco devices (via public IPs or VPN). Replace placeholders like `<PROJECT_ID>`, `<ZONE>`, `<EXTERNAL_IP>`, `<YOUR_VPN_HOST>`, `<VAULT_PASS>` with real values.

---

## Table of Contents
1. Prerequisites  
2. Create GCP VM (Console + gcloud shown)  
3. Create & use SSH key to connect from local → GCP VM  
4. (Optional) Connect Cisco VPN from the GCP VM  
5. Prepare VM: directories, Python venv, install Ansible/Netmiko/collections  
6. Files & folder layout (what to put where)  
7. Encrypt credentials with Ansible Vault  
8. Run playbooks (config push & backup)  
9. Automate backups with cron (safe vault usage)  
10. Troubleshooting (common errors & fixes)  
11. Useful verification commands  
12. Next steps / production tips  

---

## 1. Prerequisites
- A Google Cloud account with billing enabled (or free-tier eligible)  
- `gcloud` CLI installed locally (optional — you can use GCP Console)  
- Local machine with `ssh` client (Linux/macOS/WSL)  
- Access to Cisco devices (direct IPs or reachable via VPN)  

---

## 2. Create a GCP VM

### Option A — Console
- Go to **Compute Engine → VM instances → Create Instance**  
- Name: `ansible-control`  
- Region / Zone: e.g. `us-central1-a`  
- Machine type: `e2-medium (2 vCPU / 4 GB)`  
- Boot disk: Ubuntu 22.04 LTS (or 20.04)  
- Firewall: Allow SSH  

### Option B — gcloud CLI
```bash
gcloud auth login
gcloud config set project <PROJECT_ID>

gcloud compute instances create ansible-control   --zone=<ZONE>   --machine-type=e2-medium   --image-family=ubuntu-2204-lts   --image-project=ubuntu-os-cloud   --boot-disk-size=20GB
```

Get the external IP:
```bash
gcloud compute instances describe ansible-control --zone=<ZONE>   --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
```

---

## 3. Create SSH Key Pair & Connect
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/gcp_key -C "ansible-control"
ssh -i ~/.ssh/gcp_key <YOUR_USERNAME>@<EXTERNAL_IP>
```

If you used GCP Console to paste the public key, use the username from that line.

---

## 4. Connect Cisco VPN (if needed)
- Install OpenConnect:
```bash
sudo apt update && sudo apt install -y openconnect
sudo openconnect --user=<VPN_USERNAME> <YOUR_VPN_HOST>
```
For persistent site-to-site IPsec, use **strongSwan** (consult your team).

---

## 5. Prepare the VM
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git ssh

mkdir -p ~/ansible-netmiko-lab/backups ~/ansible-netmiko-lab/logs
cd ~/ansible-netmiko-lab

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install ansible netmiko paramiko ansible-pylibssh

ansible-galaxy collection install cisco.ios cisco.iosxr cisco.nxos ansible.netcommon
```

---

## 6. Files & Folder Layout
```
ansible-netmiko-lab/
├─ config_push.yml
├─ backup_config.yml
├─ inventory.ini
├─ creds.yml
├─ backups/
├─ logs/
└─ venv/
```

Example `inventory.ini`:
```ini
[cisco_routers]
ios_xrv ansible_host=10.10.20.35 ansible_network_os=iosxr ansible_connection=network_cli

[cisco_switches]
nexus9k ansible_host=10.10.20.40 ansible_network_os=nxos ansible_connection=network_cli
```

---

## 7. Encrypt Credentials with Ansible Vault
```bash
ansible-vault create creds.yml
ansible-vault encrypt creds.yml
ansible-vault edit creds.yml
```

Run with vault:
```bash
ansible-playbook -i inventory.ini config_push.yml --ask-vault-pass
```

For cron jobs:
```bash
echo "<VAULT_PASSWORD>" > ~/.vault_pass.txt
chmod 600 ~/.vault_pass.txt
ansible-playbook -i inventory.ini backup_config.yml --vault-password-file ~/.vault_pass.txt
```

---

## 8. Run the Playbooks
```bash
source ~/ansible-netmiko-lab/venv/bin/activate
cd ~/ansible-netmiko-lab

ansible-playbook -i inventory.ini config_push.yml --ask-vault-pass
ansible-playbook -i inventory.ini backup_config.yml --ask-vault-pass
```

---

## 9. Automate Backups with Cron
Example (runs nightly at 02:00):
```bash
0 2 * * * /home/<youruser>/ansible-netmiko-lab/venv/bin/ansible-playbook   -i /home/<youruser>/ansible-netmiko-lab/inventory.ini   /home/<youruser>/ansible-netmiko-lab/backup_config.yml   --vault-password-file /home/<youruser>/.vault_pass.txt   >> /home/<youruser>/ansible-netmiko-lab/logs/backup_$(date +\%F).log 2>&1
```

---

## 10. Troubleshooting
- **SSH peer issues** → Add to `~/.ssh/config`:
  ```
  Host 10.10.20.35
      HostKeyAlgorithms +ssh-dss
      StrictHostKeyChecking no
  ```
- **Module errors on XR** → Use `iosxr_config` (not `ios_config`)  
- **NXOS VLAN errors** → Use `parents:` in YAML  
- **Missing collections** → Install with:
  ```bash
  ansible-galaxy collection install cisco.ios cisco.iosxr cisco.nxos ansible.netcommon
  ```

---

## 11. Useful Verification Commands
```bash
ansible -i inventory.ini cisco_routers -m ping
ansible -i inventory.ini cisco_switches -m ping
ssh developer@10.10.20.35
show running-config | include hostname
```

---

## 12. Next Steps & Production Tips
- Store configs in a Git repo  
- Use Ansible AWX/Tower for credential management  
- Use centralized logging or S3/GCS for DR backups  
- Rotate device credentials regularly  
- Add unit tests (`check_mode`)  

---

## Appendix: Quick Command Summary
```bash
mkdir -p ~/ansible-netmiko-lab/backups
python3 -m venv venv && source venv/bin/activate
pip install ansible netmiko paramiko ansible-pylibssh
ansible-galaxy collection install cisco.ios cisco.iosxr cisco.nxos ansible.netcommon

ansible-vault encrypt creds.yml
ansible-playbook -i inventory.ini config_push.yml --ask-vault-pass
ansible-playbook -i inventory.ini backup_config.yml --vault-password-file ~/.vault_pass.txt
```
