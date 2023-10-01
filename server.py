from app import application as app

def main():
    # application.run(host="0.0.0.0", port="5000")
    app.run(debug=True, port=5000)

if __name__ == "__main__":
    main()