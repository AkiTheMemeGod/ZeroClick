let appsData = [];
let filteredApps = [];
let installStatus = {};
let selectedAppsMap = new Map(); // PERSISTENT STATE: id -> app object

let currentCategory = 'All';
let searchQuery = '';
let statusInterval = null;

// DOM Elements
const appGrid = document.getElementById('app-grid');
const categoryNav = document.getElementById('category-nav');
const currentCategoryTitle = document.getElementById('current-category-title');
const searchInput = document.getElementById('search-input');
const selectAllBtn = document.getElementById('select-all');
const deselectAllBtn = document.getElementById('deselect-all');
const installBtn = document.getElementById('install-btn');
const clearSelectionBtn = document.getElementById('clear-selection');
const selectionDock = document.getElementById('selection-dock');
const dockAppsContainer = document.getElementById('dock-apps');
const statusContainer = document.getElementById('status-container');
const adminWarning = document.getElementById('admin-warning');
const downSpeedEl = document.getElementById('down-speed');
const upSpeedEl = document.getElementById('up-speed');
const downIcon = document.querySelector('.speed-icon.down');
const upIcon = document.querySelector('.speed-icon.up');
const generateBtn = document.getElementById('generate-btn');

// Initialization
async function fetchApps() {
    try {
        const response = await fetch('/apps');
        appsData = await response.json();
        renderSidebar();
        applyFilters();
    } catch (error) {
        appGrid.innerHTML = `<div class="loading" style="color: var(--error)">Error loading apps: ${error.message}</div>`;
    }
}

// Sidebar Rendering
function renderSidebar() {
    categoryNav.innerHTML = '';
    const categories = ['All', ...new Set(appsData.map(app => app.category || 'Other'))].sort();
    
    categories.forEach(cat => {
        const count = cat === 'All' ? appsData.length : appsData.filter(a => (a.category || 'Other') === cat).length;
        const navItem = document.createElement('div');
        navItem.className = `nav-item ${currentCategory === cat ? 'active' : ''}`;
        navItem.innerHTML = `
            <span>${cat}</span>
            <span class="count-badge">${count}</span>
        `;
        
        navItem.onclick = () => {
            currentCategory = cat;
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            navItem.classList.add('active');
            currentCategoryTitle.textContent = cat === 'All' ? 'All Applications' : cat;
            applyFilters();
        };
        categoryNav.appendChild(navItem);
    });
}

// Filtering Logic
function applyFilters() {
    filteredApps = appsData.filter(app => {
        const matchesCategory = currentCategory === 'All' || (app.category || 'Other') === currentCategory;
        const matchesSearch = app.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                             (app.id && app.id.toLowerCase().includes(searchQuery.toLowerCase()));
        return matchesCategory && matchesSearch;
    });
    renderGrid();
}

// Grid Rendering
function renderGrid() {
    appGrid.innerHTML = '';
    
    if (filteredApps.length === 0) {
        appGrid.innerHTML = '<div class="loading">No applications found.</div>';
        return;
    }
    
    filteredApps.forEach(app => {
        const isSelected = selectedAppsMap.has(app.id);
        const card = document.createElement('div');
        card.className = `app-card ${isSelected ? 'selected' : ''}`;
        card.dataset.id = app.id;
        
        const iconSrc = app.icon_url || `https://www.google.com/s2/favicons?domain=microsoft.com&sz=64`;
        
        card.innerHTML = `
            <img src="${iconSrc}" class="app-icon" alt="${app.name}" onerror="this.src='https://www.google.com/s2/favicons?domain=microsoft.com&sz=64'">
            <div class="app-info">
                <h3>${app.name}</h3>
                <p>${app.category || 'Utility'}</p>
            </div>
            <input type="checkbox" class="app-checkbox" ${isSelected ? 'checked' : ''}>
        `;
        
        card.onclick = () => {
            toggleAppSelection(app);
        };
        
        appGrid.appendChild(card);
    });
}

// Selection Logic
function toggleAppSelection(app) {
    if (selectedAppsMap.has(app.id)) {
        selectedAppsMap.delete(app.id);
    } else {
        selectedAppsMap.set(app.id, app);
    }
    
    // Update the card in the grid if it exists
    const card = document.querySelector(`.app-card[data-id="${app.id}"]`);
    if (card) {
        const isSelected = selectedAppsMap.has(app.id);
        card.classList.toggle('selected', isSelected);
        card.querySelector('.app-checkbox').checked = isSelected;
    }
    
    renderSelectionDock();
}

