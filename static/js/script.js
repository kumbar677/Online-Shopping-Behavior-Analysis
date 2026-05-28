document.addEventListener('DOMContentLoaded', () => {
    // Add staggered fading animations
    const cards = document.querySelectorAll('.fade-in');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.15}s`;
    });

    // Theme Toggle Logic
    const toggleBtn = document.getElementById("themeToggle");
    if (toggleBtn) {
        const savedTheme = localStorage.getItem("theme");
        if (savedTheme === "light") {
            document.documentElement.classList.add("light-mode");
            toggleBtn.textContent = "☀️";
        }
        
        toggleBtn.addEventListener("click", () => {
            document.documentElement.classList.toggle("light-mode");
            const isLight = document.documentElement.classList.contains("light-mode");
            toggleBtn.textContent = isLight ? "☀️" : "🌙";
            localStorage.setItem("theme", isLight ? "light" : "dark");
        });
    }

    // Initial Data Load with filters
    checkHasData();

    // Bind Take Tour button
    const tourBtn = document.getElementById('startTourBtn');
    if (tourBtn) {
        tourBtn.addEventListener('click', () => {
            const emptyState = document.getElementById('empty-state-container');
            const hasData = emptyState && emptyState.style.display === 'none';
            startOnboarding(hasData);
        });
    }
});

function getFilterQueryParams() {
    const form = document.getElementById('dashboard-filters');
    if (!form) return '';
    const formData = new FormData(form);
    const params = new URLSearchParams();
    for (const [key, value] of formData.entries()) {
        if (value && value.trim() !== '') {
            params.append(key, value);
        }
    }
    return params.toString();
}

function applyFilters() {
    const qs = getFilterQueryParams();
    const prefix = qs ? '?' + qs : '';
    
    // Refresh charts by adding query string and timestamp (to bypass cache)
    const timestamp = new Date().getTime();
    const joiner = qs ? '&' : '?';
    
    document.querySelectorAll('.chart-card img').forEach(img => {
        const baseSrc = img.getAttribute('src').split('?')[0];
        img.src = `${baseSrc}${prefix}${joiner}t=${timestamp}`;
    });
    
    // Update Download Report endpoint matching filters
    const reportBtn = document.querySelector('a[href^="/api/download-report"]');
    if(reportBtn) {
        reportBtn.href = `/api/download-report${prefix}`;
    }
    
    const csvBtn = document.querySelector('a[href^="/api/export-csv"]');
    if(csvBtn) {
        csvBtn.href = `/api/export-csv${prefix}`;
    }
    
    loadDashboardData(prefix);
}

function clearFilters() {
    document.getElementById('dashboard-filters').reset();
    applyFilters();
}

function checkHasData() {
    fetch('/api/has-data')
        .then(res => res.json())
        .then(data => {
            const hasData = data.has_data;
            const emptyState = document.getElementById('empty-state-container');
            const dashboardElements = document.querySelectorAll('.filter-bar, .metrics-grid, .tab-content, .sidebar nav');
            const actionButtons = document.querySelectorAll('.header-right a, .btn-refresh[onclick="refreshData()"]');
            
            if (!hasData) {
                if (emptyState) emptyState.style.display = 'block';
                dashboardElements.forEach(el => el.style.display = 'none');
                actionButtons.forEach(el => el.style.display = 'none');
            } else {
                if (emptyState) emptyState.style.display = 'none';
                dashboardElements.forEach(el => el.style.display = '');
                actionButtons.forEach(el => el.style.display = '');
                applyFilters();
                fetchDateRange();
            }
            
            // Auto-start onboarding if first time
            const hasSeenTour = localStorage.getItem('hasSeenTour_' + hasData);
            if (!hasSeenTour) {
                setTimeout(() => {
                    if (window.driver) {
                        startOnboarding(hasData);
                        localStorage.setItem('hasSeenTour_' + hasData, 'true');
                    }
                }, 1500);
            }
        })
        .catch(err => console.error("Error checking data:", err));
}

function refreshData() {
    const btn = document.querySelector('.fa-rotate-right').parentElement;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Refreshing...';
    
    document.querySelectorAll('.fade-in').forEach(el => el.style.opacity = '0.5');
    
    applyFilters();
    
    setTimeout(() => {
        btn.innerHTML = '<i class="fa-solid fa-rotate-right"></i> Refresh';
        document.querySelectorAll('.fade-in').forEach(el => el.style.opacity = '1');
    }, 800);
}

function fetchDateRange() {
    fetch('/api/date-range')
        .then(res => res.json())
        .then(data => {
            const indicator = document.getElementById('date-range-indicator');
            if (indicator && data.min_date && data.max_date) {
                indicator.innerText = `(Available: ${data.min_date} to ${data.max_date})`;
                
                const startInput = document.getElementById('f_start_date');
                const endInput = document.getElementById('f_end_date');
                if (startInput && !startInput.value) startInput.value = data.min_date;
                if (endInput && !endInput.value) endInput.value = data.max_date;
            }
        })
        .catch(err => console.error("Error fetching date range:", err));
}

function loadDashboardData(qs = '') {
    // Determine overall stats from the api (like age analysis)
    fetch('/api/age-analysis' + qs)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.getElementById('age-table-body');
            tableBody.innerHTML = '';
            
            if (data && data.length > 0) {
                data.forEach(row => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${row.age_group}</strong></td>
                        <td>${row.num_orders.toLocaleString()}</td>
                        <td style="color: #10b981; font-weight: 600;">$${row.total_revenue.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    `;
                    tableBody.appendChild(tr);
                });
            } else {
                tableBody.innerHTML = '<tr><td colspan="3" style="text-align:center;">No data available</td></tr>';
            }

            fetchKPIs(qs);
            fetchPaymentStat(qs);
            fetchAssociationRules(qs);
            fetchRFMAnalysis(qs);
            fetchSVDPersonas(qs);
            fetchChurnRisk(qs);
            fetchCustomerSimilarity(qs);
            fetchAgeProductPreferences(qs);
            fetchStockStatus();
            fetchRestockRecommendations(qs);
            fetchSeasonalSales(qs);
            fetchSalesGrowthRecommendations(qs);
            fetchLTVPrediction(qs);
            fetchSimulationBaseline(qs);
            
            // Client-Side Chart.js Rendering Triggers Native
            renderTrendChart(qs);
            renderTopProductsChart(qs);
            renderCategoryChart(qs);
            renderPaymentChart(qs);
        })
        .catch(err => console.error("Error fetching age analysis:", err));
}

function fetchAssociationRules(qs = '') {
    fetch('/api/association-rules' + qs)
        .then(res => res.json())
        .then(data => {
            const tableBody = document.getElementById('rules-table-body');
            tableBody.innerHTML = '';
            if (data && data.length > 0) {
                data.slice(0, 6).forEach(rule => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${rule.antecedents}</td>
                        <td><strong style="color: var(--accent-purple);">${rule.consequents}</strong></td>
                        <td style="font-size:0.88rem; color:var(--text-secondary); max-width:250px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${rule.buyers || ''}">${rule.buyers || '—'}</td>
                        <td>${(rule.confidence * 100).toFixed(1)}%</td>
                    `;
                    tableBody.appendChild(tr);
                });
            } else {
                tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No strong purchasing correlations found natively in dataset.</td></tr>';
            }
        })
        .catch(err => {
            console.error("Error fetching rules:", err);
            const tableBody = document.getElementById('rules-table-body');
            if(tableBody) tableBody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:red;">Failed to Load rules.</td></tr>';
        });
}

function fetchPaymentStat(qs = '') {
    fetch('/api/payment-analysis' + qs)
        .then(res => res.json())
        .then(data => {
            if (data && data.length > 0) {
                // Assuming ordered by num_transactions descending
                const topMethod = data[0].payment_method;
                const el = document.getElementById('top-payment-stat');
                el.innerText = topMethod;
                el.classList.remove('loading-pulse');
            }
        });
}

function fetchChurnRisk(qs = '') {
    fetch('/api/churn-risk' + qs)
        .then(res => res.json())
        .then(data => {
            const tableBody = document.getElementById('churn-table-body');
            if(!tableBody) return;
            tableBody.innerHTML = '';
            if (data && data.length > 0) {
                data.forEach(user => {
                    let statusColor = '';
                    if(user.status === 'Churned') statusColor = 'color: #ef4444; font-weight: bold;';
                    else if(user.status === 'Dormant') statusColor = 'color: #ea580c; font-weight: bold;';
                    else statusColor = 'color: #eab308; font-weight: bold;';

                    const safeUser = JSON.stringify({
                        customer_name: user.customer_name,
                        email: user.email,
                        days_absent: user.days_absent,
                        total_spent: user.total_spent,
                        status: user.status,
                        interested_product: user.interested_product,
                        recommended_product: user.recommended_product,
                        discount: user.discount,
                        coupon_code: user.coupon_code
                    }).replace(/'/g, "&apos;");

                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${user.customer_name}</strong></td>
                        <td>${user.days_absent} days</td>
                        <td>$${user.total_spent.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                        <td style="${statusColor}">${user.status}</td>
                        <td><span style="color:var(--text-secondary);font-size:0.88rem;">${user.interested_product || '—'}</span></td>
                        <td><strong style="color:var(--accent-blue);font-size:0.88rem;">${user.recommended_product || '—'}</strong></td>
                        <td style="font-size: 0.9em; opacity: 0.9;">${user.action}</td>
                        <td>
                            <button class="btn-send-mail" onclick='openEmailPreview(${safeUser})'>
                                <i class="fa-solid fa-envelope"></i> Send Mail
                            </button>
                        </td>
                    `;
                    tableBody.appendChild(tr);
                });
            } else {
                tableBody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding: 20px;">No at-risk customers identified.<br><span style="color: #10b981; font-weight: bold;">Customer retention is healthy.</span></td></tr>';
            }
        })
        .catch(err => {
            console.error("Error fetching churn:", err);
            const tb = document.getElementById('churn-table-body');
            if(tb) tb.innerHTML = '<tr><td colspan="8" style="text-align:center;color:red;">Failed to Load Churn Risk.</td></tr>';
        });
}

