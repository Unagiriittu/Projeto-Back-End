from flask import Flask, request, jsonify
from usuario import Usuario, Paciente, ProfissionalSaude, Consulta, Prontuario, engine, Base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

# Inicializa a aplicação Flask
app = Flask(__name__)
Session = sessionmaker(bind=engine)
SECRET_KEY = "chave-secreta-do-sistema"

def token_requerido(f):
    """Decorador para proteger rotas com autenticação JWT."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            bearer = request.headers["Authorization"]
            token = bearer.replace("Bearer ", "")
        if not token:
            return jsonify({"erro": "Token não fornecido"}), 401
        try:
            dados = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            session = Session()
            usuario = session.query(Usuario).filter_by(id=dados["id"]).first()
            if not usuario:
                return jsonify({"erro": "Acesso não autorizado"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"erro": "Token expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401
        return f(usuario, *args, **kwargs)
    return decorated

@app.route("/registrar", methods=["POST"]) #@app.route é um decorador usado no framework Flask para mapear URLs para funções específicas, chamadas de funções de visualização
def registrar():
    """Registra um novo usuário administrador ou comum."""
    data = request.get_json()
    session = Session()
    nome = data.get("usuario")
    senha = data.get("senha")
    is_admin = data.get("is_admin", False)
    if session.query(Usuario).filter_by(nome_de_usuario=nome).first():
        return jsonify({"erro": "Usuário já existe"}), 400
    senha_hash = generate_password_hash(senha)
    novo_usuario = Usuario(nome_de_usuario=nome, senha=senha_hash, is_admin=is_admin)
    session.add(novo_usuario)
    session.commit()
    return jsonify({"mensagem": "Usuário registrado com sucesso"}), 201

@app.route("/login", methods=["POST"])
def login():
    """Realiza o login do usuário e retorna um token JWT."""
    data = request.get_json()
    session = Session()
    nome = data.get("usuario")
    senha = data.get("senha")
    usuario = session.query(Usuario).filter_by(nome_de_usuario=nome).first()
    if usuario and check_password_hash(usuario.senha, senha):
        token = jwt.encode({
            "id": usuario.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        }, SECRET_KEY, algorithm="HS256")
        return jsonify({"token": token}), 200
    return jsonify({"erro": "Credenciais inválidas"}), 401

@app.route("/paciente", methods=["POST"])
def cadastrar_paciente():
    """Cadastra um novo paciente no sistema."""
    data = request.get_json()
    session = Session()
    nascimento_formatado = datetime.datetime.strptime(data["data_nascimento"], "%Y-%m-%d").date()
    novo_paciente = Paciente(
        nome=data["nome"],
        cpf=data["cpf"],
        data_nascimento=nascimento_formatado,
        sexo=data["sexo"],
        telefone=data["telefone"],
        endereco=data["endereco"]
    )
    session.add(novo_paciente)
    session.commit()
    return jsonify({"mensagem": "Paciente cadastrado com sucesso."}), 201

@app.route("/profissional", methods=["POST"])
def cadastrar_profissional():
    """Cadastra um novo profissional de saúde no sistema."""
    data = request.get_json()
    session = Session()
    novo_profissional = ProfissionalSaude(
        nome=data["nome"],
        crm=data["crm"],
        especialidade=data["especialidade"],
        telefone=data["telefone"],
        email=data["email"]
    )
    session.add(novo_profissional)
    session.commit()
    return jsonify({"mensagem": "Profissional de saúde cadastrado com sucesso."}), 201

@app.route("/consulta", methods=["POST"])
def registrar_consulta():
    """Registra uma nova consulta entre um paciente e um profissional."""
    data = request.get_json()
    session = Session()
    data_formatada = datetime.datetime.strptime(data["data"], "%Y-%m-%d").date()
    nova_consulta = Consulta(
        id_paciente=data["id_paciente"],
        id_profissional=data["id_profissional"],
        data=data_formatada,
        hora=data["hora"],
        motivo=data["motivo"]
    )
    session.add(nova_consulta)
    session.commit()
    return jsonify({"mensagem": "Consulta registrada com sucesso"}), 201

@app.route("/prontuario", methods=["POST"])
def registrar_prontuario():
    """Registra um prontuário associado a uma consulta existente."""
    data = request.get_json()
    session = Session()
    novo_prontuario = Prontuario(
        id_consulta=data["id_consulta"],
        anotacoes=data["anotacoes"]
    )
    session.add(novo_prontuario)
    session.commit()
    return jsonify({"mensagem": "Prontuário registrado com sucesso"}), 201

@app.route("/prontuarios/paciente/<int:id_paciente>", methods=["GET"])z
def listar_prontuarios_por_paciente(id_paciente):
    """Lista todos os prontuários vinculados às consultas de um paciente."""
    session = Session()
    consultas = session.query(Consulta).filter_by(id_paciente=id_paciente).all()
    resultado = []
    for consulta in consultas:
        prontuario = session.query(Prontuario).filter_by(id_consulta=consulta.id).first()
        if prontuario:
            resultado.append({
                "id_consulta": consulta.id,
                "data": consulta.data.isoformat(),
                "hora": consulta.hora,
                "motivo": consulta.motivo,
                "anotacoes": prontuario.anotacoes
            })
    return jsonify(resultado), 200

@app.route("/pacientes", methods=["GET"])
def listar_pacientes():
    """Retorna uma lista de todos os pacientes cadastrados."""
    session = Session()
    pacientes = session.query(Paciente).all()
    return jsonify([{
        "id": p.id,
        "nome": p.nome,
        "cpf": p.cpf,
        "data_nascimento": p.data_nascimento.isoformat(),
        "sexo": p.sexo,
        "telefone": p.telefone,
        "endereco": p.endereco
    } for p in pacientes]), 200

@app.route("/profissionais", methods=["GET"])
def listar_profissionais():
    """Retorna uma lista de todos os profissionais de saúde cadastrados."""
    session = Session()
    profissionais = session.query(ProfissionalSaude).all()
    return jsonify([{
        "id": p.id,
        "nome": p.nome,
        "crm": p.crm,
        "especialidade": p.especialidade,
        "telefone": p.telefone,
        "email": p.email
    } for p in profissionais]), 200

if __name__ == "__main__":
    # Executa o servidor Flask em modo debug
    app.run(debug=True)
