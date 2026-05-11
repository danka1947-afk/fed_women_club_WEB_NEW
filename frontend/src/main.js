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


const fallbackClientCities = [
  { id: 1, slug: 'novosibirsk', name: 'Новосибирск' },
  { id: 2, slug: 'cherepovets', name: 'Череповец' },
];

const fallbackClientCategories = [
  { slug: 'krasota', title: 'Красота' },
  { slug: 'manikyur-pedikyur', title: 'Маникюр / педикюр' },
  { slug: 'volosy-okrashivanie', title: 'Волосы / окрашивание' },
  { slug: 'brovi-resnitsy', title: 'Брови / ресницы' },
  { slug: 'kosmetologiya', title: 'Косметология' },
  { slug: 'massazh-spa', title: 'Массаж / SPA' },
  { slug: 'fitnes-yoga', title: 'Фитнес / йога' },
  { slug: 'zdorove', title: 'Здоровье' },
  { slug: 'psihologiya', title: 'Психология' },
  { slug: 'odezhda-aksessuary', title: 'Одежда / аксессуары' },
  { slug: 'kafe-restorany', title: 'Кафе / рестораны' },
  { slug: 'obuchenie-master-klassy', title: 'Обучение / мастер-классы' },
  { slug: 'fotosessii', title: 'Фотосессии' },
  { slug: 'cvety-podarki', title: 'Цветы / подарки' },
  { slug: 'drugoe', title: 'Другое' },
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


const sakuraEdgePetalMarkup = Array.from({ length: 68 }, (_, index) => (
  `<span class="sakura-petal sakura-petal--${index + 1}"></span>`
)).join('');

const sakuraCenterPetalMarkup = Array.from({ length: 20 }, (_, index) => (
  `<span class="sakura-petal sakura-petal--center sakura-petal--center-${index + 1}"></span>`
)).join('');

const sakuraPetalMarkup = `${sakuraEdgePetalMarkup}${sakuraCenterPetalMarkup}`;

const renderPublicApp = () => {
  document.body.classList.remove('is-dashboard');
  root.innerHTML = `
  <div class="sakura-layer" aria-hidden="true">
    ${sakuraPetalMarkup}
  </div>
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
          <button class="login-mode-button" type="button" data-login-mode="client" role="tab" aria-selected="false">Клиент</button>
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
        <div class="admin-dashboard client-dashboard" data-client-dashboard hidden></div>
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
  bindPublicElements();
};




const authTokenKey = 'womenClubAdminAccessToken';
const partnerTokenKey = 'womenclub_partner_token';
const clientTokenKey = 'womenclub_client_token';
let activeLoginMode = 'admin';
const adminTabs = [
  { id: 'overview', label: 'Главная', icon: '⌂' },
  { id: 'users', label: 'Пользователи', icon: '👥' },
  { id: 'cities', label: 'Города', icon: '⌖' },
  { id: 'categories', label: 'Категории', icon: '✦' },
  { id: 'partners', label: 'Партнёры', icon: '♡' },
  { id: 'offers', label: 'Предложения', icon: '%' },
  { id: 'qr', label: 'QR / лиды', icon: 'QR' },
  { id: 'verifications', label: 'Подтверждения', icon: '✓' },
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
  selectedQrLinkIdForEdit: '',
  selectedPartnerIdForEdit: '',
  selectedCityIdForEdit: '',
  selectedCategoryIdForEdit: '',
  selectedOfferIdForEdit: '',
  panelMessage: '',
  formMessages: {},
  overviewPartialError: false,
  search: {
    users: '',
    cities: '',
    categories: '',
    partners: '',
    offers: '',
    qr: '',
    leads: '',
    verifications: '',
  },
};

const normalizeSearchText = (value) => String(value ?? '').trim().toLowerCase();

const getSearchableValue = (row, field) => {
  if (typeof field === 'function') {
    return field(row);
  }

  return row?.[field];
};

const filterAdminRows = (rows, query, fields) => {
  const normalizedQuery = normalizeSearchText(query);
  if (!normalizedQuery) {
    return rows;
  }

  return rows.filter((row) => fields.some((field) => normalizeSearchText(getSearchableValue(row, field)).includes(normalizedQuery)));
};

const searchableBool = (value) => `${formatBool(value)} ${value ? 'active активен активна активно да true' : 'inactive неактивен неактивна неактивно нет false'}`;

const partnerTabs = [
  { id: 'profile', label: 'Профиль', icon: '♡' },
  { id: 'offers', label: 'Предложения', icon: '%' },
  { id: 'qr', label: 'QR / лиды', icon: 'QR' },
  { id: 'verifications', label: 'Подтверждения', icon: '✓' },
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

const clientTabs = [
  { id: 'profile', label: 'Профиль', icon: '♡' },
  { id: 'catalog', label: 'Каталог', icon: '✦' },
  { id: 'subscription', label: 'Моя подписка', icon: '₽' },
  { id: 'history', label: 'История', icon: '↺' },
];

const clientState = {
  activeTab: 'profile',
  user: null,
  profile: null,
  subscription: null,
  partners: [],
  offersByPartner: {},
  selectedPartner: null,
  latestVerification: null,
  vkLinkCode: null,
  vkLinkStatus: '',
  vkLinkMessage: '',
  verifications: [],
  catalogFilters: {
    q: '',
    category_slug: '',
    city_slug: '',
  },
  panelMessage: '',
  formMessages: {},
};

let loginForm = null;
let loginModeButtons = [];
let loginMessage = null;
let adminDashboard = null;
let partnerDashboard = null;
let clientDashboard = null;

const bindPublicElements = () => {
  loginForm = document.querySelector('[data-login-form]');
  loginModeButtons = document.querySelectorAll('[data-login-mode]');
  loginMessage = document.querySelector('[data-login-message]');
  adminDashboard = document.querySelector('[data-admin-dashboard]');
  partnerDashboard = document.querySelector('[data-partner-dashboard]');
  clientDashboard = document.querySelector('[data-client-dashboard]');
  setLoginMode(activeLoginMode);
};

const bindDashboardElements = () => {
  loginForm = null;
  loginModeButtons = [];
  loginMessage = null;
  adminDashboard = document.querySelector('[data-admin-dashboard]');
  partnerDashboard = document.querySelector('[data-partner-dashboard]');
  clientDashboard = document.querySelector('[data-client-dashboard]');
};

const escapeHtml = (value) => String(value ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#039;');

const formatBool = (value) => (value ? 'Активен' : 'Неактивен');
const formatActiveStatus = (value) => (value ? 'Активно' : 'Неактивно');
const formatActiveStatusFeminine = (value) => (value ? 'Активна' : 'Неактивна');
const formatVerifiedStatus = (value) => (value ? 'Проверен' : 'Не проверен');
const formatRole = (role) => ({
  client: 'Клиент',
  partner: 'Партнёр',
  admin: 'Администратор',
}[role] || role);
const formatValue = (value) => {
  if (value === null || value === undefined || value === '') return '—';
  return escapeHtml(value);
};
const formatDate = (value) => (value ? new Date(value).toLocaleString('ru-RU') : '—');


const statusLabels = {
  active: 'Активно',
  confirmed: 'Подтверждено',
  expired: 'Истекло',
  cancelled: 'Отменено',
  canceled: 'Отменено',
  paused: 'Приостановлено',
};

const formatStatus = (status) => {
  const normalized = String(status || '').trim().toLowerCase();
  if (!normalized) return '—';
  return statusLabels[normalized] || status;
};

const getClientCityOptions = () => {
  const stateCities = Array.isArray(adminState.cities) && adminState.cities.length
    ? adminState.cities.filter((city) => city.is_active !== false)
    : [];
  const baseCities = stateCities.length ? stateCities : fallbackClientCities;
  const profile = clientState.profile || {};
  const hasSelectedCity = profile.selected_city_id
    && !baseCities.some((city) => String(city.id) === String(profile.selected_city_id));

  return [
    ...baseCities,
    ...(hasSelectedCity ? [{ id: profile.selected_city_id, slug: '', name: profile.selected_city_name || 'Выбранный город' }] : []),
  ];
};

const getClientCategoryOptions = () => {
  const stateCategories = Array.isArray(adminState.categories) && adminState.categories.length
    ? adminState.categories.filter((category) => category.is_active !== false)
    : [];
  return stateCategories.length ? stateCategories : fallbackClientCategories;
};

const formatClientCategory = (slug) => {
  const category = getClientCategoryOptions().find((item) => item.slug === slug);
  return category?.title || slug || '—';
};

const formatPartnerCategory = (partner) => partner.category_title || partner.category_name || partner.category || partner.category_slug || '—';

const renderEmptyState = (title, text, icon = '♡') => `
  <article class="client-empty-state">
    <span class="client-empty-state__icon" aria-hidden="true">${escapeHtml(icon)}</span>
    <h4>${escapeHtml(title)}</h4>
    <p>${escapeHtml(text)}</p>
  </article>
`;

const renderClientEmptyState = (title, text) => renderEmptyState(title, text);
const renderPartnerEmptyState = (title, text) => renderEmptyState(title, text, '✦');

const getToken = () => localStorage.getItem(authTokenKey);
const getPartnerToken = () => localStorage.getItem(partnerTokenKey);
const getClientToken = () => localStorage.getItem(clientTokenKey);

const setLoginMessage = (message = '') => {
  if (loginMessage) {
    loginMessage.textContent = message;
  }
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

const clearClientToken = () => {
  localStorage.removeItem(clientTokenKey);
};

const setLoginMode = (mode) => {
  activeLoginMode = mode;
  loginModeButtons.forEach((button) => {
    const isActive = button.dataset.loginMode === mode;
    button.classList.toggle('is-active', isActive);
    button.setAttribute('aria-selected', String(isActive));
  });
};

const getRoleUser = (role) => {
  if (role === 'admin') return adminState.user;
  if (role === 'partner') return partnerState.user;
  return clientState.user;
};

const getRoleTitle = (role) => ({
  admin: 'Панель администратора',
  partner: 'Кабинет партнёра',
  client: 'Личный кабинет',
}[role]);

const getRoleTabs = (role) => ({
  admin: adminTabs,
  partner: partnerTabs,
  client: clientTabs,
}[role]);

const getActiveTab = (role) => ({
  admin: adminState.activeTab,
  partner: partnerState.activeTab,
  client: clientState.activeTab,
}[role]);

const getDashboardDataAttr = (role) => ({
  admin: 'data-admin-dashboard',
  partner: 'data-partner-dashboard',
  client: 'data-client-dashboard',
}[role]);

const getTabDataAttr = (role) => ({
  admin: 'data-admin-tab',
  partner: 'data-partner-tab',
  client: 'data-client-tab',
}[role]);

const getLogoutAttr = (role) => ({
  admin: 'data-logout-button',
  partner: 'data-partner-logout-button',
  client: 'data-client-logout-button',
}[role]);

const getRoleCaption = (role) => ({
  admin: 'Управление клубом, партнёрами и подтверждениями',
  partner: 'Рабочее место партнёра клуба',
  client: 'Персональный аккаунт с привилегиями',
}[role]);

const renderDashboardApp = (role) => {
  const user = getRoleUser(role) || {};
  const roleTitle = getRoleTitle(role);
  const roleCaption = getRoleCaption(role);
  const contact = user.email || user.phone || 'пользователь клуба';
  const dashboardAttr = getDashboardDataAttr(role);
  const tabAttr = getTabDataAttr(role);
  const logoutAttr = getLogoutAttr(role);
  const activeTab = getActiveTab(role);

  document.body.classList.add('is-dashboard');
  root.innerHTML = `
    <div class="dashboard-shell" data-dashboard-role="${role}">
      <header class="dashboard-topbar">
        <div class="dashboard-brand" aria-label="Женский клуб">
          <span class="brand-mark" aria-hidden="true">ЖК</span>
          <span>
            <span class="brand-name">Женский клуб</span>
            <span class="brand-caption">Федеральный клуб привилегий для девушек</span>
          </span>
        </div>
        <div class="dashboard-title-block">
          <p class="section-kicker">Кабинет клуба</p>
          <h1>${roleTitle}</h1>
          <p class="dashboard-role-caption">${roleCaption}</p>
        </div>
        <div class="dashboard-user-block">
          <span>${escapeHtml(contact)}</span>
          <button type="button" ${logoutAttr}>Выйти</button>
        </div>
      </header>
      <div class="dashboard-layout">
        <aside class="dashboard-sidebar" aria-label="Разделы кабинета">
          <div class="dashboard-sidebar-heading">
            <span>Навигация</span>
            <strong>${roleTitle}</strong>
          </div>
          <nav class="dashboard-nav" aria-label="Меню кабинета">
            ${getRoleTabs(role).map((tab) => `
              <button class="dashboard-nav-button${activeTab === tab.id ? ' is-active' : ''}" type="button" ${tabAttr}="${tab.id}">
                <span class="dashboard-nav-icon" aria-hidden="true">${tab.icon || '•'}</span>
                <span>${tab.label}</span>
              </button>
            `).join('')}
          </nav>
        </aside>
        <main class="dashboard-main">
          <div class="admin-dashboard ${role}-dashboard" ${dashboardAttr}></div>
        </main>
      </div>
    </div>
  `;
  bindDashboardElements();
};

const showLoginForm = () => {
  adminState.user = null;
  partnerState.user = null;
  clientState.user = null;
  renderPublicApp();
  setLoginMessage();
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

const setClientPanelMessage = (message = '', type = 'info') => {
  clientState.panelMessage = message
    ? `<div class="admin-status admin-status--${type}" role="status">${escapeHtml(message)}</div>`
    : '';
};

const setClientFormMessage = (formType, message = '') => {
  clientState.formMessages[formType] = message;
};

const clientApiFetch = async (path, options = {}) => {
  const token = getClientToken();
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
    clearClientToken();
    showLoginForm();
    setLoginMode('client');
    throw new Error('Сессия клиента истекла. Войдите снова.');
  }

  if (!response.ok) {
    throw new Error(await buildErrorMessage(response));
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
};

const clientPatchJson = (path, payload) => clientApiFetch(path, {
  method: 'PATCH',
  body: JSON.stringify(payload),
});

const clientPostJson = (path, payload = {}) => clientApiFetch(path, {
  method: 'POST',
  body: JSON.stringify(payload),
});

const requestPartnerUserMe = () => partnerApiFetch('/api/v1/auth/user-me');
const loadPartnerProfile = async () => { partnerState.profile = await partnerApiFetch('/api/v1/partners/me'); };
const loadPartnerOffers = async () => { partnerState.offers = await partnerApiFetch('/api/v1/partners/me/offers'); };
const loadPartnerQrLinks = async () => { partnerState.qrLinks = await partnerApiFetch('/api/v1/partners/me/qr-links'); };
const loadPartnerLeads = async () => { partnerState.leads = await partnerApiFetch('/api/v1/partners/me/leads'); };
const loadPartnerVerifications = async () => { partnerState.verifications = await partnerApiFetch('/api/v1/partners/me/verifications'); };

const requestClientUserMe = () => clientApiFetch('/api/v1/auth/user-me');
const loadClientProfile = async () => { clientState.profile = await clientApiFetch('/api/v1/clients/me'); };
const loadClientSubscription = async () => { clientState.subscription = await clientApiFetch('/api/v1/clients/me/subscription'); };
const loadClientVerifications = async () => { clientState.verifications = await clientApiFetch('/api/v1/clients/me/verifications'); };

const buildClientCatalogPath = () => {
  const params = new URLSearchParams();
  const { q, category_slug: categorySlug, city_slug: citySlug } = clientState.catalogFilters;
  if (q) params.set('q', q);
  if (categorySlug) params.set('category_slug', categorySlug);
  if (citySlug && citySlug !== '__all__') params.set('city_slug', citySlug);
  if (!citySlug && clientState.profile?.selected_city_id) {
    params.set('city_id', clientState.profile.selected_city_id);
  }
  const query = params.toString();
  return `/api/v1/clients/catalog/partners${query ? `?${query}` : ''}`;
};

const loadClientCatalog = async () => {
  if (!clientState.profile) {
    await loadClientProfile();
  }
  clientState.partners = await clientApiFetch(buildClientCatalogPath());
};

const loadClientPartnerOffers = async (partnerId) => {
  clientState.offersByPartner[partnerId] = await clientApiFetch(`/api/v1/clients/partners/${partnerId}/offers`);
};

const renderClientLayout = () => {
  renderDashboardApp('client');
  clientDashboard.innerHTML = `
    ${clientState.panelMessage}
    <section class="admin-tab-panel">${renderClientTabContent()}</section>
  `;
};

const renderClientTabContent = () => {
  if (clientState.activeTab === 'catalog') {
    return renderClientCatalogTab();
  }
  if (clientState.activeTab === 'subscription') {
    return renderClientSubscriptionTab();
  }
  if (clientState.activeTab === 'history') {
    return renderClientHistoryTab();
  }
  return renderClientProfileTab();
};

const renderClientProfileTab = () => {
  const profile = clientState.profile || {};
  const cityOptions = getClientCityOptions();
  return `
    <div class="admin-section-heading">
      <h4>Профиль</h4>
      <p>Выберите город, чтобы видеть предложения рядом с вами.</p>
    </div>
    <div class="partner-profile-grid">
      ${[
        ['Email', profile.email],
        ['Телефон', profile.phone],
        ['Имя', profile.full_name],
        ['Город', profile.selected_city_name || 'Выберите город'],
        ['Источник', profile.source],
        ['Активность', formatBool(profile.is_active)],
      ].map(([label, value]) => `
        <div class="summary-card"><span>${label}</span><strong>${formatValue(value)}</strong></div>
      `).join('')}
    </div>
    <section class="client-vk-link-card" aria-labelledby="client-vk-link-title">
      <div class="client-vk-link-header">
        <div>
          <h4 id="client-vk-link-title">Привязка VK</h4>
          <p>Создайте одноразовый код и отправьте его VK-боту командой: Привязать КОД</p>
        </div>
        <button type="button" data-client-create-vk-code>Создать код для VK</button>
      </div>
      ${renderClientVkLinkCode()}
    </section>
    <form class="admin-form admin-form--inline" data-client-form="profile">
      <h4>Обновить профиль</h4>
      <label>Имя<input name="full_name" value="${escapeHtml(profile.full_name || '')}" /></label>
      <label>Город
        <select name="selected_city_id">
          <option value="">Выберите город</option>
          ${cityOptions.map((city) => `<option value="${escapeHtml(city.id)}" ${String(city.id) === String(profile.selected_city_id || '') ? 'selected' : ''}>${escapeHtml(city.name)}</option>`).join('')}
        </select>
      </label>
      <p class="form-message">Выберите город, чтобы видеть предложения рядом с вами.</p>
      <button type="submit">Сохранить профиль</button>
      <p class="form-message" data-client-form-message="profile">${escapeHtml(clientState.formMessages.profile || '')}</p>
    </form>
  `;
};

const renderClientVkLinkCode = () => {
  const statusClass = clientState.vkLinkStatus ? ` client-vk-link-message--${clientState.vkLinkStatus}` : '';
  const message = clientState.vkLinkMessage
    ? `<p class="client-vk-link-message${statusClass}">${escapeHtml(clientState.vkLinkMessage)}</p>`
    : '';

  if (!clientState.vkLinkCode) {
    return message;
  }

  const { code, expires_at: expiresAt, ttl_seconds: ttlSeconds } = clientState.vkLinkCode;
  return `
    <div class="client-vk-link-result">
      <span class="client-vk-link-code">${escapeHtml(code)}</span>
      <dl class="client-vk-link-meta">
        <div><dt>Истекает</dt><dd>${formatValue(formatDate(expiresAt))}</dd></div>
        <div><dt>TTL, сек.</dt><dd>${formatValue(ttlSeconds)}</dd></div>
      </dl>
      <p>Скопируйте код и отправьте VK-боту: <strong>Привязать ${escapeHtml(code)}</strong></p>
      <p class="client-warning">Код действует 10 минут. Новый код отменяет предыдущий.</p>
      ${message}
    </div>
  `;
};

const renderClientSubscriptionTab = () => {
  const subscription = clientState.subscription;
  if (!subscription) {
    return `
      <div class="admin-section-heading"><h4>Моя подписка</h4><p>Информация о вашей клубной подписке.</p></div>
      ${renderClientEmptyState('Активная подписка пока не найдена', 'Когда подписка будет оформлена, здесь появится срок действия и статус.')}
    `;
  }

  return `
    <div class="admin-section-heading"><h4>Моя подписка</h4><p>Статус и сроки текущей подписки.</p></div>
    <div class="summary-grid">
      <div class="summary-card"><span>Статус</span><strong>${formatValue(formatStatus(subscription.status))}</strong></div>
      <div class="summary-card"><span>Начало</span><strong>${formatValue(formatDate(subscription.starts_at))}</strong></div>
      <div class="summary-card"><span>Окончание</span><strong>${formatValue(formatDate(subscription.ends_at))}</strong></div>
    </div>
  `;
};

const renderClientCatalogTab = () => {
  const cityOptions = getClientCityOptions();
  const categoryOptions = getClientCategoryOptions();
  return `
    <div class="admin-section-heading">
      <h4>Каталог</h4>
      <p>Ищите партнёров по названию, категории и городу.</p>
    </div>
    <form class="admin-form client-catalog-filter" data-client-form="catalog">
      <label>Поиск<input name="q" value="${escapeHtml(clientState.catalogFilters.q)}" placeholder="Название, описание, адрес" /></label>
      <label>Категория
        <select name="category_slug">
          <option value="">Все категории</option>
          ${categoryOptions.map((category) => `<option value="${escapeHtml(category.slug)}" ${clientState.catalogFilters.category_slug === category.slug ? 'selected' : ''}>${escapeHtml(category.title)}</option>`).join('')}
        </select>
      </label>
      <label>Город
        <select name="city_slug">
          <option value="">По выбранному городу</option>
          <option value="__all__" ${clientState.catalogFilters.city_slug === '__all__' ? 'selected' : ''}>Все города</option>
          ${cityOptions.filter((city) => city.slug).map((city) => `<option value="${escapeHtml(city.slug)}" ${clientState.catalogFilters.city_slug === city.slug ? 'selected' : ''}>${escapeHtml(city.name)}</option>`).join('')}
        </select>
      </label>
      <button type="submit">Найти</button>
    </form>
    ${clientState.latestVerification ? renderClientVerificationResult(clientState.latestVerification) : ''}
    <div class="client-catalog-grid">
      ${clientState.partners.length ? clientState.partners.map(renderClientPartnerCard).join('') : renderClientEmptyState('Партнёры пока не найдены', 'Попробуйте изменить город, категорию или поисковый запрос.')}
    </div>
  `;
};

const renderClientPartnerCard = (partner) => {
  const partnerId = partner.id;
  const offers = clientState.offersByPartner[partnerId] || [];
  return `
    <article class="client-partner-card">
      <div class="client-card-topline">
        <span>${formatValue(formatClientCategory(partner.category_slug))}</span>
        <span>${partner.is_verified ? 'Проверен' : 'На проверке'}</span>
      </div>
      <h4>${formatValue(partner.name)}</h4>
      <p>${formatValue(partner.description)}</p>
      <dl class="client-card-details">
        <div><dt>Город</dt><dd>${formatValue(partner.city_name)}</dd></div>
        <div><dt>Адрес</dt><dd>${formatValue(partner.address)}</dd></div>
        <div><dt>Телефон</dt><dd>${formatValue(partner.phone)}</dd></div>
        <div><dt>Соцсети</dt><dd>${partner.social_url ? `<a href="${escapeHtml(partner.social_url)}" target="_blank" rel="noreferrer">${escapeHtml(partner.social_url)}</a>` : '—'}</dd></div>
      </dl>
      <div class="client-card-actions">
        <button type="button" data-client-load-offers="${escapeHtml(partnerId)}">Открыть предложения</button>
        <button type="button" data-client-verify-partner="${escapeHtml(partnerId)}">Подтвердить привилегию</button>
      </div>
      ${offers.length ? `<div class="client-offer-list">${offers.map((offer) => renderClientOffer(partnerId, offer)).join('')}</div>` : ''}
    </article>
  `;
};

const renderClientOffer = (partnerId, offer) => `
  <div class="client-offer-card">
    <h5>${formatValue(offer.title)}</h5>
    <p><strong>${formatValue(offer.benefit_text)}</strong></p>
    <p>${formatValue(offer.description)}</p>
    <p class="client-offer-meta">Условия: ${formatValue(offer.conditions)} · Цена: ${formatValue(offer.base_price)} · Скидка: ${formatValue(offer.discount_percent)}</p>
    <button type="button" data-client-verify-offer="${escapeHtml(partnerId)}" data-offer-id="${escapeHtml(offer.id)}">Подтвердить привилегию</button>
  </div>
`;

const renderClientVerificationResult = (verification) => `
  <div class="client-verification-result" role="status">
    <p class="section-kicker">Привилегия подтверждена</p>
    <h4>Код: ${formatValue(verification.code)}</h4>
    <p>Действует до: <strong>${formatValue(formatDate(verification.expires_at))}</strong> · TTL: <strong>${formatValue(verification.ttl_seconds)}</strong> сек.</p>
    <p>Партнёр: <strong>${formatValue(verification.partner_name)}</strong> · Предложение: <strong>${formatValue(verification.offer_title)}</strong></p>
    <p class="client-warning">Покажите этот код сотруднику партнёра. Код действует 5 минут.</p>
  </div>
`;

const renderClientHistoryTab = () => `
  <div class="admin-section-heading"><h4>История</h4><p>Ваши последние подтверждения привилегий.</p></div>
  ${renderTable(
    ['Код', 'Статус', 'Партнёр', 'Название предложения', 'Истекает', 'Подтверждено', 'Создано'],
    clientState.verifications.map((item) => [item.code, formatStatus(item.status), item.partner_name, item.offer_title, formatDate(item.expires_at), formatDate(item.confirmed_at), formatDate(item.created_at)]),
    false,
    '',
    'Пока нет подтверждений.',
  )}
`;

const renderPartnerLayout = () => {
  renderDashboardApp('partner');
  partnerDashboard.innerHTML = `
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
            ['Категория', formatPartnerCategory(profile)],
            ['Адрес', profile.address],
            ['Телефон', profile.phone],
            ['Сайт / соцсеть', profile.website_url || profile.social_url],
            ['Активность', formatBool(profile.is_active)],
            ['Проверка', formatVerifiedStatus(profile.is_verified)],
            ['Описание', profile.description],
            ['График', profile.working_hours],
          ].map(([label, value]) => `<article class="summary-card"><span>${escapeHtml(label)}</span><strong>${formatValue(value)}</strong></article>`).join('')}
        </div>
      </div>
      <form class="admin-form" data-partner-form="profile">
        <h4>Обновить профиль</h4>
        <p class="form-message">Название, город, категория, активность и проверка редактируются администратором.</p>
        <label>Описание<textarea name="description" rows="4">${escapeHtml(profile.description || '')}</textarea></label>
        <label>Адрес<input name="address" value="${escapeHtml(profile.address || '')}" /></label>
        <label>Телефон<input name="phone" autocomplete="tel" value="${escapeHtml(profile.phone || '')}" /></label>
        <label>Сайт<input name="website_url" value="${escapeHtml(profile.website_url || '')}" /></label>
        <label>Соцсеть<input name="social_url" value="${escapeHtml(profile.social_url || '')}" /></label>
        <label>График работы<input name="working_hours" value="${escapeHtml(profile.working_hours || '')}" /></label>
        <label>Логотип<input name="logo_url" value="${escapeHtml(profile.logo_url || '')}" /></label>
        <label>Обложка<input name="cover_url" value="${escapeHtml(profile.cover_url || '')}" /></label>
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
  ${partnerState.offers.length ? renderTable(
    ['Название', 'Краткая выгода', 'Описание', 'Условия', 'Базовая цена', 'Активно', 'Порядок сортировки', 'Действие'],
    partnerState.offers.map((offer) => [
      formatValue(offer.title),
      formatValue(offer.benefit_text),
      formatValue(offer.description),
      formatValue(offer.conditions),
      formatValue(offer.base_price),
      formatValue(formatActiveStatus(offer.is_active)),
      formatValue(offer.sort_order),
      renderPartnerOfferAction(offer),
    ]),
    true,
  ) : renderPartnerEmptyState('Пока нет предложений.', 'Добавьте первое предложение, чтобы клиенты видели его в каталоге.')}
  <form class="admin-form admin-form--inline" data-partner-form="offer">
    <h4>Новое предложение</h4>
    <label>Название<input name="title" required /></label>
    <label>Краткая выгода<input name="benefit_text" /></label>
    <label>Описание<textarea name="description" rows="3"></textarea></label>
    <label>Условия<textarea name="conditions" rows="3"></textarea></label>
    <label>Базовая цена<input name="base_price" inputmode="decimal" /></label>
    <label>Скидка, %<input name="discount_percent" inputmode="decimal" /></label>
    <label>Изображение<input name="image_url" /></label>
    <label>Порядок сортировки<input name="sort_order" type="number" value="0" /></label>
    <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Активно</label>
    <button type="submit">Создать предложение</button>
    <p class="form-message" data-partner-form-message="offer">${escapeHtml(partnerState.formMessages.offer || '')}</p>
  </form>
