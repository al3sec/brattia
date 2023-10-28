#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# El objetivo de este script es utilizar investing.com para realizar el analisis fundamental de una empresa.

import httpx
import numpy as np
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style


"""
 Activos por ver:

 SIMSA

"""


base_url = 'https://es.investing.com/instruments/Financials/changereporttypeajax?action=change_report_type&pair_ID='

# id, slug
empresas = {

    "AAPL":           [ "6408", "apple-computer-inc" ],
    "ENELCHILE":      [ "976489", "enersis-chile-sa" ],
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
    "AGUASA":         [ "41402", "aguas-andinas" ],
    "BANCOCHILE":     [ "41422", "banco-de-chile-(sn)" ],
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

  } 

# funciones auxiliares
def get_slug(nombre):
  return empresas[nombre][1]
   

def get_id(nombre):
  return empresas[nombre][0]


def print_si():
    print(Fore.GREEN + 'Si')
    print(Style.RESET_ALL)


def print_no():
    print(Fore.RED + 'No')
    print(Style.RESET_ALL)


def convert(balances): 
  number = 0
  strNumber = balances.text.replace(",", ".").strip('%')
  if strNumber == '-':
    return float(number)
  else:
    return float(strNumber)

  
def get_annual_data(balances, a,b,c,d):
  args = [a,b,c,d]
  lista = []
  for a in args: 
    lista.append(convert(balances[a]))
  return lista

def razon_crecimiento(arreglo):
  x = np.array([2022, 2021, 2020, 2019])
  y = np.array(arreglo)
  return np.linalg.lstsq(np.vstack([x, np.ones(len(x))]).T, y, rcond=None)[0][0]


def check_razon_creciente(razon):
  print_si() if razon > 0 else print_no()
     

