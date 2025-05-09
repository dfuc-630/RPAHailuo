from django.http import JsonResponse
import requests
import base64
import time
import requests
import re
import json
import os
from decimal import Decimal
from django.shortcuts import render
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

browser = None
def callApi1(request):
    image_url = "https://test.cdn01.avtvn.com/files/uploads/tmpkhy_nj3g.jpg?AWSAccessKeyId=minioadmin&Signature=hQXnXG7nejaCFbb5IUPW8zz1puo%3D&Expires=4898303380"
    image_response = requests.get(image_url)

    if image_response.status_code != 200:
        return JsonResponse({"error": f"Error fetching image: {image_response.status_code}"}, status=400)

    image_data = base64.b64encode(image_response.content).decode('utf-8')

    payload = {
        "model": "I2V-01-Director",
        "prompt": "[Truck left,Pan right]A woman is drinking coffee.",
        "first_frame_image": f"data:image/jpeg;base64,{image_data}"
    }

    headers = {
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJQaHVjIERvYW4iLCJVc2VyTmFtZSI6IlBodWMgRG9hbiIsIkFjY291bnQiOiIiLCJTdWJqZWN0SUQiOiIxOTE5ODc3NzU2ODEyNzkyNjQzIiwiUGhvbmUiOiIiLCJHcm91cElEIjoiMTkxOTg3Nzc1NjgwODU5ODMzOSIsIlBhZ2VOYW1lIjoiIiwiTWFpbCI6ImRvYW5kYWlwaHVjMDYwM0BnbWFpbC5jb20iLCJDcmVhdGVUaW1lIjoiMjAyNS0wNS0wNyAwOTozMjoxNiIsIlRva2VuVHlwZSI6MSwiaXNzIjoibWluaW1heCJ9.kNMMLDFRB48Bcw92LhRJTQVwp7lMMmcciZ5iTF_Cr-gXJIBFBRqqymkLTlYPp-lO-goSg18bRylQDGvTtrCD9C-d86pM9zHuDmAj483CLUhltadkib_PDJbSJqf_tzcx8aaBYrNyaYDvH05NXYONKva8_RW4FZha5X0J3VXxf21HxM1xTZ8yRE2InPXTmZNf5W4aK3T--gjxe_O_-GgZBt4wwoKw9lcxe-94IRCRwx-KHjnMqDHwFFGQLvKATjl8frXVlv6T_WPh6nA70X3eFwdRVQRr_MQsMcTCbrZQS45fDv1JHeDesB7OvlHpCUvAJhuiQ_ucj-ZtCvYxKs5k9Q',
        'Content-Type': 'application/json'
    }

    response = requests.post(
        "https://api.minimaxi.chat/v1/video_generation",
        headers=headers,
        json=payload  # ✅ Truyền dict, không phải json.dumps
    )

    return JsonResponse(response.json(), status=response.status_code)

def browser_find_element(browser, *args, timeout=30, **kwargs):
    expire = datetime.now() + timedelta(seconds=timeout)
    while datetime.now() < expire:
        try:
            return browser.find_element(*args, **kwargs)
        except Exception as ex:
            # print(ex)
            pass
        time.sleep(1)
    return None

download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
def setup_browser(request, headless=False):
    chrome_options = Options()

    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

    # Set quyền Notifications cụ thể cho trang https://neo.vpbank.com.vn là Allow (1)
    prefs = {
        "profile.default_content_setting_values.notifications": 1,
        "profile.managed_default_content_settings.notifications": 1,
        "profile.content_settings.exceptions.notifications": {
            "https://neo.vpbank.com.vn:443,*": {
                "setting": 1
            }
        }
    }

    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    global browser
    if browser is None:
        browser = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