function fetchKPIs(qs = '') {
    fetch('/api/kpis' + qs)
        .then(res => res.json())
        .then(data => {
            const tOrdersEl = document.getElementById('total-orders-stat');
            const tRevEl = document.getElementById('total-revenue-stat');
            const tUsersEl = document.getElementById('total-users-stat');
            
            if(tOrdersEl) {
                tOrdersEl.innerText = parseInt(data.orders).toLocaleString();
                tOrdersEl.classList.remove('loading-pulse');
            }
            if(tRevEl) {
                tRevEl.innerText = '$' + parseFloat(data.revenue).toLocaleString(undefined, {minimumFractionDigits: 2});
                tRevEl.classList.remove('loading-pulse');
            }
            if(tUsersEl) {
                tUsersEl.innerText = parseInt(data.customers).toLocaleString();
                tUsersEl.classList.remove('loading-pulse');
            }
        })
        .catch(err => console.error("Error fetching KPIs:", err));
}

function fetchRFMAnalysis(qs = '') {
    fetch('/api/rfm-analysis' + qs)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('rfm-table-body');
            tbody.innerHTML = '';
            if (data && data.length > 0) {
                data.forEach(customer => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${customer.name}</strong></td>
                        <td>${customer.recency}</td>
                        <td>${customer.frequency}</td>
                        <td>$${customer.monetary.toLocaleString()}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;">No data available.</td></tr>';
            }
        })
        .catch(err => console.error(err));
}

function fetchSVDPersonas(qs = '') {
    fetch('/api/svd-personas' + qs)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('svd-table-body');
            tbody.innerHTML = '';
            if (data && data.length > 0) {
                data.forEach(persona => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${persona.persona_id}</strong></td>
                        <td>${persona.strength_pct}%</td>
                        <td style="color:var(--accent-pink);">${persona.key_products}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="3" style="text-align:center;">Not enough variance for grouping.</td></tr>';
            }
        })
        .catch(err => console.error(err));
}

// Navigation highlighting & Tab Switching
const navItems = document.querySelectorAll('#sidebar-nav li');
navItems.forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Update active class on nav
        navItems.forEach(n => n.classList.remove('active'));
        this.classList.add('active');
        
        // Switch tabs
        const targetId = this.querySelector('a').getAttribute('href').substring(1);
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });
        const targetTab = document.getElementById(targetId);
        if (targetTab) {
            targetTab.classList.add('active');
        }
    });
});

// Modal functionality
function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
    document.getElementById('uploadForm').reset();
    const alert = document.getElementById('uploadAlert');
    alert.style.display = 'none';
}

// ============================================================
// COLUMN MAPPER LOGIC
// ============================================================
const STANDARD_COLUMNS = {
    users:    ['user_id', 'name', 'age', 'gender', 'country', 'city', 'state'],
    products: ['product_id', 'product_name', 'category', 'price', 'brand', 'discount', 'stock', 'cost_price'],
    orders:   ['order_id', 'user_id', 'product_id', 'quantity', 'order_date', 'total_amount', 'payment_method', 'order_status']
};

// Fuzzy match: score similarity between two strings (returns 0..1)
function fuzzyScore(a, b) {
    a = a.toLowerCase().replace(/[^a-z0-9]/g, '');
    b = b.toLowerCase().replace(/[^a-z0-9]/g, '');
    if (a === b) return 1;
    if (b.includes(a) || a.includes(b)) return 0.85;
    // Check common aliases
    const aliases = {
        name: ['customer_name', 'cname', 'c_name', 'fullname', 'username', 'user_name'],
        product_name: ['productname', 'prod_name', 'item_name', 'itemname', 'name'],
        order_date: ['date', 'purchase_date', 'orderdate', 'order_dt'],
        stock: ['inventory', 'qty_available', 'quantity_available', 'units_available'],
        cost_price: ['cost', 'purchase_price', 'buying_price', 'wholesale_price']
    };
    for (const [std, alts] of Object.entries(aliases)) {
        if (std === a && alts.includes(b)) return 0.9;
        if (std === b && alts.includes(a)) return 0.9;
    }
    return 0;
}

function autoMatchColumns(stdCols, csvHeaders) {
    const result = {};
    stdCols.forEach(std => {
        let best = '', bestScore = 0;
        csvHeaders.forEach(h => {
            const score = fuzzyScore(std, h);
            if (score > bestScore) { bestScore = score; best = h; }
        });
        result[std] = bestScore > 0.5 ? best : '';
    });
    return result;
}

let _pendingUploadFiles = null;
let _pendingClearData = false;
let _columnMappings = null;

function readCSVHeaders(file) {
    return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const text = e.target.result;
            const firstLine = text.split('\n')[0];
            const headers = firstLine.split(',').map(h => h.trim().toLowerCase().replace(/["']/g, ''));
            resolve(headers);
        };
        reader.readAsText(file.slice(0, 4096)); // Only read first 4KB
    });
}

async function submitUpload() {
    const usersFile = document.getElementById('usersFileInput').files[0];
    const productsFile = document.getElementById('productsFileInput').files[0];
    const ordersFile = document.getElementById('ordersFileInput').files[0];
    const clearDataCheckbox = document.getElementById('clear_data');
    const btn = document.getElementById('btnSubmitUpload');
    
    if (!usersFile || !productsFile || !ordersFile) {
        showAlert('Please select all three required CSV files before uploading.', 'error');
        return;
    }
    
    if (!usersFile.name.endsWith('.csv') || !productsFile.name.endsWith('.csv') || !ordersFile.name.endsWith('.csv')) {
        showAlert('Invalid file format. All files must be .csv', 'error');
        return;
    }

    // Read headers and check if column mapping is needed
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing columns...';
    
    const [uHeaders, pHeaders, oHeaders] = await Promise.all([
        readCSVHeaders(usersFile),
        readCSVHeaders(productsFile),
        readCSVHeaders(ordersFile)
    ]);

    _pendingUploadFiles = { usersFile, productsFile, ordersFile };
    _pendingClearData = clearDataCheckbox.checked;
    _columnMappings = null;

    // Check if any standard column is missing
    const uMissing = STANDARD_COLUMNS.users.filter(c => !uHeaders.includes(c));
    const pMissing = STANDARD_COLUMNS.products.filter(c => !pHeaders.includes(c));
    const oMissing = STANDARD_COLUMNS.orders.filter(c => !oHeaders.includes(c));

    const needsMapping = (uMissing.length > 0 || pMissing.length > 0 || oMissing.length > 0);

    if (needsMapping) {
        btn.disabled = false;
        btn.innerHTML = 'Upload All Data';
        buildMapperUI(
            { headers: uHeaders, missing: uMissing, label: 'Users CSV', key: 'users' },
            { headers: pHeaders, missing: pMissing, label: 'Products CSV', key: 'products' },
            { headers: oHeaders, missing: oMissing, label: 'Orders CSV', key: 'orders' }
        );
        document.getElementById('uploadModal').style.display = 'none';
        document.getElementById('columnMapperModal').style.display = 'flex';
        return;
    }

    // No mapping needed — upload directly
    doUpload(null);
}

function buildMapperUI(...fileSections) {
    const container = document.getElementById('mapperSections');
    container.innerHTML = '';

    fileSections.forEach(({ headers, missing, label, key }) => {
        if (missing.length === 0) return;

        const autoMatch = autoMatchColumns(missing, headers);
        const section = document.createElement('div');
        section.className = 'mapper-section';
        section.innerHTML = `
            <div class="mapper-section-title">
                <i class="fa-solid fa-file-csv" style="color: var(--accent-green);"></i>
                ${label} — ${missing.length} column(s) need mapping
            </div>
        `;

        missing.forEach(std => {
            const matched = autoMatch[std] || '';
            const row = document.createElement('div');
            row.className = 'mapper-row';

            const options = headers.map(h =>
                `<option value="${h}" ${h === matched ? 'selected' : ''}>${h}</option>`
            ).join('');

            const isMatched = matched !== '';
            row.innerHTML = `
                <div class="mapper-std">${std}</div>
                <div class="mapper-arrow">→</div>
                <select class="mapper-select ${isMatched ? 'matched' : ''}" data-file="${key}" data-std="${std}">
                    <option value="">— skip / not in CSV —</option>
                    ${options}
                </select>
            `;
            section.appendChild(row);
        });
        container.appendChild(section);
    });
}

function skipMapping() {
    document.getElementById('columnMapperModal').style.display = 'none';
    doUpload(null);
}

function applyMappingAndUpload() {
    const selects = document.querySelectorAll('#mapperSections .mapper-select');
    const mappings = {};
    selects.forEach(sel => {
        const file = sel.dataset.file;
        const std = sel.dataset.std;
        const val = sel.value;
        if (!mappings[file]) mappings[file] = {};
        if (val) mappings[file][std] = val;
    });
    _columnMappings = Object.keys(mappings).length > 0 ? mappings : null;
    document.getElementById('columnMapperModal').style.display = 'none';
    doUpload(_columnMappings);
}

