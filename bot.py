from flask import Flask, request, jsonify
from pydantic import BaseModel, ValidationError
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
import os, json, urllib.parse

app = Flask(__name__)
SESSION = "/tmp/rohlik-session.json"
PORT = int(os.environ.get("PORT", "10000"))

class Item(BaseModel):
    name: str
    qty: float | int = 1
    unit: str | None = None
    url: str | None = None
    notes: str | None = None
    allow_subs: bool = True

def load_cookies(context):
    if os.path.exists(SESSION):
        try:
            cookies = json.load(open(SESSION))
            context.add_cookies(cookies)
            return True
        except Exception:
            return False
    return False

def save_cookies(context):
    try:
        json.dump(context.cookies(), open(SESSION, "w"))
    except Exception:
        pass

def is_logged_in(page):
    html = page.content().lower()
    # jednoduchá heuristika – upravíme později
    return ("odhlásit" in html) or ("můj účet" in html) or ("muj ucet" in html)

def add_item(page, it: Item):
    if it.url:
        page.goto(it.url, wait_until="domcontentloaded")
    else:
        q = urllib.parse.quote_plus(it.name + (" " + it.notes if it.notes else ""))
        page.goto(f"https://www.rohlik.cz/hledat?q={q}", wait_until="domcontentloaded")
        page.wait_for_timeout(600)
        # TODO: doplnit selektor tlačítka "Do košíku" první položky
        # page.click("css=[data-test='product-card'] button:has-text('Do košíku')")
    # TODO: nastavit množství (klik na + nebo vyplnění inputu)
    page.wait_for_timeout(300)

def choose_slot(page):
    # TODO: vybrat doručovací slot (např. první dostupný/nejlevnější)
    page.wait_for_timeout(500)

@app.post("/prepare-basket")
def prepare_basket():
    try:
        payload = request.get_json(force=True)
        items = [Item(**x) for x in payload.get("items", [])]
        if not items:
            return jsonify({"status":"error","error":"No items provided"}), 400
    except ValidationError as e:
        return jsonify({"status":"error","error":e.errors()}), 400

    with sync_playwright() as p:
        # na Renderu poběží headless
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        load_cookies(context)
        page = context.new_page()
        page.goto("https://www.rohlik.cz/", wait_until="domcontentloaded")

        if not is_logged_in(page):
            browser.close()
            return jsonify({"status":"need_login","message":"No valid session. (Login flow doplníme v dalším kroku)"}), 401

        added = []
        for it in items:
            try:
                add_item(page, it)
                added.append({"name": it.name, "qty": it.qty})
            except PWTimeoutError:
                added.append({"name": it.name, "qty": it.qty, "warning":"timeout"})

        choose_slot(page)
        page.goto("https://www.rohlik.cz/objednavka", wait_until="domcontentloaded")
        summary_url = page.url
        save_cookies(context)
        browser.close()

    return jsonify({"status":"ready","summary_url":summary_url,"added":added})

@app.get("/healthz")
def healthz():
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
