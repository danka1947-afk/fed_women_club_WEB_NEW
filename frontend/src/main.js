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
        <form class="login-form" data-login-form>
          <label>
            Телефон или email
            <input type="email" name="email" autocomplete="email" placeholder="name@example.com" required />
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
const adminTabs = [
  { id: 'overview', label: 'Обзор' },
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
  overviewPartialError: false,
};

const loginForm = document.querySelector('[data-login-form]');
const loginMessage = document.querySelector('[data-login-message]');
const adminDashboard = document.querySelector('[data-admin-dashboard]');
const adminEmail = document.querySelector('[data-admin-email]');
const logoutButton = document.querySelector('[data-logout-button]');

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

const setLoginMessage = (message = '') => {
  loginMessage.textContent = message;
};

const setPanelMessage = (message = '', type = 'info') => {
  adminState.panelMessage = message
    ? `<div class="admin-status admin-status--${type}" role="status">${escapeHtml(message)}</div>`
    : '';
};

const clearToken = () => {
  localStorage.removeItem(authTokenKey);
};

const showLoginForm = () => {
  loginForm.hidden = false;
  adminDashboard.hidden = true;
  adminEmail.textContent = '';
  adminState.user = null;
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

const requestAdminMe = () => apiFetch('/api/v1/admin/me');

const postJson = (path, payload) => apiFetch(path, {
  method: 'POST',
  body: JSON.stringify(payload),
});

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
      <p class="form-message" data-form-message="city"></p>
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
      ${renderTable(['name', 'city_name', 'category_slug', 'active', 'verified'], adminState.partners.map((partner) => [partner.name, partner.city_name, partner.category_slug, formatBool(partner.is_active), formatBool(partner.is_verified)]))}
    </div>
    <form class="admin-form" data-admin-form="partner">
      <h4>Новый партнёр</h4>
      <label>city_id${renderSelect('city_id', adminState.cities.map((city) => [city.id, city.name]), true)}</label>
      <label>category_slug${renderSelect('category_slug', adminState.categories.map((category) => [category.slug, category.title]), false)}</label>
      <label>name<input name="name" required /></label>
      <label>description<textarea name="description" rows="3"></textarea></label>
      <label>address<input name="address" /></label>
      <label>phone<input name="phone" /></label>
      <label>social_url<input name="social_url" /></label>
      <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> active</label>
      <label class="checkbox-row"><input name="is_verified" type="checkbox" /> verified</label>
      <button type="submit">Создать партнёра</button>
      <p class="form-message" data-form-message="partner"></p>
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
      <p class="form-message" data-form-message="offer"></p>
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
      <p class="form-message" data-form-message="qr"></p>
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

const renderSelect = (name, options, required = false, selectedValue = '') => `
  <select name="${name}" ${required ? 'required' : ''}>
    <option value="">${required ? 'Выберите' : 'Без категории'}</option>
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
  adminState.user = user;
  setLoginMessage();
  setPanelMessage();
  renderAdminLayout();
  await loadActiveTabData();
};

const loadOverview = async () => {
  adminState.overviewPartialError = false;
  const tasks = [loadCities, loadCategories, loadPartners, loadVerifications, loadLeads];
  const results = await Promise.allSettled(tasks.map((task) => task()));
  adminState.overviewPartialError = results.some((result) => result.status === 'rejected');
};

const loadActiveTabData = async () => {
  setPanelMessage();
  renderAdminLayout();

  try {
    if (adminState.activeTab === 'overview') {
      await loadOverview();
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
  if (message) {
    message.textContent = '';
  }

  try {
    if (formType === 'city') {
      await submitCity(form);
    } else if (formType === 'partner') {
      await submitPartner(form);
    } else if (formType === 'offer') {
      await submitOffer(form);
    } else if (formType === 'qr') {
      await submitQr(form);
    }
    setPanelMessage('Сохранено.', 'success');
  } catch (error) {
    if (message) {
      message.textContent = error.message || 'Не удалось сохранить.';
    }
    setPanelMessage(error.message || 'Не удалось сохранить.', 'error');
  }

  renderAdminLayout();
};

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  setLoginMessage();

  const formData = new FormData(loginForm);
  const payload = {
    email: String(formData.get('email') || '').trim(),
    password: String(formData.get('password') || ''),
  };

  try {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    localStorage.setItem(authTokenKey, data.access_token);
    await showAdminDashboard(data.user);
    loginForm.reset();
  } catch (error) {
    clearToken();
    showLoginForm();
    setLoginMessage('Неверный логин или пароль');
  }
});

adminDashboard.addEventListener('click', (event) => {
  const tabButton = event.target.closest('[data-admin-tab]');
  const logout = event.target.closest('[data-logout-button]');

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

const restoreAdminSession = async () => {
  const token = getToken();
  if (!token) {
    showLoginForm();
    return;
  }

  try {
    const user = await requestAdminMe();
    await showAdminDashboard(user);
  } catch (error) {
    clearToken();
    showLoginForm();
  }
};

restoreAdminSession();
