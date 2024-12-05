from setuptools import setup, find_packages

setup(
    name="speed_camera",  # Package name
    version="0.1.0",  # Initial version
    description="A Python package for vehicle speed detection using YOLO and OpenCV.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  # For proper rendering on PyPI
    author="Your Name",
    author_email="your_email@example.com",
    url="https://github.com/yourusername/speed_camera",  # Replace with your GitHub repo
    packages=find_packages(),  # Automatically include all Python packages
    install_requires=[
        "numpy",
        "opencv-python",
        "picamera2"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
