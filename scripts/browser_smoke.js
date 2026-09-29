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
 * Используется 127.0.0.1, а не localhost: в некоторых окружениях localhost
 * резолвится в IPv6, и опубликованные порты начинают отвечать с задержкой.
 */

const { firefox } = require('playwright-core')

const API = process.argv[2] || 'http://127.0.0.1:5000'
const BASE = process.argv[3] || 'http://127.0.0.1:8080'
const SHOT = process.env.SHOT_DIR || '/tmp/browser-smoke'

// Позиции подобраны по данным: фото есть не у всех (112 из 190), а ТТХ
// заполнены у единиц. Иначе проверка зависела бы от того, какая позиция
// попадётся первой.
const RICH = '8c467586-9bb0-4be6-ac0b-e2ef71b0a75c' // Ronavi H1500: фото, ТТХ, комплектация
const SPARSE = '8f6e8f9c-886c-41d8-a5c7-61b49a520598' // 85ТК: фото есть, ТТХ нет
const NO_PHOTO = '3ae303da-e463-4356-ab7a-da9edec07c7d' // DMR Carrier P: фото нет, ТТХ есть

let fails = 0
const say = (ok, name, extra = '') => {
  if (!ok) fails++
  console.log(`  ${ok ? 'OK   ' : 'ОШИБКА'} ${name}${ok || !extra ? '' : '  -> ' + extra}`)
}

;(async () => {
  require('fs').mkdirSync(SHOT, { recursive: true })
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
  await page.goto(`${BASE}/catalog/${RICH}`, { waitUntil: 'domcontentloaded', timeout: 90000 })
  await page.locator('.rpd-title h1').waitFor({ timeout: 30000 }).catch(() => {})
  await page.waitForTimeout(2000)
  say(/Ronavi/i.test(await page.locator('.rpd-title h1').innerText().catch(() => '')), 'название')
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
  say(varRows > 0, `комплектаций показано: ${varRows}`, 'блок комплектаций пуст')
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
  await page.goto(`${BASE}/catalog/${SPARSE}`, { waitUntil: 'domcontentloaded', timeout: 90000 })
  await page.locator('.rpd-title h1').waitFor({ timeout: 30000 }).catch(() => {})
  await page.waitForTimeout(1500)
  say((await page.locator('.rpd-title h1').count()) > 0, 'карточка открылась')
  say(
    (await page.locator('.rpd-price__main').innerText().catch(() => '')).length > 0,
    'цена показана',
  )
  console.log(`  инфо  строк ТТХ: ${await page.locator('.rpd-spec').count()} (у позиции их нет)`)

  console.log('5. ПОЗИЦИЯ БЕЗ ФОТО')
  await page.goto(`${BASE}/catalog/${NO_PHOTO}`, { waitUntil: 'domcontentloaded', timeout: 90000 })
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
  console.log(`API: ${API}\nфронтенд: ${BASE}\nснимки: ${SHOT}`)
  console.log(fails ? `\nПРОВАЛЕНО ПРОВЕРОК: ${fails}` : '\nвсе проверки пройдены')
  process.exit(fails ? 1 : 0)
})().catch((e) => {
  console.error('СБОЙ ПРОВЕРКИ:', e.message)
  process.exit(1)
})
