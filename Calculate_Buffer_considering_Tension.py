import arcpy

arcpy.env.workspace = r'C:\Users\athil\Desktop\asdsa'
indata = r'C:\Users\athil\Desktop\asdsa\Alternativas_Leilao0022021.shp'

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

arcpy.CalculateField_management(indata, 'distancia', expression, "PYTHON_9.3", codeblock)