`;

const renderPartnerQrTab = () => `
  <div class="admin-section-heading"><h4>QR / лиды</h4><p>QR-ссылки создаёт администратор. Партнёр видит ссылки и статистику переходов.</p></div>
  ${partnerState.qrLinks.length ? renderTable(
    ['Код ссылки', 'QR-ссылка', 'Целевая ссылка', 'Deep-link payload', 'Активна'],
    partnerState.qrLinks.map((link) => [
      formatValue(link.slug),
      link.qr_url ? `<a href="${escapeHtml(link.qr_url)}" target="_blank" rel="noreferrer">${escapeHtml(link.qr_url)}</a>` : '—',
      link.target_url ? `<a href="${escapeHtml(link.target_url)}" target="_blank" rel="noreferrer">${escapeHtml(link.target_url)}</a>` : '—',
      formatValue(link.deep_link_payload),
      formatValue(formatActiveStatusFeminine(link.is_active)),
    ]),
    true,
  ) : renderPartnerEmptyState('Пока нет QR-ссылок.', 'Создайте QR-ссылку, чтобы отслеживать переходы от клиентов.')}
  <h4 class="table-title">Лиды</h4>
  ${partnerState.leads.length ? renderTable(
    ['Код ссылки', 'Лиды / переходы'],
    partnerState.leads.map((lead) => [formatValue(lead.qr_slug), formatValue(lead.total_clicks)]),
    true,
  ) : renderPartnerEmptyState('Пока нет лидов.', 'Когда клиенты перейдут по QR-ссылке, они появятся здесь.')}
