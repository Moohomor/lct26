/**
 * Проверка страницы финансирования: вход, заполнение формы, расчёт.
 *
 * Страница считает на бэкенде, поэтому проверять только статичную вёрстку
 * бессмысленно: расчёт может упасть, а таблицы — оказаться пустыми. Так
 * и вышло: блок условий RaaS молча показывал «—», потому что страница
 * читала не тот ключ ответа.
 *
 * Запуск (нужен поднятый docker compose, см. browser_smoke.js про
 * playwright-core):
 *   node scripts/financing_smoke.js http://127.0.0.1:8080
 *
 * Таймауты в проверке большие намеренно: в этом окружении localhost
 * резолвится в IPv6, и запрос к API встаёт на десятки секунд.
 */
const { firefox } = require('playwright-core')

const BASE = process.argv[2] || 'http://127.0.0.1:8080'
const SHOT = process.env.SHOT_DIR || '/tmp/fin-shot'

let fails = 0
const say = (ok, name, extra = '') => {
  if (!ok) fails++
  console.log(`  ${ok ? 'OK   ' : 'ОШИБКА'} ${name}${ok || !extra ? '' : '  -> ' + extra}`)
}

;(async () => {
  require('fs').mkdirSync(SHOT, { recursive: true })
  const browser = await firefox.launch({ headless: true })
  const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } })
  const errs = []
  page.on('console', (m) => m.type() === 'error' && errs.push(m.text().slice(0, 200)))
  page.on('pageerror', (e) => errs.push('PAGEERROR: ' + String(e).slice(0, 200)))

  console.log('1. ГОСТЬ')
  await page.goto(BASE + '/financing', { waitUntil: 'domcontentloaded', timeout: 90000 })
  await page.locator('.fin-card--gate').waitFor({ timeout: 30000 }).catch(() => {})
  say((await page.locator('.fin-card--gate').count()) > 0, 'гостю предложен вход')
  say((await page.locator('.fin-grid').count()) === 0, 'форма гостю не показывается')
  say((await page.locator('.fin-scheme-mini').count()) === 4, 'справочные схемы на месте')
  const schemeImgs = await page.locator('.fin-scheme-mini__img img').evaluateAll((els) =>
    els.map((e) => e.complete && e.naturalWidth > 0),
  )
  say(schemeImgs.length === 4 && schemeImgs.every(Boolean), `иллюстрации загрузились: ${schemeImgs.filter(Boolean).length}/4`)

  console.log('2. ВХОД')
  await page.goto(BASE + '/login', { waitUntil: 'domcontentloaded', timeout: 90000 })
  // Страница без SSR: счётчики сразу после domcontentloaded нулевые,
  // поля рисует клиент. Поэтому ждём конкретное поле, а не считаем input.
  const email = page.locator('input[type="email"]')
  const pw = page.locator('input[type="password"]')
  // Dev-сервер в этом окружении отвечает нестабильно, страница без SSR
  // рисуется клиентом, поэтому ждём с запасом и повторяем заход.
  let found = false
  for (let attempt = 1; attempt <= 3 && !found; attempt++) {
    found = await email
      .first()
      .waitFor({ timeout: 45000 })
      .then(() => true)
      .catch(() => false)
    if (!found) {
      console.log(`  (повтор входа: ${attempt})`)
      await page.goto(BASE + '/login', { waitUntil: 'domcontentloaded', timeout: 90000 })
    }
  }
  say(found, 'поля входа дождались')
  if (found) {
    await email.first().fill('user@example.com')
    await pw.first().fill('demo12345')
    await page.locator('button[type="submit"]').first().click()
    // В этом окружении localhost резолвится в IPv6, и запрос к API встаёт
    // на ~15 секунд. Вход и расчёт ждём с запасом, иначе проверка падает
    // на таймаутах, а не на дефектах.
    const ok = await page
      .waitForFunction(() => document.cookie.includes('access_token'), null, { timeout: 60000 })
      .then(() => true)
      .catch(() => false)
    say(ok, 'токен сохранён в cookie')
    // После входа приложение уходит на главную и лениво грузит её чанк.
    // Если перейти на /financing, пока грузится, запрос оборвётся и в
    // консоли появится «error loading dynamically imported module» — это
    // гонка теста, а не дефект. Ждём, пока главная действительно
    // отрисовалась, а не только успокоилась сеть.
    const home = await page
      .waitForFunction(
        () => document.body.innerText.includes('роботизированных решений'),
        null,
        { timeout: 60000 },
      )
      .then(() => true)
      .catch(() => false)
    say(home, 'главная догрузилась после входа')
  }

  console.log('3. ФОРМА')
  await page.goto(BASE + '/financing', { waitUntil: 'domcontentloaded', timeout: 90000 })
  let otypeReady = false
  for (let attempt = 1; attempt <= 3 && !otypeReady; attempt++) {
    otypeReady = await page
      .locator('.fin-otype')
      .first()
      .waitFor({ timeout: 60000 })
      .then(() => true)
      .catch(() => false)
    if (!otypeReady) {
      console.log(`  (повтор формы: ${attempt})`)
      await page.goto(BASE + '/financing', { waitUntil: 'domcontentloaded', timeout: 90000 })
    }
  }
  say(otypeReady, 'форма дождалась данных справочника')
  await page.waitForTimeout(2000)
  const otype = await page.locator('.fin-otype').count()
  say(otype === 3, `типов объекта: ${otype}`, 'ожидалось 3')
  const chips = await page.locator('.fin-chip').count()
  say(chips > 0, `процессов: ${chips}`)
  const shown = await page.locator('.fin-param').count()
  say(shown > 0, `обязательных параметров в форме: ${shown}`, 'форма пустая')
  const opts = await page.locator('.fin-pick').count()
  say(opts > 0, `позиций в подборе оборудования: ${opts}`)
  await page.screenshot({ path: `${SHOT}/01-form.png`, fullPage: true })

  console.log('4. РАСЧЁТ')
  // Берём недорогое оборудование: при умолчаниях справочника склад
  // рассчитан на 700 человек, и дорогой парк даёт заведомо минусовой ROI.
  await page.locator('.fin-input--search').fill('Ronavi')
  await page.waitForTimeout(800)
  const picks = await page.locator('.fin-pick').count()
  say(picks > 0, `поиск «Ronavi» нашёл: ${picks}`)
  await page.locator('.fin-pick').first().click()
  await page.waitForTimeout(500)
  say((await page.locator('.fin-line').count()) > 0, 'позиция добавлена в сценарий')

  await page.locator('.fin-btn--wide').click()
  const tco = page.locator('.fin-tco tbody tr')
  const got = await tco
    .first()
    .waitFor({ timeout: 120000 })
    .then(() => true)
    .catch(() => false)
  await page.waitForTimeout(2000)
  say(got, 'таблица стоимости владения появилась')
  if (got) {
    const rows = await tco.count()
    say(rows === 3, `сценариев в таблице: ${rows}`, 'модель считает три сценария')
    const best = await page.locator('.fin-badge').count()
    say(best === 1, `выделен выгодный вариант: ${best === 1 ? 'да' : 'нет'}`)
    const firstRow = await tco.first().innerText()
    console.log('        ' + firstRow.replace(/\n/g, ' | ').slice(0, 110))
  }
  const err = await page.locator('.fin-note--bad').allInnerTexts().catch(() => [])
  if (err.length) console.log('  инфо  ошибка на странице: ' + err[0].slice(0, 120))
  say((await page.locator('.fin-kpi__cell').count()) >= 4, 'показатели эффекта и окупаемости')
  say((await page.locator('.fin-years tbody tr').count()) > 0, 'денежный поток по годам')
  say((await page.locator('.fin-sens').count()) === 3, `факторов чувствительности: ${await page.locator('.fin-sens').count()}`)

  // Условия RaaS лежат внутри блока сценария (res.raas.raas). Раньше
  // страница читала res.raas напрямую и показывала пустые «—».
  const raasCells = await page.locator('.fin-kpi__cell').allInnerTexts().catch(() => [])
  const raasLine = raasCells.filter((t) => /Платёж в год|Вводный платёж|Срок договора/.test(t)).join(' | ')
  say(
    !!raasLine && !/—\s*$/.test(raasLine.trim()) && !/не число/.test(raasLine),
    `условия RaaS заполнены: ${raasLine.replace(/\n/g, ' ').slice(0, 78) || '—'}`,
    raasLine || 'блок RaaS не найден',
  )
  // Полосы чувствительности: у базовой точки (0%) отклонение нулевое
  const sensDelta = await page
    .locator('.fin-sens')
    .first()
    .locator('.fin-sens__point')
    .nth(2)
    .locator('.fin-sens__value')
    .innerText()
    .catch(() => '')
  say(
    sensDelta.includes('0 ₽'),
    `базовая точка чувствительности без отклонения: ${sensDelta}`,
    sensDelta || 'значение не найдено',
  )
  say((await page.locator('.fin-warn li').count()) > 0, 'оговорки к расчёту показаны')
  const dupes = await page.locator('.fin-warn li').allInnerTexts()
  const unique = new Set(dupes.map((s) => s.trim()))
  say(unique.size === dupes.length, `повторов в оговорках нет (${dupes.length} строк)`)
  await page.screenshot({ path: `${SHOT}/02-result.png`, fullPage: true })

  console.log('5. ОШИБКИ В КОНСОЛИ')
  if (!errs.length) say(true, 'ошибок нет')
  else {
    say(false, `ошибок: ${errs.length}`)
    ;[...new Set(errs)].slice(0, 5).forEach((e) => console.log('        ' + e))
  }

  await browser.close()
  console.log(fails ? `\nПРОВАЛЕНО: ${fails}` : '\nвсе проверки пройдены')
  console.log('снимки:', SHOT)
  process.exit(fails ? 1 : 0)
})().catch((e) => {
  console.error('СБОЙ:', e.message)
  process.exit(1)
})
