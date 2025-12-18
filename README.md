# Coloring Book Project
```
sorry there are images all over the place in this project, this was one of the issues i had while developing it was tidying it up.
you can just go through each of the py files to see how i coded each of them and kinda my thought process behind it. morphing loop was the easiest because once i had one, the other one was simple
there may be some bugs in the website that i've not caught yet. 

```
## Run it
```
python -m venv .venv
.\.venv\Scripts\activate
pip install Pillow Flask
python web_app.py
```
Open http://127.0.0.1:5000 and upload something. Results pop up under outputs/ and uploads/.

## Docker
```
docker build -t coloring-thing .
docker run --rm -p 5000:5000 coloring-thing
```

