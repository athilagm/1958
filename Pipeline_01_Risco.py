import arcpy
import locale
from arcpy.sa import *

arcpy.env.workspace = r'C:\Users\athil\Desktop\dados_leilao_2021' #caminho workspace
raster_risco = r'C:\Users\athil\Desktop\Envio_Fab\rasters\Matriz_Risco_Integrado_Brasil.tif' # caminho do raster risco integrado
raster_engenharia = r'C:\Users\athil\Desktop\Envio_Fab\rasters\Engenharia_Risco.tif' #caminho do raster risco engenharia
raster_meioambiente = r'C:\Users\athil\Desktop\Envio_Fab\rasters\MeioAmbiente_Risco.tif' #caminho do raster risco meio ambiente
raster_fundiario = r'C:\Users\athil\Desktop\Envio_Fab\rasters\Fundiario_Risco.tif' #caminho do raster risco fundiario 
raster_om = r'C:\Users\athil\Desktop\Envio_Fab\rasters\O&M_Risco.tif' #caminho do raster risco O&m

#DEFINE ONDE EST� O TRA�ADO INICIAL 

tracado_ANEEL = r'C:\Users\athil\Desktop\dados_leilao_2021\tracados.shp' # AQUI � O CAMINHO ONDE VAI ESTAR ARMAZENADO O TRA�ADO

# realizar split das fei��es de tra�ado no mesmo shapefile




##EXCUTA BUFFER DA FAIXA DE SERVID�O (~30 METERS)

#buffer Faixa de Servid�o 
Buffer_Linha_FS = "buffer_60m.shp" #OUTPUT DO BUFFER DA FAIXA DE SERVID�O
distanceField_FS = "30 Meters" #LARGURA DA FAIXA � PARTIR DO CENTRO DO TRA�ADO
sideType_FS = "FULL" 
endType_FS = "ROUND"
#parametro dissoveleType setado para "NONE", assim cria um buffer para cada linha da tabela de atributos dos tracados.
dissolveType_FS = "NONE"
dissolveField_FS = ""
arcpy.Buffer_analysis(tracado_ANEEL, Buffer_Linha_FS, distanceField_FS, sideType_FS, endType_FS, 
                      dissolveType_FS, dissolveField_FS)




## -- executar buffer de acordo com a tens�o (kv)






##EXECUTA BUFFER DO CORREDOR (15KM)

Buffer_Linha_COR = "buffer_15km.shp" #OUTPUT DO BUFFER DO CORREDOR
distanceField_COR = "15 Kilometers" #LARGURA DO CORREDOR ANEEL 15 KM
sideType_COR = "FULL" 
endType_COR = "ROUND"
dissolveType_COR = "NONE"
dissolveField_COR = ""
arcpy.Buffer_analysis(tracado_ANEEL, Buffer_Linha_COR, distanceField_COR, sideType_COR, endType_COR, 
                      dissolveType_COR, dissolveField_COR)

## RECORTA As MATRIZ DE RISCO INTEGRADO PARA O CORREDOR UTILIZANDO A FERRAMENTA EXTRACT BY MASK 

#RISCO INTEGRADO

arcpy.CheckOutExtension("Spatial")
outExtractByMask = ExtractByMask(raster_risco, Buffer_Linha_COR)
outExtractByMask.save("Corredor_Risco_INTEGRADO.tif")

## RISCO ENGENHARIA

arcpy.CheckOutExtension("Spatial")
outExtractByMask = ExtractByMask(raster_engenharia, Buffer_Linha_COR)
outExtractByMask.save("Corredor_Risco_ENG.tif")

## RISCO AMBIENTAL

arcpy.CheckOutExtension("Spatial")
outExtractByMask = ExtractByMask(raster_meioambiente, Buffer_Linha_COR)
outExtractByMask.save("Corredor_Risco_AMB.tif")

## RISCO FUNDI�RIO

arcpy.CheckOutExtension("Spatial")
outExtractByMask = ExtractByMask(raster_fundiario, Buffer_Linha_COR)
outExtractByMask.save("Corredor_Risco_FUND.tif")

## RISCO O&M

arcpy.CheckOutExtension("Spatial")
outExtractByMask = ExtractByMask(raster_om, Buffer_Linha_COR)
outExtractByMask.save("Corredor_Risco_OM.tif")


