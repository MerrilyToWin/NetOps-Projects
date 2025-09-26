# GCP Network Automation with Ansible

Automate the creation and deletion of a **VPC network, subnets, firewall rules, and HTTP load balancer** in Google Cloud Platform (GCP) using Ansible.

---

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Usage](#usage)
  - [Create Infrastructure](#create-infrastructure)
  - [Delete Infrastructure](#delete-infrastructure)
- [Playbooks Details](#playbooks-details)
- [Important Notes](#important-notes)
- [License](#license)

---

## Overview
This project automates the setup and teardown of a GCP network environment. It includes:

1. **VPC Network** – Custom VPC without automatically created subnets.  
2. **Subnets** – Frontend, Backend, and Database subnets.  
3. **Firewall Rules** – For HTTP, app ports, database access, and SSH from a specific IP.  
4. **HTTP Load Balancer**:
   - Instance Template
   - Managed Instance Group (MIG)
   - Autoscaler
   - HTTP Health Check
   - Backend Service
   - Global IP
   - URL Map, Target HTTP Proxy, and Global Forwarding Rule  

The automation ensures consistent, repeatable deployment of GCP infrastructure.

---

## Prerequisites

---
1. **Google Cloud Project**  
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/).  
   - Enable **Compute Engine API**.

---

2. **Service Account Key**  
   - Go to **IAM & Admin → Service Accounts**.  
   - Create a new service account with roles:
     - `Compute Network Admin`
     - `Compute Security Admin`
   - Generate a **JSON key** and download it locally.  
   - Update its path in `gcp.yml` under:
     ```yaml
     service_account_file: ~/path/to/service_account.json
     ```

---

3. **Windows + WSL Setup (if using Windows)**  
   Install Ubuntu on Windows Subsystem for Linux (WSL):  
   ```bash
   wsl --install -d Ubuntu
   ```
   if already installed
   ```
   wsl -d ubuntu
   ```
---

4. **Install Ansible and Google Cloud Collection**
Inside WSL/Ubuntu:
```bash
sudo apt update && sudo apt install ansible -y
ansible-galaxy collection install google.cloud
```

---

## Project Structure
```
├── gcp_vpc.yml                # Create VPC, subnets, and firewalls
├── gcp_http_load_balancer.yml # Create HTTP Load Balancer and backend
├── gcp_automate.yml           # Master playbook to run both creation playbooks
├── gcp_delete_vpc.yml         # Delete all GCP resources
└── README.md                  # Documentation
```
---

## Usage

**Create Infrastructure**
Run the master playbook to create all resources:
```
ansible-playbook gcp_automate.yml
```
This will:
- Create VPC, subnets, and firewalls.
- Launch instance templates and managed instance group (MIG).
- Configure HTTP load balancer with health checks, backend service, URL map, proxy, and global forwarding rule.

**Delete Infrastructure**
Run the deletion playbook to remove all resources:
```
ansible-playbook gcp_delete_vpc.yml
```
This will:
- Delete Global IP
- Delete Firewall rules
- Delete Subnets
- Delete VPC itself

---

## Playbooks Details

**gcp_vpc.yml**

Creates a custom VPC network.
Defines subnets: subnet-frontend, subnet-backend, subnet-database.
Sets up firewall rules for HTTP, app ports, database access, and SSH.

**gcp_http_load_balancer.yml**

Creates instance template and managed instance group (MIG).
Configures autoscaler for dynamic scaling.
Sets up HTTP health check, backend service, URL map, HTTP proxy, and global forwarding rule.

**gcp_delete_vpc.yml**

Deletes global IP, firewall rules, subnets, and finally the VPC network.
Correctly handles network and subnet dependencies.

**Important Notes**

Always delete subnets before the VPC to avoid resource-in-use errors.
Verify the service account permissions.
Customize IP ranges for subnets and firewall rules as needed.

---

## License

This project is licensed under the MIT License.

---
