const root = document.querySelector('#root');

const cities = [
  'Новосибирск',
  'Москва',
  'Санкт-Петербург',
  'Екатеринбург',
  'Казань',
];

const categories = [
  'Красота',
  'Маникюр / педикюр',
  'Волосы / окрашивание',
  'Брови / ресницы',
  'Косметология',
  'Массаж / SPA',
  'Фитнес / йога',
  'Здоровье',
  'Психология',
  'Одежда / аксессуары',
  'Кафе / рестораны',
  'Обучение / мастер-классы',
  'Фотосессии',
  'Цветы / подарки',
  'Другое',
];

root.innerHTML = `
  <main class="app-shell">
    <h1>Federal Women Club WEB</h1>
    <p>MVP web/backend skeleton based on club subscription platform.</p>

    <section aria-labelledby="city-selector-title">
      <h2 id="city-selector-title">Город</h2>
      <label>
        Выберите город для каталога партнёров
        <select name="city">
          ${cities.map((city) => `<option>${city}</option>`).join('')}
        </select>
      </label>
      <p>Подписка в MVP остаётся глобальной для клуба, не городской.</p>
    </section>

    <section aria-labelledby="categories-title">
      <h2 id="categories-title">Категории</h2>
      <ul>
        ${categories.map((category) => `<li>${category}</li>`).join('')}
      </ul>
    </section>
  </main>
`;
