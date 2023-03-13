## Підготовка до роботи

експортувати змінну оточення "LD_LIBRARY_PATH". вона повинна містити абсолютний шлях на модуль "modules"
Наприклад:
```bash
export LD_LIBRARY_PATH="/path/to/ua_sign/EUSignCP_20200521/modules"
```
Завантажити серитфікат КНЕП "CACertificates" в папку вказану в параметрі "Path"
[\SOFTWARE\Institute of Informational Technologies\Certificate Authority-1.3\End User\FileStore]
Path=/data/certificates
Можна замінити стандартне розміження сертифікатів, але потрібно зробити це скрізь де вказано "/data/certificates"

Якщо є необхідність підписання файлів за наявності інтернету, потрібно змінити параметри в файлі "osplm.ini"
Параметри CMP-сервера 
\SOFTWARE\Institute of Informational Technologies\Certificate Authority-1.3\End User\CMP
Use=1
CommonName=
Address=ca.informjust.ua ## Дані надавача послуг, в прикладі  АЦСК "ДІЯ" 
Port=80

Параметри протоколу TSP, необхідності отримувати позначки часу під час формування підпису
[\SOFTWARE\Institute of Informational Technologies\Certificate Authority-1.3\End User\TSP]
GetStamps=1
Address=ca.informjust.ua  ## Дані надавача послуг, в прикладі  АЦСК "ДІЯ" 
Port=80


Pcscd является демоном для программы pcsc-lite и для MuscleCard framework. Это менеджер ресурсов, который координирует связь со смарт-картами, с устройствами для их считывания, а также с криптографическими токинами, которые подключены к системе. Обычно pcscd запускается во время загрузки с каталога. Необхідний для роботи з апаратними токенами типу Кристал-1к, Алмаз і тд..


Помилка виникає через відсутність доступу до інтернет (делі незрозумілі)
Сертифікат пошкоджений або не може бути використаний


Якщо немає доступу до інтернету, потрібно завантажити всі сертифікати надавача вручну
Для ПД "Дія" можна завантажити https://ca.diia.gov.ua/certificates

## ТЕСТИ:
```bash
python manage.py test apps.core.tests.ua_sign_test
```