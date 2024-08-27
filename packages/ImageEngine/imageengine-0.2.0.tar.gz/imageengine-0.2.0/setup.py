from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='ImageEngine',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        "fastai",
        "duckduckgo_search",
        "icrawler",
        "requests",
        "Pillow",
    ],
    entry_points={
        'console_scripts': [
            'search-ddg=ImageEngine.search_duckduckgo:search_ddg_entry',
            'search-google=ImageEngine.search_google:search_google_entry',
            'search-bing=ImageEngine.search_bing:search_bing_entry',
            'search-web=ImageEngine.search_web:search_web_entry',
        ],
    },
    long_description=description,
    long_description_content_type="text/markdown"
)