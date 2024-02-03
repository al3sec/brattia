#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# El objetivo de este script es utilizar investing.com para realizar el analisis fundamental de una empresa.

import httpx
import numpy as np
import argparse
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style
import matplotlib.pyplot as plt


"""
 Activos por ver:

 SIMSA

"""


base_url = 'https://es.investing.com/instruments/Financials/changereporttypeajax?action=change_report_type&pair_ID='


# id, slug
empresas = {

    "AAPL":           [ "6408", "apple-computer-inc" ],
    "NVIDIA":         [ "6497", "nvidia-corp" ],
    "MELI":           [ "16599", "mercadolibre" ],
    "ENELCHILE":      [ "976489", "enersis-chile-sa" ],
    "OXIQUIM":        [ "1036886", "oxiquim" ],
    "ENELAM":         [ "41445", "enersis" ],
    "SMU":            [ "1055339", "smu" ],
    "MASISA":         [ "41468", "masisa" ],
    "HABITAT":        [ "41452", "a.f.p.-habitat" ],
    "ILC":            [ "41458", "inv-la-constru" ],
    "AAISA":          [ "1193024", "administradora-americana-de-invers" ],
    "CONCHATORO":     [ "41427", "vina-concha-to" ],
    "SOQUICOM":       [ "41485", "soquicom" ],
    "CCU":            [ "41417", "cervecerias-un" ],
    "CLOROX":         [ "7933", "clorox-co" ],
    "EMBONORB":       [ "41443", "embonor-b"],
    "LIPIGAS":        [ "996053", "empresas-lipigas-sa"],
    "NUEVAPOLAR":     [ "41462", "nuevapolar" ],
    "QUINENCO":       [ "41481", "quinenco" ],
    "PROVIDA":        [ "41480", "a.f.p.-provida" ],
    "ZOFRI":          [ "41500", "zofri" ],
    "ANDINA-A":       [ "41403", "emb-andina-a" ],
    "AESANDES":       [ "41407", "aesgener" ],
    "AGUAS-A":        [ "41402", "aguas-andinas" ],
    "CHILE":          [ "41422", "banco-de-chile-(sn)" ],
    "BCI":            [ "41412", "bci-(sn)" ],
    "CAP":            [ "41415", "cap" ],
    "CENCOSUD":       [ "41419", "cencosud" ],
    "CENCOSHOPP":     [ "1152242", "cencosud-shopping-sa" ],
    "COLBUN":         [ "41432", "colbun" ],
    "ANDINA-B":       [ "41404", "emb-andina-b" ],
    "BSANTANDER":     [ "41493", "santander-chil" ],
    "CMPC":           [ "41416", "cmpc" ],
    "COPEC":          [ "41434", "empresas-copec" ],
    "FALABELLA":      [ "41449", "falabella" ],
    "IAM":            [ "41455", "iam-sa" ],
    "OROBLANCO":      [ "41471", "oro-blanco" ],
    "RIPLEY":         [ "41482", "ripley-corp" ],
    "SECURITY":       [ "41487", "grupo-security" ],
    "SONDA":          [ "41489", "sonda" ],
    "SQM-B":          [ "41491", "soquimich-b" ],
    "LTM":            [ "41461", "latam-airlines" ],
    "CAROZZI":        [ "1161680", "carozzi-sa" ],
    "GASCO":          [ "41451", "gasco" ],
    "CRISTALES":      [ "41435", "cristales" ],
    "MALLPLAZA":      [ "1094237", "plaza" ],
    "ENTEL":          [ "41447", "entel" ],
    "ITAUCL":         [ "41431", "corpbanca-(sn)" ],
    "VAPORES":        [ "41497", "vapores" ],
    "PARAUCO":        [ "41472", "parq-arauco" ],
    "ECL":            [ "41438", "ecl-sa"],
}


# funciones auxiliares
def get_slug(nombre):
    return empresas[nombre][1]


def get_id(nombre):
    return empresas[nombre][0]


def special_print(word, color):
    print(Fore.GREEN + word) if color == 'GREEN' else  print(Fore.RED + word)
    print(Style.RESET_ALL)

def print_bool_result(condition):
    special_print('Si', 'GREEN') if condition  else special_print('No', 'RED')


def convert(balances):
    strNumber = balances.text.replace(",", ".").strip('%')
    if strNumber != '-':
        return float(strNumber)

    return float(0)


