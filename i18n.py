#!/usr/bin/env python3
# i18n.py — arayuz metinleri.
# Eksen adlari oyunun kendi yerelestirme paketlerinden alindi
# (Packages/fs-base/<locale>.locPak, MENU.OPTIONS.MULTIWINDOW.DELTA_*).
# Arayuz metinleri bu projeye ait; oyunun resmi cevirisi degil.

# eksen adlari: (lateral, vertical, roll) — oyunla ayni sira
AXES = {
    'en-US': ('Lateral rotation offset', 'Vertical rotation offset', 'Roll rotation offset'),
    'tr-TR': ('Yanal dönme dengeleyici', 'Dikey dönüş dengeleyici', 'Tono dönüş dengeleyici'),
    'de-DE': ('Lateraler Rotationsabstand', 'Vertikaler Rotationsabstand', 'Rollen-Rotationsabstand'),
    'es-ES': ('Desplazamiento de rotación lateral', 'Desplazamiento de rotación vertical',
              'Desplazamiento de rotación de balanceo'),
    'fr-FR': ('Décalage de la rotation latérale', 'Décalage de la rotation verticale',
              'Décalage de la rotation dans les tonneaux'),
    'it-IT': ('Offset rotazione laterale', 'Offset rotazione verticale', 'Offset rotazione rollio'),
    'pl-PL': ('Przesunięcie obrotu wzdłużnego', 'Przesunięcie obrotu pionowego',
              'Przesunięcie obrotu przechylenia'),
    'pt-BR': ('Deslocamento de rotação lateral', 'Deslocamento de rotação vertical',
              'Deslocamento de rotação do rolamento'),
    'ru-RU': ('Смещение: по горизонтали', 'Смещение: по вертикали', 'Смещение: крен'),
    'sv-SE': ('Sidledes rotationsförskjutning', 'Vertikal rotationsförskjutning',
              'Förskjutning av rollrotation'),
    'nb-NO': ('Siderotasjonsforskyvning', 'Loddrett rotasjonsforskyvning', 'Rullerotasjonsforskyvning'),
    'fi-FI': ('Sivuttaiskierron siirtymä', 'Pystysuuntaisen kierron siirtymä', 'Rullan kiertopoikkeama'),
    'ja-JP': ('横方向回転オフセット', '垂直回転オフセット', 'ロール回転オフセット'),
    'ko-KR': ('측면 회전 오프셋', '수직 회전 오프셋', '롤 회전 오프셋'),
    'zh-CN': ('横向角度偏移', '垂直角度偏移', '旋转角度偏移'),
}

# dil secicide gorunen adlar
NATIVE = {
    'en-US': 'English', 'tr-TR': 'Türkçe', 'de-DE': 'Deutsch', 'es-ES': 'Español',
    'fr-FR': 'Français', 'it-IT': 'Italiano', 'pl-PL': 'Polski', 'pt-BR': 'Português (BR)',
    'ru-RU': 'Русский', 'sv-SE': 'Svenska', 'nb-NO': 'Norsk', 'fi-FI': 'Suomi',
    'ja-JP': '日本語', 'ko-KR': '한국어', 'zh-CN': '中文（简体）',
}

