const root = document.querySelector('#root');

const cities = [
  'Новосибирск',
  'Череповец',
];

const categoryDirections = [
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

const categories = categoryDirections.map((category) => category.title);

const landingMenuLinks = [
  { href: '#landing-about', label: 'О клубе' },
  { href: '#landing-benefits', label: 'Привилегии' },
  { href: '#landing-partners', label: 'Партнёры' },
  { href: '#landing-directions', label: 'Направления' },
  { href: '#landing-join', label: 'Как вступить' },
  { href: '#landing-cities', label: 'Города' },
];

const landingPartnerModalState = {
  isOpen: false,
  selectedLandingDirection: null,
  partners: [],
  cache: {},
  currentIndex: 0,
  loading: false,
  error: '',
};


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


const getPasswordSetupParams = () => {
  const params = new URLSearchParams(window.location.search);
  const setupToken = params.get('setup_token');
  return {
    setupToken: setupToken ? setupToken.trim() : '',
    login: (params.get('login') || '').trim(),
  };
};

const renderPasswordSetupApp = () => {
  const { login } = getPasswordSetupParams();
  document.body.classList.remove('is-dashboard');
  root.innerHTML = `
    <div class="sakura-layer" aria-hidden="true">
      ${sakuraPetalMarkup}
    </div>
    <main class="app-shell setup-password-shell">
      <section class="panel setup-password-panel" aria-labelledby="setup-password-title">
        <p class="section-kicker">VK onboarding</p>
        <h1 id="setup-password-title">Задайте пароль</h1>
        <p>Придумайте пароль для входа в личный кабинет клуба.</p>
        <form class="login-form setup-password-form" data-password-setup-form>
          <label>
            Логин
            <input type="text" name="login" autocomplete="username" value="${escapeHtml(login)}" readonly placeholder="Логин появится после установки, если VK-бот не передал email или телефон" />
          </label>
          <label>
            Новый пароль
            <input type="password" name="password" autocomplete="new-password" placeholder="Минимум 8 символов" required />
          </label>
          <label>
            Повторите пароль
            <input type="password" name="password_confirm" autocomplete="new-password" placeholder="Повторите пароль" required />
          </label>
          <button type="submit">Сохранить пароль</button>
          <p class="login-message" data-password-setup-message role="status" aria-live="polite"></p>
        </form>
      </section>
    </main>
  `;
};

const renderPublicApp = () => {
  document.body.classList.remove('is-dashboard');
  root.innerHTML = `
  <div class="sakura-layer" aria-hidden="true">
    ${sakuraPetalMarkup}
  </div>
  <main class="app-shell">
    <header class="hero" id="landing-about" aria-labelledby="hero-title">
      <nav class="topbar" aria-label="Основная навигация">
        <div class="brand" aria-label="Женский клуб">
          <span class="brand-mark" aria-hidden="true">ЖК</span>
          <span>
            <span class="brand-name">Женский клуб</span>
            <span class="brand-caption">Федеральный клуб привилегий для девушек</span>
          </span>
        </div>
        <div class="topbar-actions" aria-label="Разделы лендинга">
          <div class="landing-menu">
            <button class="landing-menu-toggle" type="button" data-landing-menu-toggle aria-expanded="false" aria-controls="landing-menu-panel">Меню</button>
          <div class="landing-menu-panel" id="landing-menu-panel" data-landing-menu-panel hidden>
            ${landingMenuLinks.map((link) => `<a href="${link.href}" data-landing-menu-link>${link.label}</a>`).join('')}
          </div>
          </div>
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

        <div class="hero-card">
          <span class="pill">для себя</span>
          <h2>Красота, забота и вдохновение</h2>
          <p>Скидки, подарки и специальные предложения у партнёров клуба.</p>
        </div>
      </div>
    </header>

    <section class="feature-grid" id="landing-benefits" aria-label="Возможности клуба">
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

    <section class="content-grid" id="landing-partners">
      <section class="panel city-panel" id="landing-cities" aria-labelledby="city-selector-title">
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
        <span class="landing-anchor" id="landing-join" aria-hidden="true"></span>
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

    <section class="panel categories-panel" id="landing-directions" aria-labelledby="categories-title">
      <p class="section-kicker">Направления</p>
      <h2 id="categories-title">Категории партнёров</h2>
      <ul class="category-list">
        ${categoryDirections.map((category) => `
          <li>
            <button
              class="landing-direction-button direction-card"
              type="button"
              data-landing-category-slug="${category.slug}"
            >
              ${category.title}
            </button>
          </li>
        `).join('')}
      </ul>
    </section>

    <section class="landing-partner-modal" data-landing-partner-modal aria-live="polite" hidden></section>

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
  { id: 'activity', label: 'Активность', icon: '•' },
];

const adminState = {
  activeTab: 'overview',
  user: null,
  users: [],
  cities: [],
  categories: [],
  partners: [],
  partnerPhotosByPartner: {},
  partnerAnalyticsById: {},
  selectedPartnerAnalytics: null,
  partnerAnalyticsLoading: false,
  partnerAnalyticsError: '',
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
  activityItems: [],
  activityLoading: false,
  activityError: '',
  activityEventType: '',
  selectedPartnerIdForActivity: '',
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
  { id: 'analytics', label: 'Аналитика', icon: '↗' },
  { id: 'activity', label: 'Активность', icon: '•' },
];

const partnerState = {
  activeTab: 'profile',
  user: null,
  profile: null,
  photos: [],
  offers: [],
  qrLinks: [],
  leads: [],
  verifications: [],
  analytics: null,
  analyticsLoading: false,
  analyticsError: '',
  activityItems: [],
  activityLoading: false,
  activityError: '',
  panelMessage: '',
  formMessages: {},
  selectedOfferIdForEdit: '',
};

const clientTabs = [
  { id: 'profile', label: 'Профиль', icon: '♡' },
  { id: 'catalog', label: 'Каталог', icon: '✦' },
  { id: 'subscription', label: 'Моя подписка', icon: '₽' },
  { id: 'history', label: 'Мои привилегии', icon: '↺' },
  { id: 'activity', label: 'Активность', icon: '•' },
];

const clientState = {
  activeTab: 'profile',
  user: null,
  profile: null,
  subscription: null,
  partners: [],
  offersByPartner: {},
  selectedPartner: null,
  selectedPartnerId: '',
  latestVerification: null,
  vkLinkCode: null,
  vkLinkStatus: '',
  vkLinkMessage: '',
  verifications: [],
  activityItems: [],
  activityLoading: false,
  activityError: '',
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

const statusBadgeMappings = {
  'активен': { label: 'Активен', tone: 'success' },
  'активно': { label: 'Активно', tone: 'success' },
  'активна': { label: 'Активна', tone: 'success' },
  'неактивен': { label: 'Неактивен', tone: 'muted' },
  'неактивно': { label: 'Неактивно', tone: 'muted' },
  'неактивна': { label: 'Неактивна', tone: 'muted' },
  'на проверке': { label: 'На проверке', tone: 'warning' },
  'проверен': { label: 'Проверен', tone: 'success' },
  'не проверен': { label: 'Не проверен', tone: 'warning' },
  'подтверждено': { label: 'Подтверждено', tone: 'success' },
  'истекло': { label: 'Истекло', tone: 'warning' },
  'отменено': { label: 'Отменено', tone: 'danger' },
  'active': { label: 'Активно', tone: 'success' },
  'confirmed': { label: 'Подтверждено', tone: 'success' },
  'expired': { label: 'Истекло', tone: 'warning' },
  'cancelled': { label: 'Отменено', tone: 'danger' },
  'canceled': { label: 'Отменено', tone: 'danger' },
};

const getStatusBadgeMeta = (value, tone = '') => {
  const normalized = String(value || '').trim().toLowerCase();
  if (!normalized || normalized === '—') {
    return null;
  }

  const mapped = statusBadgeMappings[normalized] || { label: value, tone: tone || 'info' };
  return {
    label: mapped.label,
    tone: tone || mapped.tone || 'info',
  };
};

const renderStatusBadge = (label, tone = '') => {
  const meta = getStatusBadgeMeta(label, tone);
  if (!meta) {
    return '—';
  }

  return `<span class="status-badge status-badge--${escapeHtml(meta.tone)}">${escapeHtml(meta.label)}</span>`;
};

const renderBoolStatusBadge = (value) => renderStatusBadge(formatBool(value));
const renderActiveStatusBadge = (value) => renderStatusBadge(formatActiveStatus(value));
const renderPartnerReviewStatusBadge = (value) => (value ? renderActiveStatusBadge(value) : renderStatusBadge('На проверке'));
const renderActiveStatusFeminineBadge = (value) => renderStatusBadge(formatActiveStatusFeminine(value));
const renderVerifiedStatusBadge = (value) => renderStatusBadge(formatVerifiedStatus(value));
const formatRole = (role) => ({
  client: 'Клиент',
  partner: 'Партнёр',
  admin: 'Администратор',
}[role] || role);
const formatValue = (value) => {
  if (value === null || value === undefined || value === '') return '—';
  return escapeHtml(value);
};
const hasScientificNotation = (value) => /[+-]?\d+(?:[.,]\d+)?e[+-]?\d+%?/i.test(String(value || ''));
const formatDiscountPercent = (value) => {
  if (value === null || value === undefined || value === '') return '';
  const normalized = Number(String(value).replace(',', '.'));
  if (!Number.isFinite(normalized)) return '';
  const formatted = Math.abs(normalized).toLocaleString('ru-RU', {
    maximumFractionDigits: 2,
    useGrouping: false,
  });
  return `-${formatted}%`;
};
const formatPartnerBenefit = (offer) => {
  const benefitText = String(offer?.discount_text || offer?.benefit_text || '').trim();
  if (benefitText && !hasScientificNotation(benefitText)) {
    return benefitText;
  }
  return formatDiscountPercent(offer?.discount_percent) || 'Специальное предложение';
};

const formatOfferBasePrice = (value) => {
  if (value === null || value === undefined || value === '') return 'Цена уточняется';
  const rawValue = String(value).trim();
  if (!rawValue || hasScientificNotation(rawValue)) return 'Цена уточняется';
  const normalized = Number(rawValue.replace(',', '.'));
  if (!Number.isFinite(normalized)) return rawValue;
  return `${normalized.toLocaleString('ru-RU', {
    maximumFractionDigits: 2,
  })} ₽`;
};

const formatPrivilegeErrorMessage = (message) => ({
  'Active subscription required': 'Для получения привилегии нужна активная подписка.',
  'Offer not found': 'Предложение сейчас недоступно.',
  'Partner not found': 'Партнёр сейчас недоступен.',
  'Verification session is not active': 'Эта привилегия уже не активна.',
  'Verification session expired': 'Срок действия кода истёк.',
  'Verification session not found': 'Код не найден для вашего кабинета.',
}[String(message || '').trim()] || message || 'Не удалось выполнить действие. Попробуйте позже.');

const formatPrivilegeStatus = (status) => getStatusBadgeMeta(status)?.label || 'Активно';

const renderOfferMarketplaceCard = (offer = {}, options = {}) => {
  const imageUrl = isSafePublicAssetUrl(offer.image_url) ? offer.image_url : '';
  const title = String(offer.title || '').trim() || 'Название предложения';
  const description = String(offer.description || '').trim() || 'Опишите услугу, формат и результат, который получит участница клуба.';
  const conditions = String(offer.conditions || offer.terms || '').trim() || 'Условия получения привилегии появятся здесь.';
  const benefit = formatPartnerBenefit(offer);
  const basePrice = formatOfferBasePrice(offer.base_price);
  const ctaText = options.cta || 'Получить привилегию';
  const note = options.note || 'Так предложение увидит клиент';
  const actionHtml = options.actionHtml || `<button type="button" disabled>${escapeHtml(ctaText)}</button>`;

  return `
    <article class="offer-marketplace-card ${options.compact ? 'offer-marketplace-card--compact' : ''}">
      ${imageUrl
        ? `<div class="offer-marketplace-image" style="background-image: url('${escapeHtml(imageUrl)}')" role="img" aria-label="${escapeHtml(title)}"></div>`
        : '<div class="offer-marketplace-image offer-card-placeholder" aria-hidden="true"><span>Фото услуги</span></div>'}
      <div class="offer-marketplace-body">
        <div class="offer-marketplace-heading">
          <span class="offer-marketplace-benefit">${escapeHtml(benefit)}</span>
          ${offer.is_active === undefined ? '' : renderActiveStatusBadge(offer.is_active)}
        </div>
        <h4>${escapeHtml(title)}</h4>
        <p>${escapeHtml(description)}</p>
        <dl class="offer-marketplace-meta">
          <div><dt>Условия</dt><dd>${escapeHtml(conditions)}</dd></div>
          <div><dt>Базовая цена</dt><dd>${escapeHtml(basePrice)}</dd></div>
          <div><dt>Скидка</dt><dd>${escapeHtml(formatDiscountPercent(offer.discount_percent) || 'Индивидуально')}</dd></div>
        </dl>
        <div class="offer-marketplace-preview">
          <span>${escapeHtml(note)}</span>
          ${actionHtml}
        </div>
      </div>
    </article>
  `;
};

const renderDisplayValue = (value) => String(value || '').startsWith('<span class="status-badge') ? value : formatValue(value);
const formatDate = (value) => (value ? new Date(value).toLocaleString('ru-RU') : '—');

const activityEventMeta = {
  privilege_created: { label: 'Привилегия', icon: '♡', tone: 'privilege' },
  privilege_confirmed: { label: 'Подтверждение', icon: '✓', tone: 'confirmed' },
  privilege_expired: { label: 'Истекло', icon: '⌛', tone: 'expired' },
  qr_clicked: { label: 'QR-переход', icon: 'QR', tone: 'qr' },
  partner_created: { label: 'Партнёр', icon: '✦', tone: 'partner' },
  offer_created: { label: 'Предложение', icon: '%', tone: 'privilege' },
  qr_link_created: { label: 'QR-ссылка', icon: '⌁', tone: 'qr' },
};

const activityEventFilters = [
  { value: '', label: 'Все события' },
  { value: 'privilege_created', label: 'Привилегии' },
  { value: 'privilege_confirmed', label: 'Подтверждения' },
  { value: 'privilege_expired', label: 'Истекшие' },
  { value: 'qr_clicked', label: 'QR-переходы' },
  { value: 'partner_created', label: 'Партнёры' },
  { value: 'offer_created', label: 'Предложения' },
  { value: 'qr_link_created', label: 'QR-ссылки' },
];

const formatActivityDate = (value) => formatDate(value);

const getActivityEventMeta = (eventType) => activityEventMeta[eventType] || {
  label: 'Событие',
  icon: '•',
  tone: 'privilege',
};

const renderActivityItem = (item = {}) => {
  const eventMeta = getActivityEventMeta(item.event_type);
  const metaItems = [
    item.partner_name ? `Партнёр: ${item.partner_name}` : '',
    item.offer_title ? `Предложение: ${item.offer_title}` : '',
    item.qr_slug ? `QR: ${item.qr_slug}` : '',
  ].filter(Boolean);

  return `
    <article class="activity-item">
      <span class="activity-badge activity-badge--${escapeHtml(eventMeta.tone)}" title="${escapeHtml(eventMeta.label)}" aria-label="${escapeHtml(eventMeta.label)}">${escapeHtml(eventMeta.icon)}</span>
      <div class="activity-item__body">
        <div class="activity-item__heading">
          <div>
            <h4>${formatValue(item.title || eventMeta.label)}</h4>
            <p>${formatValue(item.description || 'Подробности события появятся здесь.')}</p>
          </div>
          <time datetime="${escapeHtml(item.occurred_at || '')}">${escapeHtml(formatActivityDate(item.occurred_at))}</time>
        </div>
        ${(metaItems.length || item.status) ? `
          <div class="activity-meta">
            ${metaItems.map((meta) => `<span>${escapeHtml(meta)}</span>`).join('')}
            ${item.status ? renderStatusBadge(formatStatus(item.status)) : ''}
          </div>
        ` : ''}
      </div>
    </article>
  `;
};

const renderActivityFeed = (items = [], options = {}) => {
  if (options.loading) {
    return '<div class="activity-empty" role="status">Загружаем события…</div>';
  }

  if (options.error) {
    return '<div class="activity-empty activity-empty--error" role="alert">Не удалось загрузить события.</div>';
  }

  if (!Array.isArray(items) || !items.length) {
    return '<div class="activity-empty">Событий пока нет.</div>';
  }

  return `<div class="activity-feed">${items.map(renderActivityItem).join('')}</div>`;
};

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


const analyticsCardDefinitions = [
  ['qr_links_count', 'QR-ссылки', 'count'],
  ['lead_clicks_count', 'Переходы по QR', 'count'],
  ['privileges_created_count', 'Получено привилегий', 'count'],
  ['privileges_confirmed_count', 'Подтверждено', 'count'],
  ['active_privileges_count', 'Активные привилегии', 'count'],
  ['expired_privileges_count', 'Истекшие привилегии', 'count'],
  ['conversion_to_privilege_percent', 'Конверсия в привилегию', 'percent'],
  ['confirmation_rate_percent', 'Процент подтверждения', 'percent'],
];

const formatAnalyticsCount = (value) => {
  const numberValue = Number(value || 0);
  return Number.isFinite(numberValue) ? String(numberValue) : '0';
};

const formatAnalyticsPercent = (value) => {
  const numberValue = Number(value || 0);
  if (!Number.isFinite(numberValue)) return '0%';
  const rounded = Math.round(numberValue * 10) / 10;
  return `${Number.isInteger(rounded) ? rounded.toFixed(0) : rounded.toFixed(1)}%`;
};

const isAnalyticsEmpty = (analytics = {}) => analyticsCardDefinitions.every(([key]) => Number(analytics?.[key] || 0) === 0);

const renderAnalyticsCards = (analytics = {}) => `
  <div class="analytics-grid">
    ${analyticsCardDefinitions.map(([key, label, type]) => `
      <article class="analytics-card">
        <strong class="analytics-value">${escapeHtml(type === 'percent' ? formatAnalyticsPercent(analytics?.[key]) : formatAnalyticsCount(analytics?.[key]))}</strong>
        <span class="analytics-label">${escapeHtml(label)}</span>
      </article>
    `).join('')}
  </div>
`;

const renderAnalyticsSection = (analytics, options = {}) => {
  const title = options.title || 'Аналитика';
  const loading = options.loading || false;
  const error = options.error || '';

  if (loading) {
    return `
      <section class="analytics-panel" aria-live="polite">
        <div class="admin-section-heading"><h4>${escapeHtml(title)}</h4><p class="analytics-hint">Аналитика помогает понять, сколько клиентов пришли из клуба и сколько привилегий реально использовали.</p></div>
        <p class="analytics-hint">Загружаем аналитику…</p>
      </section>
    `;
  }

  if (error) {
    return `
      <section class="analytics-panel" aria-live="polite">
        <div class="admin-section-heading"><h4>${escapeHtml(title)}</h4><p class="analytics-hint">Аналитика помогает понять, сколько клиентов пришли из клуба и сколько привилегий реально использовали.</p></div>
        <p class="analytics-empty">${escapeHtml(error)}</p>
      </section>
    `;
  }

  if (!analytics) {
    return `
      <section class="analytics-panel" aria-live="polite">
        <div class="admin-section-heading"><h4>${escapeHtml(title)}</h4><p class="analytics-hint">Аналитика помогает понять, сколько клиентов пришли из клуба и сколько привилегий реально использовали.</p></div>
        <p class="analytics-empty">Выберите партнёра, чтобы увидеть аналитику.</p>
      </section>
    `;
  }

  return `
    <section class="analytics-panel" aria-live="polite">
      <div class="admin-section-heading"><h4>${escapeHtml(title)}</h4><p class="analytics-hint">Аналитика помогает понять, сколько клиентов пришли из клуба и сколько привилегий реально использовали.</p></div>
      ${renderAnalyticsCards(analytics)}
      ${isAnalyticsEmpty(analytics) ? '<p class="analytics-empty">Данных пока нет. Разместите QR-код и добавьте предложения, чтобы начать получать статистику.</p>' : ''}
    </section>
  `;
};

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

const getLandingDirectionBySlug = (slug) => categoryDirections.find((category) => category.slug === slug) || null;

const isSafePublicAssetUrl = (value) => {
  const url = String(value || '').trim();
  return (url.startsWith('/assets/') || url.startsWith('/uploads/')) && !/[\s'"()]/.test(url);
};

const getActivePartnerGalleryPhotos = (photos = []) => (Array.isArray(photos) ? photos : [])
  .filter((photo) => photo?.is_active !== false && isSafePublicAssetUrl(photo?.url))
  .sort((left, right) => Number(left.sort_order || 0) - Number(right.sort_order || 0) || Number(left.id || 0) - Number(right.id || 0));

const renderLandingPartnerImage = (partner) => {
  const photos = getActivePartnerGalleryPhotos(partner?.photos);
  if (photos.length) {
    return `
      <div class="landing-partner-cover landing-partner-gallery" aria-label="Галерея партнёра">
        <div class="landing-partner-gallery-main" style="background-image: url('${escapeHtml(photos[0].url)}')" role="img" aria-label="${escapeHtml(photos[0].alt_text || partner?.name || 'Фото партнёра')}"></div>
        ${photos.length > 1 ? `<div class="landing-partner-gallery-thumbs">${photos.slice(0, 4).map((photo) => `<span style="background-image: url('${escapeHtml(photo.url)}')" aria-hidden="true"></span>`).join('')}</div>` : ''}
      </div>
    `;
  }
  const coverUrl = isSafePublicAssetUrl(partner?.cover_url) ? partner.cover_url : '';
  if (!coverUrl) {
    return '<div class="landing-partner-cover landing-partner-cover--placeholder" aria-hidden="true">♡</div>';
  }
  return `<div class="landing-partner-cover" style="background-image: url('${escapeHtml(coverUrl)}')" aria-hidden="true"></div>`;
};

const renderSafePartnerImagePreview = (url, kind, label) => {
  const safeUrl = isSafePublicAssetUrl(url) ? url : '';
  const modifier = kind === 'cover' ? 'partner-image-preview--cover' : 'partner-image-preview--logo';
  return safeUrl
    ? `<div class="partner-image-preview ${modifier}" style="background-image: url('${escapeHtml(safeUrl)}')" role="img" aria-label="${escapeHtml(label)}"></div>`
    : `<div class="partner-image-preview ${modifier} partner-image-preview--placeholder" aria-label="${escapeHtml(label)}">${kind === 'cover' ? 'Обложка' : 'Лого'}</div>`;
};

const renderSafeOfferImagePreview = (url, label = 'Фото предложения') => {
  const safeUrl = isSafePublicAssetUrl(url) ? url : '';
  return safeUrl
    ? `<div class="offer-image-preview" style="background-image: url('${escapeHtml(safeUrl)}')" role="img" aria-label="${escapeHtml(label)}"></div>`
    : `<div class="offer-image-preview offer-image-preview--placeholder" aria-label="${escapeHtml(label)}">Фото услуги</div>`;
};

const renderOfferImageUploader = (offer, scope) => {
  const isAdmin = scope === 'admin';
  const offerId = offer?.id;
  const messageKey = isAdmin ? 'offerImage' : 'offerImage';
  const message = isAdmin ? (adminState.formMessages[messageKey] || '') : (partnerState.formMessages[messageKey] || '');
  const inputAttr = isAdmin
    ? `data-admin-offer-image-upload data-offer-id="${escapeHtml(offerId || '')}"`
    : `data-partner-offer-image-upload data-offer-id="${escapeHtml(offerId || '')}"`;
  return `
    <section class="offer-image-uploader">
      <div class="admin-section-heading"><h4>Фото предложения</h4><p>Загружайте JPG, PNG или WEBP до 5 МБ. В превью показываются только /uploads/ и /assets/.</p></div>
      ${renderSafeOfferImagePreview(offer?.image_url, 'Фото предложения')}
      <div class="offer-image-upload-actions">
        ${offerId
          ? `<label class="admin-inline-action">Загрузить фото предложения<input type="file" accept="image/jpeg,image/png,image/webp" ${inputAttr} /></label>`
          : '<p class="form-message">Сначала сохраните предложение, затем загрузите фото.</p>'}
      </div>
      <p class="form-message offer-image-status" data-${isAdmin ? 'form-message' : 'partner-form-message'}="${messageKey}">${escapeHtml(message)}</p>
    </section>
  `;
};

const renderPartnerImageUploader = (partner, scope) => {
  const logoInputAttr = scope === 'admin'
    ? `data-admin-partner-image-upload="logo" data-partner-id="${escapeHtml(partner.id)}"`
    : 'data-partner-image-upload="logo"';
  const coverInputAttr = scope === 'admin'
    ? `data-admin-partner-image-upload="cover" data-partner-id="${escapeHtml(partner.id)}"`
    : 'data-partner-image-upload="cover"';
  return `
    <section class="partner-image-uploader">
      <div class="admin-section-heading"><h4>${scope === 'admin' ? 'Изображения партнёра' : 'Фотографии профиля'}</h4><p>Загружайте JPG, PNG или WEBP до 5 МБ. В превью показываются только /uploads/ и /assets/.</p></div>
      <div class="partner-image-grid">
        <article>
          <span>Логотип</span>
          ${renderSafePartnerImagePreview(partner.logo_url, 'logo', 'Логотип партнёра')}
          <div class="partner-upload-actions">
            <label class="admin-inline-action">Загрузить логотип<input type="file" accept="image/jpeg,image/png,image/webp" ${logoInputAttr} /></label>
          </div>
        </article>
        <article>
          <span>Обложка</span>
          ${renderSafePartnerImagePreview(partner.cover_url, 'cover', 'Обложка партнёра')}
          <div class="partner-upload-actions">
            <label class="admin-inline-action">Загрузить обложку<input type="file" accept="image/jpeg,image/png,image/webp" ${coverInputAttr} /></label>
          </div>
        </article>
      </div>
      <p class="form-message upload-status" data-${scope === 'admin' ? 'form-message="partnerImage"' : 'partner-form-message="profileImages"'}>${escapeHtml(scope === 'admin' ? (adminState.formMessages.partnerImage || '') : (partnerState.formMessages.profileImages || ''))}</p>
    </section>
  `;
};

const renderPartnerGallery = (partner, photos = [], scope = 'partner') => {
  const isAdmin = scope === 'admin';
  const partnerId = partner?.id || '';
  const messageKey = isAdmin ? 'partnerGallery' : 'partnerGallery';
  const message = isAdmin ? (adminState.formMessages[messageKey] || '') : (partnerState.formMessages[messageKey] || '');
  const uploadAttr = isAdmin
    ? `data-admin-partner-photo-upload data-partner-id="${escapeHtml(partnerId)}"`
    : 'data-partner-photo-upload';
  const visiblePhotos = Array.isArray(photos) ? photos : [];
  return `
    <section class="partner-gallery">
      <div class="admin-section-heading">
        <h4>Галерея партнёра</h4>
        <p>${isAdmin ? 'Добавьте живые фото, чтобы карточка выглядела привлекательнее для участниц клуба. Неактивные материалы не видны клиентам.' : 'Новые фото появятся в витрине после проверки и активации администратором.'}</p>
      </div>
      <div class="partner-gallery-upload">
        ${partnerId ? `<label class="admin-inline-action">Загрузить фото в галерею<input type="file" accept="image/jpeg,image/png,image/webp" ${uploadAttr} /></label>` : '<p class="form-message">Сначала сохраните партнёра, затем загрузите фото.</p>'}
      </div>
      ${visiblePhotos.length ? `
        <div class="partner-gallery-grid">
          ${visiblePhotos.map((photo) => {
            const safeUrl = isSafePublicAssetUrl(photo.url) ? photo.url : '';
            return `
              <article class="partner-gallery-item ${photo.is_active ? '' : 'is-muted'}">
                ${!photo.is_active ? '<div class="partner-gallery-status">' + renderStatusBadge('На проверке') + '<small>Ожидает активации администратором.</small></div>' : ''}
                ${safeUrl ? `<div class="partner-gallery-image" style="background-image: url('${escapeHtml(safeUrl)}')" role="img" aria-label="${escapeHtml(photo.alt_text || 'Фото партнёра')}"></div>` : '<div class="partner-gallery-image partner-gallery-empty">Фото скрыто</div>'}
                <form class="partner-gallery-actions" data-${isAdmin ? 'admin' : 'partner'}-gallery-form="photo" data-photo-id="${escapeHtml(photo.id)}">
                  <label>Alt<input name="alt_text" value="${escapeHtml(photo.alt_text || '')}" /></label>
                  <label>Сортировка<input name="sort_order" type="number" value="${escapeHtml(photo.sort_order || 0)}" /></label>
                  <label class="checkbox-row"><input name="is_active" type="checkbox" ${photo.is_active ? 'checked' : ''} ${!isAdmin && !photo.is_active ? 'disabled' : ''} /> Показывать</label>
                  <div class="admin-form-actions">
                    <button type="submit">Сохранить</button>
                    <button class="admin-inline-action" type="button" data-${isAdmin ? 'admin' : 'partner'}-photo-hide="${escapeHtml(photo.id)}">Скрыть фото</button>
                  </div>
                </form>
              </article>
            `;
          }).join('')}
        </div>
      ` : '<div class="partner-gallery-empty">Пока нет фото. Загрузите первое фото для живой витрины.</div>'}
      <p class="form-message" data-${isAdmin ? 'form-message' : 'partner-form-message'}="${messageKey}">${escapeHtml(message)}</p>
    </section>
  `;
};


const getPartnerPrimaryOffer = (partner, options = {}) => {
  if (options.primaryOffer) {
    return options.primaryOffer;
  }
  if (Array.isArray(options.offers) && options.offers.length) {
    return options.offers[0];
  }
  if (Array.isArray(partner?.offers) && partner.offers.length) {
    return partner.offers[0];
  }
  if (partner?.primary_offer || partner?.benefit_text || partner?.discount_text) {
    return {
      title: partner.primary_offer || 'Главная привилегия',
      benefit_text: partner.benefit_text || partner.discount_text,
      description: partner.offer_description,
    };
  }
  return null;
};

const getPartnerMarketplaceCompleteness = (partner, options = {}) => {
  const primaryOffer = getPartnerPrimaryOffer(partner, options);
  const items = [
    ['Обложка', isSafePublicAssetUrl(partner?.cover_url), 'Добавьте обложку'],
    ['Логотип', isSafePublicAssetUrl(partner?.logo_url), 'Добавьте логотип'],
    ['Описание', Boolean(String(partner?.description || '').trim()), 'Добавьте описание'],
    ['Адрес', Boolean(String(partner?.address || '').trim()), 'Добавьте адрес'],
    ['График', Boolean(String(partner?.working_hours || '').trim()), 'Добавьте график работы'],
    ['Контакты', Boolean(String(partner?.phone || partner?.website_url || partner?.social_url || '').trim()), 'Добавьте контакты'],
    ['Предложение', Boolean(primaryOffer), 'Добавьте предложение'],
  ];
  return {
    items,
    filled: items.filter(([, value]) => value).length,
    total: items.length,
    recommendations: items.filter(([, value]) => !value).map(([, , recommendation]) => recommendation),
  };
};

const renderPartnerProfileHints = (partner, options = {}) => {
  const completeness = getPartnerMarketplaceCompleteness(partner, options);
  return `
    <section class="partner-profile-hints">
      <div>
        <span class="section-kicker">Заполненность профиля</span>
        <h4>Профиль заполнен на ${escapeHtml(completeness.filled)} из ${escapeHtml(completeness.total)}</h4>
      </div>
      <ul>
        ${completeness.items.map(([label, isFilled, recommendation]) => `
          <li class="${isFilled ? 'is-complete' : ''}">
            <span>${isFilled ? '✓' : '＋'}</span>
            ${escapeHtml(isFilled ? label : recommendation)}
          </li>
        `).join('')}
      </ul>
    </section>
  `;
};

const renderPartnerMarketplaceCard = (partner = {}, options = {}) => {
  const galleryPhotos = getActivePartnerGalleryPhotos(options.photos || partner.photos);
  const coverUrl = galleryPhotos[0]?.url || (isSafePublicAssetUrl(partner.cover_url) ? partner.cover_url : '');
  const logoUrl = isSafePublicAssetUrl(partner.logo_url) ? partner.logo_url : '';
  const primaryOffer = getPartnerPrimaryOffer(partner, options);
  const contactItems = [
    ['Телефон', partner.phone],
    ['Сайт', partner.website_url],
    ['Соцсеть', partner.social_url],
  ].filter(([, value]) => String(value || '').trim());
  const cityAddress = [partner.city_name || partner.city, partner.address].filter(Boolean).join(' · ');

  return `
    <article class="partner-marketplace-card">
      <div class="partner-marketplace-cover ${coverUrl ? '' : 'partner-marketplace-cover--placeholder'}" ${coverUrl ? `style="background-image: url('${escapeHtml(coverUrl)}')"` : ''} aria-hidden="true">
        ${coverUrl ? '' : '<span>Обложка витрины</span>'}
      </div>
      <div class="partner-marketplace-body">
        <div class="partner-marketplace-heading">
          <div class="partner-marketplace-logo ${logoUrl ? '' : 'partner-marketplace-logo--placeholder'}" ${logoUrl ? `style="background-image: url('${escapeHtml(logoUrl)}')"` : ''} aria-hidden="true">${logoUrl ? '' : '♡'}</div>
          <div>
            <div class="partner-marketplace-badges">
              ${partner.is_active === undefined ? '' : renderActiveStatusBadge(partner.is_active)}
              ${partner.is_verified === undefined ? '' : renderVerifiedStatusBadge(partner.is_verified)}
            </div>
            <h3>${escapeHtml(partner.name || 'Название партнёра')}</h3>
            <p class="partner-marketplace-category">${escapeHtml(formatPartnerCategory(partner))}</p>
          </div>
        </div>
        <dl class="partner-marketplace-meta">
          <div><dt>Город и адрес</dt><dd>${cityAddress ? escapeHtml(cityAddress) : 'Адрес появится в карточке'}</dd></div>
          <div><dt>График работы</dt><dd>${escapeHtml(partner.working_hours || 'График работы появится после заполнения')}</dd></div>
        </dl>
        <p class="partner-marketplace-description">${escapeHtml(partner.description || 'Коротко расскажите, чем вы полезны участницам клуба и какую атмосферу получит клиент.')}</p>
        ${contactItems.length ? `
          <div class="partner-marketplace-contacts">
            ${contactItems.map(([label, value]) => `<span><strong>${escapeHtml(label)}:</strong> ${escapeHtml(value)}</span>`).join('')}
          </div>
        ` : '<div class="partner-marketplace-contacts"><span>Добавьте телефон, сайт или соцсеть для связи</span></div>'}
        <div class="partner-marketplace-offer">
          <span>Главная выгода</span>
          <strong>${escapeHtml(primaryOffer ? formatPartnerBenefit(primaryOffer) : 'Добавьте предложение')}</strong>
          <small>${escapeHtml(primaryOffer?.title || primaryOffer?.description || 'Так клиент быстро поймёт, какую привилегию можно получить.')}</small>
        </div>
        <div class="partner-marketplace-cta">
          <span>${escapeHtml(options.note || 'Так карточку увидит клиент')}</span>
          <button type="button" disabled>${escapeHtml(options.cta || 'Получить привилегию')}</button>
        </div>
      </div>
    </article>
  `;
};

const renderLandingPartnerCard = (partner) => {
  const offers = Array.isArray(partner?.offers) ? partner.offers : [];
  const firstOffer = offers[0] || null;
  const logoUrl = isSafePublicAssetUrl(partner?.logo_url) ? partner.logo_url : '';
  return `
    <article class="landing-partner-card">
      ${renderLandingPartnerImage(partner)}
      <div class="landing-partner-card-body">
        <div class="landing-partner-card-heading">
          ${logoUrl ? `<span class="landing-partner-logo" style="background-image: url('${escapeHtml(logoUrl)}')" aria-hidden="true"></span>` : '<span class="landing-partner-logo landing-partner-logo--placeholder" aria-hidden="true">ЖК</span>'}
          <div>
            <p class="section-kicker">${escapeHtml(partner?.city_name || 'Город клуба')}</p>
            <h3>${escapeHtml(partner?.name || 'Партнёр клуба')}</h3>
          </div>
        </div>
        <p>${escapeHtml(partner?.address || 'Адрес появится в карточке партнёра')}</p>
        ${firstOffer ? `
          <div class="landing-partner-offer">
            <strong>${escapeHtml(formatPartnerBenefit(firstOffer))}</strong>
            <span>${escapeHtml(firstOffer.title)}</span>
            <p>${escapeHtml(firstOffer.description || 'Подробности привилегии уточняйте у партнёра.')}</p>
            ${firstOffer.terms ? `<small>${escapeHtml(firstOffer.terms)}</small>` : ''}
          </div>
        ` : '<div class="landing-partner-offer"><strong>Привилегия скоро появится</strong><p>Партнёр готовит специальное предложение для участниц клуба.</p></div>'}
      </div>
    </article>
  `;
};

const renderLandingPartnerModal = () => {
  const modal = document.querySelector('[data-landing-partner-modal]');
  if (!modal) {
    return;
  }

  if (!landingPartnerModalState.isOpen || !landingPartnerModalState.selectedLandingDirection) {
    modal.hidden = true;
    modal.innerHTML = '';
    return;
  }

  const { selectedLandingDirection, partners, currentIndex, loading, error } = landingPartnerModalState;
  const hasPartners = partners.length > 0;
  const safeIndex = hasPartners ? Math.min(currentIndex, partners.length - 1) : 0;
  landingPartnerModalState.currentIndex = safeIndex;

  modal.hidden = false;
  modal.innerHTML = `
    <div class="landing-partner-panel" role="dialog" aria-modal="false" aria-labelledby="landing-partner-modal-title">
      <div class="landing-partner-panel-header">
        <div>
          <p class="section-kicker">Партнёры клуба</p>
          <h2 id="landing-partner-modal-title">${escapeHtml(selectedLandingDirection.title)}</h2>
        </div>
        <button class="landing-partner-close" type="button" data-landing-partner-close>Закрыть</button>
      </div>
      <div class="landing-partner-carousel">
        ${loading ? '<p class="landing-partner-status">Загружаем партнёров направления…</p>' : ''}
        ${error ? `<p class="landing-partner-status">${escapeHtml(error)}</p>` : ''}
        ${!loading && !error && hasPartners ? renderLandingPartnerCard(partners[safeIndex]) : ''}
        ${!loading && !error && !hasPartners ? '<p class="landing-partner-empty">Партнёры этого направления скоро появятся.</p>' : ''}
      </div>
      <div class="landing-partner-panel-actions">
        <button class="landing-carousel-button" type="button" data-landing-carousel-prev ${hasPartners && partners.length > 1 ? '' : 'disabled'}>←</button>
        <span>${hasPartners ? `${safeIndex + 1} / ${partners.length}` : '0 / 0'}</span>
        <button class="landing-carousel-button" type="button" data-landing-carousel-next ${hasPartners && partners.length > 1 ? '' : 'disabled'}>→</button>
        <a class="primary-button" href="#landing-join" data-landing-modal-cta>${hasPartners ? 'Получить привилегию' : 'Вступить в клуб'}</a>
      </div>
    </div>
  `;
};

const openLandingDirection = async (slug) => {
  const direction = getLandingDirectionBySlug(slug);
  if (!direction) {
    return;
  }

  landingPartnerModalState.isOpen = true;
  landingPartnerModalState.selectedLandingDirection = direction;
  landingPartnerModalState.currentIndex = 0;
  landingPartnerModalState.error = '';
  landingPartnerModalState.partners = landingPartnerModalState.cache[slug] || [];
  landingPartnerModalState.loading = !landingPartnerModalState.cache[slug];
  renderLandingPartnerModal();

  if (landingPartnerModalState.cache[slug]) {
    return;
  }

  try {
    const response = await fetch(`/api/v1/public/landing/partners?category_slug=${encodeURIComponent(slug)}&limit=12`);
    if (!response.ok) {
      throw new Error(await buildErrorMessage(response));
    }
    const data = await response.json();
    landingPartnerModalState.cache[slug] = Array.isArray(data.items) ? data.items : [];
    landingPartnerModalState.partners = landingPartnerModalState.cache[slug];
  } catch (error) {
    landingPartnerModalState.error = 'Не удалось загрузить партнёров. Попробуйте позже.';
  } finally {
    landingPartnerModalState.loading = false;
    renderLandingPartnerModal();
  }
};

const closeLandingPartnerModal = () => {
  landingPartnerModalState.isOpen = false;
  landingPartnerModalState.selectedLandingDirection = null;
  landingPartnerModalState.partners = [];
  landingPartnerModalState.currentIndex = 0;
  landingPartnerModalState.loading = false;
  landingPartnerModalState.error = '';
  renderLandingPartnerModal();
};

const moveLandingPartnerCarousel = (step) => {
  const total = landingPartnerModalState.partners.length;
  if (total < 2) {
    return;
  }
  landingPartnerModalState.currentIndex = (landingPartnerModalState.currentIndex + step + total) % total;
  renderLandingPartnerModal();
};

const apiFetch = async (path, options = {}) => {
  const token = getToken();
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
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

  if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
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
const loadPartnerPhotos = async () => { partnerState.photos = await partnerApiFetch('/api/v1/partners/me/photos'); };
const loadPartnerOffers = async () => {
  partnerState.offers = await partnerApiFetch('/api/v1/partners/me/offers');
  if (partnerState.selectedOfferIdForEdit && !partnerState.offers.some((offer) => String(offer.id) === String(partnerState.selectedOfferIdForEdit))) {
    partnerState.selectedOfferIdForEdit = '';
  }
};
const loadPartnerQrLinks = async () => { partnerState.qrLinks = await partnerApiFetch('/api/v1/partners/me/qr-links'); };
const loadPartnerLeads = async () => { partnerState.leads = await partnerApiFetch('/api/v1/partners/me/leads'); };
const loadPartnerVerifications = async () => { partnerState.verifications = await partnerApiFetch('/api/v1/partners/me/verifications'); };
const loadPartnerActivity = async () => {
  partnerState.activityLoading = true;
  partnerState.activityError = '';
  try {
    const data = await partnerApiFetch('/api/v1/partners/me/activity');
    partnerState.activityItems = Array.isArray(data?.items) ? data.items : [];
  } catch (error) {
    if (!getPartnerToken()) throw error;
    partnerState.activityError = error.message || 'Не удалось загрузить события.';
  } finally {
    partnerState.activityLoading = false;
  }
};
const loadPartnerAnalytics = async () => {
  partnerState.analyticsLoading = true;
  partnerState.analyticsError = '';
  try {
    partnerState.analytics = await partnerApiFetch('/api/v1/partners/me/analytics');
  } catch (error) {
    partnerState.analyticsError = error.message || 'Не удалось загрузить аналитику.';
  } finally {
    partnerState.analyticsLoading = false;
  }
};

const requestClientUserMe = () => clientApiFetch('/api/v1/auth/user-me');
const loadClientProfile = async () => { clientState.profile = await clientApiFetch('/api/v1/clients/me'); };
const loadClientSubscription = async () => { clientState.subscription = await clientApiFetch('/api/v1/clients/me/subscription'); };
const loadClientVerifications = async () => { clientState.verifications = await clientApiFetch('/api/v1/clients/me/verifications'); };
const loadClientActivity = async () => {
  clientState.activityLoading = true;
  clientState.activityError = '';
  try {
    const data = await clientApiFetch('/api/v1/clients/me/activity');
    clientState.activityItems = Array.isArray(data?.items) ? data.items : [];
  } catch (error) {
    if (!getClientToken()) throw error;
    clientState.activityError = error.message || 'Не удалось загрузить события.';
  } finally {
    clientState.activityLoading = false;
  }
};

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
  if (clientState.selectedPartnerId && !clientState.partners.some((partner) => String(partner.id) === clientState.selectedPartnerId)) {
    clientState.selectedPartner = null;
    clientState.selectedPartnerId = '';
  }
};

const loadClientPartnerDetail = async (partnerId) => {
  clientState.selectedPartner = await clientApiFetch(`/api/v1/clients/partners/${partnerId}`);
  clientState.selectedPartnerId = String(partnerId);
};

const loadClientPartnerOffers = async (partnerId) => {
  clientState.offersByPartner[partnerId] = await clientApiFetch(`/api/v1/clients/partners/${partnerId}/offers`);
};

const openClientPartnerMarketplace = async (partnerId) => {
  await Promise.all([loadClientPartnerDetail(partnerId), loadClientPartnerOffers(partnerId)]);
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
  if (clientState.activeTab === 'activity') {
    return renderClientActivityTab();
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
        ['Активность', renderBoolStatusBadge(profile.is_active)],
      ].map(([label, value]) => `
        <div class="summary-card"><span>${label}</span><strong>${renderDisplayValue(value)}</strong></div>
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
      <div class="summary-card"><span>Статус</span><strong>${renderStatusBadge(formatStatus(subscription.status))}</strong></div>
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
    <div class="client-marketplace-grid client-catalog-grid">
      ${clientState.partners.length ? clientState.partners.map(renderClientPartnerCard).join('') : renderClientEmptyState('Партнёры пока не найдены', 'Попробуйте выбрать другой город или категорию.')}
    </div>
    ${clientState.selectedPartner ? renderClientPartnerDetail(clientState.selectedPartner) : ''}
  `;
};

const getClientPartnerVisuals = (partner = {}) => {
  const photos = getActivePartnerGalleryPhotos(partner.photos);
  return {
    photos,
    coverUrl: photos[0]?.url || (isSafePublicAssetUrl(partner.cover_url) ? partner.cover_url : ''),
    logoUrl: isSafePublicAssetUrl(partner.logo_url) ? partner.logo_url : '',
  };
};

const renderClientPartnerCover = (partner = {}, className = 'client-partner-cover') => {
  const { coverUrl } = getClientPartnerVisuals(partner);
  return `
    <div class="${className} ${coverUrl ? '' : `${className}--placeholder`}" ${coverUrl ? `style="background-image: url('${escapeHtml(coverUrl)}')" role="img" aria-label="${escapeHtml(partner.name || 'Партнёр')}"` : 'aria-hidden="true"'}>
      ${coverUrl ? '' : '<span>Фото витрины</span>'}
    </div>
  `;
};

const renderClientPartnerLogo = (partner = {}) => {
  const { logoUrl } = getClientPartnerVisuals(partner);
  return `<div class="client-partner-logo ${logoUrl ? '' : 'client-partner-logo--placeholder'}" ${logoUrl ? `style="background-image: url('${escapeHtml(logoUrl)}')"` : ''} aria-hidden="true">${logoUrl ? '' : '♡'}</div>`;
};

const renderClientPartnerGallery = (partner = {}) => {
  const { photos } = getClientPartnerVisuals(partner);
  if (!photos.length) {
    return renderClientPartnerCover(partner, 'client-partner-gallery-main');
  }
  return `
    <div class="client-partner-gallery" aria-label="Галерея партнёра">
      <div class="client-partner-gallery-main" style="background-image: url('${escapeHtml(photos[0].url)}')" role="img" aria-label="${escapeHtml(photos[0].alt_text || partner.name || 'Фото партнёра')}"></div>
      ${photos.length > 1 ? `<div class="client-partner-gallery-thumbs">${photos.slice(0, 6).map((photo) => `<span style="background-image: url('${escapeHtml(photo.url)}')" aria-hidden="true"></span>`).join('')}</div>` : ''}
    </div>
  `;
};

const renderClientPartnerCard = (partner) => {
  const partnerId = partner.id;
  const cityAddress = [partner.city_name, partner.address].filter(Boolean).join(' · ');
  return `
    <article class="client-partner-card">
      ${renderClientPartnerCover(partner)}
      <div class="client-partner-card-body">
        <div class="client-card-topline">
          ${renderClientPartnerLogo(partner)}
          <div>
            <span>${formatValue(formatClientCategory(partner.category_slug))}</span>
            ${partner.is_verified ? '<span class="status-badge status-badge--success">Проверенный партнёр</span>' : ''}
          </div>
        </div>
        <h4>${formatValue(partner.name)}</h4>
        <p>${formatValue(partner.description || 'Витрина услуг партнёра скоро пополнится подробностями.')}</p>
        <div class="client-card-location">${formatValue(cityAddress || partner.city_name || partner.address)}</div>
        <div class="client-card-actions">
          <button type="button" data-client-load-offers="${escapeHtml(partnerId)}">Смотреть предложения</button>
          <button type="button" data-client-verify-partner="${escapeHtml(partnerId)}">Получить привилегию</button>
        </div>
      </div>
    </article>
  `;
};

const renderClientPartnerDetail = (partner = {}) => {
  const partnerId = partner.id;
  const offers = clientState.offersByPartner[partnerId] || [];
  const cityAddress = [partner.city_name, partner.address].filter(Boolean).join(' · ');
  const contacts = [
    ['Телефон', partner.phone],
    ['Сайт', partner.website_url],
    ['Соцсети', partner.social_url],
  ].filter(([, value]) => String(value || '').trim());
  return `
    <section class="client-partner-detail">
      <div class="client-partner-detail-hero">
        ${renderClientPartnerGallery(partner)}
        <div class="client-partner-detail-info">
          <div class="client-card-topline">
            ${renderClientPartnerLogo(partner)}
            <div>
              <span>${formatValue(formatClientCategory(partner.category_slug))}</span>
              ${partner.is_verified ? '<span class="status-badge status-badge--success">Проверенный партнёр</span>' : ''}
            </div>
          </div>
          <h3>${formatValue(partner.name)}</h3>
          <p>${formatValue(partner.description || 'Описание партнёра скоро появится.')}</p>
          <dl class="client-card-details">
            <div><dt>Город и адрес</dt><dd>${formatValue(cityAddress)}</dd></div>
            <div><dt>График работы</dt><dd>${formatValue(partner.working_hours)}</dd></div>
            ${contacts.length ? contacts.map(([label, value]) => `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join('') : ''}
          </dl>
          <button type="button" data-client-verify-partner="${escapeHtml(partnerId)}">Получить привилегию</button>
        </div>
      </div>
      <div class="client-partner-offers">
        <div class="admin-section-heading"><h4>Предложения партнёра</h4><p>Выберите услугу и получите клубную привилегию.</p></div>
        ${offers.length ? offers.map((offer) => renderClientOffer(partnerId, offer)).join('') : '<div class="client-partner-empty">Предложения скоро появятся.</div>'}
      </div>
    </section>
  `;
};

const renderClientOffer = (partnerId, offer) => renderOfferMarketplaceCard(offer, {
  cta: 'Получить привилегию',
  note: 'Карточка привилегии партнёра',
  actionHtml: `<button type="button" data-client-verify-offer="${escapeHtml(partnerId)}" data-offer-id="${escapeHtml(offer.id)}">Получить привилегию</button>`,
});

const renderClientVerificationResult = (verification) => `
  <div class="client-verification-result privilege-success-panel" role="status" data-privilege-success-panel>
    <p class="section-kicker">Привилегия активирована</p>
    <div class="privilege-success-panel__heading">
      <div>
        <h4>${formatValue(verification.partner_name)}</h4>
        <p>${formatValue(verification.offer_title || 'Клубная привилегия партнёра')}</p>
      </div>
      ${renderStatusBadge(formatPrivilegeStatus(verification.status))}
    </div>
    <div class="privilege-code" aria-label="Код подтверждения">${formatValue(verification.code)}</div>
    <p class="client-warning">Покажите этот код партнёру перед оплатой/получением услуги.</p>
    <dl class="client-card-details privilege-success-panel__meta">
      <div><dt>Срок действия</dt><dd>${formatValue(formatDate(verification.expires_at))}</dd></div>
      <div><dt>Создано</dt><dd>${formatValue(formatDate(verification.created_at))}</dd></div>
    </dl>
    <div class="client-card-actions">
      <button type="button" data-client-dismiss-privilege>Понятно</button>
      <button type="button" class="admin-inline-action" data-client-open-privileges>Мои привилегии</button>
    </div>
  </div>
`;

const renderClientPrivilegeCard = (item) => `
  <article class="client-privilege-card" data-client-privilege-card>
    <div class="client-card-topline">
      ${renderStatusBadge(formatPrivilegeStatus(item.status))}
      <span>${escapeHtml(formatDate(item.created_at) || 'Дата создания не указана')}</span>
    </div>
    <h4>${formatValue(item.partner_name)}</h4>
    <p>${formatValue(item.offer_title || 'Клубная привилегия партнёра')}</p>
    <div class="privilege-code privilege-code--card" aria-label="Код подтверждения">${formatValue(item.code)}</div>
    <dl class="client-card-details">
      <div><dt>Срок действия</dt><dd>${formatValue(formatDate(item.expires_at))}</dd></div>
      <div><dt>Подтверждено</dt><dd>${formatValue(formatDate(item.confirmed_at))}</dd></div>
    </dl>
  </article>
`;

const renderClientHistoryTab = () => `
  <div class="admin-section-heading"><h4>Мои привилегии</h4><p>История ваших активных и использованных кодов партнёрских предложений.</p></div>
  ${clientState.verifications.length
    ? `<div class="client-privilege-card-grid">${clientState.verifications.map(renderClientPrivilegeCard).join('')}</div>`
    : renderClientEmptyState('Пока нет привилегий', 'Выберите оффер в каталоге и нажмите «Получить привилегию».')}
`;

const renderClientActivityTab = () => `
  <div class="admin-section-heading admin-page-heading">
    <p class="section-kicker">Activity feed</p>
    <h4>Активность</h4>
    <p>Здесь появятся ваши действия и статусы привилегий.</p>
  </div>
  ${renderActivityFeed(clientState.activityItems, { loading: clientState.activityLoading, error: clientState.activityError })}
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
  if (partnerState.activeTab === 'analytics') {
    return renderPartnerAnalyticsTab();
  }
  if (partnerState.activeTab === 'activity') {
    return renderPartnerActivityTab();
  }
  return renderPartnerProfileTab();
};

const renderPartnerProfileTab = () => {
  const profile = partnerState.profile || {};
  return `
    <div class="admin-section-heading">
      <h4>Профиль партнёра</h4>
      <p>Настройте, как ваша карточка будет выглядеть для участниц клуба.</p>
    </div>
    <div class="partner-profile-layout">
      <aside class="partner-profile-preview">
        <span class="section-kicker">Preview витрины</span>
        ${renderPartnerMarketplaceCard(profile, { offers: partnerState.offers, note: 'Так карточку увидит клиент', photos: partnerState.photos })}
        ${renderPartnerProfileHints(profile, { offers: partnerState.offers })}
      </aside>
      <section class="partner-profile-settings">
        <div class="partner-profile-grid">
          ${[
            ['Название', profile.name],
            ['Город', profile.city_name],
            ['Категория', formatPartnerCategory(profile)],
            ['Активность', renderBoolStatusBadge(profile.is_active)],
            ['Проверка', renderVerifiedStatusBadge(profile.is_verified)],
          ].map(([label, value]) => `<article class="summary-card"><span>${escapeHtml(label)}</span><strong>${renderDisplayValue(value)}</strong></article>`).join('')}
        </div>
        <p class="form-message partner-profile-admin-note">Название, город и категорию редактирует администратор. Активность и проверка тоже контролируются администратором.</p>
        <form class="admin-form" data-partner-form="profile">
          <h4>Настройка витрины</h4>
          <label>Описание<textarea name="description" rows="4">${escapeHtml(profile.description || '')}</textarea></label>
          <label>Адрес<input name="address" value="${escapeHtml(profile.address || '')}" /></label>
          <label>Телефон<input name="phone" autocomplete="tel" value="${escapeHtml(profile.phone || '')}" /></label>
          <label>Сайт<input name="website_url" value="${escapeHtml(profile.website_url || '')}" /></label>
          <label>Соцсеть<input name="social_url" value="${escapeHtml(profile.social_url || '')}" /></label>
          <label>График работы<input name="working_hours" value="${escapeHtml(profile.working_hours || '')}" /></label>
          ${renderPartnerImageUploader(profile, 'partner')}
          ${renderPartnerGallery(profile, partnerState.photos, 'partner')}
          <details class="partner-profile-advanced">
            <summary>URL изображений</summary>
            <p class="form-message">Основной способ обновления — кнопки загрузки. URL показывается для проверки и отправляется как раньше.</p>
            <label>Логотип URL<input name="logo_url" value="${escapeHtml(profile.logo_url || '')}" readonly /></label>
            <label>Обложка URL<input name="cover_url" value="${escapeHtml(profile.cover_url || '')}" readonly /></label>
          </details>
          <button type="submit">Сохранить профиль</button>
          <p class="form-message" data-partner-form-message="profile">${escapeHtml(partnerState.formMessages.profile || '')}</p>
        </form>
      </section>
    </div>
  `;
};

const renderPartnerOfferAction = (offer) => `
  <button class="admin-inline-action" type="button" data-partner-offer-edit="${escapeHtml(offer.id)}">Редактировать</button>
  ${offer.is_active
    ? `<button class="admin-inline-action" type="button" data-partner-offer-toggle="${escapeHtml(offer.id)}">Скрыть</button>`
    : '<button class="admin-inline-action" type="button" disabled>На проверке</button>'}
`;

const renderPartnerOfferForm = () => {
  const offer = partnerState.offers.find((item) => String(item.id) === String(partnerState.selectedOfferIdForEdit));
  const isEdit = Boolean(offer);
  const previewOffer = isEdit ? offer : { is_active: false };

  return `
    <section class="offer-marketplace-preview">
      <span class="section-kicker">Preview предложения</span>
      ${renderOfferMarketplaceCard(previewOffer, { note: 'Так предложение увидит клиент' })}
    </section>
    <form class="admin-form admin-form--inline" data-partner-form="${isEdit ? 'offerEdit' : 'offer'}" ${isEdit ? `data-offer-id="${escapeHtml(offer.id)}"` : ''}>
      <h4>${isEdit ? 'Редактировать предложение' : 'Новое предложение'}</h4>
      <p class="form-message">Новое предложение появится у клиентов после проверки и активации администратором.</p>
      ${isEdit && offer?.is_active === false ? '<p class="form-message">Ожидает активации администратором.</p>' : ''}
      <label>Название<input name="title" required value="${escapeHtml(offer?.title || '')}" /></label>
      <label>Краткая выгода<input name="benefit_text" value="${escapeHtml(offer?.benefit_text || '')}" /></label>
      <label>Описание<textarea name="description" rows="3">${escapeHtml(offer?.description || '')}</textarea></label>
      <label>Условия<textarea name="conditions" rows="3">${escapeHtml(offer?.conditions || '')}</textarea></label>
      <label>Базовая цена<input name="base_price" inputmode="decimal" value="${escapeHtml(offer?.base_price || '')}" /></label>
      <label>Скидка, %<input name="discount_percent" inputmode="decimal" value="${escapeHtml(offer?.discount_percent || '')}" /></label>
      ${renderOfferImageUploader(offer, 'partner')}
      <details class="partner-profile-advanced">
        <summary>URL изображения предложения</summary>
        <p class="form-message">Основной способ обновления — кнопка загрузки. URL показывается для проверки и отправляется как раньше.</p>
        <label>URL изображения<input name="image_url" value="${escapeHtml(offer?.image_url || '')}" readonly placeholder="/uploads/offer.webp или /assets/offer.webp" /></label>
      </details>
      ${isEdit ? `<label class="checkbox-row"><input name="is_active" type="checkbox" ${offer?.is_active === false ? '' : 'checked'} ${offer?.is_active === false ? 'disabled' : ''} /> Активно</label>` : ''}
      <label>Порядок сортировки<input name="sort_order" type="number" value="${escapeHtml(offer?.sort_order || 0)}" /></label>
      <div class="admin-form-actions">
        <button type="submit">${isEdit ? 'Сохранить изменения' : 'Создать предложение'}</button>
        ${isEdit ? '<button class="admin-inline-action" type="button" data-partner-offer-edit-cancel>Отмена</button>' : ''}
      </div>
      <p class="form-message" data-partner-form-message="${isEdit ? 'offerEdit' : 'offer'}">${escapeHtml(partnerState.formMessages[isEdit ? 'offerEdit' : 'offer'] || '')}</p>
    </form>
  `;
};

const renderPartnerOffersTab = () => `
  <div class="admin-section-heading"><h4>Предложения и привилегии</h4><p>Оформите услуги так, чтобы участницы сразу понимали выгоду. Новое предложение появится у клиентов после проверки и активации администратором.</p></div>
  ${partnerState.offers.length ? `
    <div class="offer-card-grid">
      ${partnerState.offers.map((offer) => renderOfferMarketplaceCard(offer, {
        note: offer.is_active ? 'Так предложение увидит клиент' : 'Ожидает активации администратором.',
        actionHtml: `${renderPartnerOfferAction(offer)}<button type="button" disabled>Получить привилегию</button>`,
      })).join('')}
    </div>
    ${renderTable(
      ['Название', 'Краткая выгода', 'Описание', 'Условия', 'Базовая цена', 'Скидка, %', 'Активно', 'Порядок сортировки', 'Действие'],
      partnerState.offers.map((offer) => [
        formatValue(offer.title),
        formatValue(formatPartnerBenefit(offer)),
        formatValue(offer.description),
        formatValue(offer.conditions),
        formatValue(formatOfferBasePrice(offer.base_price)),
        formatValue(formatDiscountPercent(offer.discount_percent) || '—'),
        renderPartnerReviewStatusBadge(offer.is_active),
        formatValue(offer.sort_order),
        renderPartnerOfferAction(offer),
      ]),
      true,
    )}
  ` : renderPartnerEmptyState('Пока нет предложений.', 'Добавьте первое предложение, чтобы клиенты увидели вашу привилегию.')}
  ${renderPartnerOfferForm()}
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
      renderActiveStatusFeminineBadge(link.is_active),
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
  : '';

const renderPartnerConfirmationCard = (item) => `
  <article class="partner-confirmation-card" data-partner-confirmation-card>
    <div class="client-card-topline">
      ${renderStatusBadge(formatPrivilegeStatus(item.status))}
      <span>${escapeHtml(formatDate(item.created_at) || 'Новый код')}</span>
    </div>
    <h4>${formatValue(item.offer_title || 'Клубная привилегия')}</h4>
    <p>Партнёр: <strong>${formatValue(item.partner_name)}</strong></p>
    <div class="privilege-code privilege-code--card" aria-label="Код клиента">${formatValue(item.code)}</div>
    <dl class="client-card-details">
      <div><dt>Клиент</dt><dd>${formatValue(item.client_name || 'Клиент клуба')}</dd></div>
      <div><dt>Истекает</dt><dd>${formatValue(formatDate(item.expires_at))}</dd></div>
      <div><dt>Подтверждено</dt><dd>${formatValue(formatDate(item.confirmed_at))}</dd></div>
    </dl>
    ${renderPartnerVerificationAction(item) ? `<div class="client-card-actions">${renderPartnerVerificationAction(item)}</div>` : ''}
  </article>
`;

const renderPartnerVerificationsTab = () => `
  <div class="admin-section-heading"><h4>Подтверждения</h4><p>Подтверждайте активные клиентские коды до окончания срока действия.</p></div>
  ${partnerState.verifications.length
    ? `<div class="partner-confirmation-card-grid">${partnerState.verifications.map(renderPartnerConfirmationCard).join('')}</div>`
    : renderPartnerEmptyState('Пока нет подтверждений.', 'Когда клиент покажет код привилегии, подтверждение появится здесь.')}
`;

const renderPartnerAnalyticsTab = () => renderAnalyticsSection(partnerState.analytics, {
  title: 'Аналитика',
  loading: partnerState.analyticsLoading,
  error: partnerState.analyticsError,
});

const renderPartnerActivityTab = () => `
  <div class="admin-section-heading admin-page-heading">
    <p class="section-kicker">Activity feed</p>
    <h4>Активность</h4>
    <p>Лента помогает быстро видеть, что происходит с клиентами, QR и привилегиями.</p>
  </div>
  ${renderActivityFeed(partnerState.activityItems, { loading: partnerState.activityLoading, error: partnerState.activityError })}
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

const loadAdminPartnerPhotos = async (partnerId) => {
  if (!partnerId) return;
  adminState.partnerPhotosByPartner[partnerId] = await apiFetch(`/api/v1/admin/partners/${partnerId}/photos`);
};

const loadAdminPartnerAnalytics = async (partnerId) => {
  if (!partnerId) return;
  adminState.partnerAnalyticsLoading = true;
  adminState.partnerAnalyticsError = '';
  adminState.selectedPartnerAnalytics = adminState.partnerAnalyticsById[partnerId] || null;
  try {
    const analytics = await apiFetch(`/api/v1/admin/partners/${partnerId}/analytics`);
    adminState.partnerAnalyticsById[partnerId] = analytics;
    adminState.selectedPartnerAnalytics = analytics;
  } catch (error) {
    adminState.partnerAnalyticsError = error.message || 'Не удалось загрузить аналитику партнёра.';
  } finally {
    adminState.partnerAnalyticsLoading = false;
  }
};

const loadLeads = async () => {
  adminState.leads = await apiFetch('/api/v1/admin/leads/partners');
};

const loadVerifications = async () => {
  adminState.verifications = await apiFetch('/api/v1/admin/verifications');
};

const buildAdminActivityPath = () => {
  const params = new URLSearchParams();
  if (adminState.activityEventType) params.set('event_type', adminState.activityEventType);
  if (adminState.selectedPartnerIdForActivity) params.set('partner_id', adminState.selectedPartnerIdForActivity);
  params.set('limit', '50');
  return `/api/v1/admin/activity?${params.toString()}`;
};

const loadAdminActivity = async () => {
  adminState.activityLoading = true;
  adminState.activityError = '';
  try {
    const data = await apiFetch(buildAdminActivityPath());
    adminState.activityItems = Array.isArray(data?.items) ? data.items : [];
  } catch (error) {
    if (!getToken()) throw error;
    adminState.activityError = error.message || 'Не удалось загрузить события.';
  } finally {
    adminState.activityLoading = false;
  }
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
    case 'activity':
      return renderAdminActivityTab();
    default:
      return renderOverviewTab();
  }
};

const renderAdminActivityTab = () => `
  <div class="admin-section-heading admin-page-heading">
    <p class="section-kicker">Activity feed</p>
    <h4>Активность</h4>
    <p>Общая лента событий по привилегиям, QR, партнёрам и предложениям.</p>
  </div>
  <form class="activity-filter" data-admin-activity-filter>
    <label>Тип события
      <select name="event_type" data-admin-activity-event-type>
        ${activityEventFilters.map((filter) => `<option value="${escapeHtml(filter.value)}" ${adminState.activityEventType === filter.value ? 'selected' : ''}>${escapeHtml(filter.label)}</option>`).join('')}
      </select>
    </label>
  </form>
  ${renderActivityFeed(adminState.activityItems, { loading: adminState.activityLoading, error: adminState.activityError })}
`;

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
            renderBoolStatusBadge(item.is_active),
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
            renderBoolStatusBadge(city.is_active),
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
            renderActiveStatusFeminineBadge(category.is_active),
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
  const photos = adminState.partnerPhotosByPartner[adminState.selectedPartnerIdForEdit] || [];
  if (!partner) {
    return '';
  }

  return `
    <section class="partner-profile-layout partner-profile-layout--admin">
      <aside class="partner-profile-preview">
        <div class="admin-section-heading"><h4>Витрина партнёра</h4><p>Так администратор видит публичную marketplace-карточку партнёра.</p></div>
        ${renderPartnerMarketplaceCard(partner, { note: 'Так карточку увидит клиент', photos })}
        ${renderPartnerProfileHints(partner)}
      </aside>
      <form class="admin-form partner-profile-settings" data-admin-form="partnerEdit" data-partner-id="${escapeHtml(partner.id)}">
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
        <label>График работы<input name="working_hours" value="${escapeHtml(partner.working_hours || '')}" /></label>
        <label>Порядок сортировки<input name="sort_order" type="number" value="${escapeHtml(partner.sort_order ?? 0)}" /></label>
        <label class="checkbox-row"><input name="is_active" type="checkbox" ${partner.is_active ? 'checked' : ''} /> Активен</label>
        <label class="checkbox-row"><input name="is_verified" type="checkbox" ${partner.is_verified ? 'checked' : ''} /> Проверен</label>
        ${renderPartnerImageUploader(partner, 'admin')}
        ${renderPartnerGallery(partner, photos, 'admin')}
        ${renderAnalyticsSection(adminState.selectedPartnerAnalytics, {
          title: 'Аналитика партнёра',
          loading: adminState.partnerAnalyticsLoading,
          error: adminState.partnerAnalyticsError,
        })}
        <details class="partner-profile-advanced">
          <summary>URL изображения</summary>
          <p class="form-message">Загрузка логотипа и обложки — основной способ обновления изображений. Ручной URL оставлен как дополнительное поле для уже поддерживаемых /uploads/ и /assets/.</p>
          <label>Логотип URL<input name="logo_url" value="${escapeHtml(partner.logo_url || '')}" /></label>
          <label>Обложка URL<input name="cover_url" value="${escapeHtml(partner.cover_url || '')}" /></label>
        </details>
        <div class="admin-form-actions">
          <button type="submit">Сохранить изменения</button>
          <button class="admin-inline-action" type="button" data-admin-partner-edit-cancel>Отмена</button>
        </div>
        <p class="form-message" data-form-message="partnerEdit">${escapeHtml(adminState.formMessages.partnerEdit || '')}</p>
      </form>
    </section>
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
            renderBoolStatusBadge(partner.is_active),
            renderVerifiedStatusBadge(partner.is_verified),
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
  <label class="admin-inline-action admin-table-action">Загрузить фото предложения<input type="file" accept="image/jpeg,image/png,image/webp" data-admin-offer-image-upload data-offer-id="${escapeHtml(offer.id)}" /></label>
`;

const renderOfferEditForm = () => {
  const offer = adminState.offers.find((item) => String(item.id) === String(adminState.selectedOfferIdForEdit));
  if (!offer) {
    return '';
  }

  return `
    <section class="offer-marketplace-preview">
      <span class="section-kicker">Preview предложения</span>
      ${renderOfferMarketplaceCard(offer, { note: 'Так предложение увидит клиент' })}
    </section>
    <form class="admin-form admin-form--inline" data-admin-form="offerEdit" data-offer-id="${escapeHtml(offer.id)}">
      <h4>Редактировать предложение</h4>
      <label>Название<input name="title" required value="${escapeHtml(offer.title || '')}" /></label>
      <label>Скидка / выгода<input name="benefit_text" value="${escapeHtml(offer.benefit_text || '')}" /></label>
      <label>Описание<textarea name="description" rows="3">${escapeHtml(offer.description || '')}</textarea></label>
      <label>Условия<textarea name="conditions" rows="3">${escapeHtml(offer.conditions || '')}</textarea></label>
      <label>Базовая цена<input name="base_price" type="number" step="0.01" value="${escapeHtml(offer.base_price || '')}" /></label>
      <label>Скидка, %<input name="discount_percent" type="number" step="0.01" value="${escapeHtml(offer.discount_percent || '')}" /></label>
      ${renderOfferImageUploader(offer, 'admin')}
      <details class="partner-profile-advanced">
        <summary>URL изображения предложения</summary>
        <p class="form-message">Основной способ обновления — кнопка загрузки. URL показывается для проверки и отправляется как раньше.</p>
        <label>URL изображения<input name="image_url" value="${escapeHtml(offer.image_url || '')}" readonly placeholder="/uploads/offer.webp или /assets/offer.webp" /></label>
      </details>
      <label class="checkbox-row"><input name="is_active" type="checkbox" ${offer.is_active ? 'checked' : ''} /> Активно</label>
      <label>Порядок сортировки<input name="sort_order" type="number" value="${escapeHtml(offer.sort_order || 0)}" /></label>
      <div class="admin-form-actions">
        <button type="submit">Сохранить изменения</button>
        <button class="admin-inline-action" type="button" data-admin-offer-edit-cancel>Отмена</button>
      </div>
      <p class="form-message" data-form-message="offerEdit">${escapeHtml(adminState.formMessages.offerEdit || '')}</p>
    </form>
  `;
};

const renderOfferCreateForm = () => `
  <section class="offer-marketplace-preview">
    <span class="section-kicker">Preview предложения</span>
    ${renderOfferMarketplaceCard({ is_active: true }, { note: 'Так предложение увидит клиент' })}
  </section>
  <form class="admin-form admin-form--inline" data-admin-form="offer">
    <h4>Новое предложение</h4>
    <label>Название предложения<input name="title" required /></label>
    <label>Краткая выгода<input name="benefit_text" /></label>
    <label>Описание<textarea name="description" rows="3"></textarea></label>
    <label>Условия<textarea name="conditions" rows="3"></textarea></label>
    <label>Базовая цена<input name="base_price" type="number" step="0.01" /></label>
    <p class="form-message">Цена со скидкой рассчитывается по базовой цене и проценту скидки.</p>
    <label>Скидка, %<input name="discount_percent" type="number" step="0.01" /></label>
    ${renderOfferImageUploader(null, 'admin')}
    <details class="partner-profile-advanced">
      <summary>URL изображения предложения</summary>
      <p class="form-message">Сначала сохраните предложение, затем загрузите фото.</p>
      <label>URL изображения<input name="image_url" readonly placeholder="/uploads/offer.webp или /assets/offer.webp" /></label>
    </details>
    <label class="checkbox-row"><input name="is_active" type="checkbox" checked /> Активен</label>
    <label>Порядок сортировки<input name="sort_order" type="number" value="0" /></label>
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
      ${offers.length ? `<div class="offer-card-grid">${offers.map((offer) => renderOfferMarketplaceCard(offer, {
        note: 'Так предложение увидит клиент',
        actionHtml: `${renderAdminOfferAction(offer)}<button type="button" disabled>Получить привилегию</button>`,
      })).join('')}</div>` : ''}
      ${renderTable(
        ['Название предложения', 'Краткая выгода', 'Базовая цена', 'Скидка, %', 'Активно', 'Сортировка', 'Действие'],
        offers.map((offer) => [formatValue(offer.title), formatValue(formatPartnerBenefit(offer)), formatValue(formatOfferBasePrice(offer.base_price)), formatValue(formatDiscountPercent(offer.discount_percent) || '—'), renderActiveStatusBadge(offer.is_active), formatValue(offer.sort_order), renderAdminOfferAction(offer)]),
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
        qrLinks.map((link) => [formatValue(link.slug), link.qr_url ? `<a href="${escapeHtml(link.qr_url)}" target="_blank" rel="noreferrer">${escapeHtml(link.qr_url)}</a>` : '—', formatValue(link.target_url), renderActiveStatusFeminineBadge(link.is_active), renderAdminQrAction(link)]),
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
      verifications.map((item) => [renderStatusBadge(formatStatus(item.status)), formatValue(item.code), formatValue(item.partner_name), formatValue(`${item.client_name || '—'} / ${item.client_id}`), formatValue(item.offer_title), formatValue(formatDate(item.created_at)), formatValue(formatDate(item.expires_at)), formatValue(formatDate(item.confirmed_at))]),
      true,
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
    } else if (adminState.activeTab === 'activity') {
      adminState.activityLoading = true;
      adminState.activityError = '';
      renderAdminLayout();
      await loadAdminActivity();
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
      await Promise.all([loadPartnerProfile(), loadPartnerOffers(), loadPartnerPhotos()]);
    } else if (partnerState.activeTab === 'offers') {
      await loadPartnerOffers();
    } else if (partnerState.activeTab === 'qr') {
      await Promise.all([loadPartnerQrLinks(), loadPartnerLeads()]);
    } else if (partnerState.activeTab === 'verifications') {
      await loadPartnerVerifications();
    } else if (partnerState.activeTab === 'analytics') {
      await loadPartnerAnalytics();
    } else if (partnerState.activeTab === 'activity') {
      partnerState.activityLoading = true;
      partnerState.activityError = '';
      renderPartnerLayout();
      await loadPartnerActivity();
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
    } else if (clientState.activeTab === 'activity') {
      clientState.activityLoading = true;
      clientState.activityError = '';
      renderClientLayout();
      await loadClientActivity();
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

const buildPartnerOfferPayload = (formData) => ({
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

const submitPartnerOffer = async (form) => {
  const formData = new FormData(form);
  await partnerPostJson('/api/v1/partners/me/offers', buildPartnerOfferPayload(formData));
  setPartnerFormMessage('offer', 'Предложение отправлено на проверку. После активации администратором оно появится у клиентов.');
  setPartnerPanelMessage('Предложение отправлено на проверку. После активации администратором оно появится у клиентов.', 'success');
  form.reset();
  await loadPartnerOffers();
};

const submitPartnerOfferEdit = async (form) => {
  const formData = new FormData(form);
  await partnerPatchJson(`/api/v1/partners/me/offers/${form.dataset.offerId}`, buildPartnerOfferPayload(formData));
  partnerState.selectedOfferIdForEdit = '';
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
    } else if (formType === 'offerEdit') {
      await submitPartnerOfferEdit(form);
    }
    if (formType !== 'offer') {
      setPartnerFormMessage(formType, 'Сохранено.');
      setPartnerPanelMessage('Сохранено.', 'success');
    }
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
    setClientPanelMessage('Привилегия активирована. Покажите код партнёру.', 'success');
  } catch (error) {
    setClientPanelMessage(formatPrivilegeErrorMessage(error.message), 'error');
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
    setPartnerPanelMessage(offer.is_active ? 'Предложение скрыто.' : 'Ожидает активации администратором.', 'success');
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
    setPartnerPanelMessage(formatPrivilegeErrorMessage(error.message), 'error');
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
  working_hours: getOptionalText(formData, 'working_hours'),
  logo_url: getOptionalText(formData, 'logo_url'),
  cover_url: getOptionalText(formData, 'cover_url'),
  is_active: formData.has('is_active'),
  is_verified: formData.has('is_verified'),
  sort_order: Number(formData.get('sort_order') || 0),
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
    website_url: getOptionalText(formData, 'website_url'),
    social_url: getOptionalText(formData, 'social_url'),
    working_hours: getOptionalText(formData, 'working_hours'),
    logo_url: getOptionalText(formData, 'logo_url'),
    cover_url: getOptionalText(formData, 'cover_url'),
    owner_user_id: formData.get('owner_user_id') ? Number(formData.get('owner_user_id')) : null,
    is_active: formData.has('is_active'),
    is_verified: formData.has('is_verified'),
    sort_order: Number(formData.get('sort_order') || 0),
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
  base_price: decimalOrNull(formData, 'base_price'),
  discount_percent: decimalOrNull(formData, 'discount_percent'),
  image_url: getOptionalText(formData, 'image_url'),
  sort_order: Number(formData.get('sort_order') || 0),
  is_active: formData.has('is_active'),
});

const submitOffer = async (form) => {
  const formData = new FormData(form);
  await postJson(`/api/v1/admin/partners/${adminState.selectedPartnerIdForOffers}/offers`, buildOfferTextPayload(formData));
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

const uploadAdminPartnerPhoto = async (partnerId, file) => {
  const body = new FormData();
  body.append('file', file);
  const response = await apiFetch(`/api/v1/admin/partners/${partnerId}/photos`, { method: 'POST', body });
  await loadAdminPartnerPhotos(partnerId);
  return response;
};

const uploadPartnerPhoto = async (file) => {
  const body = new FormData();
  body.append('file', file);
  const response = await partnerApiFetch('/api/v1/partners/me/photos', { method: 'POST', body });
  await loadPartnerPhotos();
  return response;
};

const buildPartnerPhotoPayload = (formData) => ({
  alt_text: getOptionalText(formData, 'alt_text'),
  sort_order: Number(formData.get('sort_order') || 0),
  is_active: formData.has('is_active'),
});

const submitAdminPartnerPhoto = async (form) => {
  await patchJson(`/api/v1/admin/partner-photos/${form.dataset.photoId}`, buildPartnerPhotoPayload(new FormData(form)));
  await loadAdminPartnerPhotos(adminState.selectedPartnerIdForEdit);
};

const submitPartnerPhoto = async (form) => {
  await partnerPatchJson(`/api/v1/partners/me/photos/${form.dataset.photoId}`, buildPartnerPhotoPayload(new FormData(form)));
  await loadPartnerPhotos();
};

const hideAdminPartnerPhoto = async (photoId) => {
  await patchJson(`/api/v1/admin/partner-photos/${photoId}`, { is_active: false });
  await loadAdminPartnerPhotos(adminState.selectedPartnerIdForEdit);
};

const hidePartnerPhoto = async (photoId) => {
  await partnerPatchJson(`/api/v1/partners/me/photos/${photoId}`, { is_active: false });
  await loadPartnerPhotos();
};

const uploadAdminPartnerImage = async (partnerId, kind, file) => {
  const body = new FormData();
  body.append('file', file);
  const response = await apiFetch(`/api/v1/admin/partners/${partnerId}/images?kind=${kind}`, {
    method: 'POST',
    body,
  });
  await loadPartners();
  const selectedPartner = adminState.partners.find((item) => String(item.id) === String(partnerId));
  if (selectedPartner && response?.url) {
    selectedPartner[`${kind}_url`] = response.url;
  }
  return response;
};

const uploadPartnerProfileImage = async (kind, file) => {
  const body = new FormData();
  body.append('file', file);
  const response = await partnerApiFetch(`/api/v1/partners/me/images?kind=${kind}`, {
    method: 'POST',
    body,
  });
  if (partnerState.profile && response?.url) {
    partnerState.profile[`${kind}_url`] = response.url;
  }
  await loadPartnerProfile();
  return response;
};
const uploadAdminOfferImage = async (offerId, file) => {
  const body = new FormData();
  body.append('file', file);
  const response = await apiFetch(`/api/v1/admin/offers/${offerId}/image`, {
    method: 'POST',
    body,
  });
  if (response?.url) {
    const offer = adminState.offers.find((item) => String(item.id) === String(offerId));
    if (offer) {
      offer.image_url = response.url;
    }
  }
  await loadOffers();
  return response;
};

const uploadPartnerOfferImage = async (offerId, file) => {
  const body = new FormData();
  body.append('file', file);
  const response = await partnerApiFetch(`/api/v1/partners/me/offers/${offerId}/image`, {
    method: 'POST',
    body,
  });
  if (response?.url) {
    const offer = partnerState.offers.find((item) => String(item.id) === String(offerId));
    if (offer) {
      offer.image_url = response.url;
    }
  }
  await loadPartnerOffers();
  return response;
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


const handlePasswordSetupSubmit = async (form) => {
  const message = document.querySelector('[data-password-setup-message]');
  if (message) {
    message.textContent = '';
  }
  const { setupToken, login } = getPasswordSetupParams();
  const formData = new FormData(form);
  const password = String(formData.get('password') || '');
  const passwordConfirm = String(formData.get('password_confirm') || '');

  try {
    const response = await fetch('/api/v1/auth/password-setup/complete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: setupToken,
        password,
        password_confirm: passwordConfirm,
      }),
    });

    if (!response.ok) {
      throw new Error('Password setup failed');
    }

    await response.json();
    form.reset();
    if (message) {
      message.textContent = 'Пароль установлен. Теперь войдите в личный кабинет.';
    }
    const nextUrl = new URL(window.location.href);
    nextUrl.searchParams.delete('setup_token');
    window.history.replaceState({}, '', `${nextUrl.pathname}${nextUrl.search}${nextUrl.hash}`);
    renderPublicApp();
    setLoginMode('client');
    const loginInput = document.querySelector('[data-login-form] input[name="email"]');
    if (loginInput && login) {
      loginInput.value = login;
    }
    setLoginMessage('Пароль установлен. Теперь войдите в личный кабинет.');
  } catch (error) {
    if (message) {
      message.textContent = 'Ссылка недействительна или истекла. Запросите новую ссылку в VK-боте.';
    }
  }
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
  const menuToggle = event.target.closest('[data-landing-menu-toggle]');
  if (menuToggle) {
    const panel = document.querySelector('[data-landing-menu-panel]');
    const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
    menuToggle.setAttribute('aria-expanded', String(!isExpanded));
    if (panel) {
      panel.hidden = isExpanded;
    }
    return;
  }

  const menuLink = event.target.closest('[data-landing-menu-link]');
  if (menuLink) {
    const menuButton = document.querySelector('[data-landing-menu-toggle]');
    const panel = document.querySelector('[data-landing-menu-panel]');
    if (menuButton) {
      menuButton.setAttribute('aria-expanded', 'false');
    }
    if (panel) {
      panel.hidden = true;
    }
    return;
  }

  const directionButton = event.target.closest('[data-landing-category-slug]');
  if (directionButton) {
    await openLandingDirection(directionButton.dataset.landingCategorySlug);
    return;
  }

  if (event.target.closest('[data-landing-partner-close]')) {
    closeLandingPartnerModal();
    return;
  }

  if (event.target.closest('[data-landing-carousel-prev]')) {
    moveLandingPartnerCarousel(-1);
    return;
  }

  if (event.target.closest('[data-landing-carousel-next]')) {
    moveLandingPartnerCarousel(1);
    return;
  }

  if (event.target.closest('[data-landing-modal-cta]')) {
    closeLandingPartnerModal();
    return;
  }

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
    setFormMessage('partnerGallery');
    adminState.selectedPartnerAnalytics = adminState.partnerAnalyticsById[adminState.selectedPartnerIdForEdit] || null;
    adminState.partnerAnalyticsError = '';
    try {
      await Promise.all([
        loadAdminPartnerPhotos(adminState.selectedPartnerIdForEdit),
        loadAdminPartnerAnalytics(adminState.selectedPartnerIdForEdit),
      ]);
    } catch (error) {
      setFormMessage('partnerGallery', error.message || 'Не удалось загрузить галерею.');
    }
    renderAdminLayout();
    return;
  }

  const partnerEditCancel = event.target.closest('[data-admin-partner-edit-cancel]');
  if (partnerEditCancel) {
    adminState.selectedPartnerIdForEdit = '';
    adminState.selectedPartnerAnalytics = null;
    adminState.partnerAnalyticsError = '';
    adminState.partnerAnalyticsLoading = false;
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

  const adminPhotoHide = event.target.closest('[data-admin-photo-hide]');
  if (adminPhotoHide) {
    setFormMessage('partnerGallery');
    try {
      await hideAdminPartnerPhoto(adminPhotoHide.dataset.adminPhotoHide);
      setFormMessage('partnerGallery', 'Фото скрыто.');
      setPanelMessage('Фото скрыто без удаления файла.', 'success');
    } catch (error) {
      setFormMessage('partnerGallery', error.message || 'Не удалось скрыть фото.');
      setPanelMessage(error.message || 'Не удалось скрыть фото.', 'error');
    }
    renderAdminLayout();
    return;
  }

  const partnerPhotoHide = event.target.closest('[data-partner-photo-hide]');
  if (partnerPhotoHide) {
    setPartnerFormMessage('partnerGallery');
    try {
      await hidePartnerPhoto(partnerPhotoHide.dataset.partnerPhotoHide);
      setPartnerFormMessage('partnerGallery', 'Фото скрыто.');
      setPartnerPanelMessage('Фото скрыто без удаления файла.', 'success');
    } catch (error) {
      setPartnerFormMessage('partnerGallery', error.message || 'Не удалось скрыть фото.');
      setPartnerPanelMessage(error.message || 'Не удалось скрыть фото.', 'error');
    }
    renderPartnerLayout();
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

  const partnerOfferEditButton = event.target.closest('[data-partner-offer-edit]');
  if (partnerOfferEditButton) {
    partnerState.selectedOfferIdForEdit = partnerOfferEditButton.dataset.partnerOfferEdit;
    setPartnerFormMessage('offerEdit');
    renderPartnerLayout();
    return;
  }

  const partnerOfferEditCancel = event.target.closest('[data-partner-offer-edit-cancel]');
  if (partnerOfferEditCancel) {
    partnerState.selectedOfferIdForEdit = '';
    setPartnerFormMessage('offerEdit');
    renderPartnerLayout();
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

  const dismissPrivilegeButton = event.target.closest('[data-client-dismiss-privilege]');
  if (dismissPrivilegeButton) {
    clientState.latestVerification = null;
    renderClientLayout();
    return;
  }

  const openPrivilegesButton = event.target.closest('[data-client-open-privileges]');
  if (openPrivilegesButton) {
    clientState.latestVerification = null;
    clientState.activeTab = 'history';
    await loadActiveClientTabData();
    return;
  }

  const loadOffersButton = event.target.closest('[data-client-load-offers]');
  if (loadOffersButton) {
    try {
      await openClientPartnerMarketplace(loadOffersButton.dataset.clientLoadOffers);
      setClientPanelMessage('Партнёр и предложения открыты.', 'success');
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


const handleAdminPartnerPhotoInput = async (input) => {
  const file = input.files?.[0];
  if (!file) return;
  const partnerId = input.dataset.partnerId;
  setFormMessage('partnerGallery');
  try {
    await uploadAdminPartnerPhoto(partnerId, file);
    setFormMessage('partnerGallery', 'Фото добавлено в галерею.');
    setPanelMessage('Фото добавлено в галерею партнёра.', 'success');
  } catch (error) {
    setFormMessage('partnerGallery', error.message || 'Не удалось загрузить фото в галерею.');
    setPanelMessage(error.message || 'Не удалось загрузить фото в галерею.', 'error');
  }
  renderAdminLayout();
};

const handlePartnerPhotoInput = async (input) => {
  const file = input.files?.[0];
  if (!file) return;
  setPartnerFormMessage('partnerGallery');
  try {
    await uploadPartnerPhoto(file);
    setPartnerFormMessage('partnerGallery', 'Фото загружено и отправлено на проверку.');
    setPartnerPanelMessage('Фото загружено и отправлено на проверку.', 'success');
  } catch (error) {
    setPartnerFormMessage('partnerGallery', error.message || 'Не удалось загрузить фото в галерею.');
    setPartnerPanelMessage(error.message || 'Не удалось загрузить фото в галерею.', 'error');
  }
  renderPartnerLayout();
};

const handleAdminGalleryFormSubmit = async (form) => {
  setFormMessage('partnerGallery');
  try {
    await submitAdminPartnerPhoto(form);
    setFormMessage('partnerGallery', 'Фото обновлено.');
    setPanelMessage('Настройки фото сохранены.', 'success');
  } catch (error) {
    setFormMessage('partnerGallery', error.message || 'Не удалось сохранить фото.');
    setPanelMessage(error.message || 'Не удалось сохранить фото.', 'error');
  }
  renderAdminLayout();
};

const handlePartnerGalleryFormSubmit = async (form) => {
  setPartnerFormMessage('partnerGallery');
  try {
    await submitPartnerPhoto(form);
    setPartnerFormMessage('partnerGallery', 'Фото обновлено.');
    setPartnerPanelMessage('Настройки фото сохранены.', 'success');
  } catch (error) {
    setPartnerFormMessage('partnerGallery', error.message || 'Не удалось сохранить фото.');
    setPartnerPanelMessage(error.message || 'Не удалось сохранить фото.', 'error');
  }
  renderPartnerLayout();
};

const handleAdminPartnerImageInput = async (input) => {
  const file = input.files?.[0];
  if (!file) return;
  const kind = input.dataset.adminPartnerImageUpload;
  const partnerId = input.dataset.partnerId;
  setFormMessage('partnerImage');
  try {
    await uploadAdminPartnerImage(partnerId, kind, file);
    setFormMessage('partnerImage', 'Фото обновлено.');
    setPanelMessage('Фото партнёра обновлено.', 'success');
  } catch (error) {
    setFormMessage('partnerImage', error.message || 'Не удалось загрузить фото.');
    setPanelMessage(error.message || 'Не удалось загрузить фото.', 'error');
  }
  renderAdminLayout();
};

const handlePartnerProfileImageInput = async (input) => {
  const file = input.files?.[0];
  if (!file) return;
  const kind = input.dataset.partnerImageUpload;
  setPartnerFormMessage('profileImages');
  try {
    await uploadPartnerProfileImage(kind, file);
    setPartnerFormMessage('profileImages', 'Фото обновлено.');
    setPartnerPanelMessage('Фото обновлено.', 'success');
  } catch (error) {
    setPartnerFormMessage('profileImages', error.message || 'Не удалось загрузить фото.');
    setPartnerPanelMessage(error.message || 'Не удалось загрузить фото.', 'error');
  }
  renderPartnerLayout();
};

const handleAdminOfferImageInput = async (input) => {
  const file = input.files?.[0];
  if (!file) return;
  const offerId = input.dataset.offerId;
  setFormMessage('offerImage');
  try {
    await uploadAdminOfferImage(offerId, file);
    setFormMessage('offerImage', 'Фото предложения обновлено.');
    setPanelMessage('Фото предложения обновлено.', 'success');
  } catch (error) {
    setFormMessage('offerImage', error.message || 'Не удалось загрузить фото предложения.');
    setPanelMessage(error.message || 'Не удалось загрузить фото предложения.', 'error');
  }
  renderAdminLayout();
};

const handlePartnerOfferImageInput = async (input) => {
  const file = input.files?.[0];
  if (!file) return;
  const offerId = input.dataset.offerId;
  setPartnerFormMessage('offerImage');
  try {
    await uploadPartnerOfferImage(offerId, file);
    setPartnerFormMessage('offerImage', 'Фото предложения обновлено.');
    setPartnerPanelMessage('Фото предложения обновлено.', 'success');
  } catch (error) {
    setPartnerFormMessage('offerImage', error.message || 'Не удалось загрузить фото предложения.');
    setPartnerPanelMessage(error.message || 'Не удалось загрузить фото предложения.', 'error');
  }
  renderPartnerLayout();
};

root.addEventListener('change', (event) => {
  const adminPhotoInput = event.target.closest('[data-admin-partner-photo-upload]');
  if (adminPhotoInput) {
    handleAdminPartnerPhotoInput(adminPhotoInput);
    return;
  }

  const partnerPhotoInput = event.target.closest('[data-partner-photo-upload]');
  if (partnerPhotoInput) {
    handlePartnerPhotoInput(partnerPhotoInput);
    return;
  }

  const adminImageInput = event.target.closest('[data-admin-partner-image-upload]');
  if (adminImageInput) {
    handleAdminPartnerImageInput(adminImageInput);
    return;
  }

  const partnerImageInput = event.target.closest('[data-partner-image-upload]');
  if (partnerImageInput) {
    handlePartnerProfileImageInput(partnerImageInput);
    return;
  }

  const adminOfferImageInput = event.target.closest('[data-admin-offer-image-upload]');
  if (adminOfferImageInput) {
    handleAdminOfferImageInput(adminOfferImageInput);
    return;
  }

  const partnerOfferImageInput = event.target.closest('[data-partner-offer-image-upload]');
  if (partnerOfferImageInput) {
    handlePartnerOfferImageInput(partnerOfferImageInput);
    return;
  }

  const activityEventSelect = event.target.closest('[data-admin-activity-event-type]');
  if (activityEventSelect) {
    adminState.activityEventType = activityEventSelect.value;
    loadActiveTabData();
    return;
  }

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
  const passwordSetup = event.target.closest('[data-password-setup-form]');
  if (passwordSetup) {
    event.preventDefault();
    handlePasswordSetupSubmit(passwordSetup);
    return;
  }

  const login = event.target.closest('[data-login-form]');
  if (login) {
    event.preventDefault();
    handleLoginSubmit(login);
    return;
  }

  const adminGalleryForm = event.target.closest('[data-admin-gallery-form]');
  if (adminGalleryForm) {
    event.preventDefault();
    handleAdminGalleryFormSubmit(adminGalleryForm);
    return;
  }

  const partnerGalleryForm = event.target.closest('[data-partner-gallery-form]');
  if (partnerGalleryForm) {
    event.preventDefault();
    handlePartnerGalleryFormSubmit(partnerGalleryForm);
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

if (getPasswordSetupParams().setupToken) {
  renderPasswordSetupApp();
} else {
  restoreAdminSession();
}
