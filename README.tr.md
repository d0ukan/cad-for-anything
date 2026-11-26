<p align="center">
  <img src="assets/banner.tr.svg" alt="CAD for Anything: mekanik parçaları her yapay zeka ve her CAD programıyla tasarlayın" width="100%">
</p>

<p align="center">
  <a href="README.md">English</a> · <b>Türkçe</b>
</p>

<p align="center">
  <a href="https://github.com/d0ukan/cad-for-anything/actions/workflows/ci.yml"><img src="https://github.com/d0ukan/cad-for-anything/actions/workflows/ci.yml/badge.svg" alt="ci"></a>
  <img src="https://img.shields.io/badge/s%C3%BCr%C3%BCm-v0.5.0-1d4f7a" alt="sürüm v0.5.0">
  <a href="LICENSE"><img src="https://img.shields.io/badge/lisans-MIT-green" alt="MIT lisansı"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-3776ab?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/ba%C4%9F%C4%B1ml%C4%B1l%C4%B1k-yok-brightgreen" alt="bağımlılık yok">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-555" alt="Windows, macOS, Linux">
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/de%C4%9Fi%C5%9Fiklikler-oku-lightgrey" alt="değişiklikler"></a>
</p>

Mekanik parça ve montaj tasarımı (3D baskı, CNC, sac metal) için küçük bir
şablon. **Herhangi bir yapay zeka** ve **herhangi bir CAD programı** ile
çalışır (FreeCAD, Fusion, Inventor, SolidWorks, CATIA, Onshape, CadQuery,
OpenSCAD …). **Windows, macOS ve Linux**'ta kullanılır.

Kural dosyaları İngilizcedir; yapay zeka sizinle Türkçe konuşabilir.

| 💬 Sor | 📐 Tasarla | 🔍 Kontrol | 📦 Teslim |
| :---: | :---: | :---: | :---: |
| Yapay zeka kısa soruları sırayla sorar, gereksinimleri yazar | Modeli siz (ya da MCP / kodla yapay zeka) çizer | İki reviewer fonksiyonu ve üretimi kontrol eder | Atölye için adlı, kontrollü ve kilitli dosyalar |

## 🚀 Hızlı başlangıç

1. **Use this template** ile kendi kopyanızı oluşturun.
2. Repo linkini herhangi bir yapay zeka sohbetine verin ve
   *"Bununla bir parça tasarlamak istiyorum"* deyin.
3. Yapay zeka [AGENTS.md](AGENTS.md) dosyasını okur, soruları sırayla sorar
   ve adım adım yol gösterir. Modeli siz CAD programında çizersiniz.

## ⚙️ Nasıl çalışır

- 🖨️ **İsteğe bağlı önce FDM prototip.** İlk soru: *önce FDM prototip basıp
  test edecek misiniz?* Evet ise parça baskıya uygun tasarlanır
  (`P01`, `P02` …). Baskı işe yarayınca proje gerçek malzeme ve yönteme
  geçer (`R01`).
- 👥 **Roller:** Manager (sorular, kayıtlar), Designer (model, çıktılar) ve
  iki bağımsız reviewer — **fonksiyon** (dayanım, geçmeler, girişim,
  hareket boşluğu) ve **DFM** (üretilebilir ve monte edilebilir mi).
  Her şey **tek oturumda** yürür; yapay zeka içinde alt ajan kullanabilir,
  ama kendi başına yeni sohbet açmaz. Bkz. [ROLES.md](ROLES.md).
- 🚦 **Üç kapı, hepsini siz onaylarsınız:** G0 gereksinimler → G1 tasarım →
  RELEASE üretim dosyaları.
- 📏 **Kimlikli kısa kurallar** [rules/](rules/README.md) altında: malzeme (MAT),
  tolerans (TOL), DFM, çizim (DWG), adlandırma (REV).
- 🌳 **Parça listesi / ürün ağacı:** `project/bom.csv`; `cadctl.py bom` kontrol
  eder ve ağacı çizer (bkz. [örnek](examples/MB001-wall-bracket/README.md)).
- 🔒 **Onaylanan dosyalar kilitli:** RELEASE anında dosya özetleri (hash)
  saklanır; sonradan değişiklik yakalanır ve yeni revizyon gerekir.

