
# Other module imports.
from data_extraction.models import *

# Third party imports.
import xlsxwriter
from datetime import datetime

def CreateIsothermTemplate(id):
    well = Well.objects.get(id=id)

    datas = Data.objects.filter(page__document__well=well).all()

    filename = f"{well.well_name} - isotherms.xlsx"
    workbook = xlsxwriter.Workbook(filename)

    bold_format = workbook.add_format({'bold': True})
    italic_format = workbook.add_format({'italic': True})
    red_format = workbook.add_format({'fg_color':'#EC7070'})
    
    yellow_text_format = workbook.add_format({'color':'#FFC000'})

    date_format = workbook.add_format({'num_format': 'd-mmm-yy'})

    for data in datas:
        try:
            wellNameParts = well.well_name.split(' ')
            wellNameParts.append('#')
            wellNameParts.append('-')

            sampleName = data.text
            for part in wellNameParts:
                mStr = part + ' '
                sampleName = sampleName.replace(mStr, '')
                sampleName = sampleName.replace(part,'')
            x =sampleName.find(' ',5)
            sampleName = sampleName[:x]

            sampleDetails = f"<{well.well_name.upper()}> - <{sampleName.upper()}>"
            
            inherentMoisture = data.value2
            ashAD = data.value3
            volatileMatter = data.value4
            fixedCarbon = data.value5
            ashMoisture = data.value6
            moisture = data.value7
            isothermSampleMass = data.value8
            particleSize = data.value9
            heliumDensity = data.value10
            testTemperature = data.value11
            analysisDate = data.text12
            testGas = data.text13
            piAnalysed = data.value14
            piDAF = data.value15
            viAnalysed = data.value16
            viDAF = data.value17

            worksheetName = sampleName
            if len(sampleDetails) > 31:
                worksheetName = worksheetName[:31]
            worksheet = workbook.add_worksheet(worksheetName)
            worksheet.set_column(0,0,55)
            worksheet.set_column(1,1,23)
            worksheet.set_column(2,2,20)

            # Sample Details
            worksheet.write(0,0, 'Client', bold_format)
            worksheet.write(1,0, 'Sample Details', bold_format)
            worksheet.write(1,1, sampleDetails, red_format)
            worksheet.write(1,2, '', red_format)
            worksheet.write(1,3, '', red_format)
            worksheet.write(1,4, '', red_format)


            # Sample Properties
            # Column A
            worksheet.write(3,0, 'Sample Properties', bold_format)
            worksheet.write(4,0, 'Inherent Moisture (%, ad)')
            worksheet.write(5,0, 'Ash (%, ad)')
            worksheet.write(6,0, 'Volatile Matter (%, ad)')
            worksheet.write(7,0, 'Fixed Carbon (%, ad)')
            worksheet.write(8,0, 'Ash (%, Equilibrium Moisture basis)')
            worksheet.write_rich_string('A10', 'Moist. (%, ',yellow_text_format,'<Equilibrium>', ' Moisture basis)')
            worksheet.write(9,0, 'Moist. (%, <Equilibrium> Moisture basis)')
            worksheet.write(10,0, 'Isotherm Sample Mass (g)')
            worksheet.write(11,0, 'Isotherm Sample Mass (lb)')
            worksheet.write(12,0, 'Particle Size (mm)')
            worksheet.write(13,0, 'Particle Size (US mesh)')
            worksheet.write(14,0, 'Helium density (g/cc)')
            worksheet.write(15,0, 'Test Temperature (°C)')
            worksheet.write(16,0, 'Test Temperature (°F)')
            worksheet.write(17,0, 'Analysis date')
            worksheet.write(18,0, 'Test Gas')
            # Column B
            worksheet = WriteValue(workbook, worksheet,4,1,inherentMoisture,True)
            worksheet = WriteValue(workbook, worksheet,5,1,ashAD,True)
            worksheet = WriteValue(workbook, worksheet,6,1,volatileMatter,False)
            worksheet = WriteValue(workbook, worksheet,7,1,fixedCarbon,False)
            worksheet = WriteValue(workbook, worksheet,8,1,ashMoisture,False)
            worksheet = WriteValue(workbook, worksheet,9,1,moisture,False)
            worksheet = WriteValue(workbook, worksheet,10,1,isothermSampleMass,False)

            worksheet = WriteValue(workbook, worksheet,12,1,particleSize,True)

            worksheet = WriteValue(workbook, worksheet,14,1,heliumDensity,False)
            worksheet = WriteValue(workbook, worksheet,15,1,testTemperature,False)
            
            try:
                myData = datetime.strptime(analysisDate,'%d %b %y')
                worksheet.write_datetime('B18', myData, date_format)
            except:
                worksheet.write(17,1, analysisDate)
            worksheet = WriteValue(workbook, worksheet,18,1,testGas,False)

            # Column D
            worksheet.write(9,3, '(Moisture type = Air Dried, As Received, Equilibrium or Inherent)')
            worksheet.write(18,3, '(Test Gas = Methane, Ethane, Propane, Carbon Dioxide or Nitrogen)')

            # Langmuir Isotherm Coefficients
            # Column A
            worksheet.write(19,0, 'Langmuir Isotherm Coefficients', bold_format)

            worksheet.write(21,0, 'Pl (MPa, abs)')
            worksheet.write(22,0, 'Vl (cc/g)')
            worksheet.write(23,0, 'Pl (psia)')
            worksheet.write(24,0, 'Vl (scf/t)')
            
            # Column B
            worksheet.write(20,1, 'As analysed',italic_format)
            worksheet = WriteValue(workbook, worksheet,21,1,piAnalysed,False)
            worksheet = WriteValue(workbook, worksheet,22,1,viAnalysed,False)

            # Column C
            worksheet.write(20,2, 'daf',italic_format)
            worksheet = WriteValue(workbook, worksheet,21,2,piDAF,False)
            worksheet = WriteValue(workbook, worksheet,22,2,viDAF,False)
            
            # Methane Absorption Basis
            worksheet.write(26,0, 'Methane Absolute Adsorption at Equilibrium Moisture Basis', bold_format)
            worksheet.write(27,0, 'Pressure (MPa,abs)')
            
            worksheet.write(27,1, 'Gas Content (cc/g) at 20°C; 101.1kPa (1 atm)')
            worksheet.write(28,1, '(as analysed)')
            
            worksheet.write(28,2, '(daf)')

            # Image
            image_path = data.page.file.path()
            print(image_path)
            worksheet.insert_image('A32',image_path, {'x_scale':0.5, 'y_scale':0.5})
        except Exception as e:
            print(e)

    



    workbook.close()

def WriteValue(workbook, worksheet,row,col,value, grey):
    if grey:
        yellow_format = workbook.add_format({'fg_color':'#D9D9D9'})
        pink_format = workbook.add_format({'fg_color':'#D9D9D9'})
    else:
        yellow_format = workbook.add_format({'fg_color':'#FFFF00'})
        pink_format = workbook.add_format({'fg_color':'#FCE4D6'})

    if value:
        try:
            worksheet.write(row, col, value, yellow_format)
        except:
            mStr = "Error"
            worksheet.write(row, col, mStr, pink_format)
    else:
        if not grey:
            mStr = ""
            worksheet.write(row, col, mStr, pink_format)

    return worksheet