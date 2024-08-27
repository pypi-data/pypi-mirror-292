import subprocess
import pyautogui
import asyncio
import os
from rich.console import Console
from worker_automate_hub.utils.logger import logger
import time

console = Console()

# Função para tirar screenshots
def tirar_screenshot(nome_etapa):
    caminho_screenshot = f"{nome_etapa}_{int(time.time())}.png"
    pyautogui.screenshot(caminho_screenshot)
    console.print(f"Screenshot tirada: {caminho_screenshot}")
    return caminho_screenshot

# Função para deletar screenshots
def deletar_screenshots(caminhos_screenshots):
    for caminho in caminhos_screenshots:
        try:
            os.remove(caminho)
            console.print(f"Screenshot deletada: {caminho}")
        except OSError as e:
            console.print(f"Erro ao deletar screenshot {caminho}: {e}")

# Função principal para a conexão RDP
async def conexao_rdp(task):
    caminhos_screenshots = []
    try:
        ip = task["configEntrada"].get("ip", "")
        user = task["configEntrada"].get("user", "")
        password = task["configEntrada"].get("password", "")

        # Minimizar todas as janelas antes de iniciar a conexão
        pyautogui.hotkey('win', 'd')
        console.print("1 - Minimizando todas as telas...")
        await asyncio.sleep(2)

        # Abrir o Remote Desktop Connection
        subprocess.Popen('mstsc')
        console.print("2 - Abrindo conexao de trabalho remota...")
        await asyncio.sleep(2)  # Aguarde um pouco para a janela abrir

        # Inserir o endereço IP
        caminhos_screenshots.append(tirar_screenshot("antes_de_inserir_ip"))
        console.print("3 - Inserindo o IP...")
        pyautogui.write(ip)
        await asyncio.sleep(2)
        caminhos_screenshots.append(tirar_screenshot("depois_de_inserir_ip"))

        # Avançar para a próxima etapa
        pyautogui.press('tab')
        await asyncio.sleep(2)
        console.print("4 - Inserindo o Usuario...")
        pyautogui.write(user)
        pyautogui.press('enter')
        await asyncio.sleep(5)
        caminhos_screenshots.append(tirar_screenshot("depois_de_inserir_usuario"))

        # Inserir a senha
        console.print("5 - Inserindo a Senha...")
        pyautogui.write(password)
        pyautogui.press('enter')
        await asyncio.sleep(10)
        caminhos_screenshots.append(tirar_screenshot("depois_de_inserir_senha"))

        # Lidar com o pop-up de certificado clicando em "Yes"
        console.print("6 - Apertando left...")
        pyautogui.press('left')
        await asyncio.sleep(2)
        console.print("7 - Apertando Enter...")
        pyautogui.press('enter')
        await asyncio.sleep(20)
        caminhos_screenshots.append(tirar_screenshot("depois_do_certificado"))

        # Minimizar todas as janelas após a conexão
        console.print("8 - Minimizando todas as telas no final...")
        pyautogui.hotkey('win', 'd')
        await asyncio.sleep(2)
        caminhos_screenshots.append(tirar_screenshot("depois_de_minimizar_todas"))

        # Deletar screenshots após o sucesso
        deletar_screenshots(caminhos_screenshots)

        pyautogui.hotkey('win', 'd')

        return {"sucesso": True, "retorno": "Processo de conexão ao RDP executado com sucesso."}

    except Exception as ex:
        err_msg = f"Erro ao executar conexao_rdp: {ex}"
        logger.error(err_msg)
        console.print(err_msg, style="bold red")

        # Tirar screenshot do erro e adicionar à lista de caminhos para deletar posteriormente
        caminhos_screenshots.append(tirar_screenshot("erro"))

        # Deletar screenshots mesmo em caso de erro
        deletar_screenshots(caminhos_screenshots)

        return {"sucesso": False, "retorno": err_msg}
