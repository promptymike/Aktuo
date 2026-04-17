# Batch 1 Self-Validation Report

Data: 2026-04-18
Model: claude-haiku-4-5-20251001
Koszt: $0.1142

## Podsumowanie statusów
- Clean: 0/10
- Flagged_for_review: 10/10
- Needs_major_revision: 0/10

## Statystyki problemów (według severity)
- High: 28
- Medium: 73
- Low: 21

## Top 3 najsłabsze drafty
- wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze — 15 issues — confidence 0.68 — status `flagged_for_review`
- wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece — 14 issues — confidence 0.62 — status `flagged_for_review`
- wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat — 14 issues — confidence 0.62 — status `flagged_for_review`

## Najczęstsze kategorie problemów
- missing_critical_info: 38
- hallucination_risk: 20
- legal_anchor_uncertainty: 18
- outdated_data_risk: 17
- step_contradiction: 15
- edge_case_coverage: 14

## Szczegóły per draft

### wf_107_nowe_oznaczenia_jpk_vat_bfk_vs_di_dla_faktur_wnt_importu_i_p
- Title: Oznaczenia BFK vs DI w JPK_VAT od lutego 2026 - faktury WNT, import usług, poza KSeF
- Cluster: 107  |  Topic: JPK
- Status: `flagged_for_review`
- Confidence: 0.42
- Assessment: Draft zawiera poważne problemy z weryfikowalnością podstawy prawnej (artykuły ustawy o VAT wydają się wymyślone, rozporządzenie nie jest precyzyjnie zidentyfikowane) oraz wewnętrzne sprzeczności dotyczące stosowania kodów BFK dla dokumentów sprzed lutego 2026. Stanowisko KIS cytowane bez pełnych referencji, a sam draft przyznaje rozbieżności interpretacyjne - wymaga znacznej weryfikacji przed publikacją.
- Issues:
  - [HIGH] legal_anchor_uncertainty: Artykuł 'art. 106gb ust. 4 pkt 1 i ust. 5' ustawy o VAT nie istnieje w polskim kodeksie VAT (art. 106 to maksimum). Numery artykułów wyglądają na wymyślone lub błędnie cytowane, co podważa wiarygodność całej podstawy prawnej.
  - [HIGH] legal_anchor_uncertainty: Rozporządzenie w sprawie JPK_V7 § 10 nie jest precyzyjnie zidentyfikowane - brakuje pełnej nazwy rozporządzenia, numeru i daty wydania. Nie wiadomo, czy odnosi się do rozporządzenia MF czy innego aktu.
  - [HIGH] outdated_data_risk: Draft zawiera datę 'od lutego 2026' jako przyszłą, ale metadata wskazuje 'last_verified_at': '2026-04-17', co sugeruje, że dokument jest pisany z perspektywy kwietnia 2026. Dla użytkownika w 2026 ta informacja może być już nieaktualna lub mylna.
  - [HIGH] hallucination_risk: Stanowisko MF z '18.03' (bez roku) dotyczące BFK dla WNT jest cytowane bez pełnej referencji. Brak możliwości weryfikacji, czy taki dokument rzeczywiście istnieje i jaka jest jego pełna treść.
  - [MEDIUM] step_contradiction: Step 2 mówi, że BFK stosuje się dla faktur 'wystawionych poza KSeF mimo obowiązku', ale step 6 sugeruje, że faktury z grudnia 2025/stycznia 2026 'nie wymagają nowych oznaczeń BFK/DI' - sprzeczność w stosowaniu BFK dla dokumentów sprzed lutego 2026.
  - [MEDIUM] missing_critical_info: Brakuje wyjaśnienia, jak oznaczać faktury korygujące (faktury VAT RR) w kontekście nowych kodów BFK/DI - czy dziedziczą oznaczenie faktury pierwotnej, czy otrzymują nowe?
  - [MEDIUM] missing_critical_info: Step 5 mówi, że BFK/DI 'nie zastępują' dotychczasowych oznaczeń, ale nie wyjaśnia, w jakim polu JPK_V7 umieszcza się BFK/DI - czy to osobna kolumna, czy zastępuje istniejące pole?
  - [MEDIUM] edge_case_coverage: Edge case 'Apteka wystawiająca paragon z NIP powyżej 450 zł' zawiera stwierdzenie 'fakturę do takiego paragonu z NIP nabywcy wysyłasz do KSeF' - ale nie jest jasne, czy to dotyczy wszystkich aptek czy tylko tych spełniających określone warunki (np. wielkość obrotu).
  - [MEDIUM] hallucination_risk: Tryb 'offline24' KSeF wspomniany w related_questions nie jest znany jako oficjalna nazwa trybu - może to być wymyślony termin lub błędna nomenklatura.
  - [LOW] missing_critical_info: Brakuje informacji, jak postępować z fakturami wystawionymi przez podatnika, który zmienia status (np. z małego podatnika na zwykłego) w trakcie okresu rozliczeniowego - czy oznaczenia się zmieniają retroaktywnie?
  - [LOW] outdated_data_risk: Limity i kwoty (np. 450 zł dla paragonów uproszczonych) mogą ulec zmianie do 2026 roku - draft nie zawiera zastrzeżenia o konieczności weryfikacji aktualnych limitów.
  - [LOW] step_contradiction: Step 7 rekomenduje 'zapytanie do KIS' w razie wątpliwości, ale wcześniejsze kroki (2-3) prezentują stanowisko jako pewne - sygnalizuje to, że draft sam nie jest pewny interpretacji BFK vs DI dla WNT.

