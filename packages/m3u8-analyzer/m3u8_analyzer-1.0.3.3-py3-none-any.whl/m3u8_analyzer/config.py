from setuptools.command.install import install
import urllib.request
import os
import platform
import subprocess

sistema = platform.system()
FFMPEG_URL = ''
if sistema in ["Linux", "Darwin"]:
    FFMPEG_URL = 'https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg_linux.zip'
elif sistema == 'Windows':
    FFMPEG_URL = 'https://raw.githubusercontent.com/PauloCesar-dev404/binarios/main/ffmpeg2024-07-15-git-350146a1ea-essentials_build.zip'


def add_path(path):
    """
    Adiciona o caminho do executável à variável de ambiente PATH do sistema.

    :param path: Caminho completo para o executável.
    """
    sistema = platform.system()

    if sistema == "Windows":
        try:
            # Obtém o PATH atual
            path_atual = os.environ.get("PATH", "")
            novo_path = f"{path};{path_atual}"

            # Usando o PowerShell para adicionar o caminho ao PATH de forma persistente
            command = f"[System.Environment]::SetEnvironmentVariable('PATH', '{novo_path}', 'User')"
            subprocess.run(["powershell", "-Command", command], check=True)
            print(f"O caminho '{path}' foi adicionado ao PATH de forma persistente no Windows.")

        except subprocess.CalledProcessError as e:
            print(f"Erro ao adicionar ffmpeg ao PATH no Windows: {e}")
        except Exception as e:
            print(f"Erro geral ao adicionar ffmpeg ao PATH no Windows: {e}")

    elif sistema in ["Linux", "Darwin"]:
        # Para sistemas Unix-like (Linux/macOS)
        bashrc_path = os.path.expanduser("~/.bashrc")
        zshrc_path = os.path.expanduser("~/.zshrc")
        shell_rc_path = bashrc_path if os.path.exists(bashrc_path) else zshrc_path

        try:
            with open(shell_rc_path, "a") as file:
                file.write(f"\nexport PATH=\"{path}:$PATH\"\n")
            print(
                f"O caminho '{path}' foi adicionado ao PATH de forma persistente no arquivo '{shell_rc_path}'.")
        except Exception as e:
            print(f"Erro ao adicionar ffmpeg ao PATH de forma persistente: {e}")
    else:
        print(f"Sistema operacional '{sistema}' não suportado para configuração automática de PATH.")


def download_ffmpeg():
    """Função para baixar o binário do FFmpeg personalizado."""
    system_platform = platform.system().lower()
    user_path = os.path.expanduser('~')
    configs_dir = '.m3u8_analyzer_configs'
    bin_dir = os.path.join(user_path, configs_dir, 'bin')
    os.makedirs(bin_dir, exist_ok=True)

    ffmpeg_filename = 'ffmpeg.exe' if system_platform == 'windows' else 'ffmpeg'
    ffmpeg_path = os.path.join(bin_dir, ffmpeg_filename)

    if not os.path.exists(ffmpeg_path):
        print(f"Baixando FFmpeg de {FFMPEG_URL}...")
        urllib.request.urlretrieve(FFMPEG_URL, ffmpeg_path)
        os.chmod(ffmpeg_path, 0o755)
        print("Download concluído e permissão de execução configurada.")

        # Adiciona o caminho do binário ao PATH
        add_path(bin_dir)
    else:
        print(f"O FFmpeg já está presente em {ffmpeg_path}.")



