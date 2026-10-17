/* Страница «Бренд». Значения переносятся из brand/style-reference.md — там истина, здесь витрина.
 * Всё ниже — ПРИМЕР. Заменить на стиль человека и удалить строку example: true.
 * Чего у человека нет — оставь пустой массив [], портал покажет «пока нет», а не выдумку.
 *
 * Разделы те же, что в style-reference.md:
 *   colors · canvases · type · shape · components · slides · rules
 */
window.BRAND = {
  example: true,
  source: 'brand/style-reference.md',

  /* шапка портала: mark — два слова в логотипе, второе красится акцентом; key — приставка для localStorage */
  portal: { title: 'MY OS', mark: ['MY', 'OS'], sub: 'личный портал', key: 'myos', theme: 'auto' },

  /* токены оболочки. ink — тёмная основа, white — светлая, accent — один акцент.
     onAccent — цвет текста на акценте (не задан — подберётся сам). light* — светлая тема интерфейса. */
  tokens: {
    ink: '#14161C', white: '#FFFFFF', accent: '#3D7BFF',
    darkCard: '#1D2029', divider: '#2C3040', ui400: '#9A9CA5', ui600: '#666A75',
    lightBg: '#FFFFFF', lightShell: '#ECEDF0', lightHover: '#E4E6EB', lightBorder: '#DADDE3', lightMuted: '#4A4C52',
  },

  /* шрифт бренда. css — ссылка Google Fonts; files — свои файлы рядом с порталом (fonts/…woff2).
     ui — шрифт интерфейса портала, если отличается (не задан — берётся family). */
  fonts: {
    family: 'Inter',
    css: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800;900&display=swap',
    files: [],
  },

  hero: { title: 'Пример\nстиля', hit: 'стиля', lead: 'Здесь две строки о том, на чём стоит стиль. Пока это пример.',
          pills: ['1080 × 1350', 'Inter', 'Три цвета'] },

  colors: {
    core: [
      { name: 'Ink', hex: '#14161C', use: 'Тёмная основа: фоны, текст на светлом' },
      { name: 'White', hex: '#FFFFFF', use: 'Светлая основа: фоны, текст на тёмном' },
      { name: 'Accent', hex: '#3D7BFF', use: 'Одно главное слово, кнопка, метка' },
    ],
    service: [
      { name: 'Card', hex: '#1D2029', use: 'Карточки на тёмном' },
      { name: 'Divider', hex: '#2C3040', use: 'Линии' },
      { name: 'Muted', hex: '#9A9CA5', use: 'Вторичный текст' },
      { name: 'Paper', hex: '#ECEDF0', use: 'Подложка на светлом' },
    ],
    rules: [
      { ok: true, text: 'Акцент один на кадр.' },
      { ok: false, text: 'Пятый цвет не заводим.' },
    ],
  },

  /* полотна: фоны, градиенты, фактуры. css — значение background целиком */
  canvases: [
    { name: 'Ночь', css: 'linear-gradient(160deg,#1D2029 0%,#14161C 70%)', use: 'Обложки, тёмные слайды' },
    { name: 'Туман', css: 'radial-gradient(ellipse at 30% 20%,#FFFFFF 0%,#ECEDF0 70%)', use: 'Спокойные текстовые слайды' },
  ],

  /* типографика. base — ширина холста, от которой считаны размеры (образцы рисуются в половину) */
  type: {
    family: 'Inter', note: 'Один шрифт на всё. Заголовки капсом, текст обычным регистром.',
    weights: [ { w: 300, label: 'Light' }, { w: 400, label: 'Regular' }, { w: 600, label: 'SemiBold' }, { w: 800, label: 'ExtraBold' } ],
    base: 1080,
    scale: [
      { role: 'Обложка', size: 120, weight: 800, lh: 0.95, caps: true, sample: 'Заголовок' },
      { role: 'Заголовок слайда', size: 64, weight: 800, lh: 1.05, caps: true, sample: 'Мысль слайда' },
      { role: 'Текст', size: 34, weight: 400, lh: 1.35, sample: 'Подводка обычным регистром' },
      { role: 'Подпись', size: 22, weight: 600, lh: 1.3, sample: '@nickname' },
    ],
  },

  /* холст и формы. pad — поля по бокам, padTop/padBottom — если отличаются */
  shape: {
    canvas: { w: 1080, h: 1350, label: 'Карусель', pad: 84 },
    facts: [ ['Поля', '84 px'], ['Шапка', '64 px от верха'], ['Сетка', 'шаг 12 px'] ],
    radii: [ { r: 0, use: 'Слайды и фото' }, { r: 16, use: 'Карточки' }, { r: 999, use: 'Пилюли и кнопки' } ],
  },

  /* компоненты: живая вёрстка. html кладётся в карточку как есть, css — общий для всех.
     light: true — показывать на светлой карточке. Цвета только из токенов выше. */
  components: {
    css: `
      .c-btn{background:#3D7BFF;color:#fff;font-weight:600;font-size:15px;padding:13px 24px;border-radius:999px}
      .c-tag{border:1px solid currentColor;font-size:12px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;padding:7px 14px;border-radius:999px}
      .c-count{background:#14161C;color:#fff;font-size:13px;font-weight:600;padding:6px 12px;border-radius:999px}
    `,
    items: [
      { name: 'Кнопка', desc: 'Accent · радиус 999 · 600', html: '<span class="c-btn">Записаться</span>' },
      { name: 'Метка', desc: 'Обводка цветом текста · капс 12 px', light: true, html: '<span class="c-tag">Новое</span>' },
      { name: 'Счётчик слайдов', desc: 'Ink · 13 px · 600', light: true, html: '<span class="c-count">01/10</span>' },
    ],
  },

  /* образцы носителя: w × h холста, вёрстка внутри в cqw (1cqw = 1% ширины): 1080 px → px / 10.8 cqw */
  slides: {
    w: 1080, h: 1350,
    css: `
      .s-pad{position:absolute;inset:7.8cqw}
      .s-h{font-weight:800;text-transform:uppercase;line-height:.95;letter-spacing:-.02em}
      .s-t{font-size:3.15cqw;line-height:1.35;opacity:.75;margin-top:2.4cqw}
      .s-nick{position:absolute;left:7.8cqw;bottom:5cqw;font-size:2cqw;font-weight:600;opacity:.6}
    `,
    items: [
      { name: 'Обложка', bg: 'linear-gradient(160deg,#1D2029 0%,#14161C 70%)',
        html: '<div class="s-pad" style="color:#fff"><div class="s-h" style="font-size:11cqw">Пример<br><span style="color:#3D7BFF">обложки</span></div></div><div class="s-nick" style="color:#fff">@nickname</div>' },
      { name: 'Текстовый', bg: '#FFFFFF',
        html: '<div class="s-pad" style="top:30cqw"><div class="s-h" style="font-size:5.9cqw">Одна мысль на слайд</div><div class="s-t">Подводка обычным регистром, две-три строки.</div></div>' },
      { name: 'Акцентный', bg: '#3D7BFF',
        html: '<div class="s-pad" style="top:34cqw;color:#fff"><div class="s-h" style="font-size:7.4cqw">Главное слово</div></div>' },
      { name: 'Финал', bg: '#14161C',
        html: '<div class="s-pad" style="top:40cqw;color:#fff"><div class="s-h" style="font-size:6cqw">Подпишись</div><div class="s-t" style="color:#fff">Здесь про то, чем я делюсь.</div></div>' },
    ],
  },

  rules: {
    can: ['Один акцент на кадр', 'Много воздуха вокруг заголовка'],
    cannot: ['Пятый цвет', 'Два шрифта на одном слайде'],
  },
};
