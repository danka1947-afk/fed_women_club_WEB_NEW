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
        <div class="brand" aria-label="Женский клуб">
          <span class="brand-mark" aria-hidden="true">ЖК</span>
          <span>
            <span class="brand-name">Женский клуб</span>
            <span class="brand-caption">Федеральный клуб привилегий для девушек</span>
          </span>
        </div>
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
          <div class="city-select-shell">
            <span class="city-select-label" id="city-select-label">Город для каталога партнёров</span>
            <div class="city-choice-grid" role="radiogroup" aria-labelledby="city-select-label">
              ${cities
                .map(
                  (city, index) => `
                    <button
                      class="city-choice${index === 0 ? ' is-active' : ''}"
                      type="button"
                      role="radio"
                      aria-checked="${index === 0 ? 'true' : 'false'}"
                      data-city-choice
                    >
                      ${city}
                    </button>
                  `,
                )
                .join('')}
            </div>
          </div>
          <p class="city-select-note">Чем больше мы растём, тем больше городов подключаем. Скоро появятся новые города.</p>
        </div>
      </section>

      <section class="panel" aria-labelledby="login-title" id="login">
        <p class="section-kicker">Личный доступ</p>
        <h2 id="login-title">Вход в кабинет клуба</h2>
        <div class="login-mode-switch" role="tablist" aria-label="Тип входа">
          <button class="login-mode-button is-active" type="button" data-login-mode="admin" role="tab" aria-selected="true">Администратор</button>
          <button class="login-mode-button" type="button" data-login-mode="partner" role="tab" aria-selected="false">Партнёр</button>
        </div>
        <form class="login-form" data-login-form>
          <label>
            Телефон или email
            <input type="text" name="email" autocomplete="username" placeholder="name@example.com или +79990000000" required />
          </label>
          <label>
            Пароль
            <input type="password" name="password" autocomplete="current-password" placeholder="••••••••" required />
          </label>
          <button type="submit">Войти</button>
          <p class="login-message" data-login-message role="status" aria-live="polite"></p>
        </form>
        <div class="admin-dashboard" data-admin-dashboard hidden>
          <h3>Админ-панель</h3>
          <p>Вы вошли как: <strong data-admin-email></strong></p>
          <button type="button" data-logout-button>Выйти</button>
        </div>
        <div class="admin-dashboard partner-dashboard" data-partner-dashboard hidden></div>
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


document.querySelectorAll('[data-city-choice]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-city-choice]').forEach((choice) => {
      const isSelected = choice === button;

      choice.classList.toggle('is-active', isSelected);
      choice.setAttribute('aria-checked', String(isSelected));
    });
  });
});



const authTokenKey = 'womenClubAdminAccessToken';
const partnerTokenKey = 'womenclub_partner_token';
let activeLoginMode = 'admin';
const adminTabs = [
  { id: 'overview', label: 'Обзор' },
  { id: 'users', label: 'Пользователи' },
  { id: 'cities', label: 'Города' },
  { id: 'categories', label: 'Категории' },
  { id: 'partners', label: 'Партнёры' },
  { id: 'offers', label: 'Предложения' },
  { id: 'qr', label: 'QR / лиды' },
  { id: 'verifications', label: 'Подтверждения' },
];

const adminState = {
  activeTab: 'overview',
  user: null,
  users: [],
  cities: [],
  categories: [],
  partners: [],
  offers: [],
  qrLinks: [],
  leads: [],
  verifications: [],
  selectedPartnerIdForOffers: '',
  selectedPartnerIdForQr: '',
  panelMessage: '',
  formMessages: {},
  overviewPartialError: false,
};

const partnerTabs = [
  { id: 'profile', label: 'Профиль' },
  { id: 'offers', label: 'Предложения' },
  { id: 'qr', label: 'QR / лиды' },
  { id: 'verifications', label: 'Подтверждения' },
];

const partnerState = {
  activeTab: 'profile',
  user: null,
  profile: null,
  offers: [],
  qrLinks: [],
  leads: [],
  verifications: [],
  panelMessage: '',
  formMessages: {},
};

const loginForm = document.querySelector('[data-login-form]');
const loginModeButtons = document.querySelectorAll('[data-login-mode]');
const loginMessage = document.querySelector('[data-login-message]');
const adminDashboard = document.querySelector('[data-admin-dashboard]');
const adminEmail = document.querySelector('[data-admin-email]');
const logoutButton = document.querySelector('[data-logout-button]');
const partnerDashboard = document.querySelector('[data-partner-dashboard]');

const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const formatBool = (value) => (value ? 'да' : 'нет');
const formatValue = (value) => escapeHtml(value || '—');
const formatDate = (value) => (value ? new Date(value).toLocaleString('ru-RU') : '—');

const getToken = () => localStorage.getItem(authTokenKey);
const getPartnerToken = () => localStorage.getItem(partnerTokenKey);

const setLoginMessage = (message = '') => {
  loginMessage.textContent = message;
};

const setFormMessage = (formType, message = '') => {
  adminState.formMessages[formType] = message;
};

const setPanelMessage = (message = '', type = 'info') => {
  adminState.panelMessage = message
    ? `<div class="admin-status admin-status--${type}" role="status">${escapeHtml(message)}</div>`
    : '';
};

const clearToken = () => {
  localStorage.removeItem(authTokenKey);
};

const clearPartnerToken = () => {
  localStorage.removeItem(partnerTokenKey);
};

