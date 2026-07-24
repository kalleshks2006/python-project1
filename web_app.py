"""A small, dependency-free Python web page.

Run with:  python web_app.py
Then open: http://localhost:8000
"""

from http.server import BaseHTTPRequestHandler, HTTPServer


PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bright Studio</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f7f9fc; }
    nav { display: flex; justify-content: space-between; align-items: center; padding: 20px 9%; background: white; }
    .logo { font-size: 1.25rem; font-weight: bold; color: #4f46e5; }
    nav a { text-decoration: none; color: #475569; margin-left: 20px; }
    .hero { min-height: 480px; padding: 90px 9%; text-align: center; color: white;
            background: linear-gradient(120deg, #4f46e5, #0ea5e9); }
    h1 { max-width: 760px; margin: 0 auto 18px; font-size: clamp(2.4rem, 7vw, 4.8rem); }
    .hero p { max-width: 580px; margin: auto; font-size: 1.15rem; line-height: 1.6; }
    .button { display: inline-block; margin-top: 30px; padding: 14px 24px; border-radius: 8px;
              background: white; color: #4338ca; font-weight: bold; text-decoration: none; }
    section { max-width: 1040px; margin: auto; padding: 70px 24px; text-align: center; }
    .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 20px; margin-top: 30px; }
    .card { padding: 26px; text-align: left; background: white; border-radius: 12px;
            box-shadow: 0 8px 24px rgba(15, 23, 42, .08); }
    .card h3 { margin-top: 0; color: #4f46e5; }
    footer { padding: 24px; color: #64748b; text-align: center; background: white; }
  </style>
</head>
<body>
  <nav>
    <span class="logo">BRIGHT STUDIO</span>
    <div><a href="#services">Services</a><a href="#contact">Contact</a></div>
  </nav>
  <main>
    <div class="hero">
      <h1>Make your next idea shine.</h1>
      <p>A clean starter website built and served entirely with Python. Change the text, colors, and sections to make it yours.</p>
      <a class="button" href="#services">Explore services</a>
    </div>
    <section id="services">
      <h2>What we do</h2>
      <div class="cards">
        <article class="card"><h3>Design</h3><p>Thoughtful interfaces that make a strong first impression.</p></article>
        <article class="card"><h3>Build</h3><p>Fast, clear web experiences that work on every screen.</p></article>
        <article class="card"><h3>Grow</h3><p>Simple strategies to turn visits into lasting relationships.</p></article>
      </div>
    </section>
  </main>
  <footer id="contact">hello@example.com &middot; &copy; 2026 Bright Studio</footer>
</body>
</html>"""


class WebsiteHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(PAGE.encode("utf-8"))
        else:
            self.send_error(404, "Page not found")


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), WebsiteHandler)
    print("Website running at http://localhost:8000 (press Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()
