#Seletor.py v1-23/03/2025

import tkinter as tk
from tkinter import scrolledtext, messagebox
from tkinter.ttk import Progressbar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import threading
from webdriver_manager.chrome import ChromeDriverManager

def iniciar_driver():
    """Inicializa o WebDriver com WebDriverManager."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920x1080")

    print("Iniciando o WebDriver...")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def extrair_precos(driver):
    """Extrai preços da página com diferentes métodos e regex."""
    precos = []
    
    # Listar diferentes XPaths ou seletores que podem conter preços
    possiveis_xpaths = [
        "//span[contains(text(), 'R$')]",  # Preço comum
        "//div[contains(text(), 'R$')]",  # Outra possível tag para preços
        "//p[contains(text(), 'R$')]",    # Em <p> tags
    ]

    # Buscar preços com base nos diferentes seletores
    for xpath in possiveis_xpaths:
        try:
            elementos = driver.find_elements(By.XPATH, xpath)
            for elemento in elementos:
                texto = elemento.text
                # Usar regex para capturar preços no formato "R$ 12,99" ou variações
                match = re.search(r'R\$\s*\d{1,3}(?:\.\d{3})*,\d{2}', texto)
                if match:
                    precos.append(match.group())  # Adiciona o preço encontrado
        except Exception as e:
            print(f"Erro ao buscar preços com XPath {xpath}: {e}")
    
    return precos

def buscar_precos():
    mercados = mercado_entry.get("1.0", tk.END).strip().split("\n")
    produtos = produto_entry.get("1.0", tk.END).strip().split("\n")
    
    if not mercados or not produtos:
        messagebox.showwarning("Aviso", "Preencha os mercados e os produtos antes de buscar.")
        return
    
    resultado_text.delete("1.0", tk.END)
    progresso["value"] = 0
    
    driver = iniciar_driver()  # Inicializa o driver
    
    try:
        total_tarefas = len(mercados) * len(produtos)
        progresso_max.set(total_tarefas)
        
        for mercado in mercados:
            mercado = mercado.strip()
            if not mercado:
                continue
            resultado_text.insert(tk.END, f"Mercado: {mercado}\n")
            driver.get(mercado)
            
            try:
                # Esperar que o campo de pesquisa esteja presente e visível
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "input"))
                )
            except Exception:
                resultado_text.insert(tk.END, "Erro: Campo de pesquisa não encontrado!\n")
                continue

            for produto in produtos:
                produto = produto.strip()
                if not produto:
                    continue
                
                try:
                    search_box.clear()
                    search_box.send_keys(produto + "\n")
                    
                    # Esperar que a página carregue os preços
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//span[contains(text(), 'R$')]"))
                    )
                    
                    precos = extrair_precos(driver)
                    if precos:
                        resultado_text.insert(tk.END, f"{produto}: {', '.join(precos)}\n")
                    else:
                        resultado_text.insert(tk.END, f"{produto}: Preço não encontrado\n")
                
                except Exception:
                    resultado_text.insert(tk.END, f"{produto}: Erro ao buscar\n")
                
                progresso.step(1)

    except Exception as e:
        resultado_text.insert(tk.END, f"Erro geral durante a busca: {e}\n")
    
    finally:
        driver.quit()
        messagebox.showinfo("Concluído", "Busca finalizada!")
        progresso["value"] = 0

def iniciar_busca_thread():
    threading.Thread(target=buscar_precos).start()

# Interface gráfica (Tkinter)
root = tk.Tk()
root.title("Comparador de Preços")

tk.Label(root, text="Digite as URLs dos mercados (um por linha):").pack()
mercado_entry = scrolledtext.ScrolledText(root, width=50, height=5)
mercado_entry.pack()

tk.Label(root, text="Digite a lista de produtos (um por linha):").pack()
produto_entry = scrolledtext.ScrolledText(root, width=50, height=5)
produto_entry.pack()

progresso_max = tk.IntVar()
progresso = Progressbar(root, orient="horizontal", length=300, mode="determinate", variable=progresso_max)
progresso.pack(pady=10)

btn_buscar = tk.Button(root, text="Buscar Preços", command=iniciar_busca_thread)
btn_buscar.pack(pady=5)

resultado_text = scrolledtext.ScrolledText(root, width=60, height=10)
resultado_text.pack()

root.mainloop()

