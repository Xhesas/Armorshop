import argparse
import json
import random

import numpy as np
from datetime import datetime as dt

from flask import Flask, request, render_template, make_response
from werkzeug.utils import send_file, send_from_directory

with open("data.json", "r") as file:
    catalog = json.load(file)
emptymsg = ["It seems you’ve wandered into uncharted territory.", "It looks like you are lost, can I help you?", "You shouldn't be here! The sign clearly said \"Staff Only\"!", "Sorry, but I can't find the soup you searched for."]
badrmsg = ["You have sent an invalid request.", "I couldn't understand you, can you speak clearer?", "Is your Browser broken?"]
output = None
blacklist = None

app = Flask(__name__)

@app.route('/resources/<resource>')
@app.route('/resource/<resource>')
def route_resource(resource):
    return send_from_directory('resources/', resource, request.environ)

@app.route('/item/<item>')
def route_item(item):
    a = [a for a in catalog if a['id'] == item]
    if not a:
        return make_response(render_template('item.html'), 404)
    item = a[0]
    prices = []
    for p in ['prices', 'additionPrices']:
        if p in item:
            q = []
            element = item[p]
            q.append(do_price("glanga", element['glanga']))
            q.append(do_price("slab", element['slab']))
            q.append(do_price("diamond", element['diamond']))
            q.append(do_price("puan", element['puan']))
            prices.append(" | ".join(q))
        else:
            prices.append("")

    additions = []
    if 'tags' in item:
        for tag in item['tags']:
            for element in catalog:
                try:
                    if tag in element['addition']:
                        a = []
                        if 'additionPrices' in element:
                            price = element['additionPrices']
                        else:
                            price = element['prices']
                        a.append(["+ " + do_price("glanga", price['glanga']), "glanga"])
                        a.append(["+ " + do_price("slab", price['slab']), "slab"])
                        a.append(["+ " + do_price("diamond", price['diamond']), "diamond"])
                        a.append(["+ " + do_price("puan", price['puan']), "puan"])
                        element['price_list'] = a
                        additions.append(element)
                except:
                    pass
    return render_template(
        'item.html',
        item_name=item['name'],
        item_id=item['id'],
        item_image=item['image'],
        item_description=item['description'],
        prices=prices,
        additions=additions,
        display_button='prices' in item,
        catalog=[a for a in catalog if 'prices' in a]
    )

@app.route('/js/<js>')
def route_js(js):
    match js:
        case "" | "index" | "index.js":
            return send_file('js/index.js', request.environ)
        case "item" | "item.js":
            return send_file('js/item.js', request.environ)
        case "message" | "item.js":
            return send_file('js/message.js', request.environ)
        case _:
            return ''

@app.route('/index')
@app.route('/index.html')
@app.route('/')
def route_index():
    recommended = []
    item_list = []
    for item in catalog:
        if 'prices' in item:

            a = []
            price = item['prices']
            a.append([do_price("glanga", price['glanga']), "glanga"])
            a.append([do_price("slab", price['slab']), "slab"])
            a.append([do_price("diamond", price['diamond']), "diamond"])
            a.append([do_price("puan", price['puan']), "puan"])

            b = {
                'prices': a,
                'id': item['id'],
                'name': item['name'],
                'purchases': item['purchases']
            }

            if not 'addition' in b and len(recommended) < 5:
                recommended.append(b)
            else:
                smallest = recommended[0]
                for e in recommended:
                    if smallest['purchases'] > e['purchases']:
                        smallest = e
                if b['purchases'] > smallest['purchases']:
                    recommended[recommended.index(smallest)] = b
            item_list.append(b)

    return render_template('index.html', recommended=recommended, catalog=item_list)

@app.route('/css')
@app.route('/main.css')
@app.route('/css/')
def route_css():
    return send_file('main.css', request.environ)

@app.route('/about')
@app.route('/about.html')
def route_about():
    return render_template('about.html')

@app.route('/contact')
@app.route('/contact.html')
def route_contact():
    return render_template('contact.html')

@app.route('/faq')
@app.route('/faq.html')
def route_faq():
    return render_template('faq.html')

@app.route('/locations')
@app.route('/locations.html')
def route_locations():
    return render_template('locations.html')

