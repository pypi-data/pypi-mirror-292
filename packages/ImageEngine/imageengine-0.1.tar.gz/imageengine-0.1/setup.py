from setuptools import setup, find_packages

setup(
    name='ImageEngine',
    version='0.1',
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
    }
)