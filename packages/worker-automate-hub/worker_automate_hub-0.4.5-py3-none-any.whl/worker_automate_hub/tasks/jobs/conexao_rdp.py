import subprocess
import pyautogui
import asyncio
from rich.console import Console
from worker_automate_hub.utils.logger import logger

console = Console()

async def conexao_rdp(task):
    try:
        ip = task["configEntrada"].get("ip", "")
        user = task["configEntrada"].get("user", "")
        password = task["configEntrada"].get("password", "")

        subprocess.Popen('mstsc')
        await asyncio.sleep(2)

        pyautogui.keyDown('alt')
        pyautogui.press('tab')
        pyautogui.keyUp('alt')
        asyncio.sleep(1)

        pyautogui.write(ip)
        pyautogui.press('tab')
        await asyncio.sleep(2)

        pyautogui.press('space')
        await asyncio.sleep(2)

        pyautogui.press('tab')
        await asyncio.sleep(2)
        pyautogui.write(user)
        pyautogui.press('enter')
        await asyncio.sleep(5)

        pyautogui.write(password)
        pyautogui.press('enter')
        await asyncio.sleep(9)

        pyautogui.press('left')
        await asyncio.sleep(2)
        pyautogui.press('enter')
        await asyncio.sleep(20)

        return {"sucesso": True, "retorno": "Processo de conexão ao RDP executado com sucesso."}

    except Exception as ex:
        err_msg = f"Erro ao executar conexao_rdp: {ex}"
        logger.error(err_msg)
        console.print(err_msg, style="bold red")
        return {"sucesso": False, "retorno": err_msg}
