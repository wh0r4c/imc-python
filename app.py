from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import execute_query

app = Flask(__name__)
app.secret_key = 'banana banana'

def calcular_imc(peso, altura):
    return round(float(peso) / (float(altura) ** 2), 2)

def classificacao(imc):
    if imc < 18.5:
        return 'Abaixo do peso'
    elif imc < 25:
        return 'Peso normal'
    elif imc < 30:
        return 'Sobrepeso'
    elif imc < 35:
        return 'Obesidade Grau I'
    else:
        return 'Obesidade Grau II/III'

@app.route('/')
def index():
    sql = '''
CREATE TABLE IF NOT EXISTS calculos(
    id_calculo BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    peso DECIMAL(6,2) NOT NULL,
    altura DECIMAL(5,2) NOT NULL,

    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    alterado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deletado_em DATETIME NULL
);
'''
    resultado = execute_query(sql,fetch=True)
    print(resultado)

    return render_template('index.html')

@app.route('/usuarios')
def usuarios():
    usuarios = execute_query('SELECT * FROM usuarios', fetch=True)
    return render_template('usuarios.html', usuarios=usuarios)

@app.route('/resultados')
def resultados():
    
    try:
    
        sql = "SELECT * FROM calculos WHERE deletado_em IS NULL;"

        calculos = execute_query(sql, fetch=True)

        if calculos is None:
            calculos = []

    except Exception as e:
        flash(f'Erro ao salvar!', 'danger')
        app.logger.error(f'Erro no SELECT: {e}')
        return redirect(url_for('calcular'))

    return render_template('resultados.html', 
                           calculos=calculos, 
                           total=len(calculos),
                           calcular = calcular_imc,
                           classificacao = classificacao
                           )

@app.route('/calcular', methods=['GET', 'POST'])
def calcular():
    if request.method == 'POST':
        nome = request.form.get('nome', 'Não achei porcaria nenhuma').strip()
        peso = request.form.get('peso', '0').strip()
        altura = request.form.get('altura', '0').strip()

        peso = float(peso)
        altura = float(altura)

        try:
            sql = 'INSERT INTO calculos(nome, peso, altura) VALUES (%s, %s, %s);'
            execute_query(sql, (nome, peso, altura))
            flash(f'Produto [{nome}] cadastrado com sucesso!', 'success')

        except Exception as e:
            flash(f'Erro ao salvar!', 'danger')
            app.logger.error(f'Erro no INSERT: {e}')
            return redirect(url_for('calcular'))

    return render_template('formulario.html')

if __name__ == '__main__':
    app.run(debug=True)