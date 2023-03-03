import arcpy, os

# Set the input table
in_table=arcpy.GetParameterAsText(0)
in_RouteIDFieldname =arcpy.GetParameterAsText(1)
in_fromMsFieldname =arcpy.GetParameterAsText(2)
in_toMsFieldname =arcpy.GetParameterAsText(3)
in_maxDelta = arcpy.GetParameterAsText(4)
out_table = arcpy.GetParameterAsText(5)

arcpy.env.overwriteOutput = True
routeIDFieldname = 'RouteId'

row = None
rows = None
newRow = None
insertCursor = None

try:
    if (in_maxDelta == 0):
        raise ValueError('The maximum measure delta cannot be a value of zero')

    # Attempt to create the output table...

    arcpy.CreateTable_management(os.path.dirname(out_table), os.path.basename(out_table), '')
    arcpy.AddField_management(out_table, routeIDFieldname, "TEXT", 9, "", "", "", "NULLABLE", "NON_REQUIRED")
    arcpy.AddField_management(out_table, in_fromMsFieldname, "DOUBLE", 9, "", "", "", "NULLABLE", "NON_REQUIRED")
    arcpy.AddField_management(out_table, in_toMsFieldname, "DOUBLE", 9, "", "", "", "NULLABLE", "NON_REQUIRED")
    arcpy.AddField_management(out_table, "HPMS_BinID", "TEXT", 9, "", 50, "", "NULLABLE", "NON_REQUIRED")
    insertCursor = arcpy.InsertCursor(out_table)
    
    desc = arcpy.Describe(in_table)
    oidFieldname = desc.OIDFieldName

    arcpy.AddMessage('Finished')

    # Determine the number of rows to process.
    rowCount = int(arcpy.GetCount_management(in_table).getOutput(0))

    # Setup the progressor.
    arcpy.SetProgressor('step','writing output, please wait...', 0, rowCount, 1)


    rows = arcpy.SearchCursor(in_table)
    for row in rows:
        iteration = 1 #Setup the iteration counter (to be used in HPMS Bin naming)
        oid = row.getValue(oidFieldname)
        route = row.getValue(routeIDFieldname)
        fMs = row.getValue(in_fromMsFieldname)
        hpmsBin = row.getValue(routeIDFieldname) + '_' + str(iteration)
        
          #Optionally zero negative measures if close to true 0
        if (0 - fMs) < 0.00000004:
            fMs = 0
        
        tMs = row.getValue(in_toMsFieldname)
        arcpy.AddMessage(str(route) + ': ' + str(fMs) + ' -> ' + str(tMs))
        print str(route) + ': ' + str(fMs) + ' -> ' + str(tMs)
        
        incrementValue = (float(in_maxDelta)/ 5280.00)
        print str(incrementValue) + ' G ' 
        if (tMs < fMs) and (incrementValue > 0):
            incrementValue = incrementValue * -1
            print 'A '
        if (tMs > fMs) and (incrementValue < 0):
            incrementValue = incrementValue * -1
            print 'B '
        #print 'C'
        fromMs = fMs
        #print str(fromMs)
        continueLooping = True        
        while continueLooping:
            toMs = fromMs + incrementValue
            #print str(toMs)
            if (toMs > tMs) and (incrementValue > 0):
                toMs = tMs
                print str(toMs) + ' A: ' + str(tMs)
            if (toMs < tMs) and (incrementValue < 0):
                toMs = tMs
                print str(toMs) + ' B: ' + str(tMs)
              
                
            arcpy.AddMessage('     ' + str(fromMs) + ' -> ' + str(toMs))
            print str(fromMs) + ' -> ' + str(toMs)
            newRow = insertCursor.newRow()
            newRow.setValue(routeIDFieldname,route)
            newRow.setValue(in_fromMsFieldname, fromMs)
            newRow.setValue(in_toMsFieldname, toMs)
            print (hpmsBin)
            newRow.setValue("HPMS_BinID", hpmsBin)
            insertCursor.insertRow(newRow)

            iteration += 1
            hpmsBin = row.getValue(routeIDFieldname) + '_' + str(iteration)
            
            fromMs = toMs
            continueLooping = fromMs < tMs if incrementValue > 0 else fromMs > tMs


        # Update the progressor position 
        arcpy.SetProgressorPosition()

        

except Exception as e:
    arcpy.AddError('Exception: %s' % e)
    if row:
        arcpy.AddWarning('Offending Row: %s' % row.getValue(oidFieldname))
    if not arcpy.GetMessages() == "":
        arcpy.AddMessage(arcpy.GetMessages(2))
        print arcpy.GetMessages(2)
    else:
        #arcpy.AddMessage("Unknown Error")
        #print "Unknown Error"    
        arcpy.AddMessage(e.message)
        print e.message        

finally:
    del row
    del rows
    del newRow
    del insertCursor
    arcpy.ResetProgressor()














