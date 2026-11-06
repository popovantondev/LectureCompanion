/* Lecture Companion robot scene. No network, no storage. Sound: Web Audio after the first click or key (robot_sound.py). */
(function () {
  'use strict';
  var doc = document;
  var LANG = (doc.documentElement.lang || 'en').slice(0, 2);
  if (!/^(ru|de|en)$/.test(LANG)) LANG = 'en';
  var mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  function reduced() { return mq.matches; }
  var UI = {
    ru: {
      ask: 'Спросить робота', label: 'Вопрос роботу', ph: 'Спросите о программе…', send: 'Отправить вопрос',
      close: 'Закрыть ответ', snd: 'Звук',
      hint: 'Напишите вопрос, например: «Что делает программа?» или «Какие нужны требования?»',
      unk: 'Не знаю — загляните в руководство.', link: 'Открыть руководство →', more: 'Подробнее в руководстве →'
    },
    de: {
      ask: 'Roboter fragen', label: 'Frage an den Roboter', ph: 'Fragen Sie zum Programm …', send: 'Frage senden',
      close: 'Antwort schließen', snd: 'Ton',
      hint: 'Schreiben Sie eine Frage, zum Beispiel: „Was macht das Programm?“ oder „Welche Voraussetzungen gibt es?“',
      unk: 'Das weiß ich nicht – bitte schauen Sie in die Anleitung.', link: 'Anleitung öffnen →',
      more: 'Mehr in der Anleitung →'
    },
    en: {
      ask: 'Ask the robot', label: 'Question for the robot', ph: 'Ask about the program…', send: 'Send question',
      close: 'Close answer', snd: 'Sound',
      hint: 'Type a question, for example: “What does the program do?” or “What are the requirements?”',
      unk: "I don't know – please check the guide.", link: 'Open the guide →', more: 'More in the guide →'
    }
  };
  // k: keywords split by "|" (normalised: lower case, no accents, ß = ss). "=word" = whole word only; a word with a space = phrase
  // (2 points); plain word = word prefix (1 point, one wrong letter is forgiven for words of 5+ letters). g: generic topic, answers only
  // when the question names the program or hits two keywords. w: weight. On a tie the topic higher in the list wins.
  var TOPICS = [
    { k: '=привет|приветик|здравств|=хай|=салют|=здорово|добрый день|добрый вечер|доброе утро|как дела|как ты|как жизнь|как поживаешь|как настроение|как самочувствие|что нового|=hi|=hey|=hello|=hallo|=moin|=servus|=yo|=howdy|guten tag|guten morgen|guten abend|wie geht es|wie gehts|wie geht\'s|wie geht dir|wie lauft|alles gut|was gibt|how are you|how is it going|hows it going|how are things|whats up|how do you do|good morning|good evening|good afternoon',
      a: {
        ru: ['Привет! У меня всё хорошо — спросите о Lecture Companion.', 'Здравствуйте! Спрашивайте о программе.', 'Всё отлично, спасибо! Могу рассказать, что умеет Lecture Companion.', 'Добрый день! Дела хорошо — о чём рассказать в программе?'],
        de: ['Hallo! Mir geht es gut – fragen Sie mich zu Lecture Companion.', 'Guten Tag! Fragen zur Software? Gern.', 'Danke, bestens! Ich erzähle gern, was Lecture Companion kann.', 'Hallo! Alles gut hier – was möchten Sie über das Programm wissen?'],
        en: ['Hi! I’m doing well – ask me about Lecture Companion.', 'Hello! Ask me about the program.', 'All good, thanks! I can tell you what Lecture Companion does.', 'Hey! Doing great – what would you like to know about the program?']
      } },
    { g: 1, k: 'ты кто|кто ты|who are you|wer bist|bist du|are you|=ии|=ai|=ki|google|гугл|бот',
      a: {
        ru: 'Я демонстрационный робот этой страницы: отвечаю готовыми текстами о Lecture Companion и никуда не отправляю ваш вопрос.',
        de: 'Ich bin der Demo-Roboter dieser Seite: Ich antworte mit vorgefertigten Texten über Lecture Companion und sende Ihre Frage nirgendwohin.',
        en: 'I am this page’s demo robot: I reply with ready-made texts about Lecture Companion and send your question nowhere.'
      } },
    { k: 'согласи|закон|юридич|право|уголовн|201|stgb|dsgvo|gdpr|персональн|einwilligung|zustimm|recht|gesetz|strafbar|legal|consent|law',
      a: {
        ru: 'Заранее получите согласие всех участников: тайная запись непубличной речи может быть наказуема по § 201 StGB, а субтитры и слайды могут содержать персональные данные (DSGVO).',
        de: 'Holen Sie vorher die Einwilligung aller Beteiligten ein: Heimliches Aufzeichnen nichtöffentlicher Rede kann nach § 201 StGB strafbar sein, und Untertitel und Folien können personenbezogene Daten (DSGVO) enthalten.',
        en: 'Get everyone’s consent first: secretly recording non-public speech can be a criminal offence under § 201 StGB, and subtitles and slides may contain personal data (GDPR).'
      } },
    { g: 1, k: 'микрофон|записыва|запись|аудио|mikro|aufnahme|aufzeichn|aufnehm|microphone|record|audio',
      a: {
        ru: 'Микрофон программа не записывает: она читает живые субтитры из настольного Teams напрямую.',
        de: 'Das Programm nimmt kein Mikrofon auf: Es liest die Live-Untertitel direkt aus Teams Desktop.',
        en: 'The program does not record the microphone: it reads the live subtitles straight from Teams desktop.'
      } },
    { k: 'без интернет|нужен ли интернет|интернет|офлайн|оффлайн|без сети|=сети|=сеть|offline|online|ohne internet|internet|ohne netz|=netz|netzwerk|without internet|no internet|=wifi|=wlan|network|a network',
      a: {
        ru: 'Программа ничего не отправляет в облако: субтитры и слайды обрабатываются локально, без ключей API. Интернет при необходимости используют только Teams и Windows.',
        de: 'Das Programm schickt nichts in eine Cloud: Untertitel und Folien werden lokal verarbeitet, ohne API-Schlüssel. Das Internet nutzen bei Bedarf nur Teams und Windows.',
        en: 'The program sends nothing to a cloud: subtitles and slides are processed locally, without API keys. If needed, only Teams and Windows use the internet.'
      } },
    { k: 'защит|данн|конфиденц|приватн|облак|облач|отправля|отправл|передает|передаёт|утечк|хранит|хранен|=api|datenschutz|daten|privat|cloud|gesendet|senden|ubertrag|gespeichert|hochlad|privacy|private|data|upload|sent|send|stored|store|local|lokal|локальн',
      a: {
        ru: 'Субтитры и изображения слайдов обрабатываются локально: ни облака, ни ключей API, автоматически ничего не загружается. Последние десять ответов лежат в папке «Daten»; в чат Teams программа ничего не пишет.',
        de: 'Untertitel und Folienbilder werden lokal verarbeitet: keine Cloud, keine API-Schlüssel, nichts wird automatisch hochgeladen. Die zehn letzten Antworten liegen im Ordner „Daten“; in den Teams-Chat schreibt das Programm nichts.',
        en: 'Subtitles and slide images are processed locally: no cloud, no API keys, nothing is uploaded automatically. The last ten answers are kept in the “Daten” folder; the program writes nothing to the Teams chat.'
      } },
    { k: 'цена|цены|стоит|стоимост|бесплатн|платн|платить|оплат|подписк|лиценз|kost|preis|lizenz|kostenlos|gratis|umsonst|zahlen|=abo|cost|price|pricing|free|licen|pay|subscription',
      a: {
        ru: 'О цене в документации ничего не сказано. Сказано: ключей API и облака нет; неизменённую официальную EXE можно скачать и запускать для личного некоммерческого использования, но нельзя менять и распространять.',
        de: 'Zum Preis steht in der Dokumentation nichts. Bekannt ist: keine API-Schlüssel, keine Cloud; die unveränderte offizielle EXE darf privat und nicht kommerziell geladen und ausgeführt werden, Ändern und Weitergeben ist nicht erlaubt.',
        en: 'The documentation names no price. What it says: no API keys and no cloud; the unmodified official EXE may be downloaded and run for personal, non-commercial use, but not modified or redistributed.'
      } },
    { k: 'язык|языки|немецк|русск|англий|=de|=en|=ru|sprache|sprachen|deutsch|russisch|englisch|language|languages|german|russian|english|перевод|translat|ubersetz',
      a: {
        ru: 'Интерфейс и новые ответы — на немецком, английском и русском (по умолчанию немецкий, переключается в меню робота). Ответы идут сначала на языке субтитров лекции, затем на языке интерфейса.',
        de: 'Oberfläche und neue Antworten gibt es auf Deutsch, Englisch und Russisch (Standard ist Deutsch, umschaltbar im Roboter-Menü). Antworten kommen zuerst in der Sprache der Untertitel, dann in der Oberflächensprache.',
        en: 'The interface and new answers come in German, English and Russian (German is the default, switchable in the robot menu). Answers use the subtitle language first, then the interface language.'
      } },
    { k: 'озу|оператив|=ram|arbeitsspeicher|=speicher|=gb|=гб|32|16|memory|память|памяти',
      a: {
        ru: 'Желательно 32 ГБ ОЗУ. На 16 ГБ может не хватить одновременно для Teams и моделей.',
        de: 'Empfohlen sind 32 GB RAM. Mit 16 GB kann es für Teams und die Modelle zugleich nicht reichen.',
        en: '32 GB of RAM is recommended. 16 GB may not be enough for Teams and the models at once.'
      } },
    { k: 'npu|gpu|cpu|intel|видеокарт|процессор|графическ|ускорител|grafikkarte|prozessor|grafik|graphics|processor|openvino|accelerator',
      a: {
        ru: 'Первым используется совместимый Intel NPU; если его нет или модель не запускается, программа проверяет совместимые CPU/GPU и сохраняет самый быстрый. Всё считается локально.',
        de: 'Zuerst wird ein kompatibler Intel-NPU genutzt; fehlt er oder startet das Modell nicht, prüft das Programm kompatible CPU/GPU und merkt sich das schnellste Gerät. Alles läuft lokal.',
        en: 'A compatible Intel NPU is used first; if there is none or the model does not start, the program tests compatible CPU/GPU devices and keeps the fastest one. Everything runs locally.'
      } },
    { k: 'требован|системн|windows|виндовс|=x64|=mac|=macos|=linux|=arm|совместим|мощн|компьютер|=пк|=pc|ноутбук|железо|места|место|диск|=ssd|анфорд|anforderung|systemanforder|voraussetz|kompatibel|rechner|laptop|speicherplatz|festplatte|platz|requirement|requirements|compatible|computer|hardware|disk|space|storage|specs',
      a: {
        ru: 'Windows 11 x64, желательно 32 ГБ ОЗУ и внутренний SSD; нужны Teams Desktop и драйверы, около 25 ГБ места. Windows ARM, macOS и Linux не поддерживаются.',
        de: 'Windows 11 x64, möglichst 32 GB RAM und interne SSD; dazu Teams Desktop, Treiber und rund 25 GB Platz. Windows ARM, macOS und Linux werden nicht unterstützt.',
        en: 'Windows 11 x64, ideally 32 GB of RAM and an internal SSD; you need Teams Desktop, drivers and about 25 GB of space. Windows ARM, macOS and Linux are not supported.'
      } },
    { k: 'не подписан|nicht signiert|not signed|безопасн|вирус|подпис|антивирус|smartscreen|defender|доверя|sicher|signier|virenscanner|antivirus|virus|safe|safety|signed|unsigned|trust|malware',
      a: {
        ru: 'EXE не подписан цифровой подписью, на рабочем ПК может понадобиться одобрение IT. Проверьте источник и контрольную сумму, защиту Windows не отключайте. Проверка на втором чистом ПК пока не проведена.',
        de: 'Die EXE ist nicht digital signiert; auf einem Arbeits-PC kann eine Freigabe der IT nötig sein. Prüfen Sie Quelle und Prüfsumme und lassen Sie den Schutz aktiviert. Eine Prüfung auf einem zweiten sauberen PC steht noch aus.',
        en: 'The EXE is not digitally signed; on a work PC IT approval may be needed. Check the source and the checksum and keep your protection switched on. A check on a second clean PC is still pending.'
      } },
    { k: 'установ|скача|загруз|download|install|herunterlad|laden|einricht|joinportable|zip|распаков|запуст|=exe|starten|setup|размер|teile|parts|как начать|с чего начать|first steps|get started|erste schritte|loslegen|anfangen|wie fange|fange an|start|how do i start|how to start|how do i begin',
      a: {
        ru: 'Скачайте четыре части ZIP и JoinPortable.cmd в одну папку (около 5,8 ГБ), запустите JoinPortable.cmd (проверяет размеры и SHA-256, ничего не ставит), распакуйте ZIP на внутренний SSD и откройте LectureCompanion.exe.',
        de: 'Laden Sie die vier ZIP-Teile und JoinPortable.cmd in einen Ordner (etwa 5,8 GB), führen Sie JoinPortable.cmd aus (prüft Größen und SHA-256, installiert nichts), entpacken Sie das ZIP auf eine interne SSD und starten Sie LectureCompanion.exe.',
        en: 'Download the four ZIP parts and JoinPortable.cmd into one folder (about 5.8 GB), run JoinPortable.cmd (checks sizes and SHA-256, installs nothing), extract the ZIP to an internal SSD and open LectureCompanion.exe.'
      } },
    { k: 'ошибка при|ошибка в|fehler beim|fehler bei|error on|error when|error at|error during|не работает|ошибк|не запуска|завис|медленн|долго|сбой|проблем|не отвечает|fehler|klappt nicht|funktioniert nicht|nicht starten|langsam|hangt|problem|probleme|error|not working|doesnt work|slow|crash|freez|stuck|troubleshoot',
      a: {
        ru: 'Первый запуск и тест устройств идут дольше обычного: смотрите на этап и время. Ошибки пишутся в Daten/npu.log, Daten/server.log и Daten/device-benchmark.json; подробнее — в разделе руководства «Если что-то не работает».',
        de: 'Der erste Start und der Gerätetest dauern länger als sonst: Achten Sie auf Phase und Zeit. Fehler stehen in Daten/npu.log, Daten/server.log und Daten/device-benchmark.json; mehr im Abschnitt „Wenn etwas nicht klappt“ der Anleitung.',
        en: 'The first start and the device test take longer than usual: watch the stage and the time. Errors are logged in Daten/npu.log, Daten/server.log and Daten/device-benchmark.json; more in the guide section “Troubleshooting”.'
      } },
    { k: 'руководств|инструкц|справк|помощ|документац|гайд|мануал|guide|anleitung|handbuch|hilfe|dokumentation|manual|help|docs|documentation|tutorial|где почитать|подробнее',
      a: {
        ru: 'Пошаговое руководство есть на трёх языках: первый запуск, требования, подготовка Teams, правовые замечания, управление роботом, папки и данные, решение проблем, перенос и демо без Teams. Ссылка ниже.',
        de: 'Die Schritt-für-Schritt-Anleitung gibt es in drei Sprachen: erster Start, Voraussetzungen, Teams vorbereiten, Rechtliches, Bedienung, Ordner und Daten, Fehlersuche, Verschieben und Demo ohne Teams. Link unten.',
        en: 'The step-by-step guide comes in three languages: first launch, requirements, preparing Teams, legal notes, controls, folders and privacy, troubleshooting, moving and the demo without Teams. Link below.'
      } },
    { g: 1, k: 'режим|быстро|обычно|вдумчив|modus|modi|schnell|grundlich|normal|mode|fast|balanced|deep',
      a: {
        ru: 'Три режима: «Быстро» — коротко, без дополнительных рассуждений; «Обычно» — сбалансированно; «Вдумчиво» — дополнительные рассуждения только для текстовых вопросов.',
        de: 'Drei Modi: „Schnell“ – kurz, ohne zusätzliches Denken; „Normal“; „Gründlich“ – zusätzliches Denken nur bei Textfragen.',
        en: 'Three modes: Fast (short, no extra reasoning), Balanced and Deep (extra reasoning for text questions only).'
      } },
    { k: 'демо|попроб|пример|demo|ausprobier|beispiel|testen|try|example|без teams|ohne teams|without teams',
      a: {
        ru: 'Попробовать можно без Teams: LectureCompanionDemo.exe открывает вымышленные примеры, не запуская Teams или модели.',
        de: 'Ausprobieren geht ohne Teams: LectureCompanionDemo.exe zeigt erfundene Beispiele, ohne Teams oder Modelle zu starten.',
        en: 'You can try it without Teams: LectureCompanionDemo.exe shows fictional examples without starting Teams or the models.'
      } },
    { k: 'teams|тимс|субтитр|встреч|слайд|untertitel|folie|meeting|subtitle|caption|slide',
      a: {
        ru: 'Нужны настольный Teams и живые субтитры; новая речь проверяется примерно раз в минуту. Слайд разбирается только при настоящей демонстрации экрана. В чат Teams программа ничего не пишет.',
        de: 'Sie brauchen Teams Desktop und Live-Untertitel; neue Rede wird etwa einmal pro Minute geprüft. Eine Folie wird nur bei echter Bildschirmfreigabe analysiert. In den Teams-Chat schreibt das Programm nichts.',
        en: 'You need Teams desktop and live subtitles; new speech is checked about once a minute. A slide is analysed only during a real screen share. The program writes nothing to the Teams chat.'
      } },
    { g: 1, k: 'делает|умеет|зачем|назначен|что такое lecture|что за программа|что это за программа|что это|для чего|функци|возможност|macht|wofur|wozu|wofur ist|wozu ist|wozu dient|wofur dient|ist das gut|was ist das|was ist lecture|was kann|funktion|what does|what is it|what is this|what is lecture|what can|purpose|feature',
      w: .5,
      a: {
        ru: 'Lecture Companion помогает следить за лекцией в Teams: локально обобщает субтитры и объясняет выбранный слайд.',
        de: 'Lecture Companion hilft, einer Vorlesung in Teams zu folgen: Es fasst die Untertitel lokal zusammen und erklärt die gewählte Folie.',
        en: 'Lecture Companion helps you follow a lecture in Teams: it summarises the subtitles locally and explains the selected slide.'
      } }
  ];
  function norm(s) {
    return String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/ß/g, 'ss');
  }
  TOPICS.forEach(function (t) { t.keys = t.k.split('|').map(norm); });
  // True when a and b differ by at most one letter (one wrong, missing, extra or swapped letter).
  function near(a, b) {
    if (a === b) return true;
    var la = a.length, lb = b.length, i = 0;
    if (Math.abs(la - lb) > 1) return false;
    while (i < la && i < lb && a.charAt(i) === b.charAt(i)) i++;
    if (la === lb) {
      if (a.slice(i + 1) === b.slice(i + 1)) return true;
      return a.charAt(i) === b.charAt(i + 1) && a.charAt(i + 1) === b.charAt(i) && a.slice(i + 2) === b.slice(i + 2);
    }
    return la > lb ? a.slice(i + 1) === b.slice(i) : a.slice(i) === b.slice(i + 1);
  }
  // 1 for a word that starts with the keyword, 0.6 for a one-letter slip (keywords of 6+ letters), else 0.
  function hasWord(tokens, kw) {
    var best = 0;
    tokens.forEach(function (tk) {
      if (tk.indexOf(kw) === 0) { best = 1; return; }
      if (best || kw.length < 6) return;
      for (var d = -1; d <= 1; d++) if (tk.length >= kw.length + d && near(tk.slice(0, kw.length + d), kw)) { best = 0.6; return; }
    });
    return best;
  }
  function pick(a) { a = [].concat(a); return a[Math.floor(Math.random() * a.length)]; }
  function findTopic(question) {
    var text = norm(question);
    var tokens = text.split(/[^a-z0-9\u0400-\u04ff§]+/).filter(Boolean);
    var best = null, top = 0;
    var anchor = /lecture|companion|лекци|программ|приложен|робот|teams|тимс|vorlesung|programm|roboter|robot|program|software|\bapp\b/.test(text);
    TOPICS.forEach(function (topic) {
      var score = 0;
      topic.keys.forEach(function (kw) {
        if (kw.indexOf(' ') > -1) { if (text.indexOf(kw) > -1) score += 2; }
        else if (kw.charAt(0) === '=') { if (tokens.indexOf(kw.slice(1)) > -1) score += 1; }
        else { var hit = hasWord(tokens, kw); if (hit) score += hit; }
      });
      if (topic.g && score < 2 && !anchor) return;
      score *= topic.w || 1;
      if (score > top) { top = score; best = topic; }
    });
    return best;
  }
  var unlocked = false, ctx = null, lastSound = {}, buffers = {};
  function ensureCtx() {
    if (ctx || reduced()) return ctx;
    try { var C = window.AudioContext || window.webkitAudioContext; if (C) ctx = new C(); } catch (e) { ctx = null; }
    return ctx;
  }
  function unlock() {
    if (unlocked) return;
    unlocked = true;
    ['pointerdown', 'keydown'].forEach(function (t) { doc.removeEventListener(t, unlock, true); });
    ensureCtx();
  }
  ['pointerdown', 'keydown'].forEach(function (t) { doc.addEventListener(t, unlock, true); });
  function seeded(seed) {
    return function () { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
  }
  function tone(c, kind) {
    var rate = 24000, volume = 0.35, reveal = kind === 'reveal';
    var notes = reveal ? [[550, 1050, 0.28]] : [[980, 1260, 0.14], [820, 930, 0.10]];
    var rnd = seeded(42), data = [], phase = 0, filtered = 0;
    notes.forEach(function (n) {
      var low = n[0], high = n[1], dur = n[2], count = Math.floor(rate * dur), i, t, env, v;
      for (i = 0; i < count; i++) {
        t = i / rate;
        phase += 2 * Math.PI * (low + (high - low) * i / count) / rate;
        env = Math.min(1, t / 0.018) * Math.min(1, (dur - t) / 0.065);
        if (reveal) {
          filtered = 0.84 * filtered + 0.16 * (rnd() * 2 - 1);
          v = (0.24 * Math.sin(phase) + 1.3 * filtered) * Math.sin(Math.PI * i / count);
        } else v = Math.sin(phase) + 0.12 * Math.sin(phase * 2);
        data.push(5200 * volume * Math.max(0, Math.min(1, env)) * v / 32768);
      }
      for (i = 0; i < Math.floor(rate * 0.035); i++) data.push(0);
    });
    var buffer = c.createBuffer(1, data.length, rate);
    buffer.getChannelData(0).set(data);
    return buffer;
  }
  function play(kind) {
    if (!unlocked || reduced()) return;
    var c = ensureCtx(), now = performance.now();
    if (!c || now - (lastSound[kind] || -1e4) < 700) return;
    lastSound[kind] = now;
    try {
      if (c.state === 'suspended') { var p = c.resume(); if (p && p.catch) p.catch(function () {}); }
      var src = c.createBufferSource();
      src.buffer = buffers[kind] || (buffers[kind] = tone(c, kind));
      src.connect(c.destination);
      src.start();
    } catch (e) { }
  }
  var EYES = [{ x: 481, y: 382 }, { x: 717, y: 382 }], K = 9.08, COVER = '#06080c', BITS = 14, GAP = 0.14;
  var ICON_SEND = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 12h15M13 5.500l6.500 6.500-6.500 6.500"/></svg>';
  var scenes = 0;
  function el(tag, cls) { var n = doc.createElement(tag); if (cls) n.className = cls; return n; }
  function eyeMarkup(id) {
    var s = '<svg viewBox="0 0 1199 1312" aria-hidden="true"><defs><radialGradient id="robot-cov-' + id + '"><stop offset=".72" stop-color="' + COVER + '"/><stop offset="1" stop-color="' + COVER + '" stop-opacity="0"/></radialGradient><clipPath id="robot-clip-' + id + '"><rect x="363" y="264" width="482" height="245" rx="110"/></clipPath></defs>';
    EYES.forEach(function (e) {
      s += '<ellipse data-eye="lid" cx="' + e.x + '" cy="' + e.y + '" rx="' + 9 * K + '" ry="' + 14 * K + '" fill="url(#robot-cov-' + id + ')"/>';
      s += '<line data-eye="line" x1="' + (e.x - 4 * K) + '" x2="' + (e.x + 4 * K) + '" y1="' + e.y + '" y2="' + e.y + '" stroke="#8EE7FF" stroke-width="' + 2 * K + '" stroke-linecap="round"/>';
    });
    s += '<g clip-path="url(#robot-clip-' + id + ')">';
    for (var i = 0; i < BITS; i++) s += '<text data-eye="bit" text-anchor="middle" dominant-baseline="central">0</text>';
    return s + '</g></svg>';
  }
  function init(stage) {
    var img = stage.querySelector('img');
    if (!img || stage.getAttribute('data-robot-ready')) return;
    var T = UI[LANG], id = ++scenes, dock = stage.getAttribute('data-robot-mode') === 'dock';
    var guide = stage.getAttribute('data-guide') || 'Guide-' + LANG + '.html';
    stage.setAttribute('data-robot-ready', '1');
    var lift = el('div', 'robot-lift'), hit = el('button', 'robot-hit'), qid = 'robot-q-' + id;
    hit.type = 'button';
    hit.setAttribute('aria-expanded', 'false');
    hit.setAttribute('aria-controls', 'robot-pop-' + id);
    hit.setAttribute('aria-label', T.ask);
    img.alt = '';
    img.classList.add('robot-img');
    hit.appendChild(img);
    hit.insertAdjacentHTML('beforeend', eyeMarkup(id));
    lift.appendChild(hit);
    stage.appendChild(lift);
    stage.insertAdjacentHTML('beforeend',
      '<div class="robot-pop" id="robot-pop-' + id + '"><form class="robot-pill" autocomplete="off"><label class="robot-sr" for="' + qid + '">' + T.label +
      '</label><input type="text" id="' + qid + '" name="q" maxlength="300" placeholder="' + T.ph + '" enterkeyhint="send"><button class="robot-send" type="submit" aria-label="' +
      T.send + '">' + ICON_SEND + '</button></form><div class="robot-answer" hidden aria-live="polite" aria-busy="false"><p class="robot-typed" aria-hidden="true"></p><span class="robot-sr"></span>' +
      '<div class="robot-links"></div><button class="robot-close" type="button" aria-label="' + T.close + '">×</button></div></div>');
    function q(sel) { return stage.querySelector(sel); }
    var stack = dock ? stage.querySelector('.robot-stack') : null, meta = null;
    var form = q('.robot-pill'), input = q('input'), answer = q('.robot-answer'), typed = q('.robot-typed'),
        spoken = q('.robot-answer .robot-sr'), linkBox = q('.robot-links'), closeBtn = q('.robot-close');
    var pop = q('.robot-pop');
    if (dock) {
      meta = el('p', 'robot-meta');
      answer.insertBefore(meta, typed);
      stack.appendChild(answer);
      stack.tabIndex = 0;
      stage.classList.add('is-open');
    } else {
      count = el('span', 'robot-count');
      count.setAttribute('aria-hidden', 'true');
      answer.appendChild(count);
    }
    var svgRoot = hit.querySelector('svg');
    function all(name) { return [].slice.call(svgRoot.querySelectorAll('[data-eye="' + name + '"]')); }
    var lids = all('lid'), lines = all('line'), bits = all('bit');
    function show(list, on) { list.forEach(function (n) { n.style.visibility = on ? 'visible' : 'hidden'; }); }
    function eyes(mode) {
      show(lids, mode !== 'open'); show(lines, mode === 'closed'); show(bits, false);
    }
    var isOpen = dock, quiet = false, state = 'idle', timers = [], raf = 0, leaveTimer = 0;
    function later(fn, ms) { var t = setTimeout(fn, ms); timers.push(t); return t; }
    function stopAll() {
      timers.forEach(clearTimeout); timers = [];
      if (raf) cancelAnimationFrame(raf);
      raf = 0; state = 'idle'; eyes('open');
      answer.classList.remove('is-typing'); answer.setAttribute('aria-busy', 'false');
    }
    (function idle() {
      setTimeout(function () {
        if (!reduced() && state === 'idle' && !doc.hidden) {
          eyes('closed');
          setTimeout(function () { if (state === 'idle') eyes('open'); }, 130);
        }
        idle();
      }, 5500 + Math.random() * 5000);
    })();
    function blink(n) {
      if (state === 'think') return;
      eyes(n > 0 && n % 2 === 0 ? 'closed' : 'open');
      if (n > 0) later(function () { blink(n - 1); }, 170);
    }
    function place(base, digits) {
      bits.forEach(function (b, i) {
        var linear = base - i * GAP;
        if (Math.abs(linear) > 1) { b.style.visibility = 'hidden'; return; }
        var angle = linear * 1.35, scale = Math.max(0.16, Math.cos(angle));
        b.textContent = digits.charAt(i);
        b.setAttribute('transform', 'translate(' + (599 + 27 * K * Math.sin(angle)).toFixed(1) + ' 392) scale(' + scale.toFixed(3) + ' 1)');
        b.style.visibility = 'visible';
      });
    }
    function randBits() { var d = ''; for (var i = 0; i < BITS; i++) d += Math.random() < 0.5 ? '0' : '1'; return d; }
    // While thinking, small digits run across the face instead of the eyes (a still row with reduced motion).
    function thinkLoop() {
      var start = performance.now(), last = 0, cycle = -1, digits = '', span = 2 + (BITS - 1) * GAP;
      eyes('think');
      if (reduced()) { place(1 - GAP / 2, randBits()); return; }
      function frame(now) {
        if (state !== 'think') return;
        if (now - last >= 33) {
          last = now;
          var t = (now - start) / 1000, c = Math.floor(t / 1.9);
          if (c !== cycle) { cycle = c; digits = randBits(); }
          place(-1 + (t % 1.9) / 1.9 * span, digits);
        }
        raf = requestAnimationFrame(frame);
      }
      raf = requestAnimationFrame(frame);
    }
    // Guide mode keeps the answers of this visit so the wheel / arrows / swipe can leaf through them.
    var hist = [], histView = null, count; // count: the "2 / 3" label, made above
    function showCount() {
      if (!count) return;
      var n = hist.length, at = histView === null ? n : histView + 1;
      count.textContent = n > 1 ? at + ' / ' + n : '';
      answer.classList.toggle('is-nav', n > 1);
    }
    function paint(text, link) {
      typed.textContent = text;
      spoken.textContent = text;
      linkBox.textContent = '';
      if (link) {
        var a = el('a'); a.href = guide; a.textContent = link; linkBox.appendChild(a);
      }
    }
    function setAnswer(text, link, record) {
      paint(text, link);
      if (!dock && record) { hist.push({ text: text, link: link }); if (hist.length > 10) hist.shift(); histView = null; showCount(); }
      answer.classList.remove('is-typing');
      answer.setAttribute('aria-busy', 'false');
      state = 'idle'; eyes('open');
    }
    function p2(n) { return (n < 10 ? '0' : '') + n; }
    function stamp() { var d = new Date(); return p2(d.getHours()) + ':' + p2(d.getMinutes()) + ':' + p2(d.getSeconds()); }
    function metaMarkup(time) {
      return '<span class="robot-tag"></span><span></span><span class="robot-meta-extra"></span>';
    }
    function fillMeta(node, time) {
      node.innerHTML = metaMarkup();
      node.children[0].textContent = stage.getAttribute('data-demo-tag') || '';
      node.children[1].textContent = time;
      node.children[2].textContent = ' · ' + (stage.getAttribute('data-demo-meta') || '');
    }
    // Dock mode: the newest card is in front, older ones peek out behind it (at most three).
    // dockView = index of the card in front (null = the newest); cards after it are put away, cards before it peek out behind.
    var dockView = null;
    function dockItems() {
      var list = [].slice.call(stack.querySelectorAll('.robot-demo-card'));
      if (!answer.hidden) list.push(answer);
      return list;
    }
    function relayout() {
      var cards = [].slice.call(stack.querySelectorAll('.robot-demo-card'));
      while (cards.length > 6) stack.removeChild(cards.shift());
      var list = dockItems();
      if (dockView === null || dockView > list.length - 1) dockView = list.length - 1;
      list.forEach(function (c, i) {
        c.classList.remove('is-back', 'is-away'); c.style.removeProperty('--d');
        if (i > dockView) c.classList.add('is-away');
        else if (i < dockView) {
          var d = dockView - i;
          c.classList.add('is-back'); c.style.setProperty('--d', String(Math.min(d, 4)));
          if (d > 3) c.classList.add('is-away');
        }
      });
    }
    // Leaf through the stack: dir -1 = older (up), +1 = newer (down). Returns true when the stack can be leafed at all.
    function leaf(dir) {
      if (dock) {
        var list = dockItems(), at = dockView === null ? list.length - 1 : dockView, to = Math.max(0, Math.min(list.length - 1, at + dir));
        if (to !== at) { dockView = to; relayout(); }
        return list.length > 1;
      }
      var n = hist.length;
      if (n < 2) return false;
      if (state !== 'idle' || answer.hidden) return true;
      var from = histView === null ? n - 1 : histView, next = Math.max(0, Math.min(n - 1, from + dir));
      if (next !== from) { histView = next; paint(hist[next].text, hist[next].link); showCount(); }
      return true;
    }
    var wheelSum = 0, wheelAt = 0, swipeY = null, swipeX = 0;
    function onWheel(e) {
      if (!(dock || hist.length > 1)) return;
      e.preventDefault();
      var now = performance.now(), dy = e.deltaY * (e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? 300 : 1);
      if (now - wheelAt > 350) wheelSum = 0;
      wheelAt = now;
      wheelSum += dy;
      if (Math.abs(wheelSum) < 30) return;
      leaf(wheelSum > 0 ? 1 : -1);
      wheelSum = 0; wheelAt = now + 150;
    }
    function swipeStart(e) { if (e.pointerType !== 'mouse') { swipeY = e.clientY; swipeX = e.clientX; } }
    function swipeEnd(e) {
      if (swipeY === null) return;
      var dy = e.clientY - swipeY, dx = e.clientX - swipeX;
      swipeY = null;
      if (Math.abs(dy) > 36 && Math.abs(dy) > Math.abs(dx)) leaf(dy > 0 ? -1 : 1);
    }
    [dock ? stack : answer].forEach(function (zone) {
      zone.addEventListener('wheel', onWheel, { passive: false });
      zone.addEventListener('pointerdown', swipeStart);
      zone.addEventListener('pointerup', swipeEnd);
      zone.addEventListener('pointercancel', function () { swipeY = null; });
    });
    function pushBack() {
      var card = el('article', 'robot-demo-card'), m = el('p', 'robot-meta'), t = el('p', 'robot-text');
      fillMeta(m, answer.getAttribute('data-time') || stamp());
      t.textContent = spoken.textContent;
      card.appendChild(m); card.appendChild(t);
      stack.insertBefore(card, answer);
    }
    function ask(raw) {
      var q = String(raw).replace(/\s+/g, ' ').trim().slice(0, 300);
      stopAll();
      if (dock) {
        if (!answer.hidden && spoken.textContent) pushBack();
        answer.setAttribute('data-time', stamp());
        fillMeta(meta, answer.getAttribute('data-time'));
        typed.textContent = ''; spoken.textContent = ''; linkBox.textContent = '';
      }
      answer.hidden = false;
      if (dock) { dockView = null; relayout(); }
      else { histView = null; if (count) count.textContent = ''; }
      if (!q) { setAnswer(T.hint, ''); return; }
      var topic = findTopic(q), text = topic ? pick(topic.a[LANG]) : T.unk, link = topic ? T.more : T.link;
      input.value = '';
      state = 'think';
      typed.textContent = ''; spoken.textContent = ''; linkBox.textContent = '';
      typed.appendChild(el('span', 'robot-dots')).innerHTML = '<i></i><i></i><i></i>';
      answer.setAttribute('aria-busy', 'true');
      thinkLoop();
      later(function () {
        if (raf) cancelAnimationFrame(raf);
        raf = 0;
        if (reduced()) { setAnswer(text, link, true); return; }
        state = 'type'; eyes('open');
        typed.textContent = '';
        answer.classList.add('is-typing');
        blink(4); play('answer');
        var i = 0, chars = Array.from(text);
        (function step() {
          i++;
          typed.textContent = chars.slice(0, i).join('');
          if (i < chars.length) later(step, 25 + Math.random() * 10);
          else { stopAll(); setAnswer(text, link, true); }
        })();
      }, 800 + Math.random() * 800);
    }
    function open(focusInput) {
      clearTimeout(leaveTimer);
      if (!isOpen) {
        isOpen = true;
        stage.classList.add('is-open');
        hit.setAttribute('aria-expanded', 'true');
        play('reveal');
      }
      if (focusInput) { try { input.focus(); } catch (e) { } }
    }
    function close(returnFocus) {
      clearTimeout(leaveTimer);
      if (dock) {
        stopAll();
        answer.hidden = true; typed.textContent = ''; spoken.textContent = ''; linkBox.textContent = '';
        relayout();
        if (returnFocus) { quiet = true; try { hit.focus(); } catch (e) { } quiet = false; }
        return;
      }
      if (!isOpen) return;
      stopAll();
      isOpen = false;
      stage.classList.remove('is-open');
      hit.setAttribute('aria-expanded', 'false');
      answer.hidden = true; typed.textContent = ''; spoken.textContent = ''; linkBox.textContent = '';
      if (returnFocus) { quiet = true; try { hit.focus(); } catch (e) { } quiet = false; }
    }
    function leaveSoon() {
      clearTimeout(leaveTimer);
      if (dock) { dockLeave(); return; }
      leaveTimer = setTimeout(function () {
        var busy = state !== 'idle' || !answer.hidden || input.value || stage.contains(doc.activeElement) && doc.activeElement !== hit;
        if (!busy && !stage.matches(':hover')) close(false);
      }, 450);
    }
    // Dock (landing preview): the card stack is always there; hover, focus or touch lifts the robot, slides the question
    // field out from under it and plays the reveal sound. Leaving (or Esc) tucks the field away again.
    var askTimer = 0;
    function lift_(on) {
      if (!dock) return;
      clearTimeout(askTimer);
      if (on && !stage.classList.contains('is-lift')) play('reveal');
      stage.classList.toggle('is-lift', on);
      stage.classList.toggle('is-ask', on);
      hit.setAttribute('aria-expanded', on ? 'true' : 'false');
    }
    function dockHold() {
      var a = doc.activeElement;
      return lift.matches(':hover') || pop.matches(':hover') || input.value || a === input ||
        (a === hit && hit.matches(':focus-visible'));
    }
    function dockLeave() {
      clearTimeout(askTimer);
      askTimer = setTimeout(function () {
        if (state !== 'idle') { dockLeave(); return; }
        if (!dockHold()) lift_(false);
      }, 450);
    }
    if (dock) {
      [lift, pop].forEach(function (n) {
        n.addEventListener('pointerenter', function () { lift_(true); });
        n.addEventListener('pointerleave', dockLeave);
      });
      hit.addEventListener('focus', function () { if (!quiet) lift_(true); });
      hit.addEventListener('blur', dockLeave);
      input.addEventListener('focus', function () { lift_(true); });
    }
    function canLeaf() { return dock || hist.length > 1; }
    stage.addEventListener('keydown', function (e) {
      if ((e.key !== 'ArrowUp' && e.key !== 'ArrowDown') || !canLeaf()) return;
      var t = e.target;
      if (t !== input && t !== hit && t !== stack && !(stack && stack.contains(t))) { if (dock || !answer.contains(t)) return; }
      e.preventDefault();
      leaf(e.key === 'ArrowUp' ? -1 : 1);
    });
    stage.addEventListener('pointerenter', function () { open(false); });
    stage.addEventListener('pointerleave', leaveSoon);
    stage.addEventListener('focusin', function () { if (!quiet) open(false); });
    stage.addEventListener('focusout', function (e) { if (!e.relatedTarget || !stage.contains(e.relatedTarget)) leaveSoon(); });
    hit.addEventListener('click', function () { lift_(true); open(true); });
    stage.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      if (dock && stage.classList.contains('is-ask')) {
        e.preventDefault();
        if (!answer.hidden) close(false);
        lift_(false);
        quiet = true; try { hit.focus(); } catch (x) { } quiet = false;
      } else if (isOpen && (!dock || !answer.hidden)) { e.preventDefault(); close(true); }
    });
    doc.addEventListener('pointerdown', function (e) { if (!dock && isOpen && !stage.contains(e.target)) close(false); });
    form.addEventListener('submit', function (e) { e.preventDefault(); ask(input.value); });
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { e.preventDefault(); ask(input.value); }
    });
    closeBtn.addEventListener('click', function () { close(true); });
  }
  function start() { [].slice.call(doc.querySelectorAll('[data-robot]')).forEach(init); }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', start); else start();
})();