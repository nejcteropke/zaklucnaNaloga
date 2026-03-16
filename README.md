# Načrt aplikacije za povezovanje glasbenikov

## 🎵 CHAT SYSTEM - Novo!

### Instagram-Style Private Messaging & Group Chats

Aplikacija ima zdaj polnopravno chat sistem z modernim dizajnom:

#### ✨ Lastnosti:
1. **Private Messages (Zasebna sporočila)**
   - Instagram-podobni vmesnik s sidebrom
   - Prikaz vseh dosedanjih pogovorov
   - Oznake za neprebranih sporočil
   - Iskalnica za hitro iskanje kontaktov
   - Status "Online/Offline" indikator

2. **Group Chats (Skupinski chati)**
   - Ustvari nove grupe z več uporabniki
   - Dodaj in odstrani člane iz grupe
   - Historija skupinskih sporočil
   - Seznam članov s pravicami (admin/member)
   - Možnost zapustiti grupo

3. **UI/UX**
   - Fluidne animacije (fade, slide, bounce efekti)
   - Responziven dizajn (desktop & mobile)
   - Filtriranje (Vsa, Neprebrana, Grupe)
   - Avtomatski scroll na zadnja sporočila
   - Mod Enter-je za hitro pošiljanje sporočil

#### 🔗 Navigacija:
- **Home** → **Private Messages** (`/private_messages`)
  - Izberi uporabnika ali grupo
  - **Private Chat** (`/private_chat/<username>`) - pogovor s prijateljem
  - **Groups** (`/groups`) - upravljanje grup
    - **Create Group** (`/create_group`) - nova grupa
    - **Group Chat** (`/group_chat/<id>`) - grupni pogovor
    - **Add Members** (`/add_members/<id>`) - dodaj člane

#### 📊 Podatkovne baze:
- `private_messages.json` - zasebna sporočila
- `groups.json` - podatki o grupah
- `group_messages.json` - sporočila v grupah

---

## 1. Registracija in uporabniški profili
- Glasbeniki se registrirajo z informacijami o instrumentu, žanru, izkušnjah, ciljih in lokaciji.
- Uporabniki lahko urejajo svoj profil z dodatnimi podatki (povezave do glasbenih projektov, kratek opis).

## 2. Iskanje in filtriranje glasbenikov
Uporabniki lahko iščejo druge glasbenike na podlagi:
- **Instrumenta** (kitara, bobni, bas, vokali, itd.)
- **Glasbenega žanra**
- **Lokacije** (z izračunom razdalje med uporabniki)
- **Ciljev** (nastopanje v živo, snemanje glasbe, itd.)
- **Stopnje izkušenj**
- **Koga iščejo** (npr. basista, bobnarja)

## 3. Povezovanje in komunikacija
- Uporabniki se lahko povežejo in pošljejo sporočila drugim glasbenikom.
- Lahko shranijo druge uporabnike v svoj seznam priljubljenih.

## 4. Reševanje problema
**Problem:** Glasbeniki težko najdejo druge glasbenike za sodelovanje, saj obstoječe platforme ne omogočajo natančnega iskanja glede na instrument, glasbeni žanr, cilje in lokacijo. Pogosto se zanašajo na osebne povezave ali nepregledne forume.

**Rešitev:** Aplikacija omogoča glasbenikom iskanje in povezovanje na podlagi instrumenta, žanra, ciljev, izkušenj in lokacije. Omogoča tudi neposredno komunikacijo med uporabniki za hitrejše dogovore in sodelovanja.

**Ciljna skupina:** Mlajši glasbeniki (npr. 15-30 let), ki igrajo instrumente, ustvarjajo glasbo ali nastopajo in iščejo druge s podobnimi cilji.

**Zakaj je drugačna:** Za razliko od splošnih platform, ta ponuja natančne iskalne filtre, enostavno povezovanje in komunikacijo ter osredotočenost na mlade glasbenike s skupnimi ambicijami.

---

# Analiza trga

## Obstoječe rešitve:
- Platforme kot **Facebook skupine**, **Meetup** in **BandMix** omogočajo iskanje glasbenikov, a nimajo specifičnih filtrov za iskanje po instrumentih, žanrih, ciljih in izkušnjah.

## Ciljni trg:
- Glasbeniki vseh stopenj (začetniki, srednji, profesionalci).
- Glasbeni žanri: rock, metal, jazz, pop, itd.
- Lokacija: Lokalno in globalno iskanje glasbenikov.

## Prednosti naše aplikacije:
- Natančni iskalni filtri za instrumente, žanre, cilje in lokacije.
- Enostavna komunikacija znotraj platforme.

## Velikost trga:
- V Sloveniji je približno **20% mladih (15-30 let) aktivnih glasbenikov** – to pomeni okoli **80.000 oseb**.
- Po anketah in raziskavah glasbenih forumov se približno **50% glasbenikov aktivno povezuje** z drugimi (**40.000 oseb**).
- Med temi bi vsaj **60% (24.000)** uporabljalo platformo za iskanje bendov in glasbenih sodelavcev.

## Ključni konkurenti in njihove prednosti/slabosti:

1. **BandMix**
   - **Prednosti:** Globalna baza glasbenikov, filtriranje po instrumentih in žanrih.
   - **Slabosti:** Omejen dostop brez plačila, slabša lokalna povezljivost.

2. **Facebook skupine (npr. “Glasbeniki Slovenije”)**
   - **Prednosti:** Veliko uporabnikov, brezplačno.
   - **Slabosti:** Slabo strukturirano iskanje, manj natančno filtriranje.

3. **Meetup**
   - **Prednosti:** Organizacija dogodkov za glasbenike, možnost mreženja.
   - **Slabosti:** Ni osredotočen na glasbenike, pomanjkanje specifičnih funkcij.

4. **Vampr**
   - **Prednosti:** Osredotočen na povezovanje glasbenikov, UI podobna Tinderju.
   - **Slabosti:** Osredotočen bolj na globalno mreženje kot na lokalne bende.

5. **JamKazam**
   - **Prednosti:** Omogoča online igranje v živo s kakovostnim zvokom.
   - **Slabosti:** Ne vključuje iskanja bendov, bolj osredotočen na jam sessione.

---

# Viri prihodkov:
1. **Osnovna aplikacija je brezplačna**
2. **Premium verzija (3€/mesec)**: dostop do vseh iskalnih filtrov in podrobnejših rezultatov.
