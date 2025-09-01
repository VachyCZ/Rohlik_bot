# Rohlik Basket Bot

Automatizace pro **Rohlik.cz** – připraví nákupní košík na tvém účtu, zastaví těsně před platbou a pošle ti odkaz na souhrn objednávky.  
Plánováno k použití s **Render.com** (nasazení) a napojením na **Make (Integromat)** nebo jiný orchestrátor.

---

## 🚀 Deployment na Render

1. Připrav GitHub repozitář (součástí jsou soubory: `Dockerfile`, `bot.py`, `requirements.txt`, `render.yaml`).  
2. Na [Render.com](https://render.com) založ **New → Blueprint**, vyber tento repozitář, branch `main`.  
3. Render automaticky vytvoří službu podle `render.yaml`.  
4. Po dokončení build/deploy otevři URL služby a přidej `/healthz`, např.:
