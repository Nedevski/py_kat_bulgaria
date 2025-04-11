## KAT България - Python пакет за програмна проверка за задължения към КАТ

[![PyPI Link](https://img.shields.io/pypi/v/kat_bulgaria?style=flat-square)](https://pypi.org/project/kat-bulgaria/)
![Last release](https://img.shields.io/github/release-date/nedevski/py_kat_bulgaria?style=flat-square)
![License](https://img.shields.io/github/license/nedevski/py_kat_bulgaria?style=flat-square)
![Code size](https://img.shields.io/github/languages/code-size/nedevski/py_kat_bulgaria?style=flat-square)
[![Quality Gate](https://img.shields.io/sonar/quality_gate/Nedevski_py_kat_bulgaria?server=https%3A%2F%2Fsonarcloud.io&style=flat-square)](https://sonarcloud.io/summary/overall?id=Nedevski_py_kat_bulgaria&branch=master)
![Sonar Coverage](https://img.shields.io/sonar/coverage/Nedevski_py_kat_bulgaria?server=https%3A%2F%2Fsonarcloud.io&style=flat-square)

Този пакет позволява да се извършват лесни програмни проверки за налични глоби към [МВР](https://e-uslugi.mvr.bg/services/kat-obligations).

Цялата библиотека е обикновен wrapper около официалната система. Библиотеката **НЕ** запазва или логва вашите данни никъде. Данните са директно предадени на системата на МВР

Причината да създам този пакет е че системата на МВР понякога е нестабилна и хвърля различни видове грешки и timeouts. С негова помощ се стандартизират и валидират отговорите от системата и се извличат данни във формат, готов за употреба, или в случай на грешки - биват извлечени категорияи на грешката и смислено съобщение за грешка.

---

Ако харесвате работата ми, почерпете ме с 1 бира в Ko-Fi:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/nedevski/tip)

---

## Инсталиране

```shell
pip install kat_bulgaria
```

## Примерен скрипт:

Добавил съм примерен работещ скрипт в репото - [`sample_usage_script.py`](sample_usage_script.py).

Преди да се изпълни скрипта, обновете примерните данни с реални ваши такива.

```python
# Проверка за физически лица - лична карта:
obligations = await KatApiClient().get_obligations_individual(
    egn="валидно_егн",
    identifier_type=PersonalDocumentType.NATIONAL_ID,
    identifier="номер_лична_карта"
)
print(f"Брой задължения - ФЛ/ЛК: {len(obligations)}\n")
print(f"Raw JSON: {obligations}\n")
```

```python
# Проверка за физически лица -  шофьорска книжка:
obligations = await KatApiClient().get_obligations_individual(
    egn="валидно_егн",
    identifier_type=PersonalDocumentType.DRIVING_LICENSE,
    identifier="номер_шофьорска_книжка"
)
print(f"Брой задължения - ФЛ/ШК: {len(obligations)}\n")
print(f"Raw JSON: {obligations}\n")
```

```python
# Проверка за юридически лица - лична карта:
obligations = await KatApiClient().get_obligations_business(
    egn="валидно_егн",
    govt_id="номер_лична_карта",
    bulstat="валиден_булстат"
)
print(f"Брой задължения - ЮЛ: {len(obligations)}\n")
print(f"Raw JSON: {obligations}\n")
```

## API отговори:

Примерни API отговори може да бъдат намерени в `/tests/fixtures`.

Старая се да документирам всички API отговори до които имам достъп в [това issue](https://github.com/Nedevski/py_kat_bulgaria/issues/2) с набавяне на по-голям сет тестови данни.

Ако някой има активни глоби, бих се радвал да получа целия JSON отговор от системата на МВР. Можете да го добавите в коментар в issue-то линкнато по-горе.

Можете да си набавите JSON-а, като копирате адреса отдолу и замените `EGN_GOES_HERE` и `LICENSE_GOES_HERE` с вашите ЕГН и номер на шофьорска книжка.

https://e-uslugi.mvr.bg/api/Obligations/AND?obligatedPersonType=1&additinalDataForObligatedPersonType=1&mode=1&obligedPersonIdent=EGN_GOES_HERE&drivingLicenceNumber=LICENSE_GOES_HERE

Силно препоръчително е преди публикуване да заредите JSON-a в тесктов едитор и да редактирате всички ваши лични данни в него.