function doUpload(columnMappings) {
    const { usersFile, productsFile, ordersFile } = _pendingUploadFiles;
    const clearData = _pendingClearData;
    const btn = document.getElementById('btnSubmitUpload');

    const formData = new FormData();
    formData.append('users_file', usersFile);
    formData.append('products_file', productsFile);
    formData.append('orders_file', ordersFile);
    formData.append('clear_data', clearData ? 'true' : 'false');
    if (columnMappings) {
        formData.append('column_mappings', JSON.stringify(columnMappings));
    }

    document.getElementById('uploadModal').style.display = 'flex';
    // UI Background Task Queue Init
    btn.disabled = true;
    btn.innerText = 'Queuing Background Process...';

    const alertBox = document.getElementById('uploadAlert');
    alertBox.style.display = 'block';
    alertBox.style.backgroundColor = 'rgba(99, 102, 241, 0.1)';
    alertBox.style.border = '1px solid rgba(99, 102, 241, 0.3)';
    alertBox.style.color = '#fff';
    alertBox.innerHTML = `
        <div style="margin-bottom: 8px; font-size: 0.95rem;"><b>Processing Status:</b> <span id="pollStatusTxt" style="color:#eab308;"><i class="fa-solid fa-spinner fa-spin"></i> Establishing Cluster Logic...</span></div>
        <div style="width: 100%; background: rgba(255,255,255,0.1); border-radius: 8px; overflow: hidden; height: 16px; margin-bottom: 8px; border: 1px solid rgba(255,255,255,0.1);">
            <div id="pollProgressBar" style="width: 0%; height: 100%; background: linear-gradient(90deg, #6366f1, #ec4899); transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1);"></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #a5b4fc; font-weight: 500;">
            <span>Inserted: <span id="pollInserted">0</span></span>
            <span>Failed: <span id="pollFailed">0</span> / <span id="pollTotal">0</span></span>
        </div>
    `;

    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'queued' || data.success) {
            pollDatasetStatus(data.dataset_id, btn);
        } else {
            showAlert(data.message || 'Upload physically rejected tightly.', 'error');
            btn.disabled = false;
            btn.innerText = 'Upload All Data';
        }
    })
    .catch(err => {
        console.error('Upload Error:', err);
        showAlert('An unexpected server routing error dynamically occurred.', 'error');
        btn.disabled = false;
        btn.innerText = 'Upload All Data';
    });
}

function pollDatasetStatus(datasetId, btn) {
    const statusTxt = document.getElementById('pollStatusTxt');
    const progressBar = document.getElementById('pollProgressBar');
    const insertedTxt = document.getElementById('pollInserted');
    const failedTxt = document.getElementById('pollFailed');
    const totalTxt = document.getElementById('pollTotal');
    
    statusTxt.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> QUEUED IN BACKGROUND`;
    
    let retryCount = 0;
    
    const interval = setInterval(() => {
        fetch(`/api/dataset/${datasetId}/status`)
            .then(res => {
                if (!res.ok) throw new Error('Network latency timeout natively.');
                return res.json();
            })
            .then(data => {
                retryCount = 0; // Reset retries on success
                if(data.error) return;
                
                if (data.status === 'queued') {
                    statusTxt.innerHTML = `<i class="fa-solid fa-hourglass-half"></i> QUEUED (Position: ${data.queue_position})`;
                } else if (data.status === 'processing') {
                    statusTxt.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> PROCESSING (${data.progress_percentage}%)`;
                }
                
                progressBar.style.width = `${data.progress_percentage}%`;
                insertedTxt.innerText = data.inserted.toLocaleString();
                failedTxt.innerText = data.failed.toLocaleString();
                totalTxt.innerText = data.total_rows.toLocaleString();
                
                if (data.status === 'completed' || data.status === 'partial_success' || data.status === 'failed') {
                    clearInterval(interval);
                    const pTime = data.processing_time_seconds > 0 ? ` [${data.processing_time_seconds.toFixed(2)}s]` : '';
                    
                    if(data.status === 'failed') {
                        statusTxt.innerHTML = `<span style="color:#ef4444;"><i class="fa-solid fa-xmark"></i> FAILED TERMINATION${pTime}</span>`;
                        progressBar.style.background = '#ef4444';
                        btn.disabled = false;
                        btn.innerText = 'Retry Data Upload';
                    } else if(data.status === 'partial_success') {
                        statusTxt.innerHTML = `<span style="color:#eab308;"><i class="fa-solid fa-triangle-exclamation"></i> PARTIAL SUCCESS${pTime}</span> <a href="/api/dataset/${datasetId}/errors" style="color:#ec4899; text-decoration:underline; font-weight:bold; margin-left:10px;"><i class="fa-solid fa-download"></i> View Errors CSV</a>`;
                        progressBar.style.background = '#eab308';
                        btn.disabled = false;
                        btn.innerText = 'Acknowledge Bounds & Close';
                        btn.onclick = () => { closeUploadModal(); if(window.location.pathname === '/data-history') window.location.reload(); else checkHasData(); };
                    } else {
                        statusTxt.innerHTML = `<span style="color:#10b981;"><i class="fa-solid fa-check-double"></i> UPLOAD COMPLETED! ${data.inserted.toLocaleString()} rows processed natively${pTime}.</span>`;
                        progressBar.style.background = '#10b981';
                        btn.innerText = 'Redirecting Dashboard...';
                        setTimeout(() => {
                            closeUploadModal();
                            if(window.location.pathname === '/data-history') window.location.reload();
                            else checkHasData();
                        }, 3500);
                    }
                }
            })
            .catch(err => {
                console.error("Polling Matrix Network failure:", err);
                retryCount++;
                if (retryCount <= 5) {
                    statusTxt.innerHTML = `<span style="color:#ef4444;"><i class="fa-solid fa-triangle-exclamation"></i> Connection lost. Retrying... (${retryCount}/5)</span>`;
                } else {
                    clearInterval(interval);
                    statusTxt.innerHTML = `<span style="color:#ef4444;"><i class="fa-solid fa-circle-xmark"></i> Connection permanently lost globally.</span>`;
                    btn.disabled = false;
                    btn.innerText = 'Close Matrix';
                }
            });
    }, 2000);
}

function showAlert(msg, type) {
    const alert = document.getElementById('uploadAlert');
    alert.innerText = msg;
    alert.style.display = 'block';
    if (type === 'error') {
        alert.style.backgroundColor = 'rgba(239, 68, 68, 0.1)';
        alert.style.color = '#ef4444';
        alert.style.border = '1px solid rgba(239, 68, 68, 0.3)';
    } else if (type === 'success') {
        alert.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
        alert.style.color = '#10b981';
        alert.style.border = '1px solid rgba(16, 185, 129, 0.3)';
    } else {
        alert.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
        alert.style.color = '#3b82f6';
        alert.style.border = '1px solid rgba(59, 130, 246, 0.3)';
    }
}

// Onboarding Tour Logic
function startOnboarding(hasData) {
    if (!window.driver) return;
    const driver = window.driver.js.driver;
    
    const steps = [];
    
    if (!hasData) {
        steps.push({
            element: '#empty-state-container',
            popover: { title: 'Welcome to DataSense.AI!', description: 'Your dashboard is currently empty. Let\'s get started by uploading some datasets.', side: 'top', align: 'start' }
        });
        steps.push({
            element: 'button[onclick="document.getElementById(\'uploadModal\').style.display=\'flex\'"]',
            popover: { title: '1. Upload Data', description: 'Click here to upload your Users, Products, and Orders CSV files to generate insights.', side: 'bottom', align: 'center' }
        });
    } else {
        steps.push({
            element: '.header-left',
            popover: { title: 'Welcome to your Dashboard!', description: 'Let\'s take a quick tour of your analytics.', side: 'bottom', align: 'start' }
        });
        steps.push({
            element: '.metrics-grid',
            popover: { title: 'Key Performance Indicators', description: 'At a glance, see your total orders, revenue, customer base, and top payment method.', side: 'bottom', align: 'center' }
        });
        steps.push({
            element: '.filter-bar',
            popover: { title: 'Powerful Filtering', description: 'Slice and dice your data by date, demographics, purchase category, or price range.', side: 'bottom', align: 'center' }
        });
        steps.push({
            element: '#sidebar-nav',
            popover: { title: 'Navigation Tabs', description: 'Switch between Overview, Audience demographics, and advanced AI Insights.', side: 'right', align: 'start' }
        });
        steps.push({
            element: 'a[href^="/api/download-report"]',
            popover: { title: 'Export Reports', description: 'Download a beautifully formatted PDF report of your current analytics view.', side: 'bottom', align: 'center' }
        });
    }

    const driverObj = driver({
        showProgress: true,
        steps: steps,
        nextBtnText: 'Next →',
        prevBtnText: '← Prev',
        doneBtnText: 'Done'
    });
    
    driverObj.drive();
}

// -------------------------------------------------------------
// SECURE CSR CHART.JS RENDERINGS
// -------------------------------------------------------------
const chartRegistry = {};
Chart.defaults.color = '#9ca3af';
Chart.defaults.font.family = "'Outfit', sans-serif";

function initOrUpdateChart(ctxId, config) {
    const ctx = document.getElementById(ctxId);
    if (!ctx) return;
    if (chartRegistry[ctxId]) chartRegistry[ctxId].destroy();
    chartRegistry[ctxId] = new Chart(ctx, config);
}

// Global UI details engine for dynamic side pane rendering
let lastHoveredIndex = {};

