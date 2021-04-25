import flask
from flask import jsonify
import codecs
import db_session
from data.products import Items

blueprint = flask.Blueprint('products_api', __name__, template_folder='templates')


@blueprint.route('/api/products')
def get_products():
    db_sess = db_session.create_session()
    news = db_sess.query(Items).all()
    return jsonify(
        {"products": [item.to_dict(only=('title', 'price', 'rest')) for item in news]})


@blueprint.route('/api/products/<int:product_id>', methods=['GET'])
def get_one_product(product_id):
    db_sess = db_session.create_session()
    items = db_sess.query(Items).get(product_id)
    if not items:
        return jsonify({'error': 'Not found'})
    return jsonify({'product': items.to_dict(only=('title', 'price', 'rest'))})