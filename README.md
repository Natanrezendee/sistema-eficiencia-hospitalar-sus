# Sistema de Eficiência Hospitalar - SUS 🏥

**Avaliação 2 - Universidade (UBD)**

Sistema web para gerenciamento de atendimentos, pacientes e métricas hospitalares em conformidade com o protocolo de triagem de Manchester.

---

## 📋 Funcionalidades

✅ **Cadastro de Pacientes** - Digite os dados completos do paciente na hora do atendimento  
✅ **Cadastro de Atendimentos** - Registre admissões, triagem, diagnósticos e desfechos  
✅ **Cadastro de Hospital** - Modal para adicionar novos hospitais sem sair do formulário  
✅ **Cadastro de Médico** - Modal para adicionar novos médicos durante o atendimento  
✅ **Métricas de Monitoramento** - Dashboard com total de atendimentos, casos críticos e taxa de letalidade  
✅ **Classificação de Risco** - Protocolo de Manchester (Vermelho, Laranja, Amarelo, Verde, Azul)  
✅ **Registro de Óbitos** - Campos específicos para data, hora e causa do óbito  
✅ **Edição e Exclusão** - Modificar ou remover registros de atendimento  
✅ **Responsivo** - Design bonito e funcional em Desktop/Mobile  

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.10+ com Flask
- **Banco de Dados:** MySQL 8.0+
- **Frontend:** HTML5, CSS3 (Bootstrap 5), JavaScript
- **ORM:** SQLAlchemy
- **Servidor:** Flask Development Server (produção: Gunicorn)

---

## 📦 Pré-requisitos

```bash
Python 3.10+
MySQL 8.0+
pip (gerenciador de pacotes Python)
```

---

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/sistema-eficiencia-hospitalar.git
cd sistema-eficiencia-hospitalar
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install flask sqlalchemy pymysql
```

### 4. Configure o banco de dados

#### 4.1 Crie o banco de dados
```bash
mysql -u root -p < script_banco.sql
```

#### 4.2 Configure as credenciais em `app.py`
```python
DB_USER = "seu_usuario"
DB_PASSWORD = "sua_senha"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "eficiencia_hospitalar"
```

### 5. Organize as pastas
```
seu_projeto/
├── app.py
├── static/
│   └── background.jpg
└── templates/
    ├── index.html
    ├── formulario.html
```

### 6. Execute a aplicação
```bash
python app.py
```

Acesse em: **http://localhost:5000**

---

## 📊 Estrutura do Banco de Dados

### Tabelas Principais

#### `hospital`
- id_hospital (PK)
- cnpj (UNIQUE)
- nome
- cidade
- endereco
- capacidade_leitos

#### `medico`
- id_medico (PK)
- crm (UNIQUE)
- nome
- telefone
- especialidade

#### `paciente`
- id_paciente (PK)
- cns (UNIQUE)
- cpf (UNIQUE)
- nome
- data_nascimento
- sexo (M/F/Outro)
- telefone

#### `atendimento`
- id_atendimento (PK)
- id_paciente (FK)
- id_hospital (FK)
- id_medico (FK)
- data_hora_entrada
- triagem (Vermelho/Laranja/Amarelo/Verde/Azul)
- sintomas
- diagnostico
- desfecho (Alta médica/Evasão/Transferência/Óbito)
- causa_obito (NULL se desfecho ≠ Óbito)
- data_obito (NULL se desfecho ≠ Óbito)

---

## 🔑 Rotas Principais

| Rota | Método | Descrição |
|------|--------|-----------|
| `/` | GET | Dashboard com métricas e lista de atendimentos |
| `/novo` | GET/POST | Formulário para novo atendimento |
| `/editar/<id>` | GET/POST | Editar atendimento existente |
| `/deletar/<id>` | GET | Deletar atendimento |
| `/criar_hospital` | POST | Criar novo hospital (AJAX) |
| `/criar_medico` | POST | Criar novo médico (AJAX) |

---

## 📱 Como Usar

### 1. **Registrar Novo Atendimento**
   - Clique em "Registrar Novo Atendimento"
   - Preencha os dados do paciente
   - Se o hospital não existir, clique no botão `+` ao lado da dropdown
   - Se o médico não existir, clique no botão `+` ao lado da dropdown
   - Preencha os dados clínicos (triagem, sintomas, diagnóstico)
   - Selecione o desfecho
   - Se for Óbito, preencha data e causa
   - Clique em "Confirmar e Salvar"

### 2. **Editar Atendimento**
   - Clique no ícone ✏️ na tabela
   - Modifique os dados desejados (dados do paciente são read-only)
   - Clique em "Confirmar e Salvar"

### 3. **Deletar Atendimento**
   - Clique no ícone 🗑️ na tabela
   - Confirme a exclusão

---

## 🎨 Design & Interface

- **Navbar:** Azul institucional do SUS (#003366)
- **Cards de Métrica:** 3 indicadores principais com gradiente de cor
- **Tabela:** Responsiva com cores de triagem destacadas
- **Modais:** Bootstrap com validação em tempo real
- **Fundo:** Imagem desfocada com degradê para melhor legibilidade

---

## 🐛 Validações Implementadas

✅ CPF e CNS únicos por paciente  
✅ CNPJ único por hospital  
✅ CRM único por médico  
✅ Campos obrigatórios validados  
✅ Data de óbito não pode ser anterior à entrada  
✅ Causa do óbito obrigatória se desfecho = Óbito  
✅ Validação via Triggers MySQL  

---

## 📞 Suporte

Qualquer dúvida ou bug encontrado, abra uma **Issue** no GitHub.

---

## 📝 Licença

Este projeto é um trabalho acadêmico.

---

## 👨‍💻 Autor

**Natan**  
Curso: ubd  
Data: 2026

---

## 📸 Screenshots

*(Adicione prints do dashboard, formulário e banco de dados aqui na hora de enviar)*

---

**Repositório:** [GitHub Link](seu-repo-link)