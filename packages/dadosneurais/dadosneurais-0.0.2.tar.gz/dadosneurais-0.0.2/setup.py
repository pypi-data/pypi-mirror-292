from setuptools import setup, find_packages

setup(
    name="dadosneurais",
    version="0.0.2",
    author="Seu Nome",
    description="calc the number factorial",
    long_description=open("README.md", encoding="utf-8").read(), 
    long_description_content_type="text/markdown", 
    # url="https://github.com/usuario/repositorio", 
    packages=find_packages(), 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Versão mínima do Python requerida
    install_requires=[  # Dependências (adicione se necessário)
        # "dependencia1",
        # "dependencia2",
    ],
)