def check_razon_decreciente(razon):
  print_si() if razon <= 0 else print_no()
 

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
    self.eps_futuro = self.set_eps_futuro(n)
    self.precio_accion_futuro = self.set_precio_accion_futuro()
    self.tasa_dividendos = self.set_tasa_dividendos()
    self.precio_valor_contable = self.set_precio_valor_contable()
    self.per = self.set_per()
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

  # cantidad de dinero que tiene la empresa, para financiar sus operaciones despues de pagar las deudas de corto plazo
  def capital_de_trabajo(self, activo_circulante, pasivo_circulante):
	  return (activo_circulante - pasivo_circulante)

  # cantidad de pesos que tiene la empresa, para pagar cada peso de deuda (corto plazo) , si se agrega el inventario -> test acido, usar en empresas que vendan productos!
  def razon_corriente(self, activo_circulante, pasivo_circulante, inventario=0):
    if pasivo_circulante > 0:
      return (activo_circulante - inventario) / pasivo_circulante
    else:
      print('pasivo circulante no debe ser 0')
      return 0

  # porcion de activos que estan financiados por terceros
  def razon_endeudamiento(self, pasivos_totales, activos_totales):
    if activos_totales != 0:
      return (pasivos_totales / activos_totales)
    else:
      print('activos totales no deben ser 0')
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

      precio = elements[index].text.replace('.', '').replace(',', '.')
      # print(str(precio))
      return float(precio)
    except:
      print("una excepcion ocurrio al intentar leer el precio actual")


  def set_tasa_dividendos(self):
    url= 'https://es.investing.com/equities/' + self.slug + '-dividends'
    try:
      result = httpx.get(url)
      soup = BeautifulSoup(result.content, 'html.parser')
      elements = soup.find_all('td')

      indexes = []
      for i, a in enumerate(elements):
        # print(str(i) + ':' + a.text)
        if 'IBEX 35' in a.text:
          break 
        if '%' in a.text or '-' in a.text:
          indexes.append(i)

      lista = []
      # print(indexes)

      for j in indexes:
        lista.append(convert(elements[j]))

      return np.mean(lista)

    except:
      print("una excepcion ocurrio al intentar leer la tasa de dividendos")

   # lista con los ultimos 4 años de activo circulante
  def total_activo_circulante(self):
    return get_annual_data(self.balances,1,2,3,4)

  # lista con los ultimos 4 años de pasivo circulante
  def total_pasivo_circulante(self):
    return get_annual_data(self.balances,103,104,105,106)

  # lista con los ultimos 4 años de inventario (existencias)
  def total_inventario(self):
    return get_annual_data(self.balances,37,38,39,40)


  def total_capital_trabajo(self):
    activo = self.total_activo_circulante()
    pasivo = self.total_pasivo_circulante()
    lista = []

    for i, a in enumerate(activo):
      lista.append(self.capital_de_trabajo(a, pasivo[i]))
      
    return lista


  def total_test_acido(self):
    activo = self.total_activo_circulante()
    pasivo = self.total_pasivo_circulante()
    inventario = self.total_inventario()
    lista = []

    for i, a in enumerate(activo):
      lista.append(self.razon_corriente(a, pasivo[i], inventario[i]))
  
    return lista


  def total_razon_corriente(self):
    activo = self.total_activo_circulante()
    pasivo = self.total_pasivo_circulante()
    lista = []
  
    for i, a in enumerate(activo):
      lista.append(self.razon_corriente(a, pasivo[i]))
      
    return lista


  def pasivos_totales(self):
    return get_annual_data(self.balances,139,140,141,142)


  def activos_totales(self):
    return get_annual_data(self.balances,52,53,54,55)


  def patrimonio_neto(self):
    return get_annual_data(self.balances,175,176,177,178)


  def total_razon_endeudamiento(self):
    activo = self.activos_totales()
    pasivo = self.pasivos_totales()
    lista = []

    for i, a  in enumerate(activo):
      lista.append(self.razon_endeudamiento(pasivo[i], a))
      
    return lista

  def total_razon_deuda_patrimonio(self):
    pasivo = self.pasivos_totales()
    patrimonio = self.patrimonio_neto()
    lista = []

    for i, a  in enumerate(pasivo):
      lista.append(self.razon_endeudamiento(a, patrimonio[i]))
      
    return lista


  def acciones_circulando(self):
  # Acciones comunes en circulación
    accionesComunes = get_annual_data(self.balances,231,232,233,234)
    accionesPreferidas = get_annual_data(self.balances,236,237,238,239)
    lista = []
    for i, a in enumerate(accionesComunes):
      lista.append(a + accionesPreferidas[i])

    return lista

  def valor_libro_ajustado(self):
    accionesCirculando = self.acciones_circulando()
    patrimonioNeto = self.patrimonio_neto()
    lista = []
    for i, a in enumerate(accionesCirculando):
      lista.append(patrimonioNeto[i] / a) if a > 0 else lista.append(0)

    return lista

  def check_test_acido(self):
    totalTestAcido = self.total_test_acido()
    #return all([val > 1 for val in totalTestAcido])
    mean = np.mean(totalTestAcido)
    print(mean)
    print_si() if mean >= 1 else print_no()


  def check_capital_trabajo(self):
    totalCapitalTrabajo = self.total_capital_trabajo()
    mean = np.mean(totalCapitalTrabajo)
    print(mean)
    print_si() if mean > 0 else print_no()


  def check_razon_corriente(self):
    totalRazonCorriente = self.total_razon_corriente()
    mean = np.mean(totalRazonCorriente)
    print(mean)
    print_si() if mean >= 1 else print_no()


  def check_razon_endeudamiento(self):
    totalRazonEndeudamiento = self.total_razon_endeudamiento()
    mean = np.mean(totalRazonEndeudamiento)
    print(mean)
    print_si() if mean <= 0.5 else print_no()

  # Actividad operacional
  def margen_bruto(self, ingreso_venta, costos_directos):
    if ingreso_venta != 0:
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
    if patrimonio != 0:
      return utilidad_neta / patrimonio
    else:
      print('patrimonio no deben ser 0')

  def ROE_ajustado(self):
    if self.precio_valor_contable != 0:
      return self.ROE / self.precio_valor_contable
    else:
      print('precio bolsa libro no debe ser 0')

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
    return get_annual_data(self.resultados,153,154,155,156)


  def total_margen_bruto_calculado(self):
    totalIngresos = self.total_ingresos()
    costoVenta = self.total_costo_venta()
    lista = []

    for i, t in enumerate(totalIngresos):
      lista.append(self.margen_bruto(t, costoVenta[i]))
      
    return lista  

  # Rentabilidad sobre el capital (equity) 5YA
  def set_ROE(self):
    index = 0
    for i, r in enumerate(self.ratios):
      # print(str(i) + ':' + r.text)
      if 'Rentabilidad sobre la inversión 5YA' in r.text:
        index = i + 1

    return convert(self.ratios[index])

  # tasa de reparto (payout ratio) 5YA
  def set_tasa_reparto(self):
    index = 0
    for i, r in enumerate(self.ratios):
      # print(str(i) + ':' + r.text)
      if 'Ratio Payout TTM' == r.text:
        index = i + 1
        break

    result = convert(self.ratios[index])
    if result > 100.0:
      return 100.0
    else:
      return result

  # price earning ratio  (relacion entre el precio de la accion presente y la ganancia que tiene la empresa por accion) 
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


  # tipo de empresa por tasa de crecimiento
  def tipo_empresa(self):
    if self.g < 10:
      return 'crecimiento bajo (dividenderas)'
    if self.g < 15 and self.g > 10: 
      return 'crecimiento medio'
    if self.g > 15:
      return 'crecimiento alto'
    else:
      return  'indefinido'


  def set_tasa_crecimiento(self):
    # print('roe:' + str(roe) + ', tasa de reparto:' + str(tasa_reparto) )
    return self.ROE * (1 - (self.tasa_reparto / 100)) 


  def set_eps_presente(self):
    eps_s = self.total_beneficio_por_accion()
    return eps_s[0]


  def set_eps_futuro(self, n):
    return self.eps_presente * (1 + (self.g/100)) ** n


  def set_precio_accion_futuro(self):
    return self.eps_futuro * self.get_multiplo_per()


  # si son acciones con dividendos, se debe agregar la tasa de retorno por ella  (rentabilidad en %)
  def rentabilidad_capital(self, impuesto_dividendo):
    return 100 * ((self.precio_accion_futuro / self.precio_actual)**(1/float(self.n)) - 1 + (self.tasa_dividendos/100) * (1 - impuesto_dividendo))


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
    return 100 * (epsMean /  self.precio_actual)

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
    print(Fore.GREEN + str(self.ROE)) if round(self.ROE, 2) > 15.0 else print(Fore.RED + str(self.ROE))
    print(Style.RESET_ALL)
    

  def get_precio_actual(self):
    return self.precio_actual


  def get_precio_accion_futuro(self):
    return self.precio_accion_futuro


  def get_tasa_dividendos(self):
    return self.tasa_dividendos


  def get_precio_valor_contable(self):
    return self.precio_valor_contable

  
  def get_tasa_reparto(self):
    return self.tasa_reparto


  def get_tasa_crecimiento(self):
    return self.g


  def get_eps_futuro(self):
    return self.eps_futuro


  def get_per(self):
    return self.per


  def get_stock_name(self):
    return self.stock_name


b = Estados('SQM-B', 'Annual', 5)

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

tasaDividendo = b.get_tasa_dividendos() / 100

print('tasa promedio últimos dividendos (%):')
print(100 * tasaDividendo)
print('')

rentabilidad = b.rentabilidad_capital(0)

print('rentabilidad (%):')
print(rentabilidad)
print('')

print('valor bolsa/libro:')
bolsaLibro = b.get_precio_valor_contable()
print(bolsaLibro)
print('')

print('analisis valor bolsa/libro:')
print(b.check_valor_bolsa_libro())
print('')

print('ratio precio / utilidad (PER):')
print(b.get_per())
print('')

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

# TODO:
# -----
#
# FCF/Patrimonio
# DPS/EPS (dividend per share / earning per share) 
# (AC-Caja) / Ventas
# --------------------------------------------------------------------------------------------------------------------
# d) Futurologia? (necesitamos variables cuantitativas o chatgpt)


