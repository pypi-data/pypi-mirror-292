# from rest_framework import serializers
# from shared_dyamic_listing.models import *
#
#
# class ColumnsTitlesOutputModelNewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ColumnsTitlesOutputModelNew
#         fields = [
#             'columnTitle',
#             'isTitle',
#             'isDefault',
#             'isBusiness',
#             'isAdmin',
#             'isShown',
#             'isActive'
#         ]
#
#
# class OptionDataOutPutModelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OptionDataOutPutModel
#         fields = [
#             'optionId',
#             'optionName',
#             'optionDescription'
#         ]
#
#
# class ListingOptionOutPutModelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ListingOptionOutPutModel
#         fields = [
#             'optionName',
#             'optionDescription'
#         ]
#
#
# class TitleColumnsOutputModelSerializer(serializers.ModelSerializer):
#     titles = ColumnsTitlesOutputModelNewSerializer(many=True, read_only=True)
#     options = OptionDataOutPutModelSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = TitleColumnsOutputModel
#         fields = [
#             'columnId',
#             'columnName',
#             'columnStatus',
#             'hasOption',
#             'titles',
#             'options'
#         ]
#
#
# class ListingPreferencesOutPutModelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ListingPreferencesOutPutModel
#         fields = [
#             'columnId',
#             'columnName',
#             'columnStatus',
#             'columnTitle',
#             'hasOption',
#             'entityId',
#             'position',
#             'isSticky',
#             'isShown',
#             'isAdmin',
#             'isBusiness',
#             'isDeleted',
#             'createdBy',
#             'createdOn',
#             'modifiedBy',
#             'modifiedOn'
#         ]
#
#
# class ListingPreferencesOutPutModelUpdatedSerializer(serializers.ModelSerializer):
#     options = ListingOptionOutPutModelSerializer(many=True, read_only=True)
#     titles = ColumnsTitlesOutputModelNewSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = ListingPreferencesOutPutModelUpdated
#         fields = [
#             'columnId',
#             'columnName',
#             'columnStatus',
#             'columnTitle',
#             'hasOption',
#             'entityId',
#             'position',
#             'isSticky',
#             'isShown',
#             'isAdmin',
#             'isBusiness',
#             'isDeleted',
#             'createdBy',
#             'createdOn',
#             'modifiedBy',
#             'modifiedOn',
#             'options',
#             'titles'
#         ]
#
#
# class CountryListSerializer(serializers.ModelSerializer):
#     columns = TitleColumnsOutputModelSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = CountryList
#         fields = [
#             'countryId',
#             'columns'
#         ]
#
#
# class ColumnsTitleResponseModelSerializer(serializers.ModelSerializer):
#     country = CountryListSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = ColumnsTitleResponseModel
#         fields = [
#             'businessId',
#             'country'
#         ]
#
#
# class ColumnsTitleResponseModelNewSerializer(serializers.ModelSerializer):
#     columnsData = ColumnsTitleResponseModelSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = ColumnsTitleResponseModelNew
#         fields = [
#             'code',
#             'message',
#             'columnsData'
#         ]
#
#
# class ListingPreferencesResponsePutModelNewSerializer(serializers.ModelSerializer):
#     listingPreference = ListingPreferencesOutPutModelUpdatedSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = ListingPreferencesResponsePutModelNew
#         fields = [
#             'code',
#             'message',
#             'listingPreference'
#         ]
