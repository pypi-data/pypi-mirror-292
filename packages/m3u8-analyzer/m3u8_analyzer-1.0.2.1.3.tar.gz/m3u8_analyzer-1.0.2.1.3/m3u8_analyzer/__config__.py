import stat
import time
import requests
import zipfile
import shutil
import os
import sys
from http.client import IncompleteRead


class Configurate:
    def __init__(self):
        self.config_file_path = os.path.join(sys.prefix,
                                             '.m3u8_analyzer_config') if self.is_virtualenv() else '.m3u8_analyzer_config'
        self.BIN_DIR = 'ffmpeg-binaries'
        self.config = self.load_config(self.config_file_path)
        self.OS_SYSTEM = self.config.get('OS_SYSTEM', os.name)
        self.VERSION = self.config.get('VERSION', '1.0.2.1.3')
        self.FFMPEG_URL = self.config.get('FFMPEG_URL')
        self.FFMPEG_BINARY = self.config.get('FFMPEG_BINARY')
        self.INSTALL_DIR = self.config.get('INSTALL_DIR')

        if not self.INSTALL_DIR:
            self.INSTALL_DIR = os.path.join(sys.prefix, self.BIN_DIR) if self.is_virtualenv() else os.path.join(
                os.getcwd(), self.BIN_DIR)
            self.config['INSTALL_DIR'] = self.INSTALL_DIR
            self.save_config(self.config_file_path, self.config)

        if not os.path.exists(self.config_file_path):
            self.configure()

    def loader(self):
        """Carrega a configuração do arquivo e retorna um dicionário."""
        return self.load_config(self.config_file_path)

    # Função para ler variáveis de configuração de um arquivo .config
    def load_config(self, file_path):
        config = {}
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):  # Ignorar linhas em branco e comentários
                        key, value = line.strip().split('=', 1)
                        config[key.strip()] = value.strip()
        return config

    # Função para criar/atualizar o arquivo .config
    def save_config(self, file_path, config):
        with open(file_path, 'w') as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")

    # Função para obter entradas do usuário e atualizar o arquivo de configuração
    def configure(self):
        config = {
            'OS_SYSTEM': os.name,
            'VERSION': '1.0.2.1.2'
        }
        if os.name == 'nt':
            config[
                'FFMPEG_URL'] = 'https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg2024-07-15-git-350146a1ea-essentials_build.zip'
            config['FFMPEG_BINARY'] = 'ffmpeg.exe'
        elif os.name == 'posix':
            config[
                'FFMPEG_URL'] = 'https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg_6.1.1_3UBUNTU5.zip'
            config['FFMPEG_BINARY'] = 'ffmpeg'
        config['INSTALL_DIR'] = self.INSTALL_DIR
        self.save_config(self.config_file_path, config)

    # Função para detectar se estamos em um ambiente virtual
    def is_virtualenv(self):
        return (
                hasattr(sys, 'real_prefix') or
                (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        )

    # Função para baixar o arquivo
    def download_file(self, url: str, local_filename: str):
        """Baixa um arquivo do URL para o caminho local especificado."""
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            total_length = int(response.headers.get('content-length', 0))

            with open(local_filename, 'wb') as f:
                start_time = time.time()
                downloaded = 0

                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    f.write(data)

                    elapsed_time = time.time() - start_time
                    elapsed_time = max(elapsed_time, 0.001)  # Prevenir divisão por zero
                    speed_kbps = (downloaded / 1024) / elapsed_time
                    percent_done = (downloaded / total_length) * 100

                    sys.stdout.write(
                        f"\rBaixando Binários ffmpeg: {percent_done:.2f}% | Velocidade: {speed_kbps:.2f} KB/s | "
                        f"Tempo decorrido: {int(elapsed_time)}s")
                    sys.stdout.flush()

                sys.stdout.write("\nDownload completo.\n")
                sys.stdout.flush()
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"Erro ao baixar o arquivo: {e}\n")
            raise
        except IOError as e:
            if isinstance(e, IncompleteRead):
                sys.stderr.write("Erro de conexão: Leitura incompleta\n")
            else:
                sys.stderr.write(f"Ocorreu um erro de I/O: {str(e)}\n")
            raise

    # Função para extrair o arquivo ZIP
    def extract_zip(self, zip_path: str, extract_to: str):
        """Descompacta o arquivo ZIP no diretório especificado."""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        except zipfile.BadZipFile as e:
            sys.stderr.write(f"Erro ao descompactar o arquivo: {e}\n")
            raise

    # Função para remover o arquivo
    def remove_file(self, file_path: str):
        """Remove o arquivo especificado."""
            # Remover o diretório temporário
        if os.path.exists(file_path):
                try:
                    sys.stdout.flush()  # Certificar-se de que toda a saída foi impressa antes de remover o diretório
                    shutil.rmtree(file_path, ignore_errors=True)
                except PermissionError as e:
                    print(f"Permissão negada ao tentar remover o diretório {file_path}: {e}")
                except OSError as e:
                    print(f"Erro ao remover o diretório {file_path}: {e}")
                except Exception as e:
                    print(f"Erro inesperado ao remover o diretório {file_path}: {e}")

    # Função para instalar os binários
    def install_bins(self):
        """Instala o ffmpeg baixando e descompactando o binário apropriado."""
        zip_path = os.path.join(self.INSTALL_DIR, "ffmpeg.zip")

        # Criar o diretório de destino se não existir
        os.makedirs(self.INSTALL_DIR, exist_ok=True)

        # Baixar o arquivo ZIP
        self.download_file(self.FFMPEG_URL, zip_path)

        # Descompactar o arquivo ZIP
        self.extract_zip(zip_path, self.INSTALL_DIR)

        # Remover o arquivo ZIP
        self.remove_file(zip_path)


    # Função para desinstalar os binários
    def uninstall_bins(self):
        """Remove os binários do ffmpeg instalados no ambiente virtual com força bruta."""
        dt = self.loader()
        install_dir = dt.get('INSTALL_DIR')

        if install_dir and os.path.exists(install_dir):
            try:
                # Tenta remover o diretório e seu conteúdo
                shutil.rmtree(install_dir, ignore_errors=True)

                # Verifica se o diretório foi removido
                if not os.path.exists(install_dir):
                    print(f"ffmpeg desinstalado com sucesso do diretório: {install_dir}")
                else:
                    print(f"Falha ao remover o diretório: {install_dir}")

            except Exception as e:
                sys.stderr.write(f"Erro ao remover o diretório ffmpeg-binaries: {e}\n")
                raise
        else:
            print("ffmpeg já está desinstalado ou nunca foi instalado.")

    # Método principal para verificar e instalar o ffmpeg
    def run(self):
        ffmpeg_binary_path = os.path.join(self.INSTALL_DIR, self.FFMPEG_BINARY)
        if not os.path.exists(ffmpeg_binary_path):
            self.install_bins()
        else:
            pass


# Função principal para executar a configuração e instalação
def m():
    configurate = Configurate()
    configurate.run()


def g():
    configurate = Configurate()
    load = configurate.loader()
    return load


def r():
    configurate = Configurate()
    load = configurate.uninstall_bins()
