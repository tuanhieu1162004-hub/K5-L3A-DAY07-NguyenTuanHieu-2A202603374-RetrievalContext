# Benchmark Think Python va baseline Day 7

Tai lieu nay ghi lai giai doan TF-IDF da chay that. Hien da co dense va hybrid,
xem [huong dan retrieval](RETRIEVAL_SETUP.md) va [bang so sanh dev](../report/retrieval_dev.md).
Model chat/agent duoc noi o [buoc Ollama](AGENT_SETUP_LOCAL.md); chua danh gia
chat luong agent tren toan dev hoac test. Cac lenh chay tu thu muc co README.md,
starter/, data/ va tests/. Script su dung thu vien chuan Python 3.11+.

## 1. Dau vao va tai tao

Nguon: Think Python 2nd edition, Allen B. Downey / Green Tea Press. Quyen su
dung theo manifest Day 6: CC BY-NC 3.0. Corpus gom 48 trang noi dung chuong
1-5; giu so trang PDF goc. Dung nguyen 271 chunk cua strategy C, embedding
all-MiniLM-L6-v2, revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41, 384 chieu.

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/prepare_day6.py --day6 "C:\Users\Admin\Downloads\K5-L3-Day06-DataIngestionEngineering-main"
.\.venv\Scripts\python.exe -X utf8 starter/build_benchmark.py
```

Du lieu corpus chuyen doi nam o starter/data/day6/ (bi Git ignore). File
provenance.json ghi nguon, phien ban va model. Day 6 chi duoc doc.

## 2. Chia benchmark va dong bang dau vao

data/day7_benchmark/questions_dev.json: 15 cau co dap an duoc giu tu dev Day 6,
them 2 cau thieu evidence. questions_test.json: 5 cau co dap an moi va 2 cau
thieu evidence moi. Khong tai su dung test Day 6 da co ket qua.

Bo sung cau hoi duoc dinh nghia trong data/day7_additions.json. protocol.json
ghi thoi diem, SHA256 cua corpus, nguon va cac file benchmark. Chay lai lenh
build chi xac minh neu dau vao/benchmark khong doi. Neu sua cau hoi/nhan, tao
phien ban moi bang --output <thu-muc-moi>, ghi ly do va chay lai dev truoc test.

Khong chon cau test dua tren ket qua retrieval. Chua chay test Day 7. Cac
nhan moi do Codex (AI) chuan bi, khong duoc ghi la nhan do nguoi hoc tu cham.
Can doi chieu nguon va nhan truoc khi nop; absence_audit.json luu vet quet
48 trang va cac doan lien quan, khong suy luan absence chi tu top-k.

Ket qua doc cac ung vien absence: gia sach o trang 37 va ky hieu $ o trang
27 khong phai phi PythonAnywhere; gioi han recursion o trang 67 khong phai
heap size hoac so cua so Turtle; limit o trang 63-64 la so statement/elif.
Trang 51-52 mo ta tao va dong cua so Turtle, khong neu gioi han dong thoi
hay CPU GHz. Day la nhan AI; review thu cong cua nguoi hoc van chua co.

## 3. Quy tac evidence va filter

Khong sua text chunk, thut le code, punctuation hay ID. Khi cham, chi chuan
hoa Unicode NFC va khoang trang. Nguon va trang phai dung. Evidence co
start_char/end_char con phai khop doan goc tai dung offsets.

gold_sets la danh sach cac nhom thay the (OR). Moi nhom la danh sach cac
fragment bat buoc (AND). q07 can hai fragment o trang PDF 33. Alternative
glossary cua q12 cung can hai fragment; alternative khac van hop le.
Bo tao benchmark tach quote goc theo offsets, xac minh khong bo qua tu nao
giua cac chunk va giu quote goc trong original_gold.

Hit@1 = du mot nhom evidence trong top-1; Evidence Hit@3 = du mot nhom trong
top-3; Context Evidence Rate = du mot nhom trong cac chunk thuc su duoc giu
o context. Cac chi so dung cung quy tac day du, ke ca cau nhieu fragment.
Chi 15 cau co dap an nam trong mau so. Hai cau thieu evidence co trace
retrieval, chua duoc cham abstention vi chua chay agent that.

Chi question va filter co san trong cau hoi duoc dua vao retriever. Gold va
expected_answer chi dung o evaluator. TF-IDF hoc IDF tren toan corpus chung;
filter chapter loc candidate truoc khi cat top-k, khong lay filter tu gold.
Dense va hybrid o buoc sau can dung cung corpus va cung filter.

## 4. Chay dev

Baseline:

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/evaluate_retrieval.py --chunks starter/data/day6/chunks.json --questions data/day7_benchmark/questions_dev.json --split dev --top-k 3 --budget 800 --output starter/results/dev-tfidf-k3-b800
```

