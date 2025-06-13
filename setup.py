from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="blackjack-ai-training",
    version="1.0.0",
    author="Blackjack AI Training Team",
    description="A comprehensive blackjack training application with AI coaching and strategy optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/blackjack-ai-training",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.15.0",
        "scikit-learn>=1.3.0",
        "pillow>=10.0.0",
        "requests>=2.31.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "beautifulsoup4>=4.12.0",
        "trafilatura>=1.6.0",
    ],
    extras_require={
        "ai": ["anthropic>=0.7.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "blackjack-training=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["card_images/*.svg", "attached_assets/*"],
    },
)