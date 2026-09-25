/**
 * MarketPulse Interactive Application State & Reactive Controller
 */

// Bilingual Translation Dictionary (TR / EN)
const I18N = {
    tr: {
        brand: "MarketPulse",
        tagline: "Akıllı Finans, Hisse & Kripto İstihbarat Platformu",
        searchPlaceholder: "Hisse veya kripto sembolü ara (örn: THYAO, BTC, ASELS, NVDA)...",
        allAssets: "Tümü",
        bistAssets: "BIST Hisseleri",
        cryptoAssets: "Kripto Paralar",
        globalAssets: "Küresel (US)",
        portfolioTab: "Portföyüm",
        newsTab: "Haber & Duygu",
        alertsTab: "Alarmlar",
        addAssetBtn: "+ Varlık Ekle",
        price: "Fiyat",
        change24h: "24s Değişim",
        volume: "Hacim",
        marketCap: "Piyasa Değeri",
        peRatio: "F/K Oranı",
        pbRatio: "PD/DD",
        trend: "Trend Sinyali",
        bullish: "Yükseliş (Boğa)",
        bearish: "Düşüş (Ayı)",
        neutral: "Nötr / Yatay",
        details: "Detay / Grafik",
        timeframe1D: "1G",
        timeframe1W: "1H",
        timeframe1M: "1A",
        timeframe1Y: "1Y",
        totalPortfolioVal: "Toplam Portföy Değeri",
        totalProfitLoss: "Toplam Kâr / Zarar",
        assetAllocation: "Varlık Dağılımı",
        myPositions: "Açık Pozisyonlarım",
        symbol: "Sembol",
        quantity: "Miktar",
        buyPrice: "Alış Fiyatı",
        currentVal: "Güncel Değer",
        pnl: "Kâr / Zarar",
        actions: "İşlem",
        noPositionsYet: "Henüz portföyünüze varlık eklemediniz.",
        addPositionModalTitle: "Portföye Varlık Ekle",
        targetPrice: "Hedef Fiyat",
        condition: "Koşul",
        above: "Üstüne Çıkarsa (>=)",
        below: "Altına Düşerse (<=)",
        saveAlertBtn: "Alarmı Kaydet",
        createAlertModalTitle: "Fiyat Alarmı Kur",
        sentimentScore: "Duygu Skoru",
        latestNews: "Piyasa Haberleri & KAP Bildirimleri",
        source: "Kaynak",
        searchSuggestions: "Önerilen Popüler Varlıklar:",
        noSearchResults: "Eşleşen doğrulanmış hisse veya coin bulunamadı.",
        alertTriggered: "TETİKLENDİ 🚨",
        alertWaiting: "Bekliyor ⏳",
        deleteConfirm: "Bu kaydı silmek istediğinize emin misiniz?",
        notes: "Notlar",
        save: "Kaydet",
        cancel: "İptal",
    },
    en: {
        brand: "MarketPulse",
        tagline: "Intelligent Finance, Equities & Crypto Intelligence Platform",
        searchPlaceholder: "Search stock or crypto symbol (e.g. THYAO, BTC, ASELS, NVDA)...",
        allAssets: "All",
        bistAssets: "BIST Stocks",
        cryptoAssets: "Crypto Assets",
        globalAssets: "Global (US)",
        portfolioTab: "My Portfolio",
        newsTab: "News & Sentiment",
        alertsTab: "Alerts",
        addAssetBtn: "+ Add Asset",
        price: "Price",
        change24h: "24h Change",
        volume: "Volume",
        marketCap: "Market Cap",
        peRatio: "P/E Ratio",
        pbRatio: "P/B Ratio",
        trend: "Trend Signal",
        bullish: "Bullish",
        bearish: "Bearish",
        neutral: "Neutral",
        details: "Detail / Chart",
        timeframe1D: "1D",
        timeframe1W: "1W",
        timeframe1M: "1M",
        timeframe1Y: "1Y",
        totalPortfolioVal: "Total Portfolio Value",
        totalProfitLoss: "Total Profit / Loss",
        assetAllocation: "Asset Allocation",
        myPositions: "Open Positions",
        symbol: "Symbol",
        quantity: "Quantity",
        buyPrice: "Buy Price",
        currentVal: "Current Value",
        pnl: "Profit / Loss",
        actions: "Actions",
        noPositionsYet: "You have not added any assets to your portfolio yet.",
        addPositionModalTitle: "Add Position to Portfolio",
        targetPrice: "Target Price",
        condition: "Condition",
        above: "Rises Above (>=)",
        below: "Falls Below (<=)",
        saveAlertBtn: "Save Alert",
        createAlertModalTitle: "Set Price Alert",
        sentimentScore: "Sentiment Score",
        latestNews: "Market News & Disclosure Feed",
        source: "Source",
        searchSuggestions: "Suggested Popular Assets:",
        noSearchResults: "No verified stocks or coins found matching query.",
        alertTriggered: "TRIGGERED 🚨",
        alertWaiting: "Active ⏳",
        deleteConfirm: "Are you sure you want to delete this record?",
        notes: "Notes",
        save: "Save",
        cancel: "Cancel",
    },
};

