Zero-Touch Provisioning + Compliance
📌 Introduction

This project demonstrates an end-to-end Zero-Touch Provisioning (ZTP) and Compliance Validation System for Cisco LAN switches using:

GCP VM (Ubuntu) — automation host

Ansible + Netmiko — provisioning & configuration management

Python Parser + MongoDB — compliance validation & result storage

Flask API — JSON export of compliance results

Grafana — dashboards and reporting

The system provisions baseline configuration, validates compliance, stores results centrally, and visualizes them in real-time.

🔧 Use Cases

Automated LAN/WAN switch/router provisioning.

Ensuring baseline compliance (hostname, SNMP, NTP, Syslog, VLANs).

Centralized compliance audit across devices.

Real-time dashboards for compliance posture.

Alerts on non-compliance (email, Slack, Teams).

Extensible to ACLs, routing protocols, QoS, etc.

⚙️ Architecture
```
                ┌─────────────────────────┐
                │     GCP VM (Ubuntu)     │
                │  - Ansible + Netmiko    │
                │  - Python Parser        │
                │  - MongoDB              │
                │  - Grafana (UI)         │
                └───────────┬─────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
      ┌───────▼───────┐           ┌───────▼───────┐
      │ Cisco Router  │           │ Cisco Switch  │
      │ (Sandbox)     │           │ (LAN)         │
      └───────────────┘           └───────────────┘
              │                           │
       ┌──────▼───────┐            ┌──────▼───────┐
       │ Provisioning │            │ Compliance   │
       │ (ZTP)        │            │ Checks       │
       └──────┬───────┘            └──────┬───────┘
              │                           │
              └─────────────┬─────────────┘
                            │
                ┌───────────▼─────────────┐
                │ Python Parser + MongoDB │
                │ - Store CLI outputs     │
                │ - Calculate compliance  │
                └───────────┬─────────────┘
                            │
                ┌───────────▼─────────────┐
                │ Grafana Dashboards       │
                │ - Visualization          │
                │ - Alerts                 │
                └─────────────────────────┘
```
🚀 Setup Guide
Phase 1 — Provision GCP VM & Dependencies

Provision VM and install dependencies automatically:
```
ansible-playbook create_gcp_and_dep.yml
```

This installs:

MongoDB

Grafana

Python packages: netmiko, ansible, pymongo, flask

Base tools: git, curl, ufw

Phase 2 — Provision LAN Switch with Ansible

inventory.yml
```
all:
  hosts:
    lan_switch:
      ansible_host: host ip
      ansible_user: username
      ansible_password: password
      ansible_connection: network_cli
      ansible_network_os: ios

```
Playbook (ztp_switch.yml)
```
ansible-playbook -i inventory.yml ztp_switch.yml
```

Configures:

Hostname

SNMP community

NTP server

Syslog server

VLAN 10 & 20

Phase 3 — Compliance Checks

Run compliance script:
```
python3 compliance_check.py
```

✅ Example output:
```
{
  "device": "10.10.20.40",
  "timestamp": "2025-09-16T17:29:49",
  "compliance": {
    "hostname": true,
    "snmp": false,
    "ntp": true,
    "syslog": false,
    "vlans": true
  }
}
```

Results are stored in MongoDB → ztp_project.compliance_results.

Phase 4 — Flask API

Serve compliance data for Grafana:
```
python3 export_json_api.py
```

Test API:
```
curl http://127.0.0.1:5000/compliance
```
Phase 5 — Grafana Setup

Install plugin:
```
sudo grafana-cli plugins install simpod-json-datasource
sudo systemctl restart grafana-server
```
Access Grafana:
```
http://<VM_IP>:3000
```

Add JSON API Data Source with URL:
```
http://localhost:5000/compliance
```

✅ Save & Test → OK.

Phase 6 — SSH Tunnel (Access Grafana Locally)
```
ssh -L 3000:localhost:3000 -i ~/.ssh/netops_ssh ubuntu@<VM_IP>
```

Open in browser:
```
http://localhost:3000
```
Phase 7 — Automation with Cron

Schedule compliance checks every 10 minutes:
```
crontab -e

#Add:

*/10 * * * * /usr/bin/python3 /home/ubuntu/compliance_check.py
```

🛠️ Troubleshooting
```
# Check MongoDB
sudo systemctl status mongod

# Check Grafana
sudo systemctl status grafana-server

# Check Flask API
curl http://127.0.0.1:5000/compliance

# Check ports
sudo ss -tulpn | grep 3000
```

📂 Project Structure
```
IN LOCAL SYSTEM
├─ create_gcp_and_dep.yml   (Provision VM + dependencies)
├─ ansible.cfg
├─ gcp_key
    ├─ gcp-neetops_key.json

IN GCP VM
├─ inventory.yml             (Switch inventory)
├─ ztp_switch.yml            (Ansible playbook for provisioning)
├─ compliance_check.py       (Compliance validation)
├─ export_json_api.py  (Flask API for Grafana)
MongoDB + Grafana on VM   (Data + visualization)
```
🚀 Next Steps

Add more compliance checks (ACLs, routing, QoS).

Configure Grafana alerts for non-compliant devices.

Secure Flask API with authentication.

Deploy in Docker/Kubernetes for scalability.

Integrate CI/CD pipelines for automated updates.
