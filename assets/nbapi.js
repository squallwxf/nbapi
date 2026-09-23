    const storageKeys = {
      theme: "nbapi-theme",
      prices: "nbapi-prices"
    };

    const themeToggle = document.getElementById("themeToggle");
    const adminState = document.getElementById("adminState");
    const authLogin = document.getElementById("authLogin");
    const authSignup = document.getElementById("authSignup");
    const authUser = document.getElementById("authUser");
    const authLogout = document.getElementById("authLogout");
    const priceCells = Array.from(document.querySelectorAll("[data-price-id]"));
    const modelGrid = document.getElementById("modelGrid");
    const modelSearch = document.getElementById("modelSearch");
    const copyVisibleModels = document.getElementById("copyVisibleModels");
    const plazaPriceToggle = document.getElementById("plazaPriceToggle");
    const plazaModeToggle = document.getElementById("plazaModeToggle");
    const copyToast = document.getElementById("copyToast");
    const balanceDisplay = document.getElementById("balanceDisplay");
    const balancePill = document.getElementById("balancePill");
    const topupAmount = document.getElementById("topupAmount");
    const topupPaymentMethod = document.getElementById("topupPaymentMethod");
    const submitTopup = document.getElementById("submitTopup");
    const walletStatus = document.getElementById("walletStatus");
    const walletOrders = document.getElementById("walletOrders");
    const consumptionPeriod = document.getElementById("consumptionPeriod");
    const queryConsumption = document.getElementById("queryConsumption");
    const consumptionSummary = document.getElementById("consumptionSummary");
    const walletModelChart = document.getElementById("walletModelChart");
    const docsModelList = document.getElementById("docsModelList");
    const dashboardModels = document.getElementById("dashboardModels");
    const dashboardTodayRequests = document.getElementById("dashboardTodayRequests");
    const dashboardChannels = document.getElementById("dashboardChannels");
    const dashboardMonthAmount = document.getElementById("dashboardMonthAmount");
    const dashboardLatency = document.getElementById("dashboardLatency");
    const dashboardBalance = document.getElementById("dashboardBalance");
    const consoleModels = document.getElementById("consoleModels");
    const consoleChannels = document.getElementById("consoleChannels");
    const consoleTodayRequests = document.getElementById("consoleTodayRequests");
    const consoleBalance = document.getElementById("consoleBalance");
    const createToken = document.getElementById("createToken");
    const tokenModal = document.getElementById("tokenModal");
    const closeTokenModal = document.getElementById("closeTokenModal");
    const cancelTokenModal = document.getElementById("cancelTokenModal");
    const submitTokenModal = document.getElementById("submitTokenModal");
    const tokenNameInput = document.getElementById("tokenNameInput");
    const tokenGroupInput = document.getElementById("tokenGroupInput");
    const tokenCountInput = document.getElementById("tokenCountInput");
    const tokenExpiryInput = document.getElementById("tokenExpiryInput");
    const tokenQuotaInput = document.getElementById("tokenQuotaInput");
    const tokenUnlimitedInput = document.getElementById("tokenUnlimitedInput");
    const tokenModelsInput = document.getElementById("tokenModelsInput");
    const tokenIpInput = document.getElementById("tokenIpInput");
    const modelPricingModal = document.getElementById("modelPricingModal");
    const closeModelPricingModalButton = document.getElementById("closeModelPricingModal");
    const modelPricingModalTitle = document.getElementById("modelPricingModalTitle");
    const modelPricingModalSubtitle = document.getElementById("modelPricingModalSubtitle");
    const modelPricingModalBody = document.getElementById("modelPricingModalBody");
    const copySelectedTokens = document.getElementById("copySelectedTokens");
    const enableSelectedTokens = document.getElementById("enableSelectedTokens");
    const disableSelectedTokens = document.getElementById("disableSelectedTokens");
    const deleteSelectedTokens = document.getElementById("deleteSelectedTokens");
    const tokenSelectionInfo = document.getElementById("tokenSelectionInfo");
    const tokenList = document.getElementById("tokenList");
    const tokenAuthHint = document.getElementById("tokenAuthHint");
    const playgroundToken = document.getElementById("playgroundToken");
    const playgroundModel = document.getElementById("playgroundModel");
    const playgroundTemperature = document.getElementById("playgroundTemperature");
    const playgroundTopP = document.getElementById("playgroundTopP");
    const playgroundFrequencyPenalty = document.getElementById("playgroundFrequencyPenalty");
    const playgroundPresencePenalty = document.getElementById("playgroundPresencePenalty");
    const playgroundMaxTokens = document.getElementById("playgroundMaxTokens");
    const playgroundImageOptions = document.getElementById("playgroundImageOptions");
    const playgroundImageSizeControl = document.getElementById("playgroundImageSizeControl");
    const playgroundImageAspect = document.getElementById("playgroundImageAspect");
    const playgroundImageSize = document.getElementById("playgroundImageSize");
    const playgroundVideoOptions = document.getElementById("playgroundVideoOptions");
    const playgroundVideoResolution = document.getElementById("playgroundVideoResolution");
    const playgroundVideoRatioControl = document.getElementById("playgroundVideoRatioControl");
    const playgroundVideoRatio = document.getElementById("playgroundVideoRatio");
    const playgroundVideoDurationControl = document.getElementById("playgroundVideoDurationControl");
    const playgroundVideoDuration = document.getElementById("playgroundVideoDuration");
    const playgroundPrompt = document.getElementById("playgroundPrompt");
    const playgroundMessages = document.getElementById("playgroundMessages");
    const playgroundStatus = document.getElementById("playgroundStatus");
    const sendPlayground = document.getElementById("sendPlayground");
    const clearPlayground = document.getElementById("clearPlayground");
    const loginUsername = document.getElementById("loginUsername");
    const loginPassword = document.getElementById("loginPassword");
    const loginSubmit = document.getElementById("loginSubmit");
    const resetEmail = document.getElementById("resetEmail");
    const requestReset = document.getElementById("requestReset");
    const resetRequestStatus = document.getElementById("resetRequestStatus");
    const newResetPassword = document.getElementById("newResetPassword");
    const confirmResetPassword = document.getElementById("confirmResetPassword");
    const confirmReset = document.getElementById("confirmReset");
    const resetConfirmStatus = document.getElementById("resetConfirmStatus");
    const signupSubmit = document.getElementById("signupSubmit");
    const signupUsername = document.getElementById("signupUsername");
    const signupEmail = document.getElementById("signupEmail");
    const signupPassword = document.getElementById("signupPassword");
    const signupConfirm = document.getElementById("signupConfirm");
    const signupDesignatedAdminEnabled = document.getElementById("signupDesignatedAdminEnabled");
    const signupDesignatedAdmin = document.getElementById("signupDesignatedAdmin");
    const resetPlazaFilters = document.getElementById("resetPlazaFilters");
    const upstreamBaseUrl = document.getElementById("upstreamBaseUrl");
    const upstreamApiKey = document.getElementById("upstreamApiKey");
    const saveUpstreamApiKey = document.getElementById("saveUpstreamApiKey");
    const clearUpstreamApiKey = document.getElementById("clearUpstreamApiKey");
    const upstreamConfigStatus = document.getElementById("upstreamConfigStatus");
    const refreshUsers = document.getElementById("refreshUsers");
    const newUserName = document.getElementById("newUserName");
    const newUserPassword = document.getElementById("newUserPassword");
    const generateUserCredentials = document.getElementById("generateUserCredentials");
    const createManagedUser = document.getElementById("createManagedUser");
    const customerAssignmentPanel = document.getElementById("customerAssignmentPanel");
    const customerManagerSelect = document.getElementById("customerManagerSelect");
    const refreshManagerCustomers = document.getElementById("refreshManagerCustomers");
    const managerCustomerSummary = document.getElementById("managerCustomerSummary");
    const managerCustomerList = document.getElementById("managerCustomerList");
    const refreshPricing = document.getElementById("refreshPricing");
    const pricingList = document.getElementById("pricingList");
    const refreshChannels = document.getElementById("refreshChannels");
    const userManagementList = document.getElementById("userManagementList");
    const userSearch = document.getElementById("userSearch");
    const clearUserSearch = document.getElementById("clearUserSearch");
    const prevUsersPage = document.getElementById("prevUsersPage");
    const nextUsersPage = document.getElementById("nextUsersPage");
    const usersPageInfo = document.getElementById("usersPageInfo");
    const channelList = document.getElementById("channelList");
    const createChannelButton = document.getElementById("createChannel");
    const newChannelName = document.getElementById("newChannelName");
    const newChannelUrl = document.getElementById("newChannelUrl");
    const newChannelKey = document.getElementById("newChannelKey");
    const newChannelPriority = document.getElementById("newChannelPriority");
    const newChannelNote = document.getElementById("newChannelNote");
    const newChannelModels = document.getElementById("newChannelModels");
    const refreshUsageLogs = document.getElementById("refreshUsageLogs");
    const queryUsageLogs = document.getElementById("queryUsageLogs");
    const resetUsageLogs = document.getElementById("resetUsageLogs");
    const usageLogBody = document.getElementById("usageLogBody");
    const usagePageInfo = document.getElementById("usagePageInfo");
    const usagePageSize = document.getElementById("usagePageSize");
    const usagePrevPage = document.getElementById("usagePrevPage");
    const usageNextPage = document.getElementById("usageNextPage");
    const usageAmount = document.getElementById("usageAmount");
    const usageRequests = document.getElementById("usageRequests");
    const usageInputTokens = document.getElementById("usageInputTokens");
    const usageOutputTokens = document.getElementById("usageOutputTokens");
    const logFrom = document.getElementById("logFrom");
    const logTo = document.getElementById("logTo");
    const logToken = document.getElementById("logToken");
    const logModel = document.getElementById("logModel");
    const logRequestId = document.getElementById("logRequestId");
    const logType = document.getElementById("logType");
    const logScope = document.getElementById("logScope");
    const announcementList = document.getElementById("announcementList");
    const announcementSettings = document.getElementById("announcementSettings");
    const announcementEditorList = document.getElementById("announcementEditorList");
    const addAnnouncement = document.getElementById("addAnnouncement");
    const saveAnnouncements = document.getElementById("saveAnnouncements");
    const API_BASE = location.hostname === "127.0.0.1" || location.hostname === "localhost" || location.protocol === "file:" ? "http://127.0.0.1:8765" : "";
    let usageLogsPage = 1;
    let usageLogsTotalPages = 1;
    let sessionToken = localStorage.getItem("nbapi-session-token") || "";
    let currentUser = null;
    let authVersion = 0;
    let canManage = false;
    let isSuperAdmin = false;
    let activeApiKey = localStorage.getItem("nbapi-active-api-key") || "";
    let announcements = [];

    function tokenCacheKey() {
      return currentUser ? `nbapi-token-cache:${currentUser.username}` : "nbapi-token-cache:guest";
    }

    function readTokenCache() {
      try { return JSON.parse(localStorage.getItem(tokenCacheKey()) || "{}"); } catch { return {}; }
    }

    function writeTokenCache(cache) {
      localStorage.setItem(tokenCacheKey(), JSON.stringify(cache));
    }

    async function apiRequest(path, options = {}) {
      const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
      if (sessionToken) headers.Authorization = `Bearer ${sessionToken}`;
      const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || `请求失败（${response.status}）`);
      return data;
    }

    function roleLabel(role) {
      return role === "super_admin" ? "超级管理员" : role === "admin" ? "管理员" : "用户";
    }

    function syncAuthState() {
      canManage = Boolean(currentUser && currentUser.role !== "user");
      isSuperAdmin = Boolean(currentUser && currentUser.role === "super_admin");
      document.body.classList.toggle("logged-in", Boolean(currentUser));
      document.body.classList.toggle("can-manage", canManage);
      document.body.classList.toggle("is-super-admin", isSuperAdmin);
      adminState.textContent = currentUser ? roleLabel(currentUser.role) : "访客";
      authUser.textContent = currentUser ? `${currentUser.username} · ${roleLabel(currentUser.role)}` : "";
      authUser.style.display = currentUser ? "inline-flex" : "none";
      authLogout.style.display = currentUser ? "inline-flex" : "none";
      authLogin.style.display = currentUser ? "none" : "inline-flex";
      authSignup.style.display = currentUser ? "none" : "inline-flex";
      updateBalance();
    }

    function clearSessionState() {
      authVersion += 1;
      sessionToken = "";
      currentUser = null;
      canManage = false;
      isSuperAdmin = false;
      activeApiKey = "";
      resetPlaygroundConversation();
      accountBalance = 0;
      localStorage.removeItem("nbapi-session-token");
      localStorage.removeItem("nbapi-active-api-key");
      localStorage.removeItem("nbapi-balance");
      clearWalletView();
      clearUsageLogView();
    }

    function applyUserSession(user, token) {
      if (!currentUser || currentUser.id !== user.id || sessionToken !== token) {
        authVersion += 1;
        clearWalletView();
        clearUsageLogView();
        [logFrom, logTo, logToken, logModel, logRequestId].forEach((input) => { if (input) input.value = ""; });
        if (logType) logType.value = "";
        if (logScope) logScope.value = "self";
      }
      sessionToken = token;
      currentUser = user;
      localStorage.setItem("nbapi-session-token", token);
      activeApiKey = "";
      localStorage.removeItem("nbapi-active-api-key");
      accountBalance = Number(user.balance || 0);
      updateBalance();
      syncAuthState();
      renderPrices();
    }

    function clearWalletView() {
      if (walletStatus) walletStatus.textContent = "登录后可提交充值申请。";
      if (walletOrders) walletOrders.innerHTML = '<tr><td colspan="6" class="muted">暂无充值记录。</td></tr>';
      if (consumptionSummary) consumptionSummary.textContent = "选择统计周期后查询消费总额。";
      if (walletModelChart) walletModelChart.innerHTML = '<div class="wallet-chart-empty">查询后显示各模型消费金额。</div>';
    }

    function clearUsageLogView() {
      usageLogsPage = 1;
      usageLogsTotalPages = 1;
      if (usageAmount) usageAmount.textContent = "$0.000000";
      if (usageRequests) usageRequests.textContent = "0";
      if (usageInputTokens) usageInputTokens.textContent = "0";
      if (usageOutputTokens) usageOutputTokens.textContent = "0";
      if (usagePageInfo) usagePageInfo.textContent = "共 0 条";
      if (usageLogBody) usageLogBody.innerHTML = '<tr><td colspan="11" class="muted">登录后加载真实日志。</td></tr>';
    }

    async function performUserLogin(username, password, source = "登录") {
      const data = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      }).then(async (response) => {
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || "登录失败");
        return result;
      });
      applyUserSession(data.user, data.token);
      await loadManagerAccounts();
      await Promise.all([loadTokens(), loadAdminUsers(), loadModelCatalog(), loadWallet(), loadAnnouncements()]);
      location.hash = "console";
      applyRoute();
      showToast(`${source}成功`);
      return data;
    }

    async function loadCurrentSession() {
      if (!sessionToken) {
        syncAuthState();
        return;
      }
      try {
        const me = await apiRequest("/api/me");
        applyUserSession(me, sessionToken);
        await loadManagerAccounts();
        await Promise.all([loadTokens(), loadAdminUsers(), loadModelCatalog(), loadWallet(), loadAnnouncements()]);
      } catch {
        clearSessionState();
        syncAuthState();
        setUpstreamUiState();
        loadTokens();
      }
    }

    function formatTokenDate(timestamp) {
      return timestamp ? new Date(timestamp * 1000).toLocaleString("zh-CN", { hour12: false }) : "从未使用";
    }

    function usageLogQuery() {
      const values = { scope: isSuperAdmin ? logScope.value : "self", from: logFrom.value, to: logTo.value, token: logToken.value, model: logModel.value, requestId: logRequestId.value, type: logType.value, page: usageLogsPage, pageSize: usagePageSize.value };
      return Object.entries(values).filter(([, value]) => value !== "" && value != null).map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`).join("&");
    }

    async function loadDashboard() {
      try {
        const data = await apiRequest("/api/dashboard");
        const money = (value) => `$${Number(value || 0).toFixed(6)}`;
        const requests = Number(data.todayRequests || 0).toLocaleString();
        dashboardModels.textContent = Number(data.models || 0).toLocaleString();
        dashboardTodayRequests.textContent = requests;
        dashboardChannels.textContent = Number(data.channels || 0).toLocaleString();
        dashboardMonthAmount.textContent = money(data.monthAmount);
        dashboardLatency.textContent = data.avgLatencyMs ? `平均响应 ${data.avgLatencyMs}ms` : (currentUser ? "暂无调用记录" : "登录后显示真实调用");
        dashboardBalance.textContent = currentUser ? `账户余额：${money(data.balance)}` : "登录后显示账户余额";
        consoleModels.textContent = dashboardModels.textContent;
        consoleChannels.textContent = dashboardChannels.textContent;
        consoleTodayRequests.textContent = requests;
        consoleBalance.textContent = currentUser ? money(data.balance) : "-";
      } catch (error) {
        dashboardModels.textContent = "-";
        dashboardTodayRequests.textContent = "-";
        dashboardChannels.textContent = "-";
        dashboardMonthAmount.textContent = "-";
        dashboardBalance.textContent = "统计加载失败";
      }
    }

    async function loadWallet() {
      if (!currentUser || !sessionToken) { clearWalletView(); return; }
      const requestVersion = authVersion;
      const requestToken = sessionToken;
      const requestUserId = currentUser.id;
      try {
        const data = await apiRequest(`/api/wallet?period=${encodeURIComponent(consumptionPeriod.value)}`);
        if (requestVersion !== authVersion || requestToken !== sessionToken || requestUserId !== currentUser?.id) return;
        walletStatus.textContent = `当前余额：$${Number(data.balance || 0).toFixed(6)}。支付成功后余额会自动到账。`;
        const consumptionAmount = Number(data.consumption?.amount || 0);
        const consumptionRequests = Number(data.consumption?.requests || 0);
        consumptionSummary.innerHTML = `${data.consumption?.label || "所选周期"}消费总额：<strong>$${consumptionAmount.toFixed(6)}</strong>，共 ${consumptionRequests.toLocaleString()} 次已扣费调用。`;
        const models = data.consumption?.models || [];
        const maxModelAmount = Math.max(...models.map((item) => Number(item.amount || 0)), 0);
        walletModelChart.innerHTML = models.length ? models.map((item) => {
          const amount = Number(item.amount || 0);
          const width = maxModelAmount > 0 ? Math.max(2, amount / maxModelAmount * 100) : 2;
          return `<div class="wallet-model-row"><div class="wallet-model-name">${escapeHtml(item.model || "未知模型")}</div><div class="wallet-model-track" title="${amount.toFixed(6)}"><div class="wallet-model-bar" style="width:${width.toFixed(2)}%"></div></div><div class="wallet-model-value">$${amount.toFixed(6)} · ${Number(item.requests || 0).toLocaleString()} 次</div></div>`;
        }).join("") : '<div class="wallet-chart-empty">该统计周期暂无模型消费记录。</div>';
        walletOrders.innerHTML = data.orders?.length ? data.orders.map((item) => {
          const canSync = item.status === "pending" && item.paymentProvider === "zpay";
          return `<tr><td><code>${escapeHtml(item.merchantOrderNo || `#${item.id}`)}</code></td><td>¥${Number(item.amount).toFixed(2)}</td><td>${item.paymentMethod === "wxpay" ? "微信支付" : "支付宝"}</td><td>${item.status === "paid" ? "已到账" : item.status === "rejected" ? "已拒绝" : "待支付"}</td><td>${formatTokenDate(item.createdAt)}</td><td>${canSync ? `<button class="btn" type="button" onclick="syncWalletOrder(${Number(item.id)})">查询支付结果</button>` : "-"}</td></tr>`;
        }).join("") : '<tr><td colspan="6" class="muted">暂无充值记录。</td></tr>';
      } catch (error) {
        if (requestVersion === authVersion && requestToken === sessionToken && requestUserId === currentUser?.id) walletStatus.textContent = `加载失败：${error.message}`;
      }
    }

    async function syncWalletOrder(orderId) {
      try {
        walletStatus.textContent = "正在向支付平台查询订单状态...";
        const result = await apiRequest(`/api/wallet/orders/${orderId}/sync`, { method: "POST", body: "{}" });
        await Promise.all([loadWallet(), loadDashboard(), loadCurrentSession()]);
        showToast(result.status === "paid" ? "充值已到账" : "暂未收到支付结果");
      } catch (error) {
        walletStatus.textContent = `查询失败：${error.message}`;
      }
    }

    function renderUsageLogs(data) {
      const stats = data.stats || {};
      usageAmount.textContent = `$${Number(stats.amount || 0).toFixed(6)}`;
      usageRequests.textContent = Number(stats.requests || 0).toLocaleString();
      usageInputTokens.textContent = Number(stats.inputTokens || 0).toLocaleString();
      usageOutputTokens.textContent = Number(stats.outputTokens || 0).toLocaleString();
      usageLogsTotalPages = Number(data.totalPages || 1);
      usagePageInfo.textContent = data.total ? `显示第 ${(data.page - 1) * data.pageSize + 1} 条到第 ${Math.min(data.page * data.pageSize, data.total)} 条，共 ${data.total} 条` : "共 0 条";
      usagePrevPage.disabled = usageLogsPage <= 1;
      usageNextPage.disabled = usageLogsPage >= usageLogsTotalPages;
      if (!data.items?.length) { usageLogBody.innerHTML = '<tr><td colspan="11" class="muted">当前筛选条件下没有真实调用记录。</td></tr>'; return; }
      usageLogBody.innerHTML = data.items.map((item) => `<tr>
        <td>${escapeHtml(formatTokenDate(item.createdAt))}</td><td><strong>${escapeHtml(item.userName || "-")}</strong></td><td><strong>${escapeHtml(item.tokenName)}</strong><br><code>${escapeHtml(item.tokenHint || "-")}</code></td>
        <td>${item.billingUnit === "per_token" ? "按 Token" : "按次"}</td><td><code>${escapeHtml(item.model)}</code></td><td>${renderTimingBadges(item)}</td>
        <td>${Number(item.inputTokens || 0).toLocaleString()}</td><td>${Number(item.outputTokens || 0).toLocaleString()}</td><td><strong>$${Number(item.amount || 0).toFixed(6)}</strong></td><td>${escapeHtml(item.ip || "-")}</td>
        <td><button class="btn" type="button" data-log-detail="${item.id}">查看</button><div class="usage-detail" id="log-detail-${item.id}" hidden>${escapeHtml(item.path || "-")}<br>Request ID: ${escapeHtml(item.requestId || "-")}<br>状态：${escapeHtml(item.status || "-")}<br>计费来源：${escapeHtml(item.usageSource || "-")}<br>预扣：$${Number(item.reserved || 0).toFixed(6)}<br>结算差额：$${Number(item.adjustment || 0).toFixed(6)}<br>缓存读：${Number(item.cacheReadTokens || 0).toLocaleString()} · 缓存写：${Number(item.cacheWriteTokens || 0).toLocaleString()}</div></td></tr>`).join("");
      usageLogBody.querySelectorAll("[data-log-detail]").forEach((button) => button.addEventListener("click", () => { const detail = document.getElementById(`log-detail-${button.dataset.logDetail}`); detail.hidden = !detail.hidden; button.textContent = detail.hidden ? "查看" : "收起"; }));
    }

    async function loadUsageLogs() {
      if (!sessionToken || !currentUser) { clearUsageLogView(); return; }
      const requestVersion = authVersion;
      const requestToken = sessionToken;
      const requestUserId = currentUser.id;
      usageLogBody.innerHTML = '<tr><td colspan="11" class="muted">正在加载真实账单记录...</td></tr>';
      try {
        const data = await apiRequest(`/api/ledger?${usageLogQuery()}`);
        if (requestVersion !== authVersion || requestToken !== sessionToken || requestUserId !== currentUser?.id) return;
        usageLogsPage = Number(data.page || 1);
        renderUsageLogs(data);
      } catch (error) {
        if (requestVersion === authVersion && requestToken === sessionToken && requestUserId === currentUser?.id) usageLogBody.innerHTML = `<tr><td colspan="11" class="muted">加载失败：${escapeHtml(error.message)}</td></tr>`;
      }
    }

    function resetLogFilters() { [logFrom, logTo, logToken, logModel, logRequestId].forEach((input) => { input.value = ""; }); logType.value = ""; logScope.value = "self"; usageLogsPage = 1; loadUsageLogs(); }

    function formatDurationSeconds(milliseconds) {
      const value = Number(milliseconds || 0);
      return value > 0 ? `${(value / 1000).toFixed(3)} 秒` : "-";
    }

    function renderTimingBadges(item) {
      const first = Number(item.firstTokenMs || 0);
      const total = Number(item.latencyMs || 0);
      const seconds = (ms) => Number.isFinite(ms) && ms > 0 ? `${Number((ms / 1000).toFixed(1))} s` : "-";
      const firstColor = first <= 0 ? "muted" : first < 3000 ? "green" : first < 10000 ? "amber" : "red";
      return `<div class="usage-timing"><span class="timing-badge timing-green" tabindex="0" title="总用时：${formatDurationSeconds(total)}">${seconds(total)}</span><span class="timing-badge timing-${firstColor}" tabindex="0" title="首个上游流式响应：${formatDurationSeconds(first)}">${seconds(first)}</span>${first > 0 ? '<span class="timing-badge timing-blue" title="流式响应">流</span>' : ''}</div>`;
    }

    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
    }

    function renderAnnouncements() {
      const activeItems = announcements.filter((item) => item.active);
      announcementList.innerHTML = activeItems.length ? activeItems.map((item) => `<div class="row"><div><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.detail)}</small></div><span class="tag ${escapeHtml(item.tone)}">${escapeHtml(item.badge)}</span></div>`).join("") : '<div class="row"><small>暂无公告。</small></div>';
    }

    function renderAnnouncementEditor() {
      if (!announcementEditorList || !isSuperAdmin) return;
      announcementEditorList.innerHTML = announcements.map((item, index) => `<div class="management-card" data-announcement-index="${index}">
        <div class="management-fields">
          <div class="auth-field"><label>标题</label><input class="auth-input" data-announcement-title value="${escapeHtml(item.title)}" maxlength="80" /></div>
          <div class="auth-field"><label>状态标签</label><input class="auth-input" data-announcement-badge value="${escapeHtml(item.badge)}" maxlength="20" /></div>
          <div class="auth-field"><label>标签颜色</label><select class="auth-input" data-announcement-tone><option value="green" ${item.tone === "green" ? "selected" : ""}>绿色</option><option value="blue" ${item.tone === "blue" ? "selected" : ""}>蓝色</option><option value="orange" ${item.tone === "orange" ? "selected" : ""}>橙色</option><option value="gray" ${item.tone === "gray" ? "selected" : ""}>灰色</option></select></div>
          <div class="auth-field" style="align-content:end;"><label><input type="checkbox" data-announcement-active ${item.active ? "checked" : ""} /> 启用展示</label></div>
        </div>
        <div class="auth-field"><label>公告内容</label><textarea class="auth-input" data-announcement-detail rows="2" maxlength="240">${escapeHtml(item.detail)}</textarea></div>
        <div class="auth-actions"><button class="btn" type="button" data-remove-announcement>删除此公告</button></div>
      </div>`).join("") || '<small>暂无公告，点击“新增公告”创建。</small>';
      announcementEditorList.querySelectorAll("[data-remove-announcement]").forEach((button) => button.addEventListener("click", () => {
        const card = button.closest("[data-announcement-index]");
        announcements.splice(Number(card.dataset.announcementIndex), 1);
        renderAnnouncementEditor();
      }));
    }

    async function loadAnnouncements() {
      try {
        const data = await apiRequest("/api/announcements");
        announcements = Array.isArray(data.items) ? data.items : [];
        renderAnnouncements();
      } catch {
        renderAnnouncements();
      }
      if (isSuperAdmin && sessionToken) {
        try {
          const data = await apiRequest("/api/admin/announcements");
          announcements = Array.isArray(data.items) ? data.items : announcements;
          renderAnnouncementEditor();
          renderAnnouncements();
        } catch (error) {
          if (announcementEditorList) announcementEditorList.innerHTML = `<small>${escapeHtml(error.message)}</small>`;
        }
      }
    }

    async function loadTokens() {
      if (!sessionToken) {
        tokenAuthHint.textContent = "新用户默认没有令牌，请先登录后手动添加。";
        tokenList.innerHTML = "<small>当前未登录</small>";
        return;
      }
      try {
        const data = await apiRequest("/api/tokens");
        const cachedTokens = readTokenCache();
        data.items.forEach((item) => { if (item.id && item.token) cachedTokens[item.id] = item.token; });
        writeTokenCache(cachedTokens);
        const fullTokenFor = (item) => item.token || cachedTokens[item.id] || "";
        const playgroundTokenOptions = data.items.filter((item) => item.active && fullTokenFor(item)).map((item) => `<option value="${escapeHtml(fullTokenFor(item))}">${escapeHtml(item.name)} · ${escapeHtml(item.hint)}</option>`);
        playgroundToken.innerHTML = playgroundTokenOptions.length ? playgroundTokenOptions.join("") : "<option value=\"\">暂无可用完整 Key，请创建或重置令牌</option>";
        tokenAuthHint.textContent = currentUser ? `${currentUser.username} 的令牌。已保存完整值的 Key 可随时复制，代码更新不会使 Key 失效。` : "令牌已安全存储在服务端。";
        tokenList.innerHTML = data.items.length ? `
          <table class="token-table">
            <thead><tr><th><input type="checkbox" id="selectAllTokens" aria-label="全选令牌" /></th><th>名称</th><th>状态</th><th>剩余额度/总额度</th><th>分组</th><th>密钥</th><th>可用模型</th><th>IP 限制</th><th>创建时间</th><th>最后使用时间</th><th>过期时间</th><th>操作</th></tr></thead>
            <tbody>${data.items.map((item) => `
              <tr>
                <td><input type="checkbox" class="token-select" data-token-id="${item.id}" aria-label="选择 ${escapeHtml(item.name)}" /></td>
                <td class="token-name">${escapeHtml(item.name)}</td>
                <td><span class="tag ${item.active ? "green" : "gray"}">${item.active ? "已启用" : "已禁用"}</span></td>
                <td>${item.unlimitedQuota ? "无限额度" : ("$" + Math.max(0, Number(item.quota || 0) - Number(item.usedQuota || 0)).toFixed(6) + " / $" + item.quota)}</td>
                <td>${escapeHtml(item.group || "default")}</td>
                <td><code>${escapeHtml(item.hint)}</code></td>
                <td class="wrap" title="${escapeHtml(item.allowedModels?.length ? item.allowedModels.join(", ") : "全部模型")}">${escapeHtml(item.allowedModels?.length ? item.allowedModels.join(", ") : "全部模型")}</td>
                <td class="wrap" title="${escapeHtml(item.ipAllowlist?.length ? item.ipAllowlist.join(", ") : "不限制")}">${escapeHtml(item.ipAllowlist?.length ? item.ipAllowlist.join(", ") : "不限制")}</td>
                <td>${formatTokenDate(item.createdAt)}</td>
                <td>${formatTokenDate(item.lastUsedAt)}</td>
                <td>${item.expiresAt ? formatTokenDate(item.expiresAt) : "永不过期"}</td>
                <td><div class="token-actions">${fullTokenFor(item) ? `<button class="btn" type="button" data-copy-token-id="${item.id}">复制 Key</button>` : `<button class="btn" type="button" disabled title="旧版本没有保存完整 Key，但已保存过的原 Key 仍可继续使用">仅脱敏显示</button>`}${item.active ? `<button class="btn" type="button" data-disable-token="${item.id}">禁用</button>` : `<button class="btn" type="button" data-enable-token="${item.id}">启用</button>`}<button class="btn" type="button" data-delete-token="${item.id}">删除</button></div></td>
              </tr>`).join("")}</tbody>
          </table>` : "<small>暂无令牌，请点击“添加令牌”。</small>";
        tokenList.querySelectorAll("[data-copy-token-id]").forEach((button) => button.addEventListener("click", () => copyFullToken(cachedTokens[button.dataset.copyTokenId])));
        tokenList.querySelectorAll("[data-disable-token]").forEach((button) => button.addEventListener("click", () => disableToken(button.dataset.disableToken)));
        tokenList.querySelectorAll("[data-enable-token]").forEach((button) => button.addEventListener("click", () => setTokenActive(button.dataset.enableToken, true)));
        tokenList.querySelectorAll("[data-delete-token]").forEach((button) => button.addEventListener("click", () => deleteToken(button.dataset.deleteToken)));
        const selectAll = document.getElementById("selectAllTokens");
        const selections = Array.from(tokenList.querySelectorAll(".token-select"));
        const updateSelection = () => {
          const selectedCount = selections.filter((checkbox) => checkbox.checked).length;
          tokenSelectionInfo.textContent = `已选择 ${selectedCount} 个`;
          if (selectAll) selectAll.checked = selections.length > 0 && selectedCount === selections.length;
        };
        selections.forEach((checkbox) => checkbox.addEventListener("change", updateSelection));
        selectAll?.addEventListener("change", () => { selections.forEach((checkbox) => { checkbox.checked = selectAll.checked; }); updateSelection(); });
        updateSelection();
      } catch (error) {
        tokenList.innerHTML = `<small>${error.message}</small>`;
      }
    }

    function setUpstreamUiState(config = null) {
      if (!upstreamBaseUrl || !upstreamApiKey || !upstreamConfigStatus) return;
      const adminMode = Boolean(canManage && sessionToken);
      upstreamBaseUrl.value = config?.upstreamBaseUrl || "https://nbapi.win/v1";
      upstreamApiKey.disabled = !adminMode;
      saveUpstreamApiKey.disabled = !adminMode;
      clearUpstreamApiKey.disabled = !adminMode;
      if (!adminMode) {
        upstreamApiKey.value = "";
        upstreamConfigStatus.textContent = "管理员登录后可查看和修改上游 API Key。";
        return;
      }
      upstreamApiKey.value = "";
      const routeHint = config?.activeChannelName ? `当前路由：${config.activeChannelName}。` : "";
      upstreamConfigStatus.textContent = config?.upstreamApiKeySet
        ? `${routeHint} 已保存上游 Key，当前脱敏显示为 ${config.upstreamApiKeyHint || "******"}.`
        : `${routeHint} 当前尚未保存上游 API Key。`;
    }

    function selectedTokenIds() {
      return Array.from(tokenList.querySelectorAll(".token-select:checked")).map((checkbox) => Number(checkbox.dataset.tokenId)).filter(Boolean);
    }

    copySelectedTokens.addEventListener("click", async () => {
      const ids = selectedTokenIds();
      const cache = readTokenCache();
      const keys = ids.map((id) => cache[id]).filter(Boolean);
      if (!ids.length) { alert("请先选择令牌。"); return; }
      if (!keys.length) { alert("所选令牌没有可复制的完整 Key。旧版本创建的 Key 如果后端未保存完整值，仍可继续使用，但无法从脱敏值恢复。"); return; }
      await copyModelName(keys.join("\n"));
      showToast(`已复制 ${keys.length} 个 Key`);
    });

    disableSelectedTokens.addEventListener("click", async () => {
      const ids = selectedTokenIds();
      if (!ids.length) { alert("请先选择令牌。"); return; }
      if (!confirm(`确定禁用选中的 ${ids.length} 个令牌吗？`)) return;
      try {
        await apiRequest("/api/tokens/bulk", { method: "POST", body: JSON.stringify({ action: "disable", ids }) });
        await loadTokens();
        showToast(`已禁用 ${ids.length} 个令牌`);
      } catch (error) { alert(error.message); }
    });

    async function bulkTokenAction(action, label, confirmText) {
      const ids = selectedTokenIds();
      if (!ids.length) { alert("请先选择令牌。"); return; }
      if (confirmText && !confirm(`${confirmText}选中的 ${ids.length} 个令牌吗？`)) return;
      try {
        await apiRequest("/api/tokens/bulk", { method: "POST", body: JSON.stringify({ action, ids }) });
        await loadTokens();
        showToast(`${label} ${ids.length} 个令牌`);
      } catch (error) { alert(error.message); }
    }

    enableSelectedTokens.addEventListener("click", () => bulkTokenAction("enable", "已启用", "确定启用"));
    deleteSelectedTokens.addEventListener("click", () => bulkTokenAction("delete", "已删除", "确定永久删除"));

    async function loadUpstreamConfig() {
      if (!canManage || !sessionToken) {
        setUpstreamUiState();
        return;
      }
      try {
        const config = await apiRequest("/api/admin/config");
        setUpstreamUiState(config);
      } catch (error) {
        upstreamConfigStatus.textContent = error.message;
      }
    }

    async function saveUpstreamKey(value) {
      if (!canManage || !sessionToken) {
        alert("请先登录管理员账号。");
        return;
      }
      try {
        const config = await apiRequest("/api/admin/config", {
          method: "PUT",
          body: JSON.stringify({ upstreamApiKey: value })
        });
        setUpstreamUiState(config);
        showToast(config.upstreamApiKeySet ? "上游 Key 已保存" : "上游 Key 已清空");
      } catch (error) {
        alert(error.message);
      }
    }

    function generateManagedCredentials() {
      const suffix = crypto.getRandomValues(new Uint32Array(1))[0].toString(36).slice(-6);
      const password = crypto.getRandomValues(new Uint32Array(2)).join("").slice(-10);
      newUserName.value = `user_${suffix}`;
      newUserPassword.value = `Nb${password}a`;
      newUserPassword.type = "text";
      showToast("已生成用户名和登录密码");
    }

    async function createManagedAccount() {
      const username = newUserName.value.trim();
      const password = newUserPassword.value;
      if (!username || !password) {
        alert("请填写用户名和登录密码。");
        return;
      }
      try {
        await apiRequest("/api/admin/users", { method: "POST", body: JSON.stringify({ username, password }) });
        newUserName.value = "";
        newUserPassword.value = "";
        newUserPassword.type = "password";
        showToast("用户已添加");
        usersPage = 1;
        await loadAdminUsers();
      } catch (error) {
        alert(error.message);
      }
    }

    async function loadManagerAccounts() {
      if (!isSuperAdmin || !customerManagerSelect) return;
      const data = await apiRequest("/api/admin/managers");
      const previousManagerId = customerManagerSelect.value;
      managerAccounts = data.items || [];
      customerManagerSelect.innerHTML = managerAccounts.map((manager) => `<option value="${manager.id}">${escapeHtml(manager.username)}（${roleLabel(manager.role)}）</option>`).join("");
      if (managerAccounts.some((manager) => String(manager.id) === previousManagerId)) customerManagerSelect.value = previousManagerId;
      customerAssignmentPanel.style.display = managerAccounts.length ? "block" : "none";
      if (managerAccounts.length) await loadManagerCustomers();
      else if (managerCustomerSummary) managerCustomerSummary.textContent = "暂无可管理的管理员账号。";
    }

    async function loadManagerCustomers() {
      if (!isSuperAdmin || !customerManagerSelect || !managerCustomerList || !customerManagerSelect.value) return;
      try {
        const data = await apiRequest(`/api/admin/manager-customers?managerId=${encodeURIComponent(customerManagerSelect.value)}`);
        const manager = managerAccounts.find((item) => String(item.id) === String(customerManagerSelect.value));
        if (managerCustomerSummary) managerCustomerSummary.textContent = `${manager ? manager.username : "当前管理员"} 名下共有 ${data.items?.length || 0} 个客户。可在下方解除归属，也可在用户列表中转移客户。`;
        managerCustomerList.innerHTML = data.items?.length ? data.items.map((user) => `<div class="management-card"><div class="management-top"><strong>${escapeHtml(user.username)}</strong><span class="tag green">当前客户</span></div><div class="management-fields"><div class="auth-field"><label>账户状态</label><input class="auth-input" value="${user.active ? "启用" : "禁用"}" readonly /></div><div class="auth-field"><label>账户余额（美元）</label><input class="auth-input" value="$${Number(user.balance || 0).toFixed(6)}" readonly /></div><div class="auth-field"><label>本周充值</label><input class="auth-input" value="$${Number(user.weekRecharge || 0).toFixed(6)}" readonly /></div><div class="auth-field"><label>本月充值</label><input class="auth-input" value="$${Number(user.monthRecharge || 0).toFixed(6)}" readonly /></div></div><small>用户 ID：${user.id} · 创建时间：${new Date(user.createdAt * 1000).toLocaleString("zh-CN", { hour12: false })}</small><div class="auth-actions"><button class="btn" type="button" data-unassign-customer="${user.id}">解除归属</button></div></div>`).join("") : "<small>该管理员暂无客户。</small>";
        managerCustomerList.querySelectorAll("[data-unassign-customer]").forEach((button) => button.addEventListener("click", () => updateCustomerAssignment(button.dataset.unassignCustomer, "unassign")));
      } catch (error) { managerCustomerList.innerHTML = `<small>${escapeHtml(error.message)}</small>`; }
    }

    async function updateCustomerAssignment(userId, action = "assign", managerId = customerManagerSelect?.value) {
      try {
        await apiRequest("/api/admin/manager-customers", { method: "POST", body: JSON.stringify({ userId: Number(userId), managerId, action }) });
        showToast(action === "unassign" ? "客户归属已解除" : "客户归属已更新");
        await Promise.all([loadAdminUsers(), loadManagerCustomers()]);
      } catch (error) { alert(error.message); }
    }

    function renderPricingTable() {
      if (!pricingList) return;
      const models = (modelCatalogLoaded ? serverModelCatalog.map((item) => getModelMeta(modelCatalogItemToRow(item))) : documentedModels.map(getModelMeta));
      pricingList.innerHTML = models.map((model) => {
        const pricing = getModelPricing(model.name, model.kind);
        const token = pricing.unit === "per_token";
        const dynamic = pricing.pricingMode === "dynamic";
        const catalogItem = serverModelCatalog.find((item) => item.name === model.name);
        const active = catalogItem ? catalogItem.active !== false : true;
        return `<tr data-pricing-model="${model.name}">
          <td><code>${model.name}</code></td><td>${model.providerLabel}</td><td><span class="tag ${active ? "green" : "gray"}">${active ? "已可见" : "已隐藏"}</span></td><td>${token ? `<select class="auth-input" data-pricing-mode><option value="static" ${dynamic ? "" : "selected"}>静态</option><option value="dynamic" ${dynamic ? "selected" : ""}>动态 2 档</option></select>` : "按次"}</td><td>${token ? `<input class="auth-input" data-tier-threshold type="number" min="1" step="1" value="${Number(pricing.tierThresholdTokens || 0)}" placeholder="阈值 Token" />` : "-"}</td>
          <td>${token ? "-" : `<input class="auth-input" data-price type="number" min="0" step="0.000001" value="${pricing.amount}" />`}</td>
          <td>${token ? `<input class="auth-input" data-input-price type="number" min="0" step="0.000001" value="${pricing.inputPrice}" />` : "-"}</td>
          <td>${token ? `<input class="auth-input" data-output-price type="number" min="0" step="0.000001" value="${pricing.outputPrice}" />` : "-"}</td>
          <td>${token ? `<input class="auth-input" data-cache-read-price type="number" min="0" step="0.000001" value="${pricing.cacheReadPrice}" />` : "-"}</td>
          <td>${token ? `<input class="auth-input" data-cache-write-price type="number" min="0" step="0.000001" value="${pricing.cacheWritePrice}" />` : "-"}</td>
          <td>${token ? `<input class="auth-input" data-tier2-input-price type="number" min="0" step="0.000001" value="${pricing.tier2InputPrice || 0}" />` : "-"}</td>
          <td>${token ? `<input class="auth-input" data-tier2-output-price type="number" min="0" step="0.000001" value="${pricing.tier2OutputPrice || 0}" />` : "-"}</td>
          <td>${token ? `<input class="auth-input" data-tier2-cache-read-price type="number" min="0" step="0.000001" value="${pricing.tier2CacheReadPrice || 0}" />` : "-"}</td>
          <td>${token ? `<input class="auth-input" data-tier2-cache-write-price type="number" min="0" step="0.000001" value="${pricing.tier2CacheWritePrice || 0}" />` : "-"}</td>
          <td><div class="auth-actions"><button class="btn primary" type="button" data-save-pricing>保存</button><button class="btn" type="button" data-toggle-model>${active ? "隐藏" : "显示"}</button><button class="btn" type="button" data-delete-model>永久删除</button></div></td></tr>`;
      }).join("");
      pricingList.querySelectorAll("[data-save-pricing]").forEach((button) => button.addEventListener("click", async () => {
        const row = button.closest("[data-pricing-model]");
        const name = row.dataset.pricingModel;
        const perToken = Boolean(row.querySelector("[data-input-price]"));
        const payload = perToken
          ? { billingUnit: "per_token", price: row.querySelector("[data-input-price]").value, inputPrice: row.querySelector("[data-input-price]").value, outputPrice: row.querySelector("[data-output-price]").value, cacheReadPrice: row.querySelector("[data-cache-read-price]").value, cacheWritePrice: row.querySelector("[data-cache-write-price]").value, pricingMode: row.querySelector("[data-pricing-mode]").value, tierThresholdTokens: row.querySelector("[data-tier-threshold]").value, tier2InputPrice: row.querySelector("[data-tier2-input-price]").value, tier2OutputPrice: row.querySelector("[data-tier2-output-price]").value, tier2CacheReadPrice: row.querySelector("[data-tier2-cache-read-price]").value, tier2CacheWritePrice: row.querySelector("[data-tier2-cache-write-price]").value }
          : { billingUnit: "per_task", price: row.querySelector("[data-price]").value };
        try {
          const data = await apiRequest(`/api/admin/models/${encodeURIComponent(name)}`, { method: "PUT", body: JSON.stringify(payload) });
          serverModelPricing[name] = { amount: Number(data.price), unit: data.billingUnit, inputPrice: Number(data.inputPrice), outputPrice: Number(data.outputPrice), cacheReadPrice: Number(data.cacheReadPrice), cacheWritePrice: Number(data.cacheWritePrice), pricingMode: data.pricingMode, tierThresholdTokens: Number(data.tierThresholdTokens || 0), tier2InputPrice: Number(data.tier2InputPrice || 0), tier2OutputPrice: Number(data.tier2OutputPrice || 0), tier2CacheReadPrice: Number(data.tier2CacheReadPrice || 0), tier2CacheWritePrice: Number(data.tier2CacheWritePrice || 0) };
          renderModelSquare();
          showToast(`${name} 价格已保存`);
        } catch (error) { alert(error.message); }
      }));
      pricingList.querySelectorAll("[data-toggle-model]").forEach((button) => button.addEventListener("click", async () => {
        const row = button.closest("[data-pricing-model]");
        const name = row.dataset.pricingModel;
        const hidden = row.querySelector(".tag.gray") !== null;
        try {
          await apiRequest(`/api/admin/models/${encodeURIComponent(name)}`, { method: "PUT", body: JSON.stringify({ action: hidden ? "show" : "hide" }) });
          await loadModelPricing();
          showToast(`${name} 已${hidden ? "显示" : "隐藏"}`);
        } catch (error) { alert(error.message); }
      }));
      pricingList.querySelectorAll("[data-delete-model]").forEach((button) => button.addEventListener("click", async () => {
        const row = button.closest("[data-pricing-model]");
        const name = row.dataset.pricingModel;
        if (!confirm(`确定永久删除模型 ${name} 吗？删除后无法恢复。`)) return;
        try {
          await apiRequest(`/api/admin/models/${encodeURIComponent(name)}`, { method: "DELETE" });
          await loadModelPricing();
          showToast(`${name} 已永久删除`);
        } catch (error) { alert(error.message); }
      }));
    }

    async function loadModelPricing() {
      if (!isSuperAdmin || !sessionToken) return;
      await loadModelCatalog();
      renderPricingTable();
    }

    function renderUserCard(user) {
      const roleAction = isSuperAdmin && user.role !== "super_admin" && user.id !== currentUser?.id
        ? `<div class="auth-field"><label>权限</label><div class="auth-actions"><span class="tag ${user.role === "admin" ? "blue" : "gray"}">${roleLabel(user.role)}</span><button class="btn" type="button" data-toggle-user-role="${user.role === "admin" ? "user" : "admin"}">${user.role === "admin" ? "降为普通用户" : "升级为管理员"}</button></div></div>`
        : "";
      const assignment = isSuperAdmin && user.role === "user"
        ? `<div class="auth-field full"><label>客户归属</label><div class="auth-actions"><select class="auth-input" data-user-manager><option value="">未分配</option>${managerAccounts.map((manager) => `<option value="${manager.id}" ${String(user.managerId || "") === String(manager.id) ? "selected" : ""}>${escapeHtml(manager.username)}（${roleLabel(manager.role)}）</option>`).join("")}</select><button class="btn" type="button" data-save-user-manager>保存归属</button></div></div>`
        : "";
      return `
        <div class="management-card" data-user-id="${user.id}">
          <div class="management-top">
            <strong>${user.username}</strong>
            <span class="tag ${user.role === "super_admin" ? "purple" : user.role === "admin" ? "blue" : "gray"}">${roleLabel(user.role)}</span>
          </div>
          <div class="management-fields">
            <div class="auth-field"><label>账户状态</label><input class="auth-input" value="${user.active ? "启用" : "禁用"}" readonly /></div>
            ${user.role === "user" ? `<div class="auth-field"><label>本周充值</label><input class="auth-input" value="$${Number(user.weekRecharge || 0).toFixed(6)}" readonly /></div><div class="auth-field"><label>本月充值</label><input class="auth-input" value="$${Number(user.monthRecharge || 0).toFixed(6)}" readonly /></div>` : ""}
            ${isSuperAdmin ? `<div class="auth-field"><label>账户余额（美元）</label><input class="auth-input" type="number" min="0" step="0.000001" value="${user.balance}" data-user-balance /></div>` : ""}
            ${roleAction}
            ${assignment}
          </div>
          <small>用户 ID：${user.id} · 创建时间：${new Date(user.createdAt * 1000).toLocaleString("zh-CN", { hour12: false })}</small>
          ${isSuperAdmin ? `<div class="auth-actions"><button class="btn primary" type="button" data-save-user-balance>保存余额</button></div>` : ""}
        </div>`;
    }

    async function loadAdminUsers() {
      if (!canManage || !sessionToken || !userManagementList) {
        if (userManagementList) userManagementList.innerHTML = "<small>管理员登录后可查看用户列表。</small>";
        return;
      }
      try {
        const query = userSearch?.value?.trim() || "";
        const data = await apiRequest(`/api/admin/users?q=${encodeURIComponent(query)}&page=${usersPage}&pageSize=${usersPageSize}`);
        usersTotalPages = data.totalPages || 1;
        if (usersPage > usersTotalPages) {
          usersPage = usersTotalPages;
          await loadAdminUsers();
          return;
        }
        usersPageInfo.textContent = `第 ${data.page} / ${data.totalPages} 页，共 ${data.total} 个用户`;
        prevUsersPage.disabled = data.page <= 1;
        nextUsersPage.disabled = data.page >= data.totalPages;
        userManagementList.innerHTML = data.items.length ? data.items.map(renderUserCard).join("") : "<small>暂无用户。</small>";
        userManagementList.querySelectorAll("[data-save-user-balance]").forEach((button) => {
          button.addEventListener("click", async () => {
            const card = button.closest("[data-user-id]");
            const userId = card.dataset.userId;
            const balance = card.querySelector("[data-user-balance]").value;
            try {
              await apiRequest(`/api/admin/users/${userId}`, {
                method: "PUT",
                body: JSON.stringify({ balance })
              });
              showToast("用户余额已保存");
              await loadAdminUsers();
            } catch (error) {
              alert(error.message);
            }
          });
        });
        userManagementList.querySelectorAll("[data-save-user-manager]").forEach((button) => button.addEventListener("click", () => {
          const card = button.closest("[data-user-id]");
          const managerId = card.querySelector("[data-user-manager]").value;
          updateCustomerAssignment(card.dataset.userId, managerId ? "assign" : "unassign", managerId || null);
        }));
        userManagementList.querySelectorAll("[data-toggle-user-role]").forEach((button) => button.addEventListener("click", async () => {
          const card = button.closest("[data-user-id]");
          const nextRole = button.dataset.toggleUserRole;
          const label = nextRole === "admin" ? "升级为管理员" : "降为普通用户";
          if (!confirm(`确定将该用户${label}吗？`)) return;
          try {
            await apiRequest(`/api/admin/users/${card.dataset.userId}`, { method: "PUT", body: JSON.stringify({ role: nextRole }) });
            showToast(`用户已${label}`);
            await loadAdminUsers();
          } catch (error) { alert(error.message); }
        }));
      } catch (error) {
        userManagementList.innerHTML = `<small>${error.message}</small>`;
      }
    }

    function renderChannelCard(channel) {
      const healthLabels = { healthy: "健康", unhealthy: "异常", unknown: "未检测" };
      const healthClass = channel.healthStatus === "healthy" ? "green" : channel.healthStatus === "unhealthy" ? "orange" : "gray";
      const healthText = healthLabels[channel.healthStatus] || "未检测";
      const errorText = channel.lastError ? `最近错误：${channel.lastError}` : "尚无失败记录";
      return `
        <div class="management-card" data-channel-id="${channel.id}">
          <div class="management-top">
            <strong>${channel.name}</strong>
            <span class="tag ${channel.active ? "green" : "gray"}">${channel.active ? "启用" : "停用"}</span><span class="tag ${healthClass}">${healthText}</span>
          </div>
          <div class="management-fields">
            <div class="auth-field"><label>渠道名称</label><input class="auth-input" value="${channel.name.replace(/"/g, "&quot;")}" data-channel-name /></div>
            <div class="auth-field"><label>上游地址</label><input class="auth-input" value="${channel.upstreamBaseUrl.replace(/"/g, "&quot;")}" data-channel-url /></div>
            <div class="auth-field"><label>上游 API Key</label><input class="auth-input" type="password" placeholder="${channel.upstreamApiKeySet ? channel.upstreamApiKeyHint : "未设置"}" data-channel-key /></div>
            <div class="auth-field"><label>优先级</label><input class="auth-input" type="number" value="${channel.priority}" data-channel-priority /></div>
          </div>
          <div class="auth-field">
            <label>备注</label>
            <input class="auth-input" value="${channel.note.replace(/"/g, "&quot;")}" data-channel-note />
          </div>
          <div class="auth-field">
            <label>支持模型</label>
            <textarea class="auth-input" rows="3" placeholder="留空表示支持全部模型" data-channel-models>${(channel.allowedModels || []).map(escapeHtml).join("\n")}</textarea>
          </div>
          <small class="muted">连续失败：${Number(channel.consecutiveFailures || 0)}；${escapeHtml(errorText)}</small>
          <div class="auth-actions">
            <label style="display:flex;align-items:center;gap:8px;"><input type="checkbox" ${channel.active ? "checked" : ""} data-channel-active /> 启用渠道</label>
            <button class="btn" type="button" data-test-channel>测试渠道</button>
            <button class="btn primary" type="button" data-save-channel>保存修改</button>
          </div>
        </div>`;
    }

    async function loadAdminChannels() {
      if (!isSuperAdmin || !sessionToken || !channelList) {
        if (channelList) channelList.innerHTML = "<small>管理员登录后可查看渠道列表。</small>";
        return;
      }
      try {
        const data = await apiRequest("/api/admin/channels");
        channelList.innerHTML = data.items.length ? data.items.map(renderChannelCard).join("") : "<small>暂无渠道。</small>";
        channelList.querySelectorAll("[data-save-channel]").forEach((button) => {
          button.addEventListener("click", async () => {
            const card = button.closest("[data-channel-id]");
            const channelId = card.dataset.channelId;
            const payload = {
              name: card.querySelector("[data-channel-name]").value.trim(),
              upstreamBaseUrl: card.querySelector("[data-channel-url]").value.trim(),
              priority: card.querySelector("[data-channel-priority]").value,
              note: card.querySelector("[data-channel-note]").value.trim(),
              allowedModels: card.querySelector("[data-channel-models]").value,
              active: card.querySelector("[data-channel-active]").checked
            };
            const keyValue = card.querySelector("[data-channel-key]").value;
            if (keyValue) payload.upstreamApiKey = keyValue;
            try {
              await apiRequest(`/api/admin/channels/${channelId}`, {
                method: "PATCH",
                body: JSON.stringify(payload)
              });
              showToast("渠道信息已保存");
              await loadAdminChannels();
            } catch (error) {
              alert(error.message);
            }
          });
        });
        channelList.querySelectorAll("[data-test-channel]").forEach((button) => {
          button.addEventListener("click", async () => {
            const card = button.closest("[data-channel-id]");
            button.disabled = true;
            try {
              const result = await apiRequest(`/api/admin/channels/${card.dataset.channelId}/test`, { method: "POST" });
              showToast(`渠道连接正常，${result.latencyMs}ms`);
            } catch (error) {
              alert(`渠道测试失败：${error.message}`);
            } finally {
              button.disabled = false;
              await loadAdminChannels();
            }
          });
        });
      } catch (error) {
        channelList.innerHTML = `<small>${error.message}</small>`;
      }
    }

    async function createChannel() {
      if (!isSuperAdmin || !sessionToken) {
        alert("请先登录超级管理员账号。");
        return;
      }
      try {
        await apiRequest("/api/admin/channels", {
          method: "POST",
          body: JSON.stringify({
            name: newChannelName.value.trim(),
            upstreamBaseUrl: newChannelUrl.value.trim(),
            upstreamApiKey: newChannelKey.value,
            priority: newChannelPriority.value,
            note: newChannelNote.value.trim(),
            allowedModels: newChannelModels.value,
            active: true
          })
        });
        newChannelName.value = "";
        newChannelUrl.value = "";
        newChannelKey.value = "";
        newChannelPriority.value = "100";
        newChannelNote.value = "";
        newChannelModels.value = "";
        showToast("渠道已创建");
        await loadAdminChannels();
      } catch (error) {
        alert(error.message);
      }
    }

    async function disableToken(id) {
      if (!confirm("禁用后该 Key 将无法继续调用模型，确定继续吗？")) return;
      try { await apiRequest(`/api/tokens/${id}`, { method: "PUT", body: JSON.stringify({ active: false }) }); loadTokens(); showToast("令牌已禁用"); }
      catch (error) { alert(error.message); }
    }

    async function setTokenActive(id, active) {
      try { await apiRequest(`/api/tokens/${id}`, { method: "PUT", body: JSON.stringify({ active }) }); loadTokens(); showToast(active ? "令牌已启用" : "令牌已禁用"); }
      catch (error) { alert(error.message); }
    }

    async function deleteToken(id) {
      if (!confirm("删除后该令牌将永久失效，历史扣费记录会保留。确定删除吗？")) return;
      try { await apiRequest(`/api/tokens/${id}`, { method: "DELETE" }); loadTokens(); showToast("令牌已删除"); }
      catch (error) { alert(error.message); }
    }

    const documentedModels = [
      ["T香蕉2", "Gemini 图片", "Google", "图片生成", "/v1beta/models/{model}:generateContent", "a-orange", "G", "异步"],
      ["T香蕉pro", "Gemini 图片", "Google", "图片生成", "/v1beta/models/{model}:generateContent", "a-orange", "G", "异步"],
      ["gpt-5.5", "GPT 5.5", "OpenAI", "对话模型", "/v1/chat/completions", "a-blue", "G", "按 Token"],
      ["gpt-6-astra", "GPT 6 Astra", "OpenAI", "对话模型", "/v1/chat/completions", "a-blue", "G", "按 Token"],
      ["gpt-5.6-sol", "GPT 5.6 Sol", "OpenAI", "对话模型", "/v1/chat/completions", "a-blue", "G", "按 Token"],
      ["gpt-5.6-terra", "GPT 5.6 Terra", "OpenAI", "对话模型", "/v1/chat/completions", "a-blue", "G", "按 Token"],
      ["gpt-image-2", "GPT 图片", "OpenAI", "图片生成", "/v1/images/generations", "a-blue", "O", "异步"],
      ["claude-fable-5", "Claude Fable 5", "Anthropic", "对话模型", "/v1/messages", "a-orange", "A", "按 Token"],
      ["claude-opus-4-6", "Claude Opus 4.6", "Anthropic", "对话模型", "/v1/messages", "a-orange", "A", "按 Token"],
      ["claude-opus-4-8", "Claude Opus 4.8", "Anthropic", "对话模型", "/v1/messages", "a-orange", "A", "按 Token"],
      ["claude-sonnet-4-6", "Claude Sonnet 4.6", "Anthropic", "对话模型", "/v1/messages", "a-orange", "A", "按 Token"],
      ["gemini-3.1-flash-lite-preview", "Gemini 3.1 Flash Lite", "Google", "对话模型", "/v1beta/models/{model}:generateContent", "a-orange", "G", "按 Token"],
      ["gemini-3.1-pro-preview", "Gemini 3.1 Pro", "Google", "对话模型", "/v1beta/models/{model}:generateContent", "a-orange", "G", "按 Token"],
      ["ky-fast-720p", "可灵 Fast", "Kling", "视频生成", "/v1/videos", "a-green", "K", "按次"],
      ["ky-pro-720p", "可灵 Pro", "Kling", "视频生成", "/v1/videos", "a-green", "K", "按次"],
      ["grok-video-480p", "Grok 视频", "Grok", "视频生成", "/v1/videos", "a-red", "G", "异步"],
      ["grok-video-720p", "Grok 视频", "Grok", "视频生成", "/v1/videos", "a-red", "G", "异步"],
      ["grok-imagine-video-1.5-480p", "Grok 1.5 视频", "Grok", "视频生成", "/v1/videos", "a-red", "G", "单图"],
      ["grok-imagine-video-1.5-720p", "Grok 1.5 视频", "Grok", "视频生成", "/v1/videos", "a-red", "G", "单图"],
      ["omni-flash", "Omni 视频", "Omni", "视频生成", "/v1/videos", "a-purple", "O", "异步"],
      ["omni-flash-1080p", "Omni 视频", "Omni", "视频生成", "/v1/videos", "a-purple", "O", "异步"],
      ["omni-flash-4k", "Omni 视频", "Omni", "视频生成", "/v1/videos", "a-purple", "O", "异步"],
      ["omni-flash-components", "Omni 视频", "Omni", "参考图生视频", "/v1/videos", "a-purple", "O", "图片"],
      ["omni-flash-components-1080p", "Omni 视频", "Omni", "参考图生视频", "/v1/videos", "a-purple", "O", "图片"],
      ["omni-flash-components-4k", "Omni 视频", "Omni", "参考图生视频", "/v1/videos", "a-purple", "O", "图片"],
      ["omni-flash-edit", "Omni 视频编辑", "Omni", "视频编辑", "/v1/videos", "a-purple", "E", "编辑"],
      ["omni-flash-edit-1080p", "Omni 视频编辑", "Omni", "视频编辑", "/v1/videos", "a-purple", "E", "编辑"],
      ["omni-flash-edit-4k", "Omni 视频编辑", "Omni", "视频编辑", "/v1/videos", "a-purple", "E", "编辑"],
      ["sora-v3-fast", "Sora 视频", "Sora / Veo", "文生视频", "/v1/video/submit/generate", "a-blue", "S", "快速"],
      ["sora-v3-fast-1080p", "Sora 视频", "Sora / Veo", "文生视频", "/v1/video/submit/generate", "a-blue", "S", "快速"],
      ["sora-v3-pro", "Sora 视频", "Sora / Veo", "视频生成", "/v1/video/submit/generate", "a-blue", "S", "专业"],
      ["sora-v3-pro-1080p", "Sora 视频", "Sora / Veo", "视频生成", "/v1/video/submit/generate", "a-blue", "S", "专业"],
      ["sora-v4-480p", "Sora 4 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-blue", "S", "按次"],
      ["sora-v4-720p", "Sora 4 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-blue", "S", "按次"],
      ["sora-v4-1080p", "Sora 4 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-blue", "S", "按次"],
      ["veo-3.1-lite-720", "Veo 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-green", "V", "720p"],
      ["veo-3.1-lite-1080", "Veo 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-green", "V", "1080p"],
      ["veo-3.1-lite-4k", "Veo 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-green", "V", "4K"],
      ["veo-3.1-fast-720", "Veo 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-green", "V", "720p"],
      ["veo-3.1-fast-1080", "Veo 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-green", "V", "1080p"],
      ["veo-3.1-fast-4k", "Veo 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-green", "V", "4K"],
      ["veo-3.1-quality-720", "Veo 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-green", "V", "720p"],
      ["veo-3.1-quality-1080", "Veo 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-green", "V", "1080p"],
      ["veo-3.1-quality-4k", "Veo 视频", "Sora / Veo", "视频生成", "/v1/videos", "a-green", "V", "4K"]
    ];

    let prices = JSON.parse(localStorage.getItem(storageKeys.prices) || "{}");
    let accountBalance = Number(localStorage.getItem("nbapi-balance") || "0");
    let modelPricing = JSON.parse(localStorage.getItem("nbapi-model-pricing") || "null") || {};
    let serverModelPricing = {};
    let serverModelCatalog = [];
    let modelCatalogLoaded = false;
    let showPlazaPrices = true;
    let compactPlaza = false;
    let usersPage = 1;
    let usersPageSize = 8;
    let usersTotalPages = 1;
    let managerAccounts = [];
    const selectedFilters = { provider: "all", billing: "all", kind: "all", tag: "all", endpoint: "all" };
    const routes = ["console", "square", "playground", "tokens", "docs", "users", "pricing", "channels", "logs", "wallet", "settings", "login", "signup", "forgot-password", "reset-password"];

    function applyRoute() {
      const hashValue = (location.hash || "#console").slice(1) || "console";
      const [routeName, queryString = ""] = hashValue.split("?");
      let route = routeName;
      if (route === "reset-password") {
        const token = new URLSearchParams(queryString).get("token") || "";
        window.resetPasswordToken = token;
      }
      if (route === "models") route = "square";
      if (!routes.includes(route)) route = "console";
      const privateRoutes = ["console", "playground", "tokens", "docs", "users", "pricing", "channels", "logs", "wallet", "settings"];
      if (!currentUser && privateRoutes.includes(route)) {
        route = "square";
        history.replaceState(null, "", "#square");
      }
      if (currentUser && (route === "login" || route === "signup")) {
        route = "console";
        history.replaceState(null, "", "#console");
      }
      if (route === "users" && !canManage) {
        alert("该页面仅管理员可用，请先登录管理员账号。");
        route = currentUser ? "console" : "square";
        history.replaceState(null, "", `#${route}`);
      }
      if (route === "pricing" && !isSuperAdmin) {
        alert("模型定价仅超级管理员可用。");
        route = currentUser ? "console" : "square";
        history.replaceState(null, "", `#${route}`);
      }
      if (route === "channels" && !isSuperAdmin) {
        alert("供应商对接仅超级管理员可用。");
        route = currentUser ? "console" : "square";
        history.replaceState(null, "", `#${route}`);
      }
      document.body.classList.remove(...routes.map((item) => `route-${item}`));
      document.body.classList.add(`route-${route}`);
      document.querySelectorAll("a[href^='#']").forEach((link) => {
        link.classList.toggle("active", link.getAttribute("href") === `#${route}`);
      });
      if (route === "logs") loadUsageLogs();
      if (route === "pricing") loadModelPricing();
      if (route === "channels") loadAdminChannels();
      if (route === "users" && isSuperAdmin) loadManagerAccounts();
    }
    window.addEventListener("hashchange", applyRoute);

    function getModelMeta(model) {
      const [name, providerLabel, provider, kind, endpoint, avatarClass, initial, mode] = model;
      const tags = [];
      if (name.includes("720p")) tags.push("720p");
      if (/(fast|speed)/i.test(name)) tags.push("速度快");
      if (/(pro|quality)/i.test(name)) tags.push("稳定");
      if (/(edit|components)/i.test(name) || kind.includes("视频")) tags.push("支持真人");
      const endpointType = endpoint.includes("generateContent") ? "gemini" : endpoint.includes("messages") ? "anthropic" : "openai";
      return { name, providerLabel, provider, kind, endpoint, avatarClass, initial, mode, tags, endpointType };
    }

    const defaultModelPricing = Object.fromEntries(documentedModels.map(([name, providerLabel, provider, kind]) => [name, {
      amount: kind === "对话模型" ? 0 : kind === "图片生成" ? 0.1 : 0.5,
      unit: kind === "对话模型" ? "per_token" : "per_task",
      inputPrice: kind === "对话模型" ? 0 : undefined,
      outputPrice: kind === "对话模型" ? 0 : undefined,
      cacheReadPrice: 0,
      cacheWritePrice: 0
    }]));

    let playgroundConversation = [];

    function resetPlaygroundConversation() {
      playgroundConversation = [];
      if (playgroundMessages) playgroundMessages.innerHTML = "<div class=\"playground-message assistant\">您好，我是牛B的模型操练场，左侧选择模型和相关参数，说出你的要求，我随时为你服务。（发送快捷键 Ctrl+Enter）</div>";
      if (playgroundStatus) playgroundStatus.textContent = "登录后可使用操练场。";
    }

    function getPlaygroundModelRows() {
      if (!modelCatalogLoaded) return documentedModels;
      return serverModelCatalog.filter((item) => item.active !== false).map((item) => modelCatalogItemToRow(item));
    }

    function modelCatalogItemToRow(item) {
        const known = documentedModels.find((row) => row[0] === item.name);
        if (known) return known;
        const kind = item.kind || "对话模型";
        const endpoint = kind === "图片生成" ? "/v1/images/generations" : kind.includes("视频") ? "/v1/videos" : "/v1/chat/completions";
        return [item.name, item.providerLabel || item.provider || "上游模型", item.provider || "Unknown", kind, endpoint, "a-blue", (item.provider || "N").slice(0, 1).toUpperCase(), item.billingUnit === "per_task" ? "按次" : "按 Token"];
    }

    function populatePlaygroundModels() {
      const rows = getPlaygroundModelRows();
      playgroundModel.innerHTML = rows.map(([name, providerLabel, provider, kind]) => `<option value="${escapeHtml(name)}">${escapeHtml(name)} · ${escapeHtml(providerLabel)} · ${escapeHtml(kind)}</option>`).join("");
      updatePlaygroundControls();
    }

    function updatePlaygroundControls() {
      const row = getPlaygroundModelRows().find((item) => item[0] === playgroundModel.value);
      const meta = row ? getModelMeta(row) : null;
      const isChat = Boolean(meta && meta.kind === "对话模型");
      const isGemini = Boolean(meta && meta.endpoint.includes("generateContent"));
      const isTextCapable = isChat || isGemini;
      const isImage = Boolean(meta && meta.kind === "图片生成");
      const isVideo = Boolean(meta && meta.kind.includes("视频"));
      [[playgroundTemperature, isTextCapable], [playgroundTopP, isTextCapable], [playgroundMaxTokens, isTextCapable], [playgroundFrequencyPenalty, isChat], [playgroundPresencePenalty, isChat]].forEach(([input, enabled]) => {
        input.disabled = !enabled;
        input.closest(".playground-control")?.classList.toggle("disabled", !enabled);
      });
      [[playgroundImageOptions, isImage], [playgroundImageSizeControl, isImage], [playgroundVideoOptions, isVideo], [playgroundVideoRatioControl, isVideo], [playgroundVideoDurationControl, isVideo]].forEach(([control, visible]) => { control.hidden = !visible; });
      playgroundVideoResolution.disabled = !isVideo;
      playgroundVideoRatio.disabled = !isVideo;
      playgroundVideoDuration.disabled = !isVideo;
      updateVideoResolutionOptions(meta && meta.kind.includes("视频") ? meta.name : "");
    }

    function updateVideoResolutionOptions(model) {
      const current = playgroundVideoResolution.value;
      let values = ["720p", "1080p", "4k"];
      if (model.startsWith("grok-")) values = ["480p", "720p"];
      if (model.startsWith("sora-v3-")) values = ["720p", "1080p"];
      playgroundVideoResolution.innerHTML = values.map((value) => `<option value="${value}">${value.toUpperCase()}</option>`).join("");
      playgroundVideoResolution.value = values.includes(current) ? current : values[0];
    }

    function resolveVideoModel(model, resolution) {
      const normalized = String(resolution || "720p").toLowerCase();
      if (model.startsWith("veo-")) {
        const suffix = normalized === "4k" ? "4k" : normalized === "1080p" ? "1080" : "720";
        return model.replace(/-(720|1080|4k)$/i, `-${suffix}`);
      }
      if (model.startsWith("sora-v3-")) {
        return normalized === "1080p" ? (model.endsWith("-1080p") ? model : `${model}-1080p`) : model.replace(/-1080p$/i, "");
      }
      if (model.startsWith("omni-")) {
        if (normalized === "1080p" || normalized === "4k") return model.replace(/-(1080p|4k)$/i, "") + `-${normalized}`;
        return model.replace(/-(1080p|4k)$/i, "");
      }
      if (model.startsWith("grok-")) {
        const suffix = normalized === "480p" ? "480p" : "720p";
        return model.replace(/-(480p|720p)$/i, "") + `-${suffix}`;
      }
      return model;
    }

    function appendPlaygroundMessage(role, content) {
      const message = document.createElement("div");
      message.className = `playground-message ${role}`;
      message.textContent = content;
      playgroundMessages.appendChild(message);
      playgroundMessages.scrollTop = playgroundMessages.scrollHeight;
    }

    function removePlaygroundConversationMessage(message) {
      const index = playgroundConversation.indexOf(message);
      if (index >= 0) playgroundConversation.splice(index, 1);
    }

    function closeMediaLightbox() {
      const lightbox = document.getElementById("mediaLightbox");
      if (!lightbox) return;
      lightbox.classList.remove("show");
      lightbox.setAttribute("aria-hidden", "true");
      const media = lightbox.querySelector("img, video");
      if (media?.tagName === "VIDEO") media.pause();
    }

    function openMediaLightbox(url, taskType, resolution = "") {
      let lightbox = document.getElementById("mediaLightbox");
      if (!lightbox) {
        lightbox = document.createElement("div");
        lightbox.id = "mediaLightbox";
        lightbox.className = "media-lightbox";
        lightbox.setAttribute("aria-hidden", "true");
        lightbox.innerHTML = "<div class=\"media-lightbox-content\" role=\"dialog\" aria-modal=\"true\" aria-label=\"媒体预览\"><button class=\"media-lightbox-close\" type=\"button\" aria-label=\"关闭预览\">&times;</button><div class=\"media-lightbox-media\"></div><div class=\"media-lightbox-meta\"></div></div>";
        document.body.appendChild(lightbox);
        lightbox.addEventListener("click", (event) => { if (event.target === lightbox) closeMediaLightbox(); });
        lightbox.querySelector(".media-lightbox-close").addEventListener("click", closeMediaLightbox);
      }
      const mediaHost = lightbox.querySelector(".media-lightbox-media");
      const meta = lightbox.querySelector(".media-lightbox-meta");
      const media = document.createElement(taskType === "video" ? "video" : "img");
      media.src = url;
      media.alt = taskType === "video" ? "放大查看生成的视频" : "放大查看生成的图片";
      if (taskType === "video") {
        media.controls = true;
        media.autoplay = true;
        media.playsInline = true;
      }
      mediaHost.replaceChildren(media);
      meta.textContent = taskType === "image" && resolution ? `分辨率：${resolution}` : "点击关闭按钮或按 Esc 返回";
      lightbox.classList.add("show");
      lightbox.setAttribute("aria-hidden", "false");
      lightbox.querySelector(".media-lightbox-close").focus();
    }

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeMediaLightbox();
        closeModelPricingModal();
      }
    });

    function appendPlaygroundMedia(url, taskType) {
      const message = document.createElement("div");
      message.className = "playground-message assistant";
      const label = document.createElement("div");
      label.textContent = taskType === "video" ? "视频生成成功" : "图片生成成功";
      const media = taskType === "video" ? document.createElement("video") : document.createElement("img");
      media.src = url;
      media.alt = taskType === "video" ? "模型生成的视频" : "模型生成的图片";
      media.loading = "lazy";
      if (taskType === "video") {
        media.controls = true;
        media.playsInline = true;
      } else {
        const resolution = document.createElement("div");
        resolution.className = "media-resolution";
        resolution.textContent = "分辨率：读取中...";
        media.addEventListener("load", () => {
          resolution.textContent = media.naturalWidth && media.naturalHeight ? `分辨率：${media.naturalWidth} × ${media.naturalHeight}` : "分辨率：无法读取";
        });
        media.addEventListener("error", () => { resolution.textContent = "分辨率：无法读取"; });
        media.addEventListener("click", () => openMediaLightbox(url, taskType, resolution.textContent.replace("分辨率：", "")));
        media.style.cssText = "display:block;max-width:min(680px,100%);max-height:52vh;margin-top:8px;border-radius:8px;cursor:zoom-in;object-fit:contain;";
        message.append(label, media, resolution);
        playgroundMessages.appendChild(message);
        playgroundMessages.scrollTop = playgroundMessages.scrollHeight;
        return;
      }
      media.className = "playground-media";
      media.addEventListener("click", () => openMediaLightbox(url, taskType));
      message.append(label, media);
      playgroundMessages.appendChild(message);
      playgroundMessages.scrollTop = playgroundMessages.scrollHeight;
    }

    function appendPlaygroundVideo(url) {
      const message = document.createElement("div");
      message.className = "playground-message assistant";
      const label = document.createElement("div");
      label.textContent = "视频生成成功";
      const video = document.createElement("video");
      video.src = url;
      video.controls = true;
      video.style.cssText = "display:block;max-width:min(620px,100%);margin-top:8px;border-radius:8px;";
      message.append(label, video);
      playgroundMessages.appendChild(message);
      playgroundMessages.scrollTop = playgroundMessages.scrollHeight;
    }

    const wait = (milliseconds) => new Promise((resolve) => window.setTimeout(resolve, milliseconds));

    async function pollAsyncTask(apiKey, taskId, taskType, queryPath) {
      const maxAttempts = taskType === "video" ? 120 : 60;
      for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
        await wait(attempt === 0 ? 800 : (taskType === "video" ? 5000 : 3000));
        const taskPath = queryPath || (taskType === "video" ? `/v1/videos/${encodeURIComponent(taskId)}` : `/v1/images/tasks/${encodeURIComponent(taskId)}`);
        const response = await fetch(`${API_BASE}${taskPath}`, { headers: { "X-NBAPI-Key": apiKey, "Idempotency-Key": `playground-poll-${taskId}` } });
        const task = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(task.error?.message || task.error || `查询${taskType === "video" ? "视频" : "图片"}任务失败（${response.status}）`);
        const status = String(task.status || "").toLowerCase();
        const progress = task.progress == null ? "" : ` ${task.progress}%`;
        playgroundStatus.textContent = `${taskType === "video" ? "视频" : "图片"}任务 ${status || "processing"}${progress}，请稍候...`;
        const url = task.data?.[0]?.url || task.result?.data?.[0]?.url || task.data?.url || task.result?.url || task.url;
        if ((status === "succeeded" || status === "completed" || status === "success") && url) return url;
        if (status === "failed" || status === "error" || status === "cancelled" || status === "canceled") {
          const refunded = response.headers.get("X-NBAPI-Refunded") === "1";
          throw new Error(`${task.error?.message || `${taskType === "video" ? "视频" : "图片"}生成失败`}${refunded ? "，本次费用已自动退回。" : ""}`);
        }
      }
      throw new Error(`${taskType === "video" ? "视频" : "图片"}任务查询超时，请稍后到使用日志查看任务状态`);
    }

    function playgroundResponseText(data) {
      const content = data?.choices?.[0]?.message?.content;
      if (Array.isArray(content)) return content.map((part) => part?.text || "").join("");
      if (typeof content === "string") return content;
      const anthropicContent = data?.content;
      if (Array.isArray(anthropicContent)) {
        const text = anthropicContent.map((part) => part?.text || "").join("");
        if (text) return text;
      }
      const geminiText = data?.candidates?.[0]?.content?.parts?.map((part) => part?.text || "").join("");
      if (geminiText) return geminiText;
      if (data?.data?.[0]?.url) return `图片地址：${data.data[0].url}`;
      return JSON.stringify(data, null, 2);
    }

    async function runPlayground() {
      const prompt = playgroundPrompt.value.trim();
      const apiKey = playgroundToken.value || activeApiKey;
      if (!sessionToken) { alert("请先登录后使用操练场。"); return; }
      if (!apiKey) { alert("请先在令牌管理中创建一个令牌，并在当前浏览器中保留完整 Key。"); location.hash = "tokens"; return; }
      if (!prompt) { alert("请输入要发送的问题。"); playgroundPrompt.focus(); return; }
      const model = playgroundModel.value;
      const modelMeta = getModelMeta(getPlaygroundModelRows().find((item) => item[0] === model));
      const isGemini = modelMeta.endpoint.includes("generateContent");
      const isClaude = modelMeta.provider === "Anthropic" || modelMeta.endpoint.includes("/v1/messages");
      const isGeminiImage = isGemini && modelMeta.kind === "图片生成";
      const isAsyncMedia = modelMeta.kind === "图片生成" || modelMeta.kind.includes("视频");
      const userMessage = { role: "user", content: prompt };
      playgroundConversation.push(userMessage);
      appendPlaygroundMessage("user", prompt);
      playgroundPrompt.value = "";
      playgroundStatus.textContent = `正在调用 ${model}，请稍候...`;
      try {
        const endpoint = isGemini ? `/v1beta/models/${encodeURIComponent(model)}:generateContent` : isClaude ? "/v1/messages" : modelMeta.kind === "图片生成" ? "/v1/images/generations" : modelMeta.kind.includes("视频") ? (model.startsWith("sora-v3-") ? "/v1/video/submit/generate" : "/v1/videos") : "/v1/chat/completions";
        const selectedVideoResolution = playgroundVideoResolution.value;
        const resolvedVideoModel = modelMeta.kind.includes("视频") ? resolveVideoModel(model, selectedVideoResolution) : model;
        const requestBody = isGeminiImage
          ? { contents: [{ role: "user", parts: [{ text: prompt }] }], generationConfig: { responseModalities: ["TEXT", "IMAGE"], temperature: Number(playgroundTemperature.value), topP: Number(playgroundTopP.value), maxOutputTokens: Number(playgroundMaxTokens.value), imageConfig: { aspectRatio: playgroundImageAspect.value, imageSize: playgroundImageSize.value } } }
          : isGemini
            ? { contents: [{ role: "user", parts: [{ text: prompt }] }], generationConfig: { temperature: Number(playgroundTemperature.value), topP: Number(playgroundTopP.value), maxOutputTokens: Number(playgroundMaxTokens.value) } }
          : modelMeta.kind === "图片生成"
            ? { model, prompt, n: 1, size: playgroundImageAspect.value, image_size: playgroundImageSize.value, quality: "auto", response_format: "url" }
          : modelMeta.kind.includes("视频")
              ? endpoint.includes("submit/generate")
                ? { model: resolvedVideoModel, prompt, duration: Number(playgroundVideoDuration.value), metadata: { modeType: "text2video", ratio: playgroundVideoRatio.value, enableSound: "on" } }
                : model.startsWith("sora-v4-")
                  ? { model: resolvedVideoModel, prompt, duration: Number(playgroundVideoDuration.value), metadata: { modeType: "text2video", ratio: playgroundVideoRatio.value, enableSound: "on" } }
                  : { model: resolvedVideoModel, prompt, ...(model.startsWith("veo-") ? {} : { seconds: String(playgroundVideoDuration.value) }), aspect_ratio: playgroundVideoRatio.value, n: 1 }
              : isClaude
                ? { model, messages: playgroundConversation.map((message) => ({ role: message.role, content: message.content })), temperature: Number(playgroundTemperature.value), top_p: Number(playgroundTopP.value), max_tokens: Number(playgroundMaxTokens.value), stream: false }
                : { model, messages: playgroundConversation, temperature: Number(playgroundTemperature.value), top_p: Number(playgroundTopP.value), frequency_penalty: Number(playgroundFrequencyPenalty.value), presence_penalty: Number(playgroundPresencePenalty.value), max_tokens: Number(playgroundMaxTokens.value), stream: false };
        const requestId = `playground-${crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`}`;
        const response = await fetch(`${API_BASE}${endpoint}`, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-NBAPI-Key": apiKey, "Idempotency-Key": requestId },
          body: JSON.stringify(requestBody)
        });
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
          const refunded = response.headers.get("X-NBAPI-Refunded") === "1" || data.refunded;
          const refundAmount = response.headers.get("X-NBAPI-Refunded-Amount") || data.refundAmount || "";
          const refundText = refunded ? `，预扣费用已自动退回${refundAmount ? ` $${refundAmount}` : ""}` : "";
          throw new Error(`${data.error?.message || data.error || `调用失败（${response.status}）`}${refundText}`);
        }
        const charged = response.headers.get("X-NBAPI-Charged");
        const latestBalance = response.headers.get("X-NBAPI-Balance");
        const asyncTaskId = isAsyncMedia ? (data.task_id || data.taskId || data.id) : "";
        if (asyncTaskId) {
          const taskType = modelMeta.kind.includes("视频") ? "video" : "image";
          appendPlaygroundMessage("assistant", `${taskType === "video" ? "视频" : "图片"}任务已提交，任务编号：${asyncTaskId}`);
          playgroundStatus.textContent = `${taskType === "video" ? "视频" : "图片"}任务已进入队列，正在等待生成...`;
          const queryPath = model.startsWith("sora-v3-") ? `/v1/video/fetch/${encodeURIComponent(asyncTaskId)}` : taskType === "video" ? `/v1/videos/${encodeURIComponent(asyncTaskId)}` : `/v1/images/tasks/${encodeURIComponent(asyncTaskId)}`;
          const mediaUrl = await pollAsyncTask(apiKey, asyncTaskId, taskType, queryPath);
          appendPlaygroundMedia(mediaUrl, taskType);
          await refreshAccountBalance();
          playgroundStatus.textContent = `${taskType === "video" ? "视频" : "图片"}生成成功，本次扣费 $${charged || "0.000000"}，当前余额 $${latestBalance || accountBalance.toFixed(6)}。`;
          return;
        }
        const text = playgroundResponseText(data);
        playgroundConversation.push({ role: "assistant", content: text });
        appendPlaygroundMessage("assistant", text);
        const usageObject = data.usage || data.usageMetadata;
        const usage = usageObject ? `，使用 ${usageObject.total_tokens || usageObject.totalTokens || usageObject.totalTokenCount || 0} tokens` : "";
        await refreshAccountBalance();
        playgroundStatus.textContent = `调用成功${usage}，本次扣费 $${charged || "0.000000"}，当前余额 $${latestBalance || accountBalance.toFixed(6)}。`;
      } catch (error) {
        removePlaygroundConversationMessage(userMessage);
        appendPlaygroundMessage("system", error.message);
        playgroundStatus.textContent = "调用失败，请检查令牌、上游 Key、模型名称和余额。";
      }
    }

    async function loadModelCatalog() {
      try {
        const catalogQuery = isSuperAdmin ? "?includeInactive=1" : "";
        const data = await apiRequest(`/api/models${catalogQuery}`);
        serverModelPricing = Object.fromEntries((data.models || []).map((item) => [item.name, { amount: Number(item.price || 0), unit: item.billingUnit, inputPrice: Number(item.inputPrice || item.price || 0), outputPrice: Number(item.outputPrice || item.price || 0), cacheReadPrice: Number(item.cacheReadPrice || 0), cacheWritePrice: Number(item.cacheWritePrice || 0), pricingMode: item.pricingMode || "static", tierThresholdTokens: Number(item.tierThresholdTokens || 0), tier2InputPrice: Number(item.tier2InputPrice || 0), tier2OutputPrice: Number(item.tier2OutputPrice || 0), tier2CacheReadPrice: Number(item.tier2CacheReadPrice || 0), tier2CacheWritePrice: Number(item.tier2CacheWritePrice || 0) }]));
        serverModelCatalog = data.models || [];
        modelCatalogLoaded = true;
        populatePlaygroundModels();
        renderDocsModelList();
        renderModelSquare();
      } catch { /* The local defaults keep the plaza usable during startup. */ }
    }

    function getModelPricing(name, kind) {
      return serverModelPricing[name] || modelPricing[name] || defaultModelPricing[name] || { amount: kind === "对话模型" ? 0 : kind === "图片生成" ? 0.1 : 0.5, unit: kind === "对话模型" ? "per_token" : "per_task" };
    }

    function formatTokenThreshold(tokens) {
      const value = Number(tokens || 0);
      if (!value) return "未设置";
      if (value >= 1000 && value % 1000 === 0) return `${value / 1000}K`;
      return value.toLocaleString("zh-CN");
    }

    function getPricingTier(pricing, tierNumber = 1) {
      if (tierNumber === 2) {
        return {
          inputPrice: pricing.tier2InputPrice ?? pricing.inputPrice ?? pricing.amount ?? 0,
          outputPrice: pricing.tier2OutputPrice ?? pricing.outputPrice ?? pricing.amount ?? 0,
          cacheReadPrice: pricing.tier2CacheReadPrice ?? pricing.cacheReadPrice ?? 0,
          cacheWritePrice: pricing.tier2CacheWritePrice ?? pricing.cacheWritePrice ?? 0
        };
      }
      return {
        inputPrice: pricing.inputPrice ?? pricing.amount ?? 0,
        outputPrice: pricing.outputPrice ?? pricing.amount ?? 0,
        cacheReadPrice: pricing.cacheReadPrice ?? 0,
        cacheWritePrice: pricing.cacheWritePrice ?? 0
      };
    }

    function formatTierPriceLines(pricing, prefix = "") {
      return `${prefix}输入 $${Number(pricing.inputPrice ?? pricing.amount ?? 0).toFixed(4)} / 1M Tokens<br>${prefix}补全 $${Number(pricing.outputPrice ?? pricing.amount ?? 0).toFixed(4)} / 1M Tokens<br>${prefix}缓存读 $${Number(pricing.cacheReadPrice ?? 0).toFixed(4)} / 1M Tokens<br>${prefix}缓存创建 $${Number(pricing.cacheWritePrice ?? 0).toFixed(4)} / 1M Tokens`;
    }

    function formatPricingValue(value) {
      return `$${Number(value ?? 0).toFixed(4)}`;
    }

    function formatModelPrice(pricing, modelName = "") {
      if (pricing.unit === "per_token") {
        const tier1 = formatTierPriceLines(getPricingTier(pricing));
        if (pricing.pricingMode === "dynamic") {
          return `<div class="plaza-price-tier1"><strong>${tier1}</strong></div><button class="dynamic-price-label dynamic-price-button" type="button" data-model-pricing="${escapeHtml(modelName)}" title="点击查看两档完整计费">动态计费 · 2档</button>`;
        }
        return `<strong>${tier1}</strong>`;
      }
      return `<strong>$${Number(pricing.amount || 0).toFixed(4)} / 次</strong>`;
    }

    function renderModelPricingDetails(pricing) {
      const threshold = formatTokenThreshold(pricing.tierThresholdTokens);
      const tierRows = [
        { label: "第1档", rule: `len &lt; ${threshold}`, values: getPricingTier(pricing, 1) },
        { label: "第2档", rule: `len ≥ ${threshold}`, values: getPricingTier(pricing, 2) }
      ];
      return `
        <div class="pricing-detail-summary">
          <span>计费方式</span><strong>按量计费</strong>
          <span>档位阈值</span><strong>输入 Token ${threshold}</strong>
        </div>
        <div class="pricing-detail-table-wrap">
          <table class="pricing-detail-table">
            <thead><tr><th>档位</th><th>输入（$/1M tokens）</th><th>补全（$/1M tokens）</th><th>缓存读（$/1M tokens）</th><th>缓存创建（$/1M tokens）</th></tr></thead>
            <tbody>${tierRows.map((tier) => `<tr><td><span class="pricing-detail-tier"><strong>${tier.label}</strong><small>${tier.rule}</small></span></td><td>${formatPricingValue(tier.values.inputPrice)}</td><td>${formatPricingValue(tier.values.outputPrice)}</td><td>${formatPricingValue(tier.values.cacheReadPrice)}</td><td>${formatPricingValue(tier.values.cacheWritePrice)}</td></tr>`).join("")}</tbody>
          </table>
        </div>
        <p class="pricing-detail-note">系统会按上游返回的真实输入 Token 选择档位；达到阈值时使用第 2 档，输入、补全和缓存相关费用分别按对应价格结算。</p>
      `;
    }

    function openModelPricingModal(modelName) {
      const pricing = getModelPricing(modelName, "对话模型");
      if (!modelPricingModal || pricing.pricingMode !== "dynamic") return;
      const model = serverModelCatalog.find((item) => item.name === modelName);
      const fallback = documentedModels.find((item) => item[0] === modelName);
      modelPricingModalTitle.textContent = `${modelName} · 分档价格`;
      modelPricingModalSubtitle.textContent = `${model?.providerLabel || fallback?.[1] || "模型"} · 按上游返回的真实输入 Token 选择计费档位。`;
      modelPricingModalBody.innerHTML = renderModelPricingDetails(pricing);
      modelPricingModal.classList.add("show");
      modelPricingModal.setAttribute("aria-hidden", "false");
      closeModelPricingModalButton?.focus();
    }

    function closeModelPricingModal() {
      if (!modelPricingModal) return;
      modelPricingModal.classList.remove("show");
      modelPricingModal.setAttribute("aria-hidden", "true");
    }

    function saveModelPricing(name, amount, unit) {
      modelPricing[name] = { amount: Math.max(0, Number(amount) || 0), unit };
      localStorage.setItem("nbapi-model-pricing", JSON.stringify(modelPricing));
    }

    function updateBalance() {
      balanceDisplay.textContent = currentUser ? `$ ${accountBalance.toFixed(2)}` : "-";
      balancePill.style.display = currentUser ? "inline-flex" : "none";
      if (currentUser) localStorage.setItem("nbapi-balance", accountBalance.toFixed(2));
    }

    async function refreshAccountBalance() {
      if (!sessionToken) return null;
      const me = await apiRequest("/api/me");
      if (currentUser) currentUser.balance = me.balance;
      accountBalance = Number(me.balance || 0);
      updateBalance();
      return me;
    }

    function setTheme(theme) {
      const dark = theme === "dark";
      document.body.classList.toggle("dark", dark);
      themeToggle.textContent = dark ? "浅色模式" : "深色模式";
      localStorage.setItem(storageKeys.theme, theme);
    }

    function getPrice(cell) {
      return prices[cell.dataset.priceId] || cell.dataset.defaultPrice;
    }

    function savePrice(id, value) {
      prices[id] = value.trim() || "未设置";
      localStorage.setItem(storageKeys.prices, JSON.stringify(prices));
    }

    function renderModelSquare() {
      const query = (modelSearch?.value || "").trim().toLowerCase();
      const modelRows = getPlaygroundModelRows();
      const visibleModels = modelRows.map(getModelMeta).filter((model) =>
        `${model.name} ${model.providerLabel} ${model.provider} ${model.kind} ${model.tags.join(" ")} ${model.endpointType}`.toLowerCase().includes(query) &&
        (selectedFilters.provider === "all" || model.provider === selectedFilters.provider) &&
        (selectedFilters.kind === "all" || model.kind === selectedFilters.kind) &&
        (selectedFilters.billing === "all" || getModelPricing(model.name, model.kind).unit === selectedFilters.billing) &&
        (selectedFilters.tag === "all" || model.tags.includes(selectedFilters.tag)) &&
        (selectedFilters.endpoint === "all" || model.endpointType === selectedFilters.endpoint)
      );
      modelGrid.classList.toggle("compact-plaza", compactPlaza);
      document.getElementById("plazaCount").textContent = `当前显示 ${visibleModels.length} / ${modelRows.length} 个模型`;
      modelGrid.innerHTML = visibleModels.map((model) => {
        const pricing = getModelPricing(model.name, model.kind);
        const priceMarkup = formatModelPrice(pricing, model.name);
        return `
        <article class="plaza-card">
          <div class="plaza-card-top">
            <div class="avatar ${model.avatarClass}">${model.initial}</div>
            <div class="plaza-card-name"><strong>${model.name}</strong><small>${model.providerLabel}</small></div>
            <button class="copy-model" type="button" data-copy-model="${model.name.replace(/"/g, "&quot;")}" title="复制模型名称" aria-label="复制 ${model.name}"><span class="copy-icon"></span></button>
          </div>
          ${showPlazaPrices ? `<div class="plaza-price">${priceMarkup}<br><span>计费方式：${pricing.unit === "per_token" ? "按 1M Token，按输入/输出分别计费" : "按次"}</span></div>` : ""}
          <p class="plaza-description">${model.kind}，提交任务后通过对应查询接口获取结果。</p>
          <div class="plaza-card-foot"><span class="tag green">已接入</span><span class="tag gray">${model.kind}</span><span class="tag blue">${model.mode}</span><code>${model.endpoint}</code></div>
        </article>
      `;
      }).join("");
      modelGrid.querySelectorAll("[data-copy-model]").forEach((button) => {
        button.addEventListener("click", () => copyModelName(button.dataset.copyModel));
      });
      modelGrid.querySelectorAll("[data-model-pricing]").forEach((button) => {
        button.addEventListener("click", () => openModelPricingModal(button.dataset.modelPricing));
      });
    }

    function showToast(message) {
      copyToast.textContent = message;
      copyToast.classList.add("show");
      window.clearTimeout(copyToast.timer);
      copyToast.timer = window.setTimeout(() => copyToast.classList.remove("show"), 1600);
    }

    async function copyModelName(modelName) {
      try {
        await navigator.clipboard.writeText(modelName);
      } catch {
        const textarea = document.createElement("textarea");
        textarea.value = modelName;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        textarea.remove();
      }
      copyToast.textContent = `${modelName} 已复制`;
      copyToast.classList.add("show");
      window.clearTimeout(copyToast.timer);
      copyToast.timer = window.setTimeout(() => copyToast.classList.remove("show"), 1600);
    }

    async function copyDocText(value) {
      try {
        await navigator.clipboard.writeText(value);
      } catch {
        const textarea = document.createElement("textarea");
        textarea.value = value;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        textarea.remove();
      }
      showToast("文档内容已复制");
    }

    function renderDocsModelList() {
      if (!docsModelList) return;
      const models = serverModelCatalog.length ? serverModelCatalog.filter((item) => item.active !== false) : documentedModels.map(([name, providerLabel, provider, kind]) => ({ name, providerLabel, provider, kind }));
      docsModelList.innerHTML = models.length ? models.map((model) => `<div class="docs-model"><code>${escapeHtml(model.name)}</code><button class="btn" type="button" data-copy-doc-value="${escapeHtml(model.name)}">复制</button></div>`).join("") : '<span class="muted">暂无可用模型。</span>';
      docsModelList.querySelectorAll("[data-copy-doc-value]").forEach((button) => button.addEventListener("click", () => copyDocText(button.dataset.copyDocValue)));
    }

    document.querySelectorAll("[data-copy-target]").forEach((button) => button.addEventListener("click", () => {
      const target = document.getElementById(button.dataset.copyTarget);
      if (target) copyDocText(target.textContent);
    }));
    document.querySelectorAll("[data-copy-doc]").forEach((button) => button.addEventListener("click", () => copyDocText(button.dataset.copyDoc)));

    async function copyFullToken(token) {
      if (!token) {
        alert("这个令牌没有保存完整 Key。旧 Key 本身没有失效，如果你以前保存过仍可继续使用；脱敏值无法反推出完整 Key。");
        return;
      }
      await copyModelName(token);
      activeApiKey = token;
      localStorage.setItem("nbapi-active-api-key", activeApiKey);
      showToast("完整 API Key 已复制");
    }

    function renderPrices() {
      syncAuthState();

      priceCells.forEach((cell) => {
        const value = getPrice(cell);
        if (isSuperAdmin) {
          cell.innerHTML = `<input class="price-input" aria-label="修改价格" value="${value.replace(/"/g, "&quot;")}" />`;
          const input = cell.querySelector("input");
          input.addEventListener("change", () => savePrice(cell.dataset.priceId, input.value));
          input.addEventListener("blur", () => {
            savePrice(cell.dataset.priceId, input.value);
            input.value = getPrice(cell);
          });
        } else {
          cell.innerHTML = `<span class="price-value">${value}</span>`;
        }
      });
      renderModelSquare();
    }

    themeToggle.addEventListener("click", () => {
      setTheme(document.body.classList.contains("dark") ? "light" : "dark");
    });

    authLogin.addEventListener("click", () => {
      location.hash = "login";
      loginUsername?.focus();
    });

    authSignup.addEventListener("click", () => {
      location.hash = "signup";
      signupUsername?.focus();
    });

    authLogout.addEventListener("click", async () => {
      clearSessionState();
      syncAuthState();
      renderPrices();
      setUpstreamUiState();
      loadTokens();
      await Promise.all([loadAdminUsers(), loadModelCatalog()]);
      location.hash = "console";
      showToast("已退出登录");
    });

    async function submitLogin() {
      if (!loginUsername.value.trim() || !loginPassword.value) {
        alert("请先填写用户名和密码。");
        return;
      }
      try {
        await performUserLogin(loginUsername.value.trim(), loginPassword.value, "登录");
      } catch (error) {
        alert(error.message);
      }
    }
    loginSubmit.addEventListener("click", submitLogin);
    [loginUsername, loginPassword].forEach((input) => input.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        submitLogin();
      }
    }));

    requestReset?.addEventListener("click", async () => {
      const email = resetEmail?.value.trim() || "";
      if (!email) { alert("请输入注册邮箱。"); return; }
      requestReset.disabled = true;
      resetRequestStatus.textContent = "正在发送，请稍候...";
      try {
        const data = await fetch(`${API_BASE}/api/auth/password-reset/request`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email }) }).then(async (response) => {
          const result = await response.json();
          if (!response.ok) throw new Error(result.error || "发送失败");
          return result;
        });
        resetRequestStatus.textContent = data.message || "如果该邮箱已注册，找回邮件将发送到该邮箱。";
      } catch (error) {
        resetRequestStatus.textContent = error.message === "password_reset_not_configured" ? "密码找回服务尚未配置，请联系管理员。" : "邮件发送失败，请稍后再试。";
      } finally { requestReset.disabled = false; }
    });

    confirmReset?.addEventListener("click", async () => {
      const token = window.resetPasswordToken || "";
      const password = newResetPassword?.value || "";
      if (!token) { resetConfirmStatus.textContent = "找回链接无效，请重新申请。"; return; }
      if (password.length < 12) { alert("新密码至少 12 位。"); return; }
      if (password !== confirmResetPassword.value) { alert("两次密码不一致。"); return; }
      confirmReset.disabled = true;
      try {
        const data = await fetch(`${API_BASE}/api/auth/password-reset/confirm`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token, newPassword: password }) }).then(async (response) => {
          const result = await response.json();
          if (!response.ok) throw new Error(result.error || "重置失败");
          return result;
        });
        resetConfirmStatus.textContent = data.message || "密码已重置，请使用新密码登录。";
        window.setTimeout(() => { location.hash = "login"; }, 900);
      } catch (error) { resetConfirmStatus.textContent = error.message === "reset_token_invalid_or_expired" ? "链接已失效，请重新申请。" : "密码重置失败，请稍后再试。"; }
      finally { confirmReset.disabled = false; }
    });

    signupSubmit.addEventListener("click", async () => {
      const username = signupUsername?.value?.trim() || "";
      const email = signupEmail?.value?.trim() || "";
      const password = signupPassword?.value || "";
      const confirm = signupConfirm?.value || "";
      if (!username || !email || !password) {
        alert("请先把注册信息填完整。");
        return;
      }
      if (password !== confirm) {
        alert("两次密码不一致。");
        return;
      }
      try {
        const data = await fetch(`${API_BASE}/api/auth/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password, designatedAdmin: signupDesignatedAdminEnabled.checked ? signupDesignatedAdmin.value.trim() : "" })
        }).then(async (response) => {
          const result = await response.json();
          if (!response.ok) throw new Error(result.error || "注册失败");
          return result;
        });
        applyUserSession(data.user, data.token);
        signupUsername.value = "";
        signupEmail.value = "";
        signupPassword.value = "";
        signupConfirm.value = "";
        signupDesignatedAdmin.value = "";
        signupDesignatedAdminEnabled.checked = false;
        signupDesignatedAdmin.disabled = true;
        await loadManagerAccounts();
        await Promise.all([loadTokens(), loadAdminUsers(), loadModelCatalog()]);
        location.hash = "console";
        applyRoute();
        showToast(data.managerMatched ? `注册成功，已归属管理员 ${data.managerUsername}` : "注册成功，未匹配到指定管理员");
      } catch (error) {
        const messages = {
          username_length_invalid: "用户名长度需要 3-32 位。",
          username_format_invalid: "用户名只能包含字母、数字、下划线或短横线。",
          email_invalid: "请输入有效邮箱。",
          password_too_short: "密码至少 6 位。",
          email_already_exists: "这个邮箱已经注册。",
          username_already_exists: "这个用户名已经注册。"
        };
        alert(messages[error.message] || error.message);
      }
    });
    signupDesignatedAdminEnabled.addEventListener("change", () => {
      signupDesignatedAdmin.disabled = !signupDesignatedAdminEnabled.checked;
      if (signupDesignatedAdminEnabled.checked) signupDesignatedAdmin.focus();
      else signupDesignatedAdmin.value = "";
    });

    function closeTokenCreator() {
      tokenModal.classList.remove("show");
      tokenModal.setAttribute("aria-hidden", "true");
    }

    createToken.addEventListener("click", () => {
      if (!sessionToken) { alert("请先登录用户账号，再创建令牌。"); return; }
      tokenModal.classList.add("show");
      tokenModal.setAttribute("aria-hidden", "false");
      tokenNameInput.focus();
    });
    closeTokenModal.addEventListener("click", closeTokenCreator);
    cancelTokenModal.addEventListener("click", closeTokenCreator);
    tokenModal.addEventListener("click", (event) => { if (event.target === tokenModal) closeTokenCreator(); });
    closeModelPricingModalButton?.addEventListener("click", closeModelPricingModal);
    modelPricingModal?.addEventListener("click", (event) => { if (event.target === modelPricingModal) closeModelPricingModal(); });
    tokenUnlimitedInput.addEventListener("change", () => { tokenQuotaInput.disabled = tokenUnlimitedInput.checked; });
    submitTokenModal.addEventListener("click", async () => {
      const name = tokenNameInput.value.trim();
      if (!name) { alert("请填写令牌名称。"); tokenNameInput.focus(); return; }
      const expiresAt = tokenExpiryInput.value ? Math.floor(new Date(tokenExpiryInput.value).getTime() / 1000) : null;
      const payload = {
        name,
        group: tokenGroupInput.value.trim() || "default",
        count: Number(tokenCountInput.value || 1),
        expiresAt,
        quota: tokenQuotaInput.value || "0",
        unlimitedQuota: tokenUnlimitedInput.checked,
        allowedModels: tokenModelsInput.value,
        ipAllowlist: tokenIpInput.value
      };
      submitTokenModal.disabled = true;
      try {
        const data = await apiRequest("/api/tokens", { method: "POST", body: JSON.stringify(payload) });
        const items = data.items || [data];
        const cachedTokens = readTokenCache();
        items.forEach((item) => { if (item.id && item.token) cachedTokens[item.id] = item.token; });
        writeTokenCache(cachedTokens);
        activeApiKey = items[0].token || "";
        localStorage.setItem("nbapi-active-api-key", activeApiKey);
        closeTokenCreator();
        alert(`成功创建 ${items.length} 个令牌。完整 Key 已保存，可在令牌管理列表中继续复制；不要公开给他人。\n\n${items.map((item) => `${item.name}: ${item.token}`).join("\n")}`);
        loadTokens();
      } catch (error) { alert(error.message); } finally { submitTokenModal.disabled = false; }
    });

    document.querySelectorAll(".admin-only").forEach((item) => {
      item.addEventListener("click", (event) => {
        if (!canManage) {
          event.preventDefault();
          alert("该页面仅管理员可用，请先登录管理员账号。");
        }
      });
    });

    modelSearch.addEventListener("input", renderModelSquare);
    copyVisibleModels.addEventListener("click", () => {
      const query = (modelSearch.value || "").trim().toLowerCase();
      const names = documentedModels.map(getModelMeta).filter((model) => `${model.name} ${model.providerLabel} ${model.provider} ${model.kind} ${model.tags.join(" ")} ${model.endpointType}`.toLowerCase().includes(query)).map((model) => model.name);
      copyModelName(names.join("\n"));
    });

    saveUpstreamApiKey?.addEventListener("click", async () => {
      await saveUpstreamKey(upstreamApiKey.value);
    });

    clearUpstreamApiKey?.addEventListener("click", async () => {
      if (!confirm("确定要清空服务器里保存的上游 API Key 吗？")) return;
      await saveUpstreamKey("");
    });
    addAnnouncement?.addEventListener("click", () => {
      if (!isSuperAdmin) return;
      announcements.push({ title: "", detail: "", badge: "新", tone: "blue", active: true });
      renderAnnouncementEditor();
      announcementEditorList?.querySelector("[data-announcement-title]")?.focus();
    });
    saveAnnouncements?.addEventListener("click", async () => {
      if (!isSuperAdmin || !sessionToken) return;
      const items = Array.from(announcementEditorList?.querySelectorAll("[data-announcement-index]") || []).map((card) => ({
        title: card.querySelector("[data-announcement-title]").value.trim(),
        detail: card.querySelector("[data-announcement-detail]").value.trim(),
        badge: card.querySelector("[data-announcement-badge]").value.trim(),
        tone: card.querySelector("[data-announcement-tone]").value,
        active: card.querySelector("[data-announcement-active]").checked
      }));
      try {
        const data = await apiRequest("/api/admin/announcements", { method: "PUT", body: JSON.stringify({ items }) });
        announcements = data.items || [];
        renderAnnouncementEditor();
        renderAnnouncements();
        showToast("公告已保存");
      } catch (error) { alert(error.message); }
    });
    refreshUsers.addEventListener("click", loadAdminUsers);
    customerManagerSelect?.addEventListener("change", loadManagerCustomers);
    refreshManagerCustomers?.addEventListener("click", loadManagerCustomers);
    generateUserCredentials.addEventListener("click", generateManagedCredentials);
    createManagedUser.addEventListener("click", createManagedAccount);
    refreshPricing.addEventListener("click", loadModelPricing);
    refreshChannels?.addEventListener("click", loadAdminChannels);
    refreshUsageLogs.addEventListener("click", loadUsageLogs);
    queryUsageLogs.addEventListener("click", () => { usageLogsPage = 1; loadUsageLogs(); });
    logScope.addEventListener("change", () => { usageLogsPage = 1; loadUsageLogs(); });
    resetUsageLogs.addEventListener("click", resetLogFilters);
    usagePageSize.addEventListener("change", () => { usageLogsPage = 1; loadUsageLogs(); });
    usagePrevPage.addEventListener("click", () => { if (usageLogsPage > 1) { usageLogsPage -= 1; loadUsageLogs(); } });
    usageNextPage.addEventListener("click", () => { if (usageLogsPage < usageLogsTotalPages) { usageLogsPage += 1; loadUsageLogs(); } });
    createChannelButton?.addEventListener("click", createChannel);
    userSearch.addEventListener("input", () => {
      usersPage = 1;
      loadAdminUsers();
    });
    clearUserSearch.addEventListener("click", () => {
      userSearch.value = "";
      usersPage = 1;
      loadAdminUsers();
    });
    prevUsersPage.addEventListener("click", () => {
      if (usersPage > 1) {
        usersPage -= 1;
        loadAdminUsers();
      }
    });
    nextUsersPage.addEventListener("click", () => {
      if (usersPage < usersTotalPages) {
        usersPage += 1;
        loadAdminUsers();
      }
    });
    document.querySelectorAll("[data-filter-group]").forEach((button) => {
      button.addEventListener("click", () => {
        const group = button.dataset.filterGroup;
        selectedFilters[group] = button.dataset.filter;
        document.querySelectorAll(`[data-filter-group="${group}"]`).forEach((item) => item.classList.toggle("active", item === button));
        renderModelSquare();
      });
    });
    resetPlazaFilters.addEventListener("click", () => {
      modelSearch.value = "";
      Object.assign(selectedFilters, { provider: "all", billing: "all", kind: "all", tag: "all", endpoint: "all" });
      document.querySelectorAll("[data-filter-group]").forEach((item) => item.classList.toggle("active", item.dataset.filter === "all"));
      renderModelSquare();
    });
    plazaPriceToggle.addEventListener("click", () => {
      showPlazaPrices = !showPlazaPrices;
      plazaPriceToggle.textContent = showPlazaPrices ? "隐藏价格" : "显示价格";
      renderModelSquare();
    });
    plazaModeToggle.addEventListener("click", () => {
      compactPlaza = !compactPlaza;
      plazaModeToggle.textContent = compactPlaza ? "标准视图" : "紧凑视图";
      renderModelSquare();
    });
    populatePlaygroundModels();
    [[playgroundTemperature, "temperatureValue"], [playgroundTopP, "topPValue"], [playgroundFrequencyPenalty, "frequencyValue"], [playgroundPresencePenalty, "presenceValue"]].forEach(([input, outputId]) => {
      input.addEventListener("input", () => { document.getElementById(outputId).textContent = Number(input.value).toFixed(1); });
    });
    playgroundToken.addEventListener("change", () => { activeApiKey = playgroundToken.value; });
    playgroundModel.addEventListener("change", updatePlaygroundControls);
    sendPlayground.addEventListener("click", runPlayground);
    playgroundPrompt.addEventListener("keydown", (event) => { if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) { event.preventDefault(); runPlayground(); } });
    clearPlayground.addEventListener("click", () => {
      playgroundConversation = [];
      playgroundMessages.innerHTML = "<div class=\"playground-message assistant\">您好，我是牛B的模型操练场，左侧选择模型和相关参数，说出你的要求，我随时为你服务。（发送快捷键 Ctrl+Enter）</div>";
      playgroundStatus.textContent = "选择令牌和模型后即可开始真实测试。";
    });
    submitTopup.addEventListener("click", async () => {
      if (!currentUser) { alert("请先登录。"); return; }
      if (!topupAmount.value) { alert("请选择充值金额。"); return; }
      submitTopup.disabled = true;
      walletStatus.textContent = "正在创建支付订单...";
      try {
        const data = await apiRequest("/api/wallet/orders", { method: "POST", body: JSON.stringify({ amount: topupAmount.value, paymentMethod: topupPaymentMethod.value }) });
        topupAmount.value = "";
        if (!data.paymentUrl) throw new Error("支付地址生成失败");
        walletStatus.textContent = "正在跳转支付宝...";
        window.location.href = data.paymentUrl;
      } catch (error) {
        walletStatus.textContent = `创建订单失败：${error.message}`;
        alert(error.message);
        submitTopup.disabled = false;
      }
    });
    queryConsumption.addEventListener("click", () => loadWallet());

    setTheme(localStorage.getItem(storageKeys.theme) || "light");
    updateBalance();
    renderPrices();
    loadAnnouncements();
    loadModelCatalog();
    renderDocsModelList();
    loadDashboard();
    applyRoute();
    loadCurrentSession().then(() => { loadDashboard(); loadWallet(); applyRoute(); });
