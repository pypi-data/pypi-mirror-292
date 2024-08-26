from itertools import groupby
from operator import itemgetter

from shared_dyamic_listing.db import get_connection


def get_listing_preference_by_user_id(user_id, business_id, service_id):
    response = {
        'listingPreference': None,
        'code': None,
        'message': None
    }

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        sql = """
            DECLARE @ErrorCode INT, @ErrorMessage NVARCHAR(255);
            EXEC [dbo].[usp_ListingPreferenceByUserId_Get]
                @id = ?,                 
                @BusinessId = ?,       
                @serviceId = ?,            
                @ErrorCode = @ErrorCode OUTPUT,
                @ErrorMessage = @ErrorMessage OUTPUT;
            SELECT @ErrorCode AS ErrorCode, @ErrorMessage AS ErrorMessage;
        """

        # Execute the stored procedure
        cursor.execute(sql, (user_id, business_id, service_id))

        # Fetch the result set
        listing_preference_results = cursor.fetchall()

        # Fetch the output parameters
        cursor.nextset()  # Move to the next result set
        output_params = cursor.fetchone()
        error_code = output_params[0]
        error_message = output_params[1]

        response['code'] = error_code
        response['message'] = error_message

        if error_code == 0:
            title_result = get_column_titles_by_business_id(business_id, service_id)

            listing_preference = []

            for item in listing_preference_results:
                column_id = item.columnId

                titles_data = []
                for column in title_result['columnsData']:
                    for country in column['country']:
                        for column_data in country['columns']:
                            if column_data['columnId'] == column_id:
                                for title in column_data['titles']:
                                        titles_data.append(title)
                default_title = next((t for t in titles_data if t.get("isDefault", False)), None)
                selected_title = default_title or titles_data[0] if titles_data else None

                column_names_output = {
                    'id': item.columnId or 0,
                    'columnId': item.columnId or 0,
                    'columnName': item.columnName,
                    'position': item.position,
                    'isShown': item.isShown or True,
                    'hasOption': item.hasOption or False,
                    'isSticky': item.isSticky or False,
                    'columnStatus': item.columnStatus,
                    'entityId': item.entityId,
                    'isAdmin': item.isAdmin,
                    'isBusiness': item.isBusiness,
                    'isDeleted': item.isDeleted,
                    'createdBy': item.createdBy,
                    'createdOn': item.createdOn,
                    'modifiedBy': item.modifiedBy,
                    'modifiedOn': item.modifiedOn,
                    'options': [],
                    'columnTitle': selected_title.get('columnTitle', '') if selected_title is not None else item.columnTitle
                }

                if item.hasOption:
                    unique_options = set()
                    for opt in listing_preference_results:
                        if opt.columnId == item.columnId and opt.optionId:
                            option_id = opt.optionId
                            if option_id not in unique_options:
                                column_names_output['options'].append({
                                    'id': option_id,
                                    'optionName': opt.optionName,
                                    'optionDescription': opt.optionDescription
                                })
                                unique_options.add(option_id)
                else:
                    column_names_output['options'] = None

                listing_preference.append(column_names_output)

            # response['listingPreference'] = [
            #     dict(t) for t in {tuple(d.items()) for d in listing_preference}
            # ]
            listing_preference.sort(key=itemgetter('columnId'))
            filtered_data = [next(group) for key, group in groupby(listing_preference, key=itemgetter('columnId'))]

            response['listingPreference'] = filtered_data

        else:
            response['listingPreference'] = None

    except Exception as ex:
        response['code'] = -1
        response['message'] = str(ex)

    finally:
        cursor.close()

    return response


def get_column_titles_by_business_id(id, service_id):
    response = {
        'columnsData': None,
        'code': None,
        'message': None
    }

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # stored_proc_call = "exec usp_columnTitlesByBusinessIdNew_Get @id=?, @serviceId=?, @ErrorCode=?, @ErrorMessage=?"
        # cursor.execute(stored_proc_call, (id, service_id, None, None))
        sql = """
                   DECLARE @ErrorCode INT, @ErrorMessage NVARCHAR(255);
                   EXEC [dbo].[usp_columnTitlesByBusinessIdNew_Get]
                       @id = ?,                       
                       @serviceId = ?,            
                       @ErrorCode = @ErrorCode OUTPUT,
                       @ErrorMessage = @ErrorMessage OUTPUT;
                   SELECT @ErrorCode AS ErrorCode, @ErrorMessage AS ErrorMessage;
               """

        # Execute the stored procedure
        cursor.execute(sql, (id, service_id))

        # Fetch the result set
        column_titles_results = cursor.fetchall()

        # Fetch the output parameters
        cursor.nextset()  # Move to the next result set
        output_params = cursor.fetchone()
        error_code = output_params[0]
        error_message = output_params[1]

        response['code'] = error_code
        response['message'] = error_message

        if error_code == 0:
            columns_data = []
            for item in column_titles_results:
                existing_business = next((b for b in columns_data if b['businessId'] == item.entityId), None)
                if not existing_business:
                    existing_business = {
                        'businessId': item.entityId,
                        'country': []
                    }
                    columns_data.append(existing_business)

                existing_country = next((c for c in existing_business['country'] if c['countryId'] == item.countryId),
                                        None)
                if not existing_country:
                    existing_country = {
                        'countryId': item.countryId,
                        'columns': []
                    }
                    existing_business['country'].append(existing_country)

                existing_column = next((c for c in existing_country['columns'] if c['columnId'] == item.columnId), None)
                if not existing_column:
                    existing_column = {
                        'columnId': item.columnId,
                        'columnName': item.columnName,
                        'columnStatus': item.columnStatus,
                        'hasOption': item.hasOption or False,
                        'titles': [],
                        'options': []
                    }
                    existing_country['columns'].append(existing_column)

                if not any(t['id'] == item.titleId and t['columnTitle'] == item.columnTitle for t in
                           existing_column['titles']):
                    existing_column['titles'].append({
                        'id': item.titleId,
                        'isTitle': item.isTitle,
                        'columnTitle': item.columnTitle,
                        'isDefault': item.isDefault or False,
                        'isBusiness': item.isBusiness,
                        'isAdmin': item.isAdmin,
                        'isShown': item.isShown or False,
                        'isActive': item.isActive or True
                    })

                if item.hasOption:
                    if not any(o['optionId'] == item.optionId for o in existing_column['options']):
                        existing_column['options'].append({
                            'optionId': item.optionId or 0,
                            'optionName': item.optionName,
                            'optionDescription': item.optionDescription
                        })

            response['columnsData'] = columns_data

        else:
            response['columnsData'] = None

    except Exception as ex:
        response['code'] = -1
        response['message'] = str(ex)

    finally:
        cursor.close()

    return response


print(get_listing_preference_by_user_id(1, 1, 27))