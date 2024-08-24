import random

AXIS_CHAR = "-"
VALUE_CHAR = "·"

def print_percents_axis(length: int=100, percent_values: list[int]=[25, 50, 75, 100]):
    '''
    Genera un eje que va desde 0 hasta 100, representando los porcentajes. Si se desean añadir varios
    valores y que la longitud sea menor a todos los valores mostrados uno tras otro, la longitud se
    ajusta automáticamente a los valores uno tras otro. Donde se muestre un valor en el eje, empieza el valor:

    ····5····10···15···20···25··
             ^
           el 10%
        empieza aquí

    '''
    # Nos aseguramos de que mostrará el 100%
    percent_values.append(100)

    # Calculamos la distancia mínima
    all_values = ""
    for value in percent_values:
        if value <= 100 and value > 0:
            all_values += str(value)
    
    min_length = len(all_values)

    # Si la longitud es menor a la longitud mínima, la ajustamos
    if min_length > length:
        length = min_length

    # Creamos el eje sin valores
    axis = AXIS_CHAR * length

    percents = sorted(percent_values)
    
    # Introducimos los valores en el eje sin alterar la longitud
    for percentage in percents:
        if percentage <= 100 and value > 0:
            axis = axis[:int(percentage * length / 100) - 1] + str(percentage) + axis[int(percentage * length / 100) + len(str(percentage)) - 1:]
    
    # Añadimos un 0 al inicio del eje
    axis = "0" + axis

    # Devolvemos el eje y la longitud de valores que tiene
    return axis, length

def print_percent_row(value, max_value, max_length, row_type: int=0):
    # Tipos de fila
    #   0: Fila rellenada
    #   1: Solo se marca en el punto del valor
    
    if row_type == 1:
        return " " * (int(int(value * 100 / max_value) * max_length / 100) - 1) + VALUE_CHAR
    else:
        return VALUE_CHAR * int(int(value * 100 / max_value) * max_length / 100)