function updateChartDetails(chartId, index, dataList, type) {
    // Avoid redundant updates to improve render pipeline performance
    if (lastHoveredIndex[chartId] === index) return;
    lastHoveredIndex[chartId] = index;

    const detailsContainer = document.getElementById(chartId + '-details');
    if (!detailsContainer) return;

    const item = dataList[index];
    if (!item) return;

    let title = '';
    let valueStr = '';
    let percentStr = '';
    let insightStr = '';
    let subtitle = '';

    if (type === 'trend') {
        const total = dataList.reduce((acc, curr) => acc + curr.total_revenue, 0);
        const percent = total > 0 ? ((item.total_revenue / total) * 100).toFixed(1) : 0;
        title = item.month;
        subtitle = 'Monthly Cycle';
        valueStr = '$' + parseFloat(item.total_revenue).toLocaleString(undefined, {minimumFractionDigits: 2});
        percentStr = percent + '% share';
        insightStr = `A key sales interval driving substantial cash flow. Buyer retention during this cycle showed healthy conversion bounds.`;
    } 
    else if (type === 'products') {
        const total = dataList.reduce((acc, curr) => acc + curr.total_sold, 0);
        const percent = total > 0 ? ((item.total_sold / total) * 100).toFixed(1) : 0;
        title = item.product_name;
        subtitle = 'Star Product';
        valueStr = parseInt(item.total_sold).toLocaleString() + ' units';
        percentStr = percent + '% volume';
        insightStr = `Commanding massive unit velocity in top list. A major shopper acquisition funnel. Maintain target inventory!`;
    }
    else if (type === 'category') {
        const total = dataList.reduce((acc, curr) => acc + curr.revenue, 0);
        const percent = total > 0 ? ((item.revenue / total) * 100).toFixed(1) : 0;
        title = item.category;
        subtitle = 'Purchase Category';
        valueStr = '$' + parseFloat(item.revenue).toLocaleString(undefined, {minimumFractionDigits: 2});
        percentStr = percent + '% revenue';
        
        const insights = {
            'Electronics': 'Drives the majority of high-ticket baskets. Perfect target for bundle cross-sells and extended warranty upsells.',
            'Clothing': 'High purchase velocity and seasonal frequency. Drives recurring shopper volume. Recommended for buy-one-get-one deals.',
            'Home & Kitchen': 'Strong basket additions rate. Often purchased alongside standard daily essentials. Perfect for general promotion campaigns.',
            'Beauty': 'Superior profit margins and steady customer loyalty metrics. Highly recommended for recurring subscription and beauty tier models.',
            'Sports': 'Highly active shopper segment with above average basket size. Excellent cross-promotions conversion rate.',
            'Toys': 'Generates massive holiday spikes. Exceptional performance for customer gift basket value additions.'
        };
        insightStr = insights[title] || 'Consistent revenue contributor. Perfect target for direct re-engagement campaigns and loyalty discount triggers.';
    }
    else if (type === 'payment') {
        const total = dataList.reduce((acc, curr) => acc + curr.num_transactions, 0);
        const percent = total > 0 ? ((item.num_transactions / total) * 100).toFixed(1) : 0;
        title = item.payment_method;
        subtitle = 'Transaction Route';
        valueStr = parseInt(item.num_transactions).toLocaleString() + ' orders';
        percentStr = percent + '% share';

        const insights = {
            'Credit Card': 'Standard preferred method. Typically yields largest average order values and minimal payment processing friction.',
            'PayPal': 'Extremely popular option for quick mobile transactions. Strongly preferred by high frequency returning users.',
            'Debit Card': 'Solid transactional footprint. Provides highly reliable direct checkout lanes with zero processing delay.',
            'Apple Pay': 'Fast-growing digital wallet with supreme checkout speeds. Strongly favored by modern mobile shopper brackets.',
            'Google Pay': 'Secure checkout wallet. Preferred for swift Android system transactions.'
        };
        insightStr = insights[title] || 'Reliable transaction pipeline ensuring secure checkout flow and high success bounds.';
    }

    detailsContainer.innerHTML = `
        <div class="details-active-card">
            <div class="details-subtitle">${subtitle}</div>
            <div class="details-header">
                <span class="details-title" title="${title}">${title}</span>
                <span class="details-percentage">${percentStr}</span>
            </div>
            <div class="details-value">${valueStr}</div>
            <div class="details-insight-box">
                <div class="details-insight-text">"${insightStr}"</div>
            </div>
        </div>
    `;
}

function renderTrendChart(qs = '') {
    fetch('/api/trend' + qs).then(res => res.json()).then(data => {
        if (!data || data.length === 0) return;
        const labels = data.map(d => d.month);
        const values = data.map(d => d.total_revenue);
        
        // Render initial details view for highest element
        updateChartDetails('trendChart', 0, data, 'trend');

        initOrUpdateChart('trendChart', {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue ($)',
                    data: values,
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.08)',
                    borderWidth: 4,
                    pointBackgroundColor: '#ec4899',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: '#ec4899',
                    pointHoverBorderColor: '#ffffff',
                    pointHoverBorderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                onHover: (event, activeElements) => {
                    if (activeElements && activeElements.length > 0) {
                        const index = activeElements[0].index;
                        updateChartDetails('trendChart', index, data, 'trend');
                    }
                },
                plugins: { 
                    legend: { display: false }, 
                    tooltip: { 
                        mode: 'index', 
                        intersect: false,
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        titleColor: '#fff',
                        bodyColor: '#cbd5e1',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 10,
                        bodyFont: { family: "'Outfit', sans-serif" },
                        titleFont: { family: "'Outfit', sans-serif", weight: 'bold' }
                    } 
                },
                scales: { 
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' } }, 
                    x: { grid: { display: false } } 
                }
            }
        });
    }).catch(console.error);
}

function renderTopProductsChart(qs = '') {
    fetch('/api/top-products' + qs).then(res => res.json()).then(data => {
        if (!data || data.length === 0) return;
        const labels = data.map(d => (d.product_name.length > 25 ? d.product_name.substring(0,25)+'...' : d.product_name));
        const values = data.map(d => d.total_sold);

        // Render initial details view
        updateChartDetails('topProductsChart', 0, data, 'products');

        initOrUpdateChart('topProductsChart', {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Units Sold',
                    data: values,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    hoverBackgroundColor: '#10b981',
                    hoverBorderColor: '#ffffff',
                    hoverBorderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true, maintainAspectRatio: false,
                onHover: (event, activeElements) => {
                    if (activeElements && activeElements.length > 0) {
                        const index = activeElements[0].index;
                        updateChartDetails('topProductsChart', index, data, 'products');
                    }
                },
                plugins: { 
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 10,
                        bodyFont: { family: "'Outfit', sans-serif" }
                    }
                },
                scales: { 
                    x: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' } }, 
                    y: { grid: { display: false }, ticks: { font: { size: 10 } } } 
                }
            }
        });
    }).catch(console.error);
}

function renderCategoryChart(qs = '') {
    fetch('/api/category-analysis' + qs).then(res => res.json()).then(data => {
        if (!data || data.length === 0) return;
        
        // Render initial details view
        updateChartDetails('categoryChart', 0, data, 'category');

        initOrUpdateChart('categoryChart', {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.category),
                datasets: [{
                    data: data.map(d => d.revenue),
                    backgroundColor: ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6', '#3b82f6', '#14b8a6'],
                    borderWidth: 2,
                    borderColor: 'var(--bg-secondary)',
                    hoverBorderColor: '#ffffff',
                    hoverBorderWidth: 3,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                onHover: (event, activeElements) => {
                    if (activeElements && activeElements.length > 0) {
                        const index = activeElements[0].index;
                        updateChartDetails('categoryChart', index, data, 'category');
                    }
                },
                plugins: {
                    legend: { 
                        position: 'right', 
                        labels: { 
                            boxWidth: 12, 
                            padding: 15,
                            font: { family: "'Outfit', sans-serif" }
                        } 
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 10,
                        bodyFont: { family: "'Outfit', sans-serif" }
                    }
                },
                cutout: '70%'
            }
        });
    }).catch(console.error);
}

function renderPaymentChart(qs = '') {
    fetch('/api/payment-analysis' + qs).then(res => res.json()).then(data => {
        if (!data || data.length === 0) return;

        // Render initial details view
        updateChartDetails('paymentChart', 0, data, 'payment');

        initOrUpdateChart('paymentChart', {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.payment_method),
                datasets: [{
                    data: data.map(d => d.num_transactions),
                    backgroundColor: ['#ec4899', '#8b5cf6', '#3b82f6', '#10b981', '#f59e0b'],
                    borderWidth: 2,
                    borderColor: 'var(--bg-secondary)',
                    hoverBorderColor: '#ffffff',
                    hoverBorderWidth: 3,
                    hoverOffset: 15
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                onHover: (event, activeElements) => {
                    if (activeElements && activeElements.length > 0) {
                        const index = activeElements[0].index;
                        updateChartDetails('paymentChart', index, data, 'payment');
                    }
                },
                plugins: {
                    legend: { 
                        position: 'right', 
                        labels: { 
                            boxWidth: 12, 
                            padding: 15,
                            font: { family: "'Outfit', sans-serif" }
                        } 
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.95)',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 10,
                        bodyFont: { family: "'Outfit', sans-serif" }
                    }
                },
                cutout: '60%'
            }
        });
    }).catch(console.error);
}

