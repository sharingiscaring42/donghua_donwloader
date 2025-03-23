import argparse
import json
import os
from downloader import create_config_from_link

CONFIG_PATH = "config.json"

def load_config(path):
    if not os.path.exists(path):
        return {"last_run": 0, "list": []}
    with open(path, "r") as f:
        return json.load(f)

def save_config(config, path):
    with open(path, "w") as f:
        json.dump(config, f, indent=4)

def find_entry_by_link(config_list, link):
    for entry in config_list:
        if entry["link"].strip("/") == link.strip("/"):
            return entry
    return None

def main():
    parser = argparse.ArgumentParser(description="Add or update donghua config entry.")
    parser.add_argument("--link", required=True, help="URL to the animexin series page")
    parser.add_argument("--ep", type=int, default=0, help="Last episode seen (default: 0)")
    args = parser.parse_args()

    config = load_config(CONFIG_PATH)

    existing = find_entry_by_link(config["list"], args.link)

    if existing:
        if existing["last_ep"] == args.ep:
            print("✅ Entry already exists with the same last_ep. Nothing to update.")
            return
        else:
            print("⚠️ Entry already exists with a different last_ep:")
            print(f"   Current: {existing['last_ep']} | New: {args.ep}")
            confirm = input("Do you want to update it? (y/n): ").strip().lower()
            if confirm == "y":
                existing["last_ep"] = args.ep
                save_config(config, CONFIG_PATH)
                print("✅ Entry updated and saved.")
            else:
                print("❌ Update cancelled.")
            return
    else:
        # Create new entry
        new_entry = create_config_from_link(args.link, last_ep=args.ep)
        config["list"].append(new_entry)
        save_config(config, CONFIG_PATH)
        print("✅ New entry added and saved.")

if __name__ == "__main__":
    main()
