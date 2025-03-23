import os
import json
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from playwright.sync_api import sync_playwright

def extract_links_episode(link_serie):
    # url = "https://animexin.dev/btth-season-5/"
    response = requests.get(link_serie)
    soup = BeautifulSoup(response.content, "html.parser")

    episodes = {}

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        title_num = a_tag.find("div", class_="epl-num")
        
        if title_num:  # Make sure the div exists
            episode_number = title_num.text.strip()
            episodes[episode_number] = href  # Use the cleaned-up number as key

    # for num,link in episodes.items():
    #     print(num,link)
    
    return episodes

def filter_link_episode(link_serie, last_episode):
    episodes = extract_links_episode(link_serie)
    
    # Convert keys to integers for comparison
    filtered = {
        ep_num: link
        for ep_num, link in episodes.items()
        if ep_num.isdigit() and int(ep_num) > int(last_episode)
    }

    return filtered

def extract_mediafire_1080p_link(episode_url):
    response = requests.get(episode_url)
    
    if response.status_code != 200:
        print(f"❌ Failed to load page, status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    blocks = soup.find_all("div", class_="soraddlx")

    for block in blocks:
        heading = block.find("h3")
        if heading and "subtitle english" in heading.text.strip().lower():
            links_container = block.find("div", class_="soraurlx")
            if not links_container:
                continue

            strong_tag = links_container.find("strong")
            if strong_tag and "1080" in strong_tag.text:
                # Start extracting all 3 links
                links = {"terabox": None, "mirror": None, "mediafire": None}
                for link in links_container.find_all("a", href=True):
                    href = link["href"].lower()
                    if "terabox" in href:
                        links["terabox"] = link["href"]
                    elif "mirrored.to" in href:
                        links["mirror"] = link["href"]
                    elif "mediafire.com" in href:
                        links["mediafire"] = link["href"]
                return links

    return None


def get_new_mediafire_links(series_url, last_seen_episode):
    new_episodes = filter_link_episode(series_url, last_seen_episode)
    results = {}

    for ep, link in new_episodes.items():
        link_data = extract_mediafire_1080p_link(link)
        if link_data and link_data["mediafire"]:
            print(f"Episode {ep} - ✅ Mediafire 1080p Link: {link_data['mediafire']}")
            results[ep] = {
                "page": link,
                "mediafire": link_data["mediafire"]
            }
        else:
            print(f"Episode {ep} - ❌ Mediafire 1080p link not found from this page {link}")
    
    return results



def get_true_mediafire_link_playwright(url, headless):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)  # 👈 Turn off headless to test
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()
        print(f"🔍 Navigating to: {url}")
        page.goto(url)

        try:
            page.wait_for_selector("#downloadButton", timeout=30000)
            link = page.query_selector("#downloadButton").get_attribute("href")
            print(f"✅ Found direct link: {link}")
            return link
        except Exception as e:
            print("❌ Still blocked:", e)
            page.screenshot(path="cloudflare_block.png", full_page=True)
            return None
        finally:
            browser.close()