function fetchCustomerSimilarity(qs = '') {
    fetch('/api/customer-similarity' + qs)
        .then(res => res.json())
        .then(data => {
            const grid = document.getElementById('similarityGrid');
            if (!grid) return;
            grid.innerHTML = '';
            
            if (data.names && data.names.length > 0) {
                const table = document.createElement('table');
                table.style.width = '100%';
                table.style.borderCollapse = 'separate';
                table.style.borderSpacing = '3px';
                table.style.fontSize = '0.75rem';
                table.style.fontFamily = "'Outfit', sans-serif";
                
                // Create Header Row
                const thead = document.createElement('thead');
                const headerRow = document.createElement('tr');
                
                // Top-left corner cell
                const cornerTh = document.createElement('th');
                cornerTh.style.padding = '8px';
                cornerTh.style.backgroundColor = 'rgba(255,255,255,0.02)';
                cornerTh.style.borderRadius = '4px';
                cornerTh.style.position = 'sticky';
                cornerTh.style.left = '0';
                cornerTh.style.zIndex = '2';
                cornerTh.style.border = '1px solid rgba(255,255,255,0.05)';
                cornerTh.innerText = '';
                headerRow.appendChild(cornerTh);
                
                data.names.forEach(name => {
                    const th = document.createElement('th');
                    th.innerText = name.split(' ')[0]; // first name only to keep it compact
                    th.style.padding = '8px';
                    th.style.textAlign = 'center';
                    th.style.color = 'var(--text-secondary)';
                    th.style.backgroundColor = 'rgba(255,255,255,0.02)';
                    th.style.border = '1px solid rgba(255,255,255,0.05)';
                    th.style.borderRadius = '4px';
                    th.style.minWidth = '50px';
                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                table.appendChild(thead);
                
                // Create Table Body
                const tbody = document.createElement('tbody');
                data.data.forEach((row, i) => {
                    const tr = document.createElement('tr');
                    
                    // Row Header Name
                    const rowHeader = document.createElement('td');
                    rowHeader.innerText = data.names[i];
                    rowHeader.style.padding = '8px';
                    rowHeader.style.fontWeight = '600';
                    rowHeader.style.color = 'var(--text-primary)';
                    rowHeader.style.backgroundColor = 'rgba(255,255,255,0.02)';
                    rowHeader.style.border = '1px solid rgba(255,255,255,0.05)';
                    rowHeader.style.borderRadius = '4px';
                    rowHeader.style.position = 'sticky';
                    rowHeader.style.left = '0';
                    rowHeader.style.zIndex = '1';
                    rowHeader.style.whiteSpace = 'nowrap';
                    tr.appendChild(rowHeader);
                    
                    row.forEach((val, j) => {
                        const td = document.createElement('td');
                        td.innerText = val.toFixed(2);
                        td.style.padding = '8px';
                        td.style.textAlign = 'center';
                        td.style.borderRadius = '4px';
                        td.style.fontWeight = '600';
                        td.style.transition = 'all 0.2s ease';
                        td.style.cursor = 'pointer';
                        
                        const isSelf = i === j;
                        let r = 99, g = 102, b = 241; // Deep Blue / Violet
                        if (val >= 0.8) {
                            r = 124; g = 58; b = 237; // Royal Purple
                        } else if (val >= 0.5) {
                            r = 236; g = 72; b = 153; // Neon Pink
                        } else if (val >= 0.2) {
                            r = 99; g = 102; b = 241; // Violet
                        } else {
                            r = 30; g = 41; b = 59; // Dark Slate for low correlation
                        }
                        
                        const alpha = val * 0.75 + 0.15;
                        td.style.backgroundColor = `rgba(${r}, ${g}, ${b}, ${alpha})`;
                        td.style.color = val > 0.4 ? '#ffffff' : 'rgba(255, 255, 255, 0.6)';
                        
                        if (isSelf) {
                            td.style.border = '2px solid #ffffff';
                        } else {
                            td.style.border = '1px solid rgba(255,255,255,0.05)';
                        }
                        
                        td.title = `Match compatibility between ${data.names[i]} and ${data.names[j]}: ${(val * 100).toFixed(1)}%`;
                        
                        td.addEventListener('mouseenter', () => {
                            td.style.transform = 'scale(1.15)';
                            td.style.zIndex = '5';
                            td.style.boxShadow = '0 0 10px rgba(99, 102, 241, 0.5)';
                        });
                        td.addEventListener('mouseleave', () => {
                            td.style.transform = 'none';
                            td.style.zIndex = '0';
                            td.style.boxShadow = 'none';
                        });
                        
                        tr.appendChild(td);
                    });
                    tbody.appendChild(tr);
                });
                table.appendChild(tbody);
                grid.appendChild(table);
            } else {
                grid.innerHTML = '<p style="text-align:center; padding: 20px;">No similarity data available.</p>';
            }
        })
        .catch(err => {
            console.error("Error loading customer similarity matrix:", err);
            const grid = document.getElementById('similarityGrid');
            if (grid) {
                grid.innerHTML = '<p style="text-align:center; padding: 20px; color:#ef4444;">Failed to compile Match Matrix engine natively.</p>';
            }
        });
}

// ============================================================
// AGE DEMOGRAPHICS PRODUCT PREFERENCES
// ============================================================
function fetchAgeProductPreferences(qs = '') {
    fetch('/api/age-product-analysis' + qs)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('age-product-container');
            if (!container) return;
            container.innerHTML = '';
            const ageColors = {
                '18-25': { grad: 'linear-gradient(135deg,#6366f1,#8b5cf6)', bar: '#6366f1' },
                '26-35': { grad: 'linear-gradient(135deg,#3b82f6,#06b6d4)', bar: '#3b82f6' },
                '36-50': { grad: 'linear-gradient(135deg,#10b981,#34d399)', bar: '#10b981' },
                '50+':   { grad: 'linear-gradient(135deg,#f59e0b,#fbbf24)', bar: '#f59e0b' }
            };
            const ageIcons = { '18-25': '🎮', '26-35': '💼', '36-50': '🏡', '50+': '🌿' };
            let hasAny = false;
            ['18-25', '26-35', '36-50', '50+'].forEach(group => {
                const items = data[group] || [];
                if (!items.length) return;
                hasAny = true;
                const color = ageColors[group] || { grad: '#64748b', bar: '#64748b' };
                const maxQty = Math.max(...items.map(i => i.total_quantity), 1);
                const card = document.createElement('div');
                card.className = 'age-pref-card';
                const itemsHTML = items.map(item => `
                    <div class="age-pref-item">
                        <span class="age-pref-label" title="${item.product_name}">${item.product_name}</span>
                        <div class="age-pref-bar-wrap">
                            <div class="age-pref-bar" style="width:${Math.round((item.total_quantity/maxQty)*100)}%;background:${color.bar};"></div>
                        </div>
                        <span class="age-pref-qty">${item.total_quantity.toLocaleString()}</span>
                    </div>`).join('');
                card.innerHTML = `
                    <h4 style="background:${color.grad};-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                        ${ageIcons[group] || '👤'} Age ${group}
                    </h4>${itemsHTML}`;
                container.appendChild(card);
            });
            if (!hasAny) {
                container.innerHTML = '<div style="text-align:center;grid-column:1/-1;padding:20px;color:var(--text-secondary);">No age demographic data available. Upload a dataset with user age fields.</div>';
            }
        })
        .catch(err => {
            console.error('Error fetching age product preferences:', err);
            const c = document.getElementById('age-product-container');
            if (c) c.innerHTML = '<div style="text-align:center;grid-column:1/-1;padding:20px;color:#ef4444;">Failed to load age preferences.</div>';
        });
}

// ============================================================
// STOCK STATUS TABLE
// ============================================================
function fetchStockStatus() {
    fetch('/api/stock-analysis')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('stock-table-body');
            if (!tbody) return;
            tbody.innerHTML = '';
            if (data && data.length > 0) {
                const sorted = [...data].sort((a, b) => (a.stock || 0) - (b.stock || 0));
                sorted.slice(0, 12).forEach(p => {
                    const stock = p.stock || 0;
                    const isLow = stock < 25;
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${p.product_name}</strong></td>
                        <td style="font-size:0.85rem;color:var(--text-secondary);">${p.category || '—'}</td>
                        <td style="font-weight:700;color:${isLow ? '#ef4444' : '#10b981'};">${stock}</td>
                        <td><span style="background:${isLow ? 'rgba(239,68,68,0.15)' : 'rgba(16,185,129,0.15)'};color:${isLow ? '#ef4444' : '#10b981'};padding:2px 8px;border-radius:12px;font-size:0.78rem;font-weight:700;">${isLow ? '⚠ LOW' : '✓ OK'}</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-secondary);">No inventory data yet.</td></tr>';
            }
        })
        .catch(err => {
            console.error('Error fetching stock status:', err);
            const tbody = document.getElementById('stock-table-body');
            if (tbody) tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#ef4444;">Failed to load stock data.</td></tr>';
        });
}

// ============================================================
// RESTOCK RECOMMENDATIONS TABLE
// ============================================================
function fetchRestockRecommendations(qs = '') {
    fetch('/api/restock-recommendations' + qs)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('restock-table-body');
            if (!tbody) return;
            tbody.innerHTML = '';
            if (data && data.length > 0) {
                data.forEach(r => {
                    const prioClass = r.priority === 'CRITICAL' ? 'priority-critical' : r.priority === 'HIGH' ? 'priority-high' : 'priority-medium';
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${r.product_name}</strong><br><span style="font-size:0.78rem;color:var(--text-secondary);">${r.category}</span></td>
                        <td style="color:${r.current_stock <= 10 ? '#ef4444' : '#f59e0b'};font-weight:700;">${r.current_stock}</td>
                        <td style="color:#10b981;font-weight:700;">+${r.suggested_restock_qty} units</td>
                        <td><span class="${prioClass}">${r.priority}</span></td>
                        <td style="color:#10b981;font-weight:700;">$${r.estimated_profit.toLocaleString(undefined,{minimumFractionDigits:2})}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);">No restocking needed — inventory is healthy.</td></tr>';
            }
        })
        .catch(err => {
            console.error('Error fetching restock recommendations:', err);
            const tbody = document.getElementById('restock-table-body');
            if (tbody) tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#ef4444;">Failed to load recommendations.</td></tr>';
        });
}

function fetchSeasonalSales(qs = '') {
    fetch('/api/seasonal-product-sales' + qs)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('seasonal-sales-table-body');
            if (!tbody) return;
            tbody.innerHTML = '';
            if (data && data.length > 0) {
                data.forEach(r => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><span style="font-weight: 700; color: #ea580c;">${r.season}</span></td>
                        <td><strong>${r.product_name}</strong></td>
                        <td style="font-size:0.85rem;color:var(--text-secondary);">${r.category}</td>
                        <td style="font-weight:700;color:var(--accent-blue);">${r.total_sold.toLocaleString()}</td>
                        <td style="color:#10b981;font-weight:700;">$${r.revenue.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--text-secondary);">No seasonal data available.</td></tr>';
            }
        })
        .catch(err => {
            console.error('Error fetching seasonal sales:', err);
            const tbody = document.getElementById('seasonal-sales-table-body');
            if (tbody) tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#ef4444;">Failed to load seasonal sales.</td></tr>';
        });
}

function fetchSalesGrowthRecommendations(qs = '') {
    fetch('/api/sales-growth-recommendations' + qs)
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('growth-recommendations-table-body');
            if (!tbody) return;
            tbody.innerHTML = '';
            if (data && data.length > 0) {
                data.forEach(r => {
                    let badgeClass = 'rec-maintain';
                    if (r.recommendation.startsWith('Increase Sales')) {
                        badgeClass = 'rec-increase';
                    } else if (r.recommendation.startsWith('Promote Sales')) {
                        badgeClass = 'rec-promote';
                    } else if (r.recommendation.startsWith('Do Not') || r.recommendation.startsWith('Hold')) {
                        badgeClass = 'rec-hold';
                    }
                    
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${r.product_name}</strong><br><span style="font-size:0.75rem;color:var(--text-secondary);" title="${r.reason}">${r.reason}</span></td>
                        <td style="font-weight:700;color:var(--text-primary);">${r.quantity_sold} units</td>
                        <td><span class="rec-badge ${badgeClass}">${r.recommendation}</span></td>
                        <td style="font-size:0.8rem;color:var(--text-secondary);font-weight:600;">${r.status}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-secondary);">No growth recommendations compiled yet.</td></tr>';
            }
        })
        .catch(err => {
            console.error('Error fetching growth recommendations:', err);
            const tbody = document.getElementById('growth-recommendations-table-body');
            if (tbody) tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#ef4444;">Failed to load growth recommendations.</td></tr>';
        });
}