`;

const renderPartnerVerificationAction = (verification) => verification.status === 'active'
  ? `<button class="admin-inline-action" type="button" data-partner-confirm-verification="${escapeHtml(verification.id)}">Подтвердить привилегию</button>`
  : '—';

const renderPartnerVerificationsTab = () => `
  <div class="admin-section-heading"><h4>Подтверждения</h4><p>Подтверждайте активные клиентские коды до окончания срока действия.</p></div>
  ${partnerState.verifications.length ? renderTable(
    ['Код', 'Статус', 'Клиент', 'Название предложения', 'Истекает', 'Подтверждено', 'Действие'],
    partnerState.verifications.map((item) => [
      formatValue(item.code),
      formatValue(formatStatus(item.status)),
      formatValue(item.client_name || item.client_id),
      formatValue(item.offer_title),
      formatValue(formatDate(item.expires_at)),
      formatValue(formatDate(item.confirmed_at)),
      renderPartnerVerificationAction(item),
    ]),
    true,
  ) : renderPartnerEmptyState('Пока нет подтверждений.', 'Когда клиент покажет код привилегии, подтверждение появится здесь.')}
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
  if (adminState.selectedCityIdForEdit && !adminState.cities.some((city) => String(city.id) === String(adminState.selectedCityIdForEdit))) {
    adminState.selectedCityIdForEdit = '';
  }
};

