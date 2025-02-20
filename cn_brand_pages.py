import streamlit as st
import requests
import xml.etree.ElementTree as ET

#from numpy.ma.core import count
#import pandas as pd
#import openpyxl

class NvidiaCNURLExtractor:
    def __init__(self, sitemap_url='https://www.nvidia.cn/zh-cn.sitemap.xml'):
        self.sitemap_url = sitemap_url
        self.extracted_urls = self.extract_urls_from_sitemap()
        self.brand_names = self.get_nvidia_brand_names()

    def extract_urls_from_sitemap(self):
        """
        Extract all URLs from <loc> tags in an XML sitemap.
        """
        try:
            response = requests.get(self.sitemap_url)
            response.raise_for_status()
            root = ET.fromstring(response.content)

            urls = []
            for loc in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                urls.append(loc.text)

            return urls

        except Exception as e:
            st.error(f"Error fetching sitemap: {e}")
            return []

    def has_single_slash(self, url):
        """
        Check if URL has specific number of slashes.
        """
        slash_count = url.count('/')
        return slash_count == 3

    # def get_nvidia_brand_names(self):
    #     """
    #     Extract brand names from URLs.
    #     """
    #     brandlist = []
    #     for url in self.extracted_urls:
    #         if self.has_single_slash(url):
    #             brand = url[22:].rstrip('/')
    #             brandlist.append(brand)
    #     return sorted(set(brandlist))

    def get_nvidia_brand_names(self):
        """
        Extract brand names from URLs with more robust parsing.
        """
        brandlist = []
        for url in self.extracted_urls:
            # Remove the base URL and split the path
            path = url.replace('https://www.nvidia.cn/', '').split('/')

            # Consider first path segment as a potential brand name
            if path and len(path[0]) > 0:
                brandlist.append(path[0])

        return sorted(set(brandlist))

    def get_brand_related_urls(self, brand_name):
        """
        Get URLs related to a specific brand.
        """
        related_urls = []
        for url in self.extracted_urls:
            if f".cn/{brand_name}/" in url:
                related_urls.append(url)
        return related_urls



def main():
    st.title("NVIDIA China Brand URL Explorer")

    # Initialize extractor
    extractor = NvidiaCNURLExtractor()

    # Dropdown for brand selection
    selected_brand = st.selectbox(
        "Select a Brand",
        extractor.brand_names
    )

    # Display related URLs in text area
    if selected_brand:
        st.subheader(f"URLs for {selected_brand}")
        related_urls = extractor.get_brand_related_urls(selected_brand)

        # Convert URLs to newline-separated string
        urls_text = "\n".join(related_urls)

        # Display URLs in text area
        st.text_area(
            label=f"Related URLs for {selected_brand}",
            value=urls_text,
            height=300
        )

        # Additional statistics
        st.write(f"Total Related URLs: {len(related_urls)}")




# if __name__ == "__main__":
#     #make_sidebar()
#     main()
