import re
import yaml
import time
from datetime import datetime
from pymongo import MongoClient
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from bson.objectid import ObjectId

# =========== CONFIG - EDIT THESE ============
MONGO_URI = "mongodb+srv://merwin:<password>@storage.mazbk2j.mongodb.net/?retryWrites=true&w=majority&appName=Storage" # or your Atlas URI
DB_NAME = "NETMIKO"
DEVICES_COLL = "Storage"
CONFIGS_COLL = "Configs"
RESULTS_COLL = "Results"
RULES_FILE = "rules.yaml"
# ============================================

def load_rules(path=RULES_FILE):
    with open(path, "r") as f:
        rules = yaml.safe_load(f)
    if not isinstance(rules, dict):
        raise ValueError("rules.yaml must contain a mapping at the top level")
    return rules

def check_rules(config_text, rules):
    """
    Returns (compliant_bool, issues_list)
    issues_list: list of dicts like {"rule":"ntp", "type":"missing"/"forbidden", "pattern": "<pattern>"}
    """
    issues = []
    for rule_name, rule_spec in rules.items():
        must_have = rule_spec.get("must_have", []) or []
        must_not_have = rule_spec.get("must_not_have", []) or []

        for pattern in must_have:
            # Use regex search; rule authors can write regex or plain substrings
            if not re.search(pattern, config_text, re.IGNORECASE | re.MULTILINE):
                issues.append({"rule": rule_name, "type": "missing", "pattern": pattern})

        for pattern in must_not_have:
            if re.search(pattern, config_text, re.IGNORECASE | re.MULTILINE):
                issues.append({"rule": rule_name, "type": "forbidden", "pattern": pattern})

    compliant = (len(issues) == 0)
    return compliant, issues

def fetch_and_store_for_device(device_doc, db, rules):
    hostname = device_doc.get("hostname", device_doc.get("ip", "unknown"))
    ip = device_doc.get("ip")
    vendor = device_doc.get("vendor", "cisco_ios")  # default if missing
    username = device_doc["username"]
    password = device_doc["password"]
    secret = device_doc.get("secret")  # optional enable password

    conn_params = {
        "device_type": vendor,
        "host": ip,
        "username": username,
        "password": password,
        "port": device_doc.get("port", 22),
        "session_log": f"session_{hostname}.log",  # helpful for debugging
        # "global_delay_factor": 2,
        # "timeout": 60,
    }

    results_coll = db[RESULTS_COLL]
    configs_coll = db[CONFIGS_COLL]

    start_time = datetime.utcnow()
    print(f"[{start_time.isoformat()}] Connecting to {hostname} ({ip}) ...")
    try:
        net_connect = ConnectHandler(**conn_params)

        # If device needs enable mode
        if secret:
            try:
                net_connect.enable()
            except Exception:
                # try sending enable with secret if not automatically escalated
                net_connect.send_command(f"enable\n{secret}")

        # Disable paging — common command for Cisco IOS/XE:
        try:
            net_connect.send_command("terminal length 0", expect_string=r"#", delay_factor=1)
        except Exception:
            # some devices or platform prompts vary; safe to ignore if fails
            pass

        # Fetch running config (use device-appropriate command if needed)
        try:
            config_text = net_connect.send_command("show running-config", expect_string=r"#", delay_factor=1)
        except Exception:
            # fallback to timing-based command if prompt issues
            config_text = net_connect.send_command_timing("show running-config")

        collected_at = datetime.utcnow()

        # Insert snapshot into configs collection
        cfg_doc = {
            "hostname": hostname,
            "ip": ip,
            "collected_at": collected_at,
            "config_text": config_text
        }
        snapshot = configs_coll.insert_one(cfg_doc)
        snapshot_id = snapshot.inserted_id

        # Run compliance checks
        compliant, issues = check_rules(config_text, rules)

        # Insert result doc
        result_doc = {
            "hostname": hostname,
            "ip": ip,
            "collected_at": collected_at,
            "compliant": compliant,
            "issues": issues,
            "snapshot_id": snapshot_id,
            "duration_seconds": (datetime.utcnow() - start_time).total_seconds()
        }
        results_coll.insert_one(result_doc)

        print(f"[{hostname}] compliance: {compliant}; issues: {len(issues)}; snapshot: {snapshot_id}")
        net_connect.disconnect()
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        err_doc = {
            "hostname": hostname,
            "ip": ip,
            "collected_at": datetime.utcnow(),
            "error": type(e).__name__,
            "details": str(e)
        }
        db[RESULTS_COLL].insert_one(err_doc)
        print(f"[{hostname}] ERROR: {e}")
    except Exception as e:
        err_doc = {
            "hostname": hostname,
            "ip": ip,
            "collected_at": datetime.utcnow(),
            "error": type(e).__name__,
            "details": str(e)
        }
        db[RESULTS_COLL].insert_one(err_doc)
        print(f"[{hostname}] UNEXPECTED ERROR: {e}")

def main():
    rules = load_rules(RULES_FILE)
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    devices_coll = db[DEVICES_COLL]

    devices = list(devices_coll.find({}))
    if not devices:
        print("No devices found in devices collection. Add at least one device document.")
        return

    for d in devices:
        fetch_and_store_for_device(d, db, rules)

if __name__ == "__main__":
    main()