### 🗺️ İş akışı

```mermaid
flowchart TD
    A([Başla: repo linkini bir yapay zekaya ver]) --> B{Önce FDM prototip?}
    B -- evet --> P[Prototip aşaması<br/>P01, FDM'e uygun]
    B -- hayır --> R[Üretim aşaması<br/>R01, son yöntem]
    P --> Q
    R --> Q
    Q[Sorular: parça, kod, malzeme,<br/>birim, CAD programı] --> C{CAD'e MCP veya<br/>kodla erişim var mı?}
    C -- evet --> C1[Yapay zeka modeli çizer]
    C -- hayır --> C2[Yapay zeka adım adım<br/>CAD tarifi verir]
    C1 --> G0
    C2 --> G0
    G0{{G0: kullanıcı gereksinimleri onaylar}} --> D[Tasarım]
    D --> RV[İki bağımsız review<br/>fonksiyon + DFM]
    RV -- FAIL --> D
    RV -- PASS --> G1{{G1: kullanıcı tasarımı onaylar}}
    G1 --> E[STEP / STL / PDF / DXF çıkar<br/>+ dosya review]
    E --> REL{{RELEASE: kullanıcı dosyaları onaylar}}
    REL --> T{Prototip mi?}
    T -- hayır --> DONE([Üretime gönder])
    T -- evet --> PT{Bas ve test et: OK?}
    PT -- "hayır: bump P02" --> D
    PT -- "evet: promote R01" --> G0
    classDef gate fill:#ffcc4d,stroke:#b38600,color:#000
    classDef done fill:#5aa9e6,stroke:#1d4f7a,color:#fff
    class G0,G1,REL gate
    class A,DONE done
```

### 👥 Tek oturum, çok rol

Bütün proje **tek sohbette/oturumda** kalır. Sizinle Manager konuşur;
Designer ve reviewer işleri aynı oturumun içindeki alt ajanlara verilebilir
(`ROL-09`). Alt ajan yoksa yapay zeka rolleri sırayla kendisi oynar.

```mermaid
flowchart LR
    U((Siz)) <--> M[Manager<br/>sorular, kayıtlar,<br/>onay ister]
    subgraph S[Tek oturum]
        M
        M -- görev --> D[Designer<br/>model, çıktılar]
        M -- sadece dosyalar --> RF[Reviewer: fonksiyon<br/>dayanım, geçme,<br/>girişim, hareket]
        M -- sadece dosyalar --> RD[Reviewer: DFM<br/>üretilebilir, monte edilebilir]
        D -- sonuç --> M
        RF -- PASS / FAIL --> M
        RD -- PASS / FAIL --> M
    end
    M --> ST[(workflow-state.json<br/>cadctl.py ile)]
    classDef you fill:#ffcc4d,stroke:#b38600,color:#000
    class U you
```

### 💬 Bir oturum nasıl geçer

```mermaid
sequenceDiagram
    actor U as Siz
    participant M as Manager
    participant D as Designer
    participant R as Reviewer'lar
    U->>M: "Bununla bir parça tasarlamak istiyorum."
    M->>U: Önce FDM prototip? Parça? Kod? Malzeme? Birim? CAD programı?
    U->>M: Cevaplar
    M->>U: Gereksinimler hazır. G0 onayı?
    U->>M: Evet
    M->>D: Parçayı modelle
    D-->>M: Model + ekran görüntüsü / dosyalar
    M->>R: Fonksiyon ve DFM review (sadece dosyalar)
    R-->>M: PASS (ya da F-001 … ile FAIL)
    M->>U: Review'lar PASS. G1 onayı?
    U->>M: Evet
    D-->>M: STEP / STL / PDF / DXF
    M->>U: Dosyalar kontrol edildi. RELEASE onayı?
```

### 🔁 Revizyonlar: prototip → üretim