const setLoginMode = (mode) => {
  activeLoginMode = mode;
  loginModeButtons.forEach((button) => {
    const isActive = button.dataset.loginMode === mode;
    button.classList.toggle('is-active', isActive);
    button.setAttribute('aria-selected', String(isActive));
  });
};

const showLoginForm = () => {
  loginForm.hidden = false;
  adminDashboard.hidden = true;
  partnerDashboard.hidden = true;
  adminEmail.textContent = '';
  adminState.user = null;
  partnerState.user = null;
};

const buildErrorMessage = async (response) => {
  try {
    const data = await response.json();
    if (typeof data.detail === 'string') {
      return data.detail;
    }
  } catch (error) {
    // response body is not JSON
  }
  return `Ошибка ${response.status}`;
};

const apiFetch = async (path, options = {}) => {
  const token = getToken();
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(path, {
    ...options,
    headers,
  });

  if (response.status === 401 || response.status === 403) {
    clearToken();
    showLoginForm();
    throw new Error('Сессия истекла. Войдите снова.');
  }

  if (!response.ok) {
    throw new Error(await buildErrorMessage(response));
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
};


const setPartnerPanelMessage = (message = '', type = 'info') => {
  partnerState.panelMessage = message
    ? `<div class="admin-status admin-status--${type}" role="status">${escapeHtml(message)}</div>`
    : '';
};

const setPartnerFormMessage = (formType, message = '') => {
  partnerState.formMessages[formType] = message;
};

const partnerApiFetch = async (path, options = {}) => {
  const token = getPartnerToken();
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(path, {
    ...options,
    headers,
  });

  if (response.status === 401 || response.status === 403) {
    clearPartnerToken();
    showLoginForm();
    setLoginMode('partner');
    throw new Error('Сессия партнёра истекла. Войдите снова.');
  }

  if (!response.ok) {
    throw new Error(await buildErrorMessage(response));
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
};

const partnerPatchJson = (path, payload) => partnerApiFetch(path, {
  method: 'PATCH',
  body: JSON.stringify(payload),
});

const partnerPostJson = (path, payload = {}) => partnerApiFetch(path, {
  method: 'POST',
  body: JSON.stringify(payload),
});

const requestPartnerUserMe = () => partnerApiFetch('/api/v1/auth/user-me');
const loadPartnerProfile = async () => { partnerState.profile = await partnerApiFetch('/api/v1/partners/me'); };
const loadPartnerOffers = async () => { partnerState.offers = await partnerApiFetch('/api/v1/partners/me/offers'); };
const loadPartnerQrLinks = async () => { partnerState.qrLinks = await partnerApiFetch('/api/v1/partners/me/qr-links'); };
const loadPartnerLeads = async () => { partnerState.leads = await partnerApiFetch('/api/v1/partners/me/leads'); };
const loadPartnerVerifications = async () => { partnerState.verifications = await partnerApiFetch('/api/v1/partners/me/verifications'); };

const renderPartnerLayout = () => {
  partnerDashboard.innerHTML = `
    <div class="admin-header-card partner-header-card">
      <div>
        <p class="section-kicker">Кабинет партнёра</p>
        <h3>Кабинет партнёра</h3>
        <p>Вы вошли как: <strong>${escapeHtml(partnerState.user?.email || partnerState.user?.phone || 'партнёр')}</strong></p>
      </div>
      <button type="button" data-partner-logout-button>Выйти</button>
    </div>
    <nav class="admin-tabs" aria-label="Разделы кабинета партнёра">
      ${partnerTabs.map((tab) => `
        <button class="admin-tab${partnerState.activeTab === tab.id ? ' is-active' : ''}" type="button" data-partner-tab="${tab.id}">
          ${tab.label}
        </button>
      `).join('')}
    </nav>
    ${partnerState.panelMessage}
    <section class="admin-tab-panel">${renderPartnerTabContent()}</section>
  `;
};

const renderPartnerTabContent = () => {
  if (partnerState.activeTab === 'offers') {
    return renderPartnerOffersTab();
  }
  if (partnerState.activeTab === 'qr') {
    return renderPartnerQrTab();
  }
  if (partnerState.activeTab === 'verifications') {
    return renderPartnerVerificationsTab();
  }
  return renderPartnerProfileTab();
};

const renderPartnerProfileTab = () => {
  const profile = partnerState.profile || {};
  return `
    <div class="admin-two-column admin-two-column--wide">
      <div>
        <div class="admin-section-heading"><h4>Профиль</h4><p>Основная информация партнёра и поля, доступные для самостоятельного обновления.</p></div>
        <div class="partner-profile-grid">
          ${[
            ['Название', profile.name],
            ['Город', profile.city_name],
            ['Категория', profile.category_slug],
            ['Активность', formatBool(profile.is_active)],
            ['Верификация', formatBool(profile.is_verified)],
            ['Описание', profile.description],
            ['Адрес', profile.address],
            ['Телефон', profile.phone],
            ['Сайт', profile.website_url],
            ['Соцсети', profile.social_url],
            ['График', profile.working_hours],
          ].map(([label, value]) => `<article class="summary-card"><span>${escapeHtml(label)}</span><strong>${formatValue(value)}</strong></article>`).join('')}
        </div>
      </div>
      <form class="admin-form" data-partner-form="profile">
        <h4>Обновить профиль</h4>
        <label>description<textarea name="description" rows="4">${escapeHtml(profile.description || '')}</textarea></label>
        <label>address<input name="address" value="${escapeHtml(profile.address || '')}" /></label>
        <label>phone<input name="phone" autocomplete="tel" value="${escapeHtml(profile.phone || '')}" /></label>
        <label>website_url<input name="website_url" value="${escapeHtml(profile.website_url || '')}" /></label>
        <label>social_url<input name="social_url" value="${escapeHtml(profile.social_url || '')}" /></label>
        <label>working_hours<input name="working_hours" value="${escapeHtml(profile.working_hours || '')}" /></label>
        <label>logo_url<input name="logo_url" value="${escapeHtml(profile.logo_url || '')}" /></label>
        <label>cover_url<input name="cover_url" value="${escapeHtml(profile.cover_url || '')}" /></label>
        <button type="submit">Сохранить профиль</button>
        <p class="form-message" data-partner-form-message="profile">${escapeHtml(partnerState.formMessages.profile || '')}</p>
      </form>
    </div>
  `;
};

const renderPartnerOfferAction = (offer) => `
  <button class="admin-inline-action" type="button" data-partner-offer-toggle="${escapeHtml(offer.id)}">
    ${offer.is_active ? 'Скрыть' : 'Показать'}
  </button>
`;

const renderPartnerOffersTab = () => `
  <div class="admin-section-heading"><h4>Предложения</h4><p>Создавайте предложения и быстро скрывайте или показывайте их в каталоге.</p></div>
  ${renderTable(
    ['title', 'benefit_text', 'discount_percent', 'is_active', 'sort_order', 'action'],
    partnerState.offers.map((offer) => [formatValue(offer.title), formatValue(offer.benefit_text), formatValue(offer.discount_percent), formatValue(formatBool(offer.is_active)), formatValue(offer.sort_order), renderPartnerOfferAction(offer)]),
    true,
  )}
  <form class="admin-form admin-form--inline" data-partner-form="offer">
    <h4>Новое предложение</h4>
    <label>title<input name="title" required /></label>
    <label>benefit_text<input name="benefit_text" /></label>
    <label>description<textarea name="description" rows="3"></textarea></label>
    <label>conditions<textarea name="conditions" rows="3"></textarea></label>
    <label>base_price<input name="base_price" inputmode="decimal" /></label>
    <label>discount_percent<input name="discount_percent" inputmode="decimal" /></label>
    <label>image_url<input name="image_url" /></label>
    <label>sort_order<input name="sort_order" type="number" value="0" /></label>
    <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> active</label>
    <button type="submit">Создать предложение</button>
    <p class="form-message" data-partner-form-message="offer">${escapeHtml(partnerState.formMessages.offer || '')}</p>
  </form>
`;

const renderPartnerQrTab = () => `
  <div class="admin-section-heading"><h4>QR / лиды</h4><p>QR-ссылки создаёт администратор. Партнёр видит ссылки и статистику переходов.</p></div>
  ${renderTable(
    ['slug', 'qr_url', 'target_url', 'is_active'],
    partnerState.qrLinks.map((link) => [
      formatValue(link.slug),
      `<a href="${escapeHtml(link.qr_url)}" target="_blank" rel="noreferrer">${escapeHtml(link.qr_url)}</a>`,
      link.target_url ? `<a href="${escapeHtml(link.target_url)}" target="_blank" rel="noreferrer">${escapeHtml(link.target_url)}</a>` : '—',
      formatValue(formatBool(link.is_active)),
    ]),
    true,
  )}
  <h4 class="table-title">Лиды</h4>
  ${renderTable(['qr_slug', 'total_clicks'], partnerState.leads.map((lead) => [lead.qr_slug, lead.total_clicks]))}
`;

const renderPartnerVerificationAction = (verification) => verification.status === 'active'
  ? `<button class="admin-inline-action" type="button" data-partner-confirm-verification="${escapeHtml(verification.id)}">Подтвердить</button>`
  : '—';

const renderPartnerVerificationsTab = () => `
  <div class="admin-section-heading"><h4>Подтверждения</h4><p>Подтверждайте активные клиентские коды до окончания срока действия.</p></div>
  ${renderTable(
    ['code', 'status', 'client_name/client_id', 'offer_title', 'expires_at', 'confirmed_at', 'action'],
    partnerState.verifications.map((item) => [
      formatValue(item.code),
      formatValue(item.status),
      formatValue(item.client_name || item.client_id),
      formatValue(item.offer_title),
      formatValue(formatDate(item.expires_at)),
      formatValue(formatDate(item.confirmed_at)),
      renderPartnerVerificationAction(item),
    ]),
    true,
  )}
`;

const requestAdminMe = () => apiFetch('/api/v1/admin/me');

const postJson = (path, payload) => apiFetch(path, {
  method: 'POST',
  body: JSON.stringify(payload),
});

const patchJson = (path, payload) => apiFetch(path, {
  method: 'PATCH',
  body: JSON.stringify(payload),
});

const loadUsers = async () => {
  adminState.users = await apiFetch('/api/v1/admin/users');
};

const loadCities = async () => {
  adminState.cities = await apiFetch('/api/v1/admin/cities');
};

const loadCategories = async () => {
  adminState.categories = await apiFetch('/api/v1/admin/categories');
};

const loadPartners = async () => {
  adminState.partners = await apiFetch('/api/v1/admin/partners');
};

const loadLeads = async () => {
  adminState.leads = await apiFetch('/api/v1/admin/leads/partners');
};

const loadVerifications = async () => {
  adminState.verifications = await apiFetch('/api/v1/admin/verifications');
};

const loadOffers = async () => {
  if (!adminState.selectedPartnerIdForOffers) {
    adminState.offers = [];
    return;
  }
  adminState.offers = await apiFetch(`/api/v1/admin/partners/${adminState.selectedPartnerIdForOffers}/offers`);
};

const loadQrLinks = async () => {
  if (!adminState.selectedPartnerIdForQr) {
    adminState.qrLinks = [];
    return;
  }
  adminState.qrLinks = await apiFetch(`/api/v1/admin/partners/${adminState.selectedPartnerIdForQr}/qr-links`);
};

const ensureAdminDictionaries = async () => {
  await Promise.all([
    adminState.users.length ? Promise.resolve() : loadUsers(),
    adminState.cities.length ? Promise.resolve() : loadCities(),
    adminState.categories.length ? Promise.resolve() : loadCategories(),
    adminState.partners.length ? Promise.resolve() : loadPartners(),
  ]);
};

const renderAdminLayout = () => {
  const content = renderAdminTabContent();
  adminDashboard.innerHTML = `
    <div class="admin-header-card">
      <div>
        <p class="section-kicker">Кабинет клуба</p>
        <h3>Админ-панель</h3>
        <p>Вы вошли как: <strong data-admin-email>${escapeHtml(adminState.user?.email || '')}</strong></p>
      </div>
      <button type="button" data-logout-button>Выйти</button>
    </div>
    <nav class="admin-tabs" aria-label="Разделы админ-панели">
      ${adminTabs.map((tab) => `
        <button class="admin-tab${adminState.activeTab === tab.id ? ' is-active' : ''}" type="button" data-admin-tab="${tab.id}">
          ${tab.label}
        </button>
      `).join('')}
    </nav>
    ${adminState.panelMessage}
    <section class="admin-tab-panel">${content}</section>
  `;
};

const renderAdminTabContent = () => {
  switch (adminState.activeTab) {
    case 'users':
      return renderUsersTab();
    case 'cities':
      return renderCitiesTab();
    case 'categories':
      return renderCategoriesTab();
    case 'partners':
      return renderPartnersTab();
    case 'offers':
      return renderOffersTab();
    case 'qr':
      return renderQrTab();
    case 'verifications':
      return renderVerificationsTab();
    default:
      return renderOverviewTab();
  }
};

const renderOverviewTab = () => {
  const cards = [
    ['Пользователи', adminState.users.length],
    ['Города', adminState.cities.length],
    ['Категории', adminState.categories.length],
    ['Партнёры', adminState.partners.length],
    ['Подтверждения', adminState.verifications.length],
    ['Лиды', adminState.leads.reduce((sum, lead) => sum + Number(lead.total_clicks || 0), 0)],
  ];

  return `
    <div class="admin-section-heading">
      <h4>Обзор</h4>
      <p>${adminState.overviewPartialError ? 'Не удалось загрузить часть данных.' : 'Короткая сводка по справочникам и активности.'}</p>
    </div>
    <div class="summary-grid">
      ${cards.map(([label, value]) => `
        <article class="summary-card">
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
        </article>
      `).join('')}
    </div>
  `;
};

const renderUserActionButton = (user) => `
  <button class="admin-inline-action" type="button" data-user-active-toggle="${escapeHtml(user.id)}">
    ${user.is_active ? 'Заблокировать' : 'Активировать'}
  </button>
`;

const renderUsersTab = () => `
  <div class="admin-two-column admin-two-column--wide">
    <div>
      <div class="admin-section-heading"><h4>Пользователи</h4><p>Unified users для клиентских, партнёрских и административных кабинетов.</p></div>
      ${renderTable(
        ['id', 'email', 'phone', 'role', 'is_active', 'action'],
        adminState.users.map((item) => [
          formatValue(item.id),
          formatValue(item.email),
          formatValue(item.phone),
          formatValue(item.role),
          formatValue(formatBool(item.is_active)),
          renderUserActionButton(item),
        ]),
        true,
      )}
    </div>
    <form class="admin-form" data-admin-form="user">
      <h4>Новый пользователь</h4>
      <label>email<input name="email" type="email" autocomplete="email" /></label>
      <label>phone<input name="phone" autocomplete="tel" /></label>
      <label>password<input name="password" type="password" autocomplete="new-password" required /></label>
      <label>role${renderSelect('role', [['client', 'client'], ['partner', 'partner'], ['admin', 'admin']], true, 'client')}</label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> active</label>
      <button type="submit">Создать пользователя</button>
      <p class="form-message" data-form-message="user">${escapeHtml(adminState.formMessages.user || '')}</p>
    </form>
  </div>
`;

const renderCitiesTab = () => `
  <div class="admin-two-column">
    <div>
      <div class="admin-section-heading"><h4>Города</h4><p>Список городов для управления каталогом.</p></div>
      ${renderTable(['name', 'slug', 'active', 'sort_order'], adminState.cities.map((city) => [city.name, city.slug, formatBool(city.is_active), city.sort_order]))}
    </div>
    <form class="admin-form" data-admin-form="city">
      <h4>Новый город</h4>
      <label>name<input name="name" required /></label>
      <label>slug<input name="slug" required /></label>
      <label>sort_order<input name="sort_order" type="number" value="0" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> active</label>
      <button type="submit">Создать город</button>
      <p class="form-message" data-form-message="city">${escapeHtml(adminState.formMessages.city || '')}</p>
    </form>
  </div>
`;

const renderCategoriesTab = () => `
  <div class="admin-section-heading"><h4>Категории</h4><p>Read-only справочник категорий партнёров.</p></div>
  ${renderTable(['title', 'slug', 'sort_order'], adminState.categories.map((category) => [category.title, category.slug, category.sort_order]))}
`;

const renderPartnersTab = () => `
  <div class="admin-two-column admin-two-column--wide">
    <div>
      <div class="admin-section-heading"><h4>Партнёры</h4><p>Базовый список партнёров клуба.</p></div>
      ${renderTable(['name', 'city_name', 'category_slug', 'owner_email', 'active', 'verified'], adminState.partners.map((partner) => [partner.name, partner.city_name, partner.category_slug, partner.owner_email, formatBool(partner.is_active), formatBool(partner.is_verified)]))}
    </div>
    <form class="admin-form" data-admin-form="partner">
      <h4>Новый партнёр</h4>
      <label>city_id${renderSelect('city_id', adminState.cities.map((city) => [city.id, city.name]), true)}</label>
      <label>owner_user_id${renderSelect('owner_user_id', adminState.users.filter((item) => item.role === 'partner').map((item) => [item.id, item.email || item.phone || `partner #${item.id}`]), false, '', 'Без владельца')}</label>
      <label>category_slug${renderSelect('category_slug', adminState.categories.map((category) => [category.slug, category.title]), false)}</label>
      <label>name<input name="name" required /></label>
      <label>description<textarea name="description" rows="3"></textarea></label>
      <label>address<input name="address" /></label>
      <label>phone<input name="phone" /></label>
      <label>social_url<input name="social_url" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> active</label>
      <label class="checkbox-row"><input name="is_verified" type="checkbox" /> verified</label>
      <button type="submit">Создать партнёра</button>
      <p class="form-message" data-form-message="partner">${escapeHtml(adminState.formMessages.partner || '')}</p>
    </form>
  </div>
`;

const renderOffersTab = () => `
  <div class="admin-section-heading"><h4>Предложения</h4><p>Выберите партнёра, чтобы увидеть и создать предложения.</p></div>
  <label class="admin-select-label">Партнёр${renderPartnerPicker('offers', adminState.selectedPartnerIdForOffers)}</label>
  ${adminState.selectedPartnerIdForOffers ? `
    ${renderTable(['title', 'benefit_text', 'base_price', 'discount_percent', 'active', 'sort_order'], adminState.offers.map((offer) => [offer.title, offer.benefit_text, offer.base_price, offer.discount_percent, formatBool(offer.is_active), offer.sort_order]))}
    <form class="admin-form admin-form--inline" data-admin-form="offer">
      <h4>Новое предложение</h4>
      <label>title<input name="title" required /></label>
      <label>benefit_text<input name="benefit_text" /></label>
      <label>description<textarea name="description" rows="3"></textarea></label>
      <label>conditions<textarea name="conditions" rows="3"></textarea></label>
      <label>base_price<input name="base_price" type="number" step="0.01" /></label>
      <label>discount_percent<input name="discount_percent" type="number" step="0.01" /></label>
      <label>sort_order<input name="sort_order" type="number" value="0" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> active</label>
      <button type="submit">Создать предложение</button>
      <p class="form-message" data-form-message="offer">${escapeHtml(adminState.formMessages.offer || '')}</p>
    </form>
  ` : '<p class="empty-note">Сначала выберите партнёра.</p>'}
`;

const renderQrTab = () => `
  <div class="admin-section-heading"><h4>QR / лиды</h4><p>QR-ссылки партнёров и агрегированные переходы.</p></div>
  <label class="admin-select-label">Партнёр${renderPartnerPicker('qr', adminState.selectedPartnerIdForQr)}</label>
  ${adminState.selectedPartnerIdForQr ? `
    ${renderTable(['slug', 'qr_url', 'target_url', 'active'], adminState.qrLinks.map((link) => [formatValue(link.slug), link.qr_url ? `<a href="${escapeHtml(link.qr_url)}" target="_blank" rel="noreferrer">${escapeHtml(link.qr_url)}</a>` : '—', formatValue(link.target_url), formatValue(formatBool(link.is_active))]), true)}
    <form class="admin-form admin-form--inline" data-admin-form="qr">
      <h4>Новая QR-ссылка</h4>
      <label>slug optional<input name="slug" /></label>
      <label>target_url optional<input name="target_url" /></label>
      <label>deep_link_payload optional<input name="deep_link_payload" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> active</label>
      <button type="submit">Создать QR</button>
      <p class="form-message" data-form-message="qr">${escapeHtml(adminState.formMessages.qr || '')}</p>
    </form>
  ` : '<p class="empty-note">Сначала выберите партнёра.</p>'}
  <h4 class="table-title">Лиды партнёров</h4>
  ${renderTable(['partner_name', 'city_name', 'qr_slug', 'total_clicks'], adminState.leads.map((lead) => [lead.partner_name, lead.city_name, lead.qr_slug, lead.total_clicks]))}
`;

const renderVerificationsTab = () => `
  <div class="admin-section-heading"><h4>Подтверждения</h4><p>Последние сессии подтверждения привилегий.</p></div>
  ${renderTable(
    ['status', 'code', 'partner_name', 'client_name/client_id', 'offer_title', 'created_at', 'expires_at', 'confirmed_at'],
    adminState.verifications.map((item) => [item.status, item.code, item.partner_name, `${item.client_name || '—'} / ${item.client_id}`, item.offer_title, formatDate(item.created_at), formatDate(item.expires_at), formatDate(item.confirmed_at)]),
  )}
`;

const renderTable = (headers, rows, trustedHtml = false) => {
  if (!rows.length) {
    return '<p class="empty-note">Пока нет данных.</p>';
  }

  return `
    <div class="admin-table-wrap">
      <table class="admin-table">
        <thead><tr>${headers.map((header) => `<th>${escapeHtml(header)}</th>`).join('')}</tr></thead>
        <tbody>
          ${rows.map((row) => `<tr>${row.map((cell) => `<td>${trustedHtml ? cell : formatValue(cell)}</td>`).join('')}</tr>`).join('')}
        </tbody>
      </table>
    </div>
  `;
};

const renderSelect = (name, options, required = false, selectedValue = '', emptyLabel = null) => `
  <select name="${name}" ${required ? 'required' : ''}>
    <option value="">${emptyLabel || (required ? 'Выберите' : 'Без категории')}</option>
    ${options.map(([value, label]) => `<option value="${escapeHtml(value)}" ${String(value) === String(selectedValue) ? 'selected' : ''}>${escapeHtml(label)}</option>`).join('')}
  </select>
`;

const renderPartnerPicker = (scope, selectedValue) => `
  <select data-partner-picker="${scope}">
    <option value="">Выберите партнёра</option>
    ${adminState.partners.map((partner) => `<option value="${partner.id}" ${String(partner.id) === String(selectedValue) ? 'selected' : ''}>${escapeHtml(partner.name)}</option>`).join('')}
  </select>
`;

const showAdminDashboard = async (user) => {
  loginForm.hidden = true;
  adminDashboard.hidden = false;
  partnerDashboard.hidden = true;
  adminState.user = user;
  setLoginMessage();
  setPanelMessage();
  renderAdminLayout();
  await loadActiveTabData();
};

const showPartnerDashboard = async (user) => {
  loginForm.hidden = true;
  adminDashboard.hidden = true;
  partnerDashboard.hidden = false;
  partnerState.user = user;
  setLoginMessage();
  setPartnerPanelMessage();
  renderPartnerLayout();
  await loadActivePartnerTabData();
};

const loadOverview = async () => {
  adminState.overviewPartialError = false;
  const tasks = [loadUsers, loadCities, loadCategories, loadPartners, loadVerifications, loadLeads];
  const results = await Promise.allSettled(tasks.map((task) => task()));
  adminState.overviewPartialError = results.some((result) => result.status === 'rejected');
};

const loadActiveTabData = async () => {
  setPanelMessage();
  renderAdminLayout();

  try {
    if (adminState.activeTab === 'overview') {
      await loadOverview();
    } else if (adminState.activeTab === 'users') {
      await loadUsers();
    } else if (adminState.activeTab === 'cities') {
      await loadCities();
    } else if (adminState.activeTab === 'categories') {
      await loadCategories();
    } else if (adminState.activeTab === 'partners') {
      await ensureAdminDictionaries();
    } else if (adminState.activeTab === 'offers') {
      await ensureAdminDictionaries();
      if (!adminState.selectedPartnerIdForOffers && adminState.partners[0]) {
        adminState.selectedPartnerIdForOffers = String(adminState.partners[0].id);
      }
      await loadOffers();
    } else if (adminState.activeTab === 'qr') {
      await Promise.all([ensureAdminDictionaries(), loadLeads()]);
      if (!adminState.selectedPartnerIdForQr && adminState.partners[0]) {
        adminState.selectedPartnerIdForQr = String(adminState.partners[0].id);
      }
      await loadQrLinks();
    } else if (adminState.activeTab === 'verifications') {
      await loadVerifications();
    }
  } catch (error) {
    setPanelMessage(error.message || 'Не удалось загрузить данные.', 'error');
  }

  renderAdminLayout();
};


const loadActivePartnerTabData = async () => {
  setPartnerPanelMessage();
  renderPartnerLayout();

  try {
    if (partnerState.activeTab === 'profile') {
      await loadPartnerProfile();
    } else if (partnerState.activeTab === 'offers') {
      await loadPartnerOffers();
    } else if (partnerState.activeTab === 'qr') {
      await Promise.all([loadPartnerQrLinks(), loadPartnerLeads()]);
    } else if (partnerState.activeTab === 'verifications') {
      await loadPartnerVerifications();
    }
  } catch (error) {
    setPartnerPanelMessage(error.message || 'Не удалось загрузить данные.', 'error');
  }

  renderPartnerLayout();
};

const submitPartnerProfile = async (form) => {
  const formData = new FormData(form);
  await partnerPatchJson('/api/v1/partners/me', {
    description: getOptionalText(formData, 'description'),
    address: getOptionalText(formData, 'address'),
    phone: getOptionalText(formData, 'phone'),
    website_url: getOptionalText(formData, 'website_url'),
    social_url: getOptionalText(formData, 'social_url'),
    working_hours: getOptionalText(formData, 'working_hours'),
    logo_url: getOptionalText(formData, 'logo_url'),
    cover_url: getOptionalText(formData, 'cover_url'),
  });
  await loadPartnerProfile();
};

const submitPartnerOffer = async (form) => {
  const formData = new FormData(form);
  await partnerPostJson('/api/v1/partners/me/offers', {
    title: getOptionalText(formData, 'title'),
    benefit_text: getOptionalText(formData, 'benefit_text'),
    description: getOptionalText(formData, 'description'),
    conditions: getOptionalText(formData, 'conditions'),
    base_price: decimalOrNull(formData, 'base_price'),
    discount_percent: decimalOrNull(formData, 'discount_percent'),
    image_url: getOptionalText(formData, 'image_url'),
    is_active: formData.has('is_active'),
    sort_order: Number(formData.get('sort_order') || 0),
  });
  form.reset();
  await loadPartnerOffers();
};

const handlePartnerFormSubmit = async (form) => {
  const formType = form.dataset.partnerForm;
  setPartnerFormMessage(formType);

  try {
    if (formType === 'profile') {
      await submitPartnerProfile(form);
    } else if (formType === 'offer') {
      await submitPartnerOffer(form);
    }
    setPartnerFormMessage(formType, 'Сохранено.');
    setPartnerPanelMessage('Сохранено.', 'success');
  } catch (error) {
    setPartnerFormMessage(formType, error.message || 'Не удалось сохранить.');
    setPartnerPanelMessage(error.message || 'Не удалось сохранить.', 'error');
  }

  renderPartnerLayout();
};

const togglePartnerOffer = async (offerId) => {
  const offer = partnerState.offers.find((item) => String(item.id) === String(offerId));
  if (!offer) {
    return;
  }

  try {
    await partnerPatchJson(`/api/v1/partners/me/offers/${offerId}`, { is_active: !offer.is_active });
    await loadPartnerOffers();
    setPartnerPanelMessage(offer.is_active ? 'Предложение скрыто.' : 'Предложение опубликовано.', 'success');
  } catch (error) {
    setPartnerPanelMessage(error.message || 'Не удалось обновить предложение.', 'error');
  }

  renderPartnerLayout();
};

const confirmPartnerVerification = async (verificationId) => {
  try {
    await partnerPostJson(`/api/v1/partners/me/verifications/${verificationId}/confirm`);
    await loadPartnerVerifications();
    setPartnerPanelMessage('Подтверждение выполнено.', 'success');
  } catch (error) {
    setPartnerPanelMessage(error.message || 'Не удалось подтвердить код.', 'error');
  }

  renderPartnerLayout();
};

const getOptionalText = (formData, name) => {
  const value = String(formData.get(name) || '').trim();
  return value || null;
};

const submitCity = async (form) => {
  const formData = new FormData(form);
  await postJson('/api/v1/admin/cities', {
    name: getOptionalText(formData, 'name'),
    slug: getOptionalText(formData, 'slug'),
    sort_order: Number(formData.get('sort_order') || 0),
    is_active: formData.has('is_active'),
  });
  form.reset();
  await loadCities();
};

const submitUser = async (form) => {
  const formData = new FormData(form);
  await postJson('/api/v1/admin/users', {
    email: getOptionalText(formData, 'email'),
    phone: getOptionalText(formData, 'phone'),
    password: String(formData.get('password') || ''),
    role: getOptionalText(formData, 'role'),
    is_active: formData.has('is_active'),
  });
  form.reset();
  await loadUsers();
};

const toggleUserActive = async (userId) => {
  const currentUser = adminState.users.find((item) => String(item.id) === String(userId));
  if (!currentUser) {
    return;
  }

  try {
    await patchJson(`/api/v1/admin/users/${userId}`, {
      is_active: !currentUser.is_active,
    });
    await loadUsers();
    setPanelMessage(currentUser.is_active ? 'Пользователь заблокирован.' : 'Пользователь активирован.', 'success');
  } catch (error) {
    setPanelMessage(error.message || 'Не удалось обновить пользователя.', 'error');
  }

  renderAdminLayout();
};

const submitPartner = async (form) => {
  const formData = new FormData(form);
  await postJson('/api/v1/admin/partners', {
    city_id: Number(formData.get('city_id')),
    category_slug: getOptionalText(formData, 'category_slug'),
    name: getOptionalText(formData, 'name'),
    description: getOptionalText(formData, 'description'),
    address: getOptionalText(formData, 'address'),
    phone: getOptionalText(formData, 'phone'),
    social_url: getOptionalText(formData, 'social_url'),
    owner_user_id: formData.get('owner_user_id') ? Number(formData.get('owner_user_id')) : null,
    is_active: formData.has('is_active'),
    is_verified: formData.has('is_verified'),
  });
  form.reset();
  await loadPartners();
};

const decimalOrNull = (formData, name) => {
  const value = String(formData.get(name) || '').trim();
  return value || null;
};

const submitOffer = async (form) => {
  const formData = new FormData(form);
  await postJson(`/api/v1/admin/partners/${adminState.selectedPartnerIdForOffers}/offers`, {
    title: getOptionalText(formData, 'title'),
    benefit_text: getOptionalText(formData, 'benefit_text'),
    description: getOptionalText(formData, 'description'),
    conditions: getOptionalText(formData, 'conditions'),
    base_price: decimalOrNull(formData, 'base_price'),
    discount_percent: decimalOrNull(formData, 'discount_percent'),
    sort_order: Number(formData.get('sort_order') || 0),
    is_active: formData.has('is_active'),
  });
  form.reset();
  await loadOffers();
};

const submitQr = async (form) => {
  const formData = new FormData(form);
  await postJson(`/api/v1/admin/partners/${adminState.selectedPartnerIdForQr}/qr-links`, {
    slug: getOptionalText(formData, 'slug'),
    target_url: getOptionalText(formData, 'target_url'),
    deep_link_payload: getOptionalText(formData, 'deep_link_payload'),
    is_active: formData.has('is_active'),
  });
  form.reset();
  await loadQrLinks();
  await loadLeads();
};

const handleAdminFormSubmit = async (form) => {
  const formType = form.dataset.adminForm;
  const message = form.querySelector(`[data-form-message="${formType}"]`);
  setFormMessage(formType);
  if (message) {
    message.textContent = '';
  }

  try {
    if (formType === 'user') {
      await submitUser(form);
    } else if (formType === 'city') {
      await submitCity(form);
    } else if (formType === 'partner') {
      await submitPartner(form);
    } else if (formType === 'offer') {
      await submitOffer(form);
    } else if (formType === 'qr') {
      await submitQr(form);
    }
    setFormMessage(formType, 'Сохранено.');
    setPanelMessage('Сохранено.', 'success');
  } catch (error) {
    setFormMessage(formType, error.message || 'Не удалось сохранить.');
    if (message) {
      message.textContent = adminState.formMessages[formType];
    }
    setPanelMessage(error.message || 'Не удалось сохранить.', 'error');
  }

  renderAdminLayout();
};

loginModeButtons.forEach((button) => {
  button.addEventListener('click', () => {
    setLoginMode(button.dataset.loginMode);
    setLoginMessage();
  });
});

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  setLoginMessage();

  const formData = new FormData(loginForm);
  const loginValue = String(formData.get('email') || '').trim();
  const password = String(formData.get('password') || '');

  try {
    if (activeLoginMode === 'partner') {
      const response = await fetch('/api/v1/auth/user-login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ login: loginValue, password }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      localStorage.setItem(partnerTokenKey, data.access_token);

      if (data.user?.role !== 'partner') {
        clearPartnerToken();
        showLoginForm();
        setLoginMode('partner');
        setLoginMessage('Этот вход доступен только партнёрам');
        return;
      }

      await showPartnerDashboard(data.user);
      loginForm.reset();
      return;
    }

    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email: loginValue, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    localStorage.setItem(authTokenKey, data.access_token);
    await showAdminDashboard(data.user);
    loginForm.reset();
  } catch (error) {
    if (activeLoginMode === 'partner') {
      clearPartnerToken();
      showLoginForm();
      setLoginMode('partner');
    } else {
      clearToken();
      showLoginForm();
      setLoginMode('admin');
    }
    setLoginMessage('Неверный логин или пароль');
  }
});

adminDashboard.addEventListener('click', (event) => {
  const tabButton = event.target.closest('[data-admin-tab]');
  const logout = event.target.closest('[data-logout-button]');
  const userToggle = event.target.closest('[data-user-active-toggle]');

  if (userToggle) {
    toggleUserActive(userToggle.dataset.userActiveToggle);
    return;
  }

  if (logout) {
    clearToken();
    showLoginForm();
    return;
  }

  if (tabButton) {
    adminState.activeTab = tabButton.dataset.adminTab;
    loadActiveTabData();
  }
});

adminDashboard.addEventListener('change', (event) => {
  const picker = event.target.closest('[data-partner-picker]');
  if (!picker) {
    return;
  }

  if (picker.dataset.partnerPicker === 'offers') {
    adminState.selectedPartnerIdForOffers = picker.value;
  } else if (picker.dataset.partnerPicker === 'qr') {
    adminState.selectedPartnerIdForQr = picker.value;
  }

  loadActiveTabData();
});

adminDashboard.addEventListener('submit', (event) => {
  const form = event.target.closest('[data-admin-form]');
  if (!form) {
    return;
  }
  event.preventDefault();
  handleAdminFormSubmit(form);
});


partnerDashboard.addEventListener('click', (event) => {
  const tabButton = event.target.closest('[data-partner-tab]');
  const logout = event.target.closest('[data-partner-logout-button]');
  const offerToggle = event.target.closest('[data-partner-offer-toggle]');
  const confirmButton = event.target.closest('[data-partner-confirm-verification]');

  if (offerToggle) {
    togglePartnerOffer(offerToggle.dataset.partnerOfferToggle);
    return;
  }

  if (confirmButton) {
    confirmPartnerVerification(confirmButton.dataset.partnerConfirmVerification);
    return;
  }

  if (logout) {
    clearPartnerToken();
    showLoginForm();
    setLoginMode('partner');
    return;
  }

  if (tabButton) {
    partnerState.activeTab = tabButton.dataset.partnerTab;
    loadActivePartnerTabData();
  }
});

partnerDashboard.addEventListener('submit', (event) => {
  const form = event.target.closest('[data-partner-form]');
  if (!form) {
    return;
  }
  event.preventDefault();
  handlePartnerFormSubmit(form);
});

const restorePartnerSession = async () => {
  const token = getPartnerToken();
  if (!token) {
    showLoginForm();
    return;
  }

  try {
    const user = await requestPartnerUserMe();
    if (user.role !== 'partner') {
      clearPartnerToken();
      showLoginForm();
      return;
    }
    setLoginMode('partner');
    await showPartnerDashboard(user);
  } catch (error) {
    clearPartnerToken();
    showLoginForm();
  }
};

const restoreAdminSession = async () => {
  const token = getToken();
  if (!token) {
    await restorePartnerSession();
    return;
  }

  try {
    const user = await requestAdminMe();
    await showAdminDashboard(user);
  } catch (error) {
    clearToken();
    await restorePartnerSession();
  }
};

restoreAdminSession();
