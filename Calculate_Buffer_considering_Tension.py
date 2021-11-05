import arcpy

arcpy.env.workspace = r'C:\Users\athil\Desktop\asdsa'
tracados = r'C:\Users\athil\Desktop\asdsa\Alternativas_Leilao0022021.shp'

## -- printa a distância da faixa de servidão no campo "distancia", de acordo com
## -- a tensao da linha

expression = "getClass(!tensao!)"

codeblock = """
def getClass(tensao):
    if tensao >= 69 and tensao <= 138:
        return 20
    if tensao >= 138 and tensao <= 230:
        return 30
    if tensao >= 230 and tensao <= 500:
        return 40
    if tensao > 500:
        return 60"""

arcpy.CalculateField_management(tracados, 'distancia', expression, "PYTHON_9.3", codeblock)

## -- criar aqui uma condição para ler a FC dos tracados, e se nao enconrar
## -- nos atributos o campo tensao, realizar o buffer de 30 metros pra cada lado
## -- em todos os tracados. Do contrario, se encontrar o campo tensao, realizar
## -- o buffer de acordo com o campo "distancia"



# -- gera o buffer utilizando o campo distancia, caso enconrado o campo distancia

tracados_buffer = "faixas_servidao.shp"
distanceField = "distancia"
sideType = "FULL"
endType = "ROUND"
dissolveType = "NONE"
dissolveField = "distancia"
arcpy.Buffer_analysis(tracados, tracados_buffer, distanceField, sideType, endType, 
                      dissolveType, dissolveField)


