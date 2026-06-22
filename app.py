from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

app = Flask(__name__)

# =====================================================
# CONFIGURAÇÃO DA CONEXÃO COM O MYSQL
# =====================================================
DB_USER = "root"
DB_PASSWORD = "******"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "eficiencia_hospitalar"

connection_url = URL.create(
    "mysql+pymysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)

engine = create_engine(connection_url, pool_pre_ping=True)


def get_connection():
    return engine.connect()


def calcular_metricas():
    with get_connection() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM atendimento")).scalar() or 0

        if total == 0:
            return {"total": 0, "taxa_criticos": 0, "taxa_mortalidade": 0}

        obitos = conn.execute(
            text("SELECT COUNT(*) FROM atendimento WHERE desfecho = 'Óbito'")
        ).scalar() or 0
        
        criticos = conn.execute(
            text("SELECT COUNT(*) FROM atendimento WHERE triagem IN ('Vermelho', 'Laranja')")
        ).scalar() or 0

        return {
            "total": total,
            "taxa_criticos": round((criticos / total) * 100, 1),
            "taxa_mortalidade": round((obitos / total) * 100, 1),
        }


def buscar_atendimentos():
    with get_connection() as conn:
        rows = conn.execute(text("""
            SELECT 
                a.id_atendimento, 
                p.nome AS nome_paciente, 
                p.cpf,
                h.nome AS nome_hospital, 
                m.nome AS nome_medico,
                a.data_hora_entrada, 
                a.triagem, 
                a.sintomas, 
                a.diagnostico,
                a.desfecho, 
                a.causa_obito, 
                a.data_obito,
                a.id_paciente,
                a.id_hospital,
                a.id_medico
            FROM atendimento a
            INNER JOIN paciente p ON a.id_paciente = p.id_paciente
            INNER JOIN hospital h ON a.id_hospital = h.id_hospital
            INNER JOIN medico m ON a.id_medico = m.id_medico
            ORDER BY a.id_atendimento DESC
        """)).mappings().all()
        return [dict(r) for r in rows]


def buscar_atendimento_por_id(id_atendimento):
    with get_connection() as conn:
        row = conn.execute(text("""
            SELECT a.id_atendimento, a.id_paciente, a.id_hospital, a.id_medico,
                   a.data_hora_entrada, a.triagem, a.sintomas, a.diagnostico,
                   a.desfecho, a.causa_obito, a.data_obito,
                   p.cns, p.cpf, p.nome AS nome_paciente, p.data_nascimento, p.sexo, p.telefone
            FROM atendimento a
            INNER JOIN paciente p ON a.id_paciente = p.id_paciente
            WHERE a.id_atendimento = :id
        """), {"id": id_atendimento}).mappings().first()
        return dict(row) if row else None


def buscar_listas_auxiliares():
    """Busca os dados de apoio do banco para alimentar as caixas de seleção do formulário"""
    with get_connection() as conn:
        hospitais = conn.execute(text("SELECT id_hospital, nome FROM hospital ORDER BY nome")).mappings().all()
        medicos = conn.execute(text("SELECT id_medico, nome FROM medico ORDER BY nome")).mappings().all()
        return [dict(h) for h in hospitais], [dict(m) for m in medicos]


def criar_paciente(cns, cpf, nome, data_nascimento, sexo, telefone):
    """Cria um novo paciente e retorna o ID gerado"""
    with engine.begin() as conn:
        resultado = conn.execute(text("""
            INSERT INTO paciente (cns, cpf, nome, data_nascimento, sexo, telefone)
            VALUES (:cns, :cpf, :nome, :data_nascimento, :sexo, :telefone)
        """), {
            "cns": cns,
            "cpf": cpf,
            "nome": nome,
            "data_nascimento": data_nascimento,
            "sexo": sexo,
            "telefone": telefone if telefone else None,
        })
        return resultado.lastrowid


def criar_hospital(cnpj, nome, cidade, endereco, capacidade_leitos):
    """Cria um novo hospital e retorna o ID gerado"""
    with engine.begin() as conn:
        resultado = conn.execute(text("""
            INSERT INTO hospital (cnpj, nome, cidade, endereco, capacidade_leitos)
            VALUES (:cnpj, :nome, :cidade, :endereco, :capacidade_leitos)
        """), {
            "cnpj": cnpj,
            "nome": nome,
            "cidade": cidade,
            "endereco": endereco,
            "capacidade_leitos": capacidade_leitos,
        })
        return resultado.lastrowid


def criar_medico(crm, nome, telefone, especialidade):
    """Cria um novo médico e retorna o ID gerado"""
    with engine.begin() as conn:
        resultado = conn.execute(text("""
            INSERT INTO medico (crm, nome, telefone, especialidade)
            VALUES (:crm, :nome, :telefone, :especialidade)
        """), {
            "crm": crm,
            "nome": nome,
            "telefone": telefone if telefone else None,
            "especialidade": especialidade if especialidade else None,
        })
        return resultado.lastrowid


def formatar_datetime_para_input(valor):
    if not valor:
        return ""
    if isinstance(valor, str):
        return valor.replace(" ", "T")[:16]
    return valor.strftime("%Y-%m-%dT%H:%M")


def formatar_date_para_input(valor):
    if not valor:
        return ""
    if isinstance(valor, str):
        return valor[:10]
    return valor.strftime("%Y-%m-%d")


@app.route('/')
def index():
    metricas = calcular_metricas()
    atendimentos = buscar_atendimentos()
    return render_template('index.html', atendimentos=atendimentos, metricas=metricas)


@app.route('/novo', methods=['GET', 'POST'])
def novo_atendimento():
    if request.method == 'POST':
       
        try:
            id_paciente = criar_paciente(
                cns=request.form['paciente_cns'],
                cpf=request.form['paciente_cpf'],
                nome=request.form['paciente_nome'],
                data_nascimento=request.form['paciente_data_nascimento'],
                sexo=request.form['paciente_sexo'],
                telefone=request.form.get('paciente_telefone', '')
            )
        except Exception as e:
           
            hospitais, medicos = buscar_listas_auxiliares()
            data_atual = datetime.now().strftime("%Y-%m-%dT%H:%M")
            return render_template('formulario.html', 
                                 acao="Cadastrar", 
                                 at=None,
                                 data_atual=data_atual, 
                                 hospitais=hospitais, 
                                 medicos=medicos,
                                 erro=f"Erro ao cadastrar paciente: {str(e)}")

        entrada = request.form['data_hora_entrada'].replace('T', ' ')
        desfecho = request.form.get('desfecho') or request.form.get('situacao_saida')

        causa_obito = request.form.get('causa_obito') or None
        data_obito_raw = request.form.get('data_obito') or None
        data_obito = data_obito_raw.replace('T', ' ') if data_obito_raw else None

        if desfecho != 'Óbito':
            causa_obito = None
            data_obito = None

        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO atendimento
                    (id_paciente, id_hospital, id_medico, data_hora_entrada,
                     triagem, sintomas, diagnostico,
                     desfecho, causa_obito, data_obito)
                VALUES
                    (:id_paciente, :id_hospital, :id_medico, :data_hora_entrada,
                     :triagem, :sintomas, :diagnostico,
                     :desfecho, :causa_obito, :data_obito)
            """), {
                "id_paciente": id_paciente,
                "id_hospital": request.form['id_hospital'],
                "id_medico": request.form['id_medico'],
                "data_hora_entrada": entrada,
                "triagem": request.form['triagem'],
                "sintomas": request.form['sintomas'],
                "diagnostico": request.form['diagnostico'],
                "desfecho": desfecho,
                "causa_obito": causa_obito,
                "data_obito": data_obito,
            })

        return redirect(url_for('index'))

    
    hospitais, medicos = buscar_listas_auxiliares()
    data_atual = datetime.now().strftime("%Y-%m-%dT%H:%M")
    
    return render_template('formulario.html', 
                         acao="Cadastrar", 
                         at=None, 
                         data_atual=data_atual,
                         hospitais=hospitais, 
                         medicos=medicos,
                         erro=None)


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_atendimento(id):
    at = buscar_atendimento_por_id(id)

    if request.method == 'POST' and at:
        entrada = request.form['data_hora_entrada'].replace('T', ' ')
        desfecho = request.form.get('desfecho') or request.form.get('situacao_saida')

        causa_obito = request.form.get('causa_obito') or None
        data_obito_raw = request.form.get('data_obito') or None
        data_obito = data_obito_raw.replace('T', ' ') if data_obito_raw else None

        if desfecho != 'Óbito':
            causa_obito = None
            data_obito = None

        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE atendimento
                SET id_hospital = :id_hospital,
                    id_medico = :id_medico,
                    data_hora_entrada = :data_hora_entrada,
                    triagem = :triagem,
                    sintomas = :sintomas,
                    diagnostico = :diagnostico,
                    desfecho = :desfecho,
                    causa_obito = :causa_obito,
                    data_obito = :data_obito
                WHERE id_atendimento = :id_atendimento
            """), {
                "id_hospital": request.form['id_hospital'],
                "id_medico": request.form['id_medico'],
                "data_hora_entrada": entrada,
                "triagem": request.form['triagem'],
                "sintomas": request.form['sintomas'],
                "diagnostico": request.form['diagnostico'],
                "desfecho": desfecho,
                "causa_obito": causa_obito,
                "data_obito": data_obito,
                "id_atendimento": id,
            })

        return redirect(url_for('index'))

    if at:
        at['entrada_html'] = formatar_datetime_para_input(at['data_hora_entrada'])
        at['obito_html'] = formatar_datetime_para_input(at['data_obito'])
        at['data_nascimento_html'] = formatar_date_para_input(at['data_nascimento'])
        at['situacao_saida'] = at['desfecho']

  
    hospitais, medicos = buscar_listas_auxiliares()
    return render_template('formulario.html', 
                         acao="Editar", 
                         at=at,
                         hospitais=hospitais, 
                         medicos=medicos,
                         erro=None)


@app.route('/criar_hospital', methods=['POST'])
def criar_hospital_route():
    try:
        id_hospital = criar_hospital(
            cnpj=request.form['hospital_cnpj'],
            nome=request.form['hospital_nome'],
            cidade=request.form['hospital_cidade'],
            endereco=request.form['hospital_endereco'],
            capacidade_leitos=request.form['hospital_capacidade']
        )
        return {
            "sucesso": True,
            "id": id_hospital,
            "nome": request.form['hospital_nome']
        }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}, 400


@app.route('/criar_medico', methods=['POST'])
def criar_medico_route():
    try:
        id_medico = criar_medico(
            crm=request.form['medico_crm'],
            nome=request.form['medico_nome'],
            telefone=request.form.get('medico_telefone', ''),
            especialidade=request.form.get('medico_especialidade', '')
        )
        return {
            "sucesso": True,
            "id": id_medico,
            "nome": request.form['medico_nome']
        }
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}, 400


@app.route('/deletar/<int:id>')
def deletar_atendimento(id):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM atendimento WHERE id_atendimento = :id"), {"id": id})
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)