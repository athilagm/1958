import arcpy
import locale
from arcpy.sa import *

arcpy.env.workspace = r'C:\Users\athil\Desktop\dados_leilao_2021' ## ESSE CAMINHO EU UTILIZO PRA CRIAR UM DEFAULT WORKSPACE NA MINHA MÁQUINA, TUDO O QUE GERO À PARTIR DAQUI CAI ALI DENTRO
raster_risco = r'C:\Users\athil\Desktop\dados_leilao_2021\risco_br.tif' ##ALTERAR ESSE CAMINHO PARA O CAMINHO DO RASTER RISCO
raster_engenharia = r'C:\Users\athil\Desktop\dados_leilao_2021\risco_eng.tif' ##ALTERAR ESSE CAMINHO PARA O CAMINHO DO RASTER RISCO ENGENHARIA
raster_meioambiente = r'C:\Users\athil\Desktop\dados_leilao_2021\risco_mab.tif' ##ALTERAR ESSE CAMINHO PARA O CAMINHO DO RASTER RISCO ENGENHARIA
raster_fundiario = r'C:\Users\athil\Desktop\dados_leilao_2021\risco_fund.tif' ##ALTERAR ESSE CAMINHO PARA O CAMINHO DO RASTER RISCO FUNDIÁRIO
raster_om = r'C:\Users\athil\Desktop\dados_leilao_2021\risco_om.tif' ##ALTERAR ESSE CAMINHO PARA O CAMINHO DO RASTER RISCO O&M

#DEFINE ONDE ESTÁ O TRAÇADO INICIAL 

tracado_ANEEL = r'C:\Users\athil\Desktop\dados_leilao_2021\tracados.shp' # AQUI É O CAMINHO ONDE VAI ESTAR ARMAZENADO O TRAÇADO

##EXCUTA BUFFER DA FAIXA DE SERVIDÃO (~30 METERS)

#buffer Faixa de Servidão 
Buffer_Linha_FS = "buffer_60m.shp" #OUTPUT DO BUFFER DA FAIXA DE SERVIDÃO
distanceField_FS = "30 Meters" #LARGURA DA FAIXA À PARTIR DO CENTRO DO TRAÇADO
sideType_FS = "FULL" 
endType_FS = "ROUND"
#parametro dissoveleType setado para "NONE", assim cria um buffer para cada linha da tabela de atributos dos tracados.
dissolveType_FS = "NONE"
dissolveField_FS = ""
arcpy.Buffer_analysis(tracado_ANEEL, Buffer_Linha_FS, distanceField_FS, sideType_FS, endType_FS, 
                      dissolveType_FS, dissolveField_FS)

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

## RISCO FUNDIÁRIO

arcpy.CheckOutExtension("Spatial")
outExtractByMask = ExtractByMask(raster_fundiario, Buffer_Linha_COR)
outExtractByMask.save("Corredor_Risco_FUND.tif")

## RISCO O&M

arcpy.CheckOutExtension("Spatial")
outExtractByMask = ExtractByMask(raster_om, Buffer_Linha_COR)
outExtractByMask.save("Corredor_Risco_OM.tif")


#-------------------------------------------------------------- INICIALIZA ANÁLISE PARA RISCO BRASIL -----------------------------------------------------------#
# À PARTIR DAQUI INICIALIZA A ANÁLISE UTILIZANDO A FERRAMENTA ZONAL STATISTICS

# Set the local variables
inZoneData = Buffer_Linha_FS
zoneField = "Name"
inValueRaster = raster_risco
outZonalStatistics = ZonalStatistics(inZoneData, zoneField, inValueRaster,
                                     "MEAN", "NODATA") 

# À PARTIR DAQUI INICIALIZA A ANÁLISE UTILIZANDO A FERRAMENTA GET RASTER PROPERTIES
riscoMEANResult = arcpy.GetRasterProperties_management(outZonalStatistics)
output_risco = riscoMEANResult.getOutput(0).split(',')

# AQUI PREPARA PARA PRINAR O GRAU DE RISCO DE ACORDO COM O NÚMERO IDENTIFICADO PELA "GET RASTER PROPERTIES"
risco_1 = float("{}.{}".format(output_risco[0], output_risco[1][0:2]))
print(risco_1)
def print_risco_1(r):
  if r >= 1 and r <= 2:
      return 'MUITO BAIXO'
  if r >= 2 and r <= 3:
      return 'BAIXO'
  if r >= 3 and r <= 4:
      return 'MÉDIO'
  if r >= 4 and r <= 5:
      return 'ALTO'
  if r > 5:
      return 'MUITO ALTO'
    
print("O risco de implantação da faixa de servidão da linha Biguaçu-Siderópois neste traçado é {}".format(print_risco_1(risco_1)))

#-------------------------------------------------------------- INICIALIZA ANÁLISE PARA RISCO ENGENHARIA -----------------------------------------------------------#

# À PARTIR DAQUI INICIALIZA A ANÁLISE UTILIZANDO A FERRAMENTA ZONAL STATISTICS

# Set the local variables
inZoneData = Buffer_Linha_FS
zoneField = "Name"
inValueRaster = raster_engenharia
outZonalStatistics_eng = ZonalStatistics(inZoneData, zoneField, inValueRaster,
                                     "MEAN", "NODATA") 
# À PARTIR DAQUI INICIALIZA A ANÁLISE UTILIZANDO A FERRAMENTA GET RASTER PROPERTIES
riscoMEANengenharia = arcpy.GetRasterProperties_management(outZonalStatistics_eng)
output_eng = riscoMEANengenharia.getOutput(0).split(',')

