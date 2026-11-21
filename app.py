import json
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="AGF 2026 카탈로그", page_icon="🎁", layout="wide")
st.markdown("""
<style>
.block-container {max-width:1050px;padding:1rem .8rem}
.x-highlight {border:2px solid #3478f6;border-radius:12px;padding:12px 16px;
background:rgba(52,120,246,.09);font-size:1.05rem;font-weight:700}
@media(max-width:650px){.block-container{padding-top:.6rem}}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    def read(name):
        return json.loads((ROOT / name).read_text(encoding="utf-8"))
    return read("company_catalogs.json"), read("catalog.json"), read("events.json"), read("purchase_benefits.json"), read("product_sources.json"), read("booth_locations.json")

catalogs, products, events, benefits, sources, booths = load_data()
if "basket" not in st.session_state:
    st.session_state.basket = {}
if "basket_version" not in st.session_state:
    st.session_state.basket_version = 0

def show_images(names):
    count = 0
    for name in dict.fromkeys(names):
        path = ROOT / "assets" / Path(name).name
        if path.is_file() and path.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            st.image(str(path), use_container_width=True)
            count += 1
    return count

def official_x(name):
    url = catalogs.get(name, {}).get("x_url")
    if url:
        st.markdown(f'<div class="x-highlight">𝕏 {name} 공식 X · 최신 굿즈/이벤트 공지</div>', unsafe_allow_html=True)
        st.link_button(f"𝕏 {name} 공식 X 바로가기", url, type="primary", use_container_width=True)

def product_price(p):
    if p.get("price_tbd") or p.get("price") is None or int(p.get("price") or 0) <= 0:
        return None
    return int(p["price"])

def seller(p):
    return sources.get(str(p["id"]), {}).get("seller", p["company"])

def available_products():
    return [p for p in products if product_price(p) is not None]

def selected_rows():
    lookup = {str(p["id"]): p for p in available_products()}
    rows = []
    for pid, qty in st.session_state.basket.items():
        if pid in lookup and qty > 0:
            p = lookup[pid]
            rows.append((p, qty, product_price(p) * qty))
    return rows

def add_item(pid, qty):
    st.session_state.basket[pid] = st.session_state.basket.get(pid, 0) + qty

def update_qty(pid, qty):
    st.session_state.basket_version += 1
    if qty <= 0:
        st.session_state.basket.pop(pid, None)
    else:
        st.session_state.basket[pid] = qty

def show_benefits(rows):
    totals = {}
    for p, qty, amount in rows:
        key = seller(p)
        totals[key] = totals.get(key, 0) + amount
    matched = False
    for benefit in benefits:
        company = benefit["seller"]
        threshold = int(benefit["threshold"])
        spent = totals.get(company, 0)
        if spent == 0:
            continue
        if spent >= threshold:
            st.success(f"🎁 구매 특전 조건 달성! {benefit['title']} — {company} 구매금액 {spent:,}원")
            matched = True
        else:
            st.info(f"🎁 {benefit['title']}: {company}에서 {threshold-spent:,}원 더 구매하면 조건 달성")
        if benefit.get("note"):
            st.caption(benefit["note"])
    return matched

st.title("🎁 AGF 2026 업체별 카탈로그")
st.caption("업체별 전체 이미지 · 이벤트·경품 · 카탈로그 연동 계산기 · 배치도")
page1, page2, page3 = st.tabs(["🏬 업체별 카탈로그", "🧮 구매 계산기", "🗺️ AGF 배치도"])

with page1:
    game_tab, anime_tab = st.tabs(["🎮 게임", "🎨 피규어·애니"])
    internal = {child for v in catalogs.values() for child in v.get("children", [])}
    for category, category_tab in [("🎮 게임", game_tab), ("🎨 피규어·애니", anime_tab)]:
        with category_tab:
            names = [n for n, v in catalogs.items() if v.get("group") == category and n not in internal]
            name = st.selectbox("🏷️ 업체 선택", names, index=None, placeholder="업체를 선택하세요", key="company_" + category)
            if not name:
                st.info("업체를 선택하면 카탈로그를 볼 수 있습니다.")
                continue
            parent = name
            children = catalogs[parent].get("children", [])
            if children:
                st.caption("하위 카탈로그를 선택하면 해당 업체의 사진과 공식 X를 확인할 수 있습니다.")
                name = st.selectbox("📂 세부 카탈로그", [parent] + children, key="sub_" + parent)
            entry = catalogs[name]
            st.subheader(name)
            banners = entry.get("banner_images", [])
            if banners:
                show_images(banners)
            official_x(name)
            # 내부 카탈로그에는 부스 번호를 표시하지 않습니다.
            if name not in internal:
                codes = booths.get(name, [])
                if codes:
                    st.success(f"📍 AGF 2026 부스: **{', '.join(codes)}**")
                else:
                    st.caption("부스 번호 미등록")
            sales, free = st.tabs(["🛍️ 판매 상품", "🎁 이벤트·무료 경품"])
            for tab, key, title in ((sales, "sales_images", "판매 상품"), (free, "event_images", "이벤트·무료 경품")):
                with tab:
                    st.markdown("#### " + name + " — " + title)
                    total = show_images(entry.get(key, []))
                    for related in entry.get("related_catalogs", []):
                        imgs = related.get(key, [])
                        if not imgs:
                            continue
                        st.divider()
                        st.markdown("#### " + related.get("title", related.get("company", "관련 카탈로그")))
                        if related.get("note"):
                            st.caption(related["note"])
                        total += show_images(imgs)
                    if not total:
                        st.info("등록된 " + title + " 이미지가 없습니다.")
                    else:
                        st.caption(f"이미지 {total}장 · 원본 비율 유지")

with page2:
    st.subheader("🧮 카탈로그 연동 구매 계산기")
    st.caption("개별 상품 사진 없이 상품명·가격·수량만 선택합니다. 실제 구매·결제는 진행되지 않습니다.")
    purchasable = available_products()
    sellers = sorted({seller(p) for p in purchasable})
    selected_seller = st.selectbox("판매 업체", ["전체"] + sellers)
    matching = [p for p in purchasable if selected_seller == "전체" or seller(p) == selected_seller]
    if matching:
        labels = {
            str(p["id"]): f"[{seller(p)}] {p['name']} — {product_price(p):,}원"
            for p in matching
        }
        pid = st.selectbox("상품 선택", list(labels), format_func=lambda x: labels[x])
        chosen = next(p for p in matching if str(p["id"]) == pid)
        max_qty = chosen.get("limit_qty")
        if max_qty and int(max_qty) > 0:
            st.caption(f"상품별 구매 제한 안내: {max_qty}개 (현장 규정 확인)")
        quantity = st.number_input("추가 수량", min_value=1, max_value=999, value=1, step=1)
        if st.button("계산 목록에 추가", type="primary", use_container_width=True):
            current = st.session_state.basket.get(pid, 0)
            if max_qty and int(max_qty) > 0 and current + quantity > int(max_qty):
                st.warning(f"이 상품의 등록된 구매 제한은 {max_qty}개입니다.")
            else:
                add_item(pid, int(quantity))
                st.rerun()
    else:
        st.info("가격이 등록된 상품이 없습니다.")

    st.divider()
    st.markdown("### 🧾 선택한 상품")
    rows = selected_rows()
    if not rows:
        st.info("상품을 선택해 계산 목록에 추가해 주세요.")
    else:
        for p, qty, amount in rows:
            pid = str(p["id"])
            with st.container(border=True):
                a, b, c = st.columns([5, 2, 2], vertical_alignment="center")
                a.markdown(f"**{p['name']}**\n\n{seller(p)} · {product_price(p):,}원/개")
                new_qty = b.number_input("수량", min_value=0, max_value=999, value=qty, step=1, key=f"cart_{pid}_{st.session_state.basket_version}")
                if new_qty != qty:
                    limit = p.get("limit_qty")
                    if limit and int(limit) > 0 and new_qty > int(limit):
                        st.warning(f"{p['name']}: 구매 제한 {limit}개")
                    else:
                        update_qty(pid, int(new_qty))
                        st.rerun()
                c.metric("소계", f"{amount:,}원")
        total = sum(amount for _, _, amount in rows)
        st.metric("총 예상 구매 금액", f"{total:,}원")
        st.markdown("### 🎁 구매 이벤트 안내")
        show_benefits(rows)
        if st.button("계산 목록 전체 초기화"):
            st.session_state.basket = {}
            st.session_state.basket_version += 1
            st.rerun()
    st.caption("가격 미정·무료 상품은 계산 대상에서 제외합니다. 이벤트 조건과 가격은 공식 공지로 최종 확인하세요.")

with page3:
    st.link_button("𝕏 AGF KOREA 공식 X 바로가기", "https://x.com/AGF_Korea", type="primary", use_container_width=True)
    st.subheader("🗺️ AGF 2026 전체 배치도")
    path = ROOT / "assets" / "agf2026_floorplan.jpg"
    if path.is_file():
        st.image(str(path), use_container_width=True)
        st.download_button("📥 배치도 다운로드", path.read_bytes(), "AGF2026_배치도.jpg", "image/jpeg")
    else:
        st.info("배치도 이미지가 아직 없습니다.")
    detailed = ROOT / "assets" / "agf2026_floorplan_detailed.png"
    if detailed.is_file():
        st.markdown("### 📌 상세 배치도 · 업체별 부스 번호")
        st.image(str(detailed), use_container_width=True)
        st.caption("업로드한 최신 상세 배치도입니다. 업체별 부스 코드는 오른쪽 범례를 확인하세요.")
        st.download_button("📥 상세 배치도 다운로드", detailed.read_bytes(), "AGF2026_상세배치도.png", "image/png", use_container_width=True)

