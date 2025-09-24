# 🚀 Automated VPC, Subnets, and Firewall Deployment on Google Cloud with Ansible

This project automates the creation of a **Google Cloud VPC**, multiple **subnets**, and **firewall rules** using **Ansible** and the `google.cloud` collection.  
It’s a great starting point to learn **Infrastructure as Code (IaC)** with Ansible and Google Cloud.

---

## 📌 Prerequisites

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
---

4. **Install Ansible and Google Cloud Collection**
Inside WSL/Ubuntu:
```bash
sudo apt update && sudo apt install ansible -y
ansible-galaxy collection install google.cloud
```

---

5. **▶️ Run**
Run the playbook:
```bash
ansible-playbook gcp.yml
```

---

**📂 Project Files**
```
|- gcp.yml
|- gcp_key.json
```

---

🛠️ What This Playbook Does

Creates a custom VPC: my-vpc-network
Creates three subnets:
```
subnet-a in us-west1 → 10.10.1.0/24
subnet-b in us-central1 → 10.20.1.0/24
subnet-c in us-central1 → 10.30.1.0/24
```
Creates three firewall rules:
```
allow-ssh → TCP 22 (SSH)
allow-http → TCP 80 (Web traffic)
allow-icmp → ICMP (Ping)
```

---

✅ Verification
After running the playbook, verify resources:
```
# List networks
gcloud compute networks list --project <project-id>

# List subnets
gcloud compute networks subnets list --project <project-id>

# List firewall rules
gcloud compute firewall-rules list --project <project-id>
```

---

📌 Notes
```
Make sure your service account has Network Admin + Security Admin roles.
Firewall rules use source_ranges: ["0.0.0.0/0"] for testing. Restrict this in production.
You can easily extend this playbook to also create VM instances inside the subnets.
```

---

🤝 Contributing
```
Pull requests and issues are welcome.
Feel free to fork and adapt this project for your own GCP automation needs.
```

---

📜 License
This project is licensed under the MIT License.

---

```
👉 Do you want me to also include the **`gcp.yml` playbook code snippet** inside the README so that GitHub viewers can see the full example directly without opening the YAML file?
```