def wait_for_download_complete(download_path, timeout=6000000000):
    seconds = 0
    # Tiến hành kiểm tra và chờ đến khi có file .mp4
    while not any(f.endswith(".mp4") for f in os.listdir(download_path)):
        time.sleep(1)
        seconds += 1
        if seconds > timeout:
            raise Exception("Download timeout")
    # Lấy tất cả các file mp4 trong thư mục
    mp4_files = [f for f in os.listdir(download_path) if f.endswith(".mp4")]
    # Nếu không tìm thấy file mp4 nào (điều này không nên xảy ra do điều kiện while trên)
    if not mp4_files:
        raise Exception("No mp4 file found after download.")
    # Lấy đường dẫn đầy đủ cho tất cả các file mp4
    mp4_files_paths = [os.path.join(download_path, f) for f in mp4_files]
    # Sắp xếp các file theo thời gian sửa đổi (mới nhất sẽ ở đầu danh sách)
    mp4_files_paths.sort(key=os.path.getmtime, reverse=True)
    # Trả về file mp4 mới nhất
    return mp4_files_paths[0]


def rpavideogen(request, image_path):
    setup_browser(request, headless=False)
    browser.get("https://hailuoai.video/")
    browser.execute_script("""
        Object.defineProperty(Notification, 'permission', {
            get: function() { return 'granted'; }
        });
    """)
    time.sleep(5)

    sign_in_button = WebDriverWait(browser, 100).until(
    EC.element_to_be_clickable((By.XPATH, "//div[text()='Sign In']")))
    if not sign_in_button:
        print("Không tìm thấy nút 'Sign In'")
        return 0
    else:
        sign_in_button.click()
        print("Đã nhấn vào nút 'Sign In'")
    time.sleep(2)
    google_button = WebDriverWait(browser, 100).until(
    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Continue with Google']]")))
    if not google_button:
        print("Không tìm thấy nút 'Continue with Google'")
        return 0
    else:
        google_button.click()
        print("Đã nhấn vào nút 'Continue with Google'")
    time.sleep(2)
    # Chuyển sang cửa sổ pop-up mới
    WebDriverWait(browser, 10).until(EC.number_of_windows_to_be(2))  # Chờ cửa sổ mới xuất hiện
    window_handles = browser.window_handles  # Lấy danh sách cửa sổ
    browser.switch_to.window(window_handles[1])  # Chuyển sang cửa sổ pop-up mới
    time.sleep(2)
    email_input = WebDriverWait(browser, 100).until(
    EC.element_to_be_clickable((By.ID, "identifierId")))
    if not email_input:
        print("Không tìm thấy ô nhập email")
        return 0
    else:
        email_input.send_keys("phucdd@avtvn.com")
        print("Đã nhập email vào ô input")
    time.sleep(2)
    next_button = WebDriverWait(browser, 100).until(
    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']/ancestor::button")))
    if not next_button:
        print("Không tìm thấy nút 'Next'")
        return 0
    else:
        next_button.click()
        print("Đã nhấn vào nút 'Next'")
    time.sleep(3)
    password_input = WebDriverWait(browser, 100).until(
    EC.element_to_be_clickable((By.NAME, "Passwd")))
    if not password_input:
        print("Không tìm thấy ô nhập mật khẩu")
        return 0
    else:
        password_input.send_keys("Phuc06032004@")
        print("Đã nhập mật khẩu vào ô input")
    time.sleep(2)
    next_button = WebDriverWait(browser, 100).until(
    EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']/ancestor::button")))
    if not next_button:
        print("Không tìm thấy nút 'Next'")
        return 0
    else:
        next_button.click()
        print("Đã nhấn vào nút 'Next'")

    WebDriverWait(browser, 30).until(lambda d: len(d.window_handles) == 1)
    browser.switch_to.window(browser.window_handles[0])
    print("Đã chuyển lại về cửa sổ chính sau khi popup đóng")
    time.sleep(3)

    i_got_it_button = WebDriverWait(browser, 100).until(
    EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='I got it']"))
)

    if not i_got_it_button:
        print("Không tìm thấy nút 'I got it'")
    else:
        i_got_it_button.click()
        print("Đã nhấn vào nút 'I got it'")

    time.sleep(3)

    create_video_button = WebDriverWait(browser, 100).until(
    EC.element_to_be_clickable((By.XPATH,"//nav[.//div[text()='Create Video']]")))

    if create_video_button:
        create_video_button.click()
        print("Đã nhấn vào nút 'Create Video'")
    else:
        print("Không tìm thấy nút 'Create Video'")

    time.sleep(4)
    file_input  = browser.find_element(By.XPATH, "//input[@type='file']")
    browser.execute_script("arguments[0].style.display = 'block';", file_input)
    if file_input :
        # file_input.send_keys(r"D:\Intern\ImageToVideo\imgvideo\dev\img\test.jpg")
        file_input.send_keys(image_path)
        print("Đã nhấn vào vùng upload hình ảnh")
    else:
        print("Không tìm thấy vùng upload")

    time.sleep(2)
    textarea = browser.find_element(By.ID, "video-create-textarea")
    # Click và nhập text bằng ActionChains
    actions = ActionChains(browser)
    actions.move_to_element(textarea).click().send_keys("move hands and head also lip like doing a presentation").perform()
    time.sleep(3)

    button = browser.find_element(By.XPATH, "//button[.//span[text()='30']]")
    if button: print("tìm thấy nút 30")
    else: print("không tìm thấy nút 30")
    button.click()
    time.sleep(2)

    while True:
        try:
            print("đang đợi gen video...")
            dowload_button = browser.find_element(By.XPATH,"//button[contains(@class, 'ant-dropdown-trigger')]""[.//*[name()='svg']/*[name()='path' and contains(@d, 'M7.9997 1.434')]]")
            if dowload_button:
                print("Đã tìm thấy nút và sẽ nhấn vào nó...")
                dowload_button.click()
                break
        except Exception as e:
            print("chưa tìm thấy button:")
            time.sleep(10)


    file_path = wait_for_download_complete(download_dir)
    filename = os.path.basename(file_path)

    print("đã gen video thành công...")
    print("file path:", file_path)
    print("filename:", filename)

    with open(file_path, 'rb') as f:
        files = {
            'file': (filename, f, 'video/mp4')  # Đặt rõ tên và định dạng
        }
        data = {
            'name': filename
        }
        response = requests.post('https://staging-home.cdn01.avtvn.com/api/avatars/', files=files, data=data)

    print(response.status_code, response.text)

    time.sleep(3)
    svg_button = browser_find_element(browser,By.CSS_SELECTOR,"button.ant-dropdown-trigger svg.h-4.w-4").find_element(By.XPATH, "..")
    svg_button.click()

    delete_item = browser_find_element(browser,By.XPATH,"//li[contains(@class, 'ant-dropdown-menu-item')]//div[contains(@class, 'context-menu-item')]//span[text()='Delete']//ancestor::li")
    delete_item.click()
    time.sleep(2)

    # confirm_button = WebDriverWait(browser, 10).until(
    #     EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Confirm']]"))
    # )
    # confirm_button.click()


IMG_DIR = r"D:\Intern\ImageToVideo\imgvideo\dev\img"
PROCESSED_DIR = os.path.join(IMG_DIR, "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def get_new_image():
    """Lấy ảnh mới chưa xử lý"""
    for file in os.listdir(IMG_DIR):
        if file.lower().endswith(('.jpg', '.jpeg', '.png')) and not file.startswith("~"):
            src_path = os.path.join(IMG_DIR, file)
            processed_path = os.path.join(PROCESSED_DIR, file)
            if not os.path.exists(processed_path):
                return src_path
    return None

def rpavideogen_loop(request):
    while True:
        image_path = get_new_image()
        if image_path:
            print(f"Phát hiện ảnh mới: {image_path}")
            rpavideogen(request, image_path)
            # Đánh dấu là đã xử lý
            filename = os.path.basename(image_path)
            os.rename(image_path, os.path.join(PROCESSED_DIR, filename))
        else:
            print(" Không có ảnh mới, đang chờ...")
        time.sleep(5)