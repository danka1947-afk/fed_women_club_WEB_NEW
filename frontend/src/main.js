const root = document.querySelector('#root');

const cities = [
  'Новосибирск',
  'Череповец',
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

const featureCards = [
  {
    title: 'Скидки у партнёров',
    text: 'Скидки, подарки и специальные предложения у партнёров клуба.',
  },
  {
    title: 'Подарки и розыгрыши',
    text: 'Нежные beauty-бонусы, сезонные подборки и вдохновение для себя.',
  },
  {
    title: 'QR-подтверждение у партнёра',
    text: 'Аккуратная механика подтверждения привилегии без изменения backend-контрактов.',
  },
  {
    title: 'Выбор города',
    text: 'Выберите город и откройте доступ к предложениям рядом.',
  },
];

root.innerHTML = `
  <main class="app-shell">
    <header class="hero" aria-labelledby="hero-title">
      <nav class="topbar" aria-label="Основная навигация">
        <a class="brand" href="#hero-title" aria-label="Женский клуб">
          <span class="brand-mark" aria-hidden="true">ЖК</span>
          <span>
            <span class="brand-name">Женский клуб</span>
            <span class="brand-caption">Федеральный клуб привилегий для девушек</span>
          </span>
        </a>
        <div class="topbar-actions" aria-label="Разделы кабинета">
          <a href="#login">Вход</a>
        </div>
      </nav>

      <div class="hero-grid">
        <section class="hero-copy">
          <p class="eyebrow">Premium beauty / lifestyle</p>
          <h1 id="hero-title">Женский клуб</h1>
          <p class="subtitle">Федеральный клуб привилегий для девушек</p>
          <p class="hero-description">
            Красота, забота, отдых и вдохновение рядом с вами. Открывайте
            предложения партнёров клуба в своём городе и пользуйтесь
            привилегиями в светлом, бережном пространстве.
          </p>
          <div class="hero-actions">
            <a class="primary-button" href="#city-selector-title">Выберите город</a>
            <a class="secondary-button" href="#categories-title">Смотреть категории</a>
          </div>
        </section>

        <aside class="hero-card" aria-label="Карточка клуба">
          <div class="decor-line" aria-hidden="true"></div>
          <span class="soft-badge">для себя</span>
          <h2>Красота, забота и вдохновение</h2>
          <p>Скидки, подарки и специальные предложения у партнёров клуба.</p>
        </aside>
      </div>
    </header>

    <section class="feature-grid" aria-label="Возможности клуба">
      ${featureCards
        .map(
          (card) => `
            <article class="feature-card">
              <span aria-hidden="true"></span>
              <h2>${card.title}</h2>
              <p>${card.text}</p>
            </article>
          `,
        )
        .join('')}
    </section>

    <section class="content-grid">
      <section class="panel city-panel" aria-labelledby="city-selector-title">
        <p class="section-kicker">География клуба</p>
        <h2 id="city-selector-title">Выберите город</h2>
        <p>Выберите город и откройте доступ к предложениям рядом.</p>
        <div class="city-select-card">
          <label class="city-select-shell" for="city-select">
            <span class="city-select-label">Город для каталога партнёров</span>
            <span class="city-select-control">
              <select id="city-select" name="city">
                ${cities.map((city) => `<option>${city}</option>`).join('')}
              </select>
            </span>
          </label>
          <p class="city-select-note">Чем больше мы растём, тем больше городов подключаем. Скоро появятся новые города.</p>
        </div>
      </section>

      <section class="panel" aria-labelledby="login-title" id="login">
        <p class="section-kicker">Личный доступ</p>
        <h2 id="login-title">Вход в кабинет клуба</h2>
        <form class="login-form">
          <label>
            Телефон или email
            <input type="text" name="login" placeholder="name@example.com" />
          </label>
          <label>
            Пароль
            <input type="password" name="password" placeholder="••••••••" />
          </label>
          <button type="button">Войти</button>
        </form>
      </section>
    </section>

    <section class="panel categories-panel" aria-labelledby="categories-title">
      <p class="section-kicker">Направления</p>
      <h2 id="categories-title">Категории партнёров</h2>
      <ul class="category-list">
        ${categories.map((category) => `<li>${category}</li>`).join('')}
      </ul>
    </section>

  </main>
`;
