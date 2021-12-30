import tornado.ioloop
import tornado.web
import webbrowser
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])




if __name__ == "__main__":
    port = 9999
    bind = "localhost"
    app = make_app()
    app.listen(port)
    webbrowser.open(f"http://localhost:{port}",bind)
    tornado.ioloop.IOLoop.current().start()