### wf_10_potracenia_komornicze_niealimentacyjne_z_wynagrodzen_i_zlece
- Title: Potrącenia komornicze niealimentacyjne z wynagrodzeń, zasiłków i umów zlecenia
- Cluster: 10  |  Topic: kadry
- Status: `flagged_for_review`
- Confidence: 0.62
- Assessment: Draft zawiera poważne błędy w cytowaniu przepisów (art. 87¹ KP nie istnieje) i potencjalne nieścisłości w datach waloryzacji (825 zł na 2025 r. w dokumencie z 2026). Brakuje precyzji w kilku kluczowych procedurach (zbieg zajęć, potrącenia z drugiej wypłaty, status wynagrodzenia chorobowego) oraz konkretnych nazw formularzy. Wymaga weryfikacji prawnej przed publikacją.
- Issues:
  - [HIGH] legal_anchor_uncertainty: Art. 87¹ KP nie istnieje w Kodeksie pracy - przepisy dotyczące potrąceń to art. 87-89 KP. Brak prawidłowego odniesienia do artykułu regulującego kwotę wolną przy zajęciach niealimentacyjnych (art. 87 § 1 KP).
  - [HIGH] legal_anchor_uncertainty: Odwołanie do 'art. 833 § 2 i 2¹ KPC' wymaga weryfikacji - przepisy KPC dotyczące ochrony zasiłków i umów cywilnoprawnych mogą mieć inne numery paragrafów; brak pewności czy § 2¹ istnieje.
  - [HIGH] outdated_data_risk: Kwota wolna zasiłków określona na 825 zł (stan 2025) - dokument datowany 2026-04-17 powinien zawierać waloryzowaną kwotę na 2026 r., która mogła się zmienić w marcu 2026.
  - [MEDIUM] outdated_data_risk: Minimalne wynagrodzenie krajowe podane jako 'ok. 4666 zł brutto' w pytaniu przykładowym - ta kwota jest z 2025 r.; dla 2026 powinna być aktualna kwota obowiązująca od stycznia 2026.
  - [HIGH] missing_critical_info: Step 2 stwierdza że 'pracownik zazwyczaj nie ma potrącenia w ogóle' przy minimalnym wynagrodzeniu - brakuje precyzyjnego warunku/wariantu dla sytuacji gdy netto pracownika jest poniżej kwoty wolnej (czy potrącenie = 0 czy może być ujemne).
  - [MEDIUM] step_contradiction: Step 3 mówi że 'Świadczenia z ZFŚS co do zasady NIE podlegają egzekucji' ale Step 5 opisuje limity dla zasiłków ZUS - brakuje jasnego rozróżnienia między świadczeniami ZFŚS (które nie podlegają) a zasiłkami ZUS (które podlegają).
  - [MEDIUM] missing_critical_info: Step 4 wymaga od zleceniobiorcę 'pisma komornika potwierdzającego że zlecenie jest jedynym źródłem utrzymania' - brakuje informacji czy to pismo musi być złożone PRZED potrąceniem czy czy pracodawca może potrącać 100% do czasu dostarczenia takiego pisma.
  - [MEDIUM] missing_critical_info: Step 6 wspomina 'zgłoś zbieg do organu właściwego' ale nie precyzuje: do kogo dokładnie (sąd, komornik, ZUS), w jakim terminie i w jakiej formie.
  - [MEDIUM] hallucination_risk: Odwołanie do 'art. 773 KPC' w kontekście pierwszeństwa komornika nad ZUS - wymaga weryfikacji czy ten artykuł rzeczywiście reguluje tę kwestię; może to być błędny numer artykułu.
  - [MEDIUM] missing_critical_info: Step 7 mówi o 'formularzu z zajęcia' - brakuje nazwy konkretnego formularza (np. RPS-3, RPS-4) lub wskazania gdzie go znaleźć; 'formularz z zajęcia' jest zbyt ogólne.
  - [MEDIUM] edge_case_coverage: Edge case 'Dwie wypłaty w jednym miesiącu' stwierdza że 'druga wypłata może w całości pójść do komornika' - to wymaga weryfikacji czy rzeczywiście można potrącić 100% z drugiej wypłaty w tym samym miesiącu, czy kwota wolna liczy się od całego miesiąca.
  - [MEDIUM] missing_critical_info: Brakuje wyjaśnienia jak traktować wynagrodzenie chorobowe (pierwsze 33 dni płacone przez pracodawcę) - czy to wynagrodzenie za pracę (limity KP) czy zasiłek (limity ustawy emerytalnej); related_questions to podnoszą ale nie ma odpowiedzi w answer_steps.
  - [LOW] missing_critical_info: Brakuje informacji o proporcjonalnym wyliczeniu kwoty wolnej dla pracownika na część etatu - wspomina się to w related_questions ale nie ma procedury w answer_steps.
  - [LOW] hallucination_risk: Odwołanie do 'Comarch Optima/Symfonia' z instrukcją 'wprowadź zajęcie jako Komornicze inne' - wymaga weryfikacji czy te systemy rzeczywiście mają taką opcję i czy nazwa jest dokładna.