#-------------------------------------------------------------- INICIALIZA AN�LISE PARA RISCO BRASIL -----------------------------------------------------------#
# � PARTIR DAQUI INICIALIZA A AN�LISE UTILIZANDO A FERRAMENTA ZONAL STATISTICS

# Set the local variables
inZoneData = Buffer_Linha_FS
zoneField = "Name"
inValueRaster = raster_risco
outZonalStatistics = ZonalStatistics(inZoneData, zoneField, inValueRaster,
                                     "MEAN", "NODATA") 

# � PARTIR DAQUI INICIALIZA A AN�LISE UTILIZANDO A FERRAMENTA GET RASTER PROPERTIES
riscoMEANResult = arcpy.GetRasterProperties_management(outZonalStatistics)
output_risco = riscoMEANResult.getOutput(0).split(',')

# AQUI PREPARA PARA PRINAR O GRAU DE RISCO DE ACORDO COM O N�MERO IDENTIFICADO PELA "GET RASTER PROPERTIES"
risco_1 = float("{}.{}".format(output_risco[0], output_risco[1][0:2]))
print(risco_1)
def print_risco_1(r):
  if r >= 0 and r <= 0.10:
      return 'MUITO BAIXO'
  if r >= 0.10 and r <= 0.25:
      return 'BAIXO'
  if r >= 0.25 and r <= 0.50:
      return 'M�DIO'
  if r >= 0.50 and r <= 0.75:
      return 'ALTO'
  if r > 0.75:
      return 'MUITO ALTO'
    
print("O risco de implanta��o da faixa de servid�o da linha Bigua�u-Sider�pois neste tra�ado � {}".format(print_risco_1(risco_1)))

#-------------------------------------------------------------- INICIALIZA AN�LISE PARA RISCO ENGENHARIA -----------------------------------------------------------#

# � PARTIR DAQUI INICIALIZA A AN�LISE UTILIZANDO A FERRAMENTA ZONAL STATISTICS

# Set the local variables
inZoneData = Buffer_Linha_FS
zoneField = "Name"
inValueRaster = raster_engenharia
outZonalStatistics_eng = ZonalStatistics(inZoneData, zoneField, inValueRaster,
                                     "MEAN", "NODATA") 
# � PARTIR DAQUI INICIALIZA A AN�LISE UTILIZANDO A FERRAMENTA GET RASTER PROPERTIES
riscoMEANengenharia = arcpy.GetRasterProperties_management(outZonalStatistics_eng)
output_eng = riscoMEANengenharia.getOutput(0).split(',')

# AQUI PREPARA PARA PRINAR O GRAU DE RISCO DE ACORDO COM O N�MERO IDENTIFICADO PELA "GET RASTER PROPERTIES"
risco_2 = float("{}.{}".format(output_eng[0], output_eng[1][0:2]))
print(risco_2)
def print_risco_2(r):
  if r >= 0 and r <= 0.10:
      return 'MUITO BAIXO'
  if r >= 0.10 and r <= 0.25:
      return 'BAIXO'
  if r >= 0.25 and r <= 0.50:
      return 'M�DIO'
  if r >= 0.50 and r <= 0.75:
      return 'ALTO'
  if r > 0.75:
      return 'MUITO ALTO'
    
print("O risco de ENGENHARIA para a implanta��o da faixa de servid�o da linha Bigua�u-Sider�pois neste tra�ado � {}".format(print_risco_2(risco_2)))

#-------------------------------------------------------------- INICIALIZA AN�LISE PARA RISCO MEIO AMBIENTE ---------------------------------------------------------#
# � PARTIR DAQUI INICIALIZA A AN�LISE UTILIZANDO A FERRAMENTA ZONAL STATISTICS

# Set the local variables
inZoneData = Buffer_Linha_FS
zoneField = "Name"
inValueRaster = raster_meioambiente
outZonalStatistics_mab = ZonalStatistics(inZoneData, zoneField, inValueRaster,
                                     "MEAN", "NODATA") 
# � PARTIR DAQUI INICIALIZA A AN�LISE UTILIZANDO A FERRAMENTA GET RASTER PROPERTIES
riscoMEANmeioambiente = arcpy.GetRasterProperties_management(outZonalStatistics_mab)
output_mab = riscoMEANmeioambiente.getOutput(0).split(',')

