/**
 * Проверка главной страницы, /contacts и авторизации.
 *
 * Проверяем не разметку, а данные и поведение: главная обязана показывать
 * реальные числа каталога и не обещать того, чего в платформе нет;
 * регистрация обязана сохранить имя и фамилию вместе и принять организацию.
 */
const { firefox } = require('playwright-core')

const BASE = process.argv[2] || 'http://127.0.0.1:8080'
const SHOT = process.env.SHOT_DIR || '/tmp/home-shot'
// Уникальный почтовый ящик на каждый прогон: повторная регистрация падает
// с «пользователь уже существует», и проверка становится нестабильной.
const NEW_EMAIL = `probe${Date.now().toString(36)}@example.com`

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

  // Страница без SSR: после goto содержимое рисует клиент, поэтому
  // переходы ждут по конкретному элементу, а не по сети.
  const go = async (path, selector) => {
    await page.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 90000 })
    // В этом окружении localhost резолвится в IPv6 и запросы к API встают
    // на десятки секунд, поэтому ждём с запасом. Метка не влияет на итог:
    // содержательные проверки ниже всё равно провалятся, если страница
    // не отрисовалась.
    await page
      .locator(selector)
      .first()
      .waitFor({ timeout: 90000 })
      .catch(() => {})
    await page.waitForTimeout(800)
  }

  // ── Главная ────────────────────────────────────────────────────────────
  console.log('1. ГЛАВНАЯ')
  await go('/', '.rm-stats__cell')
  const cells = await page.locator('.rm-stats__cell').allInnerTexts().catch(() => [])
  say(cells.length === 6, `показателей: ${cells.length} — ${cells.map((c) => c.replace(/\n/g, '=')).join(', ').slice(0, 92)}`)

  // Обещания, которых платформа не выполняет. Каждое из них опровергается
  // каталогом, и на демонстрации это всплывает сразу.
  const text = await page.locator('body').innerText()
  const falseClaims = [
    [/тысяч/i, '«тысячи моделей» при 226 позициях'],
    [/измеримые результаты/i, '«измеримые результаты» — таких цифр нет'],
    [/от 2 недель/i, '«пилот от 2 недель» — нигде не зафиксировано'],
    [/лизинг, аренда/i, '«лизинг, аренда» — в модели их нет'],
  ]
  const found = falseClaims.filter(([re]) => re.test(text)).map(([, why]) => why)
  say(found.length === 0, 'неправдивых обещаний на главной нет', found.join('; '))

  // Ни одна ссылка не должна вести в 404
  const links = await page.locator('a[href^="/"]').evaluateAll((els) =>
    [...new Set(els.map((e) => e.getAttribute('href')))],
  )
  const dead = []
  for (const href of links) {
    const r = await page.request.get(BASE + href)
    if (r.status() >= 400) dead.push(`${href} → ${r.status()}`)
  }
  say(dead.length === 0, `ссылок на главной: ${links.length}, битых нет`, dead.join('; '))
  const sectionImgs = await page
    .locator('.rm-service-card img')
    .evaluateAll((els) => els.filter((e) => e.complete && e.naturalWidth > 0).length)
  const totalImgs = await page.locator('.rm-service-card img').count()
  say(sectionImgs === totalImgs, `иллюстраций загрузилось: ${sectionImgs}/${totalImgs}`)

  // Текст карточки не должен ложиться на иллюстрацию: в шести колонках
  // карточка узкая, и описание без ограничения высоты перекрывало рисунок,
  // а заголовки обрезались. Замеряем сами строки, а не контейнер с
  // отступом — иначе отступ сам даёт «перекрытие».
  const cardOverlaps = await page.evaluate(() => {
    const bad = []
    for (const card of document.querySelectorAll('.rm-service-card')) {
      const img = card.querySelector('img')
      if (!img) continue
      const i = img.getBoundingClientRect()
      for (const el of card.querySelectorAll('.rm-service-card__text h2, .rm-service-card__text p')) {
        const t = el.getBoundingClientRect()
        const overlapX = Math.min(t.right, i.right) - Math.max(t.left, i.left)
        const overlapY = Math.min(t.bottom, i.bottom) - Math.max(t.top, i.top)
        if (overlapX > 6 && overlapY > 6) {
          bad.push(`${card.getAttribute('href')}: ${el.textContent.trim().slice(0, 24)}`)
        }
      }
    }
    return bad
  })
  say(
    cardOverlaps.length === 0,
    'текст карточек не наезжает на иллюстрации',
    cardOverlaps.slice(0, 4).join('; ') || 'перекрытий нет',
  )
  const clipped = await page.evaluate(() =>
    [...document.querySelectorAll('.rm-service-card__text h2')].filter(
      (h) => h.scrollWidth > h.clientWidth + 1,
    ).length,
  )
  say(clipped === 0, 'заголовки карточек не обрезаны', `обрезано: ${clipped}`)
  await page.screenshot({ path: `${SHOT}/01-home.png`, fullPage: false, timeout: 90000 })

  // ── Контакты ───────────────────────────────────────────────────────────
  console.log('2. КОНТАКТЫ')
  await go('/contacts', '.ct-cred')
  const creds = await page.locator('.ct-cred').allInnerTexts().catch(() => [])
  say(creds.length === 3, `демо-записей показано: ${creds.length}`, 'ожидалось 3')
  say(
    creds.join(' ').includes('user@example.com') && creds.join(' ').includes('demo12345'),
    'указаны рабочие демо-учётные данные',
  )
  await page.screenshot({ path: `${SHOT}/02-contacts.png`, timeout: 90000 })

  // ── Регистрация ────────────────────────────────────────────────────────
  console.log('3. РЕГИСТРАЦИЯ')
  await go('/register', 'input[type="email"]')
  // Имя и фамилия должны быть разными полями: раньше оба писали в
  // fullName, и фамилия затирала имя.
  const nameInputs = await page
    .locator('input[autocomplete="given-name"], input[autocomplete="family-name"]')
    .count()
  say(nameInputs === 2, `отдельных полей имени и фамилии: ${nameInputs}`, 'ожидалось 2')
  const phoneInputs = await page.locator('input[autocomplete="tel"]').count()
  say(phoneInputs === 0, 'поля телефона нет — в модели такой колонки тоже нет')
  const orgInputs = await page.locator('input[autocomplete="organization"]').count()
  say(orgInputs === 1, 'поле организации есть — колонка в модели есть')

  await page.locator('input[autocomplete="given-name"]').fill('Пётр')
  await page.locator('input[autocomplete="family-name"]').fill('Тестов')
  await page.locator('input[autocomplete="organization"]').fill('ООО Проверка')
  await page.locator('input[type="email"]').fill(NEW_EMAIL)
  await page.locator('input[autocomplete="new-password"]').first().fill('parol12345')
  await page.locator('input[autocomplete="new-password"]').nth(1).fill('parol12345')
  // Согласие — не input[type=checkbox], а button[role=checkbox]. Раньше ссылки
  // из него вели в 404, поэтому проверяем, что документы открываются.
  const consentLinks = await page
    .locator('.rg-agree a')
    .evaluateAll((els) => [...new Set(els.map((e) => e.getAttribute('href')))])
  const deadConsent = []
  for (const href of consentLinks) {
    const r = await page.request.get(BASE + href)
    if (r.status() >= 400) deadConsent.push(`${href} → ${r.status()}`)
  }
  say(
    consentLinks.length >= 2 && deadConsent.length === 0,
    `документы согласия открываются: ${consentLinks.join(', ')}`,
    deadConsent.join('; ') || 'ссылок нет',
  )
  await page.locator('button[role="checkbox"]').click()
  say(
    (await page.locator('button[role="checkbox"]').getAttribute('aria-checked')) === 'true',
    'согласие отмечено',
  )
  await page.locator('button[type="submit"]').click()
  const authed = await page
    .waitForFunction(() => document.cookie.includes('access_token'), null, { timeout: 60000 })
    .then(() => true)
    .catch(() => false)
  say(authed, `регистрация ${NEW_EMAIL} выполнена`)
  const err = await page.locator('.rg-error').allInnerTexts().catch(() => [])
  say(err.length === 0, 'ошибок на форме нет', err[0] || '')

  // Вход новой учёткой: имя и организация должны сохраниться целиком
  if (authed) {
    await page.context().clearCookies()
    await go('/login', 'input[type="email"]')
    await page.locator('input[type="email"]').fill(NEW_EMAIL)
    await page.locator('input[type="password"]').fill('parol12345')
    await page.locator('button[type="submit"]').click()
    const back = await page
      .waitForFunction(() => document.cookie.includes('access_token'), null, { timeout: 60000 })
      .then(() => true)
      .catch(() => false)
    say(back, 'вход по новой учётной записи работает')
    await page.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 90000 })
    await page.waitForTimeout(4000)
    const header = await page.locator('header, .lb-headwrap').first().innerText().catch(() => '')
    const who = header.replace(/\n/g, ' ').trim()
    say(
      /Пётр Тестов/.test(who),
      `в шапке имя целиком: ${who.slice(0, 80)}`,
      `ожидали «Пётр Тестов», в шапке «${who.slice(0, 60)}»`,
    )
  }

  // ── Демо-подсказка на входе ────────────────────────────────────────────
  console.log('4. ПОДСКАЗКА НА ВХОДЕ')
  await page.context().clearCookies()
  await go('/login', '.rg-demo-fill')
  const demoBtn = page.locator('.rg-demo-fill')
  say((await demoBtn.count()) > 0, 'на странице входа есть демо-доступ')
  if (await demoBtn.count()) {
    await demoBtn.click()
    await page.waitForTimeout(400)
    const mail = await page.locator('input[type="email"]').inputValue()
    const pass = await page.locator('input[type="password"]').inputValue()
    say(
      mail === 'user@example.com' && pass === 'demo12345',
      `кнопка подставляет демо-данные: ${mail}`,
    )
  }

  console.log('5. ОШИБКИ В КОНСОЛИ')
  // Холодная загрузка в dev-сервере трансформирует чанки и иллюстрации по
  // требованию, и при медленной сети запрос успевает оборваться: страница
  // при этом полностью отрисовывается (проверено выше), но в консоль падает
  // «error loading dynamically imported module». Поэтому ошибки смотрим на
  // тёплом заходе, когда все модули уже скомпилированы.
  errs.length = 0
  await go('/', '.rm-stats__cell')
  await page.waitForTimeout(2500)
  if (!errs.length) say(true, 'на тёплом заходе ошибок нет')
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
