#!/usr/bin/env python3
"""サルースHPの掲載内容・リンク・構造を検証する。依存なし。"""
import json
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")

SPACEMARKET = "https://www.spacemarket.com/spaces/4jcdii8xoubfzdjh/"
INSTABASE = "https://www.instabase.jp/space/5648474387"
LINE = "https://page.line.me/576lhqbg"
INSTAGRAM = "https://www.instagram.com/rental_space_salus/"

SECTIONS = ["top", "about", "features", "gallery", "scenes", "equipment", "price", "reviews", "access", "contact"]


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []  # (tag, attrs dict)
        self.jsonld = []
        self._in_jsonld = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, a))
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_jsonld = True

    def handle_startendtag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_jsonld = False

    def handle_data(self, data):
        if self._in_jsonld:
            self.jsonld.append(data)

    def find(self, tag, **attrs):
        return [a for t, a in self.tags if t == tag and all(a.get(k) == v for k, v in attrs.items())]


def load():
    with open(INDEX, encoding="utf-8") as f:
        raw = f.read()
    p = Page()
    p.feed(raw)
    return raw, p


def part(raw, sid):
    """id=sid のセクションから次のセクションの手前までのHTML。"""
    after = raw.split(f'id="{sid}"', 1)
    if len(after) < 2:
        return ""
    i = SECTIONS.index(sid)
    rest = after[1]
    if i + 1 < len(SECTIONS):
        rest = rest.split(f'id="{SECTIONS[i + 1]}"', 1)[0]
    return rest


def need(text, words, where):
    return [f"{where}に「{w}」がない" for w in words if w not in text]


# ---- checks: 各関数は失敗メッセージのリストを返す ----

def check_head(raw, p):
    errs = []
    if not p.find("meta", name="viewport"):
        errs.append("viewport meta がない")
    titles = re.findall(r"<title>(.*?)</title>", raw, re.S)
    if not titles or not all(w in titles[0] for w in ("広島", "横川", "レンタルスペース")):
        errs.append("title に 広島/横川/レンタルスペース が揃っていない")
    desc = p.find("meta", name="description")
    if not desc or "横川" not in desc[0].get("content", ""):
        errs.append("meta description がない、または横川を含まない")
    for prop in ("og:title", "og:description", "og:image", "og:type"):
        if not p.find("meta", property=prop):
            errs.append(f"{prop} がない")
    return errs


def check_jsonld(raw, p):
    if not p.jsonld:
        return ["JSON-LD がない"]
    try:
        data = json.loads("".join(p.jsonld))
    except json.JSONDecodeError as e:
        return [f"JSON-LD が壊れている: {e}"]
    errs = []
    if data.get("@type") != "LocalBusiness":
        errs.append("JSON-LD @type が LocalBusiness でない")
    addr = data.get("address", {})
    if addr.get("postalCode") != "733-0003":
        errs.append("JSON-LD 郵便番号が違う")
    if "三篠町2-4-15" not in addr.get("streetAddress", ""):
        errs.append("JSON-LD 住所が違う")
    return errs


def check_sections(raw, p):
    ids = {a.get("id") for _, a in p.tags}
    return [f"セクション #{i} がない" for i in SECTIONS if i not in ids]


def check_local_files(raw, p):
    errs = []
    for tag, a in p.tags:
        for key in ("src", "href"):
            v = a.get(key)
            if not v or v.startswith(("http", "#", "mailto:", "tel:", "data:")):
                continue
            if not os.path.exists(os.path.join(ROOT, v)):
                errs.append(f"ファイルがない: {v}")
    for m in re.findall(r'content="((?:images|css|js)/[^"]+)"', raw):
        if not os.path.exists(os.path.join(ROOT, m)):
            errs.append(f"ファイルがない: {m}")
    return errs


def check_images_alt(raw, p):
    return [f"alt がない img: {a.get('src')}" for a in p.find("img") if a.get("alt") is None]


def check_external_links(raw, p):
    errs = []
    for a in p.find("a"):
        href = a.get("href", "")
        if href.startswith("http"):
            if a.get("target") != "_blank" or "noopener" not in (a.get("rel") or ""):
                errs.append(f'外部リンクに target="_blank" rel="noopener" がない: {href}')
    return errs