def print_probability_graphic(values, max_length, interval, is_sorted: bool=False, repeat_values: bool=True, row_type: int=0, show_value: bool=True):
    def add_row(value, max_value, key=None):
        res = ""
        if key == None:
            key = f"{int(value * 100 / max_value)}%"
        
        if row_type == 1:
            res += " "
        else:
            res += VALUE_CHAR
        
        res += print_percent_row(value, max_value, max_length=max_length, row_type=row_type)

        if show_value:
            res += f"{key}"
        
        res += "\n"

        return res

    # Comprobamos si deben repetirse valores o no
    if not repeat_values and type(values) == list:
        values = list(set(values))

    table = ""
    
    # Eje de porcentajes
    def percentage_intervals(interval):
        if interval > 0 and interval <= 100:
            return [((x + 1) * interval) for x in range(100 // interval)]
        else:
            return [100]
    
    percent_values = percentage_intervals(interval)

    axis, max_length = print_percents_axis(length=max_length, percent_values=percent_values)
    table += axis + "\n"

    # Comprobamos si se tienen que ordenar los datos
    if is_sorted:
        if type(values) == list:
            values.sort()
        elif type(values) == dict:
            dict(sorted(values.items()))
    
    if type(values) == list:
        for value in values:
            table += add_row(value, 100)
    elif type(values) == dict:
        for key, value in values.items():
            table += add_row(value, 100, key)
    
    print(table)

if __name__ == "__main__":
    # Máximo de caracteres que aparecerán por valores en cada línea
    max_length = 100

    # Intérvalo de valores que aparecerán en el eje
    interval = 10

    # Valores que se mostrarán
    values = []
    for i in range(random.randint(2, 35)):
        values.append(random.randint(0, 100))
    
    borns_per_year = [
        322098,
        329251,
        337380,
        341315,
        360617,
        372777,
        393181,
        410583,
        420290,
        427595,
        425715,
        454648,
        471999,
        486575,
        494997,
        519779,
        492527,
        482957,
        466371,
        454591,
        441881,
        418846,
        406380,
        397632,
        380130,
        365193,
        369035,
        362626,
        363469,
        370148,
        385786,
        396747,
        395989,
        401425,
        408434,
        418919,
        426782,
        438750,
        456298,
        473281,
        485352,
        515706,
        533008,
        571018,
        601992,
        636892,
        656357,
        677456,
        669378,
        688711,
        672963,
        672405,
        672092,
        663667,
        666568,
        667311,
        680125,
        669919,
        676361,
        697697,
        671520,
        658816,
        654616,
        663375,
        654474,
        653216,
        646784,
        608121,
        598970,
        577886,
        589188,
        593019,
        567474,
        565378,
        601759,
        642041,
        588732,
        585381,
    ]

    values = {
        2023 : 322098 * 100 / max(borns_per_year),
        2022 : 329251 * 100 / max(borns_per_year),
        2021 : 337380 * 100 / max(borns_per_year),
        2020 : 341315 * 100 / max(borns_per_year),
        2019 : 360617 * 100 / max(borns_per_year),
        2018 : 372777 * 100 / max(borns_per_year),
        2017 : 393181 * 100 / max(borns_per_year),
        2016 : 410583 * 100 / max(borns_per_year),
        2015 : 420290 * 100 / max(borns_per_year),
        2014 : 427595 * 100 / max(borns_per_year),
        2013 : 425715 * 100 / max(borns_per_year),
        2012 : 454648 * 100 / max(borns_per_year),
        2011 : 471999 * 100 / max(borns_per_year),
        2010 : 486575 * 100 / max(borns_per_year),
        2009 : 494997 * 100 / max(borns_per_year),
        2008 : 519779 * 100 / max(borns_per_year),
        2007 : 492527 * 100 / max(borns_per_year),
        2006 : 482957 * 100 / max(borns_per_year),
        2005 : 466371 * 100 / max(borns_per_year),
        2004 : 454591 * 100 / max(borns_per_year),
        2003 : 441881 * 100 / max(borns_per_year),
        2002 : 418846 * 100 / max(borns_per_year),
        2001 : 406380 * 100 / max(borns_per_year),
        2000 : 397632 * 100 / max(borns_per_year),
        1999 : 380130 * 100 / max(borns_per_year),
        1998 : 365193 * 100 / max(borns_per_year),
        1997 : 369035 * 100 / max(borns_per_year),
        1996 : 362626 * 100 / max(borns_per_year),
        1995 : 363469 * 100 / max(borns_per_year),
        1994 : 370148 * 100 / max(borns_per_year),
        1993 : 385786 * 100 / max(borns_per_year),
        1992 : 396747 * 100 / max(borns_per_year),
        1991 : 395989 * 100 / max(borns_per_year),
        1990 : 401425 * 100 / max(borns_per_year),
        1989 : 408434 * 100 / max(borns_per_year),
        1988 : 418919 * 100 / max(borns_per_year),
        1987 : 426782 * 100 / max(borns_per_year),
        1986 : 438750 * 100 / max(borns_per_year),
        1985 : 456298 * 100 / max(borns_per_year),
        1984 : 473281 * 100 / max(borns_per_year),
        1983 : 485352 * 100 / max(borns_per_year),
        1982 : 515706 * 100 / max(borns_per_year),
        1981 : 533008 * 100 / max(borns_per_year),
        1980 : 571018 * 100 / max(borns_per_year),
        1979 : 601992 * 100 / max(borns_per_year),
        1978 : 636892 * 100 / max(borns_per_year),
        1977 : 656357 * 100 / max(borns_per_year),
        1976 : 677456 * 100 / max(borns_per_year),
        1975 : 669378 * 100 / max(borns_per_year),
        1974 : 688711 * 100 / max(borns_per_year),
        1973 : 672963 * 100 / max(borns_per_year),
        1972 : 672405 * 100 / max(borns_per_year),
        1971 : 672092 * 100 / max(borns_per_year),
        1970 : 663667 * 100 / max(borns_per_year),
        1969 : 666568 * 100 / max(borns_per_year),
        1968 : 667311 * 100 / max(borns_per_year),
        1967 : 680125 * 100 / max(borns_per_year),
        1966 : 669919 * 100 / max(borns_per_year),
        1965 : 676361 * 100 / max(borns_per_year),
        1964 : 697697 * 100 / max(borns_per_year),
        1963 : 671520 * 100 / max(borns_per_year),
        1962 : 658816 * 100 / max(borns_per_year),
        1961 : 654616 * 100 / max(borns_per_year),
        1960 : 663375 * 100 / max(borns_per_year),
        1959 : 654474 * 100 / max(borns_per_year),
        1958 : 653216 * 100 / max(borns_per_year),
        1957 : 646784 * 100 / max(borns_per_year),
        1956 : 608121 * 100 / max(borns_per_year),
        1955 : 598970 * 100 / max(borns_per_year),
        1954 : 577886 * 100 / max(borns_per_year),
        1953 : 589188 * 100 / max(borns_per_year),
        1952 : 593019 * 100 / max(borns_per_year),
        1951 : 567474 * 100 / max(borns_per_year),
        1950 : 565378 * 100 / max(borns_per_year),
        1949 : 601759 * 100 / max(borns_per_year),
        1948 : 642041 * 100 / max(borns_per_year),
        1947 : 588732 * 100 / max(borns_per_year),
        1946 : 585381 * 100 / max(borns_per_year),
    }

    values = dict(sorted(values.items()))
    
    print_probability_graphic(values, max_length, interval, True, False, 1)
    print("Gráfica de estadísitcas de muestra. En este caso muestra valores de natalidad en españa por año.")