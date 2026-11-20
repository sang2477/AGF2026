
import json
from pathlib import Path

import streamlit as st


# ==========================================
# 기본 설정
# ==========================================

ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="AGF 2026 굿즈·이벤트 카탈로그",
    page_icon="🎁",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    max-width: 1050px;
    padding: 1rem 0.8rem;
}
@media (max-width: 650px) {
    .block-container {
        padding-top: 0.6rem;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# 데이터 불러오기
# ==========================================

def load():
    products = json.loads(
        (ROOT / "catalog.json").read_text(encoding="utf-8")
    )
    events = json.loads(
        (ROOT / "events.json").read_text(encoding="utf-8")
    )
    return products, events


products, events = load()


def picture(name):
    if not name:
        return

    path = ROOT / "assets" / name

    if path.is_file():
        st.image(str(path), use_container_width=True)


def price_text(product):
    if product.get("price_tbd"):
        return "가격 미정"

    price = product.get("price")
    if price is None:
        return "가격 미정"

    return f"{int(price):,}원"


# ==========================================
# 공식 X 계정
# ==========================================

OFFICIAL_X_CATEGORIES = {
    "🎮 게임": [
        ("아스트라에 오라티오", "https://x.com/Asora_KR"),
        ("아주르 프로밀리아", "https://x.com/AzurPromiliaKR"),
        ("승리의 여신: 니케", "https://x.com/NIKKE_kr"),
        ("트릭컬 리바이브", "https://x.com/Trickcal_Re"),
        ("홀로라이브 드림스", "https://x.com/holo_dreams_en"),
        ("니벨아레나", "https://x.com/NivelArena"),
        ("요스타", "https://x.com/YostarStoreKR"),
    ],
    "🛍️ 피규어·굿즈 샵": [
        ("amiami", "https://x.com/amiami_figure"),
        ("애니플러스", "https://x.com/ANIPLUS_SHOP"),
        ("애니메이트", "https://x.com/animateonlineKR"),
        ("한림사", "https://x.com/hanlimsa"),
        ("GNFTOYZ", "https://x.com/GNFTOYZ"),
        ("지니뮤직", "https://x.com/genie_kt"),
    ],
}


# ==========================================
# 메인 화면
# ==========================================

st.title("🎁 AGF 2026 굿즈·이벤트 카탈로그")

st.caption(
    "AGF 2026 참가 업체별 굿즈, 가격, "
    "무료 이벤트 및 행사 정보를 확인하는 개인 카탈로그입니다."
)

t1, t2, t3 = st.tabs([
    "🛍️ 업체별 굿즈 카탈로그",
    "🎁 무료·이벤트",
    "🗺️ 배치도·공식 X"
])


# ==========================================
# 1. 업체별 굿즈 카탈로그
# ==========================================

with t1:

    st.subheader("🛍️ 업체별 굿즈 카탈로그")

    companies = sorted({
        p["company"] for p in products
    })

    categories = sorted({
        p.get("category") or "기타"
        for p in products
    })

    a, b = st.columns(2)

    company = a.selectbox(
        "업체 선택",
        ["전체"] + companies
    )

    category = b.selectbox(
        "상품 카테고리",
        ["전체"] + categories
    )

    subcategories = sorted({
        p["subcategory"]
        for p in products
        if p.get("subcategory")
        and (
            company == "전체"
            or p["company"] == company
        )
    })

    subcategory = (
        st.selectbox(
            "내부 분류",
            ["전체"] + subcategories
        )
        if subcategories
        else "전체"
    )

    query = st.text_input(
        "🔍 굿즈 검색",
        placeholder="상품명 입력"
    )

    filtered = [
        p for p in products
        if (
            company == "전체"
            or p["company"] == company
        )
        and (
            category == "전체"
            or (p.get("category") or "기타") == category
        )
        and (
            subcategory == "전체"
            or p.get("subcategory") == subcategory
        )
        and query.lower() in p["name"].lower()
    ]

    st.caption(f"총 {len(filtered)}개 굿즈")

    if not filtered:
        st.info("조건에 맞는 굿즈가 없습니다.")

    for company_name in sorted({
        p["company"] for p in filtered
    }):

        st.markdown(f"### 🏷️ {company_name}")

        company_products = [
            p for p in filtered
            if p["company"] == company_name
        ]

        for p in company_products:

            with st.container(border=True):

                left, right = st.columns([1, 2])

                with left:
                    picture(p.get("image_path", ""))

                with right:

                    st.markdown(f"#### {p['name']}")

                    info = [
                        p.get("subcategory"),
                        p.get("category") or "기타"
                    ]

                    st.caption(
                        " · ".join(
                            str(x) for x in info if x
                        )
                    )

                    st.markdown(
                        f"**💰 {price_text(p)}**"
                    )

                    if p.get("limit_qty"):
                        st.caption(
                            f"구매 제한: "
                            f"1인 {p['limit_qty']}개"
                        )

                    if p.get("spec"):
                        st.caption(p["spec"])

                    if p.get("description"):
                        st.write(p["description"])

                    # 기존 아주르 상세 이미지 제외 설정 유지
                    if (
                        p["company"] != "아주르 프로밀리아"
                        and p.get("detail_images")
                    ):
                        with st.expander("📷 상세 사진 보기"):
                            for detail in p["detail_images"]:
                                picture(detail)

                    if p.get("source"):
                        st.link_button(
                            "🔗 공식 상품 공지",
                            p["source"],
                            use_container_width=True
                        )


# ==========================================
# 2. 무료·이벤트 카테고리
# ==========================================

with t2:

    st.subheader("🎁 무료·이벤트 카테고리")

    st.caption(
        "무료 배포, 스탬프 랠리, 경품 수령, "
        "구매 특전 정보를 확인할 수 있습니다."
    )

    event_companies = sorted({
        e["company"] for e in events
    })

    event_kinds = [
        "무료 배포",
        "스탬프 랠리",
        "경품 수령",
        "구매 특전"
    ]

    a, b = st.columns(2)

    event_company = a.selectbox(
        "게임 / 업체",
        ["전체"] + event_companies
    )

    event_kind = b.selectbox(
        "이벤트 종류",
        ["전체"] + [
            k for k in event_kinds
            if any(
                e.get("kind") == k
                for e in events
            )
        ]
    )

    event_query = st.text_input(
        "🔍 이벤트 검색",
        placeholder="쇼핑백, 스탬프, 핫팩..."
    )

    matching = [
        e for e in events
        if (
            event_company == "전체"
            or e["company"] == event_company
        )
        and (
            event_kind == "전체"
            or e.get("kind") == event_kind
        )
        and event_query.lower() in e["title"].lower()
    ]

    st.caption(
        f"총 {len(matching)}개 이벤트"
    )

    if not matching:
        st.info("조건에 맞는 이벤트가 없습니다.")

    for company_name in sorted({
        e["company"] for e in matching
    }):

        st.markdown(f"### 🎮 {company_name}")

        group = [
            e for e in matching
            if e["company"] == company_name
        ]

        if company_name == "아주르 프로밀리아":

            with st.expander(
                "🖼️ 아주르 이벤트 안내 이미지 3장",
                expanded=True
            ):

                st.caption(
                    "특별 교역소 · 스탬프 랠리 보상 · 미션 안내"
                )

                for img in (
                    "azur_event_prizes_new.png",
                    "azur_event_rewards_new.png",
                    "azur_event_missions_new.png"
                ):
                    picture(img)

        elif group[0].get("image"):
            picture(group[0]["image"])

        for e in group:

            with st.container(border=True):

                st.caption(
                    e.get("kind", "이벤트")
                )

                st.markdown(
                    f"**{e['title']}**"
                )

                if e.get("description"):
                    st.write(e["description"])

                if e.get("source"):
                    st.link_button(
                        "🔗 공식 이벤트 안내",
                        e["source"],
                        use_container_width=True
                    )

    st.divider()

    st.caption(
        "지니뮤직 구매 특전: 12월 4~6일, "
        "타이틀별 특전 구매자 전원 제공 / "
        "지니뮤직 부스에서 10만 원 이상 구매 시 "
        "쇼핑백 추가 증정. "
        "수량 한정, 소진 시 조기 종료."
    )

    st.caption(
        "현장 재고 및 참여 조건은 "
        "공식 공지를 확인해 주세요."
    )


# ==========================================
# 3. 배치도 및 공식 X
# ==========================================

with t3:

    st.subheader("🗺️ AGF 2026 전체 배치도")

    picture("agf2026_floorplan.jpg")

    path = ROOT / "assets" / "agf2026_floorplan.jpg"

    if path.exists():
        st.download_button(
            "📥 배치도 다운로드",
            path.read_bytes(),
            "AGF2026_배치도.jpg",
            "image/jpeg"
        )

    st.divider()

    st.subheader("📢 AGF 2026 공식 계정")

    st.info(
        "AGF 2026 참가 업체, 행사 공지, "
        "배치도 및 이벤트 정보를 확인할 수 있습니다."
    )

    st.link_button(
        "𝕏 AGF KOREA 공식 X 바로가기",
        "https://x.com/AGF_Korea",
        use_container_width=True
    )

    st.divider()

    st.subheader("🔗 AGF 참가 업체 공식 X")

    for group_name, accounts in OFFICIAL_X_CATEGORIES.items():

        st.markdown(f"### {group_name}")

        cols = st.columns(2)

        for i, (name, url) in enumerate(accounts):

            with cols[i % 2]:

                with st.container(border=True):

                    st.markdown(f"**{name}**")

                    st.link_button(
                        "공식 X 방문 ↗",
                        url,
                        use_container_width=True
                    )