def download_file(url, filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get('content-length', 0))
        with open(filename, 'wb') as f, tqdm(
            total=total, unit='B', unit_scale=True, desc=filename
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                bar.update(len(chunk))


def create_donghua_structure(base_path, serie, saison):
    # Construct full path
    serie_path = os.path.join(base_path, serie)
    saison_path = os.path.join(serie_path, saison)
    # Create directories if they don't exist
    os.makedirs(saison_path, exist_ok=True)
    # print(f"Created structure:\n📁{serie_path}\n📁{saison_path}")


def load_config(path):
    with open(path, "r") as f:
        return json.load(f)

def save_config(config, path):
    with open(path, "w") as f:
        json.dump(config, f, indent=4)

def create_config_from_link(link, last_ep=0, missing_ep=None):
    if missing_ep is None:
        missing_ep = []

    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract raw title
    title_tag = soup.find("h1", class_="entry-title")
    if not title_tag:
        raise Exception("❌ Could not find <h1 class='entry-title'> on the page.")

    full_title = title_tag.text.strip()

    # Extract season number
    season_match = re.search(r'[Ss]eason\s*(\d+)', full_title)
    season_number = int(season_match.group(1)) if season_match else 1
    season_str = f"{season_number:02d}"

    # Clean name (remove "Season X")
    name = re.sub(r'[Ss]eason\s*\d+', '', full_title).strip()

    # Normalize for file-friendly identifiers
    normalized = re.sub(r"[^\w]", ".", name).strip(".")
    normalized = re.sub(r"\.+", ".", normalized)  # Replace multiple dots

    return {
        "name": name,
        "link": link,
        "serie": normalized,
        "saison": f"Season.{season_str}",
        "ep": f"{normalized}.S{season_str}E",
        "last_ep": last_ep,
        "missing_ep": missing_ep
    }


def main():

    CONFIG_PATH = "config.json"
    config = load_config(CONFIG_PATH)
    BASE_DOWNLOAD_PATH = config["base_folder_download"]
    TEST = config["test"]
    HEADLESS = config["headless"]

    list_problems = []

    for show in config["list"]:
        name = show["name"]
        link = show["link"]
        serie = show["serie"]
        saison = show["saison"]
        ep_prefix = show["ep"]
        last_ep = show["last_ep"]
        print("---------------------------")
        print(f"\n📺 Processing: {name}")
        create_donghua_structure(BASE_DOWNLOAD_PATH, serie, saison)

        episode_links = filter_link_episode(link, last_ep)
        if not episode_links:
            print("✅ No new episodes.")
            continue

        # ? Step 1: List upcoming downloads
        print(f"\n📋 Episodes to download (EP > {last_ep}):")
        sorted_episodes = sorted(
            ((int(ep), url) for ep, url in episode_links.items()),
            key=lambda x: x[0]
        )
        for ep_num, _ in sorted_episodes:
            print(f"  - Episode {ep_num}")
        missing_list = []
        # ? Step 2: Start downloading
        for ep_num, page_url in sorted_episodes:
            print(f"\n➡️ Episode {ep_num} - Page: {page_url}")

            # Get 1080p English links
            links = extract_mediafire_1080p_link(page_url)
            if not links or not links["mediafire"]:
                print(f"❌ No mediafire link found for episode {ep_num} {page_url}.")
                missing_list.append(ep_num)
                show["missing_ep"] = missing_list
                list_problems.append(f"{serie} saison: {saison} episode: {ep_prefix} link: {page_url} No mediafire link found ")
                continue  # continue sequentially

            # Get direct download link
            direct_link = get_true_mediafire_link_playwright(links["mediafire"],HEADLESS)
            if not direct_link:
                print(f"❌ Could not resolve direct link {ep_num} {page_url} {direct_link}.")
                missing_list.append(ep_num)
                show["missing_ep"] = missing_list
                list_problems.append(f"{serie} saison: {saison} episode: {ep_prefix} link: {page_url} Could not resolve direct link {direct_link}")
                continue  # continue sequentially

            # Build output path
            filename = f"{ep_prefix}{str(ep_num).zfill(2)}.mp4"
            output_path = os.path.join(BASE_DOWNLOAD_PATH, serie, saison, filename)

            try:
                if not TEST:
                    download_file(direct_link, output_path)
                    print(f"✅ Downloaded: {filename}")
                    show["last_ep"] = ep_num  # Update last successfully downloaded
                    save_config(config, CONFIG_PATH)
                    print("\n💾 Config updated!")
                else:
                    print(f'TEST MODE: Skipping download {serie} saison: {saison} episode: {ep_prefix} with link: {direct_link}')
            except Exception as e:
                print(f"❌ Download failed: {e}")
                missing_list.append(ep_num)
                show["missing_ep"] = missing_list
                list_problems.append(f"{serie} saison: {saison} episode: {ep_prefix} link: {page_url} Error while downloading link {direct_link}")
                continue  # continue sequentially

    # save_config(config, CONFIG_PATH)
    # print("\n💾 Config updated!")

    for problem in list_problems:
        print(problem)

if __name__ == "__main__":
    main()


