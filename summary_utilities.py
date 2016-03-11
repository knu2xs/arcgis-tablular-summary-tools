"""
Purpose:        Provide a few quick and easy to use utilities for calculating some statistical metrics for tabular data.
DOB:            09Mar2016
Author:         Joel McCune (http://github.com/knu2xs)
"""
# import modules
import numpy
import arcpy
import scipy.stats


def calculate_zscore(table, data_field, zscore_field):
    """
    For a table supported by arcpy, calculate the zscore to a new field based on the values in the data field.
    :param table: Table supported by arcpy.
    :param data_field: Field containing the data values.
    :param zscore_field: Field to be populated with the Z-Score.
    :return:
    """
    # sql query to exclude records with null values
    sql_query = '{} IS NOT NULL'.format(data_field)

    # create the array of values from the data field
    data_list = [row[0] for row in arcpy.da.SearchCursor(table, data_field, sql_query)]

    # get a corresponding list of Z-Scores
    zscore_list = list(scipy.stats.zscore(numpy.array(data_list)))

    # create an update cursor to revise field values
    with arcpy.da.UpdateCursor(table, zscore_field, sql_query) as update_cursor:

        # iterate the rows and populate the zscore
        for index, row in enumerate(update_cursor):

            # populate the zscore field with the corresponding zscore value
            row[0] = zscore_list[index]

            # update the row
            update_cursor.updateRow(row)


def add_calculate_zscore(table, data_field, zscore_field_name, zscore_field_alias):
    """
    Wrapper around calculate field adding the added functionality of adding the field when running the tool.
    :param table: Table supported by arcpy.
    :param data_field: Field containing the data values.
    :param zscore_field_name: Field to be populated with the Z-Score.
    :param zscore_field_alias: Human readable name for the field.
    :return:
    """
    # make sure the field does not already exist
    if zscore_field_name in [field.name for field in arcpy.ListFields(table)]:
        raise Exception("Field {} already exists.".format(zscore_field_name))

    # add the field
    arcpy.AddField_management(
        in_table=table,
        field_name=zscore_field_name,
        field_alias=zscore_field_alias,
        field_type='FLOAT'
    )

    # calculate the zscore
    calculate_zscore(table, data_field, zscore_field_name)


def calculate_percent_delta(table, data_field_one, data_field_two, delta_field):
    """
    Given two fields for the same performance metric over time, create a comparison score indicating the percent change.
    :param table: Table containing the data to be calculated.
    :param data_field_one: Data field for the metric indicator for the first time period.
    :param data_field_two: Data field for the metric indicator for the second time period.
    :param delta_field: The field where the results will be saved.
    :return:
    """
    # create an update cursor
    with arcpy.da.UpdateCursor(table, [data_field_one, data_field_two, delta_field]) as update_cursor:

        # iterate
        for row in update_cursor:

            # calculate the percent change score
            row[2] = 1 - row[1] / row[2]

            # commit the update
            row.updateRow(row)


def add_calculate_percent_delta(table, data_field_one, data_field_two, delta_field_name, delta_field_alias):
    """
    Wrapper around calculate field adding the added functionality of adding the field when running the tool.
    :param table:
    :param data_field_one:
    :param data_field_two:
    :param delta_field_name:
    :param delta_field_alias:
    :return:
    """
    # make sure the field does not already exist
    if delta_field_name in [field.name for field in arcpy.ListFields(table)]:
        raise Exception("Field {} already exists.".format(delta_field_name))

    # add the field
    arcpy.AddField_management(
        in_table=table,
        field_name=delta_field_name,
        field_alias=delta_field_alias,
        field_type='FLOAT'
    )

    # calculate the percent delta
    calculate_percent_delta(table, data_field_one, data_field_two, delta_field_name)