// ============================================================
// AUTO CAMPAIGN TOGGLE
// ============================================================
function toggleAutoCampaign(checkbox) {
    const enabled = checkbox.checked;
    const banner = document.getElementById('autoCampaignBanner');
    fetch('/api/toggle-auto-campaign', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            if (banner) banner.style.display = enabled ? 'flex' : 'none';
            showToast(
                enabled ? '🤖 Auto re-engagement campaigns activated! Dormant & Churned customers will receive daily discount emails.'
                        : '⏸ Auto campaigns paused.',
                enabled ? 'success' : 'info'
            );
        }
    })
    .catch(err => {
        console.error('Error toggling auto campaign:', err);
        checkbox.checked = !enabled;
        showToast('Failed to update campaign settings.', 'error');
    });
}

function sendBulkEmails() {
    const btn = document.getElementById('btnBulkEmail');
    if (!btn) return;
    
    if (!confirm('Are you sure you want to send re-engagement emails to all currently listed at-risk users?')) {
        return;
    }
    
    btn.disabled = true;
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending Bulk...';
    
    const startDate = document.getElementById('f_start_date').value;
    const endDate = document.getElementById('f_end_date').value;
    const country = document.getElementById('f_country').value;
    const gender = document.getElementById('f_gender').value;
    const category = document.getElementById('f_category').value;
    const paymentMethod = document.getElementById('f_payment').value;
    const minAmount = document.getElementById('f_min').value;
    const maxAmount = document.getElementById('f_max').value;
    
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    if (country) params.append('country', country);
    if (gender) params.append('gender', gender);
    if (category) params.append('category', category);
    if (paymentMethod) params.append('payment_method', paymentMethod);
    if (minAmount) params.append('min_amount', minAmount);
    if (maxAmount) params.append('max_amount', maxAmount);
    
    fetch('/api/send-bulk-churn-emails?' + params.toString(), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
        btn.disabled = false;
        btn.innerHTML = originalText;
        if (data.success) {
            showToast(`✅ ${data.message}`, 'success');
        } else {
            showToast(`❌ ${data.message || 'Failed to send bulk emails.'}`, 'error');
        }
    })
    .catch(err => {
        console.error('Error sending bulk emails:', err);
        btn.disabled = false;
        btn.innerHTML = originalText;
        showToast('❌ Network error while sending bulk emails.', 'error');
    });
}

// ============================================================
// EMAIL PREVIEW MODAL
// ============================================================
let _pendingEmailData = null;

function openEmailPreview(userData) {
    if (typeof userData === 'string') {
        try { userData = JSON.parse(userData); } catch(e) {}
    }
    _pendingEmailData = userData;
    const { customer_name, days_absent, total_spent, status, interested_product, recommended_product, discount, coupon_code } = userData;
    const discountVal = discount || (status === 'Churned' ? 40 : status === 'Dormant' ? 20 : 15);
    const couponCodeVal = coupon_code || `COMEBACK${discountVal}`;
    const recProd = recommended_product || "our latest collections";
    const emailTo = userData.email || `${(customer_name || 'customer').replace(/\s+/g,'').toLowerCase()}@example.com`;

    document.getElementById('emailPreviewSubject').textContent = `We miss you, ${customer_name}! Claim your exclusive ${discountVal}% discount`;
    document.getElementById('emailPreviewRecipient').textContent = emailTo;
    document.getElementById('emailPreviewDiscount').textContent = `${discountVal}% OFF on ${recProd} (Code: ${couponCodeVal})`;

    const previewHTML = `<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body style="margin:0;padding:24px;font-family:'Segoe UI',Arial,sans-serif;background:#0f172a;color:#f8fafc;">
        <div style="max-width:520px;margin:auto;">
            <div style="text-align:center;margin-bottom:20px;">
                <h1 style="color:#3b82f6;font-size:1.5rem;margin:0;">We Miss You, ${customer_name}!</h1>
                <p style="color:#94a3b8;font-size:0.9rem;margin-top:6px;">It's been ${days_absent} days since your last purchase.</p>
            </div>
            <div style="background:rgba(30,41,59,0.9);border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:24px;text-align:center;margin-bottom:20px;">
                <p style="color:#f8fafc;line-height:1.6;margin:0 0 14px;">We noticed you previously purchased <strong>${interested_product || 'our items'}</strong>. Based on what other customers bought together with it (frequent itemset), we highly recommend <strong>${recProd}</strong>! As a special offer to bring you back, claim your discount code on <strong>${recProd}</strong>:</p>
                <div style="font-size:2.2rem;font-weight:900;color:#10b981;letter-spacing:3px;margin:12px 0;">${couponCodeVal}</div>
                <p style="font-size:1.2rem;font-weight:700;color:#8b5cf6;margin:0 0 4px;">Save ${discountVal}% OFF on ${recProd}!</p>
                <p style="font-size:0.82rem;color:#94a3b8;margin:0;">Valid for 7 days. Enter at checkout.</p>
            </div>
            <p style="color:#64748b;font-size:0.78rem;text-align:center;margin:0;">Sent by DataSense.AI Customer Retention Engine</p>
        </div></body></html>`;

    const iframe = document.getElementById('emailPreviewIframe');
    iframe.srcdoc = previewHTML;
    document.getElementById('emailPreviewModal').style.display = 'flex';
}

function closeEmailPreview() {
    document.getElementById('emailPreviewModal').style.display = 'none';
    _pendingEmailData = null;
}

function confirmSendEmail() {
    if (!_pendingEmailData) return;
    const btn = document.getElementById('btnSendEmail');
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Sending...';
    const snapshot = { ..._pendingEmailData };

    fetch('/api/send-churn-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(snapshot)
    })
    .then(res => res.json())
    .then(data => {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Send Email Now';
        closeEmailPreview();
        showToast(
            data.success
                ? `✅ Re-engagement email dispatched to ${snapshot.customer_name} successfully!`
                : '❌ Failed to send email. Check SMTP configuration.',
            data.success ? 'success' : 'error'
        );
    })
    .catch(err => {
        console.error('Error sending email:', err);
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Send Email Now';
        showToast('❌ Network error while sending email.', 'error');
    });
}

// ============================================================
// TOAST NOTIFICATION SYSTEM
// ============================================================
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const colorMap = { success: '#10b981', error: '#ef4444', info: '#3b82f6' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <span style="flex:1;color:${colorMap[type] || '#fff'};font-weight:500;">${message}</span>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;color:var(--text-secondary);cursor:pointer;font-size:1rem;padding:0 0 0 8px;">✕</button>
    `;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        toast.style.transition = 'all 0.4s ease';
        setTimeout(() => toast.remove(), 400);
    }, 5000);
}


// ============================================================
// LTV DYNAMIC PREDICTIVE SYSTEM
// ============================================================
function fetchLTVPrediction(qs = '') {
    fetch('/api/ltv-prediction' + qs)
        .then(res => res.json())
        .then(data => {
            const r2El = document.getElementById('ltv-r2-stat');
            const maeEl = document.getElementById('ltv-mae-stat');
            const statusEl = document.getElementById('ltv-status-desc');
            const tbody = document.getElementById('ltv-table-body');
            
            if (data && data.metrics) {
                if (r2El) r2El.innerText = data.metrics.r2.toFixed(3);
                if (maeEl) maeEl.innerText = '$' + data.metrics.mae.toLocaleString(undefined, {minimumFractionDigits: 2});
                if (statusEl) statusEl.innerText = data.metrics.status;
            }
            
            if (!tbody) return;
            tbody.innerHTML = '';
            
            if (data && data.users && data.users.length > 0) {
                data.users.forEach(user => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td><strong>${user.name}</strong> <span style="font-size:0.75rem; color:var(--text-secondary); display:block;">ID: ${user.user_id}</span></td>
                        <td><span style="font-size:0.85rem;">${user.country || '—'} (${user.gender || '—'}, age ${user.age || '—'})</span></td>
                        <td><span style="font-size:0.85rem; color:var(--text-secondary);">${user.first_purchase_date}</span></td>
                        <td style="font-weight: 500;">$${user.initial_spent.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                        <td>${user.initial_frequency}</td>
                        <td style="color:var(--text-secondary);">$${user.future_spent.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                        <td style="color:var(--accent-blue); font-weight: 500;">$${user.predicted_future_spent.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                        <td style="color:var(--accent-green); font-weight: 600;">$${user.predicted_total_ltv.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    `;
                    tbody.appendChild(tr);
                });
                
                renderLTVDistributionChart(data.users);
            } else {
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">No LTV predictions available. Ensure you have loaded customer transaction data.</td></tr>';
            }
        })
        .catch(err => {
            console.error("Error fetching LTV predictions:", err);
            const tbody = document.getElementById('ltv-table-body');
            if (tbody) tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:red;">Failed to load LTV predictions.</td></tr>';
        });
}

