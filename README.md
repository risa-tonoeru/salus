# レンタルスペース サルース HP

広島・横川のレンタルスペース「サルース」の1ページのホームページです。

## 構成
- `index.html` … ページ本体（文章・料金・リンクはすべてここ）
- `css/style.css` … デザイン
- `js/main.js` … スマホのメニュー、写真の拡大表示、画面下の予約ボタン
- `images/` … 掲載画像
- `tools/optimize_photos.py` … 写真をWeb用に縮小（向き補正・位置情報削除）
- `tests/check_site.py` … 掲載内容・リンクの自動チェック

## 手元で表示する
```
python3 -m http.server 8765
```
ブラウザで http://localhost:8765 を開く。

## 写真を差し替える
```
python3 tools/optimize_photos.py "元の写真のパス.HEIC" gallery-2.jpg 1400
```
差し替えたら `index.html` の該当する `alt`（写真の説明文）も書き換える。

## 料金を変えるとき
`index.html` の `id="price"` の部分と、ファーストビューの「¥1,700〜」、
`tests/check_site.py` の金額チェックをあわせて直す。

## 内容チェック
```
python3 tests/check_site.py
```
`OK` と出れば、住所・定員・料金・リンクなどが設計どおり載っています。

## 公開（GitHub Pages・無料）
1. GitHub に新しいリポジトリを作成し、このフォルダを push する
2. リポジトリの Settings → Pages → Branch を `main` / `/ (root)` にして保存
3. 数分後に `https://<ユーザー名>.github.io/<リポジトリ名>/` で公開される
4. 独自ドメインを使う場合は、同じ画面の Custom domain に設定する
