from setuptools import setup, find_packages, Command

# Lê o conteúdo do README.md
with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()
class CleanCommand(Command):
    """Comando para remover o diretório de binários ffmpeg."""
    description = 'Remove o diretório de binários ffmpeg'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        from m3u8_analyzer.__config__ import Configurate
        configurate = Configurate()
        configurate.uninstall_bins()
        print("Desinstalação completa.")
setup(
    name="m3u8-analyzer",
    version="1.0.2.1.3",
    description="Análise de dados de HLS m3u8",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="PauloCesar0073-dev404",
    author_email="paulocesar0073dev404@gmail.com",
    url='https://paulocesar-dev404.github.io/M3u8_Analyzer/',
    license="MIT",
    keywords=["hls", "m3u8", "m3u8_analyzer", "M3u8Analyzer"],
    packages=find_packages(),  # Inclui todos os pacotes encontrados automaticamente
    install_requires=['cryptography', 'requests','python-dotenv'],
    include_package_data=True,  # Inclui dados adicionais do pacote, como README.md
    cmdclass={
        'clean_bins': CleanCommand,
    },

)
