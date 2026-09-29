/**
 * Дымовая проверка каталога и карточки решения настоящим браузером.
 *
 * Нужна потому, что ошибки этого класса не видны ни в коде ответа, ни в
 * собранном CSS: страница отдаёт 200, полоса загрузки исчезает, а на экране
 * пусто. Так было трижды подряд — карточка не открывалась из-за того, что
 * родительский маршрут не содержал <NuxtPage />; маршрут был вложенным, и
 * компонент не монтировался вовсе; карточка позиции с комплектациями падала
 * с 500, а список каталога при этом открывался.
 *
 * Запуск (нужен поднятый docker compose):
 *   npm i --no-save playwright-core        # из корня репозитория
 *   npx playwright install firefox
 *   node scripts/browser_smoke.js http://127.0.0.1:5000 http://127.0.0.1:8080
 *
 * playwright-core ставится без записи в package.json: корень репозитория
 * про Node-пакеты не знает, а модуль нужен только этой проверке. Node
 * ищет его в scripts/node_modules и выше, поэтому ставить нужно в корень,
 * а не в каталог фронтенда.
 *
 * Аргументы: адрес API и адрес фронтенда. Второй можно не указывать.
 * Скрипт работает и против продакшена: позиции для проверки ищутся в
 * каталоге по названию, а не прописаны в коде — UUID у каждой базы свои.
 * Используется 127.0.0.1, а не localhost: в некоторых окружениях localhost
 * резолвится в IPv6, и опубликованные порты начинают отвечать с задержкой.
 */

const { firefox } = require('playwright-core')

const API = process.argv[2] || 'http://127.0.0.1:5000'
const BASE = process.argv[3] || 'http://127.0.0.1:8080'
const SHOT = process.env.SHOT_DIR || '/tmp/browser-smoke'

let fails = 0
const say = (ok, name, extra = '') => {
  if (!ok) fails++
  console.log(`  ${ok ? 'OK   ' : 'ОШИБКА'} ${name}${ok || !extra ? '' : '  -> ' + extra}`)
}

