import pickle
from datetime import datetime
from datetime import date
import re
import time
import getpass
import os
import sys
import re
from cryptography.fernet import Fernet
from os.path import isfile

#requirements
import json
import pandas as pd
import helium as h
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pathlib
from selenium.webdriver.firefox.options import Options

pd.options.display.max_rows = 100
pd.options.display.max_colwidth = 1000


def get_info(df,cod_gr):

    # nombre_lider missing
    try:
        nombre_lider = df['Nombre Líder'].dropna().iloc[0]
    except IndexError:
        nombre_lider = 'Sin dato Registrado'
    
    info= {
        'Nombre_Grupo' : df['Nombre Grupo'].dropna().iloc[0],

        'Nombre_Lider' : nombre_lider,

        'CCRG Grupo'  : cod_gr
    }
    
    dfi = pd.DataFrame(info, index=[0])
  
    return dfi

# Extra headers by products. It sets the extra-headers for tables in the excel sheets.
DBEH = {
    'INFO_GROUP': 'TABLE',
    'MEMBERS':['Identificación', 'Nacionalidad', 'Tiene afiliación con UdeA', 'Si no tiene afiliación UdeA diligencie el nombre de la Institución','Nro. Horas de dedicación semanales que avala el Coordinador de grupo'],
    'NC_P': {'ART_IMP_P': {'ART_P_TABLE':['URL','DOI','Si no tiene URL o DOI agregue una evidencia en el repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
             'ART_ELE_P': {'ART_E_P_TABLE':['URL','DOI','Si no tiene URL o DOI agregue una evidencia en el repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
             'LIB_P':     {'LIB_P_TABLE':['Proyecto de investigación del cual se derivó el libro (Código-Título)','Financiador(es) del proyecto del cual se derivó el libro', 'Financiador(es) de la publicación','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
             'CAP_LIB_P': {'CAP_LIB_P_TABLE':['Proyecto de investigación del cual se derivó el libro que contiene el capítulo (Código-Título)','Financiador del proyecto del cual se derivó el libro que contiene el capítulo','Financiador de la publicación','Autores','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
             'NOT_CIE_P': {'NOT_CIE_P_TABLE':['URL','DOI','Si no tiene URL o DOI genere una evidencia en el repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
             'PAT_P':     {'PAT_P_TABLE':['Autores', 'Examen de fondo favorable','Examen preliminar internacional favorable','Adjunta opiniones escritas de la bUsqueda internacional','Contrato de explotación','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']}, #  1 2 3 -1
             'PRD_INV_ART_P': {'PAAD_P_TABLE':['Autores','Tiene certificado institucional de la obra','Tiene certificado de la entidad que convoca al evento en el que participa','Tiene certificado de la entidad que convoca al premio en el que obtiene','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']}, # 1 2 3 -1
             'VAR_VEG_P':     {'VV_P_TABLE':['Autores','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
             'VAR_ANI_P':     {'VA_P_TABLE':['Autores','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
             'RAZ_PEC_P':     {'RAZ_PEC_P_TABLE':['Autores','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
             'TRA_FIL_P': {'TRA_FIL_P_TABLE':['Proyecto de investigación del cual se derivó el libro (Código-Título)','Financiador(es) del proyecto del cual se derivó el libro','Financiador(es) de la publicación','Autores','Citas recibidas (si tiene)','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']}
            },
     'DTI_P': {'DIS_IND_P': {'DI_P_TABLE':['Autores','Contrato (si aplica)','Nombre comercial (si aplica)','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'CIR_INT_P': {'ECI_P_TABLE':['Autores','Contrato (si aplica)','Nombre comercial (si aplica)','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'SOFT_P': {'SF_P_TABLE':['Autores','Contrato (si aplica)','Nombre comercial (si aplica)','TRL','Agregue la evidencia verificada al repositorio digital y copie el link del archivo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'NUTRA_P': {'NUTRA_P_TABLE':['Autores','Agregue la evidencia verificada al repositorio digital y copie el link del archivo en este campo','¿El producto cumple con los requisitos para ser avalado?']}, # add
              'COL_CIENT_P': {'COL_CIENT_P_TABLE':['Autores','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo', '¿El producto cumple con los requisitos para ser avalado?']},
              'REG_CIENT_P': {'REG_CIENT_P_TABLE':['Autores','Contrato licenciamiento (si aplica)','Agregue las evidencias verificadas al repositorio digital y copie el link del archivo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'PLT_PIL_P': {'PP_P_TABLE':['Autores','Agregue la evidencia verificada al repositorio digital y copie el link del archivo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'PRT_IND_P': {'PI_P_TABLE':['Autores','Nombre comercial (si aplica)','TRL','Agregue la evidencia verificada al repositorio digital y copie el link del archivo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'SEC_IND_P': {'SE_P_TABLE':['Autores','Agregue la evidencia verificada al repositorio digital y copie el link del archivo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'PROT_VIG_EPID_P': {'PROT_VIG_EPID_P_TABLE':['Autores','Agregue la evidencia verificada al repositorio digital y copie el link del archivo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'EMP_BSE_TEC_P': {'EBT_P_TABLE':['Autores','Agregue la evidencia verificada al repositorio digital y copie el link del archivo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'EMP_CRE_CUL_P': {'ICC_P_TABLE':['Autores','Agregue la evidencia verificada al repositorio digital y copie el link del archivo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'INN_GES_EMP_P': {'IG_P_TABLE':['Autores','Contrato (si aplica)','Nombre comercial (si aplica)','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'INN_PROC_P': {'IPP_P_TABLE':['Autores','Contrato (si aplica)','Nombre comercial (si aplica)','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'REG_NORM_REGL_LEG_P': {'RNR_P_TABLE':['Autores','Contrato (si aplica)','Convenio (si aplica)','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'CONP_TEC_P': {'CONP_TEC_P_TABLE':['Autores','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'REG_AAD_P': {'AAAD_P_TABLE':['Autores','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'SIG_DIS_P': {'SD_P_TABLE':['Autores','Contrato licenciamiento (si aplica)','Agregue las evidencias verificadas al repositorio digital y copie el link del archivo en este campo','¿El producto cumple con los requisitos para ser avalado?']}
            },
    'ASC_P': {'GEN_CONT_IMP_P': {'GC_I_P_TABLE_5':['Autores','Citas recibidas (si tiene)','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'PASC_P': {'PASC_FOR_P_TABLE':['Proyecto/Código','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?'],
               'PASC_TRA_P_TABLE':['Proyecto/Código','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?'],
               'PASC_GEN_P_TABLE':['Proyecto/Código','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?'],
               'PASC_CAD_P_TABLE':['Proyecto/Código','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
               'DC_P': {'DC_CD_P_TABLE':['Proyecto/Código','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?'],
               'DC_CON_P_TABLE':['Medio de verificación','Proyecto/Código','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?'],
               'DC_TRA_P_TABLE':['Medio de verificación','Proyecto/Código','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?'],
               'DC_DES_P_TABLE':['Medio de verificación','Proyecto/Código','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']}
            },
    'FRH_P': {'TES_DOC_P': {'TD_P_TABLE':['Número de cédula del graduado','¿La fecha fin coincide con la fecha de grado del estudiante?','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},  # 1 -1
              'TES_MAST_P': {'TM_P_TABLE':['Número de cédula del graduado','¿La fecha fin coincide con la fecha de grado del estudiante?','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']}, # 1 -1
              'TES_PREG_P': {'TP_P_TABLE':['Número de cédula del graduado','¿La fecha fin coincide con la fecha de grado del estudiante?','Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']}, # 1 -1
              'ASE_PRG_ACA_P': {'APGA_P_TABLE':['Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'ASE_CRE_CUR_P': {'ACC_P_TABLE':['Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'ASE_PRG_ONDAS_P': {'APO_P_TABLE':['Agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'PROY_INV_DES_P':{'PID_P_TABLE':['Código SIIU o código en el Centro','Si el proyecto no está en SIIU, agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'PROY_INV_CRE_P':{'INV_CRE_P_TABLE':['Código SIIU o código en el Centro','Si el proyecto no está en SIIU, agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'PROY_INV_DES_INN_P':{'PF_P_TABLE':['Código SIIU o código en el Centro','Si el proyecto no está en SIIU, agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']},
              'PROY_INV_RESP_SOC_P':{'PE_P_TABLE':['Código SIIU o código en el Centro','Si el proyecto no está en SIIU, agregue las evidencias verificadas al repositorio digital y genere un hipervínculo en este campo','¿El producto cumple con los requisitos para ser avalado?']}
              }
}

# The below variable helps  to iterate over columns in a given shet. 
d = {
                '1': 'C',
                '2': 'D',
                '3': 'E',
                '4': 'F',
                '5': 'G',
                '6': 'H',
                '7': 'I',
                '8': 'J',
                '9': 'K',
                '10': 'L',
                '11': 'M',
                '12': 'N',
                '13': 'O',
                '14': 'P',
                '15': 'Q',
                '16': 'R',
                '17': 'S',
                '18': 'T',
                '19': 'U',
                '20': 'V'
}
# Remove not necesary colmns(unnamed) from a data frame.  
def clean_df(df):
    c=[x for x in df.columns if x.find('Unnamed:') == -1 and  x.find('Revisar') == -1 and x.find('Avalar integrante') == -1]
    dfc=df[c]
    return dfc

def clean_tables(df):
    #droplevel
    try:
        df = df.droplevel(0,axis=1)
    except ValueError:
        pass
    #ignore firts(NaN) and last(string:resultados) rows
    df=df[1:-1]
    #remove unnamed columns and revisar
    cols = [x for x in df.columns if x.find('Unnamed:') == -1 and  x.find('Revisar') == -1 and x.find('Avalar integrante') == -1]
    return df[cols]

def rename_col(df,colr,colf):
    df.rename(columns = {colr: colf,}, inplace = True)
    return df

# Sheets 2 - 12.
def format_df(df, sheet_name, start_row, writer,eh, veh = None):
    'format headers'
    
    df.to_excel(writer, sheet_name, startrow = start_row+1, startcol = 2, index = False)

    # Get the xlsxwriter workbook and worksheet objects.
    worksheet = writer.sheets[sheet_name]
    
    # Set style for a merged cells     
    merge_format = workbook.add_format({
    'bold': 1,
    'border':1,
    'text_wrap': True,    
    'align': 'center',
    'valign': 'vcenter',
    'font_color': 'blue'})
    
    # define the interval for merged cells
    if not df.empty:
        start,end = 1,df.shape[1]
    else:
        start,end = 1,1
    
     # Range merged headers cells 1
    m_range = d.get(str(start)) + str(start_row + 1) + ':' + d.get(str(end)) + str(start_row +1)
    worksheet.merge_range(m_range, 'Información suministrada por la Vicerrectoría de Investigación', merge_format)
    
    # Range merged headers cells 2
    _m_range = d.get(str(end+1)) + str(start_row +1) + ':' +  d.get(str(end+len(eh))) + str(start_row +1)
    worksheet.merge_range(_m_range, 'Validación del Centro, Instituto o Corporación', merge_format)
        
    worksheet.set_row_pixels(start_row+1, 120)
    #worksheet.set_column('C:C',30,general)
    
    # Set column format by sheet
    if sheet_name=='2.Integrantes grupo':
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 2)
        worksheet.set_column('D:K',15,general)
    
    if sheet_name=='3.ART y N':
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 2)
        worksheet.set_column('C:C',20,general)
        worksheet.set_column('M:O',20, general)
     
    if sheet_name=='4.LIB y LIB_FOR':
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 2)
        worksheet.set_column('C:C',20,general)
        worksheet.set_column('I:P',20,general)

    if sheet_name=='5.CAP':
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 2)
        worksheet.set_column('C:C',20,general)
        worksheet.set_column('D:H',10,general)
        worksheet.set_column('I:K',18,general)
        worksheet.set_column('J:P',20,general)

    if sheet_name=='6.Patente_Variedades':
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 2)
        worksheet.set_column('C:C',20,general)
        worksheet.set_column('D:I',10,general)
        worksheet.set_column('J:K',20,general)
        worksheet.set_column('L:S',20,general)

    if sheet_name=='7.AAD':
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 2)
        worksheet.set_column('C:C',20,general)
        worksheet.set_column('F:K',10,general)
        worksheet.set_column('L:P',25,general)

    if sheet_name=='8.Tecnológico':
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 2)
        worksheet.set_column('C:C',20,general)
        worksheet.set_column('D:I',10,general)
        worksheet.set_column('J:S',18,general)

    if sheet_name=='9.Empresarial':
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 2)
        worksheet.set_column('C:C',20,general)
        worksheet.set_column('D:H',10,general)
        worksheet.set_column('I:N',20,general)

    if sheet_name=='10.ASC y Divulgación':
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 2)
        worksheet.set_column('C:C',28,general)
        worksheet.set_column('I:I',15,general)
        worksheet.set_column('J:N',20,general)

    if sheet_name=='11.Formación y programas':
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 2)
        worksheet.set_column('C:C',25,general)
        worksheet.set_column('D:G',10,general)
        worksheet.set_column('L:O',15,general)
        worksheet.set_column('N:N',20,general)
    
    if sheet_name=='12.Proyectos':
        worksheet.set_column('A:A', 5)
        worksheet.set_column('B:B', 2)
        worksheet.set_column('C:K',25,general)
        
    worksheet.write(start_row+1, 0, 'VoBo de VRI', merge_format)
    # Add a header format.
    
    fmt_header = workbook.add_format({
        'bold': True,
        'align': 'center',    
        'text_wrap': True,
        'valign': 'vcenter',
        'fg_color': '#33A584',
        'font_color': '#FFFFFF',
        'border': 1})
    
    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(start_row+1, col_num + 2, value, fmt_header)
        
    # write extra headers
    for col_num, value in enumerate(eh):
        worksheet.write(start_row+1, col_num + df.shape[1] + 2, value, fmt_header)

    # Write validation values    
    v_range = 'A' + str(start_row +3) + ':' + 'A' + str(df.shape[0] + start_row +2)
    worksheet.data_validation(v_range,{'validate': 'list',
                                  'source': ['Sí', 'No']})
    
    if sheet_name !='2.Integrantes grupo':
        
        v_range = d.get(str(end+len(eh))) + str(start_row +3) + ':' + d.get(str(end+len(eh))) + str(df.shape[0] + start_row +2)
        worksheet.data_validation(v_range,{'validate': 'list',
                                  'source': ['Sí', 'No']})
    
    # Integrantes
    if veh == 0:
        v_range = d.get(str(end+len(eh)-2)) + str(start_row +3) + ':' + d.get(str(end+len(eh)-2)) + str(df.shape[0] + start_row +2)
        worksheet.data_validation(v_range,{'validate': 'list',
                                'source': ['Sí', 'No']})  
    # patentes
    if veh == 1 :
        v_range = d.get(str(end+len(eh)-3)) + str(start_row +3) + ':' + d.get(str(end+len(eh)-3)) + str(df.shape[0] + start_row +2)
        worksheet.data_validation(v_range,{'validate': 'list',
                                  'source': ['Sí', 'No']})
        v_range = d.get(str(end+len(eh)-4)) + str(start_row +3) + ':' + d.get(str(end+len(eh)-4)) + str(df.shape[0] + start_row +2)
        worksheet.data_validation(v_range,{'validate': 'list',
                                  'source': ['Sí', 'No']})
        v_range = d.get(str(end+len(eh)-5)) + str(start_row +3) + ':' + d.get(str(end+len(eh)-5)) + str(df.shape[0] + start_row +2)
        worksheet.data_validation(v_range,{'validate': 'list',
                                  'source': ['Sí', 'No']})
    if veh ==2:
        v_range = d.get(str(end+len(eh)-2)) + str(start_row +3) + ':' + d.get(str(end+len(eh)-2)) + str(df.shape[0] + start_row +2)
        worksheet.data_validation(v_range,{'validate': 'list',
                                  'source': ['Sí', 'No']})
    if veh == 3:
        v_range = d.get(str(end+len(eh)-2)) + str(start_row +3) + ':' + d.get(str(end+len(eh)-3)) + str(df.shape[0] + start_row +2)
        worksheet.data_validation(v_range,{'validate': 'list',
                                  'source': ['Sí', 'No']})
        v_range = d.get(str(end+len(eh)-3)) + str(start_row +3) + ':' + d.get(str(end+len(eh)-4)) + str(df.shape[0] + start_row +2)
        worksheet.data_validation(v_range,{'validate': 'list',
                                  'source': ['Sí', 'No']})
        v_range = d.get(str(end+len(eh)-4)) + str(start_row +3) + ':' + d.get(str(end+len(eh)-5)) + str(df.shape[0] + start_row +2)
        worksheet.data_validation(v_range,{'validate': 'list',
                                  'source': ['Sí', 'No']})
        
        
##### WORKSHEET 1
def format_info(df, writer, sheet_name):
    
    '''format worksheet'''
    
    workbook=writer.book
    
    normal=workbook.add_format({'font_size':12,'text_wrap':True})
    
    merge_format = workbook.add_format({
    'bold': 1,
    'border':1,
    'text_wrap': True,    
    'align': 'center',
    'valign': 'vcenter',
    'font_color': 'black'})
    
    fmt_header = workbook.add_format({
        'align': 'center',    
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#33A584',
        'font_color': '#FFFFFF',
        'border': 1})
    
    # write df
    start_row = 6
    start_col = 3
    
    df.to_excel(writer, sheet_name, startrow =start_row, startcol=start_col,index = False)

    # get worksheet object
    worksheet = writer.sheets[sheet_name]
    
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(start_row, col_num + 3, value, fmt_header)
    
    #Prepare image insertion: See → https://xlsxwriter.readthedocs.io/example_images.html
    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 15)

    logo_path = str(pathlib.Path("__file__").parent.absolute()) + '/templates/img/logo.jpeg'
    worksheet.insert_image('A1', logo_path)
    
    # title 1 UNIVERSIDAD DE ANTIOQUIA
    title = workbook.add_format({'font_size':16,'center_across':True})

    # title 2 Vicerrectoria de Investigación
    title2 = workbook.add_format({'font_size':16,'center_across':True})
   
    # sub title 2 datos identificacion contacto
    title3 = workbook.add_format({'font_size':12,'center_across':True})
    
    # merge d1:f1
    worksheet.merge_range('D1:F1', 'UNIVERSIDAD DE ANTIOQUIA', title)
        
    # merge d2:f2
    worksheet.merge_range('D2:F2', ' Vicerrectoria de Investigación', title2)
    
    # merge d3:f3
    worksheet.merge_range('D3:F3', ' Datos de identificación y contacto', title3)
    
    # D5: F5
    worksheet.merge_range('D5:E5','Número inscripcion a la convocatoria:',merge_format)
    worksheet.write('F5','#',merge_format)
    
    # d6:f6
    worksheet.merge_range('D6:F6','Identificación del Grupo',merge_format)
        
    # d9:f9
    worksheet.merge_range('D10:F10','Identificación del Centro de Investigación',merge_format)
    # write 
    a='Nombre del Centro, Instituto o Corporación'
    worksheet.write('D11',a, fmt_header)
    worksheet.set_column('D11:D11',30, fmt_header)
    
    b='Nombre completo del Jefe de Centro, Instituto o Corporación'
    worksheet.write('E11',b, fmt_header) 
    worksheet.set_column('E11:E11',30, fmt_header)
    
    c='Email'
    worksheet.write('F11',c, fmt_header) 
    worksheet.set_column('F11:F11',30, fmt_header)
    
    # d13:f13
    worksheet.merge_range('D13:F13','Identificación de quien diligencia el formato',merge_format)
    a='Nombre completo del encargado de diligenciar el formato'
    worksheet.write('D14',a, fmt_header)
    worksheet.set_column('D14:D14',30, normal)
    
    b='Email'
    worksheet.write('E14',b, fmt_header) 
    worksheet.set_column('E14:E14',30, normal)
    
    c='Teléfono de contacto'
    worksheet.write('F14',c, fmt_header) 
    worksheet.set_column('F14:F14',30, normal)

# WORKSHEET 0
def format_ptt(workbook):
    
    #Global variables
    abstract_text='VERIFICACIÓN DE INFORMACIÓN PARA OTORGAR AVAL A LOS GRUPOS DE INVESTIGACIÓN  E INVESTIGADORES PARA SU PARTICIPACIÓN EN LA CONVOCATORIA 894 DE 2021 DE MINCIENCIAS'
    instructions='''Los grupos de investigación e investigadores de la Universidad de Antioquia que deseen participar en la Convocatoria Nacional para el reconocimiento y medición de grupos de investigación, desarrollo tecnológico o de innovación y para el reconocimiento de investigadores del Sistema Nacional de Ciencia, Tecnología e Innovación - SNCTI, 894 de 2021, deben presentar la información actualizada en las plataformas CvLAC y GrupLAC validada por el Centro de Investigación en el presente formato, y respaldada en el repositorio digital de evidencias dispuesto para este fin, para la obtención del aval institucional por parte de la Vicerrectoría de Investigación. 

    La información a validar corresponde a los años 2019-2020 y aquella que entra en la ventana de observación y debe ser modificada según el Modelo de medición de grupos. La validación comprende:

    1. Verificación de la vinculación de los integrantes a la Universidad de Antioquia y al grupo de investigación.  Diligenciar los campos solicitados. 

    2. Verificación de la producción de GNC, DTeI, ASC y FRH, en los campos habilitados en cada hoja de este formato. Las evidencias requeridas para los productos deben ser anexadas al repositorio digital asignado al grupo y se deben enlazar a cada producto.  

    Este documento debe ser diligenciado en línea.

    De antemano, la Vicerrectoría de Investigación agradece su participación en este ejercicio, que resulta de vital importancia para llevar a buen término la Convocatoria de Reconocimiento y Medición de Grupos de Investigación
    '''
    #Final part of the first sheet
    datos=clean_df(pd.read_excel(str(pathlib.Path("__file__").parent.absolute()) + '/templates/template_data.xlsx'))

    #Capture xlsxwriter object 
    # IMPORTANT → workbook is the same object used in the official document at https://xlsxwriter.readthedocs.io
    #workbook=writer.book
    #***************
    #Styles as explained in https://xlsxwriter.readthedocs.io
    title=workbook.add_format({'font_size':28,'center_across':True})
    subtitle=workbook.add_format({'font_size':24,'center_across':True})
    abstract=workbook.add_format({'font_size':20,'center_across':True,'text_wrap':True})
    normal=workbook.add_format({'font_size':12,'text_wrap':True})

    #***************
    #Creates the first work-sheet
    #IMPORTANT → worksheet is the same object  used in the official document at https://xlsxwriter.readthedocs.io
    worksheet=workbook.add_worksheet("1.Presentación")
    #Prepare image insertion: See → https://xlsxwriter.readthedocs.io/example_images.html
    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 15)
    logo_path = str(pathlib.Path("__file__").parent.absolute()) + '/templates/img/logo.jpeg'
    worksheet.insert_image('A1', logo_path)
    #Prepare text insertion: See  → https://xlsxwriter.readthedocs.io/example_images.html
    worksheet.set_column('C:C', 140,general)
    worksheet.set_row_pixels(0, 60)
    #Texts
    worksheet.write('C1', 'UNIVERSIDAD DE ANTIOQUIA',title)
    worksheet.set_row_pixels(2, 60)
    worksheet.write('C3', 'VICERRECTORÍA DE INVESTIGACIÓN',subtitle)
    worksheet.set_row_pixels(5, 100)
    worksheet.write('C6', abstract_text,abstract)
    worksheet.set_row_pixels(8, 40)
    worksheet.write('C9','PRESENTACIÓN DEL EJERCICIO',
                    workbook.add_format({'font_size':18,'center_across':True}) )
    worksheet.set_row_pixels(10, 320)
    worksheet.write('C11',instructions,normal)
    #*** ADD PANDAS DATAFRAME IN SPECIFIC POSITION ****
    #Add a data Frame in some specific position. See → https://stackoverflow.com/a/43510881/2268280
    #                                       See also → https://xlsxwriter.readthedocs.io/working_with_pandas.html
    writer.sheets["1.Presentación"]=worksheet
    datos.to_excel(writer,sheet_name="1.Presentación",startrow=12,startcol=2,index=False)
    #**************************************************
    #Fix columns heights for long text
    worksheet.set_row_pixels(17, 40)
    worksheet.set_row_pixels(18, 40)
    worksheet.set_row_pixels(19, 40)
    worksheet.set_row_pixels(20, 40)
    worksheet.set_row_pixels(22, 40)


def encrypted_login():
    login_file = 'login.enc'
    if not isfile(login_file):
        usuario = input('Usuario: ')
        contraseña = getpass.getpass('Contraseña: ')    
        ## key generation → Cannot be in repo!!!
        key = Fernet.generate_key()
     
        ## string the key in a file
        with open('filekey.key', 'wb') as filekey:
           filekey.write(key) 
        
        # opening the key
        with open('filekey.key', 'rb') as filekey:
            key = filekey.read()
         
         
        # using the generated key
        fernet = Fernet(key)
        
        encrypted = fernet.encrypt(f'{{"usuario": "{usuario}", "contraseña": "{contraseña}"}}'.encode('utf8'))
         
        # opening the file in write mode and 
        # writing the encrypted data
        with open(login_file, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
        print('local encrypted login file have been created')
    else:
        print(f'Using existing local encrypted login file from previos run: ./{login_file}')
    
    with open('filekey.key', 'rb') as filekey:
        key = filekey.read()
         
    # using the generated key
    fernet = Fernet(key)
    
    
    with open(login_file, 'rb') as enc_file:
        encrypted = enc_file.read()
     
    # decrypting the file
    decrypted = fernet.decrypt(encrypted)
    
    login = eval(decrypted.decode('utf8'))
    # internal variables inside function
    usuario = login['usuario']
    contraseña = login['contraseña']
    return usuario, contraseña

def login(user,password,institution='UNIVERSIDAD DE ANTIOQUIA',sleep=0.8,headless=True):
    #def login(user,password): → browser, otro, otro
    # MAIN CODE

    # login =
    # name_ins =
    # usser =
    # passw=

    # login
    browser = h.start_firefox('https://scienti.minciencias.gov.co/institulac2-war/',headless=headless)

    #browser = h.start_firefox('https://scienti.minciencias.gov.co/institulac2-war/')
    time.sleep(sleep)
    h.click('Consulte Aquí')

    time.sleep(sleep)
    h.write(institution,into='Digite el nombre de la Institución') # name ins

    time.sleep(sleep)
    h.click('Buscar')

    time.sleep(sleep)
    h.click(browser.find_element(By.ID, 'list_instituciones'))

    time.sleep(sleep)

    time.sleep(sleep)
    h.select('seleccione una',institution) # name_ins

    time.sleep(sleep)
    h.write(user,into='Usuario')                  # user

    time.sleep(sleep)
    h.write(password, into='Contraseña')                # passw

    time.sleep(sleep)
    h.click(h.Button('Ingresar'))

    # cookie injection
    time.sleep(sleep)
    # implementation cookie injection

    # get current cookie and store
    new_cookie=browser.get_cookies()[0]
    current_date = date.today()

    # Use strftime() to format the date and extract the year
    current_year = current_date.strftime("%Y")
    # create new_cookie with time_expire
    time_expire = (datetime(int(current_year)+1,1,1) - datetime(1970,1,1)).total_seconds()
    new_cookie['expiry'] = int(time_expire)

    # delete cookie sites
    # browser.delete_all_cookies()

    # add new cookie
    # browser.add_cookie(new_cookie)
    # try:
        # error=browser.find_element(By.CLASS_NAME, "error")
        # if error.text.lower().find('fallidos')>-1:        
            # print("ERROR! Bad login or password")
            # return False
        # else:
            # pass
    # except NoSuchElementException:
        # pass  

    # navigation 1
    time.sleep(sleep)
    h.click('Aval')

    time.sleep(sleep)
    h.click('Avalar grupos')

    time.sleep(sleep)
    h.click('Grupos Avalados')

    # -- end login --

    # list of total groups
    #select max results per page
    h.wait_until(h.Text('Ver Reporte').exists)
    h.click(browser.find_element(By.XPATH, '//table[@id="grupos_avalados"]//select[@name="maxRows"]'))

    time.sleep(sleep)
    h.select(browser.find_element(By.XPATH, '//table[@id="grupos_avalados"]//select[@name="maxRows"]'),'100')
    return browser

def get_groups(browser,DIR='InstituLAC',sleep=0.8):
    # catch 1: groups info [name, lider, cod,  link to producs]  
    # schema
    # empty df
    # select max items per page
    # while until end
    # try:
        # catch table
        # preproces table
        # catch urls
        # add url colums
        # add df
        # click next page -> raise error
    # except Nosuchelement:
        # break

    # catch 1: list of groups
    dfg=pd.DataFrame()
    cont=True

    while cont:

        try:
            # catch source
            time.sleep(sleep)
            source_g=browser.page_source

            # catch table
            time.sleep(sleep)
            df=pd.read_html(source_g, attrs={"id":"grupos_avalados"}, header=2)[0]

            # and preprocces it
            c=[x for x in df.columns if x.find('Unnamed:') == -1]
            dfgp=df[c][1:-1]
            print(dfgp.columns,dfgp.shape)

            # catch urls
            url=[a.get_attribute('href') for a in browser.find_elements(By.XPATH, '//table[@id="grupos_avalados"]//td[5]/a')]
            dfgp['Revisar'] = url
            dfg=dfg._append(dfgp)

            # click next page. this instruction rise error of the end. 
            h.click(browser.find_element(By.XPATH, '//table[@id="grupos_avalados"]//tr/td[3]/a'))

        except NoSuchElementException as e:

            print(e)
            print('out of cicle')
            break

        time.sleep(sleep)
        time.sleep(sleep)
    
    dfg=dfg.reset_index(drop=True)
    with open(f'{DIR}/dfg.pickle', 'wb') as f:
        pickle.dump(dfg, f)        
    return browser,dfg

def get_DB(browser, target_data, DB=[], dfg = pd.DataFrame(), sleep=0.8, DIR='InstituLAC', start=None, end=None, COL_Group='', start_time = 0):
    '''Get all products of institulac'''

    os.makedirs(DIR,exist_ok=True)

    if dfg.empty:
        browser,dfg=get_groups(browser,DIR=DIR,sleep=sleep)

    dfg = dfg.reset_index(drop=True)

    # Utility to handle interruptions. find start and end index to for the last COL_Group. 
    if COL_Group:
        dfcg=dfg[dfg['COL Grupo']==COL_Group]
        if not dfcg.empty:
            start=dfcg.index[0]
            end=start+1

    time.sleep(sleep*2)
    for idx in dfg.index[start:end]:       

        # Create db for store things related to group
        DBG = {} #  HERE V1. DBG.keys = [cat1,cat2,...,catN]
                 #  DBG['cat1'].keys = [prod1bycat,...prodnbycat]

        # Info group
        print(dfg.loc[idx,'Nombre del grupo'])

        # specific group url
        time.sleep(sleep)
        url_group = dfg.loc[idx,'Revisar']

        # go to url group
        time.sleep(sleep)
        browser.get(url_group)

        # catch two tables: info grupo and  members
        source=browser.page_source

        # Info group
        l_info=pd.read_html(source, match='Nombre Grupo')
        info_g=l_info[3].pivot(columns=0,values=1)

        # Store info group
        DBG['Info_group'] = info_g
        # List members
        l_int = pd.read_html(source,attrs={'id':'tblIntegrantes'},header=2)
        mem_g=l_int[0]

        # Store list of members
        DBG['Members'] =  mem_g

        # Products
        h.wait_until(lambda: browser.find_element(By.XPATH, '//td[@id="bodyPrincipal"]//a[text()="Ver productos"]') is not None)
        h.click(browser.find_element(By.XPATH, '//td[@id="bodyPrincipal"]//a[text()="Ver productos"]'))

        # Target products = ALL products: no aval, aval, aval pert (Categories)

        _target_data = [('//*[@id="ProdsNoAval"]', '//div[@id="accordionCatgNoAval"]/h3', 'categoriaNoAval=%s&subcategoriaNoAval=%s&aval=F'),
                       ('//*[@id="ProdsAval"]','//div[@id="accordionCatg"]/h3','categoria=%s&subcategoria=%s&aval=T'),
                       ('//*[@id="ProdsPertenecia"]','//div[@id="accordionCatgP"]/h3','categoriaP=%s&subcategoriaP=%s&aval=P')
                      ]
        if target_data == 'NoAval':
            target_data = target_data = _target_data[0:1]
            print('map NoAvalProds')
        elif target_data == 'Aval':
            target_data = _target_data[1:2]
            print('map institulac NoAvalProds')
        elif target_data == 'Pert':
            target_data = _target_data[2:]
            print('map Pert institulac prods')
        elif target_data == 'All':
            target_data = _target_data
            print('map all institulac prods')
        
        lcp = [] # list of categories and prods by cat dif to cero e.g. [[NC_NO_AVAL,ART_IMP_NO_AVAL],[NC,ART_IMP]...]
        for i in target_data:
            print('#####')####
            time.sleep(sleep)
            h.wait_until(lambda: browser.find_element(By.XPATH, i[0]) is not None)
            time.sleep(sleep)
            h.click(browser.find_element(By.XPATH, i[0]))
            time.sleep(sleep)
            url_base=browser.current_url
            # MAP
            # map products by macro-Cat (prod aval per) diff to cero
            sleep = 0.8
            for cat in browser.find_elements(By.XPATH, i[1]):
                # exist products
                id_cat = cat.get_attribute('id')
                print(cat.text,'----',id_cat)
                num_prods_cat = int(re.findall(r'\d+',cat.text)[0])
                if num_prods_cat > 0:
                    time.sleep(sleep)
                    h.click(cat)
                    print(cat.text,'----',id_cat)
                else:
                    continue
                for prod in browser.find_elements(By.XPATH, '//div[@aria-labelledby="%s"]/h3' % cat.get_attribute('id')):
                    # items in products
                    #h.click(cat)
                    id_prod = prod.get_attribute('id')
                    #print('           ',prod.text,id_prod)
                    #print(prod)
                    num_items_prod = int(re.findall(r'\d+',prod.text)[0])
                    if num_items_prod > 0:
                        lcp.append([id_cat,id_prod])
                        print('           ',prod.text,id_prod)
                    else:
                        continue
                time.sleep(sleep)
                h.click(cat)
        # DBG
        # build database
        for cat in lcp:
            if cat[0] not in DBG.keys():
                DBG[cat[0]] = {}
        for prod in lcp:
            # build query by case no aval, aval rev, pert
            
            if 'NO_AV' in prod[0]:
                query='categoriaNoAval=%s&subcategoriaNoAval=%s&aval=F' % (prod[0],prod[1])
            elif '_P' in prod[0]:
                query='categoriaP=%s&subcategoriaP=%s&aval=P' % (prod[0],prod[1])
            else:
                query='categoria=%s&subcategoria=%s&aval=T' % (prod[0],prod[1])
            # HERE
            url_query = url_base.split('?')[0] + '?' + query + '&' + url_base.split('?')[1]
            # do query
            browser.get(url_query)
            # wait until complete load
            h.wait_until(h.Button('Guardar').exists,timeout_secs=20)
            # load
            page_source = browser.page_source
            # detect tables
            try:
                tables = pd.read_html(browser.page_source,attrs={'class':'table'})
            # clean tables
            except (ValueError, ImportError) as e:
                tables = [None]
            try:
                tables = [clean_tables(t) for t in tables]
            except AttributeError as e:
                pass
            # store table or tables
            if len(tables)>1:
                c=0
                for t in tables:
                    if t.shape[0] >= 1:
                        DBG[prod[0]][prod[1]+'_%s' % c] = t
                        c+=1
            else:
                DBG[prod[0]][prod[1]] = tables[0]
            time.sleep(sleep)
        
        # store in general DB.
        DB.append(DBG)
        with open(f'{DIR}/DB.pickle', 'wb') as f:
            pickle.dump(DB, f)

        print(time.time()-start_time)
    
    browser.quit()  
    return DB,dfg

def to_excel(DB,dfg,DIR='InstituLAC'):
    os.makedirs(DIR,exist_ok=True)
    global general
    global writer
    global workbook

    # Format records from DB into excel
    for idxx in range(len(DB)):
    # DATA
        DBG = DB[idxx]

        ### excel name
        name = 'Plantilla_Formato de verificación de información_GrupLAC_2024_'

        cod_gr = dfg.loc[idxx,'COL Grupo']

        try:
            col_gr = dfg[dfg['Nombre del grupo']==DBG['Info_group']['Nombre Grupo'].dropna().iloc[-1]
                      ]['COL Grupo'].iloc[-1]
        except:
            col_gr=cod_gr #safe option valid in sequential mode

        # initialize object= output excel file
        os.makedirs(f'{DIR}/{col_gr}',exist_ok=True)
        os.makedirs(f'{DIR}/{col_gr}/Repositorio_digital_{col_gr}',exist_ok=True)
        writer = pd.ExcelWriter(f'{DIR}/{col_gr}/{name}{col_gr}.xlsx', engine='xlsxwriter')

        workbook=writer.book

        general=workbook.add_format({'text_wrap':True})

        # PPT uncomment if ppt is necesary
        #format_ptt(workbook)

        # INFO GROUP
        df=get_info(DBG['Info_group'], col_gr)
        format_info(df, writer, '1.Datos de contacto')

        # WORKSHEET 1
        df = clean_df(DBG['Members']) 
        eh = DBEH['MEMBERS']
        format_df(df, '2.Integrantes grupo', 1, writer, eh, veh=0) #### veh = 0

        ### NC_P ### 

        #------- w3 -------
        # 3.ART y N

        var_w3 = 0

        try:
            df=clean_df(DBG['NC_P']['ART_IMP_P'])

            #df.to_excel(writer,sheet_name='NC_P',startrow = var_nc+1)

            eh=DBEH['NC_P']['ART_IMP_P']['ART_P_TABLE']

            format_df(df, '3.ART y N',  var_w3, writer,eh)

            var_w3 += df.shape[0] + 3

        except KeyError as e:

            pass

        try:
            df=clean_df(DBG['NC_P']['ART_ELE_P'])

            #df.to_excel(writer,sheet_name='NC_P',startrow = var_nc)

            eh=DBEH['NC_P']['ART_ELE_P']['ART_E_P_TABLE']

            format_df(df, '3.ART y N', var_w3, writer,eh)

            var_w3 += df.shape[0] + 3

        except KeyError as e:

            pass

        try:
            df=clean_df(DBG['NC_P']['NOT_CIE_P'])

            #df.to_excel(writer,sheet_name='NC_P',startrow = var_nc)

            eh=DBEH['NC_P']['NOT_CIE_P']['NOT_CIE_P_TABLE']

            format_df(df, '3.ART y N', var_w3, writer,eh)

            var_w3 += df.shape[0] + 3

        except KeyError as e:

            pass
        # -------------- w3 -------------------------

        #------------ ---w4------------
        # 4.LIB y LIB_FOR
        var_w4 = 0

        # libros por pertenencia
        try:
            df=rename_col(clean_df(DBG['NC_P']['LIB_P']),'Título del artículo','Título del libro')

            #df.to_excel(writer,sheet_name='NC_P',startrow = var_nc)

            eh=DBEH['NC_P']['LIB_P']['LIB_P_TABLE']

            format_df(df, '4.LIB y LIB_FOR',  var_w4, writer,eh)

            var_w4 += df.shape[0] + 3

        except KeyError as e:

            pass

        # libros avalados con revisión
        # try:
        #     df=rename_col(clean_df(DBG['NC']['LIB']), 'Título del artículo' ,'Título del libro') 

        #     #df.to_excel(writer,sheet_name='FRH_P',startrow = var_rh)

        #     eh=DBEH['NC']['LIB']['LIB_T_AVAL_TABLE']

        #     format_df(df, '4.LIB y LIB_FOR', var_w4 , writer, eh)

        #     var_w4  += df.shape[0] + 3

        # except KeyError as e:

        #     pass


        # libros formacion
        try:
            df=rename_col(clean_df(DBG['ASC_P']['GEN_CONT_IMP_P']),'Título del libro','Título del libro formación') # lib form
            
            if df.shape[0] != 0:

                eh=DBEH['ASC_P']['GEN_CONT_IMP_P']['GC_I_P_TABLE_5']

                format_df(df, '4.LIB y LIB_FOR',  var_w4 , writer,eh)

                var_w4 += df.shape[0] + 3

            else: 
                raise(KeyError)


        except KeyError as e:

            pass  
        # --------------------w4--------------

        #--------------------w5---------------
        #5.CAP

        # cap pertenencia

        var_w5 = 0

        try:
            df=clean_df(DBG['NC_P']['CAP_LIB_P'])

            #df.to_excel(writer,sheet_name='NC_P',startrow = var_nc)

            eh=DBEH['NC_P']['CAP_LIB_P']['CAP_LIB_P_TABLE']

            format_df(df, '5.CAP',var_w5, writer,eh)

            var_w5 += df.shape[0] + 3

        except KeyError as e:

            pass

        # caps avalados con revision
          # caps avalados con revision
        # try:
        #     df = clean_df(DBG['NC']['CAP_LIB'])  ### ,veh = 2

        #     #df.to_excel(writer,sheet_name='FRH_P',startrow = var_rh)

        #     eh = DBEH['NC']['CAP_LIB']['CAP_LIB_T_AVAL_TABLE']

        #     format_df(df, '5.CAP', var_w5, writer, eh)

        #     var_w5 += df.shape[0] + 3

        # except KeyError as e:

        #     pass

        # traduccion filologica
        try:
            df=rename_col(clean_df(DBG['NC_P']['TRA_FIL_P']),'Título del libro', 'Título traducción filologica')

            #df.to_excel(writer,sheet_name='NC_P',startrow = var_nc)

            eh=DBEH['NC_P']['TRA_FIL_P']['TRA_FIL_P_TABLE']

            format_df(df, '5.CAP', var_w5, writer,eh)

            var_w5 += df.shape[0] + 3

        except KeyError as e:

            pass

        #-------------------w5------------------

        #------------w6-------------------------
        #6.Patente_Variedades
        var_w6 = 0

        # patentes
        try:
            df=rename_col(clean_df(DBG['NC_P']['PAT_P']),'Título del artículo','Título de la patente') ###### veh=1

            #df.to_excel(writer,sheet_name='NC_P',startrow = var_nc)

            eh=DBEH['NC_P']['PAT_P']['PAT_P_TABLE']

            format_df(df, '6.Patente_Variedades', var_w6, writer,eh, veh=1)

            var_w6 += df.shape[0] + 3

        except KeyError as e:

            pass

        # variedad vegetal
        try:
            df=clean_df(DBG['NC_P']['VAR_VEG_P'])

            #df.to_excel(writer,sheet_name='NC_P',startrow = var_nc)

            eh=DBEH['NC_P']['VAR_VEG_P']['VV_P_TABLE']

            format_df(df, '6.Patente_Variedades', var_w6, writer,eh)

            var_w6 += df.shape[0] + 3

        except KeyError as e:

            pass

        # Variedad Animal
        try:
            df=clean_df(DBG['NC_P']['VAR_ANI_P'])

            #df.to_excel(writer,sheet_name='NC_P',startrow = var_nc)

            eh=DBEH['NC_P']['VAR_ANI_P']['VA_P_TABLE']

            format_df(df, '6.Patente_Variedades', var_w6, writer,eh)

            var_w6 += df.shape[0] + 3

        except KeyError as e:

            pass

        # razas pecuarias mejoradas
        try:
            df=clean_df(DBG['NC_P']['RAZ_PEC_P'])

            #df.to_excel(writer,sheet_name='NC_P',startrow = var_nc)

            eh=DBEH['NC_P']['RAZ_PEC_P']['RAZ_PEC_P_TABLE']

            format_df(df, '6.Patente_Variedades', var_w6, writer,eh)

            var_w6 += df.shape[0] + 3

        except KeyError as e:

            pass
        # ---------------w6---------------------

        #---------------w7-------------------
        var_w7 = 0

        # productos investigacion creacion
        try:
            df=clean_df(DBG['NC_P']['PRD_INV_ART_P']) ###### veh = 1

            #df.to_excel(writer,sheet_name='NC_P',startrow = var_nc)

            eh=DBEH['NC_P']['PRD_INV_ART_P']['PAAD_P_TABLE']

            format_df(df, '7.AAD', var_w7, writer,eh, veh=3)

            var_w7 += df.shape[0] + 3

        except KeyError as e:

            pass

        #-------------w7---------------------

        #-------------w8----------------

        # 8.Tecnológico
        #### DTI_P

        var_w8 = 0

        # diseño industrial
        try:

            df=rename_col(clean_df(DBG['DTI_P']['DIS_IND_P']),'Nombre del diseño','Nombre del diseño industrial')

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['DIS_IND_P']['DI_P_TABLE']

            format_df(df, '8.Tecnológico', var_w8, writer, eh)

            var_w8 += df.shape[0] + 3

        except KeyError as e:

            pass

        #circuitos integrados
        try:
            df=rename_col(clean_df(DBG['DTI_P']['CIR_INT_P']),'Nombre del diseño', 'Nombre del diseño circuito')

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['CIR_INT_P']['ECI_P_TABLE']

            format_df(df, '8.Tecnológico', var_w8, writer,eh)

            var_w8 += df.shape[0] + 3

        except KeyError as e:

            pass

        # colecciones
        try:
            df=clean_df(DBG['DTI_P']['COL_CIENT_P'])

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['COL_CIENT_P']['COL_CIENT_P_TABLE']

            format_df(df, '8.Tecnológico', var_w8, writer,eh)

            var_w8 += df.shape[0] + 3


        except KeyError as e:

            pass

        # software 
        try:
            df=rename_col(clean_df(DBG['DTI_P']['SOFT_P']),'Nombre del diseño', 'Nombre del diseño de software')

            eh=DBEH['DTI_P']['SOFT_P']['SF_P_TABLE']

            format_df(df, '8.Tecnológico', var_w8, writer,eh)

            var_w8 += df.shape[0] + 3


        except KeyError as e:

            pass

        # secreto industrial
        try:
            df=rename_col(clean_df(DBG['DTI_P']['SEC_IND_P']),'Producto','Nombre secreto industrial')

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['SEC_IND_P']['SE_P_TABLE']

            format_df(df, '8.Tecnológico', var_w8, writer,eh)

            var_w8 += df.shape[0] + 3

        except KeyError as e:

            pass

        # prototipo insdustrial
        try:
            df=rename_col(clean_df(DBG['DTI_P']['PRT_IND_P']), 'Nombre del diseño', 'Nombre del prototipo')

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['PRT_IND_P']['PI_P_TABLE']

            format_df(df, '8.Tecnológico',  var_w8, writer,eh)

            var_w8 += df.shape[0] + 3

        except KeyError as e:

            pass

        # Registro distintivo
        try:
            df=clean_df(DBG['DTI_P']['SIG_DIS_P'])

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['SIG_DIS_P']['SD_P_TABLE']

            format_df(df, '8.Tecnológico', var_w8, writer,eh)

            var_w8 += df.shape[0] + 3

        except KeyError as e:

            pass

        # registros de acuerdo licencias expl obras AAD
        try:

            df=clean_df(DBG['DTI_P']['REG_AAD_P'])

            eh=DBEH['DTI_P']['REG_AAD_P']['AAAD_P_TABLE']

            format_df(df, '8.Tecnológico', var_w8, writer,eh)

            var_w8 += df.shape[0] + 3


        except KeyError as e:

            pass

        # prod nutracetico
        try:
            df=rename_col(clean_df(DBG['DTI_P']['NUTRA_P']),'Nombre del producto','Nombre del producto nutracetico')

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_nc)

            eh=DBEH['DTI_P']['NUTRA_P']['NUTRA_P_TABLE']

            format_df(df, '8.Tecnológico', var_w8, writer,eh)

            var_w8 += df.shape[0] + 3


        except KeyError as e:

            pass

        # registro cienti
        try:
            df=clean_df(DBG['DTI_P']['REG_CIENT_P'])

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['REG_CIENT_P']['REG_CIENT_P_TABLE']

            format_df(df, '8.Tecnológico',var_w8 , writer,eh)

            var_w8 += df.shape[0] + 3


        except KeyError as e:

            pass

        # planta piloto

        try:
            df=clean_df(DBG['DTI_P']['PLT_PIL_P'])

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['PLT_PIL_P']['PP_P_TABLE']

            format_df(df, '8.Tecnológico', var_w8, writer,eh)

            var_w8 += df.shape[0] + 3


        except KeyError as e:

            pass

        # protocolo vigilancia epidemologica

        try:
            df=clean_df(DBG['DTI_P']['PROT_VIG_EPID_P'])

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['PROT_VIG_EPID_P']['PROT_VIG_EPID_P_TABLE']

            format_df(df, '8.Tecnológico',var_w8, writer,eh)

            var_w8 += df.shape[0] + 3

        except KeyError as e:

            pass
        #---------------------w8----------------

        #---------------------w9----------------
        # 9.Empresarial
        var_w9 = 0

        # innovación gestion empresarial
        try:
            df=rename_col(clean_df(DBG['DTI_P']['INN_GES_EMP_P']),'Nombre de la innovación', 'Nombre de la innovación empresarial')

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['INN_GES_EMP_P']['IG_P_TABLE']

            format_df(df, '9.Empresarial', var_w9, writer,eh)

            var_w9 += df.shape[0] + 3


        except KeyError as e:

            pass


        # innovacion procesos y procedimiento
        try:
            df=rename_col(clean_df(DBG['DTI_P']['INN_PROC_P']),'Nombre de la innovación','Nombre de la innovación procesos y procedimientos')

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['INN_PROC_P']['IPP_P_TABLE']

            format_df(df, '9.Empresarial', var_w9, writer,eh)

            var_w9 += df.shape[0] + 3


        except KeyError as e:

            pass

        # regulaciones normas reglamentos legislaciones
        try:
            df=rename_col(clean_df(DBG['DTI_P']['REG_NORM_REGL_LEG_P']),'Tipo producto','Nombre regulación')

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['REG_NORM_REGL_LEG_P']['RNR_P_TABLE']

            format_df(df, '9.Empresarial', var_w9, writer,eh)

            var_w9 += df.shape[0] + 3

        except KeyError as e:

            pass

        # conceptos tecnicos
        try:
            df=clean_df(DBG['DTI_P']['CONP_TEC_P'])

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['CONP_TEC_P']['CONP_TEC_P_TABLE']

            format_df(df, '9.Empresarial', var_w9, writer,eh)

            var_w9 += df.shape[0] + 3


        except KeyError as e:

            pass

        # empresa base tecnologica
        try:
            df=rename_col(clean_df(DBG['DTI_P']['EMP_BSE_TEC_P']),'Tipo','Tipo de empresa base tecnologica')

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['EMP_BSE_TEC_P']['EBT_P_TABLE']

            format_df(df, '9.Empresarial', var_w9, writer,eh)

            var_w9 += df.shape[0] + 3


        except KeyError as e:

            pass

        # empresa de base cultural
        try:
            df=rename_col(clean_df(DBG['DTI_P']['EMP_CRE_CUL_P']),'Empresa', 'Tipo de empresa base cultural')

            #df.to_excel(writer,sheet_name='DTI_P',startrow = var_dt)

            eh=DBEH['DTI_P']['EMP_CRE_CUL_P']['ICC_P_TABLE']

            format_df(df, '9.Empresarial', var_w9, writer,eh)

            var_w9 += df.shape[0] + 3


        except KeyError as e:

            pass

        # -------------------------w9---------------------
        ######  ASC

        # -------------------------w10--------------------
        # 10.ASC y Divulgación
        var_w10 = 0 

        # productos de interes social
        try:
            df=rename_col(clean_df(DBG['ASC_P']['PASC_P']),'Nombre','Nombre producto interes social')

            if df.shape[0] != 0:

                eh=DBEH['ASC_P']['PASC_P']['PASC_FOR_P_TABLE']

                format_df(df, '10.ASC y Divulgación', var_w10, writer,eh)

                var_w10 += df.shape[0] + 3

            else:
                raise(KeyError)

        except KeyError as e:

            pass

        # Proceso de apropiación social del conocimiento resultado del trabajo conjunto 
        try:
            df=rename_col(clean_df(DBG['ASC_P']['PASC_P']), 'Nombre','Nombre del Proceso de apropiación social del conocimiento resultado del trabajo conjunto entre un Centro de Ciencia y un grupo de investigación')

            if df.shape[0] != 0:

                eh=DBEH['ASC_P']['PASC_P']['PASC_TRA_P_TABLE']

                format_df(df, '10.ASC y Divulgación', var_w10, writer,eh)

                var_w10 += df.shape[0] + 3
            else:
                raise(KeyError)

        except KeyError as e:

            pass

        # Nombre del Proceso de apropiación social del conocimiento para la generación de insumos de política pública y normatividad
        try:
            df=rename_col(clean_df(DBG['ASC_P']['PASC_P']),'Nombre','Nombre del Proceso de apropiación social del conocimiento para la generación de insumos de política pública y normatividad')

            if df.shape[0] != 0:

                eh=DBEH['ASC_P']['PASC_P']['PASC_GEN_P_TABLE']

                format_df(df, '10.ASC y Divulgación', var_w10, writer,eh)

                var_w10 += df.shape[0] + 3
            else:
                raise(KeyError)

        except KeyError as e:

            pass

        #Nombre del Proceso de apropiación social del conocimiento para el fortalecimiento de cadenas productivas
        try:
            df=rename_col(clean_df(DBG['ASC_P']['PASC_P']),'Nombre', 'Nombre del Proceso de apropiación social del conocimiento para el fortalecimiento de cadenas productivas')

            if df.shape[0] != 0:

                eh=DBEH['ASC_P']['PASC_P']['PASC_CAD_P_TABLE']

                format_df(df, '10.ASC y Divulgación', var_w10, writer,eh)

                var_w10 += df.shape[0] + 3
            else:
                raise(KeyError)

        except KeyError as e:

            pass

        # Divulgacion
        # Piezas digitales
        try:
            df=rename_col(clean_df(DBG['ASC_P']['DC_P']),'Título del proyecto','Título del proyecto para la generación de piezas digitales')

            if df.shape[0] != 0:

                eh=DBEH['ASC_P']['DC_P']['DC_CD_P_TABLE']

                format_df(df, '10.ASC y Divulgación', var_w10, writer,eh)

                var_w10 += df.shape[0] + 3
            else:
                raise(KeyError)

        except KeyError as e:

            pass

        # textuales
        try:
            df=rename_col(clean_df(DBG['ASC_P']['DC_P']),'Título del proyecto','Título del proyecto para la generación de piezas Textuales (incluyendo cartillas, periódicos, revistas, etc.), Producción de estrategias transmediáticas y Desarrollos web')

            if df.shape[0] != 0:

                eh=DBEH['ASC_P']['DC_P']['DC_CON_P_TABLE']

                format_df(df, '10.ASC y Divulgación', var_w10, writer,eh)

                var_w10 += df.shape[0] + 3
            else:
                raise(KeyError)

        except KeyError as e:

            pass

        # produccion estrategia trasmediatica
        try:
            df=rename_col(clean_df(DBG['ASC_P']['DC_P']), 'Título del proyecto','Título del proyecto estrategia trasmediatica')

            if df.shape[0] != 0:

                eh=DBEH['ASC_P']['DC_P']['DC_TRA_P_TABLE']

                format_df(df, '10.ASC y Divulgación', var_w10, writer,eh)

                var_w10 += df.shape[0] + 3
            else:
                raise(KeyError)

        except KeyError as e:

            pass

        # desarrollo web
        try:
            df=rename_col(clean_df(DBG['ASC_P']['DC_P']),'Título del proyecto','Título del proyecto desarrollo web')

            if df.shape[0] != 0:

                eh=DBEH['ASC_P']['DC_P']['DC_DES_P_TABLE']

                format_df(df, '10.ASC y Divulgación', var_w10, writer,eh)

                var_w10 += df.shape[0] + 3
            else:
                raise(KeyError)

        except KeyError as e:

            pass

        # --- --- --- -- w10 -- -- -- -- -- -- --

        # ---------------w11--------------------

        # FRH
        var_w11 = 0

        # tesis doctorado
        try:
            df=rename_col(clean_df(DBG['FRH_P']['TES_DOC_P']), 'Título','Título de la tesis de doctorado')  ### ,veh = 2

            #df.to_excel(writer,sheet_name='FRH_P',startrow = var_rh)

            eh=DBEH['FRH_P']['TES_DOC_P']['TD_P_TABLE']

            format_df(df, '11.Formación y programas', var_w11, writer, eh,veh=2)

            var_w11 += df.shape[0] + 3

        except KeyError as e:

            pass

        # tesis maestria
        try:
            df=rename_col(DBG['FRH_P']['TES_MAST_P'],'Título','Título del trabajo de grado de maestría') ### veh = 2

            #df.to_excel(writer,sheet_name='FRH_P',startrow = var_rh)

            eh=DBEH['FRH_P']['TES_MAST_P']['TM_P_TABLE']

            format_df(df, '11.Formación y programas',var_w11, writer,eh,veh=2)

            var_w11 += df.shape[0] + 3

        except KeyError as e:

            pass

        # tesis pregrado
        try:
            df=rename_col(clean_df(DBG['FRH_P']['TES_PREG_P']),'Título','Título del trabajo de grado de pregrado') ### veh = 2

            #df.to_excel(writer,sheet_name='FRH_P',startrow = var_rh)

            eh=DBEH['FRH_P']['TES_PREG_P']['TP_P_TABLE']

            format_df(df, '11.Formación y programas',var_w11, writer,eh,veh = 2)

            var_w11 += df.shape[0] + 3

        except KeyError as e:

            pass

        # asesoria programa academico
        try:
            df=rename_col(clean_df(DBG['FRH_P']['ASE_PRG_ACA_P']),'Tipo','Nombre programa académico creado') 

            eh=DBEH['FRH_P']['ASE_PRG_ACA_P']['APGA_P_TABLE']

            format_df(df, '11.Formación y programas', var_w11, writer,eh)

            var_w11 += df.shape[0] + 3

        except KeyError as e:

            pass

        # asesoria creacion de cursos
        try:
            df=rename_col(clean_df(DBG['FRH_P']['ASE_CRE_CUR_P']),'Tipo','Nombre curso creado')

            eh=DBEH['FRH_P']['ASE_CRE_CUR_P']['ACC_P_TABLE']

            format_df(df, '11.Formación y programas', var_w11, writer,eh)

            var_w11 += df.shape[0] + 3

        except KeyError as e:

            pass

        # programa ondas
        try:
            df=rename_col(clean_df(DBG['FRH_P']['ASE_PRG_ONDAS_P']),'Integrante','Integrante programa ondas')

            eh=DBEH['FRH_P']['ASE_PRG_ONDAS_P']['APO_P_TABLE']

            format_df(df, '11.Formación y programas', var_w11, writer,eh)

            var_w11 += df.shape[0] + 3

        except KeyError as e:

            pass
        #----------------w11---------------------------

        #----------------w12---------------------------
        # Proyectos
        var_w12 = 0
        
        # Proyecto de investigación y desarrollo
        try:
            df=rename_col(clean_df(DBG['FRH_P']['PROY_INV_DES_P']),'Nombre','Proyecto de investigación y desarrollo')

            eh=DBEH['FRH_P']['PROY_INV_DES_P']['PID_P_TABLE']

            format_df(df, '12.Proyectos', var_w12, writer,eh)

            var_w12 += df.shape[0] + 3

        except KeyError as e:

            pass

        # Proyecto de investigación + creación
        try:
            df=rename_col(clean_df(DBG['FRH_P']['PROY_INV_CRE_P']),'Nombre','Proyecto de investigación + creación')

            eh=DBEH['FRH_P']['PROY_INV_CRE_P']['INV_CRE_P_TABLE']

            format_df(df, '12.Proyectos', var_w12, writer,eh)

            var_w12 += df.shape[0] + 3

        except KeyError as e:

            pass

        # Proyecto de investigación, desarrollo e innovación (ID+I)
        try:
            df=rename_col(clean_df(DBG['FRH_P']['PROY_INV_DES_INN_P']),'Nombre','Proyecto de investigación, desarrollo e innovación (ID+I)')

            eh=DBEH['FRH_P']['PROY_INV_DES_INN_P']['PF_P_TABLE']

            format_df(df, '12.Proyectos', var_w12, writer,eh)

            var_w12 += df.shape[0] + 3

        except KeyError as e:

            pass

        # Proyecto de extensión y de responsabilidad social en CTeI
        try:
            df=rename_col(clean_df(DBG['FRH_P']['PROY_INV_RESP_SOC_P']),'Nombre','Proyecto de extensión y de responsabilidad social en CTeI')

            eh=DBEH['FRH_P']['PROY_INV_RESP_SOC_P']['PE_P_TABLE']

            format_df(df, '12.Proyectos', var_w12, writer,eh)

            var_w12 += df.shape[0] + 3

        except KeyError as e:

            pass

        writer.close()

# HERE 
def dummy_fix_df(DB):
    nones=False
    for i in range(len(DB)):
        for k in list(DB[i].keys())[2:]:
            for kk in  DB[i][k].keys():
                #print(i,k,kk)
                if DB[i][k][kk] is None:
                    nones=True
                    DB[i][k][kk]={kk: pd.DataFrame()} 
    return DB,nones

def checkpoint(DIR='InstituLAC',start=None,CHECKPOINT=True):
    DB_path=f'{DIR}/DB.pickle'
    dfg_path=f'{DIR}/dfg.pickle'
    RETURN=([],pd.DataFrame(),start)
    if os.path.exists(DB_path) and os.path.exists(DB_path):
        with open(DB_path, 'rb') as f:
            DB=pickle.load(f)
        with open(dfg_path, 'rb') as f:
            dfg=pickle.load(f)    
    else:
        CHECKPOINT=False
        return RETURN+(CHECKPOINT,)
        
    try:
        oldend=len(DB)-1
        if ( dfg.loc[oldend]['Nombre del grupo'] == 
             DB[oldend]['Info_group']['Nombre Grupo'].dropna().iloc[-1]
            and CHECKPOINT):
            start=oldend+1 # Reset start
            return DB,dfg,start,CHECKPOINT
    except:
        CHECKPOINT=False
        return RETURN+(CHECKPOINT,)        
# HERE
def to_json(DB,dfg,DIR='InstituLAC'):
    DFG=dfg.copy().reset_index(drop=True)
    DBJ=[]
    for i in range(len(DB)):
        db={}
        db['Group']=DFG.drop('Revisar',axis='columns').fillna('').loc[i].to_dict()

        cs=DB[i]['Info_group'].columns[1:-2]

        d={}
        for c in cs:
            try:
                d[' '.join(c.split()[0:4]).replace('(','')]=DB[i]['Info_group'][c].dropna().iloc[-1]
            except IndexError:
                d[' '.join(c.split()[0:4]).replace('(','')]=''

        db['Info_group']=d


        db['Members']=DB[i]['Members'][DB[i]['Members'].columns[1:4]].fillna('').to_dict('records')

        for k in [x for x in list(DB[i].keys()) if x not in ['Info_group','Members','Group']]:
            for kk in DB[i][k].keys():
                #print( f'{k}-{kk}{nk}' ) 
                df=DB[i][k][kk]
                if df is not None and not df.empty:
                    nk=re.sub('[A-Z\_]','',kk)
                    cs=[c for c in df.columns if c.find('Unnamed:')==-1 and c!='Revisar']
                    db[f'{k}-{kk}{nk}']=df[cs].fillna('').to_dict('records')
        DBJ.append(db)
        
    with open(f'{DIR}/DB.json', 'w') as outfile:
        json.dump(DBJ, outfile)
        
    return DBJ

def main(user, password,target_data='Pert', institution='UNIVERSIDAD DE ANTIOQUIA', DIR='InstituLAC', 
         CHECKPOINT=True,headless=True, start=None, end=None, COL_Group='',
         start_time=0):
    '''
    '''
    browser = login(user, password, institution=institution, headless=headless)
    
    LOGIN=True
    if not browser:
        LOGIN=False
        return LOGIN
        
    time.sleep(2)

    DB, dfg, start, CHECKPOINT = checkpoint(DIR=DIR, start=start, CHECKPOINT=CHECKPOINT)
    print('*' * 80)
    if CHECKPOINT:
        print(f'start → {len(DB)}')
    else:
        print(f'start → {start}')
    print('*' * 80)
    
    if end and start and end < start:
        sys.exit('ERROR! end<=start')

    DB, dfg = get_DB(browser,target_data, DB=DB, dfg=dfg, DIR=DIR,
                     start=start, end=end, COL_Group=COL_Group, start_time=start_time)

    DB, nones = dummy_fix_df(DB)
    if nones:
        print('WARNING:Nones IN DB')
    to_excel(DB, dfg, DIR=DIR)
    DBJ=to_json(DB, dfg, DIR=DIR)
    
    return LOGIN  
