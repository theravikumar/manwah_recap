from setuptools import setup, find_packages

setup(
    name="manhwa_recap",
    version="1.0.0",
    description="AI Manhwa Recap YouTube Videos Engine",
    author="Antigravity",
    packages=find_packages(),
    py_modules=["cli", "app"],
    install_requires=[
        "torch>=2.0.0",
        "numpy>=1.24.0",
        "Pillow>=9.5.0",
        "opencv-python>=4.8.0",
        "httpx>=0.24.0",
        "pyyaml>=6.0",
        "click>=8.1.0",
    ],
    entry_points={
        "console_scripts": [
            "manhwa-recap=cli:main",
        ],
    },
)