def get_annual_data(balances, a,b,c,d):
    return [ convert(balances[x]) for x in [a,b,c,d] ]


# c = un tercer array donde aplicar la funcion d
def array_calculations(a, b, d, c=None):
    a = a()
    b = b()
    if c is not None: c = c()
    return [ round(d(x, b[i], c[i]), 2) if c is not None else round(d(x, b[i]), 2) for i, x in enumerate(a)]


def razon_crecimiento(arreglo):
    x = np.array([2022, 2021, 2020, 2019])
    y = np.array(arreglo)
    return round(np.linalg.lstsq(np.vstack([x, np.ones(len(x))]).T, y, rcond=None)[0][0], 2)


def check_razon_creciente(razon):
    print_bool_result(razon > 0)
    return razon > 0


def check_razon_decreciente(razon):
    print_bool_result(razon <= 0)
    return razon <= 0


class Estados:
    def __init__(self, stock_name, period_type, n):
        self.stock_name = stock_name
        self.period_type = period_type
        self.slug = get_slug(stock_name)
        self.stock_id = get_id(stock_name)
        self.balances = self.set_balances()
        self.resultados = self.set_estado_resultado()
        self.ratios = self.set_ratios()
        self.ROE = self.set_ROE()
        self.tasa_reparto = self.set_tasa_reparto()
        self.precio_actual = self.set_precio_actual()
        self.g = self.set_tasa_crecimiento()
        self.eps_presente =  self.set_eps_presente()
        self.eps_promedio =  self.set_eps_promedio()
        self.eps_futuro = self.set_eps_futuro(n)
        self.precio_accion_futuro = self.set_precio_accion_futuro()
        self.tasa_dividendos = self.dividend_yield()
        self.precio_valor_contable = self.set_precio_valor_contable()
        self.per = self.set_per()
        self.flujos_caja = self.set_flujos_caja()
        self.n = n


    # balance de los ultimos 4 años
    def set_balances(self):
        url= base_url + self.stock_id + '&report_type=BAL&period_type=' + self.period_type
        try:
            result = httpx.get(url)
            soup = BeautifulSoup(result.content, 'html.parser')
            return soup.find_all('td')
        except:
            print("una excepcion ocurrio al intentar leer el balance")


    # cantidad de dinero que tiene la empresa, para financiar operaciones despues de pagar las deudas de corto plazo
    def capital_de_trabajo(self, activo_circulante, pasivo_circulante):
	      return (activo_circulante - pasivo_circulante)


    """
      Cantidad de pesos que tiene la empresa, para pagar cada peso de deuda (corto plazo).
      Si se agrega el inventario -> test acido, usar en empresas que vendan productos!
    """
    def razon_corriente(self, activo_circulante, pasivo_circulante, inventario=0):
        if pasivo_circulante > 0:
            return (activo_circulante - inventario) / pasivo_circulante
        else:
            print('pasivo circulante debe ser mayor a 0')
            return 0


    # porcion de activos que estan financiados por terceros
    def razon_endeudamiento(self, pasivos_totales, activos_totales):
        if activos_totales > 0:
            return pasivos_totales / activos_totales
        else:
            print('activos totales deben ser mayor 0')
        return 0


    # ultimo precio de la accion
    def set_precio_actual(self):
        url= 'https://es.investing.com/equities/' + self.slug
        try:
            result = httpx.get(url)
            soup = BeautifulSoup(result.content, 'html.parser')
            elements = soup.find_all('span')
            index = 0

            for i, a in enumerate(elements):
            # print(str(i) + ':' + a.text)
                if a.text == 'Resumen':
                    index = i + 1
                    break

            precio = elements[index].text.replace('.', '').replace(',', '.')
            # print(str(precio))
            return float(precio)

        except:
            print("una excepcion ocurrio al intentar leer el precio actual")


     # lista con los ultimos 4 años de activo circulante
    def total_activo_circulante(self):
        return get_annual_data(self.balances,1,2,3,4)


    # lista con los ultimos 4 años de pasivo circulante
    def total_pasivo_circulante(self):
        return get_annual_data(self.balances,103,104,105,106)


    # lista con los ultimos 4 años de inventario (existencias)
    def total_inventario(self):
        return get_annual_data(self.balances,37,38,39,40)


    def pasivos_totales(self):
        return get_annual_data(self.balances,139,140,141,142)


    def activos_totales(self):
        return get_annual_data(self.balances,52,53,54,55)


    def patrimonio_neto(self):
        return get_annual_data(self.balances,175,176,177,178)


    def total_ingresos(self):
        return get_annual_data(self.resultados, 1, 2, 3, 4)


    def total_margen_bruto(self):
        return get_annual_data(self.resultados, 22, 23, 24, 25)


    def total_costo_venta(self):
        return get_annual_data(self.resultados, 27, 28, 29, 30)


    def total_resultado_explotacion(self):
        return get_annual_data(self.resultados, 63, 64, 65, 66)


    # utilidad neta
    def total_resultado_ejercicio(self):
        return get_annual_data(self.resultados, 143, 144, 145, 146)


    def total_beneficio_por_accion(self):
        return get_annual_data(self.resultados,163,164,165,166)


    def total_dividendos_por_accion(self):
        return get_annual_data(self.resultados,158,159,160,161)

    def total_free_cash_flow(self):
        return get_annual_data(self.flujos_caja,119,120,121,122)


    def acciones_circulando(self):
        accionesComunes = get_annual_data(self.balances,231,232,233,234)
        accionesPreferidas = get_annual_data(self.balances,236,237,238,239)
        return [ a + accionesPreferidas[i] for i, a in enumerate(accionesComunes)]


    def total_efectivo_e_inversiones(self):
        total_arr = self.balances[5].text.splitlines()
        total = [ t for i,t in enumerate(total_arr)  if i in [14,15,16,17] ]
        return [ 0 if u == '-' else float(u.replace(",", ".").strip('%')) for u in total ]


    def total_DPS_EPS(self):
        totalBeneficio  = get_annual_data(self.resultados,153,154,155,156)
        totalDividendos = get_annual_data(self.resultados,158,159,160,161)
        return [ round(d / totalBeneficio[i], 2) if totalBeneficio[i] > 0  else 0 for i, d in enumerate(totalDividendos)]


    def valor_libro_ajustado(self):
        accionesCirculando = self.acciones_circulando()
        patrimonioNeto = self.patrimonio_neto()
        return [ round(patrimonioNeto[i] / a, 2) if a > 0 else 0 for i, a in enumerate(accionesCirculando)]


    def total_test_acido(self):
        return array_calculations(self.total_activo_circulante, self.total_pasivo_circulante,
            self.razon_corriente, self.total_inventario)


    def total_capital_trabajo(self):
        return array_calculations(self.total_activo_circulante, self.total_pasivo_circulante, self.capital_de_trabajo)


    def total_razon_corriente(self):
        return array_calculations(self.total_activo_circulante, self.total_pasivo_circulante, self.razon_corriente)


    def total_razon_endeudamiento(self):
        return array_calculations(self.pasivos_totales, self.activos_totales, self.razon_endeudamiento)


    def total_razon_deuda_patrimonio(self):
        return array_calculations(self.pasivos_totales, self.patrimonio_neto, self.razon_endeudamiento)


    def check_test_acido(self):
        totalTestAcido = self.total_test_acido()
        mean = np.mean(totalTestAcido)
        print(round(mean, 2))
        print_bool_result(mean >= 1)


    def check_capital_trabajo(self):
        totalCapitalTrabajo = self.total_capital_trabajo()
        mean = np.mean(totalCapitalTrabajo)
        print(round(mean, 2))
        print_bool_result(mean > 0)


    def check_razon_corriente(self):
        totalRazonCorriente = self.total_razon_corriente()
        mean = np.mean(totalRazonCorriente)
        print(round(mean, 2))
        print_bool_result(mean >= 1)


    def check_razon_endeudamiento(self):
        totalRazonEndeudamiento = self.total_razon_endeudamiento()
        mean = np.mean(totalRazonEndeudamiento)
        print(round(mean, 2))
        print_bool_result(mean <= 0.5)


    # Actividad operacional
    def margen_bruto(self, ingreso_venta, costos_directos):
        if ingreso_venta > 0:
            return 100 * (ingreso_venta - costos_directos) / ingreso_venta
        else:
            print('pasivo circulante no debe ser 0')
        return 0


    # beneficios antes de intereses, impuestos, depreciacion y amortizaciones
    def ebitda(self, margen_bruto, gastos_administracion, gastos_venta):
        return margen_bruto - gastos_administracion - gastos_venta


    def resultado_operacional(self, ebitda, depreciacion):
        return ebitda - depreciacion


    def roe_calculado(self, utilidad_neta, patrimonio):
        if patrimonio > 0 :
            return utilidad_neta / patrimonio
        else:
            print('patrimonio deben ser mayor a 0')


    def ROE_ajustado(self):
        if self.precio_valor_contable > 0:
            return round(self.ROE / self.precio_valor_contable, 2)
        else:
            print('precio bolsa libro debe ser mayor a 0')


    def casanegra_ratio(self, activo_circulante, total_efectivo, costo_venta):
        return round((activo_circulante - total_efectivo) / costo_venta, 2) if costo_venta > 0 else 0


    # estado resultado los ultimos 4 años
    def set_estado_resultado(self):
        url= base_url + self.stock_id + '&report_type=INC&period_type=' + self.period_type
        try:
            result = httpx.get(url)
            soup = BeautifulSoup(result.content, 'html.parser')
            return soup.find_all('td')
        except:
            print("una excepcion ocurrio al intentar leer el estado resultado")


    # ratios
    def set_ratios(self):
        url= 'https://es.investing.com/equities/' + self.slug + '-ratios'
        try:
            result = httpx.get(url)
            soup = BeautifulSoup(result.content, 'html.parser')
            return soup.find_all('td')
        except:
            print("una excepcion ocurrio al intentar leer los ratios")


    # flujos de caja
    def set_flujos_caja(self):
        # cambiando a anualizado
        with httpx.Client() as client:
            url= base_url + self.stock_id + '&report_type=CAS&period_type=' + self.period_type
            result = client.get(url)
            soup = BeautifulSoup(result.content, 'html.parser')
            return soup.find_all('td')


    # (AC-Caja) / Ventas
    def total_casanegra_ratio(self):
        return array_calculations(self.total_activo_circulante,
            self.total_efectivo_e_inversiones, self.casanegra_ratio, self.total_costo_venta)


    def total_margen_bruto_calculado(self):
        totalIngresos = self.total_ingresos()
        costoVenta = self.total_costo_venta()
        return [ round(self.margen_bruto(t, costoVenta[i]), 2) for i, t in enumerate(totalIngresos)]


    # Rentabilidad sobre el capital (equity) 5YA
    def set_ROE(self):
        index = 0
        for i, r in enumerate(self.ratios):
            # print(str(i) + ':' + r.text)
            if 'Rentabilidad sobre la inversión 5YA' in r.text:
                index = i + 1

        return convert(self.ratios[index])


    # tasa de reparto (payout ratio) 5YA  (buena entre 50 y 70 %)
    def set_tasa_reparto(self):
        index = 0
        for i, r in enumerate(self.ratios):
            # print(str(i) + ':' + r.text)
            if 'Ratio Payout TTM' == r.text:
                index = i + 1
                break

        result = convert(self.ratios[index])

        if result < 100.0:
            return result

        return 100.0


    # price earning ratio :relacion entre el precio de la accion presente y la ganancia que tiene la empresa por accion
    def set_per(self):
        if self.eps_presente != 0:
            return self.precio_actual / self.eps_presente
        else:
            print('eps no debe ser cero')
        return 0


    # Dividend Yield 5 Year Avg. 5YA
    def dividend_yield(self):
        index = 0
        for i, r in enumerate(self.ratios):
            # print(str(i) + ':' + r.text)
            if 'Promedio de Rendimiento del Dividendo en 5 Años 5YA' == r.text:
                index = i + 1
                break

        return convert(self.ratios[index])


    # Dividend Growth Rate
    def dividend_growth_rate(self):
        index = 0
        for i, r in enumerate(self.ratios):
            # print(str(i) + ':' + r.text)
            if 'Tasa de Crecimiento de los Dividendos ANN' == r.text:
                index = i + 1
                break

        return convert(self.ratios[index])


    # FCF/ Patrimonio para todos los años.
    def fcf_patrimonio(self):
        patrimonioNeto = self.patrimonio_neto()
        freeCash = self.total_free_cash_flow()
        return [ round(100 * (f / patrimonioNeto[i]) , 2)
            if patrimonioNeto[i] > 0 else 0 for i,f in enumerate(freeCash)]


    # tipo de empresa por tasa de crecimiento
    def tipo_empresa(self):
        if self.g < 10:
            return 'crecimiento bajo (dividenderas)'
        elif self.g < 15 and self.g > 10:
            return 'crecimiento medio'
        elif self.g > 15:
            return 'crecimiento alto'
        else:
            return  'indefinido'


    def set_tasa_crecimiento(self):
        # print('roe:' + str(self.ROE) + ', tasa de reparto:' + str(self.tasa_reparto) )
        return round(self.ROE * (1 - (self.tasa_reparto / 100)), 2)


    def set_eps_presente(self):
        url= 'https://es.investing.com/equities/' + self.slug
        try:
            result = httpx.get(url)
            soup = BeautifulSoup(result.content, 'html.parser')
            elements = soup.find_all('span')
            index = 0

            for i, a in enumerate(elements):
                #print(str(i) + ':' + a.text)
                if a.text == 'BPA':
                    index = i + 1
                    break

            eps = elements[index].text.replace('.', '').replace(',', '.')
            print(str(eps))
            return float(eps)
        except:
            print("una excepcion ocurrio al intentar leer el EPS presente")


    # promedio a 5 años
    def set_eps_promedio(self):
        eps_s = self.total_beneficio_por_accion()
        return np.mean(eps_s)

    # usando eps presente
    def set_eps_futuro(self, n):
        print('eps_presente: '+ str(self.eps_presente))
        print('g: '+ str(self.g))
        return  self.eps_presente * (1 + (self.g / 100)) ** n


    def set_precio_accion_futuro(self):
        return self.eps_futuro * self.get_multiplo_per()


    # si son acciones con dividendos, se debe agregar la tasa de retorno por ella  (rentabilidad en %)
    def rentabilidad_capital(self, impuesto_dividendo):
        return round(100 * ((self.precio_accion_futuro / self.precio_actual)**(1/float(self.n))
            - 1 + (self.tasa_dividendos/100) * (1 - impuesto_dividendo)), 2)


    # margen de seguridad tipico : 15 %
    def analisis_casanegra(self, margenSeguridad):
        precioPresente =  self.precio_accion_futuro / (1 + (self.g / 100))**(self.n)
        print('--------------------------------')
        print('precio presente calculado: ')
        print(round(precioPresente, 2))
        print('')

        precioAjustado = (1 - (margenSeguridad / 100)) * precioPresente

        print('precio presente calculado con margen de seguridad de ' + str(margenSeguridad) + '(%): ')
        print(round(precioAjustado, 2))
        print('')

        if self.precio_actual <= precioAjustado:
            print('[+] Comprar! precio actual en bolsa < precio presente ajustado')
        else:
            print('[+] Esperar, precio actual en bolsa > precio presente ajustado')

        print('--------------------------------')
        print('')


    """
      Utilidad = ingresos - gastos de explotación - gastos financieros
      Utilidad de explotación = ingresos - gastos de explotación
      Utilidad bruta = ingresos - costos de explotación
    """
    def grafico_amigo(self):
        totalExplotacion = self.total_resultado_explotacion()
        totalFCF = self.total_free_cash_flow()
        years = np.array([2019, 2020, 2021, 2022])
        plt.plot(years,np.array(totalExplotacion[::-1]), label="resultado explotacion")
        plt.plot(years,np.array(totalFCF[::-1]), label="free cash flow")
        plt.legend()
        plt.xlabel('años')
        plt.ylabel('$')
        plt.title('Grafico amigo ')
        plt.show()


    def check_valor_bolsa_libro(self):
        if self.precio_valor_contable >= 1.0 and self.precio_valor_contable < 6.0:
            return 'normal'
        elif self.precio_valor_contable >= 6.0:
            return 'muy alto, podria corregir precio'
        elif self.precio_valor_contable < 1.0:
            return 'valor en bolsa por debajo del valor libro'


    # precio / valor contable  (valor bolsa/libro)
    def set_precio_valor_contable(self):
        index = 0
        for i, r in enumerate(self.ratios):
        # print(str(i) + ':' + r.text)
            if 'Precio/Valor Contable MRQ' in r.text:
                index = i + 1
        # print('valor BOLSA/LIBRO:' + ratios[index].text)

        return convert(self.ratios[index])


    # tomando eps promedio de 5A
    def earning_yield(self):
        epsMean = np.mean(self.total_beneficio_por_accion())
        return round(100 * (epsMean /  self.precio_actual), 2)


    # multiplo de per (g en %)
    def get_multiplo_per(self):
        # empresas dividenderas
        if self.g < 10:
            return 12.5
        # empresas intermedias
        elif self.g < 15:
            return 18
        # empresas de crecimiento
        elif self.g >= 15:
            return 25


    def get_ratios(self):
        return self.ratios


    def get_estado_resultado(self):
        return self.resultados


    def get_balances(self):
        return self.balances


    def get_ROE(self):
        if round(self.ROE, 2) > 15.0:
            print(Fore.GREEN + str(self.ROE))
        else:
            print(Fore.RED + str(self.ROE))
        print(Style.RESET_ALL)


    def get_precio_actual(self):
        return self.precio_actual


    def get_precio_accion_futuro(self):
        return round(self.precio_accion_futuro, 2)


    def get_tasa_dividendos(self):
        return round(self.tasa_dividendos, 2)


    def get_precio_valor_contable(self):
        return self.precio_valor_contable


    def get_tasa_reparto(self):
        return self.tasa_reparto


    def get_tasa_crecimiento(self):
        return self.g


    def get_eps_futuro(self):
        return round(self.eps_futuro,2)


    def get_eps_promedio(self):
        return round(self.eps_promedio,2)

    def get_eps_presente(self):
        return round(self.eps_presente,2)


    def get_per(self):
        return round(self.per, 2)


    """
      El valor del índice PEG de 1 representa una correlación perfecta entre el valor de mercado de la empresa
      y el crecimiento de sus ganancias proyectado. Los índices de PEG superiores a 1,0 generalmente se consideran
      desfavorables, lo que sugiere que una acción está sobrevaluada. Por el contrario, los ratios son más bajos
      superiores a 1,0 se consideran mejores, lo que indica que una acción está infravalorada.
    """
    def get_peg(self):
        if self.g > 0:
            return round(self.per / self.g, 2)
        else:
            print('el crecimiento debe ser mayor a cero')
            return 0


    def get_stock_name(self):
        return self.stock_name