@app.route('/catalog')
@app.route('/catalog.json')
@app.route('/data')
@app.route('/data.json')
def route_catalog():
    return send_file('data.json', request.environ)

@app.route('/favicon')
@app.route('/favicon.ico')
def route_favicon():
    return send_file('resources/favicon.ico', request.environ)

@app.route('/sitemap.xml')
def route_sitemap():
    return send_file('robots/sitemap.xml', request.environ)

@app.route('/robots.txt')
def route_robots():
    return send_file('robots/robots.txt', request.environ)

@app.route('/purchase', methods=["POST"])
def route_purchase():
    item = request.form.get('item')
    info = request.form.get('info')
    quantity = request.form.get('quantity')
    name = request.form.get('name')
    shipment = request.form.get('shipment-type')
    address = request.form.get('address')
    date = request.form.get('date')
    msg = quantity + " " + item + ("\n" + info + "\n" if info != "" else "\n") + "Shipment type: " + shipment + "\n" + (address if date == "" else date)
    save_message(name, msg, request)
    return render_template('post-purchase.html')

@app.route('/message', methods=["POST"])
def route_message():
    name = request.form.get('name')
    msg = request.form.get('message')
    if len([1 for a in ["database", "your website", "hacked", "bitcoin"] if a in msg.lower()]) > 1:
        save_message(
            name,
            "Someone has left inappropriate stuff, look at it and laugh!\n+-----+\n" + msg + "\n+-----+\nHere are some more informations saved from the request:\n" + str(request.headers),
            request
        )
        if blacklist:
            with open(blacklist, "r") as blacklistfile:
                filedata = json.load(blacklistfile)
            filedata['blacklist'].append(str(request.environ.get('HTTP_X_REAL_IP', request.remote_addr)))
            with open(blacklist, "w") as blacklistfile:
                json.dump(filedata, blacklistfile, indent=4)
        return make_response(b'Your message has been deemed inappropriate and your ip address has been blocked! I hope you shit your pants!', 403)
    save_message(name, msg, request)
    return render_template('post-message.html')

def save_message(name, msg, r):
    o = {
        "name": name,
        "message": msg,
        "file": "",
        "user": {
            "address": r.environ.get('HTTP_X_REAL_IP', r.remote_addr),
            "client": r.headers["User-Agent"]
        },
        "time-UTC": str(dt.now()),
        "page": r.headers["Host"] + r.path
    }
    if not output:
        print(o)
    else:
        with open(output, "r") as outputfile:
            filedata = json.load(outputfile)
        filedata['requests'].append(o)
        with open(output, "w") as outputfile:
            json.dump(filedata, outputfile, indent=4)

@app.errorhandler(404)
def not_found(_):
    return make_response(render_template(
        'not_found.html',
        msg=np.random.choice(emptymsg, p=np.arange(len(emptymsg), 0, -1)/np.arange(len(emptymsg), 0, -1).sum()),
        item="/item/" + random.choice(catalog)['id']
    ), 404)

@app.errorhandler(400)
def bad_request(_):
    return make_response(render_template(
        'bad_request.html',
        msg=np.random.choice(badrmsg, p=np.arange(len(badrmsg), 0, -1)/np.arange(len(badrmsg), 0, -1).sum())
    ), 400)

def do_price(currency, price):
    match currency:
        case "glanga":
            return str(price) + " Glanga"
        case "slab":
            sbt = price % 32
            s = (price - sbt) / 32
            c = ""
            if s == 1:
                c = "1 Slab"
            elif s != 0:
                c = str(s) + " Slabs"
            if sbt and s:
                c = c + " and "
            if sbt == 1:
                c = c + "1 Slablet"
            elif sbt != 0:
                c = c + str(sbt) + " Slablets"
            elif s == 0 and sbt == 0:
                c = "0 Slabs"
            return c
        case "diamond":
            if price == 1:
                return "1 Diamond"
            else:
                return str(price) + " Diamonds"
        case "puan":
            return str(price) + " Puan Unity Argent"
    return ""


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--Output", type=str, help="Defines the output file for POST messages")
    parser.add_argument("-b", "--Blacklist", type=str, help="Defines the file to store blacklisted ips to")
    args = parser.parse_args()
    output = args.Output if args.Output else None
    blacklist = args.Blacklist if args.Blacklist else None
    app.run(port=5001)