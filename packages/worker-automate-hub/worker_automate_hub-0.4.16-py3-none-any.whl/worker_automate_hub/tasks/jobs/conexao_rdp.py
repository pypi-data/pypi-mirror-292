import subprocess
import pyautogui
import asyncio
import os
from rich.console import Console
from worker_automate_hub.utils.logger import logger
import time
import pygetwindow as gw

console = Console()

def tirar_screenshot(nome_etapa):
    caminho_screenshot = f"{nome_etapa}_{int(time.time())}.png"
    pyautogui.screenshot(caminho_screenshot)
    console.print(f"Screenshot tirada: {caminho_screenshot}")
    return caminho_screenshot

def deletar_screenshots(caminhos_screenshots):
    for caminho in caminhos_screenshots:
        try:
            os.remove(caminho)
            console.print(f"Screenshot deletada: {caminho}")
        except OSError as e:
            console.print(f"Erro ao deletar screenshot {caminho}: {e}")

def fechar_janela_existente(ip):
    janelas_encontradas = gw.getAllTitles()
    for titulo in janelas_encontradas:
        if ip in titulo:
            janela = gw.getWindowsWithTitle(titulo)[0]
            console.print(f"Fechando janela existente: {titulo}")
            janela.close()
            time.sleep(2)
            
            if titulo not in gw.getAllTitles():
                console.print(f"Janela fechada com sucesso: {titulo}")
            else:
                console.print(f"Falha ao fechar a janela: {titulo}")
            
            pyautogui.press('enter')
            time.sleep(2)
            break
    else:
        console.print(f"Nenhuma janela encontrada com o IP: {ip}")

def restaurar_janelas_rdp():
    janelas_rdp = [win for win in gw.getAllTitles() if "Conexão de Área de Trabalho Remota" in win or "Remote Desktop Connection" in win]
    
    for titulo in janelas_rdp:
        janela = gw.getWindowsWithTitle(titulo)[0]
        console.print(f"Processando janela: {titulo}")
        if janela.isMinimized:
            janela.restore()
            console.print(f"Janela restaurada: {titulo}")
        else:
            console.print(f"Janela já está aberta: {titulo}")
        time.sleep(2)

async def conexao_rdp(task):
    caminhos_screenshots = []
    try:
        ip = task["configEntrada"].get("ip", "")
        user = task["configEntrada"].get("user", "")
        password = task["configEntrada"].get("password", "")

        pyautogui.hotkey('win', 'd')
        console.print("1 - Minimizando todas as telas...")
        await asyncio.sleep(2)

        fechar_janela_existente(ip)

        subprocess.Popen('mstsc')
        console.print("2 - Abrindo conexao de trabalho remota...")
        await asyncio.sleep(2)

        caminhos_screenshots.append(tirar_screenshot("antes_de_inserir_ip"))
        console.print("3 - Inserindo o IP...")
        pyautogui.write(ip)
        await asyncio.sleep(2)
        caminhos_screenshots.append(tirar_screenshot("depois_de_inserir_ip"))

        pyautogui.press('tab')
        await asyncio.sleep(2)
        console.print("4 - Inserindo o Usuario...")
        pyautogui.write(user)
        pyautogui.press('enter')
        await asyncio.sleep(5)
        caminhos_screenshots.append(tirar_screenshot("depois_de_inserir_usuario"))

        console.print("5 - Inserindo a Senha...")
        pyautogui.write(password)
        pyautogui.press('enter')
        await asyncio.sleep(10)
        caminhos_screenshots.append(tirar_screenshot("depois_de_inserir_senha"))

        console.print("6 - Apertando left...")
        pyautogui.press('left')
        await asyncio.sleep(2)
        console.print("7 - Apertando Enter...")
        pyautogui.press('enter')
        await asyncio.sleep(20)
        caminhos_screenshots.append(tirar_screenshot("depois_do_certificado"))

        console.print("8 - Minimizando todas as telas no final...")
        pyautogui.hotkey('win', 'd')
        await asyncio.sleep(2)
        caminhos_screenshots.append(tirar_screenshot("depois_de_minimizar_todas"))

        restaurar_janelas_rdp()
        caminhos_screenshots.append(tirar_screenshot("depois_de_restaurar_janelas"))

        deletar_screenshots(caminhos_screenshots)

        return {"sucesso": True, "retorno": "Processo de conexão ao RDP executado com sucesso."}

    except Exception as ex:
        err_msg = f"Erro ao executar conexao_rdp: {ex}"
        logger.error(err_msg)
        console.print(err_msg, style="bold red")
        caminhos_screenshots.append(tirar_screenshot("erro"))
        deletar_screenshots(caminhos_screenshots)
        return {"sucesso": False, "retorno": err_msg}
