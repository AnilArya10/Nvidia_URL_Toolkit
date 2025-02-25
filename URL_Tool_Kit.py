import streamlit as st
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from typing import List, Dict
import re
import cn_brand_pages
import status_code_Main

class URLToolkit:
    def __init__(self):
        # Region Codes for Local Page Scraper
        self.REGION_CODES: Dict[str, List[str]] = {
            'EMEA': ["en-gb", "en-eu", "en-me", "it-it", "fr-fr", "pl-pl", "ru-ru", "es-es", "de-de", "tr-tr",
                     "nb-no", "sv-se", "fi-fi", "da-dk", "nl-nl", "cs-cz", "fr-be", "de-at", "ro-ro"],
            'APAC': ["en-in", "en-au", "en-sg", "en-ph", "en-my", "zh-tw", "ja-jp", "ko-kr", "id-id", "th-th", "vi-vn"],
            'LABR': ["es-la", "pt-br"],
            'CN': ["zh-cn", ".cn"]
        }
        self.unique_urls: List[str] = []
        self.sitemap_url = 'https://www.nvidia.com/en-us/en-us.sitemap.xml'
        self.extracted_sitemap_urls = self.extract_urls_from_sitemap()

    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_alternate_links(self, url: str) -> List[str]:
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            head_tag = soup.head

            if head_tag:
                alternate_links = head_tag.find_all('link', rel='alternate')

                if alternate_links:
                    self.unique_urls = list(set(link.get('href') for link in alternate_links if link.get('href')))
                    return self.unique_urls
                else:
                    st.warning("No alternate links found.")
                    return []
            else:
                st.warning("No <head> tag found in the document.")
                return []

        except requests.RequestException as e:
            st.error(f"Error fetching URL: {e}")
            return []

    def categorize_urls_by_region(self) -> Dict[str, List[str]]:
        categorized_urls = {
            'EMEA': [], 'APAC': [], 'LABR': [], 'CN': [], 'US': []
        }

        for url in self.unique_urls:
            for region, codes in self.REGION_CODES.items():
                if any(code in url for code in codes):
                    categorized_urls[region].append(url)
                    break
            else:
                categorized_urls['US'].append(url)

        return categorized_urls

    def url_converting(self, url):
        middletext = "content/nvidiaGDC/"
        firsttext = url[0:8]
        secondtext = url[11:23]
        langText = url[23:28]
        secLast = url[28:len(url) - 1]
        veryLasttext = ".html?wcmmode=disabled"
        versecText = "author"

        updatedLang = langText[3:5]
        updatednew = langText[0:2]

        def has_single_slash(url1):
            slash_count = url1.count('/')
            return slash_count == 5

        if has_single_slash(url):
            if "en-us" in url:
                return f"{firsttext}{versecText}{secondtext}{middletext}zz/en_ZZ{secLast}/home{veryLasttext}"
            else:
                return f"{firsttext}{versecText}{secondtext}{middletext}{updatedLang}/{updatednew}_{updatedLang.upper()}{secLast}/home{veryLasttext}"
        elif "en-us" in url:
            return f"{firsttext}{versecText}{secondtext}{middletext}zz/en_ZZ{secLast}{veryLasttext}"
        else:
            return f"{firsttext}{versecText}{secondtext}{middletext}{updatedLang}/{updatednew}_{updatedLang.upper()}{secLast}{veryLasttext}"

    def livetopreviewConverting(self,url):
        convertedurl=url.replace('www','preview')
        if url.__contains__("en-us"):
            return convertedurl.replace('en-us','en-zz')
        return convertedurl

    def previewtoliveConverting(self,url):
        convertedurl = url.replace('preview', 'www')
        if url.__contains__("en-zz"):
            return convertedurl.replace('en-zz', 'en-us')
        return convertedurl
    def extract_urls_from_sitemap(self):
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
        slash_count = url.count('/')
        return slash_count == 5

    def get_nvidia_brand_names(self):
        brandlist = []
        for url in self.extracted_sitemap_urls:
            if self.has_single_slash(url):
                brand = url[29:].rstrip('/')
                brandlist.append(brand)
        return sorted(set(brandlist))

    def get_brand_related_urls(self, brand_name):
        related_urls = []
        for url in self.extracted_sitemap_urls:
            if f"en-us/{brand_name}/" in url:
                related_urls.append(url)
        return related_urls

    def convert_author_to_live_url(self, author_url):
        # More flexible regex to capture dynamic path
        pattern = r'https://author\.nvidia\.com/content/nvidiaGDC/([a-z]{2})/([a-zA-Z_]{4,5})/([^/]+)/(.+)\.html'

        match = re.match(pattern, author_url)
        if not match:
            return None

        region_code, lang_code, section, path = match.groups()

        # Normalize language and region codes
        region_code = region_code.lower()
        lang_code = lang_code.lower().split('_')[0]

        # Special handling for 'home' path
        if path == 'home':
            # For 'zz' region, use 'en-us'
            if region_code == 'zz':
                live_url = f'https://www.nvidia.com/en-us/{section}/'
            else:
                live_url = f'https://www.nvidia.com/{lang_code}-{region_code}/{section}/'
        else:
            if region_code == 'zz':
                live_url = f'https://www.nvidia.com/en-us/{section}/{path}/'
            else:
                # Dynamic section and path mapping
                live_url = f'https://www.nvidia.com/{lang_code}-{region_code}/{section}/{path}/'

        return live_url

