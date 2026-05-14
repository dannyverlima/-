#!/usr/bin/env python
"""Script para testar o dashboard."""

import time
import subprocess
import sys
import requests

def test_dashboard():
    """Testa se o dashboard consegue iniciar e responder."""
    print("[*] Iniciando servidor do dashboard...")
    
    # Inicia o processo
    proc = subprocess.Popen(
        [sys.executable, '-m', 'app.main', 'dashboard'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Aguarda 3 segundos para o servidor iniciar
    time.sleep(3)
    
    try:
        # Tenta conectar
        print("[*] Testando conexão em http://localhost:5173...")
        response = requests.get("http://localhost:5173", timeout=2)
        print(f"[+] Servidor respondeu com status {response.status_code}")
        
        if "Agente Local" in response.text:
            print("[+] HTML do dashboard encontrado!")
            return True
        else:
            print("[-] HTML não contém 'Agente Local'")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[-] Falha de conexão - servidor não respondeu")
        return False
    except requests.exceptions.Timeout:
        print("[-] Timeout ao conectar ao servidor")
        return False
    except Exception as e:
        print(f"[-] Erro: {e}")
        return False
    finally:
        # Para o processo
        print("[*] Encerrando servidor...")
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("[*] Servidor encerrado")

if __name__ == "__main__":
    print("=" * 50)
    print("Teste do Dashboard do Agente Local")
    print("=" * 50)
    print()
    
    # Verifica se requests está instalado
    try:
        import requests
    except ImportError:
        print("[-] 'requests' não está instalado.")
        print("[*] Instalando...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
        import requests
    
    success = test_dashboard()
    
    print()
    print("=" * 50)
    if success:
        print("[+] Dashboard funciona corretamente!")
        sys.exit(0)
    else:
        print("[-] Erro ao testar dashboard")
        sys.exit(1)