// Global App State
const state = {
    lang: localStorage.getItem("marketpulse_lang") || "tr",
    activeTab: "all",
    assets: [],
    watchlist: new Set(),
    activeChart: null,
    activeTimeframe: "1M",
    selectedSymbol: null,
    searchDebounceTimer: null,
};

function t(key) {
    return I18N[state.lang][key] || key;
}

function setLanguage(lang) {
    state.lang = lang;
    localStorage.setItem("marketpulse_lang", lang);
    updateLanguageUI();
    renderMainView();
}

function updateLanguageUI() {
    document.querySelectorAll("[data-i18n]").forEach((el) => {
        const key = el.getAttribute("data-i18n");
        if (el.tagName === "INPUT") {
            el.placeholder = t(key);
        } else {
            el.textContent = t(key);
        }
    });

    const btnTr = document.getElementById("lang-btn-tr");
    const btnEn = document.getElementById("lang-btn-en");
    if (btnTr && btnEn) {
        if (state.lang === "tr") {
            btnTr.className = "px-2.5 py-1 rounded bg-blue-600 text-white font-medium text-xs shadow";
            btnEn.className = "px-2.5 py-1 rounded text-gray-400 hover:text-white text-xs";
        } else {
            btnEn.className = "px-2.5 py-1 rounded bg-blue-600 text-white font-medium text-xs shadow";
            btnTr.className = "px-2.5 py-1 rounded text-gray-400 hover:text-white text-xs";
        }
    }
}

