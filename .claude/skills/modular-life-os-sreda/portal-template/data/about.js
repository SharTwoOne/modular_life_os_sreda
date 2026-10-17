/* Страница «Обо мне». Значения переносятся из модуля about-me/ — только словами человека.
 * Всё ниже — ПРИМЕР. Заменить и удалить строку example: true.
 * Чего нет в файлах — оставь пустым, портал покажет «пока нет». Не выдумывай.
 */
window.ABOUT = {
  example: true,
  source: 'about-me/',

  name: 'Имя\nФамилия',          // крупно на первом экране, \n — перенос строки
  hit: 'Фамилия',                // кусок имени, который красится акцентом (можно пусто)
  oneLiner: 'Одна строка: кто я и чем занимаюсь. Его словами из about-me/profile.md.',
  facts: ['Город', 'Чем зарабатываю', 'Сколько лет в деле'],

  profile: [
    'Абзац о себе из about-me/profile.md.',
    'Второй абзац, если есть.',
  ],
  profileSource: 'about-me/profile.md',

  projects: [
    { name: 'Проект', what: 'Что это, одной строкой.', status: 'в работе' },
  ],

  goals: [
    { number: '01', text: 'Цель его словами.', when: 'к какому сроку и какая цифра' },
  ],
  goalsSource: 'about-me/goals.md',

  talk: {
    do: ['Как со мной говорить: пример из how-to-talk-to-me.md'],
    dont: ['Как не надо: пример из стоп-листа'],
  },
  talkSource: 'about-me/how-to-talk-to-me.md',

  quotes: ['Дословная фраза из about-me/verbatim.md.'],
  quotesSource: 'about-me/verbatim.md',
};
