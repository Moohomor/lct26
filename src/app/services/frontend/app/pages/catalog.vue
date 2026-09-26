<script setup lang="ts">
useHead({
  title: 'Каталог роботов',
})
</script>

<template>
    <div>
            <div class="rmc-root">
                <div class="rmc-shell">
                    <section class="rmc-hero">
                        <div><h1 class="rmc-h1">Каталог роботов</h1>
                            <p class="rmc-lead">Подберите идеальную автоматизацию для вашего бизнеса. Анализируйте технические параметры, стоимость и условия от надежных поставщиков в одном месте.</p></div>
                        <div class="rmc-stats">
                            <article class="rmc-stat"><span class="rmc-stat-icon"><svg
                                    xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="lucide lucide-boxes"><path
                                    d="M2.97 12.92A2 2 0 0 0 2 14.63v3.24a2 2 0 0 0 .97 1.71l3 1.8a2 2 0 0 0 2.06 0L12 19v-5.5l-5-3-4.03 2.42Z"></path><path
                                    d="m7 16.5-4.74-2.85"></path><path d="m7 16.5 5-3"></path><path
                                    d="M7 16.5v5.17"></path><path
                                    d="M12 13.5V19l3.97 2.38a2 2 0 0 0 2.06 0l3-1.8a2 2 0 0 0 .97-1.71v-3.24a2 2 0 0 0-.97-1.71L17 10.5l-5 3Z"></path><path
                                    d="m17 16.5-5-3"></path><path d="m17 16.5 4.74-2.85"></path><path
                                    d="M17 16.5v5.17"></path><path
                                    d="M7.97 4.42A2 2 0 0 0 7 6.13v4.37l5 3 5-3V6.13a2 2 0 0 0-.97-1.71l-3-1.8a2 2 0 0 0-2.06 0l-3 1.8Z"></path><path
                                    d="M12 8 7.26 5.15"></path><path d="m12 8 4.74-2.85"></path><path
                                    d="M12 13.5V8"></path></svg></span><span><b>955</b><span class="rmc-stat-label">моделей роботов</span></span>
                            </article>
                            <article class="rmc-stat"><span class="rmc-stat-icon"><svg
                                    xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="lucide lucide-factory"><path
                                    d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"></path><path
                                    d="M17 18h1"></path><path d="M12 18h1"></path><path d="M7 18h1"></path></svg></span><span><b>222</b><span
                                    class="rmc-stat-label">производителей</span></span></article>
                            <article class="rmc-stat"><span class="rmc-stat-icon"><svg
                                    xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="lucide lucide-users"><path
                                    d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7"
                                                                                                 r="4"></circle><path
                                    d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path
                                    d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg></span><span><b>25</b><span
                                    class="rmc-stat-label">поставщиков решений</span></span></article>
                            
                                    <NuxtLink to="/robot-selection" class="rmc-stat rmc-stat-link">
                                        <span
                                    class="rmc-stat-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20"
                                                               viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                                               stroke-width="2" stroke-linecap="round"
                                                               stroke-linejoin="round" class="lucide lucide-zap"><path
                                    d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path></svg></span><span><b
                                    class="rmc-stat-small">Быстрый подбор</b><span class="rmc-stat-label">под ваши задачи</span></span>
                                    </NuxtLink>
                        </div>
                    </section>

                    <div style="margin-top:1rem; margin-bottom: 1rem;;">
                        <label class="rmc-search" data-v-0a7a8d37=""><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-search" data-v-0a7a8d37=""><circle cx="11" cy="11" r="8" data-v-0a7a8d37=""></circle><path d="m21 21-4.3-4.3" data-v-0a7a8d37=""></path></svg><input placeholder="Поиск роботов..." aria-label="Поиск роботов" type="search" data-v-0a7a8d37="">
                    </label>
                    </div>
                    

                    <div class="rmc-filter-panel flex gap-3">
                        <div class="rmc-filter-panel__sidebar_left">
                            <section class="rmc-panel">
                        <div class="rmc-filters"><label class="rmc-field"><span>Категория</span><select>
                            <option value="" selected="selected">Все категории</option>
                            <option value="Промышленные роботы">Промышленные роботы</option>
                            <option value="Сервисные роботы">Сервисные роботы</option>
                            <option value="Коллаборативные роботы">Коллаборативные роботы</option>
                            <option value="Инспекционные роботы">Инспекционные роботы</option>
                            <option value="Уборочные роботы">Уборочные роботы</option>
                            <option value="__other">Другие роботы</option>
                        </select></label><label class="rmc-field"><span>Применение</span><select>
                            <option value="" selected="selected">Все применения</option>
                            <option value="Автомобильная промышленность">Автомобильная промышленность</option>
                            <option value="Аэропорты">Аэропорты</option>
                            <option value="Безопасность">Безопасность</option>
                            <option value="Безопасность и МЧС">Безопасность и МЧС</option>
                            <option value="Водоканалы">Водоканалы</option>
                            <option value="Вокзалы">Вокзалы</option>
                            <option value="Газораспределение">Газораспределение</option>
                            <option value="Геодезия">Геодезия</option>
                            <option value="Горнодобыча">Горнодобыча</option>
                            <option value="Городская инфраструктура">Городская инфраструктура</option>
                            <option value="Госсектор">Госсектор</option>
                            <option value="Гостиничный бизнес">Гостиничный бизнес</option>
                            <option value="Железнодорожный транспорт">Железнодорожный транспорт</option>
                            <option value="ЖКХ">ЖКХ</option>
                            <option value="ЖКХ и благоустройство">ЖКХ и благоустройство</option>
                            <option value="ЖКХ и городская среда">ЖКХ и городская среда</option>
                            <option value="Здравоохранение">Здравоохранение</option>
                            <option value="Инженерные системы">Инженерные системы</option>
                            <option value="Инспекция">Инспекция</option>
                            <option value="Инфраструктура">Инфраструктура</option>
                            <option value="Клининг">Клининг</option>
                            <option value="Коммерческая недвижимость">Коммерческая недвижимость</option>
                            <option value="Лесное хозяйство">Лесное хозяйство</option>
                            <option value="Логистика">Логистика</option>
                            <option value="Логистика и склады">Логистика и склады</option>
                            <option value="Медицина">Медицина</option>
                            <option value="Наука">Наука</option>
                            <option value="Нефтегаз">Нефтегаз</option>
                            <option value="Образование">Образование</option>
                            <option value="Образование и мероприятия">Образование и мероприятия</option>
                            <option value="Образование и наука">Образование и наука</option>
                            <option value="Отделочные работы">Отделочные работы</option>
                            <option value="Офисы и бизнес-центры">Офисы и бизнес-центры</option>
                            <option value="Проектирование">Проектирование</option>
                            <option value="Производство">Производство</option>
                            <option value="Промышленное производство">Промышленное производство</option>
                            <option value="Промышленность">Промышленность</option>
                            <option value="Промышленные роботы">Промышленные роботы</option>
                            <option value="Промышленные территории">Промышленные территории</option>
                            <option value="Ритейл">Ритейл</option>
                            <option value="Сельское хозяйство">Сельское хозяйство</option>
                            <option value="Сервис">Сервис</option>
                            <option value="Сервисные роботы">Сервисные роботы</option>
                            <option value="Складская логистика">Складская логистика</option>
                            <option value="Склады">Склады</option>
                            <option value="Спортивные объекты">Спортивные объекты</option>
                            <option value="Строительство">Строительство</option>
                            <option value="Теплоснабжение">Теплоснабжение</option>
                            <option value="Технопарки">Технопарки</option>
                            <option value="Торговля и услуги">Торговля и услуги</option>
                            <option value="Транспорт">Транспорт</option>
                            <option value="Транспорт и вокзалы">Транспорт и вокзалы</option>
                            <option value="Транспорт и логистика">Транспорт и логистика</option>
                            <option value="Транспортная инфраструктура">Транспортная инфраструктура</option>
                            <option value="ТЦ и ритейл">ТЦ и ритейл</option>
                            <option value="Управление коммерческой недвижимостью">Управление коммерческой
                                недвижимостью
                            </option>
                            <option value="Химия">Химия</option>
                            <option value="Эксплуатация недвижимости">Эксплуатация недвижимости</option>
                            <option value="Электромонтаж">Электромонтаж</option>
                            <option value="Энергетика">Энергетика</option>
                            <option value="Энергетика и нефтегаз">Энергетика и нефтегаз</option>
                            <option value="E-commerce">E-commerce</option>
                            <option value="Facility management">Facility management</option>
                            <option value="HoReCa">HoReCa</option>
                            <option value="HoReCa и общепит">HoReCa и общепит</option>
                        </select></label><label class="rmc-field"><span>Производитель</span><select>
                            <option value="" selected="selected">Все производители</option>
                            <option value="Аврора Роботикс">Аврора Роботикс</option>
                            <option value="Автомакон">Автомакон</option>
                            <option value="Агробит">Агробит</option>
                            <option value="Агромаш">Агромаш</option>
                            <option value="Айдол">Айдол</option>
                            <option value="Альбатрос">Альбатрос</option>
                            <option value="АМТ">АМТ</option>
                            <option value="АМТ Н.В">АМТ Н.В</option>
                            <option value="АО «168robotics»">АО «168robotics»</option>
                            <option value="АО «НИИАС»">АО «НИИАС»</option>
                            <option value="АО «НПО «Андроидная техника»">АО «НПО «Андроидная техника»</option>
                            <option value="АРС Смарт Роботикс">АРС Смарт Роботикс</option>
                            <option value="Астрамис">Астрамис</option>
                            <option value="Атоммаш">Атоммаш</option>
                            <option value="Аэродин">Аэродин</option>
                            <option value="Аэромакс">Аэромакс</option>
                            <option value="БалоРоботс (BALOROBOTS)">БалоРоботс (BALOROBOTS)</option>
                            <option value="БиАйДи Технолоджис Рус (Birbi)">БиАйДи Технолоджис Рус (Birbi)</option>
                            <option value="Битроботикс">Битроботикс</option>
                            <option value="Валдай роботы">Валдай роботы</option>
                            <option value="Вейбот Автомакон Роботикс">Вейбот Автомакон Роботикс</option>
                            <option value="Вирсайн инновации">Вирсайн инновации</option>
                            <option value="Газпром Нефть">Газпром Нефть</option>
                            <option value="ГК «Беспилотные системы»">ГК «Беспилотные системы»</option>
                            <option value="ГК «Геоскан»">ГК «Геоскан»</option>
                            <option value="ГК «ДТС»">ГК «ДТС»</option>
                            <option value="ГК Тихие Крылья">ГК Тихие Крылья</option>
                            <option value="ГКМП (НПО «ГКМП»)">ГКМП (НПО «ГКМП»)</option>
                            <option value="Гумич-РТК">Гумич-РТК</option>
                            <option value="ДЕМОРОБОТ">ДЕМОРОБОТ</option>
                            <option value="ДиКом-Сервис">ДиКом-Сервис</option>
                            <option value="Донской государственный технический университет (ДГТУ)">Донской
                                государственный технический университет (ДГТУ)
                            </option>
                            <option value="ДСТ-УРАЛ">ДСТ-УРАЛ</option>
                            <option value="Кабардино-Балкарский государственный университет имени Х.М. Бербекова">
                                Кабардино-Балкарский государственный университет имени Х.М. Бербекова
                            </option>
                            <option value="Карфидов Лаб">Карфидов Лаб</option>
                            <option value="КБ-интеграл">КБ-интеграл</option>
                            <option value="Клеверкоптер">Клеверкоптер</option>
                            <option value="Коботы">Коботы</option>
                            <option value="Коруфайер">Коруфайер</option>
                            <option value="Кью Групп / Qubot">Кью Групп / Qubot</option>
                            <option value="Лаборатория Будущего">Лаборатория Будущего</option>
                            <option value="ЛМТ">ЛМТ</option>
                            <option value="МАИ">МАИ</option>
                            <option value="Метровагонмаш">Метровагонмаш</option>
                            <option value="Миррико">Миррико</option>
                            <option value="МОРОС">МОРОС</option>
                            <option value="МФТИ">МФТИ</option>
                            <option value="НИУ ВШЭ">НИУ ВШЭ</option>
                            <option value="Новосибирский госуниверситет">Новосибирский госуниверситет</option>
                            <option value="ОДК-СТАР">ОДК-СТАР</option>
                            <option value="Океанос">Океанос</option>
                            <option value="ООО «Автономика»">ООО «Автономика»</option>
                            <option value="ООО «Вистарос»">ООО «Вистарос»</option>
                            <option value="ООО «Диаконт»">ООО «Диаконт»</option>
                            <option value="ООО «Тьюбот»">ООО «Тьюбот»</option>
                            <option value="ООО «Юникон»">ООО «Юникон»</option>
                            <option value="Пермский Политех">Пермский Политех</option>
                            <option value="ПНИПУ">ПНИПУ</option>
                            <option value="Прикладная Робототехника">Прикладная Робототехника</option>
                            <option value="Промтехника-Приволжье">Промтехника-Приволжье</option>
                            <option value="ПТЗ">ПТЗ</option>
                            <option value="РАСКАТ">РАСКАТ</option>
                            <option value="Робин Гуд Роботикс">Робин Гуд Роботикс</option>
                            <option value="РОБО">РОБО</option>
                            <option value="Робокс">Робокс</option>
                            <option value="РобоПро">РобоПро</option>
                            <option value="РобоСиВи">РобоСиВи</option>
                            <option value="Робот">Робот</option>
                            <option value="Росатом">Росатом</option>
                            <option value="Сбер">Сбер</option>
                            <option value="Свеза">Свеза</option>
                            <option value="Семаргл">Семаргл</option>
                            <option value="СМД">СМД</option>
                            <option value="СМП Роботикс">СМП Роботикс</option>
                            <option value="ТАРИС">ТАРИС</option>
                            <option value="Транспорт будущего">Транспорт будущего</option>
                            <option value="Транспортные системы">Транспортные системы</option>
                            <option value="Умный сервис (Интегратор)">Умный сервис (Интегратор)</option>
                            <option value="Университет Иннополис">Университет Иннополис</option>
                            <option value="Финансовый университет при Правительстве РФ и ФНАЦ ВИМ">Финансовый
                                университет при Правительстве РФ и ФНАЦ ВИМ
                            </option>
                            <option value="Эвокарго">Эвокарго</option>
                            <option value="Эйдос Робототехника">Эйдос Робототехника</option>
                            <option value="Яндекс">Яндекс</option>
                            <option value="Яндекс Роботикс">Яндекс Роботикс</option>
                            <option value="ABB">ABB</option>
                            <option value="Adam">Adam</option>
                            <option value="AgiBot">AgiBot</option>
                            <option value="AgileX Robotics">AgileX Robotics</option>
                            <option value="Agility Robotics">Agility Robotics</option>
                            <option value="Aido">Aido</option>
                            <option value="Aldebaran (SoftBank Robotics)">Aldebaran (SoftBank Robotics)</option>
                            <option value="Alpha Robotics">Alpha Robotics</option>
                            <option value="ANYbotics">ANYbotics</option>
                            <option value="Apptronik">Apptronik</option>
                            <option value="Aripix robotics">Aripix robotics</option>
                            <option value="Astribot">Astribot</option>
                            <option value="Avatar Intelligent Equipment">Avatar Intelligent Equipment</option>
                            <option value="Avidbots">Avidbots</option>
                            <option value="Beijing Fangshi Robotics">Beijing Fangshi Robotics</option>
                            <option value="Boardwalk Robotics">Boardwalk Robotics</option>
                            <option value="Booster Robotics">Booster Robotics</option>
                            <option value="Boston Dynamics">Boston Dynamics</option>
                            <option value="Canvas">Canvas</option>
                            <option value="CITIC">CITIC</option>
                            <option value="CloudMinds">CloudMinds</option>
                            <option value="Cognitive Pilot">Cognitive Pilot</option>
                            <option value="Cyberstein Robots">Cyberstein Robots</option>
                            <option value="Deep Robotics">Deep Robotics</option>
                            <option value="DJI Enterprise">DJI Enterprise</option>
                            <option value="Dobot">Dobot</option>
                            <option value="Doosan Robotics">Doosan Robotics</option>
                            <option value="DronesHub">DronesHub</option>
                            <option value="Dusty Robotics">Dusty Robotics</option>
                            <option value="Ecoplatform">Ecoplatform</option>
                            <option value="Electromotive">Electromotive</option>
                            <option value="Elephant Robotics">Elephant Robotics</option>
                            <option value="EngineAI">EngineAI</option>
                            <option value="Engineered Arts">Engineered Arts</option>
                            <option value="Envirosight LLC">Envirosight LLC</option>
                            <option value="FANUC">FANUC</option>
                            <option value="Fibbee">Fibbee</option>
                            <option value="Flyability">Flyability</option>
                            <option value="Fourier Intelligence">Fourier Intelligence</option>
                            <option value="Galbot">Galbot</option>
                            <option value="Gausium">Gausium</option>
                            <option value="Glory Air (Глори Эйр)">Glory Air (Глори Эйр)</option>
                            <option value="HAOYUNMA">HAOYUNMA</option>
                            <option value="HausBots">HausBots</option>
                            <option value="Hilti AG">Hilti AG</option>
                            <option value="Hiwonder">Hiwonder</option>
                            <option value="HMND">HMND</option>
                            <option value="Husqvarna">Husqvarna</option>
                            <option value="Ikitbot">Ikitbot</option>
                            <option value="Inchbot">Inchbot</option>
                            <option value="INOVANCE">INOVANCE</option>
                            <option value="iPEK International">iPEK International</option>
                            <option value="JAKA">JAKA</option>
                            <option value="Keenon Robotics">Keenon Robotics</option>
                            <option value="Kepler Robotics">Kepler Robotics</option>
                            <option value="Kinova">Kinova</option>
                            <option value="KUKA">KUKA</option>
                            <option value="MagicLab">MagicLab</option>
                            <option value="Mentee Robotics">Mentee Robotics</option>
                            <option value="NavBot">NavBot</option>
                            <option value="Navio">Navio</option>
                            <option value="NavVis">NavVis</option>
                            <option value="Neura Robotics">Neura Robotics</option>
                            <option value="Nilfisk">Nilfisk</option>
                            <option value="Noetix Robotics">Noetix Robotics</option>
                            <option value="Okibo">Okibo</option>
                            <option value="OrionStar">OrionStar</option>
                            <option value="PadBot">PadBot</option>
                            <option value="Paxini">Paxini</option>
                            <option value="Petoi">Petoi</option>
                            <option value="Promobot">Promobot</option>
                            <option value="Pudu Robotics">Pudu Robotics</option>
                            <option value="R2B / Robots to Business">R2B / Robots to Business</option>
                            <option value="Reeman">Reeman</option>
                            <option value="ROBCOM">ROBCOM</option>
                            <option value="Robokos">Robokos</option>
                            <option value="Ronavi Robotics">Ronavi Robotics</option>
                            <option value="Sanbot">Sanbot</option>
                            <option value="Sanctuary AI">Sanctuary AI</option>
                            <option value="Shanghai WEIBUILD Technology">Shanghai WEIBUILD Technology</option>
                            <option value="Shenzhen Legend Robot Technology">Shenzhen Legend Robot Technology</option>
                            <option value="Skyline Robotics">Skyline Robotics</option>
                            <option value="SoloCoffee">SoloCoffee</option>
                            <option value="Tesla">Tesla</option>
                            <option value="Tokyo Robotics">Tokyo Robotics</option>
                            <option value="Tron">Tron</option>
                            <option value="TUSKROBOTS">TUSKROBOTS</option>
                            <option value="UBtech">UBtech</option>
                            <option value="UBTECH Robotics">UBTECH Robotics</option>
                            <option value="UFACTORY">UFACTORY</option>
                            <option value="Unitree Robotics">Unitree Robotics</option>
                            <option value="Verobotics">Verobotics</option>
                            <option value="VIPER">VIPER</option>
                            <option value="VOSTOK">VOSTOK</option>
                            <option value="VV Technologies (ООО «В в Технологическая компания»)">VV Technologies (ООО «В
                                в Технологическая компания»)
                            </option>
                            <option value="Weilan">Weilan</option>
                            <option value="Wenming Machinery (WM Machinery)">Wenming Machinery (WM Machinery)</option>
                            <option value="Wingtra AG">Wingtra AG</option>
                            <option value="XGO">XGO</option>
                            <option value="XiaoR Geek">XiaoR Geek</option>
                            <option value="XPeng Robotics">XPeng Robotics</option>
                            <option value="YACU AI / YaCu Robotics">YACU AI / YaCu Robotics</option>
                            <option value="Yarbo">Yarbo</option>
                            <option value="Yaskawa Motoman">Yaskawa Motoman</option>
                        </select></label>
                            <button type="button" class="rmc-more-btn" aria-expanded="false">
                                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                                     fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                     stroke-linejoin="round" class="lucide lucide-sliders-horizontal">
                                    <line x1="21" x2="14" y1="4" y2="4"></line>
                                    <line x1="10" x2="3" y1="4" y2="4"></line>
                                    <line x1="21" x2="12" y1="12" y2="12"></line>
                                    <line x1="8" x2="3" y1="12" y2="12"></line>
                                    <line x1="21" x2="16" y1="20" y2="20"></line>
                                    <line x1="12" x2="3" y1="20" y2="20"></line>
                                    <line x1="14" x2="14" y1="2" y2="6"></line>
                                    <line x1="8" x2="8" y1="10" y2="14"></line>
                                    <line x1="16" x2="16" y1="18" y2="22"></line>
                                </svg>
                                Ещё фильтры
                            </button>
                        </div>
                        <div class="rmc-tabs">
                            <button type="button" aria-pressed="true" class="rmc-tab rmc-tab-active"><span
                                    class="rmc-tab-icon"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16"
                                                              viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                                              stroke-width="2" stroke-linecap="round"
                                                              stroke-linejoin="round" class="lucide lucide-layout-grid"><rect
                                    width="7" height="7" x="3" y="3" rx="1"></rect><rect width="7" height="7" x="14"
                                                                                         y="3" rx="1"></rect><rect
                                    width="7" height="7" x="14" y="14" rx="1"></rect><rect width="7" height="7" x="3"
                                                                                           y="14"
                                                                                           rx="1"></rect></svg></span><span
                                    class="rmc-tab-text">Все роботы<small>955</small></span></button>
                            <button type="button" aria-pressed="false" class="rmc-tab"><span class="rmc-tab-icon"><svg
                                    xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="lucide lucide-store"><path
                                    d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path><path
                                    d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path><path
                                    d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path><path d="M2 7h20"></path><path
                                    d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path></svg></span><span
                                    class="rmc-tab-text">Промышленные роботы<small>267</small></span></button>
                            <button type="button" aria-pressed="false" class="rmc-tab"><span class="rmc-tab-icon"><svg
                                    xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="lucide lucide-store"><path
                                    d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path><path
                                    d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path><path
                                    d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path><path d="M2 7h20"></path><path
                                    d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path></svg></span><span
                                    class="rmc-tab-text">Строительные роботы<small>190</small></span></button>
                            <button type="button" aria-pressed="false" class="rmc-tab"><span class="rmc-tab-icon"><svg
                                    xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="lucide lucide-store"><path
                                    d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path><path
                                    d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path><path
                                    d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path><path d="M2 7h20"></path><path
                                    d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path></svg></span><span
                                    class="rmc-tab-text">Транспортнологистические роботы<small>88</small></span></button>
                            <button type="button" aria-pressed="false" class="rmc-tab"><span class="rmc-tab-icon"><svg
                                    xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="lucide lucide-store"><path
                                    d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path><path
                                    d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path><path
                                    d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path><path d="M2 7h20"></path><path
                                    d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path></svg></span><span
                                    class="rmc-tab-text">ТЭК роботы<small>85</small></span></button>
                        </div>
                    </section>
                        </div>

                        <div>
                            <div class="rmc-resulthead">
                        <div>Найдено роботов: <b>955</b></div>
                        <div class="rmc-resultctl">Сортировать:<select aria-label="Сортировка">
                            <option value="popular" selected="selected">По популярности</option>
                            <option value="low">Цена ↑</option>
                            <option value="high">Цена ↓</option>
                            <option value="new">Сначала новые</option>
                        </select>
                            <button type="button" aria-label="Плитки" aria-pressed="true" class="rmc-v rmc-v-active">
                                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                                     fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                     stroke-linejoin="round" class="lucide lucide-layout-grid">
                                    <rect width="7" height="7" x="3" y="3" rx="1"></rect>
                                    <rect width="7" height="7" x="14" y="3" rx="1"></rect>
                                    <rect width="7" height="7" x="14" y="14" rx="1"></rect>
                                    <rect width="7" height="7" x="3" y="14" rx="1"></rect>
                                </svg>
                            </button>
                            <button type="button" aria-label="Список" aria-pressed="false" class="rmc-v">
                                <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                                     fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                     stroke-linejoin="round" class="lucide lucide-list">
                                    <path d="M3 12h.01"></path>
                                    <path d="M3 18h.01"></path>
                                    <path d="M3 6h.01"></path>
                                    <path d="M8 12h13"></path>
                                    <path d="M8 18h13"></path>
                                    <path d="M8 6h13"></path>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <section class="rmc-grid">
                        <article class="rmc-card"><span class="rmc-badge">★ Хит продаж</span><span class="rmc-fav"><button
                                type="button" aria-pressed="false" aria-label="Добавить PUDU CC1 Pro к сравнению"
                                title="Добавить к сравнению"
                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="PUDU CC1 Pro" loading="lazy" decoding="async"
                                                         data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_035.avif 384w, ~/assets/img/image-1_041.avif 640w, ~/assets/img/image-1_003.avif 750w, ~/assets/img/image-1_019.avif 828w, ~/assets/img/image-1_012.avif 1080w, ~/assets/img/image-1_016.avif 1200w, ~/assets/img/image-1_020.avif 1920w, ~/assets/img/image-1_053.avif 2048w, ~/assets/img/image-1_024.avif 3840w"
                                                         src="~/assets/img/image-1_024.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch"
                                                         href="/robots/pudu-cc1-pro">PUDU CC1
                                Pro</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Автономный
                                    моечный робот премиум-класса с ИИ-распознаванием загрязнений и
                                    навигацией VSLAM+ для профессиональной уборки коммерческих помещений.</p>
                                <div class="rmc-tags">
                                    <span>Уборочные роботы</span><span>Ритейл</span><span>HoReCa</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">Цена по запросу</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 1 поставщика ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                        <article class="rmc-card"><span class="rmc-badge">★ Хит продаж</span><span class="rmc-fav"><button
                                type="button" aria-pressed="false" aria-label="Добавить Pudu D5 к сравнению"
                                title="Добавить к сравнению"
                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="Pudu D5" loading="lazy" decoding="async" data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_052.avif 384w, ~/assets/img/image-1_045.avif 640w, ~/assets/img/image-1_046.avif 750w, ~/assets/img/image-1_032.avif 828w, ~/assets/img/image-1.avif 1080w, ~/assets/img/image-1_022.avif 1200w, ~/assets/img/image-1_031.avif 1920w, ~/assets/img/image-1_029.avif 2048w, ~/assets/img/image-1_014.avif 3840w"
                                                         src="~/assets/img/image-1_014.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch" href="/robots/pudu-d5">Pudu
                                D5</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Pudu
                                    D5 — индустриальный автономный робопёс, который самостоятельно
                                    ориентируется в пространстве, безопасно движется по сложным маршрутам,
                                    взаимодействует с людьми голосом и жестам</p>
                                <div class="rmc-tags"><span>Инспекционные роботы</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">Цена по запросу</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 1 поставщика ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                        <article class="rmc-card"><span class="rmc-fav"><button type="button" aria-pressed="false"
                                                                                aria-label="Добавить Робот доставщик Pudu HolaBot к сравнению"
                                                                                title="Добавить к сравнению"
                                                                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="Робот доставщик Pudu HolaBot" loading="lazy"
                                                         decoding="async" data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_036.avif 384w, ~/assets/img/image-1_050.avif 640w, ~/assets/img/image-1_017.avif 750w, ~/assets/img/image-1_023.avif 828w, ~/assets/img/image-1_009.avif 1080w, ~/assets/img/image-1_044.avif 1200w, ~/assets/img/image-1_034.avif 1920w, ~/assets/img/image-1_054.avif 2048w, ~/assets/img/image-1_025.avif 3840w"
                                                         src="~/assets/img/image-1_025.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch"
                                                         href="/robots/robot-dostavshik-pudu-holabot">Робот
                                доставщик Pudu HolaBot</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Pudu
                                    Holabot – интеллектуальный робот-помощник, способный выполнять уборку,
                                    доставку товаров и другие сервисные задачи для автоматизации бытовых и
                                    коммерческих процессов.</p>
                                <div class="rmc-tags"><span>Сервисные роботы</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">от 783&nbsp;576 ₽</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 3 поставщиков ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                        <article class="rmc-card"><span class="rmc-fav"><button type="button" aria-pressed="false"
                                                                                aria-label="Добавить Робот официант Pudu Bella Bot Pro к сравнению"
                                                                                title="Добавить к сравнению"
                                                                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="Робот официант Pudu Bella Bot Pro" loading="lazy"
                                                         decoding="async" data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_033.avif 384w, ~/assets/img/image-1_040.avif 640w, ~/assets/img/image-1_028.avif 750w, ~/assets/img/image-1_018.avif 828w, ~/assets/img/image-1_011.avif 1080w, ~/assets/img/image-1_048.avif 1200w, ~/assets/img/image-1_047.avif 1920w, ~/assets/img/image-1_039.avif 2048w, ~/assets/img/image-1_015.avif 3840w"
                                                         src="~/assets/img/image-1_015.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch"
                                                         href="/robots/robot-oficiant-pudu-bella-bot-pro">Робот
                                официант Pudu Bella Bot Pro</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Pudu
                                    BellaBot помогает автоматизировать процесс доставки заказов внутри
                                    заведения, снижая нагрузку на персонал и ускоряя обслуживание клиентов.</p>
                                <div class="rmc-tags"><span>Сервисные роботы</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">от 940&nbsp;291 ₽</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 3 поставщиков ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                        <article class="rmc-card"><span class="rmc-fav"><button type="button" aria-pressed="false"
                                                                                aria-label="Добавить Робот уборщик Pudu MT1 к сравнению"
                                                                                title="Добавить к сравнению"
                                                                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="Робот уборщик Pudu MT1" loading="lazy" decoding="async"
                                                         data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_042.avif 384w, ~/assets/img/image-1_037.avif 640w, ~/assets/img/image-1_006.avif 750w, ~/assets/img/image-1_027.avif 828w, ~/assets/img/image-1_005.avif 1080w, ~/assets/img/image-1_010.avif 1200w, ~/assets/img/image-1_026.avif 1920w, ~/assets/img/image-1_013.avif 2048w, ~/assets/img/image-1_038.avif 3840w"
                                                         src="~/assets/img/image-1_038.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch"
                                                         href="/robots/robot-uborshik-pudu-mt1">Робот
                                уборщик Pudu MT1</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Pudu MT1 — это высокотехнологичный, автономный робот для сухой
                                    уборки, управляемый искусственным интеллектом.</p>
                                <div class="rmc-tags"><span>Сервисные роботы</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">от 1&nbsp;527&nbsp;973 ₽</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 3 поставщиков ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                        <article class="rmc-card"><span class="rmc-fav"><button type="button" aria-pressed="false"
                                                                                aria-label="Добавить Робот уборщик Pudu MT1VAC к сравнению"
                                                                                title="Добавить к сравнению"
                                                                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="Робот уборщик Pudu MT1VAC" loading="lazy" decoding="async"
                                                         data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_043.avif 384w, ~/assets/img/image-1_004.avif 640w, ~/assets/img/image-1_049.avif 750w, ~/assets/img/image-1_021.avif 828w, ~/assets/img/image-1_002.avif 1080w, ~/assets/img/image-1_008.avif 1200w, ~/assets/img/image-1_051.avif 1920w, ~/assets/img/image-1_030.avif 2048w, ~/assets/img/image-1_007.avif 3840w"
                                                         src="~/assets/img/image-1_007.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch"
                                                         href="/robots/robot-uborshik-pudu-mt1vac">Робот
                                уборщик Pudu MT1VAC</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Коммерческий робот-пылесос PUDU MT1 Vac с двойной системой
                                    всасывания, HEPA-фильтрацией и AI-навигацией.</p>
                                <div class="rmc-tags"><span>Сервисные роботы</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">от 1&nbsp;000&nbsp;000 ₽</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 3 поставщиков ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                        <article class="rmc-card"><span class="rmc-badge">★ Хит продаж</span><span class="rmc-fav"><button
                                type="button" aria-pressed="false" aria-label="Добавить PUDU CC1 Pro к сравнению"
                                title="Добавить к сравнению"
                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="PUDU CC1 Pro" loading="lazy" decoding="async"
                                                         data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_035.avif 384w, ~/assets/img/image-1_041.avif 640w, ~/assets/img/image-1_003.avif 750w, ~/assets/img/image-1_019.avif 828w, ~/assets/img/image-1_012.avif 1080w, ~/assets/img/image-1_016.avif 1200w, ~/assets/img/image-1_020.avif 1920w, ~/assets/img/image-1_053.avif 2048w, ~/assets/img/image-1_024.avif 3840w"
                                                         src="~/assets/img/image-1_024.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch"
                                                         href="/robots/pudu-cc1-pro">PUDU CC1
                                Pro</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Автономный
                                    моечный робот премиум-класса с ИИ-распознаванием загрязнений и
                                    навигацией VSLAM+ для профессиональной уборки коммерческих помещений.</p>
                                <div class="rmc-tags">
                                    <span>Уборочные роботы</span><span>Ритейл</span><span>HoReCa</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">Цена по запросу</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 1 поставщика ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                        <article class="rmc-card"><span class="rmc-badge">★ Хит продаж</span><span class="rmc-fav"><button
                                type="button" aria-pressed="false" aria-label="Добавить Pudu D5 к сравнению"
                                title="Добавить к сравнению"
                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="Pudu D5" loading="lazy" decoding="async" data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_052.avif 384w, ~/assets/img/image-1_045.avif 640w, ~/assets/img/image-1_046.avif 750w, ~/assets/img/image-1_032.avif 828w, ~/assets/img/image-1.avif 1080w, ~/assets/img/image-1_022.avif 1200w, ~/assets/img/image-1_031.avif 1920w, ~/assets/img/image-1_029.avif 2048w, ~/assets/img/image-1_014.avif 3840w"
                                                         src="~/assets/img/image-1_014.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch" href="/robots/pudu-d5">Pudu
                                D5</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Pudu
                                    D5 — индустриальный автономный робопёс, который самостоятельно
                                    ориентируется в пространстве, безопасно движется по сложным маршрутам,
                                    взаимодействует с людьми голосом и жестам</p>
                                <div class="rmc-tags"><span>Инспекционные роботы</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">Цена по запросу</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 1 поставщика ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                        <article class="rmc-card"><span class="rmc-fav"><button type="button" aria-pressed="false"
                                                                                aria-label="Добавить Робот доставщик Pudu HolaBot к сравнению"
                                                                                title="Добавить к сравнению"
                                                                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="Робот доставщик Pudu HolaBot" loading="lazy"
                                                         decoding="async" data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_036.avif 384w, ~/assets/img/image-1_050.avif 640w, ~/assets/img/image-1_017.avif 750w, ~/assets/img/image-1_023.avif 828w, ~/assets/img/image-1_009.avif 1080w, ~/assets/img/image-1_044.avif 1200w, ~/assets/img/image-1_034.avif 1920w, ~/assets/img/image-1_054.avif 2048w, ~/assets/img/image-1_025.avif 3840w"
                                                         src="~/assets/img/image-1_025.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch"
                                                         href="/robots/robot-dostavshik-pudu-holabot">Робот
                                доставщик Pudu HolaBot</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Pudu
                                    Holabot – интеллектуальный робот-помощник, способный выполнять уборку,
                                    доставку товаров и другие сервисные задачи для автоматизации бытовых и
                                    коммерческих процессов.</p>
                                <div class="rmc-tags"><span>Сервисные роботы</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">от 783&nbsp;576 ₽</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 3 поставщиков ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                        <article class="rmc-card"><span class="rmc-fav"><button type="button" aria-pressed="false"
                                                                                aria-label="Добавить Робот официант Pudu Bella Bot Pro к сравнению"
                                                                                title="Добавить к сравнению"
                                                                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="Робот официант Pudu Bella Bot Pro" loading="lazy"
                                                         decoding="async" data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_033.avif 384w, ~/assets/img/image-1_040.avif 640w, ~/assets/img/image-1_028.avif 750w, ~/assets/img/image-1_018.avif 828w, ~/assets/img/image-1_011.avif 1080w, ~/assets/img/image-1_048.avif 1200w, ~/assets/img/image-1_047.avif 1920w, ~/assets/img/image-1_039.avif 2048w, ~/assets/img/image-1_015.avif 3840w"
                                                         src="~/assets/img/image-1_015.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch"
                                                         href="/robots/robot-oficiant-pudu-bella-bot-pro">Робот
                                официант Pudu Bella Bot Pro</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Pudu
                                    BellaBot помогает автоматизировать процесс доставки заказов внутри
                                    заведения, снижая нагрузку на персонал и ускоряя обслуживание клиентов.</p>
                                <div class="rmc-tags"><span>Сервисные роботы</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">от 940&nbsp;291 ₽</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 3 поставщиков ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                        <article class="rmc-card"><span class="rmc-fav"><button type="button" aria-pressed="false"
                                                                                aria-label="Добавить Робот уборщик Pudu MT1 к сравнению"
                                                                                title="Добавить к сравнению"
                                                                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="Робот уборщик Pudu MT1" loading="lazy" decoding="async"
                                                         data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_042.avif 384w, ~/assets/img/image-1_037.avif 640w, ~/assets/img/image-1_006.avif 750w, ~/assets/img/image-1_027.avif 828w, ~/assets/img/image-1_005.avif 1080w, ~/assets/img/image-1_010.avif 1200w, ~/assets/img/image-1_026.avif 1920w, ~/assets/img/image-1_013.avif 2048w, ~/assets/img/image-1_038.avif 3840w"
                                                         src="~/assets/img/image-1_038.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch"
                                                         href="/robots/robot-uborshik-pudu-mt1">Робот
                                уборщик Pudu MT1</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Pudu MT1 — это высокотехнологичный, автономный робот для сухой
                                    уборки, управляемый искусственным интеллектом.</p>
                                <div class="rmc-tags"><span>Сервисные роботы</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">от 1&nbsp;527&nbsp;973 ₽</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 3 поставщиков ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                        <article class="rmc-card"><span class="rmc-fav"><button type="button" aria-pressed="false"
                                                                                aria-label="Добавить Робот уборщик Pudu MT1VAC к сравнению"
                                                                                title="Добавить к сравнению"
                                                                                class="flex items-center justify-center h-7 rounded border transition-all border-white/70 bg-white/60 text-[#0568FF] hover:bg-white !h-[28px] w-[28px] !rounded-[8px]"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-git-compare h-3.5 w-3.5"><circle cx="18"
                                                                                                              cy="18"
                                                                                                              r="3"></circle><circle
                                cx="6" cy="6" r="3"></circle><path d="M13 6h3a2 2 0 0 1 2 2v7"></path><path
                                d="M11 18H8a2 2 0 0 1-2-2V9"></path></svg></button><button
                                title="Добавить в вотчлист (Следить)"
                                class="flex items-center justify-center h-7 rounded border transition-all text-faint hover:text-sub hover:border-line !h-[28px] w-[28px] !rounded-[8px] border-white/70 bg-white/60"><svg
                                xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                stroke-linejoin="round" class="lucide lucide-bell h-3 w-3"><path
                                d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"></path><path
                                d="M10.3 21a1.94 1.94 0 0 0 3.4 0"></path></svg></button></span>
                            <div class="rmc-visual"><img alt="Робот уборщик Pudu MT1VAC" loading="lazy" decoding="async"
                                                         data-nimg="fill"
                                                         style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent;"
                                                         sizes="(max-width: 720px) 100vw, (max-width: 1100px) 50vw, 460px"
                                                         srcset="~/assets/img/image-1_043.avif 384w, ~/assets/img/image-1_004.avif 640w, ~/assets/img/image-1_049.avif 750w, ~/assets/img/image-1_021.avif 828w, ~/assets/img/image-1_002.avif 1080w, ~/assets/img/image-1_008.avif 1200w, ~/assets/img/image-1_051.avif 1920w, ~/assets/img/image-1_030.avif 2048w, ~/assets/img/image-1_007.avif 3840w"
                                                         src="~/assets/img/image-1_007.avif"></div>
                            <div class="rmc-body"><h3><a class="rmc-stretch"
                                                         href="/robots/robot-uborshik-pudu-mt1vac">Робот
                                уборщик Pudu MT1VAC</a></h3>
                                <p class="rmc-maker">Pudu Robotics · Китай</p>
                                <p class="rmc-desc">Коммерческий робот-пылесос PUDU MT1 Vac с двойной системой
                                    всасывания, HEPA-фильтрацией и AI-навигацией.</p>
                                <div class="rmc-tags"><span>Сервисные роботы</span></div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">от 1&nbsp;000&nbsp;000 ₽</div>
                                        <div class="rmc-sup">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="11" height="11"
                                                 viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                                 stroke-linecap="round" stroke-linejoin="round"
                                                 class="lucide lucide-store">
                                                <path d="m2 7 4.41-4.41A2 2 0 0 1 7.83 2h8.34a2 2 0 0 1 1.42.59L22 7"></path>
                                                <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
                                                <path d="M15 22v-4a2 2 0 0 0-2-2h-2a2 2 0 0 0-2 2v4"></path>
                                                <path d="M2 7h20"></path>
                                                <path d="M22 7v3a2 2 0 0 1-2 2a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 16 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 12 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 8 12a2.7 2.7 0 0 1-1.59-.63.7.7 0 0 0-.82 0A2.7 2.7 0 0 1 4 12a2 2 0 0 1-2-2V7"></path>
                                            </svg>
                                            от 3 поставщиков ›
                                        </div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                 width="14" height="14"
                                                                                 viewBox="0 0 24 24" fill="none"
                                                                                 stroke="currentColor" stroke-width="2"
                                                                                 stroke-linecap="round"
                                                                                 stroke-linejoin="round"
                                                                                 class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></div>
                            </div>
                        </article>
                    </section>
                    <nav class="rmc-pages" aria-label="Страницы каталога">
                        <button type="button" aria-label="Предыдущая страница" disabled="disabled">
                            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                 stroke-linejoin="round" class="lucide lucide-chevron-left">
                                <path d="m15 18-6-6 6-6"></path>
                            </svg>
                        </button>
                        <button type="button" aria-current="page" class="rmc-page-active">1</button>
                        <button type="button">2</button>
                        <button type="button">3</button>
                        <span class="rmc-gap">…</span>
                        <button type="button">160</button>
                        <button type="button" aria-label="Следующая страница">
                            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                 stroke-linejoin="round" class="lucide lucide-chevron-right">
                                <path d="m9 18 6-6-6-6"></path>
                            </svg>
                        </button>
                    </nav>
                        </div>
                    </div>
                    
                </div>
                
            </div>
        </div>