# AQUI PREPARA PARA PRINAR O GRAU DE RISCO DE ACORDO COM O NÚMERO IDENTIFICADO PELA "GET RASTER PROPERTIES"
risco_2 = float("{}.{}".format(output_eng[0], output_eng[1][0:2]))
print(risco_2)
def print_risco_2(r):
  if r >= 1 and r <= 2:
      return 'MUITO BAIXO'
  if r >= 2 and r <= 3:
      return 'BAIXO'
  if r >= 3 and r <= 4:
      return 'MÉDIO'
  if r >= 4 and r <= 5:
      return 'ALTO'
  if r > 5:
      return 'MUITO ALTO'
    
print("O risco de ENGENHARIA para a implantação da faixa de servidão da linha Biguaçu-Siderópois neste traçado é {}".format(print_risco_2(risco_2)))

#-------------------------------------------------------------- INICIALIZA ANÁLISE PARA RISCO MEIO AMBIENTE ---------------------------------------------------------#
# À PARTIR DAQUI INICIALIZA A ANÁLISE UTILIZANDO A FERRAMENTA ZONAL STATISTICS

# Set the local variables
inZoneData = Buffer_Linha_FS
zoneField = "Name"
inValueRaster = raster_meioambiente
outZonalStatistics_mab = ZonalStatistics(inZoneData, zoneField, inValueRaster,
                                     "MEAN", "NODATA") 
# À PARTIR DAQUI INICIALIZA A ANÁLISE UTILIZANDO A FERRAMENTA GET RASTER PROPERTIES
riscoMEANmeioambiente = arcpy.GetRasterProperties_management(outZonalStatistics_mab)
output_mab = riscoMEANmeioambiente.getOutput(0).split(',')

# AQUI PREPARA PARA PRINAR O GRAU DE RISCO DE ACORDO COM O NÚMERO IDENTIFICADO PELA "GET RASTER PROPERTIES"
risco_3 = float("{}.{}".format(output_mab[0], output_mab[1][0:2]))
print(risco_3)
def print_risco_3(r):
  if r >= 1 and r <= 2:
      return 'MUITO BAIXO'
  if r >= 2 and r <= 3:
      return 'BAIXO'
  if r >= 3 and r <= 4:
      return 'MÉDIO'
  if r >= 4 and r <= 5:
      return 'ALTO'
  if r > 5:
      return 'MUITO ALTO'
    
print("O risco de MEIO AMBIENTE para a implantação da faixa de servidão da linha Biguaçu-Siderópois neste traçado é {}".format(print_risco_3(risco_3)))

#-------------------------------------------------------------- INICIALIZA ANÁLISE PARA RISCO FUNDIÁRIO ---------------------------------------------------------#
# À PARTIR DAQUI INICIALIZA A ANÁLISE UTILIZANDO A FERRAMENTA ZONAL STATISTICS

# Set the local variables
inZoneData = Buffer_Linha_FS
zoneField = "Name"
inValueRaster = raster_fundiario
outZonalStatistics_fund = ZonalStatistics(inZoneData, zoneField, inValueRaster,
                                     "MEAN", "NODATA")

# À PARTIR DAQUI INICIALIZA A ANÁLISE UTILIZANDO A FERRAMENTA GET RASTER PROPERTIES
riscoMEANfundiario = arcpy.GetRasterProperties_management(outZonalStatistics_fund)
output_fund = riscoMEANfundiario.getOutput(0).split(',')

# AQUI PREPARA PARA PRINAR O GRAU DE RISCO DE ACORDO COM O NÚMERO IDENTIFICADO PELA "GET RASTER PROPERTIES"
risco_4 = float("{}.{}".format(output_fund[0], output_fund[1][0:2]))
print(risco_4)
def print_risco_4(r):
  if r >= 1 and r <= 2:
      return 'MUITO BAIXO'
  if r >= 2 and r <= 3:
      return 'BAIXO'
  if r >= 3 and r <= 4:
      return 'MÉDIO'
  if r >= 4 and r <= 5:
      return 'ALTO'
  if r > 5:
      return 'MUITO ALTO'
    
print("O risco de FUNDIÁRIO para a implantação da faixa de servidão da linha Biguaçu-Siderópois neste traçado é {}".format(print_risco_4(risco_4)))

#-------------------------------------------------------------- INICIALIZA ANÁLISE PARA RISCO O&M ----------------------------------------------------------------#
# À PARTIR DAQUI INICIALIZA A ANÁLISE UTILIZANDO A FERRAMENTA ZONAL STATISTICS

# Set the local variables
inZoneData = Buffer_Linha_FS
zoneField = "Name"
inValueRaster = raster_om
outZonalStatistics_om = ZonalStatistics(inZoneData, zoneField, inValueRaster,
                                     "MEAN", "NODATA") 

# À PARTIR DAQUI INICIALIZA A ANÁLISE UTILIZANDO A FERRAMENTA GET RASTER PROPERTIES
riscoMEANom = arcpy.GetRasterProperties_management(outZonalStatistics_om)
output_om = riscoMEANom.getOutput(0).split(',')

# AQUI PREPARA PARA PRINAR O GRAU DE RISCO DE ACORDO COM O NÚMERO IDENTIFICADO PELA "GET RASTER PROPERTIES"
risco_5 = float("{}.{}".format(output_om[0], output_om[1][0:2]))
print(risco_5)
def print_risco_5(r):
  if r >= 1 and r <= 2:
      return 'MUITO BAIXO'
  if r >= 2 and r <= 3:
      return 'BAIXO'
  if r >= 3 and r <= 4:
      return 'MÉDIO'
  if r >= 4 and r <= 5:
      return 'ALTO'
  if r > 5:
      return 'MUITO ALTO'
    
print("O risco de OPERAÇÃO E MANUTENÇÃO (O&M) para a implantação da faixa de servidão da linha Biguaçu-Siderópois neste traçado é {}".format(print_risco_5(risco_5)))