// Formatters
function formatCurrency(val, curr = "TRY") {
    if (val === null || val === undefined) return "-";
    const symbol = curr === "USD" ? "$" : (curr === "%" ? "%" : "₺");
    if (val >= 1e9) {
        return `${symbol}${(val / 1e9).toFixed(2)}B`;
    }
    if (val >= 1e6) {
        return `${symbol}${(val / 1e6).toFixed(2)}M`;
    }
    return `${symbol}${val.toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

// Load Headline Market Indicators
async function loadIndices() {
    try {
        const res = await fetch("/api/indices");
        const data = await res.json();
        const container = document.getElementById("ticker-bar");
        if (!container) return;

        container.innerHTML = data.map((item) => {
            const isPos = item.change_pct >= 0;
            const sign = isPos ? "+" : "";
            const color = isPos ? "text-emerald-400" : "text-rose-400";
            return `
                <div class="flex items-center space-x-2 text-xs font-mono py-1 px-3 border-r border-gray-800 shrink-0">
                    <span class="text-gray-400 font-semibold">${item.symbol}</span>
                    <span class="text-gray-200 font-medium">${item.value.toLocaleString("tr-TR")}</span>
                    <span class="${color} font-bold">${sign}${item.change_pct}%</span>
                </div>
            `;
        }).join("");
    } catch (e) {
        console.error("Failed to load indices", e);
    }
}

// Load Watchlist
async function loadWatchlist() {
    try {
        const res = await fetch("/api/watchlist");
        const symbols = await res.json();
        state.watchlist = new Set(symbols);
    } catch (e) {
        console.error("Failed to load watchlist", e);
    }
}

// Load Assets Grid
async function loadAssets(type = "all") {
    const grid = document.getElementById("assets-grid");
    if (!grid) return;
    grid.innerHTML = `<div class="col-span-full py-12 text-center text-gray-400 font-mono text-sm animate-pulse">Yükleniyor / Loading...</div>`;

    try {
        const res = await fetch(`/api/assets?type=${type}`);
        state.assets = await res.json();
        renderAssetsGrid(state.assets);
    } catch (e) {
        grid.innerHTML = `<div class="col-span-full py-12 text-center text-rose-400 font-mono text-sm">Veri yüklenemedi: ${e}</div>`;
    }
}

function renderAssetsGrid(assets) {
    const grid = document.getElementById("assets-grid");
    if (!grid) return;

    if (!assets || assets.length === 0) {
        grid.innerHTML = `<div class="col-span-full py-12 text-center text-gray-500 font-mono text-sm">Kayıtlı varlık bulunamadı.</div>`;
        return;
    }

    grid.innerHTML = assets.map((a) => {
        const isPos = a.change_pct_24h >= 0;
        const sign = isPos ? "+" : "";
        const color = isPos ? "text-emerald-400" : "text-rose-400";
        const bgBadge = isPos ? "bg-emerald-950/60 text-emerald-400 border-emerald-800/40" : "bg-rose-950/60 text-rose-400 border-rose-800/40";
        const isStar = state.watchlist.has(a.symbol);

        const typeBadge = a.asset_type === "bist" 
            ? '<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-blue-900/60 text-blue-300 border border-blue-700/50">BIST</span>'
            : a.asset_type === "crypto"
            ? '<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-900/60 text-amber-300 border border-amber-700/50">CRYPTO</span>'
            : '<span class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-purple-900/60 text-purple-300 border border-purple-700/50">NASDAQ</span>';

        const desc = state.lang === "tr" ? a.description_tr : a.description_en;

        return `
            <div class="glass-panel p-4 rounded-xl border border-gray-800/80 shimmer-card cursor-pointer flex flex-col justify-between" onclick="openChartModal('${a.symbol}')">
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center space-x-2">
                            ${typeBadge}
                            <span class="font-bold text-white tracking-wide text-base">${a.symbol}</span>
                            <span class="text-xs text-gray-400 truncate max-w-[130px]">${a.name}</span>
                        </div>
                        <button onclick="event.stopPropagation(); toggleWatchlist('${a.symbol}')" class="text-gray-500 hover:text-amber-400 transition">
                            <span class="${isStar ? 'text-amber-400' : 'text-gray-600'} text-lg">★</span>
                        </button>
                    </div>

                    <p class="text-xs text-gray-400 line-clamp-2 mb-3 min-h-[32px]">${desc}</p>
                </div>

                <div class="pt-3 border-t border-gray-800/60">
                    <div class="flex items-baseline justify-between">
                        <span class="text-lg font-bold text-white font-mono">${formatCurrency(a.current_price, a.currency)}</span>
                        <span class="px-2 py-0.5 rounded text-xs font-mono font-bold border ${bgBadge}">${sign}${a.change_pct_24h}%</span>
                    </div>

                    <div class="grid grid-cols-2 gap-2 mt-2.5 text-[11px] text-gray-400 font-mono">
                        <div><span class="text-gray-500">${t('volume')}:</span> ${formatCurrency(a.volume_24h, a.currency)}</div>
                        <div class="text-right"><span class="text-gray-500">RSI:</span> <span class="${a.rsi_14 > 70 ? 'text-rose-400' : (a.rsi_14 < 35 ? 'text-emerald-400' : 'text-gray-300')}">${a.rsi_14}</span></div>
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

// Strict Search with suggestions
function onSearchInput(val) {
    clearTimeout(state.searchDebounceTimer);
    const box = document.getElementById("search-results-box");
    if (!val || val.trim().length === 0) {
        if (box) box.classList.add("hidden");
        return;
    }

    state.searchDebounceTimer = setTimeout(async () => {
        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(val.trim())}&type=${state.activeTab}`);
            const data = await res.json();
            renderSearchResults(data);
        } catch (e) {
            console.error("Search error", e);
        }
    }, 200);
}

function renderSearchResults(data) {
    const box = document.getElementById("search-results-box");
    if (!box) return;

    box.classList.remove("hidden");

    if (data.total_matches === 0) {
        const msg = state.lang === "tr" ? data.message_tr : data.message_en;
        const chips = (data.suggestions || []).map((s) => `
            <button onclick="selectSearchSymbol('${s}')" class="px-2.5 py-1 bg-gray-800 hover:bg-blue-600 text-gray-200 text-xs rounded font-mono font-bold transition">
                ${s}
            </button>
        `).join("");

        box.innerHTML = `
            <div class="p-4 text-center">
                <p class="text-xs text-rose-400 font-medium mb-2">${msg}</p>
                ${chips ? `<div class="text-[11px] text-gray-400 mb-1.5">${t('searchSuggestions')}</div><div class="flex flex-wrap gap-1.5 justify-center">${chips}</div>` : ''}
            </div>
        `;
        return;
    }

    box.innerHTML = data.results.map((item) => `
        <div onclick="selectSearchSymbol('${item.symbol}')" class="p-3 hover:bg-gray-800/80 cursor-pointer border-b border-gray-800 last:border-none flex items-center justify-between transition">
            <div class="flex items-center space-x-2">
                <span class="font-bold text-white font-mono text-sm">${item.symbol}</span>
                <span class="text-xs text-gray-400">${item.name}</span>
            </div>
            <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 uppercase">${item.asset_type}</span>
        </div>
    `).join("");
}

function selectSearchSymbol(sym) {
    const box = document.getElementById("search-results-box");
    if (box) box.classList.add("hidden");
    const input = document.getElementById("main-search-input");
    if (input) input.value = sym;
    openChartModal(sym);
}

// Watchlist toggle
async function toggleWatchlist(sym) {
    try {
        const res = await fetch("/api/watchlist/toggle", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol: sym }),
        });
        const data = await res.json();
        if (data.is_in_watchlist) {
            state.watchlist.add(sym);
        } else {
            state.watchlist.delete(sym);
        }
        if (state.activeTab === "watchlist") {
            renderWatchlist();
        } else {
            renderAssetsGrid(state.assets);
        }
    } catch (e) {
        console.error("Watchlist error", e);
    }
}

// Interactive Chart Modal
async function openChartModal(symbol, timeframe = "1M") {
    state.selectedSymbol = symbol;
    state.activeTimeframe = timeframe;

    const modal = document.getElementById("chart-modal");
    if (!modal) return;
    modal.classList.remove("hidden");

    document.getElementById("modal-symbol").textContent = symbol;
    document.getElementById("modal-quote-details").innerHTML = `<span class="animate-pulse">Veri alınıyor...</span>`;

    // Fetch quote
    const qRes = await fetch(`/api/assets/${symbol}`);
    const assetData = await qRes.json();

    const isPos = assetData.change_pct_24h >= 0;
    const sign = isPos ? "+" : "";
    const color = isPos ? "text-emerald-400" : "text-rose-400";
    const desc = state.lang === "tr" ? assetData.description_tr : assetData.description_en;

    document.getElementById("modal-title").textContent = assetData.name;
    document.getElementById("modal-quote-details").innerHTML = `
        <div class="flex items-baseline space-x-3 mb-1">
            <span class="text-2xl font-bold font-mono text-white">${formatCurrency(assetData.current_price, assetData.currency)}</span>
            <span class="text-sm font-bold font-mono ${color}">${sign}${assetData.change_pct_24h}%</span>
        </div>
        <p class="text-xs text-gray-400 line-clamp-2">${desc}</p>
        <div class="flex flex-wrap gap-4 mt-3 text-xs text-gray-300 font-mono">
            <div><span class="text-gray-500">${t('peRatio')}:</span> ${assetData.pe_ratio || '-'}</div>
            <div><span class="text-gray-500">${t('pbRatio')}:</span> ${assetData.pb_ratio || '-'}</div>
            <div><span class="text-gray-500">RSI (14):</span> ${assetData.rsi_14}</div>
            <div><span class="text-gray-500">${t('trend')}:</span> <span class="font-bold ${color}">${assetData.trend}</span></div>
        </div>
    `;

    // Fetch chart points
    const cRes = await fetch(`/api/chart/${symbol}?timeframe=${timeframe}`);
    const chartData = await cRes.json();
    renderChart(chartData.points, isPos);

    // Update active timeframe button styles
    ["1D", "1W", "1M", "1Y"].forEach((tf) => {
        const btn = document.getElementById(`tf-btn-${tf}`);
        if (btn) {
            btn.className = tf === timeframe 
                ? "px-3 py-1 bg-blue-600 text-white rounded text-xs font-bold" 
                : "px-3 py-1 bg-gray-800 text-gray-400 hover:text-white rounded text-xs font-bold";
        }
    });
}

function renderChart(points, isPositive) {
    const ctx = document.getElementById("price-chart-canvas").getContext("2d");
    if (state.activeChart) {
        state.activeChart.destroy();
    }

    const labels = points.map((p) => p.time);
    const data = points.map((p) => p.price);

    const strokeColor = isPositive ? "#10b981" : "#f43f5e";
    const fillColor = isPositive ? "rgba(16, 185, 129, 0.12)" : "rgba(244, 63, 94, 0.12)";

    state.activeChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    data: data,
                    borderColor: strokeColor,
                    backgroundColor: fillColor,
                    fill: true,
                    tension: 0.25,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: strokeColor,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: "index",
                    intersect: false,
                    backgroundColor: "#1e293b",
                    titleColor: "#94a3b8",
                    bodyColor: "#ffffff",
                    borderColor: "#334155",
                    borderWidth: 1,
                    callbacks: {
                        label: (ctx) => ` Fiyat: ${ctx.parsed.y.toLocaleString("tr-TR")}`,
                    },
                },
            },
            scales: {
                x: {
                    grid: { color: "rgba(255,255,255,0.03)" },
                    ticks: { color: "#64748b", font: { size: 10 } },
                },
                y: {
                    grid: { color: "rgba(255,255,255,0.05)" },
                    ticks: { color: "#64748b", font: { size: 10 } },
                },
            },
        },
    });
}

function closeChartModal() {
    const modal = document.getElementById("chart-modal");
    if (modal) modal.classList.add("hidden");
    if (state.activeChart) {
        state.activeChart.destroy();
        state.activeChart = null;
    }
}

// Portfolio View
async function renderPortfolioView() {
    const main = document.getElementById("content-area");
    main.innerHTML = `<div class="p-8 text-center text-gray-400 font-mono animate-pulse">Portföy hesaplanıyor...</div>`;

    try {
        const res = await fetch("/api/portfolio");
        const data = await res.json();

        const isPos = data.total_pnl_try >= 0;
        const sign = isPos ? "+" : "";
        const color = isPos ? "text-emerald-400" : "text-rose-400";

        main.innerHTML = `
            <div class="space-y-6">
                <!-- Summary Metrics Cards -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="glass-panel p-5 rounded-xl border border-gray-800">
                        <div class="text-xs text-gray-400 font-medium mb-1">${t('totalPortfolioVal')}</div>
                        <div class="text-2xl font-bold font-mono text-white">${formatCurrency(data.total_value_try, 'TRY')}</div>
                        <div class="text-xs text-gray-400 font-mono mt-1">≈ ${formatCurrency(data.total_value_usd, 'USD')}</div>
                    </div>

                    <div class="glass-panel p-5 rounded-xl border border-gray-800">
                        <div class="text-xs text-gray-400 font-medium mb-1">${t('totalProfitLoss')}</div>
                        <div class="text-2xl font-bold font-mono ${color}">${sign}${formatCurrency(data.total_pnl_try, 'TRY')}</div>
                        <div class="text-xs font-bold font-mono ${color} mt-1">${sign}${data.total_pnl_pct}%</div>
                    </div>

                    <div class="glass-panel p-5 rounded-xl border border-gray-800">
                        <div class="text-xs text-gray-400 font-medium mb-1">${t('assetAllocation')}</div>
                        <div class="flex items-center space-x-3 mt-2 text-xs font-mono">
                            <span class="text-blue-400">BIST: %${data.allocation_pct.bist || 0}</span>
                            <span class="text-amber-400">CRYPTO: %${data.allocation_pct.crypto || 0}</span>
                            <span class="text-purple-400">GLOBAL: %${data.allocation_pct.global || 0}</span>
                        </div>
                    </div>
                </div>

                <!-- Position List Table -->
                <div class="glass-panel rounded-xl border border-gray-800 overflow-hidden">
                    <div class="p-4 border-b border-gray-800 flex items-center justify-between">
                        <h3 class="font-bold text-white text-base">${t('myPositions')} (${data.positions_count})</h3>
                        <button onclick="openAddPositionModal()" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold transition">
                            ${t('addAssetBtn')}
                        </button>
                    </div>

                    ${data.positions.length === 0 ? `
                        <div class="p-8 text-center text-gray-500 font-mono text-xs">${t('noPositionsYet')}</div>
                    ` : `
                        <div class="overflow-x-auto">
                            <table class="w-full text-left text-xs font-mono">
                                <thead class="bg-gray-900/60 text-gray-400 uppercase border-b border-gray-800">
                                    <tr>
                                        <th class="p-3">${t('symbol')}</th>
                                        <th class="p-3">${t('quantity')}</th>
                                        <th class="p-3">${t('buyPrice')}</th>
                                        <th class="p-3">${t('currentVal')}</th>
                                        <th class="p-3">${t('pnl')}</th>
                                        <th class="p-3 text-right">${t('actions')}</th>
                                    </tr>
                                </thead>
                                <tbody class="divide-y divide-gray-800">
                                    ${data.positions.map((p) => {
                                        const pnlPos = p.pnl_amount >= 0;
                                        const pnlColor = pnlPos ? "text-emerald-400" : "text-rose-400";
                                        const pnlSign = pnlPos ? "+" : "";
                                        return `
                                            <tr class="hover:bg-gray-800/40">
                                                <td class="p-3 font-bold text-white">${p.symbol}</td>
                                                <td class="p-3">${p.quantity}</td>
                                                <td class="p-3">${formatCurrency(p.buy_price, p.currency)}</td>
                                                <td class="p-3">${formatCurrency(p.current_value, p.currency)}</td>
                                                <td class="p-3 ${pnlColor} font-bold">${pnlSign}${formatCurrency(p.pnl_amount, p.currency)} (${pnlSign}${p.pnl_pct}%)</td>
                                                <td class="p-3 text-right">
                                                    <button onclick="deletePosition(${p.id})" class="text-rose-400 hover:text-rose-300 font-bold">Sil</button>
                                                </td>
                                            </tr>
                                        `;
                                    }).join("")}
                                </tbody>
                            </table>
                        </div>
                    `}
                </div>
            </div>
        `;
    } catch (e) {
        console.error("Portfolio render error", e);
    }
}

// News & Sentiment View
async function renderNewsView() {
    const main = document.getElementById("content-area");
    main.innerHTML = `<div class="p-8 text-center text-gray-400 font-mono animate-pulse">Haberler taranıyor...</div>`;

    try {
        const res = await fetch("/api/news");
        const items = await res.json();

        main.innerHTML = `
            <div class="space-y-4">
                <div class="flex items-center justify-between mb-4">
                    <h2 class="text-lg font-bold text-white">${t('latestNews')}</h2>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    ${items.map((n) => {
                        const isBull = n.sentiment_label === "BULLISH";
                        const isBear = n.sentiment_label === "BEARISH";
                        const badgeColor = isBull 
                            ? "bg-emerald-950/80 text-emerald-400 border-emerald-800" 
                            : (isBear ? "bg-rose-950/80 text-rose-400 border-rose-800" : "bg-amber-950/80 text-amber-400 border-amber-800");
                        
                        const title = state.lang === "tr" ? n.title_tr : n.title_en;
                        const summary = state.lang === "tr" ? n.summary_tr : n.summary_en;

                        return `
                            <div class="glass-panel p-5 rounded-xl border border-gray-800 flex flex-col justify-between shimmer-card">
                                <div>
                                    <div class="flex items-center justify-between mb-2">
                                        <span class="text-[10px] font-bold px-2 py-0.5 rounded border ${badgeColor}">
                                            ${n.sentiment_label} (${n.sentiment_score > 0 ? '+' : ''}${n.sentiment_score})
                                        </span>
                                        <span class="text-xs text-gray-500 font-mono">${n.published_at}</span>
                                    </div>
                                    <h4 class="font-bold text-white text-sm leading-snug mb-2">${title}</h4>
                                    <p class="text-xs text-gray-400 leading-relaxed">${summary}</p>
                                </div>
                                <div class="mt-4 pt-3 border-t border-gray-800 flex items-center justify-between text-[11px] text-gray-400">
                                    <span>${t('source')}: <strong class="text-gray-300">${n.source}</strong></span>
                                    <div class="flex space-x-1.5">
                                        ${n.related_symbols.map((s) => `
                                            <span onclick="openChartModal('${s}')" class="cursor-pointer font-mono font-bold text-blue-400 hover:underline">#${s}</span>
                                        `).join("")}
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join("")}
                </div>
            </div>
        `;
    } catch (e) {
        console.error("News render error", e);
    }
}

// Alerts View
async function renderAlertsView() {
    const main = document.getElementById("content-area");
    main.innerHTML = `<div class="p-8 text-center text-gray-400 font-mono animate-pulse">Alarmlar kontrol ediliyor...</div>`;

    try {
        const res = await fetch("/api/alerts");
        const alerts = await res.json();

        main.innerHTML = `
            <div class="space-y-6">
                <div class="flex items-center justify-between">
                    <h2 class="text-lg font-bold text-white">${t('alertsTab')} (${alerts.length})</h2>
                    <button onclick="openCreateAlertModal()" class="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-bold transition">
                        + Yeni Fiyat Alarmı
                    </button>
                </div>

                ${alerts.length === 0 ? `
                    <div class="glass-panel p-8 text-center text-gray-500 font-mono text-xs rounded-xl border border-gray-800">
                        Aktif bir fiyat alarmınız bulunmuyor.
                    </div>
                ` : `
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        ${alerts.map((al) => `
                            <div class="glass-panel p-4 rounded-xl border border-gray-800 flex items-center justify-between">
                                <div>
                                    <div class="flex items-center space-x-2 mb-1">
                                        <span class="font-bold text-white font-mono text-base">${al.symbol}</span>
                                        <span class="text-xs text-gray-400">${al.condition === 'ABOVE' ? '>=' : '<='} ${al.target_price}</span>
                                    </div>
                                    <span class="text-[11px] font-bold ${al.is_triggered ? 'text-rose-400' : 'text-emerald-400'}">
                                        ${al.is_triggered ? t('alertTriggered') : t('alertWaiting')}
                                    </span>
                                </div>
                                <button onclick="deleteAlert(${al.id})" class="text-xs text-gray-500 hover:text-rose-400 font-bold p-1">
                                    Sil
                                </button>
                            </div>
                        `).join("")}
                    </div>
                `}
            </div>
        `;
    } catch (e) {
        console.error("Alerts render error", e);
    }
}

// Watchlist View
function renderWatchlist() {
    const list = state.assets.filter((a) => state.watchlist.has(a.symbol));
    renderAssetsGrid(list);
}

// Navigation Tab Switcher
function switchTab(tab) {
    state.activeTab = tab;

    // Update Tab UI
    document.querySelectorAll(".nav-tab").forEach((btn) => {
        if (btn.getAttribute("data-tab") === tab) {
            btn.classList.add("tab-active");
            btn.classList.remove("text-gray-400");
        } else {
            btn.classList.remove("tab-active");
            btn.classList.add("text-gray-400");
        }
    });

    renderMainView();
}

function renderMainView() {
    const content = document.getElementById("content-area");

    if (state.activeTab === "portfolio") {
        renderPortfolioView();
    } else if (state.activeTab === "news") {
        renderNewsView();
    } else if (state.activeTab === "alerts") {
        renderAlertsView();
    } else if (state.activeTab === "watchlist") {
        content.innerHTML = `<div id="assets-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>`;
        renderWatchlist();
    } else {
        // Assets view (all, bist, crypto, global)
        content.innerHTML = `<div id="assets-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>`;
        loadAssets(state.activeTab);
    }
}

// Modals: Add Position
function openAddPositionModal(prefillSymbol = "") {
    const modal = document.getElementById("add-position-modal");
    if (modal) modal.classList.remove("hidden");
    const symInput = document.getElementById("pos-symbol");
    if (symInput && prefillSymbol) symInput.value = prefillSymbol;
}

function closeAddPositionModal() {
    const modal = document.getElementById("add-position-modal");
    if (modal) modal.classList.add("hidden");
}

async function submitPositionForm(e) {
    e.preventDefault();
    const symbol = document.getElementById("pos-symbol").value;
    const qty = parseFloat(document.getElementById("pos-qty").value);
    const buyPrice = parseFloat(document.getElementById("pos-price").value);
    const notes = document.getElementById("pos-notes").value;

    try {
        const res = await fetch("/api/portfolio", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol, quantity: qty, buy_price: buyPrice, notes }),
        });
        if (!res.ok) {
            const err = await res.json();
            alert("Hata: " + err.error);
            return;
        }
        closeAddPositionModal();
        if (state.activeTab === "portfolio") {
            renderPortfolioView();
        } else {
            switchTab("portfolio");
        }
    } catch (e) {
        alert("Bağlantı hatası: " + e);
    }
}

async function deletePosition(id) {
    if (!confirm(t('deleteConfirm'))) return;
    try {
        await fetch(`/api/portfolio/${id}`, { method: "DELETE" });
        renderPortfolioView();
    } catch (e) {
        alert("Silme hatası: " + e);
    }
}

// Modals: Create Alert
function openCreateAlertModal(prefillSymbol = "") {
    const modal = document.getElementById("alert-modal");
    if (modal) modal.classList.remove("hidden");
    const symInput = document.getElementById("alert-symbol");
    if (symInput && prefillSymbol) symInput.value = prefillSymbol;
}

function closeCreateAlertModal() {
    const modal = document.getElementById("alert-modal");
    if (modal) modal.classList.add("hidden");
}

async function submitAlertForm(e) {
    e.preventDefault();
    const symbol = document.getElementById("alert-symbol").value;
    const targetPrice = parseFloat(document.getElementById("alert-price").value);
    const condition = document.getElementById("alert-condition").value;

    try {
        const res = await fetch("/api/alerts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ symbol, target_price: targetPrice, condition }),
        });
        if (!res.ok) {
            const err = await res.json();
            alert("Hata: " + err.error);
            return;
        }
        closeCreateAlertModal();
        if (state.activeTab === "alerts") {
            renderAlertsView();
        } else {
            switchTab("alerts");
        }
    } catch (e) {
        alert("Bağlantı hatası: " + e);
    }
}

async function deleteAlert(id) {
    if (!confirm(t('deleteConfirm'))) return;
    try {
        await fetch(`/api/alerts/${id}`, { method: "DELETE" });
        renderAlertsView();
    } catch (e) {
        alert("Silme hatası: " + e);
    }
}

// Global initialization
window.addEventListener("DOMContentLoaded", async () => {
    updateLanguageUI();
    await loadIndices();
    await loadWatchlist();
    renderMainView();

    // Auto-refresh headline indices every 30s
    setInterval(loadIndices, 30000);
});