### wf_139_ksef_obieg_archiwizacja_i_weryfikacja_faktur_w_biurze
- Title: KSeF w biurze rachunkowym: obieg, archiwizacja i weryfikacja faktur kosztowych klientów
- Cluster: 139  |  Topic: KSeF
- Status: `flagged_for_review`
- Confidence: 0.68
- Assessment: Draft zawiera praktyczne kroki dla obiegu faktur KSeF w biurze rachunkowym, ale ma kilka poważnych luk: brak procedury dla biura bez dostępu do KSeF klienta, niepewne cytaty artykułów ustawy o VAT, oraz niejasności dotyczące obsługi błędów mapowania i duplikatów. Wymaga weryfikacji aktualności danych na 2026 i potwierdzenia nazw węzłów XML.
- Issues:
  - [MEDIUM] legal_anchor_uncertainty: Artykuł 106gb ust. 3-6 oraz 106na ust. 1, 3-4 są cytowane jako regulujące moment uznania faktury za otrzymaną i obsługę faktur poza KSeF, ale brak weryfikacji czy te konkretne ustępy rzeczywiście zawierają te regulacje w obecnym brzmieniu ustawy o VAT (stan na 2026).
  - [MEDIUM] legal_anchor_uncertainty: Artykuł 106nd ust. 2 pkt 1-6 i 11 - liczba punktów (11) wydaje się podejrzana dla jednego ustępu; wymaga weryfikacji czy struktura artykułu rzeczywiście zawiera 11 punktów w tym ustępie.
  - [HIGH] outdated_data_risk: Draft wspomina okres przechowywania faktur w KSeF przez MF na 10 lat, ale nie uwzględnia potencjalnych zmian w regulacjach przechowywania danych lub archiwizacji między 2024 a 2026; wymaga potwierdzenia aktualności tego okresu.
  - [MEDIUM] outdated_data_risk: Wymienione programy (Comarch Optima, Symfonia, Enova, wFirma) i ich funkcjonalności integracji z KSeF mogły ulec zmianom do 2026; szczególnie dotyczy to mapowania pól i dostępności OCR/paneli akceptacji.
  - [HIGH] missing_critical_info: Brak procedury obsługi sytuacji, gdy klient nie ma dostępu do KSeF (np. nie posiada certyfikatu, nie ma uprawnień) - draft zakłada, że klient zawsze może pobrać faktury, ale nie opisuje alternatywy dla biura bez dostępu do systemu klienta.
  - [MEDIUM] missing_critical_info: Krok 3 wspomina 'split payment' jako element weryfikacji, ale nie wyjaśnia jak biuro ma weryfikować czy faktura podlega split payment ani jakie są konsekwencje dla księgowania - brakuje procedury obsługi tego mechanizmu.
  - [MEDIUM] missing_critical_info: Draft nie opisuje procedury obsługi duplikatów faktur w KSeF (np. gdy sprzedawca wystawił dwie faktury z tym samym numerem) - brakuje kroku weryfikacji unikalności faktury przed księgowaniem.
  - [MEDIUM] step_contradiction: Krok 4 mówi że 'nie ma obowiązku drukowania' faktur, ale Krok 5 i common_mistakes powtarzają to jako błąd - brakuje jasnego wyjaśnienia czy backup XML jest obowiązkowy czy rekomendowany, i jakie są konsekwencje braku backupu przy kontroli.
  - [MEDIUM] hallucination_risk: Draft wspomina 'kod QR' dla faktur wystawionych w trybie offline24/awaryjnym - wymaga weryfikacji czy faktury offline rzeczywiście zawierają kod QR i czy jest to standard w KSeF.
  - [MEDIUM] hallucination_risk: Węzły XML 'P_6' (data sprzedaży) i 'Platnosc/TerminyPlatnosci' są cytowane jako standardowe, ale brak potwierdzenia czy dokładnie tak się nazywają w schemacie XML KSeF - mogą to być uproszczenia lub nieaktualne nazwy.
  - [LOW] hallucination_risk: Draft wspomina 'paragon z NIP' jako dokument spoza KSeF - wymaga weryfikacji czy paragony rzeczywiście mogą być wystawiane z NIP i czy trafiają do KSeF czy są zwolnione.
  - [MEDIUM] edge_case_coverage: Edge case dotyczący faktury z datą sprzedaży w innym miesiącu niż wystawienia jest realistyczny, ale draft nie wyjaśnia jak to wpływa na moment powstania obowiązku podatkowego w praktyce księgowania (czy księgować w miesiącu sprzedaży czy wystawienia).
  - [LOW] edge_case_coverage: Edge case 'klient nie chce wdrażać OCR/panelu' zakłada że zestawienie Excel jest realną alternatywą, ale nie opisuje jak biuro ma weryfikować czy lista numerów KSeF w Excelu jest kompletna i czy nie brakuje faktur.
  - [MEDIUM] missing_critical_info: Brak procedury obsługi błędów w mapowaniu danych przez sprzedawcę (Krok 6) - draft mówi 'poproś klienta o kontakt ze sprzedawcą', ale nie wyjaśnia co zrobić jeśli sprzedawca nie poprawi danych ani jak długo czekać przed księgowaniem na podstawie XML.
  - [MEDIUM] missing_critical_info: Draft nie opisuje procedury obsługi faktur korygujących w KSeF - czy są osobnym dokumentem, czy modyfikują oryginalną fakturę, i jak wpływa to na archiwizację i księgowanie.

### wf_21_sprawozdania_finansowe_do_krs_kas_schematy_i_skladanie
- Title: Sporządzanie i składanie sprawozdań finansowych do KRS/KAS - schematy, wersje, procedura
- Cluster: 21  |  Topic: rachunkowość
- Status: `flagged_for_review`
- Confidence: 0.72
- Assessment: Draft zawiera solidną strukturę proceduralną, ale ma kilka poważnych luk dotyczących aktualności schematów XSD na 2026 r., weryfikacji artykułów ustawy oraz brakuje precyzji w procedurach alternatywnych (np. oświadczenia zamiast podpisów, skan vs podpis elektroniczny). Wymaga manual legal review i aktualizacji referencji do systemów KRS.
- Issues:
  - [HIGH] outdated_data_risk: Draft zawiera konkretne schematy XSD (załącznik nr 1 v 1.3, nr 4, nr 5) i odniesienia do wersji schematów obowiązujących za 2025 r., ale nie ma mechanizmu aktualizacji dla 2026 r. MF regularnie zmienia wersje schematów, a procedura powinna wskazywać gdzie sprawdzić aktualną wersję, nie konkretne numery.
  - [MEDIUM] legal_anchor_uncertainty: Art. 45 ust. 1g UoR jest cytowany jako podstawa obowiązku elektronicznego, ale brakuje weryfikacji czy ten artykuł rzeczywiście istnieje w aktualnym brzmieniu ustawy o rachunkowości (mogły być zmiany legislacyjne do 2026 r.).
  - [MEDIUM] missing_critical_info: Krok 3 wymienia możliwość złożenia 'oświadczenia jednego członka + odmowę pozostałych' zamiast podpisów wszystkich członków zarządu, ale nie precyzuje formularza, struktury tego oświadczenia ani czy wymaga ono podpisu elektronicznego - to może prowadzić do błędów proceduralnych.
  - [MEDIUM] step_contradiction: Krok 1 stwierdza że spółka cywilna prowadząca KH 'nie składa do żadnego rejestru', ale edge case mówi o 'przekroczeniu limitu obrotów' - brakuje jasnego wyjaśnienia czy limit obrotów zmienia status składania czy tylko obowiązek sporządzenia.
  - [MEDIUM] hallucination_risk: Draft wspomina 'bezpłatny system RDF (Repozytorium Dokumentów Finansowych) w eKRS' - nazwa i akronim RDF powinny być zweryfikowane, gdyż mogą być zmienione lub nieaktualne w systemach KRS na 2026 r.
  - [MEDIUM] missing_critical_info: Krok 4 wymaga 'uchwały o stosowaniu uproszczeń (jeśli dotyczy - dołącza się do KRS wraz z SF, podpisana elektronicznie lub skan podpisanego dokumentu)' - brakuje wyjaśnienia czy skan papierowego dokumentu spełnia wymóg 'podpisanego elektronicznie' czy to dwa alternatywne warianty.
  - [LOW] edge_case_coverage: Edge case o 'spółce zawieszonej bez operacji' powołuje się na art. 3 ust. 6 UoR, ale nie wyjaśnia czy 'pojedyncza transakcja' oznacza każdą operację czy tylko operacje gospodarcze (np. czy opłacenie podatku VAT liczy się jako operacja).
  - [LOW] missing_critical_info: Krok 5 wymaga 'PESEL osoby uprawnionej ujawnionej w KRS' do złożenia RDF, ale nie wyjaśnia co zrobić gdy osoba uprawniona nie ma PESEL (np. obcokrajowiec) - to jest powiązane z related_question ale nie rozwiązane w procedurze.
  - [LOW] hallucination_risk: Krok 6 wspomina 'art. 79 UoR - odpowiedzialność karna' za brak SF, ale nie ma weryfikacji czy ten artykuł rzeczywiście dotyczy odpowiedzialności karnej (może być to art. 77 lub inny - draft sam wspomina art. 77 w edge case).
  - [LOW] outdated_data_risk: Draft zawiera termin '30 kwietnia roku następującego' dla KAS, ale nie uwzględnia potencjalnych zmian w terminie dla 2026 r. (mogą być zmiany w ustawie o podatku dochodowym lub regulacjach KAS).