</template>

<style scoped>
                    .rmc-root { position: relative; min-height: 100vh; padding-bottom: 18px;
                      font-family: 'Manrope','Inter',system-ui,sans-serif; color: #111A31; }
                    .rmc-bg { position: absolute; inset: 0; z-index: 0; overflow: hidden; }
                    .rmc-bg-veil { position: absolute; inset: 0;
                      background: linear-gradient(180deg, rgba(246,250,255,0.62), rgba(246,250,255,0.80)); }
                    .rmc-shell { position: relative; z-index: 1; width: min(1480px, 94%); margin: 0 auto; padding: 8px 0 10px; }

                    /* ── Герой: две колонки, чтобы не отъедать высоту у карточек ─────────────── */
                    .rmc-hero { display: grid; grid-template-columns: 1fr 1.9fr; gap: 34px; align-items: center; }
                    .rmc-h1 { margin: 0; font-family: 'Sora','Manrope',sans-serif; font-size: clamp(26px,2.5vw,36px);
                      font-weight: 800; letter-spacing: -0.03em; color: #0B1532; }
                    .rmc-lead { max-width: 440px; margin: 7px 0 0; font-size: 12px; line-height: 1.5; color: #4F5F77; }

                    .rmc-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 11px; }
                    .rmc-stat { display: flex; align-items: center; gap: 10px; min-height: 50px; padding: 8px 11px;
                      border: 1px solid rgba(255,255,255,0.68); border-radius: 14px;
                      background: linear-gradient(145deg, rgba(255,255,255,0.72), rgba(231,242,253,0.52));
                      backdrop-filter: blur(22px); box-shadow: inset 0 1px 0 #fff, 0 10px 26px rgba(45,75,115,0.08); }
                    .rmc-stat-link { text-decoration: none; transition: transform .18s; }
                    .rmc-stat-link:hover { transform: translateY(-2px); }
                    .rmc-stat-icon { display: grid; place-items: center; width: 32px; height: 32px; flex: 0 0 32px;
                      border-radius: 10px; background: rgba(255,255,255,0.8); color: var(--accent); }
                    .rmc-stat b { display: block; font-size: 19px; font-weight: 800; color: var(--accent); letter-spacing: -0.02em; line-height: 1.1; }
                    .rmc-stat-small { font-size: 13.5px !important; }
                    .rmc-stat-label { display: block; margin-top: 2px; font-size: 10px; line-height: 1.3; color: #2E3E56; }

                    /* ── Панель фильтров ─────────────────────────────────────────────────────── */
                    .rmc-panel { margin-top: 8px; border: 1px solid rgba(255,255,255,0.68); border-radius: 17px;
                      background: linear-gradient(145deg, rgba(255,255,255,0.62), rgba(225,239,252,0.45));
                      backdrop-filter: blur(28px); box-shadow: inset 0 1px 0 #fff, 0 18px 44px rgba(45,75,115,0.10); overflow: hidden; }
                    .rmc-filters {display: grid; gap: 12px;
                      align-items: end; padding: 12px 13px 8px; }
                    .rmc-field { display: block; min-width: 0; }
                    .rmc-field > span { display: block; margin-bottom: 4px; font-size: 10.5px; color: #5B6C86; }
                    .rmc-search, .rmc-field select, .rmc-more-btn, .rmc-extra > select, .rmc-extra > .rmc-check {
                      height: 38px; border: 1px solid rgba(255,255,255,0.72); border-radius: 10px;
                      background: rgba(255,255,255,0.62); font-size: 12.5px; color: #111A31; }
                    .rmc-search { display: flex; align-items: center; gap: 9px; padding: 0 13px; color: #7A8AA3; min-width: 0; }
                    .rmc-search input { width: 100%; min-width: 0; border: 0; background: transparent; outline: 0; font: inherit; color: #111A31; }
                    .rmc-field select { width: 100%; padding: 0 11px; outline: 0; }
                    .rmc-more-btn { display: inline-flex; align-items: center; justify-content: center; gap: 7px;
                      cursor: pointer; font-weight: 600; color: #33445F; }
                    .rmc-extra { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; padding: 0 14px 10px; }
                    .rmc-extra > select { min-width: 190px; padding: 0 11px; outline: 0; }
                    .rmc-check { display: inline-flex; align-items: center; gap: 8px; padding: 0 13px; color: #33445F; cursor: pointer; }
                    .rmc-check input { width: 15px; height: 15px; accent-color: #0B64F4; cursor: pointer; }
                    .rmc-reset { display: inline-flex; align-items: center; gap: 5px; cursor: pointer;
                      color: #0B64F4; font-size: 12px; font-weight: 600; background: transparent; border: 0; }

                    /* Семь вкладок в одну строку — как в референсе */
                    .rmc-tabs { display: grid; gap: 6px; padding: 0 13px 8px; }
                    .rmc-tab { display: flex; align-items: center; gap: 8px; min-height: 44px; padding: 6px 8px; cursor: pointer;
                      text-align: left; border: 1px solid rgba(255,255,255,0.55); border-radius: 11px;
                      background: rgba(255,255,255,0.38); color: #22314A; font: inherit; min-width: 0; }
                    .rmc-tab-active { border-color: var(--accent); background: rgba(255,255,255,0.72); box-shadow: 0 8px 22px rgba(65,105,165,0.08); }
                    .rmc-tab-icon { display: grid; place-items: center; width: 27px; height: 27px; flex: 0 0 27px;
                      border-radius: 8px; background: rgba(255,255,255,0.75); color: var(--accent); }
                    .rmc-tab-text { min-width: 0; font-size: 10px; font-weight: 700; line-height: 1.2;
                      display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }
                    .rmc-tab-text small { display: block; margin-top: 3px; font-size: 10.5px; font-weight: 600; color: #47607F; }

                    /* ── Строка результатов ──────────────────────────────────────────────────── */
                    .rmc-resulthead { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;
                      gap: 8px; padding: 5px 4px 9px; font-size: 12px; color: #33445F; }
                    .rmc-resulthead b { color: var(--accent); }
                    .rmc-resultctl { display: flex; align-items: center; gap: 8px; color: #e8f3ff;}
                    .rmc-resultctl select { height: 32px; border: 1px solid rgba(255,255,255,0.72); border-radius: 8px;
                      background: rgba(255,255,255,0.62); padding: 0 10px; font: inherit; font-size: 12px; color: #111A31; outline: 0; }
                    .rmc-v { display: grid; place-items: center; width: 32px; height: 32px; cursor: pointer;
                      border: 1px solid rgba(255,255,255,0.72); border-radius: 8px; background: rgba(255,255,255,0.58); color: #5B6C86; }
                    .rmc-v-active { color: #fff; background: linear-gradient(135deg,#2B82FF,#075CF0); border-color: transparent; }

                    /* ── Карточки ────────────────────────────────────────────────────────────── */
                    .rmc-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
                    .rmc-list { display: flex; flex-direction: column; gap: 10px; }
                    .rmc-card { position: relative; display: flex; flex-direction: column; padding: 10px 12px 11px;
                      border: 1px solid rgba(255,255,255,0.68); border-radius: 15px;
                      background: linear-gradient(145deg, rgba(255,255,255,0.74), rgba(232,241,251,0.56));
                      backdrop-filter: blur(24px); box-shadow: inset 0 1px 0 #fff, 0 14px 32px rgba(41,70,112,0.10);
                      transition: transform .22s, box-shadow .22s; }
                    .rmc-card:hover { transform: translateY(-3px); box-shadow: inset 0 1px 0 #fff, 0 22px 44px rgba(38,69,118,0.15); }
                    /* Фото лежит на фоне карточки, а не в отдельной полосе — как на референсе */
                    /* Фото товара часто на белом фоне — без мягкой подложки оно теряется на карточке */
                    .rmc-visual { position: relative; height: 150px; margin: 1px 0 7px; border-radius: 12px;
                      background: radial-gradient(ellipse at center, rgba(255,255,255,0.95), rgba(255,255,255,0.18) 70%); }
                    .rmc-noimg { display: grid; place-items: center; height: 100%; font-size: 40px; opacity: 0.2; }
                    .rmc-badge { position: absolute; left: 11px; top: 11px; z-index: 2; padding: 4px 8px; border-radius: 999px;
                      background: rgba(235,244,255,0.92); color: #0B64F4; font-size: 9px; font-weight: 700; }
                    .rmc-badge-new { background: rgba(225,250,233,0.92); color: #15964F; }
                    .rmc-fav { position: absolute; right: 10px; top: 9px; z-index: 3; display: flex; gap: 6px; }
                    .rmc-body { display: flex; flex-direction: column; flex: 1; min-width: 0; }
                    .rmc-body h3 { margin: 0; font-size: 14px; font-weight: 800; line-height: 1.2; color: #0B1532;
                      display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }
                    .rmc-stretch { text-decoration: none; color: inherit; }
                    .rmc-stretch::after { content: ''; position: absolute; inset: 0; z-index: 1; }
                    .rmc-maker { margin: 3px 0 0; font-size: 10px; color: #5D6D84; }
                    .rmc-desc { margin: 5px 0 6px; font-size: 10.5px; line-height: 1.38; color: #46566F;
                      display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }
                    .rmc-tags { display: flex; gap: 5px; flex-wrap: wrap; max-height: 20px; overflow: hidden; }
                    .rmc-tags span { padding: 3px 6px; border-radius: 6px; background: rgba(245,248,253,0.8); font-size: 9.5px; color: #46566F; white-space: nowrap; }
                    .rmc-foot { display: flex; align-items: flex-end; justify-content: space-between; gap: 8px; margin-top: auto; padding-top: 6px; }
                    .rmc-price { color: var(--accent); font-size: 16.5px; font-weight: 800; letter-spacing: -0.02em; }
                    .rmc-sup { display: inline-flex; align-items: center; gap: 4px; margin-top: 4px; font-size: 10px; color: #52657F; }
                    .rmc-go { display: grid; place-items: center; width: 30px; height: 30px; flex: 0 0 30px; border-radius: 9px;
                      background: rgba(255,255,255,0.72); border: 1px solid rgba(255,255,255,0.85); color: #0B64F4; }

                    /* Список — то же содержимое строкой */
                    .rmc-card-row { flex-direction: row; align-items: center; gap: 14px; padding: 11px 13px; }
                    .rmc-card-row .rmc-visual { width: 190px; flex: 0 0 190px; height: 104px; margin: 0; }
                    .rmc-card-row .rmc-body { flex: 1; }
                    .rmc-card-row .rmc-desc { -webkit-line-clamp: 1; }
                    .rmc-card-row .rmc-foot { margin-top: 7px; padding-top: 0; }

                    .rmc-empty { display: grid; place-items: center; gap: 10px; padding: 48px 20px; color: #6B7A93;
                      border: 1px dashed rgba(255,255,255,0.8); border-radius: 15px; background: rgba(255,255,255,0.45); }
                    .rmc-empty p { margin: 0; font-size: 13px; }

                    .rmc-pages { display: flex; justify-content: center; align-items: center; gap: 7px; padding: 8px 0 2px; }
                    .rmc-pages button { display: grid; place-items: center; width: 32px; height: 32px; cursor: pointer;
                      border: 1px solid rgba(255,255,255,0.72); border-radius: 9px; background: rgba(255,255,255,0.58);
                      font: inherit; font-size: 12.5px; color: #33445F; }
                    .rmc-pages button:disabled { opacity: 0.4; cursor: default; }
                    .rmc-page-active { color: #fff !important; background: linear-gradient(135deg,#2B82FF,#075CF0) !important; border-color: transparent !important; font-weight: 700; }
                    .rmc-gap { color: #7A8AA3; }
                    .rmc-filter-panel__sidebar_left {
                        width: 50rem;
                      }

                    @media (max-width: 1280px) {
                      .rmc-tabs { grid-template-columns: repeat(4, minmax(0, 1fr)); }
                      .rmc-filter-panel {
                        flex-direction: column;
                      }
                      .rmc-filter-panel__sidebar_left {
                        width: 100%;
                      }

                    }
                    @media (max-width: 1100px) {
                      .rmc-hero { grid-template-columns: 1fr; gap: 18px; }
                      .rmc-filters { grid-template-columns: 1fr 1fr; }
                      .rmc-search { grid-column: 1 / -1; }
                      .rmc-grid { grid-template-columns: repeat(2, 1fr); }

                    }
                    @media (max-width: 720px) {
                      .rmc-shell { width: calc(100% - 20px); }
                      .rmc-stats { grid-template-columns: 1fr 1fr; }
                      .rmc-filters { grid-template-columns: 1fr; }
                      .rmc-tabs { grid-template-columns: 1fr 1fr; }
                      .rmc-grid { grid-template-columns: 1fr; }
                      .rmc-resulthead { align-items: flex-start; }
                      .rmc-card-row { flex-direction: column; align-items: stretch; }
                      .rmc-card-row .rmc-visual { width: 100%; flex: none; height: 150px; }
                    }
                </style>