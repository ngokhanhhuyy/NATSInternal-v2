from app import application

def main():
    # application.run(host="0.0.0.0", port="5000")
    application.run(debug=True, port=5000)

if __name__ == "__main__":
    main()