function renderSelectionDock() {
    const count = selectedAppsMap.size;
    
    if (count === 0) {
        selectionDock.classList.remove('visible');
        setTimeout(() => { if (selectedAppsMap.size === 0) selectionDock.classList.add('hidden'); }, 500);
        return;
    }
    
    selectionDock.classList.remove('hidden');
    // small delay to ensure 'visible' transition works
    setTimeout(() => selectionDock.classList.add('visible'), 10);
    
    dockAppsContainer.innerHTML = '';
    selectedAppsMap.forEach(app => {
        const iconSrc = app.icon_url || `https://www.google.com/s2/favicons?domain=microsoft.com&sz=64`;
        const img = document.createElement('img');
        img.src = iconSrc;
        img.className = 'mini-icon';
        img.title = app.name;
        img.onclick = (e) => {
            e.stopPropagation();
            toggleAppSelection(app);
        };
        dockAppsContainer.appendChild(img);
    });
    
    installBtn.innerHTML = `Install ${count} App${count > 1 ? 's' : ''}`;
}

// Global Handlers
searchInput.oninput = (e) => {
    searchQuery = e.target.value;
    applyFilters();
};

selectAllBtn.onclick = () => {
    filteredApps.forEach(app => {
        if (!selectedAppsMap.has(app.id)) {
            selectedAppsMap.set(app.id, app);
        }
    });
    renderGrid();
    renderSelectionDock();
};

deselectAllBtn.onclick = () => {
    filteredApps.forEach(app => {
        selectedAppsMap.delete(app.id);
    });
    renderGrid();
    renderSelectionDock();
};

clearSelectionBtn.onclick = () => {
    selectedAppsMap.clear();
    renderGrid();
    renderSelectionDock();
};

// Installation Execution
installBtn.onclick = async () => {
    const selectedIds = Array.from(selectedAppsMap.keys());
    if (selectedIds.length === 0) return;
    
    try {
        installBtn.disabled = true;
        const response = await fetch('/install', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ app_ids: selectedIds })
        });
        
        const data = await response.json();
        if (!data.admin) adminWarning.classList.remove('hidden');
        
        if (!statusInterval) statusInterval = setInterval(pollStatus, 1500);
        pollStatus();
        
        // Optionally clear selection after starting install
        // selectedAppsMap.clear();
        // renderGrid();
        // renderSelectionDock();
        
    } catch (error) {
        console.error('Install launch error:', error);
    }
};

// EXE Generation Execution
generateBtn.onclick = async () => {
    const selectedIds = Array.from(selectedAppsMap.keys());
    if (selectedIds.length === 0) return;
    
    try {
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Building...';
        
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ app_ids: selectedIds })
        });
        
        if (!response.ok) throw new Error('Build failed');
        
        // Trigger browser download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "ZeroClickInstaller.exe";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
        generateBtn.innerHTML = '<i class="fas fa-check"></i> Ready!';
        setTimeout(() => {
            generateBtn.disabled = false;
            generateBtn.innerHTML = 'Get Your Installer';
        }, 3000);
        
    } catch (error) {
        console.error('Generation error:', error);
        generateBtn.innerHTML = 'Error Building';
        generateBtn.classList.add('error');
        setTimeout(() => {
            generateBtn.disabled = false;
            generateBtn.innerHTML = 'Get Your Installer';
            generateBtn.classList.remove('error');
        }, 3000);
    }
};

async function pollStatus() {
    try {
        const response = await fetch('/status');
        installStatus = await response.json();
        
        const statusIds = Object.keys(installStatus);
        if (statusIds.length === 0) return;
        
        statusContainer.innerHTML = '';
        let active = false;
        
        statusIds.forEach(appId => {
            const data = installStatus[appId];
            const app = appsData.find(a => a.id === appId);
            const name = app ? app.name : appId;
            
            const item = document.createElement('div');
            item.className = `status-item ${data.status}`;
            const progress = data.progress || 0;
            
            item.innerHTML = `
                <div class="status-header">
                    <span class="status-name">${name}</span>
                    <span class="status-msg">${data.message}</span>
                </div>
                <div class="progress-container">
                    <div class="progress-fill" style="width: ${progress}%"></div>
                </div>
            `;
            
            statusContainer.appendChild(item);
            if (['pending', 'downloading', 'installing', 'verifying'].includes(data.status)) {
                active = true;
            }
        });
        
        if (!active) {
            clearInterval(statusInterval);
            statusInterval = null;
            installBtn.disabled = false;
            installBtn.innerHTML = 'Install Selected';
        }
    } catch (error) {
        console.error('Polling error:', error);
    }
}

async function updateNetworkSpeed() {
    try {
        const response = await fetch('/network-speed');
        if (!response.ok) throw new Error('Speed API not ready');
        
        const data = await response.json();
        if (!data || !data.download) return;

        downSpeedEl.textContent = data.download;
        upSpeedEl.textContent = data.upload;
        
        const downValue = parseFloat(data.download) || 0;
        const upValue = parseFloat(data.upload) || 0;
        
        downIcon.style.animationDuration = downValue > 0 ? '1s' : '3s';
        upIcon.style.animationDuration = upValue > 0 ? '1s' : '3s';
        
    } catch (error) {
        // Silently handle polling errors until server restarts
        downSpeedEl.textContent = '---';
        upSpeedEl.textContent = '---';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchApps();
    setInterval(updateNetworkSpeed, 2000);
});
