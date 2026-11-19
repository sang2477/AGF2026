import json
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='AGF 2026 개인 굿즈 보관함', page_icon='🎁', layout='wide')
st.markdown('''<style>.block-container{max-width:1050px;padding:1rem .8rem} @media(max-width:650px){.block-container{padding-top:.6rem}} </style>''', unsafe_allow_html=True)

def load():
    return json.loads((ROOT/'catalog.json').read_text(encoding='utf-8')),json.loads((ROOT/'events.json').read_text(encoding='utf-8'))
products,events=load()
if 'cart' not in st.session_state: st.session_state.cart={}

def picture(name):
    p=ROOT/'assets'/name
    if name and p.is_file():st.image(str(p),use_container_width=True)

st.title('🎁 AGF 2026 굿즈·이벤트 카탈로그')
st.caption('모바일 지원 · 장바구니는 현재 접속 중에만 유지되며 새 접속 시 초기화됩니다.')
t1,t2,t3,t4=st.tabs(['🛍️ 굿즈 카테고리','🧾 장바구니','🎁 무료·이벤트 카테고리','🗺️ 배치도'])
with t1:
    companies=sorted({p['company'] for p in products})
    categories=sorted({p.get('category') or '기타' for p in products})
    a,b=st.columns(2)
    company=a.selectbox('업체',['전체']+companies)
    category=b.selectbox('카테고리',['전체']+categories)
    subcategories=sorted({p.get('subcategory') for p in products if p.get('subcategory') and (company=='전체' or p['company']==company)})
    subcategory=st.selectbox('내부 분류',['전체']+subcategories) if subcategories else '전체'
    query=st.text_input('상품 검색')
    selected=[p for p in products if (company=='전체' or p['company']==company) and (category=='전체' or p.get('category')==category) and (subcategory=='전체' or p.get('subcategory')==subcategory) and query.lower() in p['name'].lower()]
    st.caption(f'{len(selected)}개 상품')
    for p in selected:
        with st.container(border=True):
            left,right=st.columns([1,2])
            with left:picture(p.get('image_path',''))
            with right:
                st.markdown(f"**{p['name']}**")
                st.caption(f"{p['company']} · {p.get('subcategory')+' · ' if p.get('subcategory') else ''}{p.get('category') or '기타'}")
                st.write('**가격 미정**' if p.get('price_tbd') else f"**{p['price']:,}원**")
                if p.get('spec'):st.caption(p['spec'])
                if p.get('description'):st.write(p['description'])
                if p['company'] != '아주르 프로밀리아' and p.get('detail_images'):
                    with st.expander('📷 상세 사진 보기'):
                        for detail in p['detail_images']:
                            picture(detail)
                if p.get('source'):st.link_button('공식 공지',p['source'])
                pid=str(p['id'])
                limit=99 if p.get('price_tbd') else int(p.get('limit_qty') or 99)
                qty=st.number_input('장바구니 수량',min_value=0,max_value=max(1,limit),value=min(limit,int(st.session_state.cart.get(pid,0))),key=f'qty_{pid}')
                if st.button('🛒 장바구니 넣기',key=f'save_{pid}'):
                    st.session_state.cart[pid]=qty
                    st.toast('장바구니에 반영했어!')
with t2:
    cart=st.session_state.cart
    selected=[p for p in products if cart.get(str(p['id']),0)>0]
    total=sum(p['price']*cart[str(p['id'])] for p in selected if not p.get('price_tbd'))
    a,b,c=st.columns(3)
    a.metric('상품 종류',len(selected));b.metric('총 수량',sum(cart[str(p['id'])] for p in selected));c.metric('확정 금액',f'{total:,}원')
    if any(p.get('price_tbd') for p in selected):st.warning('가격 미정 상품은 합계에서 제외했어.')
    rows=[{'업체':p['company'],'상품':p['name'],'수량':cart[str(p['id'])],'단가':'미정' if p.get('price_tbd') else p['price'],'소계':'미정' if p.get('price_tbd') else p['price']*cart[str(p['id'])]} for p in selected]
    if rows:
        st.dataframe(rows,hide_index=True,use_container_width=True)
    else:st.info('아직 선택한 굿즈가 없어.')
    genie_sum=sum(p['price']*cart[str(p['id'])] for p in selected if p.get('subcategory')=='지니뮤직 콜라보')
    if genie_sum>0:st.info('지니뮤직 콜라보 구매 특전: 구매자 전원 타이틀별 특전 제공 (현장 수량 한정)')
    if genie_sum>=100000:st.success('지니뮤직 부스 구매금액 10만 원 이상: 쇼핑백 추가 증정 대상 (소진 시 종료)')
    if any(p['company']=='아스트라에 오라티오' for p in selected):st.caption('아스트라에 오라티오 굿즈 구매 특전: 타포린 백 (현장 조건 확인)')
    if any(p['company']=='아스트라에 오라티오' and p['name']=='티저 아트북' for p in selected):st.caption('티저 아트북 구매 특전: 클리어 파일 백 (현장 조건 확인)')
