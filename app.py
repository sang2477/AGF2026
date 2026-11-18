import csv
import io
import json
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='AGF 2026 개인 굿즈 보관함', page_icon='🎁', layout='wide')
st.markdown('''<style>.block-container{max-width:1050px;padding:1rem .8rem} @media(max-width:650px){.block-container{padding-top:.6rem}} </style>''', unsafe_allow_html=True)

@st.cache_data
def load():
    return json.loads((ROOT/'catalog.json').read_text(encoding='utf-8')),json.loads((ROOT/'events.json').read_text(encoding='utf-8'))
products,events=load()
if 'cart' not in st.session_state: st.session_state.cart={}
if 'checks' not in st.session_state: st.session_state.checks={}

def picture(name):
    p=ROOT/'assets'/name
    if name and p.is_file():st.image(str(p),use_container_width=True)

st.title('🎁 AGF 2026 굿즈·경품 보관함')
st.caption('로그인 없음 · 개인정보 수집 없음 · 모바일 지원 · 구매 계획은 현재 접속 세션에만 유지')
with st.expander('💾 내 기록 백업 / 복원 (기기 이동용)'):
    st.info('서버에 개인 기록을 저장하지 않아. 새로 접속하거나 세션이 종료되면 기록이 사라질 수 있으니 JSON으로 백업해 줘.')
    backup={'cart':st.session_state.cart,'checks':st.session_state.checks}
    st.download_button('내 기록 JSON 저장',json.dumps(backup,ensure_ascii=False,indent=2).encode('utf-8'),'agf2026_backup.json','application/json')
    file=st.file_uploader('저장한 JSON 파일 불러오기',type=['json'])
    if file and st.button('기록 복원'):
        try:
            data=json.load(file)
            valid_products={str(p['id']) for p in products}
            valid_events={e['id'] for e in events}
            cart={str(k):int(v) for k,v in data.get('cart',{}).items() if str(k) in valid_products and isinstance(v,int) and 0<=v<=99}
            checks={str(k):bool(v) for k,v in data.get('checks',{}).items() if str(k) in valid_events and isinstance(v,bool)}
            st.session_state.cart=cart;st.session_state.checks=checks
            for k in list(st.session_state):
                if k.startswith('event_') and k not in ('event_company','event_kind','event_search'):
                    del st.session_state[k]
            st.success('복원 완료');st.rerun()
        except Exception as exc:st.error(f'복원할 수 없는 파일이야: {exc}')

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
                if p.get('detail_images'):
                    with st.expander('📷 상세 사진 보기'):
                        for detail in p['detail_images']:
                            picture(detail)
                if p.get('source'):st.link_button('공식 공지',p['source'])
                pid=str(p['id'])
                limit=99 if p.get('price_tbd') else int(p.get('limit_qty') or 99)
                qty=st.number_input('모의 구매 수량',min_value=0,max_value=max(1,limit),value=min(limit,int(st.session_state.cart.get(pid,0))),key=f'qty_{pid}')
                if st.button('수량 저장',key=f'save_{pid}'):
                    st.session_state.cart[pid]=qty
                    st.toast('장바구니에 저장했어!')
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
        csvbuf=io.StringIO();w=csv.DictWriter(csvbuf,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        st.download_button('장바구니 CSV 다운로드',csvbuf.getvalue().encode('utf-8-sig'),'agf2026_cart.csv','text/csv')
    else:st.info('아직 선택한 굿즈가 없어.')
    genie_sum=sum(p['price']*cart[str(p['id'])] for p in selected if p.get('subcategory')=='지니뮤직 콜라보')
    if genie_sum>0:st.info('지니뮤직 콜라보 구매 특전: 구매자 전원 타이틀별 특전 제공 (현장 수량 한정)')
    if genie_sum>=100000:st.success('지니뮤직 부스 구매금액 10만 원 이상: 쇼핑백 추가 증정 대상 (소진 시 종료)')
    if any(p['company']=='아스트라에 오라티오' for p in selected):st.caption('아스트라에 오라티오 굿즈 구매 특전: 타포린 백 (현장 조건 확인)')
    if any(p['company']=='아스트라에 오라티오' and p['name']=='티저 아트북' for p in selected):st.caption('티저 아트북 구매 특전: 클리어 파일 백 (현장 조건 확인)')
with t3:
    st.subheader('🎁 무료·이벤트 카테고리')
    st.caption('무료 배포 · 스탬프 랠리 · 경품 수령 · 구매 특전을 종류별로 확인하고 체크할 수 있어.')
    event_companies=sorted({e['company'] for e in events})
    event_kinds=['무료 배포','스탬프 랠리','경품 수령','구매 특전']
    a,b=st.columns(2)
    event_company=a.selectbox('게임 / 업체',['전체']+event_companies,key='event_company')
    event_kind=b.selectbox('이벤트 종류',['전체']+[k for k in event_kinds if any(e.get('kind')==k for e in events)],key='event_kind')
    event_query=st.text_input('이벤트 검색',key='event_search',placeholder='쇼핑백, 스탬프, 핫팩...')
    matching=[e for e in events if (event_company=='전체' or e['company']==event_company)
              and (event_kind=='전체' or e.get('kind')==event_kind)
              and event_query.lower() in e['title'].lower()]
    completed=sum(bool(st.session_state.checks.get(e['id'],False)) for e in matching)
    st.caption(f'표시 중 {len(matching)}개 · 완료 {completed}개')
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
                eid=e['id']
                # Widget key itself is the source of truth. Seed only when not present.
                widget_key=f'event_{eid}'
                if widget_key not in st.session_state:
                    st.session_state[widget_key]=bool(st.session_state.checks.get(eid,False))
                checked=st.checkbox(e['title'],key=widget_key)
                st.session_state.checks[eid]=checked
                if e.get('source'):st.link_button('공식 이벤트 안내',e['source'])
    if not matching:st.info('선택한 조건에 맞는 이벤트가 없어.')
    st.caption('지니뮤직 구매 특전: 12월 4~6일, 타이틀별 특전 구매자 전원 제공 / 지니뮤직 부스에서 10만 원 이상 구매 시 쇼핑백 추가 증정. 수량 한정, 소진 시 조기 종료.')
    st.caption('현장 재고 및 참여 조건은 공식 공지를 확인해 줘.')
with t4:
    st.subheader('AGF 2026 전체 배치도')
    picture('agf2026_floorplan.jpg')
    path=ROOT/'assets'/'agf2026_floorplan.jpg'
    if path.exists():st.download_button('배치도 다운로드',path.read_bytes(),'AGF2026_배치도.jpg','image/jpeg')
