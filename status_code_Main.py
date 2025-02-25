import streamlit as st
import requests
from collections import defaultdict
import csv
from io import StringIO
import time

def check_url_status(urls):
    status_groups = defaultdict(list)
    for url in urls:
        try:
            response = requests.head(url, allow_redirects=False, timeout=5)
            if response.status_code == 301:
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    redirected_response = requests.head(redirect_url, timeout=5)
                    status_code = f"301 -> {redirected_response.status_code}"
                    url = f"{url} -> {redirect_url}"
                else:
                    status_code = 301
            else:
                status_code = response.status_code
        except requests.exceptions.RequestException:
            status_code = "Error"
        status_groups[status_code].append(url)
    return status_groups

def create_download_csv(results):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Status Code", "URL"])
    for status, urls in results.items():
        for url in urls:
            writer.writerow([status, url])
    return output.getvalue()

def format_results(results):
    output = ""
    for status, url_list in results.items():
        output += f"Status {status}:\n"
        for url in url_list:
            output += f"- {url}\n"
        output += "\n"
    return output

def main():
    st.title("🦅URL Status Checker")

    url_input = st.text_area("Enter URLs (one per line):", height=200)
    urls = [url.strip() for url in url_input.splitlines() if url.strip()]

    if st.button("Check URL Status"):
        if urls:
            start_time = time.time()
            results = check_url_status(urls)
            end_time = time.time()

            time_taken = end_time - start_time
            st.write(f"Time taken to check {len(urls)} URLs: {time_taken:.2f} seconds")

            st.session_state.results = results
            st.session_state.formatted_results = format_results(results)

    if 'formatted_results' in st.session_state:
        st.subheader("Results grouped by Status Code:")
        st.text_area("Results:", value=st.session_state.formatted_results, height=300)

    if 'results' in st.session_state:
        csv_data = create_download_csv(st.session_state.results)
        st.download_button(
            label="Download Results as CSV",
            data=csv_data,
            file_name="url_status.csv",
            mime="text/csv",
        )

    if not urls:
        st.info("Enter URLs and click 'Check URL Status' to begin.")

# if __name__ == "__main__":
#     main()
