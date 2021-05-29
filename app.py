# learn is the package
from fuprox import app
import eventlet
import eventlet.wsgi

port = 9000
if __name__ == "__main__":
    app.run("0.0.0.0",port, debug=True)
    # eventlet.wsgi.server(eventlet.listen(('', port)), app)



