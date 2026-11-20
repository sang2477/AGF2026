import json
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='AGF 2026 업체별 카탈로그', page_icon='🎁', layout='wide')
st.markdown('<style>.block-container{max-width:1050px;padding:1rem .8rem}@media(max-width:650px){.block-container{padding-top:.6rem}}</style>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    catalogs = json.loads((ROOT / 'company_catalogs.json').read_text(encoding='utf-8'))
    products = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
    events = json.loads((ROOT / 'events.json').read_text(encoding='utf-8'))
    return catalogs, products, events

catalogs, products, events = load_data()

def show_images(names):
    count = 0
    for name in dict.fromkeys(names):
        path = ROOT / 'assets' / name
        if path.is_file() and path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
            st.image(str(path), use_container_width=True)
            count += 1
    return count

st.title('🎁 AGF 2026 업체별 카탈로그')
st.caption('업체별 전체 카탈로그 · 이벤트·무료 경품 · AGF 배치도')
page = st.radio('메뉴', ['🏬 업체별 카탈로그', '🗺️ AGF 배치도'], horizontal=True, label_visibility='collapsed')

if page == '🏬 업체별 카탈로그':
    category = st.radio('카테고리', ['🎮 게임', '🎨 피규어·애니'], horizontal=True)
    names = [n for n, v in catalogs.items() if v.get('group', '🎨 피규어·애니') == category]
    name = st.selectbox('🏷️ 업체 선택', names, index=None, placeholder='확인할 업체를 선택하세요', key='company_' + category)
    if not name:
        st.info('업체를 선택하면 판매 상품과 이벤트·무료 경품의 전체 안내 이미지를 확인할 수 있어요.')
    else:
        entry = catalogs[name]
        st.subheader(name)
        if entry.get('x_url'):
            st.link_button('𝕏 ' + name + ' 공식 X 바로가기', entry['x_url'], use_container_width=True, type='primary')
        sales, free = st.tabs(['🛍️ 판매 상품', '🎁 이벤트·무료 경품'])
        for tab, key, title in ((sales, 'sales_images', '판매 상품'), (free, 'event_images', '이벤트·무료 경품')):
            with tab:
                st.markdown('#### ' + name + ' — ' + title)
                total = show_images(entry.get(key, []))
                for related in entry.get('related_catalogs', []):
                    images = related.get(key, [])
                    if not images:
                        continue
                    other = related.get('company', '')
                    st.divider()
                    st.markdown('#### ' + related.get('title', other))
                    if other in catalogs and catalogs[other].get('x_url'):
                        st.link_button('𝕏 ' + other + ' 공식 X', catalogs[other]['x_url'], use_container_width=True)
                    if related.get('note'):
                        st.caption(related['note'])
                    total += show_images(images)
                if total == 0:
                    st.info('등록된 ' + title + ' 전체 이미지가 없습니다. 추후 추가 예정입니다.')
                else:
                    st.caption(f'이미지 {total}장 · 원본 비율 유지')
                records = products if key == 'sales_images' else events
                urls = list(dict.fromkeys(r.get('source') for r in records if r.get('company') in (name, name.replace('승리의 여신: ', '')) and r.get('source')))
                if urls:
                    with st.expander('🔗 기존 공식 공지 원문'):
                        for i, url in enumerate(urls, 1):
                            st.link_button(f'공식 공지 {i}', url)
else:
    st.subheader('🗺️ AGF 2026 전체 배치도')
    path = ROOT / 'assets' / 'agf2026_floorplan.jpg'
    if path.is_file():
        st.image(str(path), use_container_width=True)
        st.download_button('📥 배치도 다운로드', path.read_bytes(), 'AGF2026_배치도.jpg', 'image/jpeg')
    else:
        st.info('배치도 이미지가 아직 없습니다.')
    st.divider()
    st.link_button('𝕏 AGF KOREA 공식 X 바로가기', 'https://x.com/AGF_Korea', use_container_width=True)
