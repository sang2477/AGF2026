# AGF 2026 굿즈·경품 보관함

**V4.6 최초 GitHub 업로드 통합본** — 로그인 및 개인정보 입력 없는 Streamlit 웹사이트

## 기능
- **굿즈 카테고리**: 굿즈 23개, 사진, 업체별/상품 종류별/내부 분류(니케 → 지니뮤직 콜라보) 검색
- **무료·이벤트 카테고리**: 무료 배포, 스탬프 랠리, 경품 수령, 구매 특전별 필터와 완료 체크
- 개인 모의 장바구니, 구매 특전 안내
- 무료 경품 및 이벤트 체크 12개
- AGF 부스 배치도
- JSON 백업·불러오기

## GitHub에 최초 업로드
1. 이 ZIP을 **압축 해제**합니다.
2. GitHub에서 `AGF2026` 저장소를 만듭니다.
3. **Upload files**를 선택하고 압축 해제한 폴더 **안의 모든 파일과 `assets`, `.streamlit` 폴더**를 올립니다.
4. 최상위에 `app.py`, `catalog.json`, `events.json`, `requirements.txt`가 있는지 확인하고 Commit합니다.
5. Streamlit Community Cloud (https://share.streamlit.io)에서 저장소의 `main` 브랜치와 `app.py`를 선택해 Deploy합니다.

## 로컬 실행
```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

## 업데이트
- 굿즈: `catalog.json` 및 `assets/`
- 경품·이벤트: `events.json` 및 `assets/`
- 프로그램 기능: `app.py`
- 변경 파일만 기존 GitHub 저장소에 업로드해 Commit하면 같은 사이트에 반영됩니다.

## 데이터 및 공개 범위
- 로그인과 개인정보 입력 기능이 없습니다.
- 이 앱의 장바구니·체크 데이터는 **접속 세션에만 임시 저장**됩니다. 장기간 보관하려면 앱의 JSON 백업 기능을 사용하세요.
- 공개 GitHub 저장소와 공개 Streamlit 주소는 **다른 사람도 접근할 수 있습니다**. 주소만 안다고 차단되는 개인 전용 사이트는 아닙니다.
- 개인 정보나 비밀키, SQLite DB를 저장소에 업로드하지 마세요.

## V4.6 추가 사항
- 니케 → 지니뮤직 콜라보 CD 플레이어와 ARK/VIVE 음반에 상세 이미지 각 1장 추가
- 상품 카드에서 `상세 사진 보기` 펼침 및 구성 설명 표시
- 기존 23개 상품·12개 이벤트 및 기타 기능 유지
