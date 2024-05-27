from DatasetsFactory import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=True)
else:
    app_gunicorn = create_app()