def main():
    st.set_page_config(layout="wide", page_title="URL Toolkit")

    # Initialize toolkit
    toolkit = URLToolkit()

    # Sidebar navigation
    page = st.sidebar.radio(
        "Select Tool",
        ["Local Page Scraper", "Live to Author Converter", "Author to live Converter", "Live To Preview Converter", "Preview To Live Converter", "US Brand Pages", "CN Brand Pages", "Driver URLS","Status Code Checker"]
    )

    if page == "Local Page Scraper":
        st.title("🌐 Local Page URL Scraper")

        url_input = st.text_area(
            "Enter URLs (one per line)",
            placeholder="https://nvidia.com\nhttps://nvidia.com/en-us/",
            height=300
        )

        if st.button("Scrape Local Pages"):
            if url_input.strip():
                urls = [url.strip() for url in url_input.split('\n') if url.strip()]
                results = {}

                for url in urls:
                    st.write(f"Processing URL: {url}")
                    alternate_urls = toolkit.fetch_alternate_links(url)

                    if alternate_urls:
                        categorized_urls = toolkit.categorize_urls_by_region()
                        results[url] = categorized_urls

                # Convert results to formatted text
                output_text = ""
                for base_url, categorized_urls in results.items():
                    output_text += f"Base URL: {base_url}\n"
                    for region, urls in categorized_urls.items():
                        if urls:
                            output_text += f"\n{region} URLs:\n"
                            output_text += "\n".join(urls) + "\n"
                    output_text += "\n" + "=" * 50 + "\n"

                # Display results in text area
                st.text_area(
                    "Scraped Local Pages",
                    value=output_text,
                    height=400
                )

    elif page == "Live to Author Converter":
        st.title("🔗 Live to Author URL Converter")

        # Create columns with adjusted widths
        col1, col2 = st.columns([2, 2])  # Equal width columns

        with col1:
            urls_input = st.text_area(
                "Enter Live URLs",
                height=300
            )

        with col2:
            # Placeholder for converted URLs
            converted_urls_output = st.empty()

        # Button below the input text area
        if st.button("Convert URLs"):
            if urls_input:
                urls = [url.strip() for url in urls_input.split()]
                converted_urls = [toolkit.url_converting(url) for url in urls]

                # Display converted URLs in the second column
                converted_urls_output.text_area(
                    "Converted Author URLs",
                    "\n".join(converted_urls),
                    height=300
                )

    elif page == "CN Brand Pages":
        cn_brand_pages.main()


    elif page == "US Brand Pages":
        st.title("🔍 NVIDIA US Brand URL Explorer")

        selected_brand = st.selectbox(
            "Select a Brand",
            toolkit.get_nvidia_brand_names()
        )

        if selected_brand:
            related_urls = toolkit.get_brand_related_urls(selected_brand)

            st.subheader(f"URLs for {selected_brand}")
            st.text_area(
                label=f"Related URLs for {selected_brand}",
                value="\n".join(related_urls),
                height=300
            )

            st.metric("Total Related URLs", len(related_urls))
    elif page == "Live To Preview Converter":
        st.title("🔗 Live to Preview URL Converter")
        # Create columns with adjusted widths
        col1, col2 = st.columns([2, 2])  # Equal width columns

        with col1:
            urls_input = st.text_area(
                "Enter Live URLs",
                height=300
            )

        with col2:
            # Placeholder for converted URLs
            converted_urls_output = st.empty()

        # Button below the input text area
        if st.button("Convert URLs"):
            if urls_input:
                urls = [url.strip() for url in urls_input.split()]
                converted_urls = [toolkit.livetopreviewConverting(url) for url in urls]

                # Display converted URLs in the second column
                converted_urls_output.text_area(
                    "Converted Preview URLs",
                    "\n".join(converted_urls),
                    height=300
                )
    elif page == "Preview To Live Converter":
        st.title("🔗 Preview to Live URL Converter")
        # Create columns with adjusted widths
        col1, col2 = st.columns([2, 2])  # Equal width columns

        with col1:
            urls_input = st.text_area(
                "Enter Preview URLs",
                height=300
            )

        with col2:
            # Placeholder for converted URLs
            converted_urls_output = st.empty()

        # Button below the input text area
        if st.button("Convert URLs"):
            if urls_input:
                urls = [url.strip() for url in urls_input.split()]
                converted_urls = [toolkit.previewtoliveConverting(url) for url in urls]

                # Display converted URLs in the second column
                converted_urls_output.text_area(
                    "Converted Live URLs",
                    "\n".join(converted_urls),
                    height=300
                )
    elif page == "Driver URLS":
        st.title("🛹 Driver URLS")
        # Define options for the dropdown
        # options = ['Game Ready Drivers', 'Studio Drivers', 'Quadro / NVIDIA RTX','Unix / Linux', 'Tesla']
        options = ["Origin","Preview","Live"]

        # Create a dropdown
        selected_option = st.selectbox('Choose an option:', options)

        origin_urls=[
            "============================Index==================================",
            'https://origin-aws-prod-us.nvidia.com/download/index.aspx?lang=en-us',
            'https://origin-aws-prod-us.nvidia.com/download/index.aspx?lang=en-us',
            'https://origin-aws-prod-uk.nvidia.com/download/index.aspx?lang=en-uk',
            'https://origin-aws-prod-de.nvidia.com/download/index.aspx?lang=de',
            'https://origin-aws-prod-fr.nvidia.com/download/index.aspx?lang=fr',
            'https://origin-aws-prod-es.nvidia.com/download/index.aspx?lang=es',
            'https://origin-aws-prod-pl.nvidia.com/download/index.aspx?lang=pl',
            'https://origin-aws-prod-it.nvidia.com/download/index.aspx?lang=it',
            'https://origin-aws-prod-ru.nvidia.com/download/index.aspx?lang=ru',
            'https://origin-aws-prod-la.nvidia.com/download/index.aspx?lang=la',
            'https://origin-aws-prod-br.nvidia.com/download/index.aspx?lang=br',
            'https://origin-aws-prod-tw.nvidia.com/download/index.aspx?lang=tw',
            'https://origin-aws-prod-jp.nvidia.com/download/index.aspx?lang=jp',
            'https://origin-aws-prod-kr.nvidia.com/download/index.aspx?lang=kr',
            'https://origin-aws-prod-in.nvidia.com/download/index.aspx?lang=en-in',
            'https://origin-aws-prod-cn.nvidia.com/download/index.aspx?lang=cn',
            'https://origin-aws-prod-tr.nvidia.com/drivers',
            "============================Find==================================",
            'https://origin-aws-prod-us.nvidia.com/download/Find.aspx?lang=en-us',
            'https://origin-aws-prod-uk.nvidia.com/download/Find.aspx?lang=en-uk',
            'https://origin-aws-prod-de.nvidia.com/download/Find.aspx?lang=de',
            'https://origin-aws-prod-fr.nvidia.com/download/Find.aspx?lang=fr',
            'https://origin-aws-prod-es.nvidia.com/download/Find.aspx?lang=es',
            'https://origin-aws-prod-pl.nvidia.com/download/Find.aspx?lang=pl',
            'https://origin-aws-prod-it.nvidia.com/download/Find.aspx?lang=it',
            'https://origin-aws-prod-ru.nvidia.com/download/Find.aspx?lang=ru',
            'https://origin-aws-prod-la.nvidia.com/download/Find.aspx?lang=la',
            'https://origin-aws-prod-br.nvidia.com/download/Find.aspx?lang=br',
            'https://origin-aws-prod-tw.nvidia.com/download/Find.aspx?lang=tw',
            'https://origin-aws-prod-jp.nvidia.com/download/Find.aspx?lang=jp',
            'https://origin-aws-prod-kr.nvidia.com/download/Find.aspx?lang=kr',
            'https://origin-aws-prod-in.nvidia.com/download/Find.aspx?lang=en-in',
            'https://origin-aws-prod-cn.nvidia.com/download/Find.aspx?lang=cn',
            'https://origin-aws-prod-tr.nvidia.com/drivers/beta'
        ]
        origin_url_text = "\n".join(origin_urls)
        preview_urls=[
            '===============Enterprise=============',
            'https://preview.nvidia.com/en-zz/drivers/',
            'https://preview.nvidia.com/en-gb/drivers/',
            'https://preview.nvidia.cn/drivers/ lookup /',
            'https://preview.nvidia.com/zh-tw/drivers/',
            'https://preview.nvidia.com/ja-jp/drivers/',
            'https://preview.nvidia.com/ko-kr/drivers/',
            'https://preview.nvidia.com/en-in/drivers/',
            'https://preview.nvidia.com/de-de/drivers/',
            'https://preview.nvidia.com/es-es/drivers/',
            'https://preview.nvidia.com/fr-fr/drivers/',
            'https://preview.nvidia.com/it-it/drivers/',
            'https://preview.nvidia.com/pl-pl/drivers/',
            'https://preview.nvidia.com/tr-tr/drivers/',
            'https://preview.nvidia.com/ru-ru/drivers/',
            'https://preview.nvidia.com/es-la/drivers/',
            'https://preview.nvidia.com/pt-br/drivers/',
            '=================GeForce====================',
            'https://preview.nvidia.com/en-zz/geforce/drivers/',
            'https://preview.nvidia.com/en-gb/geforce/drivers/',
            'https://preview.nvidia.com/zh-cn/geforce/drivers/',
            'https://preview.nvidia.com/zh-tw/geforce/drivers/',
            'https://preview.nvidia.com/ja-jp/geforce/drivers/',
            'https://preview.nvidia.com/ko-kr/geforce/drivers/',
            'https://preview.nvidia.com/en-in/geforce/drivers/',
            'https://preview.nvidia.com/de-de/geforce/drivers/',
            'https://preview.nvidia.com/es-es/geforce/drivers/',
            'https://preview.nvidia.com/fr-fr/geforce/drivers/',
            'https://preview.nvidia.com/it-it/geforce/drivers/',
            'https://preview.nvidia.com/pl-pl/geforce/drivers/',
            'https://preview.nvidia.com/tr-tr/geforce/drivers/',
            'https://preview.nvidia.com/ru-ru/geforce/drivers/',
            'https://preview.nvidia.com/es-la/geforce/drivers/',
            'https://preview.nvidia.com/pt-br/geforce/drivers/'
        ]
        preview_url_text = "\n".join(preview_urls)
        live_urls=[
            '===============Enterprise=============',
            'https://www.nvidia.com/en-us/drivers/',
            'https://www.nvidia.com/en-gb/drivers/',
            'https://www.nvidia.cn/drivers/lookup /',
            'https://www.nvidia.com/zh-tw/drivers/',
            'https://www.nvidia.com/ja-jp/drivers/',
            'https://www.nvidia.com/ko-kr/drivers/',
            'https://www.nvidia.com/en-in/drivers/',
            'https://www.nvidia.com/de-de/drivers/',
            'https://www.nvidia.com/es-es/drivers/',
            'https://www.nvidia.com/fr-fr/drivers/',
            'https://www.nvidia.com/it-it/drivers/',
            'https://www.nvidia.com/pl-pl/drivers/',
            'https://www.nvidia.com/tr-tr/drivers/',
            'https://www.nvidia.com/ru-ru/drivers/',
            'https://www.nvidia.com/es-la/drivers/',
            'https://www.nvidia.com/pt-br/drivers/',
            '=================GeForce====================',
            'https://www.nvidia.com/en-us/geforce/drivers/',
            'https://www.nvidia.com/en-gb/geforce/drivers/',
            'https://www.nvidia.com/zh-cn/geforce/drivers/',
            'https://www.nvidia.com/zh-tw/geforce/drivers/',
            'https://www.nvidia.com/ja-jp/geforce/drivers/',
            'https://www.nvidia.com/ko-kr/geforce/drivers/',
            'https://www.nvidia.com/en-in/geforce/drivers/',
            'https://www.nvidia.com/de-de/geforce/drivers/',
            'https://www.nvidia.com/es-es/geforce/drivers/',
            'https://www.nvidia.com/fr-fr/geforce/drivers/',
            'https://www.nvidia.com/it-it/geforce/drivers/',
            'https://www.nvidia.com/pl-pl/geforce/drivers/',
            'https://www.nvidia.com/tr-tr/geforce/drivers/',
            'https://www.nvidia.com/ru-ru/geforce/drivers/',
            'https://www.nvidia.com/es-la/geforce/drivers/',
            'https://www.nvidia.com/pt-br/geforce/drivers/'
        ]
        live_url_text="\n".join(live_urls)
        # Display the selected option
        st.write(f'You selected: {selected_option}')
        if selected_option=="Origin":
            st.text_area("List of URLs", value=origin_url_text, height=600)
        elif selected_option=='Preview':
            st.text_area("List of URLs", value=preview_url_text, height=600)
        elif selected_option=='Live':
            st.text_area("List of URLs", value=live_url_text, height=600)
    elif page == "Author to live Converter":
        st.title("🔗 Author to live URL Converter")

        # Create columns with adjusted widths
        col1, col2 = st.columns([2, 2])  # Equal width columns

        with col1:
            urls_input = st.text_area(
                "Enter Author URLs",
                height=300
            )

        with col2:
            # Placeholder for converted URLs
            converted_urls_output = st.empty()

        # Button below the input text area
        if st.button("Convert URLs"):
            if urls_input:
                urls = [url.strip() for url in urls_input.split()]
                converted_urls = [toolkit.convert_author_to_live_url(url) for url in urls]

                # Display converted URLs in the second column
                converted_urls_output.text_area(
                    "Converted Live URLs",
                    "\n".join(converted_urls),
                    height=300
                )
        elif page=="Status Code Checker":
        status_code_Main.main()
if __name__ == "__main__":
    main()
