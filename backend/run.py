from app import criar_app

if __name__ == '__main__':
    criar_app().run(debug=True) # Roda o backend em flask do servidor, pegando da função 'criar_app' dentro do modulo app.
    # O modo de debug deve ficar ativo somente durante o desenvolvimento da aplicação, 
    # e a correção de bugs futuros que vierem a aparecer.