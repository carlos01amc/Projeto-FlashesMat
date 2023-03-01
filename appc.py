import sympy
import plotly.graph_objs as go
import numpy as np
import sys

"""x**2 if x >= 0 else -x**2"""

def create_function(f, x):
    """
    Avalia a função f em cada valor de x e retorna o resultado.
    """
    return np.array([f(xi) for xi in x])


def is_continuous_at(f, a):
    try:
        # Verifica se o limite à esquerda existe
        left_limit = f(a - 0.0001)
        left_value = f(a)
        if abs(left_limit - left_value) > 0.0001:
            return False
        
        # Verifica se o limite à direita existe
        right_limit = f(a + 0.0001)
        right_value = f(a)
        if abs(right_limit - right_value) > 0.0001:
            return False
        
        # Se os limites à esquerda e à direita existem e são iguais ao valor da função no ponto,
        # então a função é contínua no ponto
        return True
    except:
        return False

def main():
    # Pede ao usuário para inserir a função
    f = input("Digite a função a ser testada (use 'x' como variável independente): ")
    try:
        f = sympy.sympify(f)
        f = sympy.lambdify('x', f)
    except:
        print("A função inserida é inválida.")
        return

    # Pede ao usuário para inserir o ponto
    a = input("Digite o ponto em que deseja verificar a continuidade: ")
    try:
        a = float(a)
    except:
        print("O valor inserido é inválido.")
        return

    # Verifica se a função é contínua no ponto a
    if is_continuous_at(f, a):
        print(f"A função é contínua no ponto {a}.")
    else:
        print(f"A função não é contínua no ponto {a}.")
    
    # Cria um array de valores de x para plotar a função
    x_values = np.linspace(a - 10, a + 10, 1000)

    # Avalia a função em cada valor de x
    y_values = create_function(f, x_values)

    # Cria o gráfico da função usando o Plotly
    trace = go.Scatter(x=x_values, y=y_values)
    layout = go.Layout(title="Gráfico da função", xaxis=dict(title="x"), yaxis=dict(title="y"))
    fig = go.Figure(data=[trace], layout=layout)
    fig.show()


if __name__ == '__main__':
    main()