# Lecture Companion

<!-- public-release:start -->
Помогает следить за лекцией в Teams: локально обобщает субтитры и объясняет выбранный слайд.

**Windows 11 · x64 · Предварительный выпуск 2.4**

**[Скачать](https://github.com/popovantondev/LectureCompanion/releases/tag/v2.4)** · **[Инструкция](https://popovantondev.github.io/LectureCompanion/Guide-ru.html)** · **[Сообщить об ошибке](https://github.com/popovantondev/LectureCompanion/issues/new/choose)**

**Требования и ограничения:** Teams Desktop и совместимые драйверы; рекомендуются 32 ГБ RAM, внутренняя SSD и 25 ГБ свободного места для частей, ZIP и распаковки. EXE не подписан; проверка на втором чистом ПК не выполнена.

**Первые шаги:** Скачайте четыре части и JoinPortable.cmd в одну папку (всего около 5,8 ГБ). Запустите JoinPortable.cmd для проверки и сборки ZIP, распакуйте целиком и откройте LectureCompanion.exe.

**Файлы приложения:**

- [`JoinPortable.cmd`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/JoinPortable.cmd)
- [`LectureCompanion-2.4-Final-Portable.zip.part01`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/LectureCompanion-2.4-Final-Portable.zip.part01)
- [`LectureCompanion-2.4-Final-Portable.zip.part02`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/LectureCompanion-2.4-Final-Portable.zip.part02)
- [`LectureCompanion-2.4-Final-Portable.zip.part03`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/LectureCompanion-2.4-Final-Portable.zip.part03)
- [`LectureCompanion-2.4-Final-Portable.zip.part04`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/LectureCompanion-2.4-Final-Portable.zip.part04)

**Контрольные суммы:** [`SHA256SUMS`](https://github.com/popovantondev/LectureCompanion/releases/download/v2.4/SHA256SUMS)
<!-- public-release:end -->

**Windows 11 · Portable · Версия 2.4 · Локальная обработка · Предрелизная версия без подписи**

[Deutsch](README.md) · [Русский](README.ru.md) · [English](README.en.md)

![Lecture Companion — русский интерфейс и синтетические примеры](docs/screenshots/app-ru.png)

*Синтетическое демо: без реальной встречи, субтитров и данных участников.*

Lecture Companion помогает следить за IT-лекциями в Microsoft Teams. Программа кратко пересказывает новые субтитры и по запросу объясняет текущий демонстрируемый слайд. Обработка остаётся на компьютере — без API-ключа и облачного резерва.

## Возможности

- Отделяет новые субтитры от прежнего контекста.
- По нажатию снимает свежий кадр демонстрации, а не чата встречи.
- Отвечает сначала на языке лекции, затем на языке интерфейса; совпадающий язык не дублируется.
- Хранит до десяти ответов в перелистываемых карточках; вопросы и разбор слайда доступны сразу.
- Предпочитает совместимый Intel NPU, иначе использует локальный CPU/GPU.
- Поддерживает немецкий, английский и русский для интерфейса и новых ответов.

## Скачать и запустить

Релиз 2.4 опубликован как предварительная версия. Скачай все четыре части ZIP и `JoinPortable.cmd` со [страницы релиза v2.4](https://github.com/popovantondev/LectureCompanion/releases/tag/v2.4) и положи их в одну папку. Запусти `JoinPortable.cmd` двойным щелчком: он проверит размеры частей и SHA-256, ничего не устанавливая. Полностью распакуй собранный ZIP на внутренний SSD, затем запусти `LectureCompanion.exe`. Порядок работы описан в [русской пошаговой инструкции](https://popovantondev.github.io/LectureCompanion/Guide-ru.html).

- [Подробная инструкция на русском](docs/USER_GUIDE.ru.md)
- Windows 11 x64; рекомендуется 32 ГБ ОЗУ. Совместимые драйверы и настольный Teams должны быть уже установлены.
- Первый запуск и загрузка моделей могут занять время. Архив занимает несколько гигабайт.

## Конфиденциальность и ограничения

Субтитры и запрошенные изображения слайдов обрабатываются локально. Программа не использует облачный резерв и не загружает их автоматически. Содержание встречи может включать личные данные: соблюдай правила организации и не публикуй реальные субтитры или скриншоты.

Ответы могут содержать ошибки. Защищённые или свёрнутые окна Teams и обновления программы могут помешать чтению субтитров или слайда. Скорость и совместимость зависят от компьютера и драйверов. EXE не подписан; проверка на чистом втором ПК с Windows ещё не проведена.

## Документация и разработка

[Руководство](docs/USER_GUIDE.ru.md) · [Архитектура и сборка](docs/РАЗРАБОТКА.ru.md) · [Отчёт проверок](VERIFICATION.ru.md) · [Подготовка релиза](PUBLIC-REPOSITORY.md)

Проверки исходников без моделей: `python verify.py --node PATH_TO_NODE`; для интерфейса Windows добавь `--ui`. Синтетическое демо запускается без Teams и моделей — двойным щелчком по `LectureCompanionDemo.exe`.

## Права на использование

Исходный код и изображение робота доступны только для просмотра, без разрешения на повторное использование. Неизменённую официальную EXE разрешается скачать и запускать для личного некоммерческого использования; изменять или распространять её нельзя. На сторонние компоненты распространяются их собственные лицензии и уведомления (`LICENSE`, `THIRD_PARTY.md`). GitHub может разрешать просмотр и форки публичных репозиториев — это не техническая защита от копирования.