### wf_49_srodki_trwale_jednorazowa_amortyzacja_vs_koszty_bezposrednie
- Title: Środki trwałe do 10 tys. zł i powyżej – wybór między kosztami bezpośrednimi, jednorazową amortyzacją a amortyzacją liniową
- Cluster: 49  |  Topic: KPiR
- Status: `flagged_for_review`
- Confidence: 0.62
- Assessment: Draft zawiera wiele konkretnych artykułów i procedur, ale ma istotne luki w weryfikacji aktualności limitów de minimis i progów dla 2026 r., oraz niepewności dotyczące rzeczywistego brzmienia art. 22k ust. 14 PIT (może to być przepis CIT). Wymaga manualnej weryfikacji wszystkich cytowanych artykułów i limitów finansowych przed publikacją.
- Issues:
  - [HIGH] legal_anchor_uncertainty: Art. 22k ust. 14 PIT dotyczący jednorazowej amortyzacji fabrycznie nowych ŚT do 100 000 zł jest cytowany dla osób fizycznych, ale limit 100 000 zł i grupy KŚT 3–6 i 8 mogą być regulacją dedykowaną CIT (spółkom). Wymaga weryfikacji czy art. 22k ust. 14 rzeczywiście istnieje w ustawie o PIT czy jest to przepis z CIT.
  - [MEDIUM] legal_anchor_uncertainty: Art. 22d ust. 1 PIT jest cytowany jako podstawa do nieujmowania w ewidencji ŚT składników ≤ 10 000 zł, ale brakuje wyraźnego odniesienia do art. 22c (definicja środka trwałego) – niepewne czy art. 22d ust. 1 rzeczywiście zawiera tę regulację czy jest to uproszczenie.
  - [HIGH] outdated_data_risk: Limit pomocy de minimis podany jako 300 tys. euro w 3 latach może być nieaktualny dla 2026 r. – przepisy mogły ulec zmianie, a dokument nie zawiera źródła ani daty ostatniej weryfikacji tego limitu.
  - [MEDIUM] outdated_data_risk: Próg dla małego podatnika podany jako 2 mln euro przychodu brutto może ulec zmianie w 2026 r.; dokument nie zawiera informacji o możliwych zmianach legislacyjnych ani warunkach przejściowych.
  - [MEDIUM] step_contradiction: Krok 2 (Opcja A) mówi o zaliczeniu bezpośrednio w koszty bez ewidencji dla ≤ 10 000 zł, ale Krok 6 wymaga zwiększenia wartości początkowej przy ulepszeniu > 10 000 zł – brakuje wyjaśnienia czy ulepszenie istniejącego ŚT poniżej 10 000 zł (które było w kosztach) zmienia jego status na ewidencjonowany.
  - [HIGH] missing_critical_info: Brakuje kroku dotyczącego VAT – czy wartość początkowa to cena netto czy brutto dla podatnika VAT; dokument wspomina 'netto dla czynnego podatnika VAT' w kroku 1, ale nie wyjaśnia jak to wpływa na wybór między opcjami A, B, C.
  - [MEDIUM] missing_critical_info: Brakuje informacji o terminie wprowadzenia ŚT do ewidencji – czy musi to być miesiąc zakupu czy można opóźnić do następnego miesiąca; krok 5 wspomina 'miesiąc następny' ale nie jest jasne czy to obowiązek czy opcja.
  - [MEDIUM] missing_critical_info: Krok 4 wspomina 'zaświadczenie z US o pomocy de minimis' ale nie wyjaśnia procedury uzyskania tego zaświadczenia ani czy jest ono wymagane przed zastosowaniem jednorazowej amortyzacji czy tylko do dokumentacji.
  - [MEDIUM] hallucination_risk: Krok 5 wspomina konkretne programy (Comarch Optima, WFirma, Symfonia) i kody KŚT (669 dla testera diagnostycznego, 808 dla mebli) – te kody mogą być zmienione w 2026 r. lub mogą być nieprecyzyjne; wymaga weryfikacji aktualności Wykazu KŚT.
  - [MEDIUM] hallucination_risk: Edge case o mieszkaniu jako lokalu firmy powołuje się na zmianę od 2023 r. (art. 22c pkt 2 PIT), ale dokument jest datowany na 2026 r. – brakuje informacji czy ta regulacja obowiązuje nadal czy została zmieniona.
  - [MEDIUM] edge_case_coverage: Edge case o spółce z o.o. kupującej kocioł węglowy powołuje się na art. 16k ust. 14 CIT, ale dokument jest dedykowany KPiR (osobom fizycznym) – ta informacja może być myląca dla użytkownika; brakuje wyjaśnienia czy przepisy CIT mają analogię w PIT.
  - [MEDIUM] missing_critical_info: Brakuje wyjaśnienia jak traktować ŚT zakupione przed 2026 r. a amortyzowane w 2026 r. – czy obowiązują przepisy z roku zakupu czy z roku amortyzacji; istotne dla przejścia na nowe przepisy.
  - [LOW] step_contradiction: Krok 7 mówi o wykazaniu w PIT-36/36L zał. B, ale dla KPiR (podatnika ryczałtowego lub skali) formularz może być inny – brakuje uściślenia dla jakich podatników ten krok ma zastosowanie.

