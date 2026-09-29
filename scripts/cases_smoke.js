/**
 * Проверка страниц «Пилотирование» и «Кейсы».
 *
 * Обе страницы строятся из каталога, поэтому проверяем не разметку, а
 * данные: сколько позиций пришло, отфильтровались ли они по отрасли и
 * открывается ли карточка из списка. На /cases и /pilot-testing страниц
 * раньше не было — на них вели ссылки из шапки и подвала, и они отдавали 404.
 */
const { firefox } = require('playwright-core')

const BASE = process.argv[2] || 'http://127.0.0.1:8080'
const SHOT = process.env.SHOT_DIR || '/tmp/cases-shot'

let fails = 0
const say = (ok, name, extra = '') => {
  if (!ok) fails++
  console.log(`  ${ok ? 'OK   ' : 'ОШИБКА'} ${name}${ok || !extra ? '' : '  -> ' + extra}`)
}

;(async () => {
  require('fs').mkdirSync(SHOT, { recursive: true })
  const browser = await firefox.launch({ headless: true })
  const page = await browser.newPage({ viewport: { width: 1500, height: 1000 } })
  const errs = []
  page.on('console', (m) => m.type() === 'error' && errs.push(m.text().slice(0, 200)))
  page.on('pageerror', (e) => errs.push('PAGEERROR: ' + String(e).slice(0, 200)))

  // ── Пилотирование ──────────────────────────────────────────────────────
  console.log('1. ПИЛОТИРОВАНИЕ')
  await page.goto(BASE + '/pilot-testing', { waitUntil: 'domcontentloaded', timeout: 90000 })
  const pilotReady = await page
    .locator('.pt-item')
    .first()
    .waitFor({ timeout: 60000 })
    .then(() => true)
    .catch(() => false)
  say(pilotReady, 'карточки пилотов дождались')
  await page.waitForTimeout(1500)
  const pilotCount = await page.locator('.pt-item').count()
  say(pilotCount > 0, `пилотов показано: ${pilotCount}`, 'список пуст')
  const stats = await page.locator('.pt-stat').allInnerTexts().catch(() => [])
  say(stats.length === 4, `показателей: ${stats.length} — ${stats.map((s) => s.replace(/\n/g, '=')).join(', ').slice(0, 74)}`)
  const trlCols = await page.locator('.pt-trl__col').count()
  say(trlCols > 0, `столбцов по УГТ: ${trlCols}`)
  const withPhoto = await page.locator('.pt-item__visual img').count()
  say(withPhoto > 0, `фото в карточках: ${withPhoto}`)
  const pilotsTagged = await page.locator('.pt-tag--trl').count()
  say(pilotsTagged > 0, `меток УГТ: ${pilotsTagged}`)

  // Фильтр по отрасли должен реально сузить список
  const beforeFilter = await page.locator('.pt-item').count()
  const opts = await page.locator('.pt-filters select option').count()
  if (opts > 1) {
    await page.locator('.pt-filters select').selectOption({ index: 1 })
    await page.waitForTimeout(900)
    const afterFilter = await page.locator('.pt-item').count()
    say(
      afterFilter > 0 && afterFilter < beforeFilter,
      `фильтр по отрасли сузил список: ${beforeFilter} → ${afterFilter}`,
      `стало ${afterFilter}`,
    )
    await page.screenshot({ path: `${SHOT}/01-pilots.png` })
    await page.locator('.pt-filters select').selectOption('')
    await page.waitForTimeout(600)
  }
  say((await page.locator('.pt-item').count()) === beforeFilter, 'сброс фильтра вернул все позиции')

  // Фото не должно наезжать на текст карточки. В колоночном флексе блок
  // изображения сжимался по контенту, и вытянутый снимок уезжал под себя:
  // заголовок оказывался поверх фотографии.
  const overlaps = await page.evaluate(() => {
    const bad = []
    for (const item of document.querySelectorAll('.pt-item')) {
      const vis = item.querySelector('.pt-item__visual')
      const h3 = item.querySelector('h3')
      if (!vis || !h3) continue
      const v = vis.getBoundingClientRect()
      const t = h3.getBoundingClientRect()
      if (t.top < v.bottom - 1) bad.push(h3.textContent.trim().slice(0, 30))
    }
    return bad
  })
  say(overlaps.length === 0, 'фото не наезжает на заголовок', overlaps.slice(0, 3).join(', '))
  await page.screenshot({ path: `${SHOT}/01-pilots.png` })

  // ── Кейсы ──────────────────────────────────────────────────────────────
  console.log('2. КЕЙСЫ')
  await page.goto(BASE + '/cases', { waitUntil: 'domcontentloaded', timeout: 90000 })
  const casesReady = await page
    .locator('.bc-item__link')
    .first()
    .waitFor({ timeout: 60000 })
    .then(() => true)
    .catch(() => false)
  say(casesReady, 'карточки кейсов дождались')
  await page.waitForTimeout(1500)
  const caseCount = await page.locator('.bc-item__link').count()
  say(caseCount > 0, `кейсов показано: ${caseCount}`, 'список пуст')
  const cstats = await page.locator('.bc-stat').allInnerTexts().catch(() => [])
  say(cstats.length === 4, `показателей: ${cstats.length} — ${cstats.map((s) => s.replace(/\n/g, '=')).join(', ').slice(0, 74)}`)
  const okTags = await page.locator('.bc-tag--ok').count()
  say(okTags > 0, `отмечено «В эксплуатации»: ${okTags}`)
  // Ссылка на источник данных обязательна: без неё цифры выглядят как
  // выдуманные, а они взяты из каталога внедрения.
  say(
    (await page.locator('.bc-source').innerText().catch(() => '')).includes('каталог'),
    'указан источник данных',
  )
  const caseOverlaps = await page.evaluate(() => {
    const bad = []
    for (const item of document.querySelectorAll('.bc-item__link')) {
      const vis = item.querySelector('.bc-item__visual')
      const h3 = item.querySelector('h3')
      if (!vis || !h3) continue
      const v = vis.getBoundingClientRect()
      const t = h3.getBoundingClientRect()
      if (t.top < v.bottom - 1) bad.push(h3.textContent.trim().slice(0, 30))
    }
    return bad
  })
  say(caseOverlaps.length === 0, 'фото не наезжает на заголовок', caseOverlaps.slice(0, 3).join(', '))
  await page.screenshot({ path: `${SHOT}/02-cases.png` })

  // ─�� Переход в карточку из кейса ─────────────────────────────────────────
  console.log('3. ПЕРЕХОД В КАРТОЧКУ')
  await page.locator('.bc-item__link').first().click()
  const h1 = page.locator('.rpd-title h1')
  const opened = await h1
    .waitFor({ timeout: 40000 })
    .then(() => true)
    .catch(() => false)
  await page.waitForTimeout(1500)
  say(opened, `карточка открылась: ${page.url().replace(BASE, '')}`)
  say(!!(await h1.innerText().catch(() => '')), `название: ${await h1.innerText().catch(() => '—')}`)

  console.log('4. ОШИБКИ В КОНСОЛИ')
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
