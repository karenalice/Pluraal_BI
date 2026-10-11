# Pluraal BI - Plataforma Integrada de Dashboards Power BI

Plataforma corporativa e educacional para acesso e gestão de relatórios do **Power BI**, desenvolvida com base na arquitetura, identidade visual e modelo de autenticação do **Pluraal SaaS**.

---

## 🎯 Principais Funcionalidades

1. **Autenticação e Hierarquia Institucional**:
   - Tela de login idêntica ao ecossistema Pluraal SaaS.
   - Níveis hierárquicos: `Master`, `Administrador`, `uniao`, `associacao`, `escola`.
   - Barreira de segurança obrigatória para alteração de senha no primeiro acesso.
   - Suporte a expiração de data de login (`data_expiracao_login`).

2. **Regras de Negócio e Gestão de Permissões**:
   - **Master**:
     - Acesso a todos os relatórios cadastrados.
     - Pode criar, editar e desativar qualquer usuário.
     - Pode autorizar o **Administrador** a criar usuários (`pode_criar_usuario`).
     - É o **único que pode autorizar o Administrador a cadastrar novos links** do Power BI (`pode_criar_link`).
     - Pode cadastrar novos dashboards do Power BI.
   - **Administrador**:
     - Se autorizado com `pode_criar_usuario`: pode cadastrar usuários e atribuir links a eles.
     - Se autorizado com `pode_criar_link`: pode cadastrar novos relatórios do Power BI.
     - Não pode conceder permissões superiores a outros usuários.
   - **Demais Níveis (`uniao`, `associacao`, `escola`)**:
     - Acesso exclusivo de visualização aos links previamente atribuídos.

3. **Experiência do Usuário (Single vs. Multi Dashboard)**:
   - **Apenas 1 Dashboard Atribuído**: O sistema abre o relatório do Power BI diretamente em tela cheia com visualizador embutido e barra superior de contexto, **sem necessidade de passar pela Home**.
   - **Mais de 1 Dashboard Atribuído**: O sistema exibe o **Hub de Relatórios** com busca dinâmica em tempo real (com suporte a tecla ESC), contador de dashboards disponíveis, cópia rápida de URL com feedback visual e botão para visualização interna ou em nova aba.

4. **Multi-Banco (Supabase & MySQL)**:
   - Suporte completo a **Supabase (PostgreSQL)** e **MySQL** no schema/database `bi_pluraal`.
   - O PostgreSQL legado (`xwqllkbwtverxtxmqolb`) permanece **completamente intacto**.
   - Alternância simples via variável `DB_ENGINE=supabase` ou `DB_ENGINE=mysql` no `.env`.

---

## 📁 Estrutura de Pastas

```
pluraal link BI/
├── Backend/
│   ├── config/
│   │   └── settings.py             # Configurações do ambiente e JWT
│   ├── database/
│   │   ├── connection.py           # Conexão híbrida (Supabase PostgreSQL / MySQL)
│   │   └── migrate.py              # Script de migração e sincronização
│   ├── middleware/
│   │   └── auth_middleware.py      # Validação de token JWT e permissões
│   ├── routes/
│   │   ├── auth_routes.py          # Rotas de login, troca de senha e sessão
│   │   ├── hierarchy_routes.py     # Metadados de hierarquia e delegação
│   │   ├── link_routes.py          # Gestão de links e rotas de dashboards
│   │   └── user_routes.py          # Gestão e criação de usuários
│   └── server.py                   # Servidor Flask com rotas estáticas e API
├── Frontend/
│   ├── assets/
│   │   └── img/                    # Logos e ícones institucionais do Pluraal
│   ├── css/
│   │   ├── auth.css                # Estilização da tela de login
│   │   ├── base.css                # Estilos base
│   │   ├── bi.css                  # Estilos dos cards, viewer e modais do BI
│   │   ├── components.css          # Componentes visuais
│   │   ├── theme.css               # Tema Pluraal
│   │   ├── user-modal.css          # Estilos de modais
│   │   └── variables.css           # Variáveis de cor e tipografia
│   ├── js/
│   │   ├── api.js                  # Cliente HTTP e gerenciamento de token
│   │   ├── app.js                  # Orquestração do app e regras de exibição
│   │   ├── auth.js                 # Lógica de login e barreira de primeiro acesso
│   │   ├── bi.js                   # Cards, filtros e viewer do Power BI
│   │   └── users.js                # Gestão de usuários e cadastro de links
│   └── index.html                  # Interface principal da aplicação
├── .env                            # Credenciais de conexão (Supabase / MySQL)
├── .gitignore                      # Arquivos ignorados pelo Git
├── requirements.txt                # Dependências Python
└── run.py                          # Inicializador do projeto
```

---

## 🚀 Como Executar Localmente

1. **Instalar Dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Iniciar o Servidor**:
   ```bash
   python run.py
   ```
   Acesse no navegador: **`http://localhost:5050`**

---

## 🔄 Alternando Entre Supabase e MySQL

No arquivo `.env`:
- Para usar o **Supabase**:
  ```env
  DB_ENGINE=supabase
  ```
- Para usar o **MySQL**:
  ```env
  DB_ENGINE=mysql
  ```
Ambos os bancos já contêm as tabelas, usuários e os 17 dashboards iniciais configurados.
