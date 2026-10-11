// Dashboard Hub and Power BI Viewer Logic

let currentDashboards = [];
let activeViewingDashboard = null;

function escaparHTML(texto) {
  return String(texto ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function normalizarPesquisa(texto) {
  return String(texto ?? "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .trim();
}

function encurtarLink(link) {
  const inicio = 38;
  const fim = 16;
  if (!link) return "";
  if (link.length <= inicio + fim + 3) return link;
  return link.substring(0, inicio) + "..." + link.substring(link.length - fim);
}

async function copiarLink(link, botao) {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(link);
    } else {
      const textarea = document.createElement("textarea");
      textarea.value = link;
      textarea.style.position = "fixed";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }
    mostrarCopiado(botao);
  } catch (erro) {
    console.error(erro);
    alert("Não foi possível copiar o link.");
  }
}

function mostrarCopiado(botao) {
  const original = botao.innerHTML;
  botao.classList.add("copiado");
  botao.innerHTML = `
    <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
      <path d="M5 12L10 17L19 7" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `;
  botao.title = "Link copiado";
  setTimeout(() => {
    botao.innerHTML = original;
    botao.title = "Copiar link";
    botao.classList.remove("copiado");
  }, 1500);
}

function abrirDashboard(dashboard) {
  activeViewingDashboard = dashboard;
  const hubView = document.getElementById("hubView");
  const biView = document.getElementById("biView");
  const usersView = document.getElementById("usersView");
  const iframe = document.getElementById("biIframe");
  const titleEl = document.getElementById("biViewerTitle");
  const backBtn = document.getElementById("biBackToHubBtn");

  hubView.classList.add("hidden");
  usersView.classList.add("hidden");
  biView.classList.remove("hidden");

  titleEl.textContent = dashboard.nome;
  iframe.src = dashboard.link;

  // Show or hide "Voltar" button depending on how many dashboards user has or if manager
  const user = API.getUser();
  const hasMultiple = currentDashboards.length > 1;
  const isManager = user && (user.hierarquia === "Master" || user.pode_criar_usuario || user.pode_criar_link);

  if (hasMultiple || isManager) {
    backBtn.classList.remove("hidden");
  } else {
    backBtn.classList.add("hidden");
  }
}

function fecharDashboard() {
  const hubView = document.getElementById("hubView");
  const biView = document.getElementById("biView");
  const iframe = document.getElementById("biIframe");

  iframe.src = "about:blank";
  biView.classList.add("hidden");
  hubView.classList.remove("hidden");
  activeViewingDashboard = null;
}

function criarCard(dashboard) {
  const card = document.createElement("div");
  card.className = "dashboard-card";

  const nomeSeguro = escaparHTML(dashboard.nome);
  const linkSeguro = escaparHTML(dashboard.link);
  const linkCurto = escaparHTML(encurtarLink(dashboard.link));
  const monograma = (dashboard.nome || "BI").substring(0, 2).toUpperCase();

  card.innerHTML = `
    <div class="card-header">
      <div class="card-title-group">
        <div class="card-unit-badge">${monograma}</div>
        <div class="card-title-area">
          <h3>${nomeSeguro}</h3>
          <div style="font-size: 0.72rem; color: #82c673; display: flex; align-items: center; gap: 5px; margin-top: 2px;">
            <span class="bi-stats-dot"></span> Relatório Ativo
          </div>
        </div>
      </div>
      <a href="${linkSeguro}" target="_blank" rel="noopener noreferrer" class="icon-box" title="Abrir em nova aba">
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M14 4H20V10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M10 14L20 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M20 14V20H4V4H10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </a>
    </div>

    <p class="card-description">
      ${dashboard.descricao ? escaparHTML(dashboard.descricao) : "Acesse os indicadores e gráficos consolidados do Power BI."}
    </p>

    <div class="card-actions-area">
      <button type="button" class="btn-open-embed" title="Visualizar na plataforma">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        <span>Visualizar Dashboard</span>
      </button>
    </div>

    <div class="dashboard-link-area">
      <a href="${linkSeguro}" target="_blank" rel="noopener noreferrer" class="dashboard-link-text" title="${linkSeguro}">
        ${linkCurto}
      </a>
      <button type="button" class="btn-copiar-link" title="Copiar link do Power BI">
        <svg viewBox="0 0 24 24" fill="none">
          <rect x="9" y="9" width="10" height="10" rx="2" stroke="currentColor" stroke-width="2"/>
          <path d="M15 9V6C15 4.9 14.1 4 13 4H6C4.9 4 4 4.9 4 6V13C4 14.1 4.9 15 6 15H9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
  `;

  // Attach card open action
  card.querySelector(".btn-open-embed").addEventListener("click", () => {
    abrirDashboard(dashboard);
  });

  // Attach copy button action
  const botaoCopiar = card.querySelector(".btn-copiar-link");
  botaoCopiar.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    copiarLink(dashboard.link, botaoCopiar);
  });

  return card;
}

function renderizarDashboards(lista) {
  const listaDashboards = document.getElementById("listaDashboards");
  const quantidadeDashboards = document.getElementById("quantidadeDashboards");
  const nenhumResultado = document.getElementById("nenhumResultado");

  if (!listaDashboards) return;
  listaDashboards.innerHTML = "";

  quantidadeDashboards.textContent = `${lista.length} ${
    lista.length === 1 ? "dashboard disponível" : "dashboards disponíveis"
  }`;

  if (lista.length === 0) {
    nenhumResultado.classList.remove("hidden");
    return;
  }
  nenhumResultado.classList.add("hidden");

  lista.forEach(dash => {
    listaDashboards.appendChild(criarCard(dash));
  });
}

function filtrarDashboards() {
  const campoPesquisa = document.getElementById("campoPesquisa");
  if (!campoPesquisa) return;

  const busca = normalizarPesquisa(campoPesquisa.value);
  const filtrados = currentDashboards.filter(d =>
    normalizarPesquisa(d.nome).includes(busca)
  );
  renderizarDashboards(filtrados);
}

// Attach Search Listeners
document.addEventListener("DOMContentLoaded", () => {
  const campoPesquisa = document.getElementById("campoPesquisa");
  if (campoPesquisa) {
    campoPesquisa.addEventListener("input", filtrarDashboards);
    campoPesquisa.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        campoPesquisa.value = "";
        renderizarDashboards(currentDashboards);
      }
    });
  }

  const backBtn = document.getElementById("biBackToHubBtn");
  if (backBtn) {
    backBtn.addEventListener("click", fecharDashboard);
  }
});
