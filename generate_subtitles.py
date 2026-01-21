import os
from bs4 import BeautifulSoup
import logging
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

TIME_PATTERN = re.compile(r"^\d{2}:\d{2}:\d{2} - \d{2}:\d{2}:\d{2}$")

def extract_subtitles(html_file):
    """Extract subtitles from an HTML file and return as a Markdown string."""
    try:
        logging.info(f"Processing file: {html_file}")
        with open(html_file, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Course name: folder name + html filename (without extension)
        folder_name = os.path.basename(os.path.dirname(html_file))
        file_stem = os.path.splitext(os.path.basename(html_file))[0]
        course_name_text = f"{folder_name}{file_stem}"

        # Extract subtitles with timestamps
        subtitles = []
        for div in soup.find_all('div', class_='css-10s8ss9'):
            ps = div.find_all('p')
            if not ps:
                continue

            time_tag = None
            text_tag = None
            for p in ps:
                text = p.get_text(strip=True)
                if not text:
                    continue
                if TIME_PATTERN.match(text):
                    time_tag = p
                elif text_tag is None:
                    text_tag = p

            if time_tag and text_tag:
                time_text = time_tag.get_text(strip=True)
                subtitle_text = text_tag.get_text(strip=True)
                subtitles.append(f"{time_text}  \n{subtitle_text}\n")

        if not subtitles:
            # Fallback: pair time and text by order in all p tags
            ps = soup.find_all('p')
            i = 0
            while i < len(ps):
                time_text = ps[i].get_text(strip=True)
                if TIME_PATTERN.match(time_text):
                    j = i + 1
                    while j < len(ps):
                        subtitle_text = ps[j].get_text(strip=True)
                        if subtitle_text and not TIME_PATTERN.match(subtitle_text):
                            subtitles.append(f"{time_text}  \n{subtitle_text}\n")
                            i = j
                            break
                        j += 1
                i += 1

        # Combine into Markdown format
        markdown_content = f"# 課程名稱：{course_name_text}\n\n"
        markdown_content += "\n".join(subtitles)
        return markdown_content

    except Exception as e:
        logging.error(f"Error processing file {html_file}: {e}")
        return None

def process_html_files(base_dir):
    """Process all HTML files in subdirectories and generate Markdown files."""
    try:
        for root, _, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.html'):
                    html_path = os.path.join(root, file)
                    markdown_path = os.path.splitext(html_path)[0] + '.md'

                    if os.path.exists(markdown_path):
                        logging.info(f"Skipped: {html_path} (Markdown file already exists)")
                        continue

                    markdown_content = extract_subtitles(html_path)
                    if markdown_content:
                        with open(markdown_path, 'w', encoding='utf-8') as md_file:
                            md_file.write(markdown_content)
                        logging.info(f"Converted: {html_path} to {markdown_path}")
                    else:
                        logging.warning(f"No content extracted from: {html_path}")
    except Exception as e:
        logging.critical(f"Critical error during processing: {e}")

if __name__ == "__main__":
    base_directory = os.path.dirname(os.path.abspath(__file__))
    logging.info("Starting subtitle conversion process...")
    process_html_files(base_directory)
    logging.info("Subtitle conversion process completed.")