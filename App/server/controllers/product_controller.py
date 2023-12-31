from collections import defaultdict
from flask import request, render_template
import os
import random
import datetime
from server import app
from server.models.product_model import get_products, get_auction_products, get_products_variants, create_product, get_auction_managements
from werkzeug.utils import secure_filename

PAGE_SIZE = 6
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route('/admin/product.html', methods=['GET'])
def admin_product():
    return render_template('product_create.html')

@app.route('/')
@app.route('/admin/recommendation.html')
def product_recommendation_page():
    res = get_products(100, 0, {"source": "amazon"},)
    return render_template('product_recommendation.html', products = [{"id": p["id"], "title": p["title"]} for p in res["products"]])

def find_product(category, paging):
    if (category == 'all') :
        return get_products(PAGE_SIZE, paging, {"category": category})
    elif (category in ['men', 'women', 'accessories']):
        return get_products(PAGE_SIZE, paging, {"category": category})
    elif (category == 'search'):
        keyword = request.values["keyword"]
        if (keyword):
            return get_products(PAGE_SIZE, paging, {"keyword": keyword})
    elif (category == 'details'):
        product_id = request.values["id"]
        return get_products(PAGE_SIZE, paging, {"id": product_id})
    elif (category == 'recommend'):
        product_id = request.values["id"]
        return get_products(3, paging, {"recommend": product_id})
    
def find_auction_product(category, paging):
    if (category == 'all') :
        return get_auction_products(PAGE_SIZE, paging, {"category": category})
    elif (category in ['men', 'women', 'accessories']):
        return get_auction_products(PAGE_SIZE, paging, {"category": category})
    elif (category == 'search'):
        keyword = request.values["keyword"]
        if (keyword):
            return get_auction_products(PAGE_SIZE, paging, {"keyword": keyword})
    elif (category == 'details'):
        product_id = request.values["id"]
        return get_auction_products(PAGE_SIZE, paging, {"id": product_id})
    elif (category == 'recommend'):
        product_id = request.values["id"]
        return get_auction_products(3, paging, {"recommend": product_id})

def get_products_with_detail(products):
    product_ids = [p["id"] for p in products]
    variants = get_products_variants(product_ids)
    variants_map = defaultdict(list)
    for variant in variants:
        variants_map[variant["product_id"]].append(variant)

    def parse(product, variants_map):
        product_id = product["id"]
        product["main_image"] =  product["main_image"]
        product["images"] = [img for img in product["images"].split(',')]
        product_variants = variants_map[product_id]
        if (not product_variants):
            return product

        product["variants"] = [
            {
                "color_code": v["color_code"],
                "size": v["size"],
                "stock": v["stock"]
            }
            for v in product_variants
        ]
        colors = [
            {
                "code": v["color_code"],
                "name": v["color_name"]
            }
            for v in product_variants
        ]
        product["colors"] = list({c['code'] + c["name"]: c for c in colors}.values())
        product["sizes"] = list(set([
            v["size"]
            for v in product_variants   
        ]))

        return product

    return [
        parse(product, variants_map) for product in products
    ]

def get_auction_with_management(auctions):
    auction_ids = [a["id"] for a in auctions]
    managements = get_auction_managements(auction_ids)
    managements_map = defaultdict(list)
    for management in managements:
        managements_map[management["auction_product_id"]].append(management)

    def parse(auction, managements_map):
        auction_id = auction["id"]
        auction_managements = managements_map[auction_id]
        if (not auction_managements):
            return auction
        
        auction["auction_id"] = auction_managements[0]["auction_id"]
        auction["start_time"] = auction_managements[0]["start_time"]
        auction["end_time"] = auction_managements[0]["end_time"]
        auction["status"] = auction_managements[0]["status"]
        return auction
    
    return [
        parse(auction, managements_map) for auction in auctions
    ]



@app.route('/api/1.0/products/<category>', methods=['GET'])
def api_get_products(category):
    paging = request.values.get('paging') or 0
    paging = int(paging)
    res = find_product(category, paging)

    if (not res):
        return {"error":'Wrong Request'}

    products = res.get("products") 
    product_count = res.get("product_count")

    if (not products):
        return {"error":'Wrong Request'}
    
    if (not len(products)):
        if (category == 'details'):
            return {"data": None}
        else:
            return {"data": []}

    products_with_detail = \
        get_products_with_detail(products) if products[0]["source"] == 'native' else products
    if (category == 'details'):
        products_with_detail = products_with_detail[0]

    result = {}
    if (product_count > (paging + 1) * PAGE_SIZE):
        result = {
            "data": products_with_detail,
            "next_paging": paging + 1
        } 
    else: 
        result = {"data": products_with_detail}
    
    return result

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def save_file(folder, file):
    folder_root = app.root_path + app.config['UPLOAD_FOLDER']
    folder_path = folder_root + '/' + folder
    if not os.path.isdir(folder_path):
        os.mkdir(folder_path)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(
            folder_path,
            filename
        ))
        return filename
    else:
        return None

@app.route('/api/1.0/product', methods=['POST'])
def api_create_product():
    form = request.form.to_dict()
    product_id = form["product_id"]
    main_image = request.files.get("main_image")
    main_image_name = save_file(product_id, main_image)
    other_images = request.files.getlist('other_images')
    other_images_names = []
    for file in other_images:
        other_images_names.append(save_file(product_id, file))

    product = {
        'id': form['product_id'],
        'category': form['category'],
        'title': form['title'],
        'description': form['description'],
        'price': int(form['price']),
        'texture': form['texture'],
        'wash': form['wash'],
        'place': form['place'],
        'note': form['note'],
        'story': form['story'],
        'main_image': main_image_name,
        'images': ','.join(other_images_names),
        'source': 'native'
    }

    variants = [   
        {
            "size": size,
            "color_code": color_code,
            "color_name": color_name,
            "stock": random.randint(1,10),
            "product_id": product_id
        }
        for (color_code, color_name) 
        in zip(form["color_codes"].split(','), form["color_names"].split(','))
        for size
        in form["sizes"].split(',')
    ]

    create_product(product, variants)
    return "Ok"

@app.route('/api/1.0/auction/product', methods=['GET'])
def auction_sale():
    paging = request.values.get('paging') or 0
    paging = int(paging)
    res = find_auction_product('all', paging)
    auctions = res.get("products")

    if (not auctions):
        return {"error":'Wrong Request'}
    
    auction_with_management = get_auction_with_management(auctions)

    result = {
        "data": auction_with_management
    } 
    return result