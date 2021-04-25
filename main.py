from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect
from flask_login import LoginManager, login_user, login_required, logout_user

import db_session
from data.users import User
from data.shopping import goods
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    rest = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        return self.title


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def home():
    items = Item.query.order_by(Item.price).all()
    return render_template('home.html', data=items)


@app.route('/shopping')
def cart_show():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == session["email"]).first()
    items = Item.query.order_by(Item.price).all()
    good_s = db_sess.query(goods)
    return render_template('shopping.html', data=items, user=user, good_s=good_s, price=0)


@app.route('/pay')
def pay():
    return "Место для будущей формы оплаты"



@app.route('/shopping_add/<int:product_id>')
def cart_add(product_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == session["email"]).first()
    item = db_sess.query(Item).filter(Item.id == product_id).first()
    if item.rest > 0:
        good = goods(product_id=product_id, user_id=user.id)
        db_sess.add(good)
        item.rest -= 1
    db_sess.commit()
    return redirect("/")


@app.route('/shopping_del/<int:product_id>')
def cart_del(product_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == session["email"]).first()
    good = db_sess.query(goods).filter(goods.product_id == product_id, goods.user_id == user.id).first()
    item = db_sess.query(Item).filter(Item.id == product_id).first()
    item.rest += 1
    db_sess.delete(good)
    db_sess.commit()
    return redirect("/shopping")


@app.route('/about')
def about():
    return render_template('about_us.html')


@app.route('/where')
def where():
    return render_template('address.html')


@app.route('/make', methods=['POST', 'GET'])
def make():
    if request.method != "POST":
        return render_template('make.html')
    else:
        title = request.form['title']
        price = request.form['price']
        rest = request.form['rest']
        title = Item(title=title, price=price, rest=rest)
        try:
            db.session.add(title)
            db.session.commit()
            return redirect('/make')
        except:
            return 'Ошибочка (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧'


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        session["email"] = form.email.data
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


def main():
    import products_api
    app.register_blueprint(products_api.blueprint)
    db_session.global_init("store.db")
    app.run(port=8000, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()