# main
if __name__=="__main__":

    parser = argparse.ArgumentParser(prog="stocks.py", epilog="Fundamental Analisis Script", usage="stocks.py [options] -n <STOCK-NAME>", prefix_chars='-', add_help=True)

    parser.add_argument('-n', action='store', metavar='stock-name', type=str, help='Stock Name.\tExample: AAPL', required=True)
    parser.add_argument('-v', action='version', version='alpha - v1.0', help='Prints the version of stocks.py')

    args = parser.parse_args()

    b = Estados(args.n, 'Annual', 5)

    # --------------------------------------------------------------------------------------------------------------------
    # a) Balance  (fotografía de la empresa)

    """
        Criterios a cumplir en los balances anuales:

           1) capital de trabajo > 0
           2) razon corriente > 1
           3) test acido > 1
           4) razon de endeudamiento < 50%

           5) Activos totales crecientes
           6) Patrimonio creciente (total equity)
           7) Numero de acciones constantes o disminuyendo

    """
    print('nombre de la accion:')
    print(b.get_stock_name())
    print('')

    print('total activo circulante:')
    totalActivoCirculante = b.total_activo_circulante()
    print(totalActivoCirculante)
    print('')

    print('total pasivo circulante:')
    print(b.total_pasivo_circulante())
    print('')

    print('total capital de trabajo:')
    total = b.total_capital_trabajo()
    print(total)
    print('')

    print('total razon corriente:')
    razon = b.total_razon_corriente()
    print(razon)
    print('')

    print('total inventario:')
    inventario = b.total_inventario()
    print(inventario)
    print('')

    print('total test acido:')
    test = b.total_test_acido()
    print(test)
    print('')

    print('activos totales:')
    activosTotales = b.activos_totales()
    print(activosTotales)
    print('')

    print('pasivos totales:')
    pasivosTotales = b.pasivos_totales()
    print(pasivosTotales)
    print('')

    print('total razon endeudamiento:')
    totalRazonEndeudamiento = b.total_razon_endeudamiento()
    print(totalRazonEndeudamiento)
    print('')

    print('razon crecimiento activos totales:')
    razonCrecimientoActivos = razon_crecimiento(activosTotales)
    print(razonCrecimientoActivos)
    print('')

    print('razon crecimiento activos circulantes:')
    razonActivoCirculante = razon_crecimiento(totalActivoCirculante)
    print(razonActivoCirculante)
    print('')

    print('patrimonio neto:')
    patrimonioNeto = b.patrimonio_neto()
    print(patrimonioNeto)
    print('')

    print('razon crecimiento patrimonio:')
    razonPatrimonio = razon_crecimiento(patrimonioNeto)
    print(razonPatrimonio)
    print('')

    print('acciones circulando:')
    acciones = b.acciones_circulando()
    print(acciones)
    print('')

    print('razon crecimiento acciones:')
    razonAcciones = razon_crecimiento(acciones)
    print(razonAcciones)
    print('')


    # 1) capital de trabajo > 0
    print('total capital de trabajo positivo?:')
    b.check_capital_trabajo()


    # 2) razon corriente > 1
    print('razon corriente > 1?:')
    b.check_razon_corriente()


    # 3) test acido > 1
    print('test acido > 1?:')
    b.check_test_acido()


    # 4) razon de endeudamiento < 50%
    print('razon endeudamiento menor a 0.5?:')
    b.check_razon_endeudamiento()


    # 5) Activos totales crecientes
    print('razon crecimiento activos > 0 :')
    check_razon_creciente(razonCrecimientoActivos)


    # 6) Patrimonio creciente (total equity)
    print('patrimonio creciente? :')
    check_razon_creciente(razonPatrimonio)


    # 7) Numero de acciones constantes o disminuyendo
    print('acciones constantes o disminuyendo? :')
    check_razon_decreciente(razonAcciones)

    # --------------------------------------------------------------------------------------------------------------------
    # b) Estado Resultado  (reporte en un periodo determinado de tiempo respecto ingresos y egresos)

    """
        Criterios a cumplir en el estado resultado:

           1) ingresos crecientes
           2) margen bruto creciente (sobre 40 %)
           3) resultado operacional creciente
           4) utilidad neta creciente (sobre 20 %)
           5) EPS creciente
           6) ROE > 15 %


    """

    print('total ingresos:')
    totalIngresos = b.total_ingresos()
    print(totalIngresos)
    print('')

    razonIngresos = razon_crecimiento(totalIngresos)

    print('razon ingresos:')
    print(razonIngresos)
    print('')


    # 1) ingresos crecientes
    print('razon ingresos creciente?:')
    check_razon_creciente(razonIngresos)

    print('total margen bruto:')
    totalMargenBruto = b.total_margen_bruto()
    print(totalMargenBruto)
    print('')

    razonMargenBruto = razon_crecimiento(totalMargenBruto)

    print('razon margen bruto:')
    print(razonMargenBruto)
    print('')

    print('total margen bruto calculado (%):')
    margenBrutoCalculado = b.total_margen_bruto_calculado()
    print(margenBrutoCalculado)
    print('')


    # 2) margen bruto creciente (sobre 40 %)
    print('margen bruto creciente?:')
    check_razon_creciente(razonMargenBruto)


    # 3) resultado operacional creciente
    print('total resultado explotacion:')
    totalResultadoExplotacion = b.total_resultado_explotacion()
    print(totalResultadoExplotacion)
    print('')


    razonResultadoExplotacion = razon_crecimiento(totalResultadoExplotacion)
    print('razon resultado explotacion:')
    print(razonResultadoExplotacion)
    print('')
    print('resultado explotacion creciente?:')
    check_razon_creciente(razonResultadoExplotacion)


    # 4) utilidad neta creciente (sobre 20 %)
    totalResultadoEjercicio = b.total_resultado_ejercicio()

    print('total resultado ejercicio:')
    print(totalResultadoEjercicio)
    print('')

    print('razon ejercicio:')
    razonResultadoEjercicio = razon_crecimiento(totalResultadoEjercicio)
    print(razonResultadoEjercicio)
    print('')

    print('resultado ejercicio creciente?:')
    check_razon_creciente(razonResultadoEjercicio)


    # 5) EPS creciente
    totalBeneficioPorAccion = b.total_beneficio_por_accion()

    print('total beneficio por accion (EPS):')
    print(totalBeneficioPorAccion)
    print('')

    print('razon beneficio por accion:')
    razonBeneficioPorAccion = razon_crecimiento(totalBeneficioPorAccion)
    print(razonBeneficioPorAccion)
    print('')

    print('razon beneficio por accion creciente?:')
    check_razon_creciente(razonBeneficioPorAccion)


    # 6) ROE > 15 %

    print('ROE (%):')

    b.get_ROE()
    print('')

    print('ROE ajustado (%):')

    roeAjustado = b.ROE_ajustado()
    print(roeAjustado)
    print('')

    # --------------------------------------------------------------------------------------------------------------------
    # c) Valorizacion de la Empresa

    """
        Pasos para tomar decision de inversion en la empresa:

           1) Determinar G para ver tasa de crecimiento
           2) Calcular un estimado de EPS futuro
           3) Aplicar multiplo de PER que corresponda
           4) Calcular rentabilidad de nuestro capital

    """

    # 1) Determinar G para ver tasa de crecimiento


    tasaReparto = b.get_tasa_reparto()

    print('tasa de reparto (%):')
    print(tasaReparto)
    print('')


    g = b.get_tasa_crecimiento()
    print('tasa de crecimiento (%):')
    print(g)
    print('')


    print('tipo de empresa:')
    print(b.tipo_empresa())
    print('')


    # 2) Calcular un estimado de EPS futuro

    epsFuturo = b.get_eps_futuro()

    print('epsFuturo:')
    print(epsFuturo)
    print('')

    epsPresente = b.get_eps_presente()

    print('epsPresente:')
    print(epsPresente)
    print('')

    epsPromedio = b.get_eps_promedio()

    print('epsPromedio:')
    print(epsPromedio)
    print('')


    # 3) Aplicar multiplo de PER que corresponda (precio en 5 años)

    print('precio accion a 5 años:')
    precioFuturo = b.get_precio_accion_futuro()
    print(precioFuturo)
    print('')

    # Calcular rentabilidad de nuestro capital
    precioPresente = b.get_precio_actual()

    print('precio actual:')
    print(precioPresente)
    print('')

    rentabilidad = b.rentabilidad_capital(0)

    print('rentabilidad (%):')
    print(rentabilidad)
    print('')

    if g > 0:
        print('Como g > 0 análisis casanegra :')
        b.analisis_casanegra(15)


    print('valor bolsa/libro:')
    bolsaLibro = b.get_precio_valor_contable()
    print(bolsaLibro)
    print('')

    print('analisis valor bolsa/libro:')
    print(b.check_valor_bolsa_libro())
    print('')

    # PER (para empresas dividenderas) 12-15
    print('ratio precio / utilidad (PER):')
    print(b.get_per())
    print('')

    print('ratio (precio / utilidad) / g (PEG):')
    print(b.get_peg())
    print('')

    # Deuda / patrimonio >>> 1, muy superior a 1,  mejor hacerse a un lado.
    print('deuda total / patrimonio:')
    print(b.total_razon_deuda_patrimonio())
    print('')
    print('valor libro ajustado:')
    print(b.valor_libro_ajustado())
    print('')

    print('Earnings yield (EPS/P) (%):')
    print(b.earning_yield())
    print('')

    print('Dividend yield (D/P) (%):')
    print(b.dividend_yield())
    print('')

    print('Dividend growth yield (%):')
    print(b.dividend_growth_rate())
    print('')

    # FCF/Patrimonio (bueno: sobre 15-18%)
    print('FCF / Patrimonio %:')
    print(b.fcf_patrimonio())
    print('')
    print('(AC-Caja) / Ventas:')
    casanegra = b.total_casanegra_ratio()
    print(casanegra)
    print('')

    print('(AC-Caja) / Ventas constante o disminuyendo? :')
    razonCasanegra = razon_crecimiento(casanegra)
    print(razonCasanegra)
    check_razon_decreciente(razonCasanegra)
    print('')

    # DPS/EPS (dividend per share / earning per share)  fracción que efectivamente la empresa reparte
    print('DPS/EPS para cada año:')
    print(b.total_DPS_EPS())
    print('')

    print('DPS/EPS promedio % (últimos 4 años):')
    print(100 * round(np.mean(b.total_DPS_EPS()) ,2))

    print('Gráfico amigo:')
    b.grafico_amigo()

    # --------------------------------------------------------------------------------------------------------------------
    # d) Futurologia? (necesitamos variables cuantitativas o chatgpt)