const loadCategories = async () => {
  adminState.categories = await apiFetch('/api/v1/admin/categories');
  if (adminState.selectedCategoryIdForEdit && !adminState.categories.some((category) => String(category.id) === String(adminState.selectedCategoryIdForEdit))) {
    adminState.selectedCategoryIdForEdit = '';
  }
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
    adminState.selectedOfferIdForEdit = '';
    return;
  }
  adminState.offers = await apiFetch(`/api/v1/admin/partners/${adminState.selectedPartnerIdForOffers}/offers`);
  if (adminState.selectedOfferIdForEdit && !adminState.offers.some((offer) => String(offer.id) === String(adminState.selectedOfferIdForEdit))) {
    adminState.selectedOfferIdForEdit = '';
  }
};

const loadQrLinks = async () => {
  if (!adminState.selectedPartnerIdForQr) {
    adminState.qrLinks = [];
    adminState.selectedQrLinkIdForEdit = '';
    return;
  }
  adminState.qrLinks = await apiFetch(`/api/v1/admin/partners/${adminState.selectedPartnerIdForQr}/qr-links`);
  if (adminState.selectedQrLinkIdForEdit && !adminState.qrLinks.some((link) => String(link.id) === String(adminState.selectedQrLinkIdForEdit))) {
    adminState.selectedQrLinkIdForEdit = '';
  }
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
  renderDashboardApp('admin');
  const content = renderAdminTabContent();
  adminDashboard.innerHTML = `
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
    ['Пользователи', adminState.users.length, 'Аккаунты всех ролей'],
    ['Города', adminState.cities.length, 'Активная география'],
    ['Категории', adminState.categories.length, 'Направления каталога'],
    ['Партнёры', adminState.partners.length, 'CRM-база клуба'],
    ['Подтверждения', adminState.verifications.length, 'Сессии привилегий'],
    ['Лиды', adminState.leads.reduce((sum, lead) => sum + Number(lead.total_clicks || 0), 0), 'Переходы по QR'],
  ];
  const quickActions = [
    ['users', 'Пользователи', 'Создать или активировать аккаунт'],
    ['partners', 'Партнёры', 'Добавить партнёра и владельца'],
    ['cities', 'Города', 'Настроить географию клуба'],
    ['qr', 'QR / лиды', 'Посмотреть QR-ссылки и лиды'],
  ];

  return `
    <div class="admin-section-heading admin-page-heading">
      <p class="section-kicker">CRM overview</p>
      <h4>Обзор</h4>
      <p>${adminState.overviewPartialError ? 'Не удалось загрузить часть данных.' : 'Короткая сводка по справочникам и активности.'}</p>
    </div>
    <div class="summary-grid">
      ${cards.map(([label, value, caption]) => `
        <article class="summary-card">
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
          <small>${escapeHtml(caption)}</small>
        </article>
      `).join('')}
    </div>
    <section class="quick-actions-panel" aria-labelledby="quick-actions-title">
      <div class="admin-section-heading">
        <h4 id="quick-actions-title">Быстрые действия</h4>
        <p>Самые частые административные разделы в один клик.</p>
      </div>
      <div class="quick-actions-grid">
        ${quickActions.map(([tab, label, caption]) => `
          <button class="quick-action-card" type="button" data-admin-tab="${tab}">
            <span>${escapeHtml(label)}</span>
            <strong>${escapeHtml(caption)}</strong>
          </button>
        `).join('')}
      </div>
    </section>
  `;
};

const renderUserActionButton = (user) => `
  <button class="admin-inline-action admin-table-action" type="button" data-user-active-toggle="${escapeHtml(user.id)}">
    ${user.is_active ? 'Заблокировать' : 'Активировать'}
  </button>
`;

const renderAdminSearch = (scope, placeholder) => {
  const value = adminState.search?.[scope] || '';
  return `
    <div class="admin-toolbar">
      <label class="admin-search">
        <span class="visually-hidden">${escapeHtml(placeholder)}</span>
        <input class="admin-search-input" data-admin-search="${escapeHtml(scope)}" value="${escapeHtml(value)}" placeholder="${escapeHtml(placeholder)}" />
      </label>
      ${value ? `<button class="admin-search-reset" type="button" data-admin-search-reset="${escapeHtml(scope)}">Сбросить</button>` : ''}
    </div>
  `;
};

const renderUsersTab = () => {
  const users = filterAdminRows(adminState.users, adminState.search.users, ['email', 'phone', 'role', (item) => formatRole(item.role), (item) => searchableBool(item.is_active)]);
  return `
    <div class="admin-two-column admin-two-column--wide">
      <div>
        <div class="admin-section-heading"><h4>Пользователи</h4><p>Unified users для клиентских, партнёрских и административных кабинетов.</p></div>
        ${renderAdminSearch('users', 'Поиск по пользователям')}
        ${renderTable(
          ['ID', 'Email', 'Телефон', 'Роль', 'Активен', 'Действие'],
          users.map((item) => [
            formatValue(item.id),
            formatValue(item.email),
            formatValue(item.phone),
            formatValue(formatRole(item.role)),
            formatValue(formatBool(item.is_active)),
            renderUserActionButton(item),
          ]),
          true,
          'admin-table--compact',
          adminState.search.users ? 'Ничего не найдено.' : 'Пока нет данных.',
        )}
      </div>
      <form class="admin-form" data-admin-form="user">
        <h4>Новый пользователь</h4>
        <label>Email<input name="email" type="email" autocomplete="email" /></label>
        <label>Телефон<input name="phone" autocomplete="tel" /></label>
        <label>Пароль<input name="password" type="password" autocomplete="new-password" required /></label>
        <label>Роль${renderSelect('role', [['client', 'Клиент'], ['partner', 'Партнёр'], ['admin', 'Администратор']], true, 'client')}</label>
        <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Активен</label>
        <button type="submit">Создать пользователя</button>
        <p class="form-message" data-form-message="user">${escapeHtml(adminState.formMessages.user || '')}</p>
      </form>
    </div>
  `;
};

const renderCityActionButtons = (city) => `
  <div class="admin-inline-actions">
    <button class="admin-inline-action admin-table-action" type="button" data-admin-city-edit="${escapeHtml(city.id)}">Редактировать</button>
    <button class="admin-inline-action admin-table-action" type="button" data-admin-city-active-toggle="${escapeHtml(city.id)}">
      ${city.is_active ? 'Деактивировать' : 'Активировать'}
    </button>
  </div>
`;

const renderCityCreateForm = () => `
  <form class="admin-form" data-admin-form="city">
    <h4>Новый город</h4>
    <label>Название города<input name="name" required /></label>
    <label>Слаг / код города<input name="slug" required /></label>
    <label>Порядок сортировки<input name="sort_order" type="number" value="0" /></label>
    <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Активен</label>
    <button type="submit">Создать город</button>
    <p class="form-message" data-form-message="city">${escapeHtml(adminState.formMessages.city || '')}</p>
  </form>
`;

const renderCityEditForm = () => {
  const city = adminState.cities.find((item) => String(item.id) === String(adminState.selectedCityIdForEdit));
  if (!city) {
    return '';
  }

  return `
    <form class="admin-form" data-admin-form="cityEdit" data-city-id="${escapeHtml(city.id)}">
      <h4>Редактировать город</h4>
      <label>Название<input name="name" value="${escapeHtml(city.name || '')}" required /></label>
      <label>Slug<input name="slug" value="${escapeHtml(city.slug || '')}" required /></label>
      <label>Порядок сортировки<input name="sort_order" type="number" value="${escapeHtml(city.sort_order ?? 0)}" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" ${city.is_active ? 'checked' : ''} /> Активен</label>
      <div class="admin-form-actions">
        <button type="submit">Сохранить изменения</button>
        <button class="admin-inline-action" type="button" data-admin-city-edit-cancel>Отмена</button>
      </div>
      <p class="form-message" data-form-message="cityEdit">${escapeHtml(adminState.formMessages.cityEdit || '')}</p>
    </form>
  `;
};

const renderCitiesTab = () => {
  const cities = filterAdminRows(adminState.cities, adminState.search.cities, ['name', 'slug', (city) => searchableBool(city.is_active)]);
  return `
    <div class="admin-two-column">
      <div>
        <div class="admin-section-heading"><h4>Города</h4><p>Список городов для управления каталогом.</p></div>
        ${renderAdminSearch('cities', 'Поиск по городам')}
        ${renderTable(
          ['Город', 'Слаг', 'Активен', 'Сортировка', 'Действие'],
          cities.map((city) => [
            formatValue(city.name),
            formatValue(city.slug),
            formatValue(formatBool(city.is_active)),
            formatValue(city.sort_order),
            renderCityActionButtons(city),
          ]),
          true,
          'admin-table--compact',
          adminState.search.cities ? 'Ничего не найдено.' : 'Пока нет данных.',
        )}
      </div>
      ${adminState.selectedCityIdForEdit ? renderCityEditForm() : renderCityCreateForm()}
    </div>
  `;
};

const getCategoryName = (category) => category.name || category.title || '';

const renderCategoryActionButtons = (category) => `
  <div class="admin-inline-actions">
    <button class="admin-inline-action admin-table-action" type="button" data-admin-category-edit="${escapeHtml(category.id)}">Редактировать</button>
    <button class="admin-inline-action admin-table-action" type="button" data-admin-category-active-toggle="${escapeHtml(category.id)}">
      ${category.is_active ? 'Деактивировать' : 'Активировать'}
    </button>
  </div>
`;

const renderCategoryCreateForm = () => `
  <form class="admin-form" data-admin-form="category">
    <h4>Новая категория</h4>
    <label>Название<input name="name" required /></label>
    <label>Slug<input name="slug" required /></label>
    <label>Порядок сортировки<input name="sort_order" type="number" value="0" /></label>
    <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Активна</label>
    <button type="submit">Создать категорию</button>
    <p class="form-message" data-form-message="category">${escapeHtml(adminState.formMessages.category || '')}</p>
  </form>
`;

const renderCategoryEditForm = () => {
  const category = adminState.categories.find((item) => String(item.id) === String(adminState.selectedCategoryIdForEdit));
  if (!category) {
    return '';
  }

  return `
    <form class="admin-form" data-admin-form="categoryEdit" data-category-id="${escapeHtml(category.id)}">
      <h4>Редактировать категорию</h4>
      <label>Название<input name="name" value="${escapeHtml(getCategoryName(category))}" required /></label>
      <label>Slug<input name="slug" value="${escapeHtml(category.slug || '')}" required /></label>
      <label>Порядок сортировки<input name="sort_order" type="number" value="${escapeHtml(category.sort_order ?? 0)}" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" ${category.is_active ? 'checked' : ''} /> Активна</label>
      <div class="admin-form-actions">
        <button type="submit">Сохранить изменения</button>
        <button class="admin-inline-action" type="button" data-admin-category-edit-cancel>Отмена</button>
      </div>
      <p class="form-message" data-form-message="categoryEdit">${escapeHtml(adminState.formMessages.categoryEdit || '')}</p>
    </form>
  `;
};

const renderCategoriesTab = () => {
  const categories = filterAdminRows(adminState.categories, adminState.search.categories, ['name', 'title', 'slug', (category) => searchableBool(category.is_active)]);
  return `
    <div class="admin-two-column">
      <div>
        <div class="admin-section-heading"><h4>Категории</h4><p>Справочник категорий партнёров с безопасной деактивацией.</p></div>
        ${renderAdminSearch('categories', 'Поиск по категориям')}
        ${renderTable(
          ['Категория', 'Слаг', 'Активна', 'Сортировка', 'Действие'],
          categories.map((category) => [
            formatValue(getCategoryName(category)),
            formatValue(category.slug),
            formatValue(formatBool(category.is_active)),
            formatValue(category.sort_order),
            renderCategoryActionButtons(category),
          ]),
          true,
          'admin-table--compact',
          adminState.search.categories ? 'Ничего не найдено.' : 'Пока нет данных.',
        )}
      </div>
      ${adminState.selectedCategoryIdForEdit ? renderCategoryEditForm() : renderCategoryCreateForm()}
    </div>
  `;
};

const renderAdminPartnerAction = (partner) => `
  <button class="admin-inline-action admin-table-action" type="button" data-admin-partner-edit="${escapeHtml(partner.id)}">Редактировать</button>
`;

const renderPartnerEditForm = () => {
  const partner = adminState.partners.find((item) => String(item.id) === String(adminState.selectedPartnerIdForEdit));
  if (!partner) {
    return '';
  }

  return `
    <form class="admin-form" data-admin-form="partnerEdit" data-partner-id="${escapeHtml(partner.id)}">
      <h4>Редактировать партнёра</h4>
      <label>Город${renderSelect('city_id', adminState.cities.map((city) => [city.id, city.name]), true, partner.city_id)}</label>
      <label>Категория${renderSelect('category_slug', adminState.categories.map((category) => [category.slug, category.title]), false, partner.category_slug)}</label>
      <label>Владелец${renderSelect('owner_user_id', adminState.users.filter((item) => item.role === 'partner').map((item) => [item.id, item.email || item.phone || `Партнёр #${item.id}`]), false, partner.owner_user_id || '', 'Без владельца')}</label>
      <label>Название<input name="name" required value="${escapeHtml(partner.name || '')}" /></label>
      <label>Описание<textarea name="description" rows="3">${escapeHtml(partner.description || '')}</textarea></label>
      <label>Адрес<input name="address" value="${escapeHtml(partner.address || '')}" /></label>
      <label>Телефон<input name="phone" value="${escapeHtml(partner.phone || '')}" /></label>
      <label>Сайт<input name="website_url" value="${escapeHtml(partner.website_url || '')}" /></label>
      <label>Соцсеть<input name="social_url" value="${escapeHtml(partner.social_url || '')}" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" ${partner.is_active ? 'checked' : ''} /> Активен</label>
      <label class="checkbox-row"><input name="is_verified" type="checkbox" ${partner.is_verified ? 'checked' : ''} /> Проверен</label>
      <div class="admin-form-actions">
        <button type="submit">Сохранить изменения</button>
        <button class="admin-inline-action" type="button" data-admin-partner-edit-cancel>Отмена</button>
      </div>
      <p class="form-message" data-form-message="partnerEdit">${escapeHtml(adminState.formMessages.partnerEdit || '')}</p>
    </form>
  `;
};

const renderPartnersTab = () => {
  const partners = filterAdminRows(adminState.partners, adminState.search.partners, [
    'name',
    'city_name',
    'category_slug',
    'owner_email',
    'phone',
    (partner) => searchableBool(partner.is_active),
    (partner) => (partner.is_verified ? 'verified проверен проверенный true' : 'unverified не проверен непроверенный false'),
  ]);
  return `
    <div class="admin-two-column admin-two-column--wide">
      <div>
        <div class="admin-section-heading"><h4>Партнёры</h4><p>Базовый список партнёров клуба.</p></div>
        ${renderAdminSearch('partners', 'Поиск по партнёрам')}
        ${renderTable(
          ['Партнёр', 'Город', 'Категория', 'Владелец', 'Активен', 'Проверен', 'Действие'],
          partners.map((partner) => [
            formatValue(partner.name),
            formatValue(partner.city_name),
            formatValue(partner.category_slug),
            formatValue(partner.owner_email),
            formatValue(formatBool(partner.is_active)),
            formatValue(partner.is_verified ? 'Проверен' : 'Не проверен'),
            renderAdminPartnerAction(partner),
          ]),
          true,
          'admin-table--compact',
          adminState.search.partners ? 'Ничего не найдено.' : 'Пока нет данных.',
        )}
      </div>
      ${adminState.selectedPartnerIdForEdit ? renderPartnerEditForm() : `
    <form class="admin-form" data-admin-form="partner">
      <h4>Новый партнёр</h4>
      <label>Город${renderSelect('city_id', adminState.cities.map((city) => [city.id, city.name]), true)}</label>
      <label>Владелец / аккаунт партнёра${renderSelect('owner_user_id', adminState.users.filter((item) => item.role === 'partner').map((item) => [item.id, item.email || item.phone || `Партнёр #${item.id}`]), false, '', 'Без владельца')}</label>
      <label>Категория${renderSelect('category_slug', adminState.categories.map((category) => [category.slug, category.title]), false)}</label>
      <label>Название партнёра<input name="name" required /></label>
      <label>Описание<textarea name="description" rows="3"></textarea></label>
      <label>Адрес<input name="address" /></label>
      <label>Телефон<input name="phone" /></label>
      <label>Ссылка на соцсеть / сайт<input name="social_url" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Активен</label>
      <label class="checkbox-row"><input name="is_verified" type="checkbox" /> Проверен</label>
      <button type="submit">Создать партнёра</button>
      <p class="form-message" data-form-message="partner">${escapeHtml(adminState.formMessages.partner || '')}</p>
    </form>
    `}
    </div>
  `;
};

const renderAdminOfferAction = (offer) => `
  <button class="admin-inline-action admin-table-action" type="button" data-admin-offer-edit="${escapeHtml(offer.id)}">Редактировать</button>
`;

const renderOfferEditForm = () => {
  const offer = adminState.offers.find((item) => String(item.id) === String(adminState.selectedOfferIdForEdit));
  if (!offer) {
    return '';
  }

  return `
    <form class="admin-form admin-form--inline" data-admin-form="offerEdit" data-offer-id="${escapeHtml(offer.id)}">
      <h4>Редактировать предложение</h4>
      <label>Название<input name="title" required value="${escapeHtml(offer.title || '')}" /></label>
      <label>Скидка / выгода<input name="benefit_text" value="${escapeHtml(offer.benefit_text || '')}" /></label>
      <label>Описание<textarea name="description" rows="3">${escapeHtml(offer.description || '')}</textarea></label>
      <label>Условия<textarea name="conditions" rows="3">${escapeHtml(offer.conditions || '')}</textarea></label>
      <label>Порядок сортировки<input name="sort_order" type="number" value="${escapeHtml(offer.sort_order || 0)}" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" ${offer.is_active ? 'checked' : ''} /> Активно</label>
      <div class="admin-form-actions">
        <button type="submit">Сохранить изменения</button>
        <button class="admin-inline-action" type="button" data-admin-offer-edit-cancel>Отмена</button>
      </div>
      <p class="form-message" data-form-message="offerEdit">${escapeHtml(adminState.formMessages.offerEdit || '')}</p>
    </form>
  `;
};

const renderOfferCreateForm = () => `
  <form class="admin-form admin-form--inline" data-admin-form="offer">
    <h4>Новое предложение</h4>
    <label>Название предложения<input name="title" required /></label>
    <label>Краткая выгода<input name="benefit_text" /></label>
    <label>Описание<textarea name="description" rows="3"></textarea></label>
    <label>Условия<textarea name="conditions" rows="3"></textarea></label>
    <label>Базовая цена<input name="base_price" type="number" step="0.01" /></label>
    <p class="form-message">Цена со скидкой рассчитывается по базовой цене и проценту скидки.</p>
    <label>Скидка, %<input name="discount_percent" type="number" step="0.01" /></label>
    <label>Порядок сортировки<input name="sort_order" type="number" value="0" /></label>
    <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Активен</label>
    <button type="submit">Создать предложение</button>
    <p class="form-message" data-form-message="offer">${escapeHtml(adminState.formMessages.offer || '')}</p>
  </form>
`;

const renderOffersTab = () => {
  const offers = filterAdminRows(adminState.offers, adminState.search.offers, ['title', 'description', 'benefit_text', 'discount_text', 'terms', 'conditions', (offer) => searchableBool(offer.is_active)]);
  return `
    <div class="admin-section-heading"><h4>Предложения</h4><p>Выберите партнёра, чтобы увидеть и создать предложения.</p></div>
    <label class="admin-select-label">Партнёр${renderPartnerPicker('offers', adminState.selectedPartnerIdForOffers)}</label>
    ${adminState.selectedPartnerIdForOffers ? `
      ${renderAdminSearch('offers', 'Поиск по предложениям')}
      ${renderTable(
        ['Название предложения', 'Описание', 'Базовая цена', 'Скидка, %', 'Активно', 'Сортировка', 'Действие'],
        offers.map((offer) => [formatValue(offer.title), formatValue(offer.benefit_text), formatValue(offer.base_price), formatValue(offer.discount_percent), formatValue(formatBool(offer.is_active)), formatValue(offer.sort_order), renderAdminOfferAction(offer)]),
        true,
        'admin-table--compact',
        adminState.search.offers ? 'Ничего не найдено.' : 'Пока нет данных.',
      )}
      ${adminState.selectedOfferIdForEdit ? renderOfferEditForm() : renderOfferCreateForm()}
    ` : '<p class="empty-note">Сначала выберите партнёра.</p>'}
  `;
};

const renderAdminQrAction = (link) => `
  <button class="admin-inline-action admin-table-action" type="button" data-admin-qr-edit="${escapeHtml(link.id)}">Редактировать</button>
`;

const renderQrCreateForm = () => `
  <form class="admin-form admin-form--inline" data-admin-form="qr">
    <h4>Новая QR-ссылка</h4>
    <label>Код ссылки<input name="slug" /></label>
    <label>Целевая ссылка<input name="target_url" /></label>
    <label>Deep link payload / payload<input name="deep_link_payload" /></label>
    <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Активен</label>
    <button type="submit">Создать QR</button>
    <p class="form-message" data-form-message="qr">${escapeHtml(adminState.formMessages.qr || '')}</p>
  </form>
`;

const renderQrEditForm = () => {
  const link = adminState.qrLinks.find((item) => String(item.id) === String(adminState.selectedQrLinkIdForEdit));
  if (!link) {
    return '';
  }

  return `
    <form class="admin-form admin-form--inline" data-admin-form="qrEdit" data-qr-link-id="${escapeHtml(link.id)}">
      <h4>Редактировать QR-ссылку</h4>
      <label>Slug<input name="slug" value="${escapeHtml(link.slug || '')}" /></label>
      <label>Целевая ссылка<input name="target_url" value="${escapeHtml(link.target_url || '')}" /></label>
      <label>Deep-link payload<input name="deep_link_payload" value="${escapeHtml(link.deep_link_payload || '')}" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" ${link.is_active ? 'checked' : ''} /> Активна</label>
      <div class="admin-form-actions">
        <button type="submit">Сохранить изменения</button>
        <button class="admin-inline-action" type="button" data-admin-qr-edit-cancel>Отмена</button>
      </div>
      <p class="form-message" data-form-message="qrEdit">${escapeHtml(adminState.formMessages.qrEdit || '')}</p>
    </form>
  `;
};

const renderQrTab = () => {
  const qrLinks = filterAdminRows(adminState.qrLinks, adminState.search.qr, ['slug', 'target_url', 'deep_link_payload', (link) => searchableBool(link.is_active)]);
  const leads = filterAdminRows(adminState.leads, adminState.search.leads, ['partner_name', 'city_name', 'qr_slug', 'target_url', 'deep_link_payload', 'total_clicks']);
  return `
    <div class="admin-section-heading"><h4>QR / лиды</h4><p>QR-ссылки партнёров и агрегированные переходы.</p></div>
    <label class="admin-select-label">Партнёр${renderPartnerPicker('qr', adminState.selectedPartnerIdForQr)}</label>
    ${adminState.selectedPartnerIdForQr ? `
      ${renderAdminSearch('qr', 'Поиск по QR')}
      ${renderTable(
        ['Код ссылки', 'QR-ссылка', 'Целевая ссылка', 'Активна', 'Действие'],
        qrLinks.map((link) => [formatValue(link.slug), link.qr_url ? `<a href="${escapeHtml(link.qr_url)}" target="_blank" rel="noreferrer">${escapeHtml(link.qr_url)}</a>` : '—', formatValue(link.target_url), formatValue(formatBool(link.is_active)), renderAdminQrAction(link)]),
        true,
        'admin-table--compact',
        adminState.search.qr ? 'Ничего не найдено.' : 'Пока нет данных.',
      )}
      ${adminState.selectedQrLinkIdForEdit ? renderQrEditForm() : renderQrCreateForm()}
    ` : '<p class="empty-note">Сначала выберите партнёра.</p>'}
    <h4 class="table-title">Лиды партнёров</h4>
    ${renderAdminSearch('leads', 'Поиск по лидам')}
    ${renderTable(['Партнёр', 'Город', 'Код ссылки', 'Лиды / переходы'], leads.map((lead) => [lead.partner_name, lead.city_name, lead.qr_slug, lead.total_clicks]), false, 'admin-table--compact', adminState.search.leads ? 'Ничего не найдено.' : 'Пока нет данных.')}
  `;
};

const renderVerificationsTab = () => {
  const verifications = filterAdminRows(adminState.verifications, adminState.search.verifications, [
    'status',
    'code',
    'partner_name',
    'client_name',
    'client_id',
    'offer_title',
    'created_at',
    'expires_at',
    'confirmed_at',
    (item) => formatDate(item.created_at),
    (item) => formatDate(item.expires_at),
    (item) => formatDate(item.confirmed_at),
  ]);
  return `
    <div class="admin-section-heading"><h4>Подтверждения</h4><p>Последние сессии подтверждения привилегий.</p></div>
    ${renderAdminSearch('verifications', 'Поиск по подтверждениям')}
    ${renderTable(
      ['Статус', 'Код', 'Партнёр', 'Клиент', 'Название предложения', 'Создано', 'Истекает', 'Подтверждено'],
      verifications.map((item) => [item.status, item.code, item.partner_name, `${item.client_name || '—'} / ${item.client_id}`, item.offer_title, formatDate(item.created_at), formatDate(item.expires_at), formatDate(item.confirmed_at)]),
      false,
      'admin-table--compact',
      adminState.search.verifications ? 'Ничего не найдено.' : 'Пока нет данных.',
    )}
  `;
};

const getAdminTableCellClass = (header) => {
  if (header === 'Действие') {
    return 'admin-table-cell--actions';
  }

  if (['Описание', 'Название предложения', 'Партнёр', 'Email', 'Телефон', 'Владелец', 'QR-ссылка', 'Целевая ссылка', 'Клиент'].includes(header)) {
    return 'admin-table-cell--wrap';
  }

  return 'admin-table-cell--truncate';
};

const renderTable = (headers, rows, trustedHtml = false, tableModifier = '', emptyMessage = 'Пока нет данных.') => {
  if (!rows.length) {
    return `<div class="empty-note">${escapeHtml(emptyMessage)}</div>`;
  }

  const tableClassName = ['admin-table', tableModifier].filter(Boolean).join(' ');

  return `
    <div class="admin-table-wrap">
      <table class="${tableClassName}">
        <thead><tr>${headers.map((header) => `<th class="${getAdminTableCellClass(header)}">${escapeHtml(header)}</th>`).join('')}</tr></thead>
        <tbody>
          ${rows.map((row) => `<tr>${row.map((cell, index) => `<td class="${getAdminTableCellClass(headers[index])}">${trustedHtml ? cell : formatValue(cell)}</td>`).join('')}</tr>`).join('')}
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
  adminState.user = user;
  setLoginMessage();
  setPanelMessage();
  renderAdminLayout();
  await loadActiveTabData();
};

const showPartnerDashboard = async (user) => {
  partnerState.user = user;
  setLoginMessage();
  setPartnerPanelMessage();
  renderPartnerLayout();
  await loadActivePartnerTabData();
};

const showClientDashboard = async (user) => {
  clientState.user = user;
  setLoginMessage();
  setClientPanelMessage();
  renderClientLayout();
  await loadActiveClientTabData();
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
    if (!getToken()) {
      return;
    }
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
    if (!getPartnerToken()) {
      return;
    }
    setPartnerPanelMessage(error.message || 'Не удалось загрузить данные.', 'error');
  }

  renderPartnerLayout();
};

const loadActiveClientTabData = async () => {
  setClientPanelMessage();
  renderClientLayout();

  try {
    if (clientState.activeTab === 'profile') {
      await loadClientProfile();
    } else if (clientState.activeTab === 'catalog') {
      await loadClientCatalog();
    } else if (clientState.activeTab === 'subscription') {
      await loadClientSubscription();
    } else if (clientState.activeTab === 'history') {
      await loadClientVerifications();
    }
  } catch (error) {
    if (!getClientToken()) {
      return;
    }
    setClientPanelMessage(error.message || 'Не удалось загрузить данные.', 'error');
  }

  renderClientLayout();
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

const submitClientProfile = async (form) => {
  const formData = new FormData(form);
  const selectedCityId = String(formData.get('selected_city_id') || '').trim();
  await clientPatchJson('/api/v1/clients/me', {
    full_name: getOptionalText(formData, 'full_name'),
    selected_city_id: selectedCityId ? Number(selectedCityId) : null,
  });
  await loadClientProfile();
};

const submitClientCatalogFilters = async (form) => {
  const formData = new FormData(form);
  clientState.catalogFilters = {
    q: String(formData.get('q') || '').trim(),
    category_slug: String(formData.get('category_slug') || '').trim(),
    city_slug: String(formData.get('city_slug') || '').trim(),
  };
  await loadClientCatalog();
};

const handleClientFormSubmit = async (form) => {
  const formType = form.dataset.clientForm;
  setClientFormMessage(formType);

  try {
    if (formType === 'profile') {
      await submitClientProfile(form);
    } else if (formType === 'catalog') {
      await submitClientCatalogFilters(form);
    }
    setClientFormMessage(formType, 'Сохранено.');
    setClientPanelMessage(formType === 'catalog' ? 'Каталог обновлён.' : 'Сохранено.', 'success');
  } catch (error) {
    setClientFormMessage(formType, error.message || 'Не удалось сохранить.');
    setClientPanelMessage(error.message || 'Не удалось сохранить.', 'error');
  }

  renderClientLayout();
};

const createClientVerification = async (partnerId, offerId = null) => {
  try {
    clientState.latestVerification = await clientPostJson(`/api/v1/clients/partners/${partnerId}/verify`, {
      ...(offerId ? { offer_id: Number(offerId) } : {}),
      source: 'web',
    });
    setClientPanelMessage('Привилегия подтверждена.', 'success');
  } catch (error) {
    setClientPanelMessage(error.message || 'Не удалось подтвердить привилегию.', 'error');
  }

  renderClientLayout();
};

const createClientVkLinkCode = async () => {
  clientState.vkLinkStatus = '';
  clientState.vkLinkMessage = '';

  try {
    clientState.vkLinkCode = await clientPostJson('/api/v1/clients/me/vk-link-codes');
    clientState.vkLinkStatus = 'success';
    clientState.vkLinkMessage = 'Код VK создан.';
  } catch (error) {
    if (error.message === 'Сессия клиента истекла. Войдите снова.') {
      return;
    }
    clientState.vkLinkStatus = 'error';
    clientState.vkLinkMessage = 'Не удалось создать код VK. Попробуйте позже.';
  }

  renderClientLayout();
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

const buildCityPayload = (formData) => ({
  name: getOptionalText(formData, 'name'),
  slug: getOptionalText(formData, 'slug'),
  sort_order: Number(formData.get('sort_order') || 0),
  is_active: formData.has('is_active'),
});

const buildCategoryPayload = (formData) => ({
  name: getOptionalText(formData, 'name'),
  slug: getOptionalText(formData, 'slug'),
  sort_order: Number(formData.get('sort_order') || 0),
  is_active: formData.has('is_active'),
});

const submitCity = async (form) => {
  const formData = new FormData(form);
  await postJson('/api/v1/admin/cities', buildCityPayload(formData));
  form.reset();
  await loadCities();
};

const submitCityEdit = async (form) => {
  const cityId = form.dataset.cityId;
  const formData = new FormData(form);
  await patchJson(`/api/v1/admin/cities/${cityId}`, buildCityPayload(formData));
  await loadCities();
};

const submitCategory = async (form) => {
  const formData = new FormData(form);
  await postJson('/api/v1/admin/categories', buildCategoryPayload(formData));
  form.reset();
  await loadCategories();
};

const submitCategoryEdit = async (form) => {
  const categoryId = form.dataset.categoryId;
  const formData = new FormData(form);
  await patchJson(`/api/v1/admin/categories/${categoryId}`, buildCategoryPayload(formData));
  await loadCategories();
};

const toggleCategoryActive = async (categoryId) => {
  const category = adminState.categories.find((item) => String(item.id) === String(categoryId));
  if (!category) {
    return;
  }

  const confirmationText = category.is_active ? 'Деактивировать категорию?' : 'Активировать категорию?';
  if (!window.confirm(confirmationText)) {
    return;
  }

  try {
    await patchJson(`/api/v1/admin/categories/${categoryId}`, { is_active: category.is_active ? false : true });
    await loadCategories();
    setPanelMessage(category.is_active ? 'Категория деактивирована.' : 'Категория активирована.', 'success');
  } catch (error) {
    setPanelMessage(error.message || 'Не удалось обновить категорию.', 'error');
  }

  renderAdminLayout();
};

const toggleCityActive = async (cityId) => {
  const city = adminState.cities.find((item) => String(item.id) === String(cityId));
  if (!city) {
    return;
  }

  const confirmationText = city.is_active ? 'Убрать город из активных?' : 'Активировать город?';
  if (!window.confirm(confirmationText)) {
    return;
  }

  try {
    await patchJson(`/api/v1/admin/cities/${cityId}`, { is_active: city.is_active ? false : true });
    await loadCities();
    setPanelMessage(city.is_active ? 'Город деактивирован.' : 'Город активирован.', 'success');
  } catch (error) {
    setPanelMessage(error.message || 'Не удалось обновить город.', 'error');
  }

  renderAdminLayout();
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

const buildPartnerPayload = (formData) => ({
  city_id: Number(formData.get('city_id')),
  category_slug: getOptionalText(formData, 'category_slug'),
  owner_user_id: formData.get('owner_user_id') ? Number(formData.get('owner_user_id')) : null,
  name: getOptionalText(formData, 'name'),
  description: getOptionalText(formData, 'description'),
  address: getOptionalText(formData, 'address'),
  phone: getOptionalText(formData, 'phone'),
  website_url: getOptionalText(formData, 'website_url'),
  social_url: getOptionalText(formData, 'social_url'),
  is_active: formData.has('is_active'),
  is_verified: formData.has('is_verified'),
});

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

const submitPartnerEdit = async (form) => {
  const partnerId = form.dataset.partnerId;
  const formData = new FormData(form);
  await patchJson(`/api/v1/admin/partners/${partnerId}`, buildPartnerPayload(formData));
  await loadPartners();
};

const decimalOrNull = (formData, name) => {
  const value = String(formData.get(name) || '').trim();
  return value || null;
};

const buildOfferTextPayload = (formData) => ({
  title: getOptionalText(formData, 'title'),
  benefit_text: getOptionalText(formData, 'benefit_text'),
  description: getOptionalText(formData, 'description'),
  conditions: getOptionalText(formData, 'conditions'),
  sort_order: Number(formData.get('sort_order') || 0),
  is_active: formData.has('is_active'),
});

const submitOffer = async (form) => {
  const formData = new FormData(form);
  await postJson(`/api/v1/admin/partners/${adminState.selectedPartnerIdForOffers}/offers`, {
    ...buildOfferTextPayload(formData),
    base_price: decimalOrNull(formData, 'base_price'),
    discount_percent: decimalOrNull(formData, 'discount_percent'),
  });
  form.reset();
  await loadOffers();
};

const submitOfferEdit = async (form) => {
  const offerId = form.dataset.offerId;
  const formData = new FormData(form);
  await patchJson(`/api/v1/admin/offers/${offerId}`, buildOfferTextPayload(formData));
  await loadOffers();
};

const buildQrPayload = (formData) => ({
  slug: getOptionalText(formData, 'slug'),
  target_url: getOptionalText(formData, 'target_url'),
  deep_link_payload: getOptionalText(formData, 'deep_link_payload'),
  is_active: formData.has('is_active'),
});

const submitQr = async (form) => {
  const formData = new FormData(form);
  await postJson(`/api/v1/admin/partners/${adminState.selectedPartnerIdForQr}/qr-links`, buildQrPayload(formData));
  form.reset();
  await loadQrLinks();
  await loadLeads();
};

const submitQrEdit = async (form) => {
  const qrLinkId = form.dataset.qrLinkId;
  const formData = new FormData(form);
  await patchJson(`/api/v1/admin/qr-links/${qrLinkId}`, buildQrPayload(formData));
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
    } else if (formType === 'cityEdit') {
      await submitCityEdit(form);
    } else if (formType === 'category') {
      await submitCategory(form);
    } else if (formType === 'categoryEdit') {
      await submitCategoryEdit(form);
    } else if (formType === 'partner') {
      await submitPartner(form);
    } else if (formType === 'partnerEdit') {
      await submitPartnerEdit(form);
    } else if (formType === 'offer') {
      await submitOffer(form);
    } else if (formType === 'offerEdit') {
      await submitOfferEdit(form);
    } else if (formType === 'qr') {
      await submitQr(form);
    } else if (formType === 'qrEdit') {
      await submitQrEdit(form);
    }
    setFormMessage(formType, 'Сохранено.');
    setPanelMessage('Сохранено.', 'success');
    renderAdminLayout();
  } catch (error) {
    setFormMessage(formType, error.message || 'Не удалось сохранить.');
    if (message) {
      message.textContent = adminState.formMessages[formType];
    }
    setPanelMessage(error.message || 'Не удалось сохранить.', 'error');
  }

  renderAdminLayout();
};

const handleLoginSubmit = async (form) => {
  setLoginMessage();

  const formData = new FormData(form);
  const loginValue = String(formData.get('email') || '').trim();
  const password = String(formData.get('password') || '');

  try {
    if (activeLoginMode === 'partner' || activeLoginMode === 'client') {
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
      const expectedRole = activeLoginMode;
      const tokenKey = expectedRole === 'partner' ? partnerTokenKey : clientTokenKey;
      localStorage.setItem(tokenKey, data.access_token);

      if (data.user?.role !== expectedRole) {
        if (expectedRole === 'partner') {
          clearPartnerToken();
        } else {
          clearClientToken();
        }
        showLoginForm();
        setLoginMode(expectedRole);
        setLoginMessage(expectedRole === 'partner' ? 'Этот вход доступен только партнёрам' : 'Этот вход доступен только клиентам');
        return;
      }

      form.reset();
      if (expectedRole === 'partner') {
        await showPartnerDashboard(data.user);
      } else {
        await showClientDashboard(data.user);
      }
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
    form.reset();
    await showAdminDashboard(data.user);
  } catch (error) {
    if (activeLoginMode === 'partner') {
      clearPartnerToken();
      showLoginForm();
      setLoginMode('partner');
    } else if (activeLoginMode === 'client') {
      clearClientToken();
      showLoginForm();
      setLoginMode('client');
    } else {
      clearToken();
      showLoginForm();
      setLoginMode('admin');
    }
    setLoginMessage('Неверный логин или пароль');
  }
};

root.addEventListener('click', async (event) => {
  const cityChoice = event.target.closest('[data-city-choice]');
  if (cityChoice) {
    document.querySelectorAll('[data-city-choice]').forEach((choice) => {
      const isSelected = choice === cityChoice;
      choice.classList.toggle('is-active', isSelected);
      choice.setAttribute('aria-checked', String(isSelected));
    });
    return;
  }

  const loginModeButton = event.target.closest('[data-login-mode]');
  if (loginModeButton) {
    setLoginMode(loginModeButton.dataset.loginMode);
    setLoginMessage();
    return;
  }

  const adminSearchReset = event.target.closest('[data-admin-search-reset]');
  if (adminSearchReset) {
    adminState.search[adminSearchReset.dataset.adminSearchReset] = '';
    renderAdminLayout();
    return;
  }

  const userToggle = event.target.closest('[data-user-active-toggle]');
  if (userToggle) {
    toggleUserActive(userToggle.dataset.userActiveToggle);
    return;
  }

  const cityEditButton = event.target.closest('[data-admin-city-edit]');
  if (cityEditButton) {
    adminState.selectedCityIdForEdit = cityEditButton.dataset.adminCityEdit;
    setFormMessage('cityEdit');
    renderAdminLayout();
    return;
  }

  const cityEditCancel = event.target.closest('[data-admin-city-edit-cancel]');
  if (cityEditCancel) {
    adminState.selectedCityIdForEdit = '';
    setFormMessage('cityEdit');
    renderAdminLayout();
    return;
  }

  const cityActiveToggle = event.target.closest('[data-admin-city-active-toggle]');
  if (cityActiveToggle) {
    toggleCityActive(cityActiveToggle.dataset.adminCityActiveToggle);
    return;
  }

  const categoryEditButton = event.target.closest('[data-admin-category-edit]');
  if (categoryEditButton) {
    adminState.selectedCategoryIdForEdit = categoryEditButton.dataset.adminCategoryEdit;
    setFormMessage('categoryEdit');
    renderAdminLayout();
    return;
  }

  const categoryEditCancel = event.target.closest('[data-admin-category-edit-cancel]');
  if (categoryEditCancel) {
    adminState.selectedCategoryIdForEdit = '';
    setFormMessage('categoryEdit');
    renderAdminLayout();
    return;
  }

  const categoryActiveToggle = event.target.closest('[data-admin-category-active-toggle]');
  if (categoryActiveToggle) {
    toggleCategoryActive(categoryActiveToggle.dataset.adminCategoryActiveToggle);
    return;
  }

  const partnerEditButton = event.target.closest('[data-admin-partner-edit]');
  if (partnerEditButton) {
    adminState.selectedPartnerIdForEdit = partnerEditButton.dataset.adminPartnerEdit;
    setFormMessage('partnerEdit');
    renderAdminLayout();
    return;
  }

  const partnerEditCancel = event.target.closest('[data-admin-partner-edit-cancel]');
  if (partnerEditCancel) {
    adminState.selectedPartnerIdForEdit = '';
    setFormMessage('partnerEdit');
    renderAdminLayout();
    return;
  }

  const offerEditButton = event.target.closest('[data-admin-offer-edit]');
  if (offerEditButton) {
    adminState.selectedOfferIdForEdit = offerEditButton.dataset.adminOfferEdit;
    setFormMessage('offerEdit');
    renderAdminLayout();
    return;
  }

  const offerEditCancel = event.target.closest('[data-admin-offer-edit-cancel]');
  if (offerEditCancel) {
    adminState.selectedOfferIdForEdit = '';
    setFormMessage('offerEdit');
    renderAdminLayout();
    return;
  }

  const qrEditButton = event.target.closest('[data-admin-qr-edit]');
  if (qrEditButton) {
    adminState.selectedQrLinkIdForEdit = qrEditButton.dataset.adminQrEdit;
    setFormMessage('qrEdit');
    renderAdminLayout();
    return;
  }

  const qrEditCancel = event.target.closest('[data-admin-qr-edit-cancel]');
  if (qrEditCancel) {
    adminState.selectedQrLinkIdForEdit = '';
    setFormMessage('qrEdit');
    renderAdminLayout();
    return;
  }

  const adminLogout = event.target.closest('[data-logout-button]');
  if (adminLogout) {
    clearToken();
    showLoginForm();
    setLoginMode('admin');
    return;
  }

  const adminTabButton = event.target.closest('[data-admin-tab]');
  if (adminTabButton) {
    adminState.activeTab = adminTabButton.dataset.adminTab;
    loadActiveTabData();
    return;
  }

  const partnerOfferToggle = event.target.closest('[data-partner-offer-toggle]');
  if (partnerOfferToggle) {
    togglePartnerOffer(partnerOfferToggle.dataset.partnerOfferToggle);
    return;
  }

  const partnerConfirmButton = event.target.closest('[data-partner-confirm-verification]');
  if (partnerConfirmButton) {
    confirmPartnerVerification(partnerConfirmButton.dataset.partnerConfirmVerification);
    return;
  }

  const partnerLogout = event.target.closest('[data-partner-logout-button]');
  if (partnerLogout) {
    clearPartnerToken();
    showLoginForm();
    setLoginMode('partner');
    return;
  }

  const partnerTabButton = event.target.closest('[data-partner-tab]');
  if (partnerTabButton) {
    partnerState.activeTab = partnerTabButton.dataset.partnerTab;
    loadActivePartnerTabData();
    return;
  }

  const clientLogout = event.target.closest('[data-client-logout-button]');
  if (clientLogout) {
    clearClientToken();
    showLoginForm();
    setLoginMode('client');
    return;
  }

  const clientTabButton = event.target.closest('[data-client-tab]');
  if (clientTabButton) {
    clientState.activeTab = clientTabButton.dataset.clientTab;
    await loadActiveClientTabData();
    return;
  }

  const createVkCodeButton = event.target.closest('[data-client-create-vk-code]');
  if (createVkCodeButton) {
    await createClientVkLinkCode();
    return;
  }

  const loadOffersButton = event.target.closest('[data-client-load-offers]');
  if (loadOffersButton) {
    try {
      await loadClientPartnerOffers(loadOffersButton.dataset.clientLoadOffers);
      setClientPanelMessage('Предложения загружены.', 'success');
    } catch (error) {
      setClientPanelMessage(error.message || 'Не удалось загрузить предложения.', 'error');
    }
    renderClientLayout();
    return;
  }

  const verifyOfferButton = event.target.closest('[data-client-verify-offer]');
  if (verifyOfferButton) {
    await createClientVerification(verifyOfferButton.dataset.clientVerifyOffer, verifyOfferButton.dataset.offerId);
    return;
  }

  const verifyPartnerButton = event.target.closest('[data-client-verify-partner]');
  if (verifyPartnerButton) {
    await createClientVerification(verifyPartnerButton.dataset.clientVerifyPartner);
  }
});

root.addEventListener('input', (event) => {
  const searchInput = event.target.closest('[data-admin-search]');
  if (!searchInput) {
    return;
  }

  const searchScope = searchInput.dataset.adminSearch;
  adminState.search[searchScope] = searchInput.value;
  renderAdminLayout();
  requestAnimationFrame(() => {
    const updatedInput = root.querySelector(`[data-admin-search="${searchScope}"]`);
    if (updatedInput) {
      updatedInput.focus();
      updatedInput.setSelectionRange(updatedInput.value.length, updatedInput.value.length);
    }
  });
});

root.addEventListener('change', (event) => {
  const picker = event.target.closest('[data-partner-picker]');
  if (!picker) {
    return;
  }

  if (picker.dataset.partnerPicker === 'offers') {
    adminState.selectedPartnerIdForOffers = picker.value;
    adminState.selectedOfferIdForEdit = '';
    setFormMessage('offerEdit');
  } else if (picker.dataset.partnerPicker === 'qr') {
    adminState.selectedPartnerIdForQr = picker.value;
    adminState.selectedQrLinkIdForEdit = '';
    setFormMessage('qrEdit');
  }

  loadActiveTabData();
});

root.addEventListener('submit', (event) => {
  const login = event.target.closest('[data-login-form]');
  if (login) {
    event.preventDefault();
    handleLoginSubmit(login);
    return;
  }

  const adminForm = event.target.closest('[data-admin-form]');
  if (adminForm) {
    event.preventDefault();
    handleAdminFormSubmit(adminForm);
    return;
  }

  const partnerForm = event.target.closest('[data-partner-form]');
  if (partnerForm) {
    event.preventDefault();
    handlePartnerFormSubmit(partnerForm);
    return;
  }

  const clientForm = event.target.closest('[data-client-form]');
  if (clientForm) {
    event.preventDefault();
    handleClientFormSubmit(clientForm);
  }
});

const restoreClientSession = async () => {
  const token = getClientToken();
  if (!token) {
    showLoginForm();
    return;
  }

  try {
    const user = await requestClientUserMe();
    if (user.role !== 'client') {
      clearClientToken();
      showLoginForm();
      return;
    }
    setLoginMode('client');
    await showClientDashboard(user);
  } catch (error) {
    clearClientToken();
    showLoginForm();
  }
};

const restorePartnerSession = async () => {
  const token = getPartnerToken();
  if (!token) {
    await restoreClientSession();
    return;
  }

  try {
    const user = await requestPartnerUserMe();
    if (user.role !== 'partner') {
      clearPartnerToken();
      await restoreClientSession();
      return;
    }
    setLoginMode('partner');
    await showPartnerDashboard(user);
  } catch (error) {
    clearPartnerToken();
    await restoreClientSession();
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
