from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from pathlib import Path
import time

def wait_for_new_download(download_dir: Path, previous_files: set[Path], timeout=120):
    start = time.time()

    while time.time() - start < timeout:
        # Wait for Chrome to finish writing
        if any(download_dir.glob("*.crdownload")):
            time.sleep(0.5)
            continue

        current_files = set(download_dir.glob("*.zip"))
        new_files = current_files - previous_files

        if new_files:
            return new_files.pop()

        time.sleep(0.5)

    raise TimeoutError("Download timed out.")


download_dir = Path.cwd() / "downloads" / "tracts_2008"
download_dir.mkdir(parents=True, exist_ok=True)

options = webdriver.ChromeOptions()
options.add_experimental_option(
    "prefs",
    {
        "download.default_directory": str(download_dir.resolve()),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    },
)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

driver.get(
    "https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2008&layergroup=Census+Tracts"
)


wait.until(EC.presence_of_element_located((By.ID, "fips_87")))

# Save all options before the page changes
options_list = [
    (o.get_attribute("value"), o.text)
    for o in Select(driver.find_element(By.ID, "fips_87")).options
    if o.get_attribute("value")
]

for value, state in options_list:
    print(f"Downloading {state}")

    # Re-find the select each iteration
    select = Select(wait.until(
        EC.element_to_be_clickable((By.ID, "fips_87"))
    ))
    select.select_by_value(value)

    # Click Download
    # download_btn = wait.until(
    #     EC.element_to_be_clickable((By.XPATH, "//input[@value='Download']"))
    # )
    download_btn = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//input[@type='button' and (@value='Download' or @value='Download state file')]",
            )
        )
    )
    before = set(download_dir.glob("*.zip"))
    download_btn.click()

    new_file = wait_for_new_download(download_dir, before)

    safe_state = (
        state.replace(" ", "_")
            .replace(",", "")
            .replace(".", "")
    )

    new_name = f"{safe_state}_{new_file.name}"
    new_path = new_file.with_name(new_name)

    new_file.rename(new_path)

    print(f"Downloaded: {new_path.name}")
    
driver.quit()