### wf_62_vat_przy_wykupie_sprzedazy_i_darowiznie_samochodu_z_firmy
- Title: VAT przy wykupie, sprzedaży i darowiźnie samochodu osobowego z firmy (leasing, ST, cele prywatne)
- Cluster: 62  |  Topic: VAT
- Status: `flagged_for_review`
- Confidence: 0.72
- Assessment: Draft zawiera solidną strukturę procedury, ale ma kilka poważnych luk: brak weryfikacji aktualności stawek VAT i limitów na 2026 r., niejasności w rozróżnieniu między scenariuszami VAT/PIT, oraz brak kroku dotyczącego korekty VAT przy wycofaniu. Wymaga uzupełnienia o brakujące kroki i wyjaśnienia sprzeczności między krokami 4 i 6.
- Issues:
  - [MEDIUM] legal_anchor_uncertainty: Art. 86a ust. 1-3 ustawy o VAT reguluje odliczenie VAT od pojazdów, ale draft nie precyzuje, czy odnosi się do art. 86a w brzmieniu obowiązującym w 2026 r. – przepis ten był wielokrotnie nowelizowany i mogą obowiązywać inne limity/warunki niż w 2024 r.
  - [HIGH] outdated_data_risk: Draft zawiera konkretne stawki VAT (23%) i limity (150 000 zł w related_questions), ale nie wskazuje, że mogą ulec zmianie do 2026 r.; brak zastrzeżenia o konieczności weryfikacji aktualnych stawek i progów.
  - [MEDIUM] step_contradiction: Krok 4 stwierdza, że sprzedaż auta wycofanego na cele prywatne 'nie podlega VAT ani PIT z działalności', ale krok 6 mówi o PIT z działalności przy sprzedaży przed upływem 6 lat – brak jasnego wyjaśnienia, kiedy VAT/PIT się pojawia, a kiedy nie.
  - [HIGH] missing_critical_info: Draft nie wyjaśnia, czy samochód osobowy (kategoria M1) podlega innym regułom niż pojazdy użytkowe; art. 86a VAT ma specjalne warunki dla pojazdów osobowych, ale procedura nie zawiera kroku weryfikacji kategorii pojazdu.
  - [MEDIUM] missing_critical_info: Brak kroku dotyczącego wpływu wycofania samochodu z działalności na konieczność korekty wcześniej odliczonego VAT (art. 89 VAT) – draft wspomina to w related_questions, ale nie w głównym workflow.
  - [MEDIUM] hallucination_risk: Krok 3 wspomina 'Comarch Optima / wFirma / Symfonia' jako konkretne systemy księgowe – te nazwy mogą być nieaktualne w 2026 r. lub mogą być zastąpione innymi rozwiązaniami; to szczegół implementacyjny, nie przepis prawny.
  - [LOW] hallucination_risk: Krok 7 wspomina formularz 'SD-Z2' do zgłoszenia darowizny – należy zweryfikować, czy ta nazwa formularza jest aktualna dla 2026 r. (formularze mogą być zmieniane przez MF).
  - [MEDIUM] edge_case_coverage: Edge case dotyczący 'Spółki na CIT estońskim' jest niejasny – draft stwierdza, że 'sprzedaż sama w sobie nie generuje 50% CIT estońskiego', ale nie wyjaśnia, jakie są rzeczywiste skutki VAT/CIT w tym scenariuszu; może być wymyślony lub niekompletny.
  - [MEDIUM] missing_critical_info: Draft nie zawiera kroku dotyczącego różnicy między 'wycofaniem' samochodu z działalności (zmiana przeznaczenia) a 'sprzedażą' – te dwa zdarzenia mogą mieć różne skutki VAT/PIT, ale procedura traktuje je łącznie.
  - [LOW] step_contradiction: Krok 5 mówi o 'dokumencie wewnętrznym' dla darowizny, ale nie precyzuje, czy to wystarczy dla celów VAT – art. 7 ust. 2 VAT wymaga dokumentu potwierdzającego dostawę, ale draft nie wyjaśnia, jaki dokument jest wymagany.