function renderLTVDistributionChart(users) {
    const brackets = {
        'Under $100': 0,
        '$100 - $250': 0,
        '$250 - $500': 0,
        '$500 - $1,000': 0,
        'Over $1,000': 0
    };
    
    users.forEach(u => {
        const val = u.predicted_total_ltv;
        if (val < 100) brackets['Under $100']++;
        else if (val < 250) brackets['$100 - $250']++;
        else if (val < 500) brackets['$250 - $500']++;
        else if (val < 1000) brackets['$500 - $1,000']++;
        else brackets['Over $1,000']++;
    });
    
    const labels = Object.keys(brackets);
    const counts = Object.values(brackets);
    
    const isLightMode = document.documentElement.classList.contains('light-mode');
    const labelColor = isLightMode ? '#4b5563' : '#9ca3af';
    const gridColor = isLightMode ? '#e5e7eb' : 'rgba(255, 255, 255, 0.08)';
    
    initOrUpdateChart('ltvDistributionChart', {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Customers',
                data: counts,
                backgroundColor: [
                    'rgba(99, 102, 241, 0.7)',
                    'rgba(59, 130, 246, 0.7)',
                    'rgba(16, 185, 129, 0.7)',
                    'rgba(245, 158, 11, 0.7)',
                    'rgba(236, 72, 153, 0.7)'
                ],
                borderColor: [
                    '#6366f1', '#3b82f6', '#10b981', '#f59e0b', '#ec4899'
                ],
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleColor: '#fff',
                    bodyColor: '#f8fafc',
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    grid: { color: gridColor },
                    ticks: { color: labelColor, stepSize: 1 },
                    title: { display: true, text: 'Customers Count', color: labelColor }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: labelColor }
                }
            }
        }
    });
}

// -------------------------------------------------------------
// WHAT-IF SIMULATOR ENGINE
// -------------------------------------------------------------
window.simulationBaseline = null;

const SIM_ELASTICITY = {
    marketing: {
        '18-25': 0.45,
        '26-35': 0.35,
        '36-50': 0.25,
        '50+': 0.15
    },
    price: {
        'Electronics': -1.6,
        'Clothing': -1.3,
        'Home & Kitchen': -1.0,
        'Beauty': -0.7,
        'Sports': -1.2,
        'Toys': -0.9,
        'default': -1.0
    }
};

function fetchSimulationBaseline(qs = '') {
    fetch('/api/simulation-baseline' + qs)
        .then(res => res.json())
        .then(data => {
            window.simulationBaseline = data;
            initSimulationSliders();
            updateSimulation();
        })
        .catch(err => {
            console.error("Error fetching simulation baseline:", err);
            showToast("Failed to load simulation baseline dataset.", "error");
        });
}

function initSimulationSliders() {
    if (!window.simulationBaseline || !window.simulationBaseline.matrix) return;
    
    const categories = [...new Set(window.simulationBaseline.matrix.map(row => row.Category))].sort();
    
    const priceContainer = document.getElementById('price-sliders-container');
    const discountContainer = document.getElementById('discount-sliders-container');
    
    if (priceContainer) {
        priceContainer.innerHTML = '';
        categories.forEach(cat => {
            const catId = cat.replace(/\s+/g, '-');
            const sliderHTML = `
                <div class="slider-group" style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span>${cat}:</span>
                        <strong id="val-p-${catId}">0%</strong>
                    </div>
                    <input type="range" id="slide-p-${catId}" min="-30" max="50" value="0" step="5" style="width: 100%; cursor: pointer;" oninput="updateSimulation()">
                </div>
            `;
            priceContainer.insertAdjacentHTML('beforeend', sliderHTML);
        });
    }

    if (discountContainer) {
        discountContainer.innerHTML = '';
        categories.forEach(cat => {
            const catId = cat.replace(/\s+/g, '-');
            const sliderHTML = `
                <div class="slider-group" style="margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px;">
                        <span>${cat}:</span>
                        <strong id="val-d-${catId}">0%</strong>
                    </div>
                    <input type="range" id="slide-d-${catId}" min="0" max="50" value="0" step="5" style="width: 100%; cursor: pointer;" oninput="updateSimulation()">
                </div>
            `;
            discountContainer.insertAdjacentHTML('beforeend', sliderHTML);
        });
    }
}

function updateSimulation() {
    if (!window.simulationBaseline || !window.simulationBaseline.matrix) return;
    
    // Read marketing sliders
    const m_18_25 = parseFloat(document.getElementById('slide-m-18-25').value) / 100;
    const m_26_35 = parseFloat(document.getElementById('slide-m-26-35').value) / 100;
    const m_36_50 = parseFloat(document.getElementById('slide-m-36-50').value) / 100;
    const m_50 = parseFloat(document.getElementById('slide-m-50').value) / 100;

    // Update label text
    document.getElementById('val-m-18-25').innerText = (m_18_25 >= 0 ? '+' : '') + Math.round(m_18_25 * 100) + '%';
    document.getElementById('val-m-26-35').innerText = (m_26_35 >= 0 ? '+' : '') + Math.round(m_26_35 * 100) + '%';
    document.getElementById('val-m-36-50').innerText = (m_36_50 >= 0 ? '+' : '') + Math.round(m_36_50 * 100) + '%';
    document.getElementById('val-m-50').innerText = (m_50 >= 0 ? '+' : '') + Math.round(m_50 * 100) + '%';

    // Color labels (green for positive, red for negative)
    ['18-25', '26-35', '36-50', '50'].forEach(grp => {
        const val = parseFloat(document.getElementById('slide-m-' + grp).value);
        const el = document.getElementById('val-m-' + grp);
        if (el) {
            if (val > 0) { el.style.color = 'var(--accent-green)'; }
            else if (val < 0) { el.style.color = '#ef4444'; }
            else { el.style.color = 'var(--text-primary)'; }
        }
    });

    const categories = [...new Set(window.simulationBaseline.matrix.map(row => row.Category))];
    const categoryPriceChanges = {};
    const categoryDiscounts = {};

    categories.forEach(cat => {
        const catId = cat.replace(/\s+/g, '-');
        const priceSlide = document.getElementById('slide-p-' + catId);
        const discountSlide = document.getElementById('slide-d-' + catId);
        
        categoryPriceChanges[cat] = priceSlide ? parseFloat(priceSlide.value) / 100 : 0;
        categoryDiscounts[cat] = discountSlide ? parseFloat(discountSlide.value) / 100 : 0;

        // Update dynamic labels
        const pLabel = document.getElementById('val-p-' + catId);
        if (pLabel) {
            pLabel.innerText = (categoryPriceChanges[cat] >= 0 ? '+' : '') + Math.round(categoryPriceChanges[cat] * 100) + '%';
            if (categoryPriceChanges[cat] > 0) pLabel.style.color = 'var(--accent-green)';
            else if (categoryPriceChanges[cat] < 0) pLabel.style.color = '#ef4444';
            else pLabel.style.color = 'var(--text-primary)';
        }

        const dLabel = document.getElementById('val-d-' + catId);
        if (dLabel) {
            dLabel.innerText = Math.round(categoryDiscounts[cat] * 100) + '%';
            if (categoryDiscounts[cat] > 0) dLabel.style.color = 'var(--accent-green)';
            else dLabel.style.color = 'var(--text-primary)';
        }
    });

    // Run projection per cell
    let totalBaselineRevenue = 0;
    let totalProjectedRevenue = 0;
    let totalBaselineOrders = 0;
    let totalProjectedOrders = 0;
    let incrementalMarketingSpend = 0;
    let baselineMarketingSpend = 0;

    const ageProjections = { '18-25': { base: 0, proj: 0 }, '26-35': { base: 0, proj: 0 }, '36-50': { base: 0, proj: 0 }, '50+': { base: 0, proj: 0 } };
    const categoryProjections = {};
    categories.forEach(cat => { categoryProjections[cat] = { base: 0, proj: 0 }; });

    window.simulationBaseline.matrix.forEach(cell => {
        const age = cell.Age_Group;
        const cat = cell.Category;
        const baseRev = cell.revenue;
        const baseQty = cell.quantity;
        const baseOrd = cell.orders;

        totalBaselineRevenue += baseRev;
        totalBaselineOrders += baseOrd;

        ageProjections[age].base += baseRev;
        categoryProjections[cat].base += baseRev;

        // Marketing Multiplier
        let mChange = 0;
        if (age === '18-25') mChange = m_18_25;
        else if (age === '26-35') mChange = m_26_35;
        else if (age === '36-50') mChange = m_36_50;
        else if (age === '50+') mChange = m_50;

        const mElasticity = SIM_ELASTICITY.marketing[age] || 0.2;
        const mMultiplier = Math.pow(1 + mChange, mElasticity);

        // Price/Discount Multiplier
        const pChange = categoryPriceChanges[cat] || 0;
        const dRate = categoryDiscounts[cat] || 0;
        const netPriceRatio = (1 + pChange) * (1 - dRate);
        const pElasticity = SIM_ELASTICITY.price[cat] || SIM_ELASTICITY.price['default'];
        const qMultiplier = Math.pow(netPriceRatio, pElasticity);

        // Projected values
        const projQty = baseQty * mMultiplier * qMultiplier;
        const projOrd = baseOrd * mMultiplier * qMultiplier;
        const projRev = baseRev * mMultiplier * qMultiplier * netPriceRatio;

        totalProjectedRevenue += projRev;
        totalProjectedOrders += projOrd;

        ageProjections[age].proj += projRev;
        categoryProjections[cat].proj += projRev;
    });

    // Marketing ROI calculations
    // Assume baseline marketing spend is 10% of revenue for each age group
    ['18-25', '26-35', '36-50', '50+'].forEach(age => {
        const baseRev = ageProjections[age].base;
        const baseSpend = baseRev * 0.10;
        baselineMarketingSpend += baseSpend;

        let mChange = 0;
        if (age === '18-25') mChange = m_18_25;
        else if (age === '26-35') mChange = m_26_35;
        else if (age === '36-50') mChange = m_36_50;
        else if (age === '50+') mChange = m_50;

        incrementalMarketingSpend += baseSpend * mChange;
    });

    const revDelta = totalProjectedRevenue - totalBaselineRevenue;
    const revPct = totalBaselineRevenue > 0 ? (revDelta / totalBaselineRevenue) * 100 : 0;
    
    const ordDelta = totalProjectedOrders - totalBaselineOrders;
    const ordPct = totalBaselineOrders > 0 ? (ordDelta / totalBaselineOrders) * 100 : 0;

    // Update main KPIs
    document.getElementById('sim-revenue-val').innerText = '$' + totalProjectedRevenue.toLocaleString(undefined, {minimumFractionDigits: 2});
    const revPctBadge = document.getElementById('sim-revenue-pct');
    revPctBadge.innerText = (revDelta >= 0 ? '+' : '') + revPct.toFixed(2) + '%';
    revPctBadge.className = `rec-badge ${revDelta >= 0 ? 'rec-increase' : 'rec-hold'}`;

    document.getElementById('sim-orders-val').innerText = Math.round(totalProjectedOrders).toLocaleString();
    const ordPctBadge = document.getElementById('sim-orders-pct');
    ordPctBadge.innerText = (ordDelta >= 0 ? '+' : '') + ordPct.toFixed(2) + '%';
    ordPctBadge.className = `rec-badge ${ordDelta >= 0 ? 'rec-increase' : 'rec-hold'}`;

    const roiValEl = document.getElementById('sim-roi-val');
    const roiDescEl = document.getElementById('sim-roi-desc');
    
    if (incrementalMarketingSpend === 0) {
        roiValEl.innerText = '—';
        roiValEl.style.color = 'var(--text-secondary)';
        roiDescEl.innerText = 'No Spend Change';
    } else {
        const roi = revDelta / incrementalMarketingSpend;
        roiValEl.innerText = (roi >= 0 ? '+' : '') + roi.toFixed(1) + 'x';
        if (roi >= 2.0) {
            roiValEl.style.color = 'var(--accent-green)';
            roiDescEl.innerText = 'Highly Efficient';
        } else if (roi >= 1.0) {
            roiValEl.style.color = 'var(--accent-blue)';
            roiDescEl.innerText = 'Profitable';
        } else if (roi > 0) {
            roiValEl.style.color = 'var(--accent-orange)';
            roiDescEl.innerText = 'Diminishing Returns';
        } else {
            roiValEl.style.color = '#ef4444';
            roiDescEl.innerText = 'Net Loss';
        }
    }

    // Render / Update Charts
    updateSimulationCharts(ageProjections, categoryProjections);

    // Update Advice text
    generateSimulationInsights(m_18_25, m_26_35, m_36_50, m_50, categoryPriceChanges, categoryDiscounts, revDelta, revPct, incrementalMarketingSpend);
}

