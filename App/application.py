from server import app
from waitress import serve

if __name__ == "__main__":
    if (app.env == "production"):
        print('prod. connect')
        serve(app, host='0.0.0.0', port = 3000)
    else:
        print('dev. connect')
        app.debug = True
        app.run('0.0.0.0', port = 8080)