### wf_63_leasing_samochodu_osobowego_limity_kup_i_odliczenie_vat
- Title: Leasing operacyjny samochodu osobowego – limity KUP i odliczenie VAT
- Cluster: 63  |  Topic: PIT
- Status: `flagged_for_review`
- Confidence: 0.62
- Assessment: Draft zawiera szczegółowe procedury, ale ma kilka poważnych luk: brakuje jasnego wyjaśnienia, czy limit dotyczy wartości pojazdu czy rat, brakuje konkretnych przykładów dla VAT-owców z 50% odliczeniem, a przejście limitów 150→100 tys. zł od 1.01.2026 wymaga weryfikacji źródła prawnego. Rekomendacja: wymagana weryfikacja artykułów PIT i VAT oraz potwierdzenie zmian limitów w obwieszczeniu MF przed publikacją.
- Issues:
  - [HIGH] legal_anchor_uncertainty: Art. 23 ust. 5c PIT cytowany jako podstawa dla 'zasady ochrony praw nabytych' i przejścia limitu 150→100 tys. zł od 1.01.2026 – wymaga weryfikacji, czy ten konkretny ustęp rzeczywiście zawiera przepis przejściowy dla umów zawartych do 31.12.2025, czy jest to interpretacja wymagająca potwierdzenia w obwieszczeniu MF.
  - [HIGH] outdated_data_risk: Draft zawiera limit 100 tys. zł 'od 1.01.2026' dla samochodów spalinowych emitujących >50g CO2/km, ale nie wskazuje źródła tej zmiany (ustawa, rozporządzenie, data wejścia w życie) – w 2026 mogą obowiązywać inne limity lub warunki emisyjne.
  - [MEDIUM] outdated_data_risk: Limit 225 tys. zł dla samochodów elektrycznych podany bez daty obowiązywania – czy dotyczy umów zawartych do 31.12.2025, czy obowiązuje również od 1.01.2026, czy ulega zmianie?
  - [MEDIUM] step_contradiction: Krok 1 mówi 'dla VAT-owca odliczającego 50% VAT – do limitu doliczasz 50% nieodliczonego VAT', ale krok 3 przykład pokazuje 'auto 200 000 zł netto, VAT 100% odliczalny' – brakuje jasnego przykładu dla VAT-owca z 50% odliczeniem, co może prowadzić do błędnego wyliczenia bazy proporcji.
  - [HIGH] missing_critical_info: Brakuje wyjaśnienia, czy limit 150/100 tys. zł dotyczy wartości pojazdu (jak sugeruje krok 2) czy sumy rat leasingowych w części kapitałowej – to fundamentalna różnica dla wyliczenia proporcji, szczególnie w leasingu długoterminowym.
  - [MEDIUM] missing_critical_info: Krok 4 wspomina 'współczynnik sprzedaży (art. 90 VAT)' dla podatników ze sprzedażą mieszaną, ale nie wyjaśnia, czy ten współczynnik zmniejsza również proporcję KUP czy tylko odliczenie VAT – brakuje konkretnego przykładu.
  - [MEDIUM] hallucination_risk: Krok 6 odnosi się do konkretnych modułów w programach 'Comarch Optima' (moduł Środki Trwałe → Pojazdy) i 'WFirma' (Pojazdy → Dodaj pojazd) – te ścieżki menu mogą być nieaktualne lub różnić się w zależności od wersji oprogramowania.
  - [MEDIUM] edge_case_coverage: Edge case 'Samochód z homologacją ciężarową' sugeruje, że pojazd może być traktowany jako osobowy dla PIT mimo VAT-26 – ale brakuje wskazania, jaki dokument/interpretacja stanowi podstawę tej klasyfikacji (czy to interpretacja indywidualna, czy utrwalona praktyka).
  - [MEDIUM] edge_case_coverage: Edge case 'Sprzedaż mieszana VAT' opisuje 'dwukrotne' liczenie proporcji (50% + wskaźnik sprzedaży), ale nie wyjaśnia, czy to mnożenie czy kolejne zastosowanie – przykład numeryczny byłby niezbędny.
  - [HIGH] missing_critical_info: Brakuje wyjaśnienia, czy 'wartość samochodu' w kroku 2 to wartość rynkowa, wartość z umowy leasingu, czy wartość przedmiotu leasingu (bez wyposażenia dodatkowego) – to wpływa na wyliczenie proporcji.
  - [MEDIUM] step_contradiction: Krok 5 mówi 'AC/GAP – proporcja do limitu 150 000 zł liczona od wartości samochodu z polisy', ale wcześniej (krok 2) limit może być 100 tys. zł od 1.01.2026 – czy AC/GAP zawsze liczą się do 150 tys. zł czy do obowiązującego limitu?
  - [MEDIUM] missing_critical_info: Krok 7 wspomina 'najem krótkoterminowy (≤6 mies.) – bez limitu wartości', ale nie wyjaśnia, czy to oznacza 100% KUP czy nadal 75% przy użytku mieszanym – brakuje jasności co do zakresu 'bez limitu'.
  - [MEDIUM] legal_anchor_uncertainty: Art. 86a ust. 1-3 VAT cytowany dla 'zasady 50% odliczenia VAT przy użytku mieszanym' – wymaga weryfikacji, czy te konkretne ustępy rzeczywiście zawierają regulację dla samochodów osobowych czy są to przepisy ogólne wymagające interpretacji.
  - [LOW] outdated_data_risk: Draft zawiera 'last_verified_at': '2026-04-17' (przyszła data) – jeśli to data generacji, może wskazywać na błąd w metadanych; jeśli to rzeczywista data weryfikacji, wymaga potwierdzenia aktualności przepisów na kwiecień 2026.

### wf_79_maly_zus_plus_ponowne_skorzystanie_po_przerwie_2026
- Title: Mały ZUS Plus – ponowne skorzystanie z ulgi po przerwie od 2026 roku
- Cluster: 79  |  Topic: ZUS
- Status: `flagged_for_review`
- Confidence: 0.62
- Assessment: Draft zawiera solidną strukturę procedury, ale ma kilka poważnych luk w weryfikacji aktualności danych (limit 120 tys. zł, kody ZUS) oraz brakuje wyjaśnień dla złożonych scenariuszy przejścia między kodami ubezpieczenia. Wymaga weryfikacji artykułów ustawy i waloryzacji limitów na 2026 rok przed publikacją.
- Issues:
  - [HIGH] legal_anchor_uncertainty: Art. 18c ustawy o systemie ubezpieczeń społecznych jest cytowany jako źródło regulacji 36/60 miesięcy, ale brak weryfikacji czy przepis rzeczywiście zawiera wszystkie wymienione warunki (limit 120 tys. zł, 60 dni prowadzenia, przesłanki negatywne dotyczące byłego pracodawcy). Artykuł może być zmieniony lub interpretowany inaczej w 2026 roku.
  - [MEDIUM] legal_anchor_uncertainty: Art. 36 ust. 14 jest przywoływany dla terminu 7 dni i 31 stycznia, ale draft nie precyzuje czy przepis dotyczy dokładnie obu terminów czy tylko jednego z nich, oraz czy regulacja nie uległa zmianie między 2025 a 2026 rokiem.
  - [HIGH] outdated_data_risk: Limit przychodu 120 000 zł dla 2026 roku nie jest zweryfikowany – draft zakłada że pozostanie na tym poziomie, ale limity ZUS-owe są waloryzowane corocznie i mogą ulec zmianie. Brak odniesienia do rozporządzenia waloryzacyjnego na 2026 rok.
  - [MEDIUM] step_contradiction: Krok 5 mówi o terminie 'do 31 stycznia 2026 r.' dla zgłoszenia, ale krok 6 wskazuje że jeśli działalność jest zawieszona w styczniu i wznowiona później, obowiązuje termin 7 dni. Brak jasnego wyjaśnienia czy termin 31 stycznia dotyczy tylko kontynuacji bez przerwy, czy też innych scenariuszy.
  - [HIGH] missing_critical_info: Draft nie wyjaśnia procedury dla scenariusza gdzie przedsiębiorca wykorzystał część z 36 miesięcy (np. 12 m-cy w 2025), przegapił termin 31 stycznia 2026, a następnie zawiesił i wznowił działalność – czy może wtedy wznowić ulgę na pozostałe miesiące czy licznik się zeruje?
  - [MEDIUM] missing_critical_info: Krok 3 odwołuje się do 'PUE ZUS (zakładka Ubezpieczony → Ulgi)' ale nie wyjaśnia czy ta funkcjonalność jest dostępna dla wszystkich typów podatników lub czy interfejs PUE może się zmienić w 2026 roku. Brak alternatywnego sposobu weryfikacji.
  - [MEDIUM] missing_critical_info: Krok 7 wymaga złożenia DRA II 'z wyliczeniem podstawy według dochodu z 2025 r.' ale draft nie wyjaśnia jak obliczyć podstawę jeśli dochód w 2025 roku był mieszany (część na preferencji 0570, część na dużym ZUS 0510).
  - [MEDIUM] hallucination_risk: Draft wspomina 'kod tytułu ubezpieczenia (0590)' dla Małego ZUS Plus – należy zweryfikować czy kod 0590 rzeczywiście obowiązuje w 2026 roku, ponieważ kody ZUS mogą ulec zmianie w wyniku zmian legislacyjnych.
  - [LOW] hallucination_risk: Edge case o 'decyzjach ZUS' potwierdzających że zawieszenie nie przerywa biegu 24 miesięcy preferencji – brak konkretnych numerów decyzji lub dat, co utrudnia weryfikację tej informacji.
  - [MEDIUM] edge_case_coverage: Draft nie pokrywa scenariusza gdzie przedsiębiorca zmienia formę opodatkowania (np. z ryczałtu na skalę podatkową) w trakcie roku – czy wpływa to na prawo do Małego ZUS Plus lub na sposób liczenia przychodu?
  - [MEDIUM] edge_case_coverage: Brak wyjaśnienia co się dzieje jeśli przedsiębiorca przekroczy limit 120 tys. zł przychodu w trakcie roku korzystania z Małego ZUS Plus – czy ulga pada natychmiast, czy od następnego miesiąca, czy trzeba zwrócić składki?
  - [LOW] missing_critical_info: Draft wspomina 'Comarch Optima / WFirma / Symfonia' jako systemy do ustawienia schematu składek, ale nie wyjaśnia czy wszystkie te systemy są aktualizowane dla zmian 2026 roku lub czy istnieją inne popularne systemy księgowe.