```mermaid
flowchart LR
    P1[P01<br/>FDM baskı] -- test başarısız: bump --> P2[P02<br/>FDM baskı]
    P2 -- test OK: promote --> R1[R01<br/>son malzeme]
    R1 -- release sonrası değişiklik: bump --> R2[R02]
    classDef proto fill:#7fc4f5,stroke:#1d4f7a,color:#000
    classDef prod fill:#2a6fa8,stroke:#0f2742,color:#fff
    class P1,P2 proto
    class R1,R2 prod
```

## 🛠️ Yardımcı araç

Bağımlılık yok, Python 3.10+. Windows, macOS ve Linux'ta test edilir.

```
python scripts/cadctl.py next      # şimdi ne yapılacak, kim yapacak, hangi komut
python scripts/cadctl.py status    # proje durumu
python scripts/cadctl.py check     # üretim dosyaları var ve doğru adlı mı?
python scripts/cadctl.py bom       # project/bom.csv'den ürün ağacı (--mermaid ile şema)
```

Diğer komutlar: `set`, `approve`, `review`, `block`, `unblock`, `bump`,
`promote`, `name`. Ayrıntı: `python scripts/cadctl.py -h`.

Örnek çıktı ([MB001 örneğinden](examples/MB001-wall-bracket/README.md);
aracın çıktısı İngilizcedir):

```
$ python scripts/cadctl.py next
Next (User): Approve design (G1) for R01
  python scripts/cadctl.py approve G1 --evidence "<where the user approved>"

$ python scripts/cadctl.py bom
MB001-00  Wall bracket kit  [assembly]
|-- 1 x MB001-01  Bracket  [make: S235 steel, 2 mm, zinc plated, sheet-metal]
|-- 2 x SCREW-6X50  Wood screw  [buy: 6 x 50 mm, pan head, zinc]
`-- 2 x PLUG-8  Wall plug  [buy: 8 mm nylon]
```

Aynı ağaç `bom --mermaid` ile:

```mermaid
flowchart TD
    n0[["MB001-00<br/>Wall bracket kit"]]
    n1["MB001-01<br/>Bracket"]
    n2(["SCREW-6X50<br/>Wood screw"])
    n3(["PLUG-8<br/>Wall plug"])
    n0 -- "1x" --> n1
    n0 -- "2x" --> n2
    n0 -- "2x" --> n3
```

## 🔌 CAD erişimi (isteğe bağlı)

CAD programınızı söyledikten sonra yapay zeka ona bir MCP sunucusu üzerinden
erişip erişemediğini kontrol eder. Erişemiyorsa programınız için bilinen MCP
sunucularını gösterir ve kurmak mı yoksa adım adım tarifle devam etmek mi
istediğinizi sorar.
Liste ve ayrıntılar: [AGENTS.md, bölüm 5](AGENTS.md#5-cad-access-check-after-question-6).

| CAD programı | Yapay zeka nasıl çalışır |
| :--- | :--- |
| Fusion · Inventor · SolidWorks · CATIA · Onshape · FreeCAD | 🔌 Bağlıysa MCP sunucusu, değilse 📝 adım adım tarif |
| CadQuery · OpenSCAD (kod) | 🐍 Yapay zeka `project/cad/` içine betik yazar ve çalıştırır (örnek: [`.py`](examples/MB001-wall-bracket/cad/mb001_bracket.py), [`.scad`](examples/MB001-wall-bracket/cad/mb001_bracket.scad)) |
| Diğerleri | 📝 Adım adım tarif; siz ekran görüntüsü veya dosya gönderirsiniz |

## 📁 Dosyalar

| Yol | Ne |
| :--- | :--- |
| `AGENTS.md` | Yapay zeka için talimat: ne okur, ne sorar |
| `ROLES.md` | Roller, kapılar, prototip → üretim akışı |
| `rules/` | Kural dosyaları |
| `project/` | Sizin projeniz: `requirements.md`, `workflow-state.json`, `bom.csv`, `cad/` (isteğe bağlı model betikleri), `release/` |
| `examples/MB001-wall-bracket/` | Doldurulmuş örnek |
| `scripts/cadctl.py` | Durum, sıradaki adım, kapı kontrolü |
| `assets/` | README görselleri |

## 🤝 Katkı

Bkz. [CONTRIBUTING.md](CONTRIBUTING.md). README değişince hem `README.md`
hem `README.tr.md` güncellenir.
