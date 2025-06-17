from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, ForeignKey, Text
from sqlalchemy.orm import declarative_base

# Define a URL do banco de dados SQLite local
DATABASE_URL = "sqlite:///./login.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Usuario(Base):
    """Modelo para usuários do sistema (administradores ou comuns)."""
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nome_de_usuario = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)

class Paciente(Base):
    """Modelo para pacientes cadastrados no sistema."""
    __tablename__ = "pacientes"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    sexo = Column(String, nullable=False)
    telefone = Column(String)
    endereco = Column(String)

class ProfissionalSaude(Base):
    """Modelo para profissionais de saúde (médicos, enfermeiros etc.)."""
    __tablename__ = "profissionais"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    crm = Column(String, unique=True, nullable=False)
    especialidade = Column(String)
    telefone = Column(String)
    email = Column(String)

class Consulta(Base):
    """Modelo para consultas realizadas entre pacientes e profissionais."""
    __tablename__ = "consultas"
    id = Column(Integer, primary_key=True)
    id_paciente = Column(Integer, ForeignKey('pacientes.id'), nullable=False)
    id_profissional = Column(Integer, ForeignKey('profissionais.id'), nullable=False)
    data = Column(Date, nullable=False)
    hora = Column(String, nullable=False)
    motivo = Column(String)

class Prontuario(Base):
    """Modelo para prontuários médicos vinculados às consultas."""
    __tablename__ = "prontuarios"
    id = Column(Integer, primary_key=True)
    id_consulta = Column(Integer, ForeignKey('consultas.id'), nullable=False)
    anotacoes = Column(Text, nullable=False)

# Cria todas as tabelas no banco de dados
Base.metadata.create_all(engine)