UI = {
    'en-US': dict(
        hint='Sliders locked after Sim Update 6? Drag here — the value goes straight into the running sim.',
        connecting='connecting…', connected='connected', not_running='sim not running',
        bad_rva='values look wrong — press Detect', reconnect='Reconnect', detect='Detect',
        scanning='scanning…', detected='offset found', ambiguous='several candidates — pick one',
        admin='write failed — run as administrator', reverted='the sim reverted the value',
        language='Language', pick_title='Which one is the Multi Window offset?',
        pick_hint='Pick the row that matches the numbers shown in the sim.', ok='OK', cancel='Cancel'),
    'tr-TR': dict(
        hint='Sim Update 6 sonrası kaydırıcılar kilitli mi? Buradan sürükle — değer doğrudan çalışan simülasyona yazılır.',
        connecting='bağlanıyor…', connected='bağlı', not_running='simülasyon açık değil',
        bad_rva='değerler anlamsız — Bul düğmesine bas', reconnect='Yeniden Bağlan', detect='Bul',
        scanning='taranıyor…', detected='offset bulundu', ambiguous='birkaç aday — birini seç',
        admin='yazılamadı — yönetici olarak çalıştır', reverted='simülasyon değeri geri aldı',
        language='Dil', pick_title='Hangisi Multi Window offset?',
        pick_hint='Simülatörde görünen sayılarla eşleşen satırı seç.', ok='Tamam', cancel='Vazgeç'),
    'de-DE': dict(
        hint='Seit Sim Update 6 gesperrt? Hier ziehen — der Wert geht direkt in die laufende Simulation.',
        connecting='verbinde…', connected='verbunden', not_running='Simulator läuft nicht',
        bad_rva='Werte unplausibel — „Suchen" drücken', reconnect='Neu verbinden', detect='Suchen',
        scanning='suche…', detected='Offset gefunden', ambiguous='mehrere Kandidaten — einen wählen',
        admin='Schreiben fehlgeschlagen — als Administrator starten', reverted='Simulator hat den Wert zurückgesetzt',
        language='Sprache', pick_title='Welcher ist der Multi-Window-Offset?',
        pick_hint='Zeile wählen, die zu den Zahlen im Simulator passt.', ok='OK', cancel='Abbrechen'),
    'es-ES': dict(
        hint='¿Deslizadores bloqueados tras el Sim Update 6? Arrastra aquí — el valor va directo al simulador.',
        connecting='conectando…', connected='conectado', not_running='el simulador no está abierto',
        bad_rva='valores incorrectos — pulsa Buscar', reconnect='Reconectar', detect='Buscar',
        scanning='buscando…', detected='desplazamiento encontrado', ambiguous='varios candidatos — elige uno',
        admin='error al escribir — ejecuta como administrador', reverted='el simulador revirtió el valor',
        language='Idioma', pick_title='¿Cuál es el desplazamiento de Multi Window?',
        pick_hint='Elige la fila que coincida con los números del simulador.', ok='Aceptar', cancel='Cancelar'),
    'fr-FR': dict(
        hint='Curseurs verrouillés après le Sim Update 6 ? Glissez ici — la valeur part directement dans le simulateur.',
        connecting='connexion…', connected='connecté', not_running='le simulateur n’est pas lancé',
        bad_rva='valeurs incohérentes — cliquez sur Détecter', reconnect='Reconnecter', detect='Détecter',
        scanning='analyse…', detected='décalage trouvé', ambiguous='plusieurs candidats — choisissez-en un',
        admin='écriture impossible — lancez en administrateur', reverted='le simulateur a annulé la valeur',
        language='Langue', pick_title='Lequel est le décalage Multi Window ?',
        pick_hint='Choisissez la ligne qui correspond aux valeurs affichées dans le simulateur.',
        ok='OK', cancel='Annuler'),
    'it-IT': dict(
        hint='Cursori bloccati dopo il Sim Update 6? Trascina qui — il valore va direttamente nel simulatore.',
        connecting='connessione…', connected='connesso', not_running='il simulatore non è in esecuzione',
        bad_rva='valori errati — premi Trova', reconnect='Riconnetti', detect='Trova',
        scanning='ricerca…', detected='offset trovato', ambiguous='più candidati — scegline uno',
        admin='scrittura non riuscita — avvia come amministratore', reverted='il simulatore ha annullato il valore',
        language='Lingua', pick_title='Qual è l’offset Multi Window?',
        pick_hint='Scegli la riga che corrisponde ai numeri mostrati nel simulatore.', ok='OK', cancel='Annulla'),
    'pl-PL': dict(
        hint='Suwaki zablokowane po Sim Update 6? Przeciągnij tutaj — wartość trafia prosto do symulatora.',
        connecting='łączenie…', connected='połączono', not_running='symulator nie jest uruchomiony',
        bad_rva='nieprawidłowe wartości — naciśnij Szukaj', reconnect='Połącz ponownie', detect='Szukaj',
        scanning='skanowanie…', detected='znaleziono przesunięcie', ambiguous='kilku kandydatów — wybierz jednego',
        admin='zapis nieudany — uruchom jako administrator', reverted='symulator cofnął wartość',
        language='Język', pick_title='Które to przesunięcie Multi Window?',
        pick_hint='Wybierz wiersz zgodny z liczbami widocznymi w symulatorze.', ok='OK', cancel='Anuluj'),
    'pt-BR': dict(
        hint='Controles travados após o Sim Update 6? Arraste aqui — o valor vai direto para o simulador.',
        connecting='conectando…', connected='conectado', not_running='o simulador não está aberto',
        bad_rva='valores estranhos — clique em Detectar', reconnect='Reconectar', detect='Detectar',
        scanning='procurando…', detected='deslocamento encontrado', ambiguous='vários candidatos — escolha um',
        admin='falha ao gravar — execute como administrador', reverted='o simulador reverteu o valor',
        language='Idioma', pick_title='Qual é o deslocamento do Multi Window?',
        pick_hint='Escolha a linha que corresponde aos números mostrados no simulador.', ok='OK', cancel='Cancelar'),
    'ru-RU': dict(
        hint='Ползунки заблокированы после Sim Update 6? Тяните здесь — значение уходит прямо в симулятор.',
        connecting='подключение…', connected='подключено', not_running='симулятор не запущен',
        bad_rva='значения неверны — нажмите «Найти»', reconnect='Переподключить', detect='Найти',
        scanning='поиск…', detected='смещение найдено', ambiguous='несколько кандидатов — выберите один',
        admin='запись не удалась — запустите от имени администратора', reverted='симулятор вернул значение',
        language='Язык', pick_title='Какое из них — смещение Multi Window?',
        pick_hint='Выберите строку, совпадающую с числами в симуляторе.', ok='ОК', cancel='Отмена'),
    'sv-SE': dict(
        hint='Reglagen låsta efter Sim Update 6? Dra här — värdet går direkt in i simulatorn.',
        connecting='ansluter…', connected='ansluten', not_running='simulatorn körs inte',
        bad_rva='orimliga värden — tryck Sök', reconnect='Anslut igen', detect='Sök',
        scanning='söker…', detected='förskjutning hittad', ambiguous='flera kandidater — välj en',
        admin='skrivning misslyckades — kör som administratör', reverted='simulatorn återställde värdet',
        language='Språk', pick_title='Vilken är Multi Window-förskjutningen?',
        pick_hint='Välj raden som matchar siffrorna i simulatorn.', ok='OK', cancel='Avbryt'),
    'nb-NO': dict(
        hint='Låste glidebrytere etter Sim Update 6? Dra her — verdien går rett inn i simulatoren.',
        connecting='kobler til…', connected='tilkoblet', not_running='simulatoren kjører ikke',
        bad_rva='urimelige verdier — trykk Søk', reconnect='Koble til igjen', detect='Søk',
        scanning='søker…', detected='forskyvning funnet', ambiguous='flere kandidater — velg én',
        admin='skriving mislyktes — kjør som administrator', reverted='simulatoren tilbakestilte verdien',
        language='Språk', pick_title='Hvilken er Multi Window-forskyvningen?',
        pick_hint='Velg raden som samsvarer med tallene i simulatoren.', ok='OK', cancel='Avbryt'),
    'fi-FI': dict(
        hint='Liukusäätimet lukittu Sim Update 6:n jälkeen? Vedä tästä — arvo menee suoraan simulaattoriin.',
        connecting='yhdistetään…', connected='yhdistetty', not_running='simulaattori ei ole käynnissä',
        bad_rva='arvot epäilyttäviä — paina Etsi', reconnect='Yhdistä uudelleen', detect='Etsi',
        scanning='etsitään…', detected='siirtymä löytyi', ambiguous='useita ehdokkaita — valitse yksi',
        admin='kirjoitus epäonnistui — suorita järjestelmänvalvojana', reverted='simulaattori palautti arvon',
        language='Kieli', pick_title='Mikä on Multi Window -siirtymä?',
        pick_hint='Valitse rivi, joka vastaa simulaattorissa näkyviä lukuja.', ok='OK', cancel='Peruuta'),
    'ja-JP': dict(
        hint='Sim Update 6 以降スライダーがロック？ここでドラッグ — 値はそのままシミュレーターに書き込まれます。',
        connecting='接続中…', connected='接続済み', not_running='シミュレーターが起動していません',
        bad_rva='値が不正です —「検出」を押してください', reconnect='再接続', detect='検出',
        scanning='スキャン中…', detected='オフセットを検出', ambiguous='候補が複数あります — 1つ選択',
        admin='書き込み失敗 — 管理者として実行してください', reverted='シミュレーターが値を元に戻しました',
        language='言語', pick_title='どれが Multi Window のオフセットですか？',
        pick_hint='シミュレーターに表示されている数値と一致する行を選んでください。', ok='OK', cancel='キャンセル'),
    'ko-KR': dict(
        hint='Sim Update 6 이후 슬라이더가 잠겼나요? 여기서 드래그하세요 — 값이 시뮬레이터에 바로 기록됩니다.',
        connecting='연결 중…', connected='연결됨', not_running='시뮬레이터가 실행 중이 아닙니다',
        bad_rva='값이 이상합니다 — "검색"을 누르세요', reconnect='다시 연결', detect='검색',
        scanning='검색 중…', detected='오프셋을 찾았습니다', ambiguous='후보가 여러 개입니다 — 하나 선택',
        admin='쓰기 실패 — 관리자 권한으로 실행하세요', reverted='시뮬레이터가 값을 되돌렸습니다',
        language='언어', pick_title='어느 것이 Multi Window 오프셋입니까?',
        pick_hint='시뮬레이터에 표시된 숫자와 일치하는 행을 선택하세요.', ok='확인', cancel='취소'),
    'zh-CN': dict(
        hint='Sim Update 6 后滑块被锁定？在这里拖动 — 数值会直接写入正在运行的模拟器。',
        connecting='正在连接…', connected='已连接', not_running='模拟器未运行',
        bad_rva='数值异常 — 请点击“查找”', reconnect='重新连接', detect='查找',
        scanning='正在扫描…', detected='已找到偏移', ambiguous='有多个候选 — 请选择一个',
        admin='写入失败 — 请以管理员身份运行', reverted='模拟器已还原该数值',
        language='语言', pick_title='哪一个是 Multi Window 偏移？',
        pick_hint='请选择与模拟器中显示的数字一致的行。', ok='确定', cancel='取消'),
}

FALLBACK = 'en-US'


def strings(locale):
    return UI.get(locale, UI[FALLBACK])


def axes(locale):
    return AXES.get(locale, AXES[FALLBACK])


def ordered_axes(locale):
    """(alan, etiket) — lateral, vertical, roll sirasi (oyunla ayni)."""
    lat, ver, roll = axes(locale)
    return [('lateral', lat), ('vertical', ver), ('roll', roll)]