def check_no_placeholder_text(raw, p):
    return [f"仮テキストが残っている: {w}" for w in ("TODO", "TBD", "Lorem", "ダミー") if w in raw]


def check_hero_about_features(raw, p):
    errs = []
    hero = part(raw, "top")
    errs += need(hero, ("横川駅", "徒歩8分", "72㎡", "最大30名", "¥1,980〜", SPACEMARKET), "ファーストビュー")
    errs += need(part(raw, "about"), ("健康の女神", "こころ", "からだ", "おかね", "2024年"), "Salusについて")
    errs += need(part(raw, "features"), ("アクセス", "広さ", "清潔"), "特徴")
    return errs


def check_scenes_equipment(raw, p):
    errs = []
    gal = [a for a in p.find("a") if "gallery__item" in (a.get("class") or "")]
    if len(gal) < 6:
        errs.append(f"ギャラリー項目が6件未満: {len(gal)}")
    errs += need(part(raw, "scenes"), ("セミナー", "講座・教室", "ヨガ・ピラティス", "撮影", "ワークショップ", "会議"), "ご利用シーン")
    eq = part(raw, "equipment")
    errs += need(eq, ("テーブル", "ソファ", "全身鏡", "電子レンジ", "キッチン", "Bluetoothスピーカー", "HDMI", "飲食可", "除菌",
                      "有料オプション", "プロジェクター", "スクリーン", "¥1,500"), "設備")
    if "Wi-Fi" in eq:
        errs.append("設備に仕様にない Wi-Fi が書かれている")
    return errs


def check_info_sections(raw, p):
    errs = []
    price = part(raw, "price")
    errs += need(price, ("¥1,980〜", "¥1,700", "¥1,900", "¥5,500", "¥6,000", "¥8,000", "¥9,000", "¥12,000", "¥13,000",
                         "¥15,000", "¥17,000", "20%オフ", "税込", "定期利用", LINE,
                         "1時間から", "9:00〜20:00", "72㎡", "最大30名（着席20名）",
                         "禁煙", "持ち帰り", "元に戻し", "マルチ商法", "宗教活動", "各予約サイトの規定に準じます"), "料金・ご利用案内")
    if re.search(r"1,650|2,194|17,424|23,100|090", raw):
        errs.append("掲載しない金額（予約サイト固有の金額）または電話番号が含まれている")
    rev = part(raw, "reviews")
    errs += need(rev, ("★4.7", "★5.0", SPACEMARKET, INSTABASE), "お客様の声")
    acc = part(raw, "access")
    errs += need(acc, ("〒733-0003", "広島県広島市西区三篠町2-4-15 桑原ビル2階", "JR横川駅", "横川一丁目駅", "三滝駅", "白島駅",
                       "徒歩8分", "徒歩12分", "徒歩15分", "google.com/maps", "Googleマップで開く"), "アクセス")
    errs += need(part(raw, "contact"), (SPACEMARKET, INSTABASE, LINE, INSTAGRAM), "予約・問い合わせ以降")
    if 'class="sticky-cta"' not in raw:
        errs.append("固定予約ボタンがない")
    return errs


def check_js_hooks(raw, p):
    errs = []
    path = os.path.join(ROOT, "js", "main.js")
    js = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    for sel in (".nav-toggle", "site-nav", ".gallery__item", ".sticky-cta", "lightbox"):
        if sel not in js:
            errs.append(f"main.js が {sel} を扱っていない")
    if not p.find("dialog", id="lightbox"):
        errs.append("dialog#lightbox がない")
    return errs


CHECKS = [
    check_head,
    check_jsonld,
    check_sections,
    check_local_files,
    check_images_alt,
    check_external_links,
    check_no_placeholder_text,
    check_hero_about_features,
    check_scenes_equipment,
    check_info_sections,
    check_js_hooks,
]


def main():
    raw, p = load()
    fails = []
    for c in CHECKS:
        fails += c(raw, p)
    for f in fails:
        print("FAIL:", f)
    if fails:
        sys.exit(1)
    print(f"OK ({len(CHECKS)} checks)")


if __name__ == "__main__":
    main()
