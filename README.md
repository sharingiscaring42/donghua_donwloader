# Donghua Downloader 📥

A Python tool to automatically fetch, resolve, and download episodes of donghua from [animexin.dev](https://animexin.dev), using Mediafire direct links.

---

## 🧰 Requirements

- Python 3.7+
- pip
- Optional: `xvfb` (for headless Linux environments)

---

## 📦 Installation

1. **Clone the project**
```bash
   git clone https://github.com/sharingiscaring42/donghua-downloader.git
   cd donghua-downloader
```
2. **Create a virtual environment (optional but recommended)**
```bash
    python3 -m venv venv
    source venv/bin/activate
```

3. **Install dependencies**
```bash
    pip install -r requirements.txt
    playwright install
```

4. **(Optional) Headless playwright for linux**
```bash
    sudo apt install xvfb
```
Otherwise need to put 
```json
{
  "headless": false
}
```
inside the config.json and a GUI to launch

5. **Configure the path where to download the files**
```json
{
  "base_folder_download": "path_where_download"
}
```
The file folder will look like this:
```bash
├── Donghua/                    
│   ├── Battle.Through.The.Heavens/
│   │   └── Season.05/
│   │       ├── Battle.Through.The.Heavens.S05E138.mp4
│   │       └── ...
│   └── Renegade.Immortal/
│       └── Season.01/
│           └── Renegade.Immortal.S01E072.mp4
```

6. **Add config**
```bash
    python3 add_to_config.py --link https://animexin.dev/throne-of-seal/ --ep 100
```
7. **Relaunch every 4h**

***Relaunch Option 1: cron (linux)***
```bash
    crontab -e
    0 */4 * * * /usr/bin/python3 /path/to/your/main.py >> /path/to/log.txt 2>&1
```
where you edit the path for downloader and the path log

***Relaunch Option 2: pm2***
install npm then pm2 (google it)
put yourself inside this folder 
link to the env with full path if you created one
```bash
    pm2 start downloader.py --name donghua-downloader --interpreter python3 --cron "0 */4 * * *"
```


**Examples adding config**

```bash
user@computer:~/code/donghua_donwloader$ python3 add_to_config.py --link https://animexin.dev/throne-of-seal/ --ep 100
✅ New entry added and saved.
user@computer:~/code/donghua_donwloader$ python3 add_to_config.py --link https://animexin.dev/throne-of-seal/ --ep 100
✅ Entry already exists with the same last_ep. Nothing to update.
user@computer:~/code/donghua_donwloader$ python3 add_to_config.py --link https://animexin.dev/throne-of-seal/ --ep 98
⚠️ Entry already exists with a different last_ep:
   Current: 100 | New: 98
Do you want to update it? (y/n): y
✅ Entry updated and saved.
user@computer:~/code/donghua_donwloader$ python3 add_to_config.py --link https://animexin.dev/throne-of-seal/ --ep 105
⚠️ Entry already exists with a different last_ep:
   Current: 98 | New: 105
Do you want to update it? (y/n): y
✅ Entry updated and saved.
```


**Examples running downloader**
```bash
---------------------------

📺 Processing: Throne of Seal

📋 Episodes to download (EP > 150):
  - Episode 151

➡️ Episode 151 - Page: https://animexin.dev/throne-of-seal-episode-151-indonesia-english-sub/
🔍 Navigating to: https://www.mediafire.com/file/.../AnimeXin.dev_throne_ep_151_eng_%25281%2529.mp4/file
✅ Found direct link: https://download2391.mediafire.com/.../AnimeXin.dev+throne+ep+151+eng+%281%29.mp4
.../donghua/Throne.of.Seal/Season.01/Throne.of.Seal.S01E151.mp4: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████| 490M/490M [00:40<00:00, 12.2MB/s]
✅ Downloaded: Throne.of.Seal.S01E151.mp4

💾 Config updated!

```