### wf_7_zaliczanie_umow_zlecenie_i_dg_do_stazu_pracy_od_2026
- Title: Zaliczanie okresów umów zlecenie i działalności gospodarczej do stażu pracy od 1 stycznia 2026 r.
- Cluster: 7  |  Topic: kadry
- Status: `flagged_for_review`
- Confidence: 0.62
- Assessment: Draft zawiera solidną strukturę proceduralną, ale ma kilka poważnych luk w zakotwiczeniu prawnym (art. 3021 KP, formularz US-7) i brakuje mu jasności co do inicjacji procesu zaliczania oraz zakresu retroaktywności zmian od 2026 r. Wymaga weryfikacji aktualnego stanu ustawodawstwa i precyzacji procedur administracyjnych.
- Issues:
  - [HIGH] legal_anchor_uncertainty: Draft powołuje się na 'znowelizowany art. 3021 Kodeksu pracy' w kroku 1, ale w legal_anchors podany jest tylko art. 22 KP. Brak potwierdzenia, czy art. 3021 rzeczywiście istnieje i czy nowelizacja weszła w życie 1 stycznia 2026 r. – wymaga weryfikacji aktualnego stanu prawnego.
  - [MEDIUM] legal_anchor_uncertainty: Krok 2 odwołuje się do formularza 'US-7' jako dokumentu rozstrzygającego z ZUS, ale nie ma tego formularza w legal_anchors. Należy potwierdzić, czy US-7 to rzeczywisty, aktualny formularz ZUS czy może chodzi o inny dokument (np. zaświadczenie o okresach ubezpieczenia).
  - [MEDIUM] outdated_data_risk: Draft zawiera konkretne nazwy systemów kadrowo-płacowych (Comarch Optima, Symfonia Kadry i Płace, Enova) w kroku 6, ale nie wiadomo, czy w 2026 r. będą to nadal dominujące rozwiązania lub czy ich interfejsy będą identyczne – może wymagać aktualizacji.
  - [HIGH] missing_critical_info: Brak wyjaśnienia, jak pracownik powinien złożyć wniosek o zaliczenie okresów do stażu pracy – czy to automatyczne przy zatrudnieniu, czy wymaga osobnego wniosku do pracodawcy/ZUS? Procedura inicjacji procesu nie jest jasna.
  - [MEDIUM] missing_critical_info: Krok 3 wspomina 'zaświadczenie/legitymację potwierdzającą status studenta', ale nie precyzuje, czy legitymacja studencka sprzed wielu lat będzie akceptowana, czy potrzebne jest zaświadczenie z uczelni – brak wytycznych czasowych.
  - [MEDIUM] step_contradiction: Krok 5 stwierdza, że 'przerwy w opłacaniu składek z tytułu zasiłku nie przerywają ciągłości ubezpieczenia', ale krok 4 mówi o 'eliminacji duplikatów' – niejasne, czy zasiłki w trakcie DG/zlecenia są traktowane jako odrębny okres czy jako kontynuacja tego samego okresu.
  - [MEDIUM] hallucination_risk: Krok 7 rozróżnia 'staż pracy ogólny' od 'stażu urlopowego' i wspomina zasadę 'korzystniejszego dla pracownika okresu, bez podwajania' – ta zasada nie jest wyjaśniona w legal_anchors i może być interpretowana na wiele sposobów.
  - [MEDIUM] edge_case_coverage: Edge case dotyczący 'brak dokumentów sprzed wielu lat' wspomina 'wniosek USP w ZUS', ale nie wyjaśnia, czy ZUS ma obowiązek wydać zaświadczenie dla okresów sprzed 2026 r., jeśli pracownik nie ma dokumentów – procedura jest niejasna.
  - [MEDIUM] missing_critical_info: Draft nie wyjaśnia, czy zaliczenie okresów do stażu pracy od 2026 r. ma charakter retroaktywny (czy można zaliczyć okresy sprzed 2026 r.) czy dotyczy tylko okresów od 1 stycznia 2026 r. – to ma znaczenie dla pracowników z historią zatrudnienia.
  - [LOW] hallucination_risk: Krok 6 wspomina 'adnotację zlecenie lub DG' w systemach kadrowych, ale nie ma potwierdzenia, czy wszystkie wymienione systemy obsługują takie adnotacje lub czy istnieje standardowy kod do tego celu.

