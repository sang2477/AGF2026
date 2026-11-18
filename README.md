# AGF 2026 굿즈·경품 보관함 — V5.0 통합 수정본

## 변경 사항
- 아주르 프로밀리아 상품 12개의 대표 이미지를 `azur_item_01.png` ~ `azur_item_12.png`로 통일
- 기존 개별 이미지 `azur_product_*.png`와 전체 굿즈 포스터 `azur_goods_new.png`를 통합본에서 제거
- 아주르 상품의 상세 사진 영역 제거 (다른 업체 상세 사진은 유지)
- `catalog.json` 로딩 캐시 제거: 배포 시 구형 JSON이 표시되는 혼란 방지
- 기존 굿즈 23개, 이벤트, 장바구니, 배치도, 백업 기능 유지

## 기존 GitHub 저장소에 업데이트하기
1. 압축을 풀고 `app.py`, `catalog.json`, `events.json`, `requirements.txt`, `README.md`, `.streamlit/config.toml`을 기존 저장소에 반영하세요.
2. `assets/azur_item_01.png`부터 `azur_item_12.png`까지 12개를 업로드하세요. 다른 `assets` 이미지도 기존대로 유지해야 합니다.
3. GitHub 웹 업로드는 예전 파일을 자동으로 삭제하지 않습니다. `azur_product_*.png` 및 `azur_goods_new.png`는 앱에서 더 이상 사용하지 않으므로 남아 있어도 화면에는 표시되지 않습니다. 필요하면 나중에 삭제하세요.
4. GitHub에서 Commit한 뒤 Streamlit 앱의 재배포를 확인하고 브라우저 새로고침하세요.

## 로컬 실행
```bash
pip install -r requirements.txt
streamlit run app.py
```

**참고:** 이 통합본의 아주르 이미지들은 작은 원본을 보정·확대한 것이므로 세부 화질 복원에는 한계가 있습니다.
