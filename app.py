from service import app


# We want to run our app from python and not the command line always
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