# AQUI PREPARA PARA PRINAR O GRAU DE RISCO DE ACORDO COM O N�MERO IDENTIFICADO PELA "GET RASTER PROPERTIES"
risco_3 = float("{}.{}".format(output_mab[0], output_mab[1][0:2]))
print(risco_3)
def print_risco_3(r):
  if r >= 0 and r <= 0.10:
      return 'MUITO BAIXO'
  if r >= 0.10 and r <= 0.25:
      return 'BAIXO'
  if r >= 0.25 and r <= 0.50:
      return 'M�DIO'
  if r >= 0.50 and r <= 0.75:
      return 'ALTO'
  if r > 0.75:
      return 'MUITO ALTO'
    
print("O risco de MEIO AMBIENTE para a implanta��o da faixa de servid�o da linha Bigua�u-Sider�pois neste tra�ado � {}".format(print_risco_3(risco_3)))

#-------------------------------------------------------------- INICIALIZA AN�LISE PARA RISCO FUNDI�RIO ---------------------------------------------------------#
# � PARTIR DAQUI INICIALIZA A AN�LISE UTILIZANDO A FERRAMENTA ZONAL STATISTICS

# Set the local variables
inZoneData = Buffer_Linha_FS
zoneField = "Name"
inValueRaster = raster_fundiario
outZonalStatistics_fund = ZonalStatistics(inZoneData, zoneField, inValueRaster,
                                     "MEAN", "NODATA")

# � PARTIR DAQUI INICIALIZA A AN�LISE UTILIZANDO A FERRAMENTA GET RASTER PROPERTIES
riscoMEANfundiario = arcpy.GetRasterProperties_management(outZonalStatistics_fund)
output_fund = riscoMEANfundiario.getOutput(0).split(',')

# AQUI PREPARA PARA PRINAR O GRAU DE RISCO DE ACORDO COM O N�MERO IDENTIFICADO PELA "GET RASTER PROPERTIES"
risco_4 = float("{}.{}".format(output_fund[0], output_fund[1][0:2]))
print(risco_4)
def print_risco_4(r):
  if r >= 0 and r <= 0.10:
      return 'MUITO BAIXO'
  if r >= 0.10 and r <= 0.25:
      return 'BAIXO'
  if r >= 0.25 and r <= 0.50:
      return 'M�DIO'
  if r >= 0.50 and r <= 0.75:
      return 'ALTO'
  if r > 0.75:
      return 'MUITO ALTO'
    
print("O risco de FUNDI�RIO para a implanta��o da faixa de servid�o da linha Bigua�u-Sider�pois neste tra�ado � {}".format(print_risco_4(risco_4)))

#-------------------------------------------------------------- INICIALIZA AN�LISE PARA RISCO O&M ----------------------------------------------------------------#
# � PARTIR DAQUI INICIALIZA A AN�LISE UTILIZANDO A FERRAMENTA ZONAL STATISTICS

# Set the local variables
inZoneData = Buffer_Linha_FS
zoneField = "Name"
inValueRaster = raster_om
outZonalStatistics_om = ZonalStatistics(inZoneData, zoneField, inValueRaster,
                                     "MEAN", "NODATA") 

# � PARTIR DAQUI INICIALIZA A AN�LISE UTILIZANDO A FERRAMENTA GET RASTER PROPERTIES
riscoMEANom = arcpy.GetRasterProperties_management(outZonalStatistics_om)
output_om = riscoMEANom.getOutput(0).split(',')

# AQUI PREPARA PARA PRINAR O GRAU DE RISCO DE ACORDO COM O N�MERO IDENTIFICADO PELA "GET RASTER PROPERTIES"
risco_5 = float("{}.{}".format(output_om[0], output_om[1][0:2]))
print(risco_5)
def print_risco_5(r):
  if r >= 0 and r <= 0.10:
      return 'MUITO BAIXO'
  if r >= 0.10 and r <= 0.25:
      return 'BAIXO'
  if r >= 0.25 and r <= 0.50:
      return 'M�DIO'
  if r >= 0.50 and r <= 0.75:
      return 'ALTO'
  if r > 0.75:
      return 'MUITO ALTO'
    
print("O risco de OPERA��O E MANUTEN��O (O&M) para a implanta��o da faixa de servid�o da linha Bigua�u-Sider�pois neste tra�ado � {}".format(print_risco_5(risco_5)))




#printar valores numa tabela 
