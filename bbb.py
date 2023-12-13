from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://joaovitorcaldeir:toledo22@joaovitorcaldeira.mysql.pythonanywhere-services.com:3306/joaovitorcaldeir$mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'senha secreta'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuario"
    id = db.Column('usu_id', db.Integer, primary_key=True)
    nome = db.Column('usu_nome', db.String(256))
    email = db.Column('usu_email', db.String(256))
    senha = db.Column('usu_senha', db.String(256))
    end = db.Column('usu_end', db.String(256))
    anuncios = db.relationship('Anuncio', backref='usuario', lazy=True)

    def __init__(self, nome, email, senha, end):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.end = end

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column('cat_id', db.Integer, primary_key=True)
    nome = db.Column('cat_nome', db.String(256))
    desc = db.Column('cat_desc', db.String(256))
    anuncios = db.relationship('Anuncio', backref='categoria', lazy=True)

    def __init__ (self, nome, desc):
        self.nome = nome
        self.desc = desc

class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id = db.Column('anu_id', db.Integer, primary_key=True)
    nome = db.Column('anu_nome', db.String(256))
    desc = db.Column('anu_desc', db.String(256))
    qtd = db.Column('anu_qtd', db.Integer)
    preco = db.Column('anu_preco', db.Float)
    cat_id = db.Column('cat_id', db.Integer, db.ForeignKey("categoria.cat_id"))
    usu_id = db.Column('usu_id', db.Integer, db.ForeignKey("usuario.usu_id"))

    def __init__(self, nome, desc, qtd, preco, cat_id, usu_id):
        self.nome = nome
        self.desc = desc
        self.qtd = qtd
        self.preco = preco
        self.cat_id = cat_id
        self.usu_id = usu_id

@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('pagnaoencontrada.html')

@login_manager.user_loader
def load_user(id):
    return Usuario.query.get(int(id))

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        passwd = hashlib.sha512(str(request.form.get('passwd')).encode("utf-8")).hexdigest()

        user = Usuario.query.filter_by(email=email, senha=passwd).first()

        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/")
@login_required
def index():
    anuncios = Anuncio.query.all()
    return render_template('index.html', anuncios=anuncios)

@app.route("/cad/usuario")
@login_required
def usuario():
    usuarios = Usuario.query.all()
    return render_template('usuario.html', usuarios=usuarios, titulo="Usuario")

@app.route("/criar/<string:entidade>", methods=['GET', 'POST'])
@login_required
def criar(entidade):
    if request.method == 'POST':
        return redirect(url_for('listar', entidade=entidade))

    return render_template('criar.html', titulo=entidade.capitalize())

@app.route("/listar/<string:entidade>")
@login_required
def listar(entidade):
    registros = None

    return render_template('listar.html', registros=registros, titulo=entidade.capitalize())

@app.route("/detalhes/<string:entidade>/<int:id>")
@login_required
def detalhes(entidade, id):
    registro = None

    return render_template('detalhes.html', registro=registro, titulo=entidade.capitalize())

@app.route("/editar/<string:entidade>/<int:id>", methods=['GET', 'POST'])
@login_required
def editar(entidade, id):
    registro = None

    if request.method == 'POST':
        return redirect(url_for('listar', entidade=entidade))

    return render_template('editar.html', registro=registro, titulo=entidade.capitalize())

@app.route("/deletar/<string:entidade>/<int:id>")
@login_required
def deletar(entidade, id):
    return redirect(url_for('listar', entidade=entidade))

@app.route("/usuario/criar", methods=['POST'])
def criarusuario():
    hash = hashlib.sha512(str(request.form.get('passwd')).encode("utf-8")).hexdigest()
    usuario = Usuario(request.form.get('user'), request.form.get('email'), hash, request.form.get('end'))
    db.session.add(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/usuario/detalhar/<int:id>")
def detalharusuario(id):
    usuario = Usuario.query.get(id)
    return render_template('detalhes_usuario.html', usuario=usuario)

@app.route("/usuario/editar/<int:id>", methods=['GET','POST'])
def editarusuario(id):
    usuario = Usuario.query.get(id)
    if request.method == 'POST':
        usuario.nome = request.form.get('user')
        usuario.email = request.form.get('email')
        usuario.senha = hashlib.sha512(str(request.form.get('passwd')).encode("utf-8")).hexdigest()
        usuario.end = request.form.get('end')
        db.session.commit()
        return redirect(url_for('usuario'))

    return render_template('eusuario.html', usuario=usuario, titulo="Usuario")

@app.route("/usuario/deletar/<int:id>")
def deletarusuario(id):
    usuario = Usuario.query.get(id)
    db.session.delete(usuario)
    db.session.commit()
    return redirect(url_for('usuario'))

@app.route("/cad/anuncio")
@login_required
def anuncio():
    anuncios = Anuncio.query.all()
    categorias = Categoria.query.all()
    return render_template('anuncio.html', anuncios=anuncios, categorias=categorias, titulo="Anuncio")

@app.route("/anuncio/criar", methods=['POST'])
def criaranuncio():
    anuncio = Anuncio(request.form.get('nome'), request.form.get('desc'), request.form.get('qtd'),
                      request.form.get('preco'), request.form.get('cat'), request.form.get('uso'))
    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

@app.route("/anuncio/detalhar/<int:id>")
def detalharanuncio(id):
    anuncio = Anuncio.query.get(id)
    return render_template('detalhes_anuncio.html', anuncio=anuncio)

@app.route("/anuncio/editar/<int:id>", methods=['GET','POST'])
def editaranuncio(id):
    anuncio = Anuncio.query.get(id)
    if request.method == 'POST':
        anuncio.nome = request.form.get('nome')
        anuncio.desc = request.form.get('desc')
        anuncio.qtd = request.form.get('qtd')
        anuncio.preco = request.form.get('preco')
        anuncio.cat_id = request.form.get('cat')
        anuncio.usu_id = request.form.get('usu')
        db.session.commit()
        return redirect(url_for('anuncio'))

    categorias = Categoria.query.all()
    usuarios = Usuario.query.all()
    return render_template('eanuncio.html', anuncio=anuncio, categorias=categorias, usuarios=usuarios, titulo="Anuncio")

@app.route("/anuncio/deletar/<int:id>")
def deletaranuncio(id):
    anuncio = Anuncio.query.get(id)
    db.session.delete(anuncio)
    db.session.commit()
    return redirect(url_for('anuncio'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)