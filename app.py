from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    port = os.environ.get('PORT', 'Non défini')
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Railway Test</title>
        <style>
            body {{ font-family: Arial; text-align: center; padding: 50px; background: #667eea; color: white; }}
            .success {{ background: green; padding: 20px; border-radius: 10px; margin: 20px; }}
        </style>
    </head>
    <body>
        <div class="success">
            <h1>🎉 SUCCESS ! Railway fonctionne !</h1>
            <p><strong>Port utilisé :</strong> {port}</p>
            <p><strong>Application :</strong> En ligne et opérationnelle</p>
            <p>✅ Prêt pour l'étape suivante !</p>
        </div>
        <a href="/test" style="color: yellow; font-size: 18px;">🔗 Tester une autre page</a>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return '''
    <h1 style="color: green;">✅ Page test OK !</h1>
    <a href="/">Retour accueil</a>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Démarrage Flask sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
