import os
import streamlit as st
import streamlit.components.v1 as components
import requests
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# ページ設定
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="情報漏洩ダメージ・シミュレーター",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# サイドバーアイコン文字化け修正（Material Symbols → 矢印に置換）
# ─────────────────────────────────────────────
components.html("""
<script>
const fix = () => {
  const root = window.parent.document;
  root.querySelectorAll('span').forEach(el => {
    const t = el.textContent.trim();
    if (t === 'keyboard_double_arrow_right') el.textContent = '»';
    if (t === 'keyboard_double_arrow_left') el.textContent = '«';
    if (t === 'close') el.textContent = '✕';
  });
};
fix();
const obs = new MutationObserver(fix);
obs.observe(window.parent.document.body, { childList: true, subtree: true });
</script>
""", height=0)

# ─────────────────────────────────────────────
# スタイル
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&display=swap');
    html, body, [class*="st-"] {
        font-family: 'Noto Sans JP', sans-serif;
    }


    /* テキスト入力欄 */
    .stTextInput > div > div > input {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1.5px solid #e0e0e0 !important;
        font-size: 16px !important;
        border-radius: 8px !important;
    }
    .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #111111 !important;
    }

    /* ヘッダーバナー */
    .header-banner {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #1565c0 100%);
        color: white;
        padding: 32px 36px;
        border-radius: 14px;
        margin-bottom: 32px;
    }
    .header-banner h1 {
        color: white; font-size: 1.9rem; margin: 0 0 8px 0;
        font-family: 'Noto Sans JP', sans-serif; font-weight: 700;
    }
    .header-banner p {
        color: #bbdefb; margin: 0; font-size: 0.95rem;
        font-family: 'Noto Sans JP', sans-serif;
    }

    /* 財務サマリーカード */
    .fin-card {
        background: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 10px;
        padding: 18px 20px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .fin-card .label {
        font-size: 0.8rem; color: #888; margin-bottom: 6px;
        font-family: 'Noto Sans JP', sans-serif;
    }
    .fin-card .value {
        font-size: 1.4rem; font-weight: 700; color: #212121;
        font-family: 'Noto Sans JP', sans-serif;
    }

    /* ─── ヒーロー: 被害総額 ─── */
    .damage-hero {
        background: linear-gradient(135deg, #fff5f5 0%, #ffebee 100%);
        border: 1px solid #ffcdd2;
        border-radius: 14px;
        padding: 36px 32px;
        text-align: center;
        margin: 24px 0;
    }
    .damage-hero .damage-label {
        font-size: 0.95rem; color: #b71c1c; font-weight: 500;
        letter-spacing: 0.08em; margin-bottom: 8px;
        font-family: 'Noto Sans JP', sans-serif;
    }
    .damage-hero .damage-amount {
        font-size: 3.2rem; font-weight: 900; color: #c62828;
        margin: 4px 0 12px 0; line-height: 1.2;
        font-family: 'Noto Sans JP', sans-serif;
    }
    .damage-hero .damage-sub {
        font-size: 1rem; color: #d32f2f; font-weight: 500;
        font-family: 'Noto Sans JP', sans-serif;
    }

    /* ─── 横棒比較バー ─── */
    .bar-section {
        margin: 20px 0 8px 0;
    }
    .bar-section .bar-title {
        font-size: 0.95rem; font-weight: 700; color: #333;
        margin-bottom: 14px;
        font-family: 'Noto Sans JP', sans-serif;
    }
    .bar-row {
        display: flex; align-items: center; margin-bottom: 10px;
    }
    .bar-row .bar-label {
        width: 110px; font-size: 0.82rem; color: #555;
        font-weight: 500; flex-shrink: 0;
        font-family: 'Noto Sans JP', sans-serif;
    }
    .bar-row .bar-track {
        flex: 1; height: 32px; background: #f5f5f5;
        border-radius: 6px; position: relative;
        display: flex; align-items: center;
    }
    .bar-row .bar-fill {
        height: 100%; border-radius: 6px;
        transition: width 0.6s ease;
    }
    .bar-fill.profit { background: linear-gradient(90deg, #1565c0, #1e88e5); }
    .bar-fill.damage { background: linear-gradient(90deg, #c62828, #e53935); }
    .bar-row .bar-value {
        font-size: 0.82rem; font-weight: 700; margin-left: 10px;
        white-space: nowrap; color: #333;
        font-family: 'Noto Sans JP', sans-serif;
    }

    /* 内訳カード */
    .breakdown-card {
        background: #fafafa;
        border: 1px solid #eee;
        border-radius: 8px;
        padding: 14px 12px;
        text-align: center;
    }
    .breakdown-card .bd-label {
        font-size: 0.72rem; color: #888; margin-bottom: 4px;
        font-family: 'Noto Sans JP', sans-serif;
    }
    .breakdown-card .bd-value {
        font-size: 1.05rem; font-weight: 700; color: #333;
        font-family: 'Noto Sans JP', sans-serif;
    }

    /* セールスピッチ */
    .pitch-box {
        background: #f8fdf8;
        border: 1px solid #c8e6c9;
        border-left: 5px solid #2e7d32;
        border-radius: 10px;
        padding: 24px 28px;
        margin: 24px 0;
        font-size: 0.98rem;
        line-height: 1.9;
        color: #2e7d32;
        font-family: 'Noto Sans JP', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

BASE_URL = "https://edinetdb.jp/v1"

# ─────────────────────────────────────────────
# API 関数群
# ─────────────────────────────────────────────

def search_company(query: str, api_key: str) -> list:
    """企業名・証券コードで検索し候補リストを返す。"""
    headers = {"X-API-Key": api_key} if api_key else {}
    try:
        r = requests.get(
            f"{BASE_URL}/search",
            params={"q": query},
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        return r.json().get("data", [])
    except Exception as e:
        st.error(f"検索エラー: {e}")
        return []


def get_financials(edinet_code: str, api_key: str) -> dict | None:
    """
    /companies/{code}/financials から最新年度の財務データを取得。
    レスポンス: {"data": [{"fiscal_year":..., "revenue":..., ...}, ...]}
    """
    headers = {"X-API-Key": api_key}
    try:
        r = requests.get(
            f"{BASE_URL}/companies/{edinet_code}/financials",
            headers=headers,
            timeout=15,
        )
        if r.status_code == 401:
            st.error("❌ APIキーが無効です。サイドバーで正しいAPIキーを入力してください。")
            return None
        if r.status_code == 403:
            st.error("❌ APIキーの権限が不足しています。EDINET DBのダッシュボードをご確認ください。")
            return None
        r.raise_for_status()

        data = r.json().get("data", [])
        if not data:
            return None

        # 最新年度（リストの先頭）を使用
        latest = data[0]
        return latest

    except Exception as e:
        st.error(f"財務データ取得エラー: {e}")
        return None


def extract_financials(fin: dict) -> tuple:
    """
    財務データdictから売上高・利益・利益種別ラベルを抽出。
    優先順位: operating_income → ordinary_income → net_income
    """
    revenue = fin.get("revenue")

    # 利益の優先順位フォールバック
    profit = None
    profit_label = ""

    oi = fin.get("operating_income")
    if oi is not None and oi != 0:
        profit = oi
        profit_label = "営業利益"
    else:
        ord_i = fin.get("ordinary_income")
        if ord_i is not None and ord_i != 0:
            profit = ord_i
            profit_label = "経常利益"
        else:
            ni = fin.get("net_income")
            if ni is not None and ni != 0:
                profit = ni
                profit_label = "純利益"

    fiscal_year = fin.get("fiscal_year", "不明")
    return revenue, profit, profit_label, fiscal_year


def calc_damage(revenue: float) -> dict:
    """
    損害額の計算ロジック。
    - 固定被害額: 5,000万円
    - 通知・調査費用: 売上高の0.05%
    - 訴訟・賠償リスク: 売上高の0.3%
    - ブランド毀損: 売上高の0.8%
    - 株価下落: 売上高の0.5%
    """
    fixed        = 50_000_000
    notification = revenue * 0.0005
    litigation   = revenue * 0.003
    brand        = revenue * 0.008
    stock_drop   = revenue * 0.005

    total = fixed + notification + litigation + brand + stock_drop

    return {
        "fixed":        fixed,
        "notification": notification,
        "litigation":   litigation,
        "brand":        brand,
        "stock_drop":   stock_drop,
        "total":        total,
    }


def fmt_oku(yen: float) -> str:
    """円を「〇〇億円」表記に変換。"""
    oku = yen / 1e8
    if oku >= 1:
        return f"{oku:,.1f}億円"
    else:
        man = yen / 1e4
        return f"{man:,.0f}万円"


# ─────────────────────────────────────────────
# サイドバー
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔑 APIキー設定")
    saved_key = os.environ.get("EDINET_API_KEY", "")
    api_key = st.text_input(
        "EDINET DB APIキー",
        value=saved_key,
        type="password",
        placeholder="edb_xxxxxxxxxxxxxxxx",
        help="https://edinetdb.jp/developers で無料取得できます",
    )
    if api_key:
        st.success("✅ APIキーが設定されました")
    else:
        st.warning("⚠️ APIキーを入力してください")
        st.markdown(
            "[APIキーを無料取得する →](https://edinetdb.jp/developers)",
            unsafe_allow_html=False,
        )

    st.divider()
    st.markdown("### 使い方")
    st.markdown(
        "1. 企業名または証券コードを入力\n"
        "2. 「シミュレーション開始」をクリック\n"
        "3. 複数候補が出たら対象企業を選択"
    )
    st.divider()
    st.markdown("### 入力例")
    st.markdown(
        "- ソフトバンク\n"
        "- 富士通\n"
        "- NTTデータ\n"
        "- 7203（トヨタ）"
    )

# ─────────────────────────────────────────────
# メイン画面
# ─────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
  <h1>🔐 情報漏洩ダメージ・シミュレーター</h1>
  <p>上場企業の有価証券報告書（EDINET）をもとに、情報漏洩インシデント発生時の経営へのダメージを定量的に可視化します。</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### 企業を検索する")

col_input, col_btn = st.columns([5, 1])
with col_input:
    query = st.text_input(
        "企業名または証券コード",
        placeholder="例: ソフトバンク、富士通、7203",
        label_visibility="collapsed",
    )
with col_btn:
    run = st.button("シミュレーション開始", type="primary", use_container_width=True)

# ─────────────────────────────────────────────
# 検索・シミュレーション実行
# ─────────────────────────────────────────────
if run:
    if not api_key:
        st.error("❌ 左サイドバーにAPIキーを入力してください。")
        st.stop()
    if not query.strip():
        st.warning("企業名または証券コードを入力してください。")
        st.stop()

    with st.spinner("企業を検索中..."):
        candidates = search_company(query.strip(), api_key)

    if not candidates:
        st.error(f"「{query}」に一致する企業が見つかりませんでした。別のキーワードをお試しください。")
        st.stop()

    # 前回の結果をクリアして候補を保存
    st.session_state.pop("selected", None)
    st.session_state["candidates"] = candidates

    if len(candidates) == 1:
        st.session_state["selected"] = candidates[0]
    else:
        st.session_state.pop("selected", None)

# ─── 候補選択フロー ───
if "candidates" in st.session_state:
    candidates = st.session_state["candidates"]

    if len(candidates) > 1 and "selected" not in st.session_state:
        st.info("複数の候補が見つかりました。対象企業を選択してください。")
        options = {
            f"{c.get('name', c.get('filer_name', '不明'))}　（コード: {c.get('sec_code', c.get('edinet_code', '?'))}）": c
            for c in candidates
        }
        choice = st.selectbox("企業を選択", list(options.keys()))
        if st.button("この企業でシミュレーション", type="primary"):
            st.session_state["selected"] = options[choice]
            st.rerun()
        st.stop()

if "selected" in st.session_state:
    selected = st.session_state["selected"]
    company_name = selected.get("name") or selected.get("filer_name") or "不明"
    edinet_code  = selected.get("edinet_code") or selected.get("edinetCode") or ""

    st.success(f"「{company_name}」を選択しました。")

    if not edinet_code:
        st.error("EDINETコードが取得できませんでした。")
        st.stop()

    with st.spinner("財務データを取得中..."):
        fin_data = get_financials(edinet_code, api_key)

    if fin_data is None:
        st.error("財務データを取得できませんでした。しばらくしてから再度お試しください。")
        st.stop()

    revenue, profit, profit_label, fiscal_year = extract_financials(fin_data)

    if revenue is None:
        st.error(
            f"「{company_name}」の売上高データが取得できませんでした。\n\n"
            "バイオベンチャー等の開発段階企業では売上高がEDINETに記載されていない場合があります。"
        )
        st.stop()

    # ─────────────────────────────────────────
    # 結果表示
    # ─────────────────────────────────────────
    damage = calc_damage(revenue)
    total_damage = damage["total"]

    st.divider()

    # ─── 財務サマリー（コンパクト） ───
    st.markdown(f"#### {company_name}　─　{fiscal_year}年度")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="fin-card">
          <div class="label">売上高（{fiscal_year}年度）</div>
          <div class="value">{fmt_oku(revenue)}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        if profit is not None:
            st.markdown(f"""
            <div class="fin-card">
              <div class="label">{profit_label}（{fiscal_year}年度）</div>
              <div class="value">{fmt_oku(profit)}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="fin-card">
              <div class="label">利益データ</div>
              <div class="value">─</div>
            </div>""", unsafe_allow_html=True)

    # ─── ヒーロー: 被害総額 ───
    if profit is not None and profit > 0:
        damage_ratio = (total_damage / profit) * 100
        sub_text = f"{fiscal_year}年度{profit_label}（{fmt_oku(profit)}）の <strong>{damage_ratio:.1f}%</strong> に相当"
    elif profit is not None:
        damage_ratio = 100.0
        sub_text = f"{profit_label}が赤字の状況下で、さらにこの額のキャッシュアウトが発生"
    else:
        damage_ratio = None
        sub_text = f"売上高の <strong>{(total_damage/revenue*100):.2f}%</strong> に相当するキャッシュアウト"

    st.markdown(f"""
    <div class="damage-hero">
      <div class="damage-label">情報漏洩インシデント発生時の想定損害総額</div>
      <div class="damage-amount">約 {fmt_oku(total_damage)}</div>
      <div class="damage-sub">{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # ─── 横棒比較バー（営業利益 vs 損害額） ───
    if profit is not None and profit > 0:
        bar_max = max(profit, total_damage)
        profit_pct = (profit / bar_max) * 100
        damage_pct = (total_damage / bar_max) * 100

        st.markdown(f"""
        <div class="bar-section">
          <div class="bar-title">{profit_label}と想定損害額の比較</div>
          <div class="bar-row">
            <div class="bar-label">{profit_label}</div>
            <div class="bar-track">
              <div class="bar-fill profit" style="width: {profit_pct:.1f}%;"></div>
              <div class="bar-value">{fmt_oku(profit)}</div>
            </div>
          </div>
          <div class="bar-row">
            <div class="bar-label">想定損害額</div>
            <div class="bar-track">
              <div class="bar-fill damage" style="width: {damage_pct:.1f}%;"></div>
              <div class="bar-value" style="color: #c62828;">{fmt_oku(total_damage)}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ─── 損害額の内訳 ───
    st.markdown("")
    st.markdown("##### 損害内訳")
    breakdown_cols = st.columns(5)
    items = [
        ("フォレンジック等", damage["fixed"]),
        ("通知・調査費用", damage["notification"]),
        ("訴訟・賠償", damage["litigation"]),
        ("ブランド毀損", damage["brand"]),
        ("株価下落影響", damage["stock_drop"]),
    ]
    for col, (label, val) in zip(breakdown_cols, items):
        with col:
            st.markdown(f"""
            <div class="breakdown-card">
              <div class="bd-label">{label}</div>
              <div class="bd-value">{fmt_oku(val)}</div>
            </div>""", unsafe_allow_html=True)

    # ─── セールスピッチ ───
    ratio_str = f"{damage_ratio:.1f}%" if damage_ratio is not None else f"{(total_damage/revenue*100):.2f}%（対売上高）"
    st.markdown(f"""
    <div class="pitch-box">
      <strong>情報漏洩インシデントの約8割は「人的ミス（誤送信・紛失・設定ミス）」が原因です。</strong><br><br>
      この <strong>{ratio_str} の利益喪失リスク</strong>は、従業員の行動を変えることで防げます。<br><br>
      <strong>「ラーニングハブ for セキュリティ」</strong>── 分散学習で本質的なセキュリティ意識を組織に定着させ、御社の利益を守ります。
    </div>
    """, unsafe_allow_html=True)
