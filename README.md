# FlaskAPP_Licenta_2024

### Obiective nerealizate:
* Flask-Email - confirmarea crearii contului prin generarea unui token de validare si trimiterea acestuia prin email
* Time Session Expired - setarea unui timp de pastrare a autentificarii (3 ore) - consulta Flask-Login
* AJAX request GET and POST - JavaScript
* Implementarea unei librarii prin care se vor accesa dataset-urile in alte aplicatii - inca nu mi-e clar acest task
* Evaluarea seturilor de date prin aplicarea catorva algoritmi de machine learning pentru evidentierea unor metrici, grafice, etc...
### Obiective nerealizate Update 26.05.2024
* Nu s-a implementat istoricul accesarilor fisierelor!
* Nu s-a realizat partea de vizualizare a unui set de date! - grafic, head, max min...etc
* Exista buguri pe paginile dataseturilor precum: pagina de cautare are paginare, dar nu functioneaza corespunzator, trebuie implementata o alta pagina separata de listare pentru search ca la groupe!
* La fel acelasi bug exista si pe upload files legat de parte de search, dar mai mult si cand nu exista un fisier in dataset, tot afiseaza tabelul si nu ar trebui!
* Package-ul nu a fost implementat
* Deployment-ul nu a fost implementat
### De terminat neaparat:
* Package-ul !!! - nu uita pe autentificare sa adaugi un token de verificare pentru partea de load
* Deployment-ul: dockerfile-ul(cu gunicorn) si containerul cu Nginx
* Afisarea paginilor pentru useri: datasets(aceeasi pagina ca pentru admin, fara upload si partea de edit) pe care au acces!