;(async () => {
  require('fs').mkdirSync(SHOT, { recursive: true })

  // Три позиции с разным наполнением. Ищем их в каталоге по названию:
  // фото есть не у всех позиций, а ТТХ заполнены у единиц, и без явного
  // выбора проверка зависела бы от того, какая позиция попадётся первой.
  const listing = await fetch(`${API}/api/v1/catalog?limit=500`).then((r) => r.json())
  const items = listing.items || []
  const pick = (test) => items.find(test)
  const RICH = pick((i) => i.photo_url && (i.completeness || 0) >= 60 && i.name.startsWith('Ronavi'))
  const SPARSE = pick((i) => i.photo_url && (i.completeness || 0) < 30)
  const NO_PHOTO = pick((i) => !i.photo_url && (i.completeness || 0) >= 60)
  for (const [label, it] of [
    ['с фото и ТТХ', RICH],
    ['без ТТХ', SPARSE],
    ['без фото', NO_PHOTO],
  ]) {
    if (!it) {
      say(false, `в каталоге нет позиции «${label}» — проверка неполная`)
      process.exit(1)
    }
  }
  console.log(
    `позиции: ${RICH.name} / ${SPARSE.name} / ${NO_PHOTO.name}\n` +
      `API: ${API}\nфронтенд: ${BASE}\n`,
  )

  const browser = await firefox.launch({ headless: true })
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })

  const reqs = []
  const errs = []
  page.on('request', (r) => {
    if (r.url().includes('/api/')) reqs.push(r.url().replace(/https?:\/\/[^/]+/, ''))
  })
  page.on('console', (m) => {
    if (m.type() === 'error') errs.push(m.text().slice(0, 220))
  })
  page.on('pageerror', (e) => errs.push('PAGEERROR: ' + String(e).slice(0, 220)))

  console.log('1. КАТАЛОГ')
  await page.goto(BASE + '/catalog', { waitUntil: 'domcontentloaded', timeout: 90000 })
  // Ждём именно карточек: счётчик сразу после загрузки может быть нулём
  // из-за холодной сборки, а кликать уже есть по чему.
  const got = await page
    .waitForSelector('article.rmc-card', { timeout: 60000 })
    .then(() => true)
    .catch(() => false)
  say(got, 'карточки дождались')
  await page.waitForTimeout(1200)
  const cards = await page.locator('article.rmc-card').count()
  say(cards > 0, `карточек отрисовано: ${cards}`, 'ни одной')
  const photos = await page.locator('article.rmc-card .rmc-visual--photo img').count()
  say(photos > 0, `фото в карточках: ${photos}`)
  await page.screenshot({ path: `${SHOT}/01-catalog.png` })

  console.log('2. КЛИК ПО ПЛОЩАДИ КАРТОЧКИ')
  reqs.length = 0
  const box = await page.locator('article.rmc-card').first().boundingBox()
  // Кликаем не по названию, а по нижней части карточки: целиком её
  // накрывает ::after растянутой ссылки, и по названию клик прошёл бы
  // даже при сломанной карточке.
  await page.mouse.click(box.x + box.width * 0.5, box.y + box.height * 0.82)
  const h1 = page.locator('.rpd-title h1')
  const opened = await h1
    .waitFor({ timeout: 30000 })
    .then(() => true)
    .catch(() => false)
  await page.waitForTimeout(2500)
  say(opened, `карточка открылась: ${page.url().replace(BASE, '')}`)
  const detailReq = reqs.filter((r) => /\/catalog\/[0-9a-f-]{36}$/.test(r))
  say(detailReq.length > 0, `запрос карточки к API: ${detailReq[0] || 'не было'}`, 'не было')
  const loading = await page
    .locator('.nuxt-loading-indicator')
    .evaluate((el) => el.style.opacity !== '0')
    .catch(() => false)
  say(!loading, 'полоса загрузки погасла')

  console.log('3. КАРТОЧКА С ТТХ')
  await page.goto(`${BASE}/catalog/${RICH.id}`, { waitUntil: 'domcontentloaded', timeout: 90000 })
  await page.locator('.rpd-title h1').waitFor({ timeout: 30000 }).catch(() => {})
  await page.waitForTimeout(2000)
  const title = await page.locator('.rpd-title h1').innerText().catch(() => '')
  say(title.trim() === RICH.name, `название: ${title.trim() || '—'}`, `ожидали ${RICH.name}`)
  const specs = await page.locator('.rpd-spec').count()
  say(specs > 0, `строк ТТХ и цены: ${specs}`, 'блок не отрисовался')
  const price = await page.locator('.rpd-price__main').innerText().catch(() => '')
  say(!!price, `цена: ${price || '—'}`)
  const imgOk = await page
    .locator('.rpd-visual img')
    .evaluate((el) => el.complete && el.naturalWidth > 0)
    .catch(() => false)
  say(imgOk, 'фото загрузилось')
  const varRows = await page.locator('.rpd-variant').count()
  // Комплектации есть не у каждой позиции, поэтому сверяем с тем, что
  // отдал API: блок обязан совпасть, а не просто «что-то нарисовалось».
  const expectVariants = await fetch(`${API}/api/v1/catalog/${RICH.id}`)
    .then((r) => r.json())
    .then((d) => (d.variants || []).length)
  say(
    varRows === expectVariants,
    `комплектаций: ${varRows} (в данных ${expectVariants})`,
    'не совпало с данными',
  )
  // applicable_object_types хранит коды (warehouse, airport) — на карточке
  // должны быть названия из справочника.
  const conditions = await page.locator('.rpd-block p').allInnerTexts().catch(() => [])
  const objLine = (conditions.find((t) => t.includes('объектов')) || '').trim()
  say(
    !!objLine && !/warehouse|airport|medical/.test(objLine),
    `типы объектов по-русски: ${objLine.slice(0, 60) || '—'}`,
    objLine || 'строка не отрисована',
  )
  say((await page.locator('.rpd-state').count()) === 0, 'не застряла в загрузке/ошибке')
  await page.screenshot({ path: `${SHOT}/02-solution.png`, fullPage: true })

  console.log('4. КАРТОЧКА БЕЗ ТТХ')
  await page.goto(`${BASE}/catalog/${SPARSE.id}`, { waitUntil: 'domcontentloaded', timeout: 90000 })
  await page.locator('.rpd-title h1').waitFor({ timeout: 30000 }).catch(() => {})
  await page.waitForTimeout(1500)
  say(
    (await page.locator('.rpd-title h1').innerText().catch(() => '')).trim() === SPARSE.name,
    `карточка открылась: ${SPARSE.name}`,
  )
  say(
    (await page.locator('.rpd-price__main').innerText().catch(() => '')).length > 0,
    'цена показана',
  )
  const sparseSpecs = await page.locator('.rpd-spec').count()
  // Блок ТТХ у такой позиции скрыт законно, но у неё остаётся цена —
  // проверяем, что страница не схлопнулась целиком.
  say(sparseSpecs === 0, `блок ТТХ скрыт (строк: ${sparseSpecs})`, 'показан при заполненности 0%')

  console.log('5. ПОЗИЦИЯ БЕЗ ФОТО')
  await page.goto(`${BASE}/catalog/${NO_PHOTO.id}`, { waitUntil: 'domcontentloaded', timeout: 90000 })
  await page.locator('.rpd-title h1').waitFor({ timeout: 30000 }).catch(() => {})
  await page.waitForTimeout(1500)
  say((await page.locator('.rpd-visual--none').count()) > 0, 'показана заглушка «Нет фото»')
  say((await page.locator('.rpd-spec').count()) > 0, 'ТТХ на месте, несмотря на отсутствие фото')

  console.log('6. ОШИБКИ В КОНСОЛИ')
  if (!errs.length) say(true, 'ошибок нет')
  else {
    say(false, `ошибок: ${errs.length}`)
    ;[...new Set(errs)].slice(0, 6).forEach((e) => console.log('        ' + e))
  }

  await browser.close()
  console.log(`снимки: ${SHOT}`)
  console.log(fails ? `\nПРОВАЛЕНО ПРОВЕРОК: ${fails}` : '\nвсе проверки пройдены')
  process.exit(fails ? 1 : 0)
})().catch((e) => {
  console.error('СБОЙ ПРОВЕРКИ:', e.message)
  process.exit(1)
})
