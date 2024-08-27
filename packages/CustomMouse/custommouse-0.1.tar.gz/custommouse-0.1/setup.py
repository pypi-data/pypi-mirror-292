from setuptools import setup, find_packages

setup(
    name="CustomMouse",
    version="0.1",
    author="tolik_4ip",
    author_email="Kakashka@gmail.com",
    description="Кастомная либка для симуляции мышки (EAC UNDETECT)",
    # long_description=open('README.md').read(),  # Уберите или добавьте, если нужно
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",  # Указывает, что библиотека поддерживает Python 2
        "Programming Language :: Python :: 3",  # Также добавляем Python 3, если это актуально
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',  # Это указывает минимальную версию Python (для Python 2)
)
