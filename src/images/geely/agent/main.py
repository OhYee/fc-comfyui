from routes.routes import Routes

r = Routes()

if __name__ == "__main__":
    r.app.run(debug=False, host="0.0.0.0", port=9000)
