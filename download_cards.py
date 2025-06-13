import requests
import os
from urllib.parse import urljoin

def download_card_images():
    """Download all playing card images from nicubunu.ro"""
    base_url = "https://nicubunu.ro/graphics/playingcards/simple/"
    
    # Card definitions
    ranks = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    
    # Create directory
    os.makedirs('card_images', exist_ok=True)
    
    # Download each card
    for suit in suits:
        for rank in ranks:
            filename = f"{suit}_{rank}.svg"
            url = urljoin(base_url, filename)
            
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    with open(f"card_images/{filename}", 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {filename}")
                else:
                    print(f"Failed to download: {filename} (Status: {response.status_code})")
            except Exception as e:
                print(f"Error downloading {filename}: {e}")
    
    # Download card back
    try:
        back_url = urljoin(base_url, "back.svg")
        response = requests.get(back_url, timeout=10)
        if response.status_code == 200:
            with open("card_images/back.svg", 'wb') as f:
                f.write(response.content)
            print("Downloaded: back.svg")
    except Exception as e:
        print(f"Error downloading card back: {e}")

if __name__ == "__main__":
    download_card_images()