# NanoMan Critics

1. Szia! Gratulálok a projekthez!
Tök jó látni, hogy saját eszközt építesz egy létező problémára. A "Low Resource" filozófia nagyon szimpatikus, a Postman tényleg zabálja a memóriát mostanában.
Átfutottam a kódot, és mivel kérted a visszajelzést, összeszedtem pár dolgot. Van benne sok minden, ami nagyon jól meg van oldva (például a UI és a logika szétválasztása, vagy hogy a kéréseket külön Thread-ben futtatod, így nem fagy le a GUI), de találtam pár olyan pontot, amit érdemes javítani, hogy tényleg stabil legyen:
A "Hiányzó láncszem": Offline mentés
A leírásban említetted az Offline-first működést és a mentett előzményeket. A kódodban viszont a self.history = [] csak a memóriában él. Ha bezárod az ablakot, minden elveszik.
Tipp: Érdemes lenne egy egyszerű sqlite3 adatbázist vagy egy history.json fájlt írni/olvasni indításkor és kilépéskor, hogy az adatok tényleg megmaradjanak.
A túl szigorú URL ellenőrzés
A logic.py-ban lévő regex nagyon szigorú. Bár biztonságosnak tűnik, kizárhat valid belső hálózati címeket.
Például: Egy céges intraneten a http://belsoserver/api valid lehet (ahol nincs .com vagy domain végződés), de a regexed megköveteli a pontot a domainben (+\.).
Tipp: A requests könyvtár elég jól kezeli a hibás URL-eket. Lehet, hogy elég lenne csak a sémát (http/https) ellenőrizni, a többit pedig rábízni a try-except blokkra a küldésnél.
Teljesítménycsapda a színezésnél
A UI.py-ban az apply_json_highlighting függvény soronként és regex-szel parse-olja a választ.
Veszély: Ha kapok egy 5MB-os JSON választ (ami API tesztelésnél előfordul), ez a függvény másodpercekre, vagy akár végleg lefagyaszthatja a UI-t, mert a Tkinter Text widget tag-elése lassú művelet.
Tipp: Érdemes limitálni, hogy mekkora méret felett kapcsolja ki a színezést, vagy csak az első X sort színezze.
Header kezelés apróság
A parse_headers függvény dictionary-t használ (headers = {}).
Ez felülírja a duplikált kulcsokat. Bár ritka, de a HTTP specifikáció engedi a duplikált headeröket (pl. Set-Cookie többször is szerepelhet). Bár Python requests dict-et vár, érdemes tudni erről a limitációról.
GET kérés és a Body
A UI-ban a _execute_request metódusban van egy ilyen sor:
if method == "GET": payload = None
Bár a szabvány szerint a GET-nek nem szokott body-ja lenni, technikailag lehetséges (pl. ElasticSearch queryk). Egy fejlesztői eszköznél jobb, ha nem "fogod a kezét" a usernek, hanem engeded neki elküldeni, ha nagyon akarja.
Összességében: Tök jó alap, a struktúra tiszta és olvasható! Ha a perzisztenciát (mentést) megcsinálod, tényleg hasznos kis tool lehet belőle. Hajrá! #ez egy nagyon hasznos kifejezetten epitö jellegü kritika volt,ezt meg kell rendesen köszönnöm.

2. https://www.postman.com/ - piacvezető, letölthető, van ingyenes része, ami bőven elég a legtöbb felhasználónak. #ez nem relevans szerintem.

3. Öröm látni hogy sokat dolgozol. Legközelebb érdemes annak az AI-nak feltenni a kérdést hogy létezik e valami használható megoldás a problémádra és csak kicsit csodálkozni ha az első válasz a curl lesz. #ez egy kellemetlen ember, feketeöves linux user

4. ebben igazad van, de vizuálisan sokszor kényelmesebb. A postman bloatware-é válása óta én is kerestem az utódját, ami grafikus felülettel rendelkezik

5. A Postman sok esetben kényelmesebb, mint egy (AI által javasolt) curl parancs. Kicsit olyan ez, mint a vim és egy GUI-s szövegszerkesztő viszonya: a vim zseniális, ha napi szinten használod, de vannak helyzetek, amikor egy azonnal induló, vizuális eszköz praktikusabb.
A NanoMan ezt a rést célozza meg. A Postman időközben eléggé „kinőtte magát”, így szerintem a NanoMan jó irányba indult el.

6. Én nem szerettem meg főleg a harminc tabon eldugott hetven beállítása miatt és a huszonhat kattintás miatt ami egy sima http kérés elküldéséhez kell, de én mondhatni Linuxon szocializálódtam és szerintem ezen nem veszünk össze. Legyen NanoMan, postman, curl, mindenki találja meg a saját kényelmét. #ez megint az a kellemetlen ember

7. Akkor kár az almát a körtével hasonlítani (Curl vs NanoMan vagy CLI vs GUI)

8. Bár nem én írtam a hasonlatot, de a gyors és mindig kéznél van az a vim és a curl 😉. De azért csak így tovább, akinek kabát kell, vegyen kabátot, akinek meg a papné, az papot. 😉 #ez megint a kellemetlen ember

9. "létezik e valami használható megoldás a problémádra"
Ha minden problémára létező megoldást elfogadunk, akkor tulajdonképp be is fejezhetjük a programozást. Ebben a nagy AI flow-ban a hívők szerint meg fog szűnni a programozók munkája. A fenti gondolatmenetet követve ez valóban így lenne.
De szerencsére mindig van valaki, akinek nem jó az épp "használható megoldás", és kitalál valami újat. 🙂 #nagyon hasznos

10. Ebben nem értünk egyet. Próbáltam finoman utalni arra hogy létezik a curl, ami egyszerű és pont erre való de azt is szerettem volna elérni, hogy a szerző maga nézzen utána. Írhattam volna Google második találat szavakkal is, akkor nem zavar meg senkit az AI.
Ettől függetlenül ahogy fentebb láttad támogatom a fejlődést és mindig lesznek új problémák viszont ezzel aranyosan nőni fog a megoldások száma is. Mérlegelni kell, ahogy eddig is. #megint a kellemetlen ember

11. Tetszik, h nem kell regisztrálni, felhőt túrni .... csak egyszerűen megy!

12. Király. Ez majd kölleni fog! 😁 Köcce! 👍🤜🤛

13. A POSTMAN erre teljesen jó, én azt szoktam használni. # postman mas kategoria.