### wf_merge_120_121_ksef_moment_podatkowy_data_wystawienia_korekty
- Title: KSeF: moment podatkowy, data wystawienia faktury i ujęcie korekt w VAT/JPK
- Cluster: merge_120_121  |  Topic: KSeF
- Status: `flagged_for_review`
- Confidence: 0.62
- Assessment: Draft zawiera poważne problemy z numeracją artykułów ustawy o VAT (art. 106na, 106gb – najprawdopodobniej wymyślone) oraz niejasności w definiowaniu daty wystawienia faktury w KSeF vs. momentu obowiązku podatkowego. Wymaga pilnej weryfikacji źródeł prawnych i wyjaśnienia kilku sprzeczności między krokami.
- Issues:
  - [HIGH] legal_anchor_uncertainty: Art. 106na ust. 1 i 3 ustawy o VAT – numery artykułów wyglądają na wymyślone; polska ustawa o VAT nie zawiera artykułów o numeracji 106na (struktura artykułów VAT to zwykle art. 1-141, bez prefiksów literowych). Należy zweryfikować prawidłowe numery artykułów definiujące datę wystawienia faktury w KSeF.
  - [HIGH] legal_anchor_uncertainty: Art. 106gb ust. 3 ustawy o VAT – artykuł o tej numeracji nie istnieje w polskiej ustawie o VAT. Prawidłowe przepisy dotyczące faktur korygujących w KSeF znajdują się w art. 106e-106g lub rozporządzeniach wykonawczych; należy zweryfikować dokładne źródło.
  - [HIGH] hallucination_risk: Step 1 twierdzi, że 'datą wystawienia faktury ustrukturyzowanej jest dzień przesłania faktury do KSeF' – to może być uproszczeniem lub błędem. Ustawa o VAT rozróżnia datę wystawienia (wpisana w fakturze) od daty otrzymania (w KSeF); draft nie wyjaśnia, czy zmienia się faktycznie data wystawienia, czy tylko moment obowiązku podatkowego.
  - [MEDIUM] step_contradiction: Step 2 mówi, że obowiązek VAT powstaje z chwilą dostawy (art. 19a ust. 1), ale step 3 mówi, że prawo do odliczenia powstaje 'w okresie, w którym powstał obowiązek podatkowy u sprzedawcy, ale nie wcześniej niż w okresie otrzymania faktury' – brakuje wyjaśnienia, czy dla nabywcy obowiązek powstaje w innym momencie niż dla sprzedawcy.
  - [MEDIUM] missing_critical_info: Step 3 nie wyjaśnia, co się dzieje, gdy faktura trafia do KSeF po upływie 3 miesięcy od dostawy – czy prawo do odliczenia wygasa, czy można je odliczyć w okresie otrzymania faktury? To kluczowe dla praktyki.
  - [MEDIUM] outdated_data_risk: Step 4 wspomina 'JPK_CIT od 2025/2026' – dokument ma datę weryfikacji 2026-04-17, ale nie jest jasne, czy wymogi JPK_CIT już obowiązują w 2026 czy są planowane. Należy potwierdzić status tego obowiązku.
  - [MEDIUM] missing_critical_info: Step 5 definiuje korekty z powodu 'błędu rachunkowego' vs 'przyczyn następczych', ale nie wyjaśnia, jak księgować korektę, gdy wystawca błędnie określił datę sprzedaży (np. wpisał luty zamiast stycznia) – czy to błąd rachunkowy czy następczy?
  - [MEDIUM] hallucination_risk: Step 6 wspomina konkretne programy (Comarch Optima, Symfonia, Enova, wFirma) i ich zachowanie przy imporcie z KSeF – bez źródła trudno zweryfikować, czy wszystkie te programy rzeczywiście zaciągają datę wystawienia zamiast daty sprzedaży z KSeF.
  - [MEDIUM] step_contradiction: Step 7 mówi 'Jeśli wystawca błędnie wystawił fakturę z datą marzec zamiast luty i skorygował ją do zera, do JPK trafia tylko prawidłowa faktura' – ale wcześniej (step 5) mówi się, że korekta z powodu błędu trafia do okresu faktury pierwotnej. Brakuje wyjaśnienia, czy błędna faktura w ogóle trafia do JPK czy jest całkowicie neutralizowana.
  - [LOW] edge_case_coverage: Edge case 'Faktura VAT metoda kasowa' wspomina 'wyciągi bankowe' – ale dla metody kasowej VAT decyduje data zapłaty, a dla KPiR data dostawy; draft nie wyjaśnia, jak rozliczyć te dwie różne daty w praktyce.
  - [LOW] edge_case_coverage: Edge case 'Import towarów spoza UE' wspomina 'dokument celny (SAD/PZC)' – PZC (Pismo Zatwierdzające Cło) nie jest standardowym dokumentem celnym; powinno być SAD (Pojedyncze Zgłoszenie Celne) lub inny dokument celny, ale PZC wymaga weryfikacji.
  - [LOW] missing_critical_info: Draft nie wyjaśnia, jak postępować, gdy faktura w KSeF ma datę wystawienia przyszłą (np. wystawiona 01.03, ale data w polu P_1 to 05.03) – czy data wystawienia to data przesłania czy data wpisana w fakturze?

## Rekomendacje dalszych kroków
- 10 draft(y) `flagged_for_review` — Paweł w weekendowej walidacji powinien przejść kategorie problemów i zdecydować: akceptacja z poprawką, regeneracja, czy merge z ekspertem.
- Duża liczba flag `high` — rozważ czy system prompt generatora (Opus) wymaga zacieśnienia instrukcji o aktualne limity 2026 i cytowanie dokładnych numerów artykułów.
- Następny krok: przejść top 3 najsłabsze drafty i porównać flagowane problemy z rzeczywistym stanem prawnym — jeśli potwierdzą się, regenerować z poprawioną materialą lub zwiększonym KB retrieval.