Thu nghiem 1, tang context budget:

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/evaluate_retrieval.py --chunks starter/data/day6/chunks.json --questions data/day7_benchmark/questions_dev.json --split dev --top-k 3 --budget 2000 --output starter/results/dev-tfidf-k3-b2000
```

Thu nghiem 2, tang so candidate va budget:

```powershell
.\.venv\Scripts\python.exe -X utf8 starter/evaluate_retrieval.py --chunks starter/data/day6/chunks.json --questions data/day7_benchmark/questions_dev.json --split dev --top-k 8 --budget 4000 --output starter/results/dev-tfidf-k8-b4000
```

Budget tinh bang KY TU, gom header nguon, khong phai token. File ket qua
cung ten se bi ghi de khi chay lai. Moi thu muc co summary.json va traces.json.
Runner kiem tra checksum corpus va split cau hoi voi protocol truoc khi chay.

## 5. Ket qua va hai loi dev

| Cau hinh | Hit@1 | Evidence Hit@3 | Context Evidence Rate |
|---|---|---|---|
| TF-IDF k=3, budget=800 | 5/15 (33.3%) | 8/15 (53.3%) | 5/15 (33.3%) |
| TF-IDF k=3, budget=2000 | 5/15 (33.3%) | 8/15 (53.3%) | 8/15 (53.3%) |
| TF-IDF k=8, budget=4000 | 5/15 (33.3%) | 8/15 (53.3%) | 12/15 (80.0%) |

q05: evidence dinh nghia variable o rank 2, trang 36, chunk
2cde73c27461559f77e0ede7. Baseline lay duoc trong top-3 nhung context 800
ky tu chi giu rank 1, nen context khong du evidence. Gia thuyet: budget qua
nho loai bo evidence dung. Tang len 2000 giu du evidence; ranking khong doi.
q10 va q12 cung het loi mat evidence trong context o thu nghiem nay.

q07: can ca 30778f61bef932f3ed9263c7 (rank 1) va
2d6429c9b0799d98c9fc0906 (rank 6), trang 33. k=3 khong du evidence du tang
budget len 2000. Gia thuyet: tang candidate pool va budget giu du ca hai.
k=8/budget=4000 co du evidence trong context. Hit@3 van 0 cho q07, dung voi
cutoff chung. Vi thay hai tham so cung luc, chua tach rieng tac dong tung bien.

Khong chot cau hinh cuoi tu cac ket qua TF-IDF nay: chua co grounded
answer/citation/abstention cua agent that.
Ba dong tren la BA CAU HINH TF-IDF, khong phai ba phuong phap retrieval.
Dense tren pgvector Day 6 va hybrid da duoc so sanh rieng trong
[retrieval_dev.md](../report/retrieval_dev.md). Buoc con lai la ket noi model chat that.

elapsed_ms tung query va median_ms trong summary.json chi do retrieval +
pack context; khong gom checksum, nap file, tao index hay cham evidence.
index_seconds duoc bao rieng. Khong bao gom LLM. Phi dich vu retrieval TF-IDF
la 0 USD; context lon hon co the tang token/chi phi khi noi model sau nay.

## 6. Kiem tra code

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
```

Test kiem tra AND/OR evidence, source/page/offset, khong bo tu khi tach gold,
filter va mau so retrieval. Test mock khong thay benchmark agent that.