with t3:
    st.subheader('🎁 무료·이벤트 카테고리')
    st.caption('무료 배포 · 스탬프 랠리 · 경품 수령 · 구매 특전을 한눈에 볼 수 있는 안내판이야. 현장 참여 조건은 공식 공지를 확인해 줘.')
    event_companies=sorted({e['company'] for e in events})
    event_kinds=['무료 배포','스탬프 랠리','경품 수령','구매 특전']
    a,b=st.columns(2)
    event_company=a.selectbox('게임 / 업체',['전체']+event_companies,key='event_company')
    event_kind=b.selectbox('이벤트 종류',['전체']+[k for k in event_kinds if any(e.get('kind')==k for e in events)],key='event_kind')
    event_query=st.text_input('이벤트 검색',key='event_search',placeholder='쇼핑백, 스탬프, 핫팩...')
    matching=[e for e in events if (event_company=='전체' or e['company']==event_company)
              and (event_kind=='전체' or e.get('kind')==event_kind)
              and event_query.lower() in e['title'].lower()]
    st.caption(f'표시 중 {len(matching)}개 이벤트')
    for company in sorted({e['company'] for e in matching}):
        st.markdown(f'#### {company}')
        group=[e for e in matching if e['company']==company]
        if company=='아주르 프로밀리아':
            with st.expander('🖼️ 아주르 이벤트 안내 이미지 3장',expanded=True):
                st.caption('특별 교역소 · 스탬프 랠리 보상 · 미션 안내')
                for img in ('azur_event_prizes_new.png','azur_event_rewards_new.png','azur_event_missions_new.png'):
                    picture(img)
        elif group[0].get('image'):
            picture(group[0]['image'])
        for e in group:
            with st.container(border=True):
                st.caption(e.get('kind','이벤트'))
                st.markdown(f"**{e['title']}**")
                if e.get('source'):
                    st.markdown(f"[🔗 공식 이벤트 안내]({e['source']})")
    if not matching:st.info('선택한 조건에 맞는 이벤트가 없어.')
    st.caption('지니뮤직 구매 특전: 12월 4~6일, 타이틀별 특전 구매자 전원 제공 / 지니뮤직 부스에서 10만 원 이상 구매 시 쇼핑백 추가 증정. 수량 한정, 소진 시 조기 종료.')
    st.caption('현장 재고 및 참여 조건은 공식 공지를 확인해 줘.')
with t4:
    st.subheader('AGF 2026 전체 배치도')
    picture('agf2026_floorplan.jpg')
    path=ROOT/'assets'/'agf2026_floorplan.jpg'
    if path.exists():st.download_button('배치도 다운로드',path.read_bytes(),'AGF2026_배치도.jpg','image/jpeg')

    st.divider()
    st.subheader('🔗 AGF 참가 업체 공식 X')
    st.caption('게임 및 피규어·굿즈 샵으로 분류한 공식 계정 모음입니다. 향후 업체 추가 시 OFFICIAL_X_CATEGORIES에 등록하면 됩니다.')
    OFFICIAL_X_CATEGORIES = {
        '🎮 게임': [
            ('아스트라에 오라티오', 'https://x.com/Asora_KR'),
            ('아주르 프로밀리아', 'https://x.com/AzurPromiliaKR'),
            ('승리의 여신: 니케', 'https://x.com/NIKKE_kr'),
            ('트릭컬 리바이브', 'https://x.com/Trickcal_Re'),
            ('홀로라이브 드림스', 'https://x.com/holo_dreams_en'),
            ('니벨아레나', 'https://x.com/NivelArena'),
            ('요스타 (한국 굿즈 스토어)', 'https://x.com/YostarStoreKR'),
        ],
        '🛍️ 피규어·굿즈 샵': [
            ('amiami', 'https://x.com/amiami_figure'),
            ('애니플러스', 'https://x.com/ANIPLUS_SHOP'),
            ('애니메이트', 'https://x.com/animateonlineKR'),
            ('한림사', 'https://x.com/hanlimsa'),
            ('GNFTOYZ', 'https://x.com/GNFTOYZ'),
            ('지니뮤직', 'https://x.com/genie_kt'),
        ],
    }
    for group, accounts in OFFICIAL_X_CATEGORIES.items():
        st.markdown(f'### {group}')
        cols = st.columns(2)
        for i, (name, url) in enumerate(accounts):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f'**{name}**')
                    st.link_button('공식 X 방문 ↗', url, use_container_width=True)
