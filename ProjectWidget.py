import sys
import os
import requests
import webbrowser
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QListWidget, QListWidgetItem, QFrame, QScrollArea
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

# Directory to store downloaded images
download_dir = "nasa_images"
image_url = "https://www.flickr.com/photos/nasawebbtelescope/with/54378060725/"
news_url = "https://www.nasa.gov/2025-news-releases/"

def download_images():
    """Download images from the specified URL."""
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    response = requests.get(image_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    images = soup.find_all('img')
    
    image_urls = []
    for img in images:
        if 'src' in img.attrs:
            img_url = img['src']
            if img_url.startswith("//"):
                img_url = "https:" + img_url
            image_urls.append(img_url)
    
    downloaded_images = []
    for idx, img_url in enumerate(image_urls):  # Download all images
        img_path = os.path.join(download_dir, f"image_{idx}.jpg")
        if not os.path.exists(img_path):
            img_data = requests.get(img_url).content
            with open(img_path, 'wb') as f:
                f.write(img_data)
        downloaded_images.append(img_path)
    
    return downloaded_images

def fetch_news_articles():
    """Fetch news articles from the NASA 2025 News Releases page."""
    response = requests.get(news_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all news articles
    articles = soup.find_all('a', class_='hds-content-item-heading')
    news_items = []

    for article in articles:
        # Extract title
        title_tag = article.find('div', class_='hds-a11y-heading-22')
        title = title_tag.text.strip() if title_tag else "No Title"

        # Extract description (if available)
        description_tag = article.find_next('p', class_='margin-top-0 margin-bottom-1')
        description = description_tag.text.strip() if description_tag else "No Description"

        # Extract article URL
        article_url = article.get('href')
        if article_url and not article_url.startswith('http'):
            article_url = 'https://www.nasa.gov' + article_url

        # Add title, description, and URL to the news items list
        news_items.append((title, description, article_url))
    
    return news_items

class ImageDashboard(QWidget):
    def __init__(self, image_paths, news_items):
        super().__init__()
        self.image_paths = image_paths
        self.current_index = 0
        self.news_items = news_items
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        # Create a fixed-size frame for the image
        self.image_frame = QFrame(self)
        self.image_frame.setFixedSize(750, 500)
        self.image_frame.setStyleSheet("border: 1px solid black;")
        self.image_layout = QVBoxLayout(self.image_frame)

        self.image_label = QLabel(self.image_frame)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_layout.addWidget(self.image_label)
        self.update_image()

        # Navigation buttons for images
        self.button_layout = QHBoxLayout()
        self.prev_button = QPushButton("← Previous")
        self.next_button = QPushButton("Next →")
        self.prev_button.clicked.connect(self.prev_image)
        self.next_button.clicked.connect(self.next_image)
        
        self.button_layout.addWidget(self.prev_button)
        self.button_layout.addWidget(self.next_button)
        
        # Featured News section
        self.news_label = QLabel("Featured News")
        self.news_scroll = QScrollArea()
        self.news_scroll.setWidgetResizable(True)
        self.news_content = QWidget()
        self.news_layout = QVBoxLayout(self.news_content)

        for title, description, link in self.news_items:
            # Create a clickable title button
            title_button = QPushButton(title)
            title_button.setStyleSheet("text-align: left; padding: 5px; color: blue; text-decoration: underline;")
            title_button.setFlat(True)  # Make the button look like a link
            title_button.clicked.connect(lambda _, url=link: webbrowser.open(url))

            # Create a description label
            description_label = QLabel(description)
            description_label.setWordWrap(True)

            # Add title button and description to the layout
            self.news_layout.addWidget(title_button)
            self.news_layout.addWidget(description_label)
            self.news_layout.addSpacing(20)

        self.news_scroll.setWidget(self.news_content)
        
        # Add widgets to the main layout
        self.layout.addWidget(self.image_frame)
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.news_label)
        self.layout.addWidget(self.news_scroll)
        
        self.setLayout(self.layout)
        self.setWindowTitle("NASA Image & News Dashboard")
        self.resize(800, 800)

    def update_image(self):
        """Update the displayed image."""
        if self.image_paths:
            pixmap = QPixmap(self.image_paths[self.current_index])
            self.image_label.setPixmap(pixmap.scaled(750, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def next_image(self):
        """Show the next image."""
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.update_image()

    def prev_image(self):
        """Show the previous image."""
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.update_image()

if __name__ == "__main__":
    # Download images and fetch news articles
    image_paths = download_images()
    news_items = fetch_news_articles()
    
    # Start the application
    app = QApplication(sys.argv)
    dashboard = ImageDashboard(image_paths, news_items)
    dashboard.show()
    sys.exit(app.exec())