function updateSimulationCharts(ageProjections, categoryProjections) {
    const isLightMode = document.documentElement.classList.contains('light-mode');
    const labelColor = isLightMode ? '#4b5563' : '#9ca3af';
    const gridColor = isLightMode ? '#e5e7eb' : 'rgba(255, 255, 255, 0.08)';

    // Age Chart data
    const ageGroups = ['18-25', '26-35', '36-50', '50+'];
    const ageBaseData = ageGroups.map(grp => ageProjections[grp].base);
    const ageProjData = ageGroups.map(grp => ageProjections[grp].proj);

    initOrUpdateChart('simulationAgeChart', {
        type: 'bar',
        data: {
            labels: ageGroups,
            datasets: [
                {
                    label: 'Baseline Revenue ($)',
                    data: ageBaseData,
                    backgroundColor: 'rgba(99, 102, 241, 0.4)',
                    borderColor: '#6366f1',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    label: 'Projected Revenue ($)',
                    data: ageProjData,
                    backgroundColor: 'rgba(139, 92, 246, 0.85)',
                    borderColor: '#8b5cf6',
                    borderWidth: 1,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: labelColor, boxWidth: 10, font: { size: 10 } }
                },
                title: {
                    display: true,
                    text: 'Revenue Projection by Age Group',
                    color: labelColor,
                    font: { size: 12, weight: 'bold' }
                }
            },
            scales: {
                y: { grid: { color: gridColor }, ticks: { color: labelColor, font: { size: 9 } } },
                x: { grid: { display: false }, ticks: { color: labelColor, font: { size: 10 } } }
            }
        }
    });

    // Category Chart data
    const categories = Object.keys(categoryProjections).sort();
    const catBaseData = categories.map(cat => categoryProjections[cat].base);
    const catProjData = categories.map(cat => categoryProjections[cat].proj);

    initOrUpdateChart('simulationCategoryChart', {
        type: 'bar',
        data: {
            labels: categories,
            datasets: [
                {
                    label: 'Baseline Revenue ($)',
                    data: catBaseData,
                    backgroundColor: 'rgba(59, 130, 246, 0.4)',
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                    borderRadius: 4
                },
                {
                    label: 'Projected Revenue ($)',
                    data: catProjData,
                    backgroundColor: 'rgba(16, 185, 129, 0.85)',
                    borderColor: '#10b981',
                    borderWidth: 1,
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: labelColor, boxWidth: 10, font: { size: 10 } }
                },
                title: {
                    display: true,
                    text: 'Revenue Projection by Category',
                    color: labelColor,
                    font: { size: 12, weight: 'bold' }
                }
            },
            scales: {
                y: { grid: { color: gridColor }, ticks: { color: labelColor, font: { size: 9 } } },
                x: { grid: { display: false }, ticks: { color: labelColor, font: { size: 8 } } }
            }
        }
    });
}

function resetSimulationParameters() {
    // Reset marketing
    ['18-25', '26-35', '36-50', '50'].forEach(grp => {
        const slide = document.getElementById('slide-m-' + grp);
        if (slide) slide.value = 0;
    });

    if (window.simulationBaseline && window.simulationBaseline.matrix) {
        const categories = [...new Set(window.simulationBaseline.matrix.map(row => row.Category))];
        categories.forEach(cat => {
            const catId = cat.replace(/\s+/g, '-');
            const priceSlide = document.getElementById('slide-p-' + catId);
            const discountSlide = document.getElementById('slide-d-' + catId);
            if (priceSlide) priceSlide.value = 0;
            if (discountSlide) discountSlide.value = 0;
        });
    }

    updateSimulation();
    showToast('🔮 Simulation parameters reset to baseline values.', 'info');
}

function generateSimulationInsights(m_18_25, m_26_35, m_36_50, m_50, categoryPriceChanges, categoryDiscounts, revDelta, revPct, incrementalMarketingSpend) {
    const textContainer = document.getElementById('simulation-advisory-text');
    if (!textContainer) return;

    let html = '';

    if (revDelta === 0 && incrementalMarketingSpend === 0) {
        html = '<p>The simulator is currently running in baseline mode. Drag sliders on the left to simulate marketing actions, pricing changes, or discounts to project your revenue delta.</p>';
        textContainer.innerHTML = html;
        return;
    }

    html += `<p style="margin-bottom: 8px;"><strong>Outcome Summary:</strong> The simulated parameters yield a revenue change of <strong style="color: ${revDelta >= 0 ? 'var(--accent-green)' : '#ef4444'};">${revDelta >= 0 ? '+' : ''}$${Math.abs(revDelta).toLocaleString(undefined, {maximumFractionDigits: 2})} (${(revDelta >= 0 ? '+' : '')}${revPct.toFixed(2)}%)</strong>.</p>`;

    // Add specific marketing spend remarks
    let marketingRemarks = [];
    if (m_18_25 > 0) {
        marketingRemarks.push(`Increasing marketing spend on <strong>18-25 cohort</strong> by ${Math.round(m_18_25*100)}% capitalizes on their high elasticity (0.45), drawing in strong volume.`);
    }
    if (m_50 > 0.30) {
        marketingRemarks.push(`Increasing marketing spend on <strong>Seniors (50+)</strong> by ${Math.round(m_50*100)}% may see diminishing returns due to their lower elasticity (0.15). Consider shifting budget to younger brackets for better efficiency.`);
    }
    if (marketingRemarks.length > 0) {
        html += `<p style="margin-bottom: 6px;"><i class="fa-solid fa-bullhorn" style="color: var(--accent-purple); margin-right: 6px;"></i> ${marketingRemarks.join(' ')}</p>`;
    }

    // Add price elasticity remarks
    let pricingRemarks = [];
    Object.keys(categoryPriceChanges).forEach(cat => {
        const pChange = categoryPriceChanges[cat];
        if (pChange > 0.15 && cat === 'Electronics') {
            pricingRemarks.push(`Raising <strong>Electronics</strong> prices by ${Math.round(pChange*100)}% triggers an elastic volume contraction (-1.6 coefficient). This price hike reduces total electronics revenue despite the higher unit price.`);
        } else if (pChange > 0 && cat === 'Beauty') {
            pricingRemarks.push(`Raising <strong>Beauty</strong> prices by ${Math.round(pChange*100)}% increases revenue because beauty products are highly inelastic (-0.7 coefficient). Shoppers here show strong brand loyalty.`);
        } else if (pChange < -0.10 && cat === 'Electronics') {
            pricingRemarks.push(`Reducing <strong>Electronics</strong> prices by ${Math.round(Math.abs(pChange)*100)}% generates a substantial quantity surge (+1.6 elasticity), boosting overall category cash flow.`);
        }
    });

    if (pricingRemarks.length > 0) {
        html += `<p style="margin-bottom: 6px;"><i class="fa-solid fa-tags" style="color: var(--accent-blue); margin-right: 6px;"></i> ${pricingRemarks.join(' ')}</p>`;
    }

    // Add discount remarks
    let discountRemarks = [];
    Object.keys(categoryDiscounts).forEach(cat => {
        const dRate = categoryDiscounts[cat];
        if (dRate > 0.25) {
            discountRemarks.push(`The high discount of ${Math.round(dRate*100)}% on <strong>${cat}</strong> drives a large conversion volume, but drastically compresses unit margins, which may impact net profitability.`);
        }
    });

    if (discountRemarks.length > 0) {
        html += `<p style="margin-bottom: 6px;"><i class="fa-solid fa-percent" style="color: var(--accent-green); margin-right: 6px;"></i> ${discountRemarks.join(' ')}</p>`;
    }

    textContainer.innerHTML = html;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    let icon = '<i class="fa-solid fa-circle-info" style="color: var(--accent-blue);"></i>';
    if (type === 'success') icon = '<i class="fa-solid fa-circle-check" style="color: var(--accent-green);"></i>';
    if (type === 'error') icon = '<i class="fa-solid fa-circle-exclamation" style="color: #ef4444;"></i>';
    
    toast.innerHTML = `${icon} <span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        toast.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}


