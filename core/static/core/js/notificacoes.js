const API_BASE_URL = '/api/notificacao/'; 
const API_UNREAD_COUNT_URL = `${API_BASE_URL}nao_lidas/`; 

// Agrupamento de Elementos DOM
const [notificationList, unreadCountElement, loadingMessage, errorMessage, emptyMessage, markAllReadBtn] = [
    'notification-list', 'unred-count', 'loading-message', 'error-message', 'empty-message', 'mark-all-read-btn'
].map(id => document.getElementById(id));

// --- 1. FUNÇÕES DE UTILIDADE ---

// Função auxiliar padrão do Django para obter o CSRF token
const getCookie = name => {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return null;
};

const formatarData = dateString => {
    if (!dateString) return 'Data Indisponível';
    try {
        return new Date(dateString).toLocaleDateString('pt-BR', { year: 'numeric', month: 'long', day: 'numeric' });
    } catch (e) {
        return dateString;
    }
};

const getIconClass = tipo => {
    switch (tipo) {
        case 'PEDIDO': return 'fas fa-box';
        case 'PROMOCAO': return 'fas fa-fire';
        case 'CUPOM': return 'fas fa-tag';
        case 'NOVIDADE': return 'fas fa-bolt';
        default: return 'fas fa-bell';
    }
};

// --- 2. FUNÇÕES DE INTERAÇÃO COM A API ---

async function fetchUnreadCount() {
    try {
        const response = await fetch(API_UNREAD_COUNT_URL);
        const data = await response.json();
        const count = data.count || 0;
        
        unreadCountElement.textContent = count;
        markAllReadBtn.disabled = count === 0;
    } catch (error) {
        console.error("Erro ao buscar contagem:", error);
    }
}

async function marcarComoLida(itemElement) {
    const notificacaoId = itemElement.dataset.id;
    const url = `${API_BASE_URL}${notificacaoId}/marcar_lida/`;

    try {
        const response = await fetch(url, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
        });
        
        if (response.ok) {
            itemElement.classList.replace('status-nao-lida', 'status-lida');
            itemElement.querySelector('.read-indicator')?.remove();

            await fetchUnreadCount(); 
            window.location.href = itemElement.href;
        } else {
            console.error('Falha ao marcar como lida:', response.statusText);
        }
    } catch (error) {
        console.error("Erro de rede:", error);
    }
}

// --- 3. RENDERIZAÇÃO E PREENCHIMENTO ---

const renderizarItem = item => {
    const { lida, tipo, titulo, mensagem, url_destino, data_criacao, id } = item;
    const statusClass = lida ? 'status-lida' : 'status-nao-lida';
    const iconClass = getIconClass(tipo);
    const href = url_destino || '#';

    return `
        <a href="${href}" class="notification-item tipo-${tipo} ${statusClass}" data-id="${id}">
            <div class="icon-wrapper"><i class="${iconClass}"></i></div>
            <div class="content-wrapper">
                <h2 class="title">${titulo}</h2>
                <p class="message">${mensagem}</p>
                <span class="date">Criado em: ${formatarData(data_criacao)}</span>
            </div>
            ${!lida ? '<span class="read-indicator"></span>' : ''}
        </a>
    `;
};

function preencherLista(notificacoes) {
    loadingMessage.classList.add('hidden');
    errorMessage.classList.add('hidden');
    
    if (!notificacoes || notificacoes.length === 0) {
        emptyMessage.classList.remove('hidden');
        markAllReadBtn.disabled = true;
        return;
    }

    emptyMessage.classList.add('hidden');
    
    // Constrói o HTML usando map e join (sintaxe limpa)
    const htmlContent = notificacoes.map(renderizarItem).join('');
    notificationList.innerHTML = htmlContent;

    // Atribui eventos de clique apenas para itens não lidos
    document.querySelectorAll('.notification-item.status-nao-lida').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault(); 
            marcarComoLida(item);
        });
    });
}

// --- 4. FUNÇÃO PRINCIPAL DE INICIALIZAÇÃO ---

async function initNotificacoes() {
    try {
        const response = await fetch(API_BASE_URL);

        if (!response.ok) {
            throw new Error('Falha ao buscar a lista.');
        }

        const data = await response.json();
        
        // Trata a paginação do DRF, se houver (acessando data.results)
        const notificacoes = Array.isArray(data) ? data : data.results || [];
        
        preencherLista(notificacoes);
        fetchUnreadCount();
    } catch (error) {
        console.error("Erro fatal:", error);
        loadingMessage.classList.add('hidden');
        errorMessage.classList.remove('hidden');
    }
}

// --- 5. EVENT LISTENERS ---

markAllReadBtn.addEventListener('click', () => {
    alert("Função 'Marcar Todas como Lidas' não implementada no servidor.");
});

document.addEventListener('DOMContentLoaded', initNotificacoes);